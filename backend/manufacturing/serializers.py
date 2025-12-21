from rest_framework import serializers
from .models import (WorkCenter, BillOfMaterials, BOMItem, BOMOperation,
                     ProductionOrder, MaterialConsumption, QualityCheck, ProductionDowntime)

class WorkCenterSerializer(serializers.ModelSerializer):
    capacity_uom_name = serializers.CharField(source='capacity_uom.name', read_only=True)
    
    class Meta:
        model = WorkCenter
        fields = '__all__'

class BOMItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    uom_symbol = serializers.CharField(source='uom.symbol', read_only=True)
    quantity_with_scrap = serializers.ReadOnlyField()
    total_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = BOMItem
        fields = '__all__'

class BOMOperationSerializer(serializers.ModelSerializer):
    work_center_name = serializers.CharField(source='work_center.name', read_only=True)
    total_time_minutes = serializers.ReadOnlyField()
    operation_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = BOMOperation
        fields = '__all__'

class BillOfMaterialsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    uom_symbol = serializers.CharField(source='uom.symbol', read_only=True)
    items = BOMItemSerializer(many=True, read_only=True)
    operations = BOMOperationSerializer(many=True, read_only=True)
    total_material_cost = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BillOfMaterials
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

class BOMListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    
    class Meta:
        model = BillOfMaterials
        fields = ('id', 'product_name', 'product_code', 'version', 'quantity', 'is_default', 'is_active')

class MaterialConsumptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    uom_symbol = serializers.CharField(source='uom.symbol', read_only=True)
    consumed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MaterialConsumption
        fields = '__all__'
    
    def get_consumed_by_name(self, obj):
        return obj.consumed_by.username if obj.consumed_by else None

class QualityCheckSerializer(serializers.ModelSerializer):
    checked_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = QualityCheck
        fields = '__all__'
    
    def get_checked_by_name(self, obj):
        return obj.checked_by.username if obj.checked_by else None

class ProductionDowntimeSerializer(serializers.ModelSerializer):
    work_center_name = serializers.CharField(source='work_center.name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    reported_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionDowntime
        fields = '__all__'
    
    def get_reported_by_name(self, obj):
        return obj.reported_by.username if obj.reported_by else None

class ProductionOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    bom_version = serializers.CharField(source='bom.version', read_only=True)
    uom_symbol = serializers.CharField(source='uom.symbol', read_only=True)
    material_consumptions = MaterialConsumptionSerializer(many=True, read_only=True)
    quality_checks = QualityCheckSerializer(many=True, read_only=True)
    downtimes = ProductionDowntimeSerializer(many=True, read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    total_estimated_cost = serializers.ReadOnlyField()
    total_actual_cost = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductionOrder
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

class ProductionOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductionOrder
        fields = ('id', 'order_number', 'product_name', 'planned_quantity', 'produced_quantity',
                  'status', 'priority', 'completion_percentage', 'planned_start_date')
