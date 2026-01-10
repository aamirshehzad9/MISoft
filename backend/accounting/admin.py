from django.contrib import admin
from .models import (
    # Legacy models
    FiscalYear, AccountType, ChartOfAccounts, JournalEntry, JournalEntryLine,
    Invoice, InvoiceItem, Payment, PaymentAllocation, BankAccount, TaxCode,
    # V2 models
    AccountV2, CostCenterV2, DepartmentV2, CurrencyV2, ExchangeRateV2,
    TaxMasterV2, TaxGroupV2, TaxGroupItemV2, VoucherV2, VoucherEntryV2,
    FairValueMeasurement, Entity, FXRevaluationLog, NumberingScheme,
    # Approval models
    ApprovalWorkflow, ApprovalLevel, ApprovalRequest, ApprovalAction
)


# ============================================
# LEGACY MODELS ADMIN
# ============================================

@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_closed')
    list_filter = ('is_closed',)


@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_category')
    list_filter = ('type_category',)


@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ('account_code', 'account_name', 'account_type', 'is_active', 'is_header', 'current_balance')
    list_filter = ('account_type', 'is_active', 'is_header')
    search_fields = ('account_code', 'account_name')
    ordering = ('account_code',)


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2
    fields = ('line_number', 'account', 'description', 'debit_amount', 'credit_amount', 'partner')


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('entry_number', 'entry_date', 'entry_type', 'status', 'total_debit', 'total_credit', 'is_balanced')
    list_filter = ('entry_type', 'status', 'entry_date')
    search_fields = ('entry_number', 'reference_number', 'description')
    inlines = [JournalEntryLineInline]
    readonly_fields = ('created_at', 'created_by', 'total_debit', 'total_credit', 'is_balanced')
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('line_number', 'product', 'description', 'quantity', 'unit_price', 'discount_percentage', 'tax_percentage', 'line_total')
    readonly_fields = ('line_total',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'invoice_type', 'partner', 'invoice_date', 'total_amount', 'outstanding_amount', 'status')
    list_filter = ('invoice_type', 'status', 'invoice_date')
    search_fields = ('invoice_number', 'partner__name', 'reference_number')
    inlines = [InvoiceItemInline]
    readonly_fields = ('created_at', 'created_by', 'outstanding_amount')


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 1
    fields = ('invoice', 'allocated_amount')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_number', 'payment_type', 'partner', 'amount', 'payment_date', 'payment_mode')
    list_filter = ('payment_type', 'payment_mode', 'payment_date')
    search_fields = ('payment_number', 'partner__name', 'reference_number')
    inlines = [PaymentAllocationInline]
    readonly_fields = ('created_at', 'created_by')


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_name', 'account_number', 'bank_name', 'currency', 'current_balance', 'is_active')
    list_filter = ('is_active', 'currency')
    search_fields = ('account_name', 'account_number', 'bank_name', 'iban')


@admin.register(TaxCode)
class TaxCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'tax_percentage', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'description')


# ============================================
# V2 MODELS ADMIN
# ============================================

@admin.register(AccountV2)
class AccountV2Admin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'account_group', 'ias_reference_code', 'ifrs_category', 'is_group', 'current_balance', 'is_active']
    list_filter = ['account_type', 'account_group', 'ias_reference_code', 'ifrs_category', 'measurement_basis', 'is_group', 'is_active']
    search_fields = ['code', 'name', 'ias_reference_code', 'ifrs_subcategory']
    ordering = ['code']
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'parent', 'description')
        }),
        ('Classification', {
            'fields': ('account_type', 'account_group')
        }),
        ('IFRS Compliance', {
            'fields': ('ias_reference_code', 'ifrs_category', 'ifrs_subcategory', 'measurement_basis'),
            'description': 'IAS/IFRS compliance fields for international financial reporting standards'
        }),
        ('Properties', {
            'fields': ('is_group', 'is_active', 'allow_direct_posting')
        }),
        ('Balances', {
            'fields': ('opening_balance', 'current_balance')
        }),
        ('Migration', {
            'fields': ('migrated_from_legacy',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['current_balance']


@admin.register(CostCenterV2)
class CostCenterV2Admin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(DepartmentV2)
class DepartmentV2Admin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(CurrencyV2)
class CurrencyV2Admin(admin.ModelAdmin):
    list_display = ['currency_code', 'currency_name', 'symbol', 'is_base_currency', 'is_active']
    list_filter = ['is_base_currency', 'is_active']
    search_fields = ['currency_code', 'currency_name']
    ordering = ['currency_code']


@admin.register(ExchangeRateV2)
class ExchangeRateV2Admin(admin.ModelAdmin):
    list_display = ['from_currency', 'to_currency', 'exchange_rate', 'rate_date']
    list_filter = ['from_currency', 'to_currency', 'rate_date']
    ordering = ['-rate_date']


@admin.register(TaxMasterV2)
class TaxMasterV2Admin(admin.ModelAdmin):
    list_display = ['tax_code', 'tax_name', 'tax_type', 'tax_rate', 'is_active']
    list_filter = ['tax_type', 'is_active']
    search_fields = ['tax_code', 'tax_name']
    ordering = ['tax_code']


@admin.register(TaxGroupV2)
class TaxGroupV2Admin(admin.ModelAdmin):
    list_display = ['group_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['group_name']


@admin.register(TaxGroupItemV2)
class TaxGroupItemV2Admin(admin.ModelAdmin):
    list_display = ['tax_group', 'tax', 'sequence', 'apply_on_previous']
    list_filter = ['tax_group', 'apply_on_previous']
    ordering = ['tax_group', 'sequence']


class VoucherEntryV2Inline(admin.TabularInline):
    model = VoucherEntryV2
    extra = 2
    fields = ['account', 'debit_amount', 'credit_amount', 'cost_center', 'department', 'description']


@admin.register(VoucherV2)
class VoucherV2Admin(admin.ModelAdmin):
    list_display = ['voucher_number', 'voucher_type', 'voucher_date', 'party', 'total_amount', 'status']
    list_filter = ['voucher_type', 'status', 'voucher_date']
    search_fields = ['voucher_number', 'reference_number']
    ordering = ['-voucher_date', '-voucher_number']
    inlines = [VoucherEntryV2Inline]
    fieldsets = (
        ('Voucher Information', {
            'fields': ('voucher_number', 'voucher_type', 'voucher_date', 'reference_number')
        }),
        ('Party & Currency', {
            'fields': ('party', 'currency', 'exchange_rate')
        }),
        ('Amount & Status', {
            'fields': ('total_amount', 'status')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approved_at')
        }),
        ('Narration', {
            'fields': ('narration',)
        }),
        ('Migration', {
            'fields': ('migrated_from_legacy',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['approved_at']


@admin.register(FairValueMeasurement)
class FairValueMeasurementAdmin(admin.ModelAdmin):
    list_display = ['account', 'measurement_date', 'fair_value_level', 'fair_value', 'carrying_amount', 'gain_loss']
    list_filter = ['fair_value_level', 'valuation_technique', 'measurement_purpose', 'measurement_date']
    search_fields = ['account__code', 'account__name', 'external_valuer', 'notes']
    ordering = ['-measurement_date', '-created_at']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('account', 'measurement_date', 'measurement_purpose')
        }),
        ('Fair Value Details', {
            'fields': ('fair_value', 'carrying_amount', 'gain_loss', 'recognized_in_pl')
        }),
        ('IFRS 13 Compliance', {
            'fields': ('fair_value_level', 'valuation_technique', 'valuation_description', 'inputs_used')
        }),
        ('External Valuation', {
            'fields': ('external_valuer', 'valuer_credentials', 'valuation_report_ref'),
            'classes': ('collapse',)
        }),
        ('Accounting Entry', {
            'fields': ('voucher',),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': ('created_by', 'created_at', 'approved_by', 'approved_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )




@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ['entity_code', 'entity_name', 'entity_type', 'functional_currency', 'consolidation_percentage', 'is_active']
    list_filter = ['entity_type', 'consolidation_method', 'functional_currency', 'is_active', 'country']
    search_fields = ['entity_code', 'entity_name', 'short_name', 'registration_number', 'tax_id']
    ordering = ['entity_code']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Entity Identification', {
            'fields': ('entity_code', 'entity_name', 'short_name', 'entity_type')
        }),
        ('Hierarchy', {
            'fields': ('parent_entity',)
        }),
        ('Currency & Location (IAS 21)', {
            'fields': ('country', 'functional_currency', 'presentation_currency')
        }),
        ('Consolidation Settings (IFRS 10)', {
            'fields': ('consolidation_percentage', 'consolidation_method', 'eliminate_intercompany')
        }),
        ('Registration', {
            'fields': ('registration_number', 'tax_id')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'state', 'postal_code', 'phone', 'email'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'activation_date', 'deactivation_date')
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(FXRevaluationLog)
class FXRevaluationLogAdmin(admin.ModelAdmin):
    list_display = ['revaluation_id', 'entity', 'revaluation_date', 'net_fx_gain_loss', 'status', 'voucher', 'created_at']
    list_filter = ['status', 'execution_method', 'auto_posted', 'reversal_created', 'revaluation_date', 'entity']
    search_fields = ['revaluation_id', 'entity__entity_code', 'entity__entity_name', 'voucher__voucher_number']
    ordering = ['-revaluation_date', '-created_at']
    readonly_fields = ['revaluation_id', 'created_at', 'is_successful', 'has_fx_impact']
    
    fieldsets = (
        ('Revaluation Information', {
            'fields': ('revaluation_id', 'entity', 'revaluation_date', 'functional_currency')
        }),
        ('Results', {
            'fields': ('accounts_revalued', 'total_gain', 'total_loss', 'net_fx_gain_loss', 'is_successful', 'has_fx_impact')
        }),
        ('Vouchers', {
            'fields': ('voucher', 'reversal_voucher')
        }),
        ('Execution Details', {
            'fields': ('status', 'execution_method', 'auto_posted', 'reversal_created')
        }),
        ('Detailed Results', {
            'fields': ('revaluation_details',),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(NumberingScheme)
class NumberingSchemeAdmin(admin.ModelAdmin):
    list_display = ['scheme_name', 'document_type', 'preview_number', 'next_number', 'reset_frequency', 'is_active', 'entity']
    list_filter = ['document_type', 'reset_frequency', 'is_active', 'entity']
    search_fields = ['scheme_name', 'prefix', 'suffix']
    ordering = ['document_type', 'scheme_name']
    readonly_fields = ['created_at', 'updated_at', 'preview_number']
    actions = ['reset_counter_action', 'activate_schemes', 'deactivate_schemes']
    
    fieldsets = (
        ('Scheme Information', {
            'fields': ('scheme_name', 'document_type', 'entity')
        }),
        ('Format Configuration', {
            'fields': ('prefix', 'date_format', 'separator', 'padding', 'suffix')
        }),
        ('Sequence Management', {
            'fields': ('next_number', 'reset_frequency', 'last_reset_date')
        }),
        ('Preview', {
            'fields': ('preview_number',),
            'description': 'Preview of the next generated number'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    
    def preview_number(self, obj):
        """Display preview of next number"""
        if obj.pk:
            return obj.generate_preview()
        return '-'
    preview_number.short_description = 'Next Number Preview'
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    @admin.action(description='Reset counter to 1')
    def reset_counter_action(self, request, queryset):
        """Reset counter for selected schemes"""
        from datetime import date
        
        count = 0
        for scheme in queryset:
            scheme.next_number = 1
            scheme.last_reset_date = date.today()
            scheme.save()
            count += 1
        
        self.message_user(
            request,
            f'Successfully reset {count} numbering scheme(s) to 1.'
        )
    
    @admin.action(description='Activate selected schemes')
    def activate_schemes(self, request, queryset):
        """Activate selected schemes"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Successfully activated {updated} numbering scheme(s).'
        )
    
    @admin.action(description='Deactivate selected schemes')
    def deactivate_schemes(self, request, queryset):
        """Deactivate selected schemes"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Successfully deactivated {updated} numbering scheme(s).'
        )


# ============================================
# APPROVAL WORKFLOW ADMIN
# ============================================

class ApprovalLevelInline(admin.TabularInline):
    model = ApprovalLevel
    extra = 1
    fields = ['level_number', 'approver', 'min_amount', 'max_amount', 'is_mandatory']
    ordering = ['level_number']


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ['workflow_name', 'document_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['document_type', 'is_active']
    search_fields = ['workflow_name']
    inlines = [ApprovalLevelInline]
    ordering = ['workflow_name']
    
    fieldsets = (
        ('Workflow Details', {
            'fields': ('workflow_name', 'description')
        }),
        ('Configuration', {
            'fields': ('document_type', 'is_active')
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at')
        }),
    )
    readonly_fields = ['created_at']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ApprovalActionInline(admin.TabularInline):
    model = ApprovalAction
    extra = 0
    fields = ['action', 'approver', 'action_date', 'comments', 'ip_address']
    readonly_fields = ['action', 'approver', 'action_date', 'comments', 'ip_address']
    can_delete = False
    ordering = ['-action_date']


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['document_type', 'document_id', 'requester', 'amount', 'status', 'current_level', 'current_approver', 'request_date']
    list_filter = ['status', 'document_type', 'workflow']
    search_fields = ['document_id', 'requester__username']
    inlines = [ApprovalActionInline]
    readonly_fields = ['request_date', 'completion_date']
    ordering = ['-request_date']
    
    fieldsets = (
        ('Request Details', {
            'fields': ('workflow', 'document_type', 'document_id', 'amount', 'requester')
        }),
        ('Status', {
            'fields': ('status', 'current_level', 'current_approver')
        }),
        ('Timestamps', {
            'fields': ('request_date', 'completion_date')
        }),
    )


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    list_display = ['approval_request', 'action', 'approver', 'action_date']
    list_filter = ['action', 'action_date']
    search_fields = ['approver__username', 'comments']
    readonly_fields = ['approval_request', 'approver', 'action', 'comments', 'ip_address', 'action_date']
    ordering = ['-action_date']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


