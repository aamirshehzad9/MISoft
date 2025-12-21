from rest_framework import serializers
from .models import ProductCategory, UnitOfMeasure, Product, ProductVariant

class ProductCategorySerializer(serializers.ModelSerializer):
    full_path = serializers.ReadOnlyField()
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = '__all__'
    
    def get_children_count(self, obj):
        return obj.children.count()

class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    base_uom_name = serializers.CharField(source='base_uom.name', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    current_stock = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'current_stock')
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    base_uom_symbol = serializers.CharField(source='base_uom.symbol', read_only=True)
    
    class Meta:
        model = Product
        fields = ('id', 'code', 'name', 'category_name', 'product_type', 'base_uom_symbol',
                  'selling_price', 'minimum_stock', 'is_active')
