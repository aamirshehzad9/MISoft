from django.contrib import admin
from .models import ProductCategory, UnitOfMeasure, Product, ProductVariant

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'uom_type', 'is_active')
    list_filter = ('uom_type', 'is_active')
    search_fields = ('name', 'symbol')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'product_type', 'selling_price', 'is_active')
    list_filter = ('product_type', 'category', 'is_active', 'is_manufactured', 'track_batches')
    search_fields = ('name', 'code', 'barcode', 'hs_code')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'barcode', 'qr_code', 'category', 'product_type')
        }),
        ('Description', {
            'fields': ('description', 'specifications', 'image')
        }),
        ('Units of Measure', {
            'fields': ('base_uom', 'purchase_uom', 'sales_uom', 'purchase_to_base_factor', 'sales_to_base_factor')
        }),
        ('Inventory Tracking', {
            'fields': ('track_inventory', 'track_batches', 'track_serial_numbers')
        }),
        ('Stock Levels', {
            'fields': ('minimum_stock', 'maximum_stock', 'reorder_point', 'reorder_quantity', 'storage_location', 'shelf_life_days')
        }),
        ('Pricing', {
            'fields': ('standard_cost', 'last_purchase_price', 'selling_price')
        }),
        ('Suppliers & Tax', {
            'fields': ('preferred_vendor', 'tax_category', 'hs_code')
        }),
        ('Manufacturing', {
            'fields': ('is_manufactured', 'manufacturing_lead_time_days')
        }),
        ('Status', {
            'fields': ('is_active', 'is_purchasable', 'is_saleable')
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

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('variant_code', 'product', 'variant_name', 'price_adjustment', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('variant_name', 'variant_code', 'barcode')
