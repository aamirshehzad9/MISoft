from django.contrib import admin
from .models import (
    # Legacy models
    FiscalYear, AccountType, ChartOfAccounts, JournalEntry, JournalEntryLine,
    Invoice, InvoiceItem, Payment, PaymentAllocation, BankAccount, TaxCode,
    # V2 models
    AccountV2, CostCenterV2, DepartmentV2, CurrencyV2, ExchangeRateV2,
    TaxMasterV2, TaxGroupV2, TaxGroupItemV2, VoucherV2, VoucherEntryV2
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
    list_display = ['code', 'name', 'account_type', 'account_group', 'is_group', 'current_balance', 'is_active']
    list_filter = ['account_type', 'account_group', 'is_group', 'is_active']
    search_fields = ['code', 'name']
    ordering = ['code']
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'parent', 'description')
        }),
        ('Classification', {
            'fields': ('account_type', 'account_group')
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
