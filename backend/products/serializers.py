"""
UoM Conversion Serializers
"""
from rest_framework import serializers
from products.models import UoMConversion, UnitOfMeasure, Product, ProductVariant


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product"""
    
    # Backward compatibility: map uom to base_uom for frontend
    uom = serializers.PrimaryKeyRelatedField(source='base_uom', read_only=True)
    uom_name = serializers.CharField(source='base_uom.name', read_only=True)
    uom_symbol = serializers.CharField(source='base_uom.symbol', read_only=True)
    
    # New fields with correct names
    base_uom_name = serializers.CharField(source='base_uom.name', read_only=True)
    base_uom_symbol = serializers.CharField(source='base_uom.symbol', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'description', 'category', 'category_name',
            'base_uom', 'base_uom_name', 'base_uom_symbol',
            'uom', 'uom_name', 'uom_symbol',  # Backward compatibility
            'standard_cost', 'selling_price', 'product_type',
            'minimum_stock', 'maximum_stock', 'reorder_point',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']



class UnitOfMeasureSerializer(serializers.ModelSerializer):
    """Serializer for UnitOfMeasure"""
    
    class Meta:
        model = UnitOfMeasure
        fields = ['id', 'name', 'symbol', 'uom_type', 'is_active']


class UoMConversionSerializer(serializers.ModelSerializer):
    """Serializer for UoMConversion"""
    
    from_uom_detail = UnitOfMeasureSerializer(source='from_uom', read_only=True)
    to_uom_detail = UnitOfMeasureSerializer(source='to_uom', read_only=True)
    conversion_type_display = serializers.CharField(source='get_conversion_type_display', read_only=True)
    
    class Meta:
        model = UoMConversion
        fields = [
            'id', 'from_uom', 'to_uom', 'from_uom_detail', 'to_uom_detail',
            'conversion_type', 'conversion_type_display', 'multiplier', 'formula',
            'is_active', 'is_bidirectional', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductVariantQuickCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for quick-creating product variants from voucher/invoice forms
    Task 1.6.2: AJAX Variant Creation
    
    Validates:
    - Required fields (product, variant_name, variant_code)
    - Unique variant_code across all variants
    - Unique barcode (if provided)
    - Valid price_adjustment format
    """
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'variant_name', 'variant_code',
            'price_adjustment', 'barcode', 'is_active'
        ]
        read_only_fields = ['id', 'is_active']
    
    def validate_variant_code(self, value):
        """Ensure variant code is unique across all variants"""
        if ProductVariant.objects.filter(variant_code=value).exists():
            raise serializers.ValidationError(
                f"Variant with code '{value}' already exists. Please use a unique code."
            )
        return value
    
    def validate_barcode(self, value):
        """Ensure barcode is unique if provided"""
        if value:  # Only validate if barcode is provided
            if ProductVariant.objects.filter(barcode=value).exists():
                raise serializers.ValidationError(
                    f"Barcode '{value}' is already in use. Please use a unique barcode."
                )
        return value
    
    def validate_product(self, value):
        """Ensure product exists and is active"""
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot create variant for inactive product."
            )
        return value
    
    def create(self, validated_data):
        """Create variant with default is_active=True"""
        # Ensure is_active is True by default
        validated_data['is_active'] = True
        
        # Set price_adjustment to 0 if not provided
        if 'price_adjustment' not in validated_data:
            validated_data['price_adjustment'] = 0
        
        return super().create(validated_data)
