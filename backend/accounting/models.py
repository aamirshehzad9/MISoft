from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from partners.models import BusinessPartner

User = get_user_model()


# ============================================
# LEGACY MODELS (Existing - Keep for now)
# ============================================
# These models will remain active during migration
# They will be gradually phased out after data migration

class FiscalYear(models.Model):
    """Fiscal year management - LEGACY"""
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-start_date']
        db_table = 'accounting_fiscalyear'
    
    def __str__(self):
        return self.name


class AccountType(models.Model):
    """Account types for Chart of Accounts - LEGACY"""
    TYPE_CHOICES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    name = models.CharField(max_length=50)
    type_category = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['type_category', 'name']
        db_table = 'accounting_accounttype'
    
    def __str__(self):
        return f"{self.name} ({self.get_type_category_display()})"


class ChartOfAccounts(models.Model):
    """Chart of Accounts - LEGACY (will be replaced by AccountV2)"""
    account_code = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT, related_name='accounts')
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_accounts')
    currency = models.CharField(max_length=3, default='PKR')
    is_active = models.BooleanField(default=True)
    is_header = models.BooleanField(default=False, help_text="Header account (no direct posting)")
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    opening_balance_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['account_code']
        verbose_name = "Chart of Accounts (Legacy)"
        verbose_name_plural = "Chart of Accounts (Legacy)"
        db_table = 'accounting_chartofaccounts'
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"
    
    @property
    def current_balance(self):
        return self.opening_balance


class JournalEntry(models.Model):
    """Journal Entry Header - LEGACY"""
    ENTRY_TYPE_CHOICES = [
        ('general', 'General Journal'),
        ('sales', 'Sales Journal'),
        ('purchase', 'Purchase Journal'),
        ('cash_receipt', 'Cash Receipt'),
        ('cash_payment', 'Cash Payment'),
        ('bank', 'Bank Journal'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ]
    
    entry_number = models.CharField(max_length=50, unique=True)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES, default='general')
    entry_date = models.DateField()
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name='journal_entries')
    reference_number = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    posted_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_journal_entries')
    
    class Meta:
        ordering = ['-entry_date', '-entry_number']
        verbose_name_plural = "Journal Entries (Legacy)"
        db_table = 'accounting_journalentry'
    
    def __str__(self):
        return f"{self.entry_number} - {self.entry_date}"
    
    @property
    def total_debit(self):
        return sum(line.debit_amount for line in self.lines.all())
    
    @property
    def total_credit(self):
        return sum(line.credit_amount for line in self.lines.all())
    
    @property
    def is_balanced(self):
        return abs(self.total_debit - self.total_credit) < Decimal('0.01')


class JournalEntryLine(models.Model):
    """Journal Entry Lines - LEGACY"""
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    line_number = models.IntegerField(default=1)
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='journal_lines')
    description = models.CharField(max_length=500, blank=True)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    partner = models.ForeignKey(BusinessPartner, on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_lines')
    
    class Meta:
        ordering = ['line_number']
        db_table = 'accounting_journalentryline'
    
    def __str__(self):
        return f"{self.account.account_code} - Dr: {self.debit_amount}, Cr: {self.credit_amount}"


class Invoice(models.Model):
    """Sales and Purchase Invoices - LEGACY"""
    INVOICE_TYPE_CHOICES = [
        ('sales', 'Sales Invoice'),
        ('purchase', 'Purchase Invoice'),
        ('sales_return', 'Sales Return'),
        ('purchase_return', 'Purchase Return'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    invoice_date = models.DateField()
    due_date = models.DateField()
    partner = models.ForeignKey(BusinessPartner, on_delete=models.PROTECT, related_name='invoices')
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    reference_number = models.CharField(max_length=100, blank=True)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    notes = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    
    class Meta:
        ordering = ['-invoice_date', '-invoice_number']
        db_table = 'accounting_invoice'
    
    def __str__(self):
        return f"{self.invoice_number} - {self.partner.name}"
    
    @property
    def outstanding_amount(self):
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.outstanding_amount > 0


class InvoiceItem(models.Model):
    """Invoice line items - LEGACY"""
    from products.models import Product
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    line_number = models.IntegerField(default=1)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='invoice_items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=12, decimal_places=4)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['line_number']
        db_table = 'accounting_invoiceitem'
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_percentage / Decimal('100'))
        taxable = subtotal - discount
        tax = taxable * (self.tax_percentage / Decimal('100'))
        self.line_total = taxable + tax
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment transactions - LEGACY"""
    PAYMENT_TYPE_CHOICES = [
        ('receipt', 'Receipt'),
        ('payment', 'Payment'),
    ]
    
    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('online', 'Online Payment'),
    ]
    
    payment_number = models.CharField(max_length=50, unique=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    payment_date = models.DateField()
    partner = models.ForeignKey(BusinessPartner, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True, help_text="Cheque/Transaction number")
    bank_account = models.ForeignKey('BankAccount', on_delete=models.PROTECT, null=True, blank=True, related_name='payments')
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payments')
    
    class Meta:
        ordering = ['-payment_date', '-payment_number']
        db_table = 'accounting_payment'
    
    def __str__(self):
        return f"{self.payment_number} - {self.amount}"


class PaymentAllocation(models.Model):
    """Allocate payments to invoices - LEGACY"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='allocations')
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payment_allocations')
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        unique_together = [['payment', 'invoice']]
        db_table = 'accounting_paymentallocation'
    
    def __str__(self):
        return f"{self.payment.payment_number} -> {self.invoice.invoice_number}: {self.allocated_amount}"


class BankAccount(models.Model):
    """Bank account master - LEGACY"""
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200, blank=True)
    iban = models.CharField(max_length=50, blank=True)
    swift_code = models.CharField(max_length=20, blank=True)
    gl_account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='bank_accounts')
    currency = models.CharField(max_length=3, default='PKR')
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['account_name']
        db_table = 'accounting_bankaccount'
    
    def __str__(self):
        return f"{self.account_name} - {self.account_number}"
    
    @property
    def current_balance(self):
        return self.opening_balance


class TaxCode(models.Model):
    """Tax codes for GST/VAT - LEGACY"""
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    sales_tax_account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='sales_tax_codes')
    purchase_tax_account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='purchase_tax_codes')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['code']
        db_table = 'accounting_taxcode'
    
    def __str__(self):
        return f"{self.code} - {self.tax_percentage}%"


# ============================================
# NEW ENHANCED MODELS (V2 - Coexist with Legacy)
# ============================================
# These are the new world-class models
# They will gradually replace the legacy models

class AccountV2(models.Model):
    """Enhanced Hierarchical Chart of Accounts - NEW VERSION"""
    
    ACCOUNT_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    ACCOUNT_GROUPS = [
        # Assets
        ('current_asset', 'Current Asset'),
        ('fixed_asset', 'Fixed Asset'),
        ('investment', 'Investment'),
        ('other_asset', 'Other Asset'),
        # Liabilities
        ('current_liability', 'Current Liability'),
        ('long_term_liability', 'Long Term Liability'),
        ('other_liability', 'Other Liability'),
        # Equity
        ('capital', 'Capital'),
        ('retained_earnings', 'Retained Earnings'),
        ('drawings', 'Drawings'),
        # Revenue
        ('sales', 'Sales'),
        ('other_income', 'Other Income'),
        # Expense
        ('direct_expense', 'Direct Expense'),
        ('indirect_expense', 'Indirect Expense'),
        ('operating_expense', 'Operating Expense'),
    ]
    
    # Hierarchical structure
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )
    
    # Account identification
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    
    # Classification
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_group = models.CharField(max_length=50, choices=ACCOUNT_GROUPS)
    
    # Properties
    is_group = models.BooleanField(default=False, help_text="Group accounts cannot have direct postings")
    is_active = models.BooleanField(default=True)
    allow_direct_posting = models.BooleanField(default=True)
    
    # Balances
    opening_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Description
    description = models.TextField(blank=True)
    
    # Migration tracking
    migrated_from_legacy = models.ForeignKey(
        ChartOfAccounts,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Legacy account this was migrated from"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='accounts_v2_created'
    )
    
    class Meta:
        ordering = ['code']
        verbose_name = 'Account (V2)'
        verbose_name_plural = 'Chart of Accounts (V2 - Enhanced)'
        db_table = 'accounting_account_v2'
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_full_path(self):
        """Get full hierarchical path"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_balance(self):
        """Calculate current balance based on account type"""
        return self.current_balance
    
    def update_balance(self, debit_amount, credit_amount):
        """Update account balance based on account type"""
        if self.account_type in ['asset', 'expense']:
            # Debit increases, Credit decreases
            self.current_balance += (debit_amount - credit_amount)
        else:  # liability, equity, revenue
            # Credit increases, Debit decreases
            self.current_balance += (credit_amount - debit_amount)
        self.save()


# ============================================
# COST CENTERS & DEPARTMENTS (V2)
# ============================================

class CostCenterV2(models.Model):
    """Cost center for expense tracking - V2"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = 'Cost Center (V2)'
        verbose_name_plural = 'Cost Centers (V2)'
        db_table = 'accounting_costcenter_v2'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class DepartmentV2(models.Model):
    """Department for organizational tracking - V2"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = 'Department (V2)'
        verbose_name_plural = 'Departments (V2)'
        db_table = 'accounting_department_v2'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ============================================
# MULTI-CURRENCY SUPPORT (V2)
# ============================================

class CurrencyV2(models.Model):
    """Currency master - V2"""
    currency_code = models.CharField(max_length=3, unique=True)  # USD, EUR, GBP, PKR
    currency_name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    is_base_currency = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Currency (V2)'
        verbose_name_plural = 'Currencies (V2)'
        ordering = ['currency_code']
        db_table = 'accounting_currency_v2'
    
    def __str__(self):
        return f"{self.currency_code} - {self.currency_name}"


class ExchangeRateV2(models.Model):
    """Daily exchange rates - V2"""
    from_currency = models.ForeignKey(
        CurrencyV2,
        on_delete=models.CASCADE,
        related_name='rates_from_v2'
    )
    to_currency = models.ForeignKey(
        CurrencyV2,
        on_delete=models.CASCADE,
        related_name='rates_to_v2'
    )
    rate_date = models.DateField()
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_currency', 'to_currency', 'rate_date']
        ordering = ['-rate_date']
        verbose_name = 'Exchange Rate (V2)'
        verbose_name_plural = 'Exchange Rates (V2)'
        db_table = 'accounting_exchangerate_v2'
    
    def __str__(self):
        return f"{self.from_currency.currency_code} to {self.to_currency.currency_code} @ {self.exchange_rate} on {self.rate_date}"


# ============================================
# TAX SYSTEM (V2)
# ============================================

class TaxMasterV2(models.Model):
    """Tax master with rates and accounts - V2"""
    TAX_TYPES = [
        ('vat', 'VAT'),
        ('gst', 'GST'),
        ('sales_tax', 'Sales Tax'),
        ('service_tax', 'Service Tax'),
        ('excise', 'Excise Duty'),
        ('customs', 'Customs Duty'),
    ]
    
    tax_code = models.CharField(max_length=20, unique=True)
    tax_name = models.CharField(max_length=100)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPES)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Tax accounts
    tax_collected_account = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        related_name='tax_collected_for_v2'
    )
    tax_paid_account = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        related_name='tax_paid_for_v2'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tax Master (V2)'
        verbose_name_plural = 'Tax Masters (V2)'
        ordering = ['tax_code']
        db_table = 'accounting_taxmaster_v2'
    
    def __str__(self):
        return f"{self.tax_code} - {self.tax_name} ({self.tax_rate}%)"


class TaxGroupV2(models.Model):
    """Tax group for compound taxes - V2"""
    group_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tax Group (V2)'
        verbose_name_plural = 'Tax Groups (V2)'
        db_table = 'accounting_taxgroup_v2'
    
    def __str__(self):
        return self.group_name


class TaxGroupItemV2(models.Model):
    """Tax items in a tax group - V2"""
    tax_group = models.ForeignKey(TaxGroupV2, on_delete=models.CASCADE, related_name='items_v2')
    tax = models.ForeignKey(TaxMasterV2, on_delete=models.CASCADE, related_name='group_items_v2')
    sequence = models.IntegerField(default=1)
    apply_on_previous = models.BooleanField(
        default=False,
        help_text="Apply this tax on previous tax amount (compound tax)"
    )
    
    class Meta:
        ordering = ['sequence']
        unique_together = ['tax_group', 'tax']
        verbose_name = 'Tax Group Item (V2)'
        verbose_name_plural = 'Tax Group Items (V2)'
        db_table = 'accounting_taxgroupitem_v2'
    
    def __str__(self):
        return f"{self.tax_group.group_name} - {self.tax.tax_name}"


# ============================================
# VOUCHER SYSTEM (V2 - Double-Entry)
# ============================================

class VoucherV2(models.Model):
    """Universal voucher for all accounting transactions - V2"""
    
    VOUCHER_TYPES = [
        ('JE', 'Journal Entry'),
        ('SI', 'Sales Invoice'),
        ('PI', 'Purchase Invoice'),
        ('CPV', 'Cash Payment Voucher'),
        ('BPV', 'Bank Payment Voucher'),
        ('CRV', 'Cash Receipt Voucher'),
        ('BRV', 'Bank Receipt Voucher'),
        ('DN', 'Debit Note'),
        ('CN', 'Credit Note'),
        ('CE', 'Contra Entry'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Identification
    voucher_number = models.CharField(max_length=50, unique=True)
    voucher_type = models.CharField(max_length=10, choices=VOUCHER_TYPES)
    voucher_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Party
    party = models.ForeignKey(
        BusinessPartner,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='vouchers_v2'
    )
    
    # Amounts
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Currency
    currency = models.ForeignKey(
        CurrencyV2,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='vouchers_v2'
    )
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000')
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vouchers_v2_approved'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Narration
    narration = models.TextField(blank=True)
    
    # Migration tracking
    migrated_from_legacy = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Legacy journal entry this was migrated from"
    )
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vouchers_v2_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-voucher_date', '-voucher_number']
        verbose_name = 'Voucher (V2)'
        verbose_name_plural = 'Vouchers (V2)'
        db_table = 'accounting_voucher_v2'
    
    def __str__(self):
        return f"{self.voucher_type} - {self.voucher_number}"
    
    def validate_double_entry(self):
        """Validate that debits equal credits"""
        total_debit = sum(
            entry.debit_amount for entry in self.entries_v2.all()
        )
        total_credit = sum(
            entry.credit_amount for entry in self.entries_v2.all()
        )
        
        if total_debit != total_credit:
            raise ValueError(
                f"Debits ({total_debit}) must equal Credits ({total_credit})"
            )
        return True
    
    def post(self):
        """Post voucher and update account balances"""
        from django.db import transaction
        
        if self.status == 'posted':
            raise ValueError("Voucher is already posted")
        
        self.validate_double_entry()
        
        with transaction.atomic():
            # Update account balances
            for entry in self.entries_v2.all():
                entry.account.update_balance(
                    entry.debit_amount,
                    entry.credit_amount
                )
            
            # Update status
            self.status = 'posted'
            self.save()
        
        return True


class VoucherEntryV2(models.Model):
    """Double-entry voucher lines - V2"""
    voucher = models.ForeignKey(
        VoucherV2,
        on_delete=models.CASCADE,
        related_name='entries_v2'
    )
    account = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        related_name='voucher_entries_v2'
    )
    
    # Double-entry amounts
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Cost tracking
    cost_center = models.ForeignKey(
        CostCenterV2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voucher_entries_v2'
    )
    department = models.ForeignKey(
        DepartmentV2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voucher_entries_v2'
    )
    
    # Currency amount (for multi-currency)
    currency_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Description
    description = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['id']
        verbose_name = 'Voucher Entry (V2)'
        verbose_name_plural = 'Voucher Entries (V2)'
        db_table = 'accounting_voucherentry_v2'
    
    def __str__(self):
        return f"{self.voucher.voucher_number} - {self.account.name}"
    
    def clean(self):
        """Validate that either debit or credit is non-zero, but not both"""
        from django.core.exceptions import ValidationError
        
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValidationError("Entry cannot have both debit and credit amounts")
        
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValidationError("Entry must have either debit or credit amount")
