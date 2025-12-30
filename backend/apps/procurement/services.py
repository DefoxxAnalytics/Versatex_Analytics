"""
Business logic for procurement data processing with security enhancements:
- CSV formula injection prevention
- File type validation
- Sanitized error messages
"""
import pandas as pd
import uuid
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import Supplier, Category, Transaction, DataUpload

logger = logging.getLogger(__name__)

# Characters that can trigger formula execution in spreadsheets
FORMULA_CHARS = ('=', '+', '-', '@', '\t', '\r', '\n')

# Maximum rows to process in a single upload
MAX_ROWS_PER_UPLOAD = 50000


def sanitize_csv_value(value: str) -> str:
    """
    Sanitize a CSV value to prevent formula injection.
    Prefixes dangerous characters with a single quote.
    """
    if not value or not isinstance(value, str):
        return value

    value = value.strip()

    # Check if the value starts with a formula character
    if value and value[0] in FORMULA_CHARS:
        # Prefix with single quote to prevent formula execution
        return "'" + value

    return value


def validate_csv_file(file) -> tuple[bool, str]:
    """
    Validate that a file is actually a CSV file.
    Returns (is_valid, error_message).
    """
    # Check file extension
    if not file.name.lower().endswith('.csv'):
        return False, "File must have .csv extension"

    # Check file size (50MB max)
    if file.size > 50 * 1024 * 1024:
        return False, "File size must be less than 50MB"

    # Try to read first few bytes to check if it's text
    try:
        file.seek(0)
        first_bytes = file.read(1024)
        file.seek(0)

        # Check for binary content (null bytes, etc.)
        if b'\x00' in first_bytes:
            return False, "File appears to be binary, not CSV"

        # Try to decode as UTF-8
        try:
            first_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Try common encodings
            try:
                first_bytes.decode('latin-1')
            except UnicodeDecodeError:
                return False, "File encoding not recognized"

    except Exception as e:
        logger.warning(f"CSV validation error: {e}")
        return False, "Could not validate file format"

    return True, ""


class CSVProcessor:
    """
    Process CSV files and import procurement data
    With security enhancements for formula injection prevention
    """

    REQUIRED_COLUMNS = ['supplier', 'category', 'amount', 'date']
    OPTIONAL_COLUMNS = [
        'description', 'subcategory', 'location', 'fiscal_year',
        'spend_band', 'payment_method', 'invoice_number'
    ]

    def __init__(self, organization, user, file, skip_duplicates=True):
        self.organization = organization
        self.user = user
        self.file = file
        self.skip_duplicates = skip_duplicates
        self.batch_id = str(uuid.uuid4())
        self.errors = []
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'duplicates': 0
        }

    def process(self):
        """
        Main processing method
        Returns: DataUpload instance
        """
        # Validate file first
        is_valid, error_msg = validate_csv_file(self.file)
        if not is_valid:
            raise ValueError(f"Invalid file: {error_msg}")

        # Create upload record
        upload = DataUpload.objects.create(
            organization=self.organization,
            uploaded_by=self.user,
            file_name=self.file.name,
            file_size=self.file.size,
            batch_id=self.batch_id,
            status='processing'
        )

        try:
            # Read CSV
            df = pd.read_csv(self.file)
            self.stats['total'] = len(df)

            # Check row limit
            if len(df) > MAX_ROWS_PER_UPLOAD:
                raise ValueError(
                    f"File contains {len(df)} rows, maximum allowed is {MAX_ROWS_PER_UPLOAD}"
                )

            # Validate columns
            self._validate_columns(df)

            # Process rows
            self._process_rows(df)

            # Update upload record
            upload.total_rows = self.stats['total']
            upload.successful_rows = self.stats['successful']
            upload.failed_rows = self.stats['failed']
            upload.duplicate_rows = self.stats['duplicates']
            upload.error_log = self._sanitize_error_log()
            upload.completed_at = timezone.now()

            if self.stats['failed'] == 0:
                upload.status = 'completed'
            elif self.stats['successful'] > 0:
                upload.status = 'partial'
            else:
                upload.status = 'failed'

            upload.save()

        except Exception as e:
            logger.error(f"CSV processing error: {e}")
            upload.status = 'failed'
            upload.error_log = [{'error': self._sanitize_error_message(str(e))}]
            upload.completed_at = timezone.now()
            upload.save()
            raise ValueError(self._sanitize_error_message(str(e)))

        return upload

    def _sanitize_error_log(self) -> list:
        """Sanitize error log to remove sensitive data"""
        sanitized = []
        for error in self.errors[:100]:  # Limit to 100 errors
            sanitized.append({
                'row': error.get('row', 0),
                'error': self._sanitize_error_message(error.get('error', 'Unknown error')),
                # Don't include raw data in error log
            })
        return sanitized

    def _sanitize_error_message(self, message: str) -> str:
        """Remove potentially sensitive information from error messages"""
        sensitive_patterns = [
            'DETAIL:', 'SQL', 'psycopg2', 'postgresql',
            '/app/', '/home/', 'Traceback', 'File "'
        ]

        message_lower = message.lower()
        for pattern in sensitive_patterns:
            if pattern.lower() in message_lower:
                return 'An error occurred while processing this row.'

        # Truncate long messages
        if len(message) > 200:
            return message[:200] + '...'

        return message

    def _validate_columns(self, df):
        """Validate required columns exist"""
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(missing)}")

    def _process_rows(self, df):
        """Process each row in the dataframe"""
        for index, row in df.iterrows():
            try:
                self._process_row(row, index)
                self.stats['successful'] += 1
            except Exception as e:
                self.stats['failed'] += 1
                self.errors.append({
                    'row': index + 2,  # +2 for header and 0-indexing
                    'error': str(e),
                    # Don't store raw data for security
                })

    @transaction.atomic
    def _process_row(self, row, index):
        """Process a single row with formula injection prevention"""
        # Get or create supplier (sanitize name)
        supplier_name = sanitize_csv_value(str(row['supplier']).strip())
        if not supplier_name or supplier_name == "'":
            raise ValueError("Supplier name is required")

        supplier, _ = Supplier.objects.get_or_create(
            organization=self.organization,
            name=supplier_name,
            defaults={'is_active': True}
        )

        # Get or create category (sanitize name)
        category_name = sanitize_csv_value(str(row['category']).strip())
        if not category_name or category_name == "'":
            raise ValueError("Category name is required")

        category, _ = Category.objects.get_or_create(
            organization=self.organization,
            name=category_name,
            defaults={'is_active': True}
        )

        # Parse date
        try:
            date = pd.to_datetime(row['date']).date()
        except Exception:
            raise ValueError(f"Invalid date format: {row['date']}")

        # Parse and validate amount
        try:
            amount_str = str(row['amount']).replace(',', '').replace('$', '').strip()
            amount = Decimal(amount_str)
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            if amount > Decimal('999999999999.99'):
                raise ValueError("Amount exceeds maximum allowed value")
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Invalid amount value: {row['amount']}")

        # Build optional fields with sanitization
        optional_data = {}
        for col in self.OPTIONAL_COLUMNS:
            if col in row and pd.notna(row[col]):
                # Sanitize all string values to prevent formula injection
                value = str(row[col]).strip()
                optional_data[col] = sanitize_csv_value(value)

        # Get invoice number for uniqueness check
        invoice_number = optional_data.get('invoice_number', '')

        # Use database constraint for duplicate detection (race-condition safe)
        try:
            Transaction.objects.create(
                organization=self.organization,
                uploaded_by=self.user,
                supplier=supplier,
                category=category,
                amount=amount,
                date=date,
                upload_batch=self.batch_id,
                invoice_number=invoice_number,
                **{k: v for k, v in optional_data.items() if k != 'invoice_number'}
            )
        except IntegrityError:
            # Duplicate detected by database constraint
            if self.skip_duplicates:
                self.stats['duplicates'] += 1
                self.stats['successful'] -= 1  # Will be incremented in caller, so offset
                return
            raise ValueError("Duplicate transaction detected")


def get_duplicate_transactions(organization, days=30):
    """
    Find potential duplicate transactions
    """
    from django.db.models import Count
    from datetime import timedelta

    cutoff_date = timezone.now().date() - timedelta(days=days)

    duplicates = Transaction.objects.filter(
        organization=organization,
        date__gte=cutoff_date
    ).values(
        'supplier', 'category', 'amount', 'date'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=1)

    return duplicates


def bulk_delete_transactions(organization, transaction_ids):
    """
    Bulk delete transactions for an organization
    """
    return Transaction.objects.filter(
        organization=organization,
        id__in=transaction_ids
    ).delete()


def export_transactions_to_csv(organization, filters=None):
    """
    Export transactions to CSV format with formula injection prevention
    """
    queryset = Transaction.objects.filter(organization=organization)

    if filters:
        if 'start_date' in filters and filters['start_date']:
            queryset = queryset.filter(date__gte=filters['start_date'])
        if 'end_date' in filters and filters['end_date']:
            queryset = queryset.filter(date__lte=filters['end_date'])
        if 'supplier' in filters and filters['supplier']:
            queryset = queryset.filter(supplier_id=filters['supplier'])
        if 'category' in filters and filters['category']:
            queryset = queryset.filter(category_id=filters['category'])

    # Convert to dataframe
    data = queryset.values(
        'supplier__name', 'category__name', 'amount', 'date',
        'description', 'subcategory', 'location', 'fiscal_year',
        'spend_band', 'payment_method', 'invoice_number'
    )

    df = pd.DataFrame(data)

    # Rename columns
    df.columns = [
        'Supplier', 'Category', 'Amount', 'Date',
        'Description', 'Subcategory', 'Location', 'Fiscal Year',
        'Spend Band', 'Payment Method', 'Invoice Number'
    ]

    # Sanitize all string columns to prevent formula injection in exported CSV
    string_columns = ['Supplier', 'Category', 'Description', 'Subcategory',
                      'Location', 'Spend Band', 'Payment Method', 'Invoice Number']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: sanitize_csv_value(str(x)) if pd.notna(x) else '')

    return df
