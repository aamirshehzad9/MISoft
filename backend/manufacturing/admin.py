from django.contrib import admin
from .models import (WorkCenter, BillOfMaterials, BOMItem, BOMOperation,
                     ProductionOrder, MaterialConsumption, QualityCheck, ProductionDowntime)

@admin.register(WorkCenter)
class WorkCenterAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'capacity_per_hour', 'hourly_rate', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')

class BOMItemInline(admin.TabularInline):
    model = BOMItem
    extra = 1
    fields = ('sequence', 'item_type', 'product', 'quantity', 'uom', 'scrap_percentage')

class BOMOperationInline(admin.TabularInline):
    model = BOMOperation
    extra = 1
    fields = ('sequence', 'operation_name', 'work_center', 'setup_time_minutes', 'run_time_minutes')

@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'version', 'quantity', 'is_default', 'is_active')
    list_filter = ('is_active', 'is_default', 'bom_type')
    search_fields = ('product__name', 'product__code', 'version')
    inlines = [BOMItemInline, BOMOperationInline]
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'product', 'planned_quantity', 'produced_quantity', 'status', 'priority')
    list_filter = ('status', 'priority', 'planned_start_date')
    search_fields = ('order_number', 'product__name', 'batch_number', 'lot_number')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'completion_percentage')
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'product', 'bom', 'batch_number', 'lot_number')
        }),
        ('Quantity', {
            'fields': ('planned_quantity', 'produced_quantity', 'rejected_quantity', 'uom', 'completion_percentage')
        }),
        ('Schedule', {
            'fields': ('planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Estimated Costs', {
            'fields': ('estimated_material_cost', 'estimated_labor_cost', 'estimated_overhead_cost'),
            'classes': ('collapse',)
        }),
        ('Actual Costs', {
            'fields': ('actual_material_cost', 'actual_labor_cost', 'actual_overhead_cost'),
            'classes': ('collapse',)
        }),
        ('Notes & Metadata', {
            'fields': ('notes', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(MaterialConsumption)
class MaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ('production_order', 'product', 'consumed_quantity', 'uom', 'total_cost', 'consumed_at')
    list_filter = ('consumed_at',)
    search_fields = ('production_order__order_number', 'product__name', 'batch_number')

@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = ('production_order', 'check_name', 'status', 'checked_at', 'checked_by')
    list_filter = ('status', 'check_type', 'checked_at')
    search_fields = ('production_order__order_number', 'check_name', 'parameter_name')

@admin.register(ProductionDowntime)
class ProductionDowntimeAdmin(admin.ModelAdmin):
    list_display = ('production_order', 'work_center', 'downtime_type', 'start_time', 'duration_minutes')
    list_filter = ('downtime_type', 'work_center', 'start_time')
    search_fields = ('production_order__order_number', 'description')
