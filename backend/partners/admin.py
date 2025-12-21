from django.contrib import admin
from .models import BusinessPartner

@admin.register(BusinessPartner)
class BusinessPartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'partner_type_display', 'phone', 'email', 'outstanding_balance', 'is_active')
    list_filter = ('is_customer', 'is_vendor', 'is_active', 'created_at')
    search_fields = ('name', 'company_name', 'email', 'phone', 'tax_id')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company_name', 'contact_person')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'mobile')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Partner Type', {
            'fields': ('is_customer', 'is_vendor')
        }),
        ('Financial Information', {
            'fields': ('credit_limit', 'outstanding_balance', 'payment_terms_days', 'tax_id')
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
