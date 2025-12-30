"""
Serializers for procurement data
"""
from rest_framework import serializers
from .models import Supplier, Category, Transaction, DataUpload


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model"""
    transaction_count = serializers.IntegerField(read_only=True)
    total_spend = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'code', 'contact_email', 'contact_phone',
            'address', 'is_active', 'created_at', 'updated_at',
            'transaction_count', 'total_spend'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    transaction_count = serializers.IntegerField(read_only=True)
    total_spend = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'parent', 'parent_name', 'description',
            'is_active', 'created_at', 'updated_at',
            'transaction_count', 'total_spend'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'supplier', 'supplier_name', 'category', 'category_name',
            'amount', 'date', 'description', 'subcategory', 'location',
            'fiscal_year', 'spend_band', 'payment_method', 'invoice_number',
            'upload_batch', 'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'updated_at']


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating transactions"""
    supplier_name = serializers.CharField(write_only=True, required=False)
    category_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Transaction
        fields = [
            'supplier', 'supplier_name', 'category', 'category_name',
            'amount', 'date', 'description', 'subcategory', 'location',
            'fiscal_year', 'spend_band', 'payment_method', 'invoice_number'
        ]

    def validate_supplier(self, value):
        """Ensure supplier belongs to user's organization"""
        if value is None:
            return value
        user_org = self.context['request'].user.profile.organization
        if value.organization_id != user_org.id:
            raise serializers.ValidationError(
                "Supplier does not belong to your organization"
            )
        return value

    def validate_category(self, value):
        """Ensure category belongs to user's organization"""
        if value is None:
            return value
        user_org = self.context['request'].user.profile.organization
        if value.organization_id != user_org.id:
            raise serializers.ValidationError(
                "Category does not belong to your organization"
            )
        return value

    def create(self, validated_data):
        # Get organization from context
        organization = self.context['request'].user.profile.organization
        
        # Handle supplier creation if name provided
        supplier_name = validated_data.pop('supplier_name', None)
        if supplier_name and 'supplier' not in validated_data:
            supplier, _ = Supplier.objects.get_or_create(
                organization=organization,
                name=supplier_name
            )
            validated_data['supplier'] = supplier
        
        # Handle category creation if name provided
        category_name = validated_data.pop('category_name', None)
        if category_name and 'category' not in validated_data:
            category, _ = Category.objects.get_or_create(
                organization=organization,
                name=category_name
            )
            validated_data['category'] = category
        
        # Set organization and user
        validated_data['organization'] = organization
        validated_data['uploaded_by'] = self.context['request'].user
        
        return super().create(validated_data)


class TransactionBulkDeleteSerializer(serializers.Serializer):
    """Serializer for bulk delete operations"""
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )


class DataUploadSerializer(serializers.ModelSerializer):
    """Serializer for DataUpload model"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    
    class Meta:
        model = DataUpload
        fields = [
            'id', 'file_name', 'file_size', 'batch_id',
            'total_rows', 'successful_rows', 'failed_rows', 'duplicate_rows',
            'status', 'error_log', 'uploaded_by', 'uploaded_by_name',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'completed_at']


class CSVUploadSerializer(serializers.Serializer):
    """Serializer for CSV file upload"""
    file = serializers.FileField()
    skip_duplicates = serializers.BooleanField(default=True)
    
    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed")
        
        # Check file size (max 50MB)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 50MB")
        
        return value
