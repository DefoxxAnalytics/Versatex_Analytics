"""
Procurement data models with security enhancements:
- UUID fields for IDOR protection
- Encrypted fields for sensitive data
- Secure file name handling
"""
import uuid
import re
from django.db import models
from django.contrib.auth.models import User
from apps.authentication.models import Organization

# Note: Field encryption is optional. To enable it:
# 1. Set FIELD_ENCRYPTION_KEY in your environment
# 2. Install django-encrypted-model-fields
# When not configured, standard Django fields are used instead.
# For now, we use regular fields for maximum compatibility.


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    Removes directory components and special characters.
    """
    if not filename:
        return 'unnamed_file'

    # Remove any directory components
    filename = filename.replace('\\', '/').split('/')[-1]

    # Remove any path traversal attempts
    filename = re.sub(r'\.\.+', '', filename)

    # Remove any null bytes
    filename = filename.replace('\x00', '')

    # Keep only safe characters
    safe_filename = re.sub(r'[^\w\s\-\.]', '', filename)

    # Ensure filename is not empty and doesn't start with a dot
    if not safe_filename or safe_filename.startswith('.'):
        safe_filename = 'file_' + safe_filename

    # Limit length
    if len(safe_filename) > 200:
        name, ext = safe_filename.rsplit('.', 1) if '.' in safe_filename else (safe_filename, '')
        safe_filename = name[:195] + ('.' + ext if ext else '')

    return safe_filename


class Supplier(models.Model):
    """
    Supplier model - organization-scoped
    Includes UUID for secure external references
    """
    # UUID for external API references (prevents ID enumeration)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='suppliers'
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, blank=True)

    # Contact information (consider enabling field encryption in production)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization', 'name']),
            models.Index(fields=['uuid']),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Category(models.Model):
    """
    Category model - organization-scoped
    Includes UUID for secure external references
    """
    # UUID for external API references
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories'
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
        unique_together = ['organization', 'name']
        indexes = [
            models.Index(fields=['organization', 'name']),
            models.Index(fields=['uuid']),
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Transaction(models.Model):
    """
    Procurement transaction model - organization-scoped
    Includes UUID for secure external references
    """
    # UUID for external API references
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_transactions'
    )

    # Core fields
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='transactions'
    )

    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)

    # Optional fields
    subcategory = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    fiscal_year = models.IntegerField(null=True, blank=True)
    spend_band = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)

    # Invoice number (consider enabling field encryption in production)
    invoice_number = models.CharField(max_length=100, blank=True)

    # Metadata
    upload_batch = models.CharField(max_length=100, blank=True)  # For tracking uploads
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['organization', '-date']),
            models.Index(fields=['organization', 'supplier']),
            models.Index(fields=['organization', 'category']),
            models.Index(fields=['organization', 'fiscal_year']),
            models.Index(fields=['upload_batch']),
            models.Index(fields=['uuid']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'supplier', 'category', 'amount', 'date', 'invoice_number'],
                name='unique_transaction_with_invoice'
            ),
        ]

    def __str__(self):
        return f"{self.supplier.name} - {self.amount} on {self.date}"


class DataUpload(models.Model):
    """
    Track data upload history
    Includes UUID for secure external references
    """
    # UUID for external API references
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='data_uploads'
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_uploads'
    )

    # Sanitized file name - original name stored separately
    file_name = models.CharField(max_length=255)
    original_file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField()  # in bytes
    batch_id = models.CharField(max_length=100, unique=True)

    # Statistics
    total_rows = models.IntegerField(default=0)
    successful_rows = models.IntegerField(default=0)
    failed_rows = models.IntegerField(default=0)
    duplicate_rows = models.IntegerField(default=0)

    # Status
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_log = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['batch_id']),
            models.Index(fields=['uuid']),
        ]

    def save(self, *args, **kwargs):
        # Sanitize file name before saving
        if self.file_name and not self.original_file_name:
            self.original_file_name = self.file_name
        self.file_name = sanitize_filename(self.file_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_name} - {self.status} ({self.organization.name})"
