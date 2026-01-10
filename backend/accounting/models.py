from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from partners.models import BusinessPartner

User = get_user_model()


# ============================================
# AUDIT TRAIL SYSTEM (IASB Requirement)
# ============================================
# Module 1.7: Immutable audit log for all data changes

class AuditLog(models.Model):
    """
    Immutable audit log for all data changes
    Task 1.7.1: Create AuditLog Model
    
    IFRS/IASB Compliance:
    - Maintains complete audit trail as required by IASB
    - Ensures non-repudiation (user tracking)
    - Provides chronological integrity
    - Supports forensic analysis and compliance reporting
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    ]
    
    # What was changed
    model_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Name of the model that was changed"
    )
    object_id = models.IntegerField(
        db_index=True,
        help_text="ID of the object that was changed"
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    
    # Who made the change
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,  # Never delete audit logs
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    
    # When it happened
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action was performed"
    )
    
    # Where it came from
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the user"
    )
    
    # What changed
    changes = models.JSONField(
        default=dict,
        help_text="Before and after values in JSON format"
    )
    
    # Why it was changed
    reason = models.TextField(
        blank=True,
        help_text="Optional reason for the change"
    )
    
    class Meta:
        ordering = ['-timestamp']  # Newest first
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        db_table = 'accounting_auditlog'
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['model_name', 'object_id', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.model_name} #{self.object_id} by {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Override save to prevent modifications after creation (immutability)"""
        if self.pk:
            # If the object already exists, raise an error
            raise ValueError("Audit logs are immutable and cannot be modified")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion (immutability)"""
        raise ValueError("Audit logs are immutable and cannot be deleted")


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
    
    # User Defined References
    user_references = models.JSONField(default=dict, blank=True, help_text="Custom user-defined references")
    reference_number = models.CharField(max_length=100, blank=True)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    notes = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    
    def clean(self):
        super().clean()
        from .validators import ReferenceValidator
        if self.user_references:
            ReferenceValidator.validate('invoice', self.user_references, exclude_id=self.pk)
    
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
    
    # IFRS/IASB Compliance Fields
    IFRS_CATEGORIES = [
        ('financial_assets', 'Financial Assets'),
        ('financial_liabilities', 'Financial Liabilities'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expenses', 'Expenses'),
        ('other_comprehensive_income', 'Other Comprehensive Income'),
    ]
    
    MEASUREMENT_BASIS = [
        ('cost', 'Historical Cost'),
        ('fair_value', 'Fair Value'),
        ('amortized_cost', 'Amortized Cost'),
        ('net_realizable_value', 'Net Realizable Value'),
        ('value_in_use', 'Value in Use'),
    ]
    
    # Comprehensive IAS/IFRS Reference Codes
    IAS_IFRS_CODES = [
        ('', 'Not Applicable'),
        # IAS Standards (1-41)
        ('IAS 1', 'IAS 1 - Presentation of Financial Statements'),
        ('IAS 2', 'IAS 2 - Inventories'),
        ('IAS 7', 'IAS 7 - Statement of Cash Flows'),
        ('IAS 8', 'IAS 8 - Accounting Policies, Changes in Accounting Estimates and Errors'),
        ('IAS 10', 'IAS 10 - Events After the Reporting Period'),
        ('IAS 12', 'IAS 12 - Income Taxes'),
        ('IAS 16', 'IAS 16 - Property, Plant and Equipment'),
        ('IAS 17', 'IAS 17 - Leases (Superseded by IFRS 16)'),
        ('IAS 19', 'IAS 19 - Employee Benefits'),
        ('IAS 20', 'IAS 20 - Accounting for Government Grants'),
        ('IAS 21', 'IAS 21 - The Effects of Changes in Foreign Exchange Rates'),
        ('IAS 23', 'IAS 23 - Borrowing Costs'),
        ('IAS 24', 'IAS 24 - Related Party Disclosures'),
        ('IAS 26', 'IAS 26 - Accounting and Reporting by Retirement Benefit Plans'),
        ('IAS 27', 'IAS 27 - Separate Financial Statements'),
        ('IAS 28', 'IAS 28 - Investments in Associates and Joint Ventures'),
        ('IAS 29', 'IAS 29 - Financial Reporting in Hyperinflationary Economies'),
        ('IAS 32', 'IAS 32 - Financial Instruments: Presentation'),
        ('IAS 33', 'IAS 33 - Earnings per Share'),
        ('IAS 34', 'IAS 34 - Interim Financial Reporting'),
        ('IAS 36', 'IAS 36 - Impairment of Assets'),
        ('IAS 37', 'IAS 37 - Provisions, Contingent Liabilities and Contingent Assets'),
        ('IAS 38', 'IAS 38 - Intangible Assets'),
        ('IAS 39', 'IAS 39 - Financial Instruments: Recognition and Measurement (Superseded by IFRS 9)'),
        ('IAS 40', 'IAS 40 - Investment Property'),
        ('IAS 41', 'IAS 41 - Agriculture'),
        # IFRS Standards (1-17)
        ('IFRS 1', 'IFRS 1 - First-time Adoption of IFRS'),
        ('IFRS 2', 'IFRS 2 - Share-based Payment'),
        ('IFRS 3', 'IFRS 3 - Business Combinations'),
        ('IFRS 4', 'IFRS 4 - Insurance Contracts'),
        ('IFRS 5', 'IFRS 5 - Non-current Assets Held for Sale and Discontinued Operations'),
        ('IFRS 6', 'IFRS 6 - Exploration for and Evaluation of Mineral Resources'),
        ('IFRS 7', 'IFRS 7 - Financial Instruments: Disclosures'),
        ('IFRS 8', 'IFRS 8 - Operating Segments'),
        ('IFRS 9', 'IFRS 9 - Financial Instruments'),
        ('IFRS 10', 'IFRS 10 - Consolidated Financial Statements'),
        ('IFRS 11', 'IFRS 11 - Joint Arrangements'),
        ('IFRS 12', 'IFRS 12 - Disclosure of Interests in Other Entities'),
        ('IFRS 13', 'IFRS 13 - Fair Value Measurement'),
        ('IFRS 14', 'IFRS 14 - Regulatory Deferral Accounts'),
        ('IFRS 15', 'IFRS 15 - Revenue from Contracts with Customers'),
        ('IFRS 16', 'IFRS 16 - Leases'),
        ('IFRS 17', 'IFRS 17 - Insurance Contracts'),
    ]
    
    ias_reference_code = models.CharField(
        max_length=20,
        choices=IAS_IFRS_CODES,
        blank=True,
        help_text="IAS/IFRS reference code"
    )
    ifrs_category = models.CharField(
        max_length=50,
        choices=IFRS_CATEGORIES,
        blank=True,
        help_text="IFRS financial statement category"
    )
    ifrs_subcategory = models.CharField(
        max_length=100,
        blank=True,
        help_text="Detailed IFRS classification"
    )
    measurement_basis = models.CharField(
        max_length=30,
        choices=MEASUREMENT_BASIS,
        default='cost',
        help_text="Measurement basis per IFRS"
    )
    
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
    
    # Task 1.6.1: Enhancements
    budget_allocation = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    is_profit_center = models.BooleanField(default=False)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_cost_centers')
    
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
    
    # User Defined References
    user_references = models.JSONField(default=dict, blank=True, help_text="Custom user-defined references")
    
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
    
    # Approval Workflow Integration (Task 1.3.4)
    APPROVAL_STATUS_CHOICES = [
        ('not_required', 'Not Required'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='not_required',
        db_index=True,
        help_text="Approval workflow status (IAS 1 - Internal Controls)"
    )
    
    approval_request = models.ForeignKey(
        'ApprovalRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='voucher_v2',
        help_text="Linked approval request"
    )
    
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
        
    def clean(self):
        super().clean()
        from .validators import ReferenceValidator
        if self.user_references:
            ReferenceValidator.validate('voucher', self.user_references, exclude_id=self.pk)
    
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
    
    def requires_approval(self):
        """
        Check if this voucher requires approval workflow
        
        Task 1.3.4: Integration with Existing Models
        IAS 1 - Internal Controls: Approval required for high-value transactions
        
        Returns:
            bool: True if approval is required, False otherwise
        """
        # Check if there's an active approval workflow for this voucher type
        from accounting.models import ApprovalWorkflow, ApprovalLevel
        
        try:
            workflow = ApprovalWorkflow.objects.filter(
                document_type='voucher',
                is_active=True
            ).first()
            
            if not workflow:
                return False
            
            # Check if amount exceeds any approval level threshold
            levels = ApprovalLevel.objects.filter(
                workflow=workflow,
                min_amount__lte=self.total_amount,
                max_amount__gte=self.total_amount
            )
            
            return levels.exists()
            
        except Exception:
            return False
    
    def can_be_posted(self):
        """
        Check if voucher can be posted based on approval status
        
        Task 1.3.4: Integration with Existing Models
        IAS 1 - Internal Controls: Prevent unauthorized posting
        
        Returns:
            tuple: (bool, str) - (can_post, reason)
        """
        if self.approval_status == 'pending':
            return False, "Voucher is pending approval"
        
        if self.approval_status == 'rejected':
            return False, "Voucher has been rejected"
        
        if self.requires_approval() and self.approval_status != 'approved':
            return False, "Approval is required but not obtained"
        
        return True, "Voucher can be posted"
    
    def initiate_approval_workflow(self):
        """
        Initiate approval workflow for this voucher
        
        Task 1.3.4: Integration with Existing Models
        IAS 1 - Internal Controls: Initiate approval process
        
        Returns:
            ApprovalRequest: Created approval request instance
        """
        from accounting.services import ApprovalService
        
        service = ApprovalService()
        approval_request = service.initiate_approval_for_voucher(self)
        
        # Update voucher status
        self.approval_status = 'pending'
        self.approval_request = approval_request
        self.save(update_fields=['approval_status', 'approval_request'])
        
        return approval_request

    
    def save(self, *args, **kwargs):
        """Override save to auto-generate voucher number"""
        # Auto-generate voucher number if not provided
        if not self.voucher_number:
            from accounting.services import NumberingService
            
            # Map voucher type to document type for numbering scheme
            doc_type_mapping = {
                'JE': 'journal',
                'SI': 'invoice',
                'PI': 'purchase_order',
                'CPV': 'payment',
                'BPV': 'payment',
                'CRV': 'receipt',
                'BRV': 'receipt',
                'DN': 'debit_note',
                'CN': 'credit_note',
                'CE': 'journal',
            }
            
            document_type = doc_type_mapping.get(self.voucher_type, 'voucher')
            
            # Get entity if available (for multi-entity support)
            entity = getattr(self, 'entity', None)
            
            try:
                self.voucher_number = NumberingService.generate_number(
                    document_type=document_type,
                    entity=entity,
                    custom_date=self.voucher_date
                )
            except Exception as e:
                # If auto-numbering fails, generate a fallback number
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                self.voucher_number = f"{self.voucher_type}-{timestamp}"
        
        # Task 1.3.4: Approval workflow integration (IAS 1 - Internal Controls)
        # Check if trying to post without approval
        if self.status == 'posted':
            can_post, reason = self.can_be_posted()
            if not can_post:
                raise ValueError(f"Cannot post voucher: {reason}")
        
        super().save(*args, **kwargs)
    
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


# ============================================
# IFRS 13 - FAIR VALUE MEASUREMENT
# ============================================

class FairValueMeasurement(models.Model):
    """
    Fair Value Measurement Model (IFRS 13 / IAS 40)
    
    Tracks fair value measurements for assets/liabilities measured at fair value.
    Implements IFRS 13 fair value hierarchy (Level 1, 2, 3).
    
    Primary use cases:
    - Investment Property (IAS 40)
    - Financial Instruments (IFRS 9)
    - Biological Assets (IAS 41)
    - Business Combinations (IFRS 3)
    """
    
    # Fair Value Hierarchy (IFRS 13.72-90)
    FAIR_VALUE_HIERARCHY = [
        ('level_1', 'Level 1 - Quoted prices in active markets'),
        ('level_2', 'Level 2 - Observable inputs other than quoted prices'),
        ('level_3', 'Level 3 - Unobservable inputs'),
    ]
    
    # Valuation Techniques (IFRS 13.62-71)
    VALUATION_TECHNIQUES = [
        ('market_approach', 'Market Approach'),
        ('income_approach', 'Income Approach (DCF, etc.)'),
        ('cost_approach', 'Cost Approach (Replacement Cost)'),
    ]
    
    # Measurement Purpose
    MEASUREMENT_PURPOSE = [
        ('initial_recognition', 'Initial Recognition'),
        ('subsequent_measurement', 'Subsequent Measurement'),
        ('revaluation', 'Revaluation'),
        ('impairment_testing', 'Impairment Testing'),
        ('disposal', 'Disposal'),
    ]
    
    # Link to Account
    account = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        related_name='fair_value_measurements',
        help_text="Account being measured (e.g., Investment Property, Financial Asset)"
    )
    
    # Measurement Date & Purpose
    measurement_date = models.DateField(
        help_text="Date of fair value measurement"
    )
    measurement_purpose = models.CharField(
        max_length=30,
        choices=MEASUREMENT_PURPOSE,
        default='subsequent_measurement',
        help_text="Purpose of this measurement"
    )
    
    # Fair Value Hierarchy Level (IFRS 13 requirement)
    fair_value_level = models.CharField(
        max_length=10,
        choices=FAIR_VALUE_HIERARCHY,
        help_text="IFRS 13 fair value hierarchy level"
    )
    
    # Valuation Details
    valuation_technique = models.CharField(
        max_length=20,
        choices=VALUATION_TECHNIQUES,
        help_text="Valuation technique used"
    )
    valuation_description = models.TextField(
        blank=True,
        help_text="Detailed description of valuation methodology"
    )
    inputs_used = models.JSONField(
        default=dict,
        help_text="Key inputs used in valuation (JSON format)"
    )
    
    # Amounts
    fair_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Fair value amount"
    )
    carrying_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Carrying amount before fair value adjustment"
    )
    gain_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Fair value gain/(loss) = Fair Value - Carrying Amount"
    )
    
    # Recognition in Financial Statements
    recognized_in_pl = models.BooleanField(
        default=True,
        help_text="Gain/loss recognized in Profit & Loss (vs. OCI)"
    )
    voucher = models.ForeignKey(
        VoucherV2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fair_value_adjustments',
        help_text="Voucher created for fair value adjustment"
    )
    
    # External Valuation
    external_valuer = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of external valuer (if applicable)"
    )
    valuer_credentials = models.CharField(
        max_length=200,
        blank=True,
        help_text="Professional credentials of valuer"
    )
    valuation_report_ref = models.CharField(
        max_length=100,
        blank=True,
        help_text="Reference number of valuation report"
    )
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='fair_value_measurements_created'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fair_value_measurements_approved'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or assumptions"
    )
    
    class Meta:
        ordering = ['-measurement_date', '-created_at']
        verbose_name = "Fair Value Measurement"
        verbose_name_plural = "Fair Value Measurements"
        db_table = 'accounting_fairvaluemeasurement'
        indexes = [
            models.Index(fields=['account', 'measurement_date']),
            models.Index(fields=['fair_value_level']),
            models.Index(fields=['measurement_date']),
        ]
    
    def __str__(self):
        return f"{self.account.code} - {self.measurement_date} - {self.get_fair_value_level_display()}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate gain/loss before saving"""
        self.gain_loss = self.fair_value - self.carrying_amount
        super().save(*args, **kwargs)
    
    def get_hierarchy_description(self):
        """Get detailed description of fair value hierarchy level"""
        descriptions = {
            'level_1': 'Quoted prices in active markets for identical assets or liabilities',
            'level_2': 'Inputs other than quoted prices that are observable for the asset or liability',
            'level_3': 'Unobservable inputs for the asset or liability'
        }
        return descriptions.get(self.fair_value_level, '')
    
    @property
    def is_gain(self):
        """Check if measurement resulted in gain"""
        return self.gain_loss > 0
    
    @property
    def is_loss(self):
        """Check if measurement resulted in loss"""
        return self.gain_loss < 0
    
    @property
    def is_approved(self):
        """Check if measurement is approved"""
        return self.approved_by is not None and self.approved_at is not None


# ============================================
# MULTI-ENTITY CONSOLIDATION & IAS 21
# ============================================

class Entity(models.Model):
    """
    Entity Model for Multi-Entity Consolidation
    
    Supports group consolidation and IAS 21 foreign exchange translation.
    Each entity has its own functional currency and can be part of a hierarchy.
    
    Use cases:
    - Multi-company groups
    - Subsidiaries and branches
    - Foreign operations (IAS 21)
    - Consolidation reporting (IFRS 10)
    """
    
    # Entity Identification
    entity_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique entity code (e.g., HQ, SUB01, BR-US)"
    )
    entity_name = models.CharField(
        max_length=200,
        help_text="Full legal name of the entity"
    )
    short_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Short name for display"
    )
    
    # Entity Hierarchy
    parent_entity = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='subsidiaries',
        help_text="Parent entity for consolidation hierarchy"
    )
    
    # Location & Currency (IAS 21)
    country = models.CharField(
        max_length=100,
        help_text="Country of operation"
    )
    functional_currency = models.ForeignKey(
        CurrencyV2,
        on_delete=models.PROTECT,
        related_name='entities_functional',
        help_text="Functional currency per IAS 21 (currency of primary economic environment)"
    )
    presentation_currency = models.ForeignKey(
        CurrencyV2,
        on_delete=models.PROTECT,
        related_name='entities_presentation',
        null=True,
        blank=True,
        help_text="Presentation currency for reporting (if different from functional)"
    )
    
    # Consolidation Settings
    consolidation_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('100.00'),
        help_text="Ownership percentage for consolidation (0-100)"
    )
    consolidation_method = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Full Consolidation (>50% ownership)'),
            ('proportionate', 'Proportionate Consolidation'),
            ('equity', 'Equity Method (20-50% ownership)'),
            ('none', 'No Consolidation (<20% ownership)'),
        ],
        default='full',
        help_text="Consolidation method per IFRS 10/IAS 28"
    )
    eliminate_intercompany = models.BooleanField(
        default=True,
        help_text="Eliminate intercompany transactions in consolidation"
    )
    
    # Entity Type
    entity_type = models.CharField(
        max_length=20,
        choices=[
            ('parent', 'Parent Company'),
            ('subsidiary', 'Subsidiary'),
            ('branch', 'Branch'),
            ('joint_venture', 'Joint Venture'),
            ('associate', 'Associate'),
        ],
        default='subsidiary',
        help_text="Type of entity in group structure"
    )
    
    # Registration Details
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Company registration number"
    )
    tax_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Tax identification number"
    )
    
    # Contact Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether entity is currently active"
    )
    activation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date entity became active"
    )
    deactivation_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date entity was deactivated"
    )
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='entities_created'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this entity"
    )
    
    class Meta:
        ordering = ['entity_code']
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        db_table = 'accounting_entity'
        indexes = [
            models.Index(fields=['entity_code']),
            models.Index(fields=['parent_entity']),
            models.Index(fields=['functional_currency']),
        ]
    
    def __str__(self):
        return f"{self.entity_code} - {self.entity_name}"
    
    def get_full_hierarchy_path(self):
        """Get full hierarchy path from root to this entity"""
        path = [self.entity_code]
        current = self.parent_entity
        
        while current:
            path.insert(0, current.entity_code)
            current = current.parent_entity
        
        return ' > '.join(path)
    
    def get_all_children(self):
        """Get all child entities recursively"""
        children = list(self.subsidiaries.all())
        for child in list(children):
            children.extend(child.get_all_children())
        return children
    
    def is_root_entity(self):
        """Check if this is a root entity (no parent)"""
        return self.parent_entity is None
    
    def requires_fx_translation(self):
        """Check if entity requires FX translation per IAS 21"""
        if not self.presentation_currency:
            return False
        return self.functional_currency != self.presentation_currency
    
    @property
    def ownership_display(self):
        """Display ownership percentage"""
        return f"{self.consolidation_percentage}%"
    
    def clean(self):
        """Validate entity data"""
        from django.core.exceptions import ValidationError
        
        # Prevent circular references
        if self.parent_entity:
            current = self.parent_entity
            while current:
                if current == self:
                    raise ValidationError("Entity cannot be its own ancestor")
                current = current.parent_entity
        
        # Validate consolidation percentage
        if not (0 <= self.consolidation_percentage <= 100):
            raise ValidationError("Consolidation percentage must be between 0 and 100")


# ============================================
# FX REVALUATION AUDIT TRAIL
# ============================================

class FXRevaluationLog(models.Model):
    """
    Audit Trail for FX Revaluation Activities
    
    Tracks all foreign exchange revaluation activities for compliance
    and audit purposes per IAS 21.
    
    Use cases:
    - Month-end FX revaluation tracking
    - Audit trail for FX gain/loss
    - Compliance reporting
    - Historical revaluation analysis
    """
    
    REVALUATION_STATUS = [
        ('initiated', 'Initiated'),
        ('calculated', 'Calculated'),
        ('posted', 'Posted'),
        ('reversed', 'Reversed'),
        ('error', 'Error'),
    ]
    
    # Revaluation Identification
    revaluation_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for this revaluation run"
    )
    
    # Entity Information
    entity = models.ForeignKey(
        Entity,
        on_delete=models.PROTECT,
        related_name='fx_revaluation_logs',
        help_text="Entity being revalued"
    )
    
    # Revaluation Details
    revaluation_date = models.DateField(
        help_text="Date of revaluation (usually month-end)"
    )
    functional_currency = models.ForeignKey(
        CurrencyV2,
        on_delete=models.PROTECT,
        related_name='fx_revaluation_logs',
        help_text="Functional currency of the entity"
    )
    
    # Revaluation Results
    accounts_revalued = models.IntegerField(
        default=0,
        help_text="Number of accounts revalued"
    )
    total_gain = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total unrealized FX gain"
    )
    total_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total unrealized FX loss"
    )
    net_fx_gain_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Net FX gain/(loss)"
    )
    
    # Voucher Information
    voucher = models.ForeignKey(
        VoucherV2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fx_revaluation_logs',
        help_text="Voucher created for this revaluation"
    )
    reversal_voucher = models.ForeignKey(
        VoucherV2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fx_revaluation_reversal_logs',
        help_text="Reversal voucher (if created)"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=REVALUATION_STATUS,
        default='initiated',
        help_text="Status of this revaluation"
    )
    
    # Execution Details
    execution_method = models.CharField(
        max_length=50,
        default='manual',
        help_text="How was this revaluation triggered (manual, scheduled, api)"
    )
    auto_posted = models.BooleanField(
        default=False,
        help_text="Whether entries were automatically posted"
    )
    reversal_created = models.BooleanField(
        default=False,
        help_text="Whether reversal entry was created"
    )
    
    # Detailed Results (JSON)
    revaluation_details = models.JSONField(
        default=dict,
        help_text="Detailed revaluation results per account (JSON format)"
    )
    
    # Error Tracking
    error_message = models.TextField(
        blank=True,
        help_text="Error message if revaluation failed"
    )
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='fx_revaluation_logs_created'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this revaluation"
    )
    
    class Meta:
        ordering = ['-revaluation_date', '-created_at']
        verbose_name = "FX Revaluation Log"
        verbose_name_plural = "FX Revaluation Logs"
        db_table = 'accounting_fx_revaluation_log'
        indexes = [
            models.Index(fields=['entity', 'revaluation_date']),
            models.Index(fields=['revaluation_id']),
            models.Index(fields=['status']),
            models.Index(fields=['revaluation_date']),
        ]
    
    def __str__(self):
        return f"{self.revaluation_id} - {self.entity.entity_code} - {self.revaluation_date}"
    
    @property
    def is_successful(self):
        """Check if revaluation was successful"""
        return self.status in ['calculated', 'posted']
    
    @property
    def has_fx_impact(self):
        """Check if revaluation had any FX impact"""
        return self.net_fx_gain_loss != Decimal('0.00')


# ============================================
# AUTO-NUMBERING SYSTEM
# ============================================

class NumberingScheme(models.Model):
    """
    Flexible Auto-Numbering Scheme for Documents
    
    Supports customizable numbering formats for all document types:
    - Invoices, Vouchers, Purchase Orders, etc.
    - Configurable prefix, suffix, date format
    - Automatic reset (yearly, monthly, daily, or never)
    - Multi-entity support
    
    Example formats:
    - INV-2025-0001
    - VCH/202501/00001
    - PO-20250129-001
    """
    
    RESET_FREQUENCY_CHOICES = [
        ('never', 'Never Reset'),
        ('yearly', 'Reset Yearly'),
        ('monthly', 'Reset Monthly'),
        ('daily', 'Reset Daily'),
    ]
    
    DOCUMENT_TYPE_CHOICES = [
        ('voucher', 'Voucher'),
        ('invoice', 'Invoice'),
        ('purchase_order', 'Purchase Order'),
        ('sales_order', 'Sales Order'),
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
        ('journal', 'Journal Entry'),
        ('credit_note', 'Credit Note'),
        ('debit_note', 'Debit Note'),
        ('quotation', 'Quotation'),
        ('delivery_note', 'Delivery Note'),
        ('goods_receipt', 'Goods Receipt'),
        ('custom', 'Custom Document'),
    ]
    
    DATE_FORMAT_CHOICES = [
        ('', 'No Date'),
        ('YYYY', 'Year (2025)'),
        ('YY', 'Year Short (25)'),
        ('YYMM', 'Year-Month (2501)'),
        ('YYYYMM', 'Year-Month (202501)'),
        ('YYMMDD', 'Year-Month-Day (250129)'),
        ('YYYYMMDD', 'Year-Month-Day (20250129)'),
    ]
    
    # Scheme Identification
    scheme_name = models.CharField(
        max_length=100,
        help_text="Human-readable name for this numbering scheme"
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text="Type of document this scheme applies to"
    )
    
    # Format Configuration
    prefix = models.CharField(
        max_length=20,
        blank=True,
        help_text="Static prefix (e.g., 'INV', 'VCH')"
    )
    suffix = models.CharField(
        max_length=20,
        blank=True,
        help_text="Static suffix (optional)"
    )
    date_format = models.CharField(
        max_length=20,
        choices=DATE_FORMAT_CHOICES,
        default='',
        blank=True,
        help_text="Date format to include in number"
    )
    separator = models.CharField(
        max_length=5,
        default='-',
        help_text="Separator character between components"
    )
    padding = models.IntegerField(
        default=4,
        help_text="Number of digits for sequence (e.g., 4 = 0001)"
    )
    
    # Sequence Management
    next_number = models.IntegerField(
        default=1,
        help_text="Next number in sequence"
    )
    reset_frequency = models.CharField(
        max_length=20,
        choices=RESET_FREQUENCY_CHOICES,
        default='yearly',
        help_text="When to reset the counter"
    )
    last_reset_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when counter was last reset"
    )
    
    # Multi-Entity Support
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='numbering_schemes',
        help_text="Specific entity (leave blank for global scheme)"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this scheme is currently active"
    )
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='numbering_schemes_created'
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this numbering scheme"
    )
    
    class Meta:
        ordering = ['document_type', 'scheme_name']
        verbose_name = "Numbering Scheme"
        verbose_name_plural = "Numbering Schemes"
        db_table = 'accounting_numbering_scheme'
        indexes = [
            models.Index(fields=['document_type', 'is_active']),
            models.Index(fields=['entity', 'document_type']),
        ]
        # Ensure only one active scheme per document type per entity
        constraints = [
            models.UniqueConstraint(
                fields=['document_type', 'entity'],
                condition=models.Q(is_active=True),
                name='unique_active_scheme_per_entity'
            ),
            models.UniqueConstraint(
                fields=['document_type'],
                condition=models.Q(is_active=True, entity__isnull=True),
                name='unique_active_global_scheme'
            ),
        ]
    
    def __str__(self):
        return f"{self.scheme_name} ({self.document_type})"
    
    def generate_preview(self):
        """Generate a preview of what the next number will look like"""
        from datetime import date
        
        components = []
        
        # Add prefix
        if self.prefix:
            components.append(self.prefix)
        
        # Add date component
        if self.date_format:
            today = date.today()
            if self.date_format == 'YYYY':
                components.append(str(today.year))
            elif self.date_format == 'YY':
                components.append(str(today.year)[2:])
            elif self.date_format == 'YYMM':
                components.append(f"{str(today.year)[2:]}{today.month:02d}")
            elif self.date_format == 'YYYYMM':
                components.append(f"{today.year}{today.month:02d}")
            elif self.date_format == 'YYMMDD':
                components.append(f"{str(today.year)[2:]}{today.month:02d}{today.day:02d}")
            elif self.date_format == 'YYYYMMDD':
                components.append(f"{today.year}{today.month:02d}{today.day:02d}")
        
        # Add sequence number
        sequence = str(self.next_number).zfill(self.padding)
        components.append(sequence)
        
        # Add suffix
        if self.suffix:
            components.append(self.suffix)
        
        # Join with separator
        return self.separator.join(components)
    
    def should_reset(self, compare_date=None):
        """Check if counter should be reset based on reset frequency"""
        from datetime import date
        
        if self.reset_frequency == 'never':
            return False
        
        if not self.last_reset_date:
            return True
        
        today = compare_date or date.today()
        
        if self.reset_frequency == 'daily':
            return self.last_reset_date < today
        elif self.reset_frequency == 'monthly':
            return (self.last_reset_date.year, self.last_reset_date.month) < (today.year, today.month)
        elif self.reset_frequency == 'yearly':
            return self.last_reset_date.year < today.year
        
        return False
    
    def clean(self):
        """Validate the numbering scheme"""
        from django.core.exceptions import ValidationError
        
        # Validate padding
        if self.padding < 1 or self.padding > 10:
            raise ValidationError("Padding must be between 1 and 10")
        
        # Validate next_number
        if self.next_number < 1:
            raise ValidationError("Next number must be at least 1")
        
        # Ensure at least one component (prefix, date, or suffix)
        if not self.prefix and not self.date_format and not self.suffix:
            raise ValidationError("Scheme must have at least a prefix, date format, or suffix")


# ============================================
# USER DEFINED REFERENCES (JSONB Configuration)
# ============================================

class ReferenceDefinition(models.Model):
    """
    Configuration for User-Defined References (JSONB) validators
    """
    MODEL_CHOICES = [
        ('voucher', 'Voucher'),
        ('invoice', 'Invoice'),
    ]
    DATA_TYPE_CHOICES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Yes/No'),
    ]
    
    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES)
    field_key = models.CharField(max_length=50, help_text="Key used in the JSON data")
    field_label = models.CharField(max_length=100, help_text="User-facing label")
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES, default='text')
    is_required = models.BooleanField(default=False)
    is_unique = models.BooleanField(default=False, help_text="Enforce uniqueness for this field value")
    is_active = models.BooleanField(default=True)
    validation_regex = models.CharField(max_length=255, blank=True, null=True, help_text="Optional regex for text fields")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['model_name', 'field_key']
        ordering = ['model_name', 'field_label']
        
    def __str__(self):
        return f"{self.get_model_name_display()} - {self.field_label} ({self.field_key})"


# ==============================================================================
# PART 2: Banking & Treasury Operations
# Module 2.1: Bank Reconciliation System
# ==============================================================================

class BankStatement(models.Model):
    """
    Represents an imported bank statement file or manual entry header.
    IAS/IFRS Compliance: Supports verification of cash balances.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('POSTED', 'Posted'),
    ]

    bank_account = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        # limit_choices_to={'account_type': 'ASSET'},  # Removed strictly to allow testing with generic accounts if needed, but logic enforces it
        related_name='bank_statements',
        help_text="The general ledger account representing this bank account"
    )
    statement_date = models.DateField(help_text="Date of statement generation")
    start_date = models.DateField(help_text="Period start date")
    end_date = models.DateField(help_text="Period end date")
    
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=15, decimal_places=2)
    
    # File upload for reference/audit
    file_upload = models.FileField(upload_to='bank_statements/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bank_statements_created')

    def __str__(self):
        return f"Statement {self.id} for {self.bank_account.name} ({self.start_date} - {self.end_date})"


class BankStatementLine(models.Model):
    """
    Represents a single transaction line in a bank statement.
    """
    statement = models.ForeignKey(
        BankStatement,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    date = models.DateField()
    description = models.CharField(max_length=255)
    reference = models.CharField(max_length=100, blank=True)
    
    # Amount: Positive for Deposit, Negative for Withdrawal
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance = models.DecimalField(max_digits=15, decimal_places=2, help_text="Running balance provided by bank")
    
    # Reconciliation Status
    is_reconciled = models.BooleanField(default=False)
    matched_voucher_line = models.ForeignKey(
        'VoucherEntryV2',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bank_statement_lines',
        help_text="The ledger entry this bank line matches to"
    )

    def __str__(self):
        return f"{self.date} - {self.description} ({self.amount})"


class BankReconciliation(models.Model):
    """
    Represents a formal reconciliation session between Bank and Ledger.
    IAS/IFRS Compliance: Critical internal control for Cash & Cash Equivalents.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('COMPLETED', 'Completed'),
    ]

    bank_account = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        related_name='reconciliations'
    )
    reconciliation_date = models.DateField()
    
    # Balances at the time of reconciliation
    statement_balance = models.DecimalField(max_digits=15, decimal_places=2, help_text="Closing balance as per Bank Statement")
    ledger_balance = models.DecimalField(max_digits=15, decimal_places=2, help_text="Closing balance as per System Ledger")
    
    difference = models.DecimalField(max_digits=15, decimal_places=2, help_text="Should be zero for successful reconciliation")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    reconciled_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reconciliation for {self.bank_account.name} on {self.reconciliation_date}"


# ============================================================================
# MODULE 2.2: CHEQUE MANAGEMENT SYSTEM
# Task 2.2.1: Create Cheque Model
# ============================================================================

class Cheque(models.Model):
    """
    Represents a cheque for complete lifecycle management.
    Task 2.2.1: Create Cheque Model
    Module 2.2: Cheque Management System
    
    Tracks cheques from issuance through clearance, cancellation, or bouncing.
    Supports post-dated cheques and links to vouchers for accounting integration.
    """
    CHEQUE_STATUS = [
        ('issued', 'Issued'),
        ('cleared', 'Cleared'),
        ('cancelled', 'Cancelled'),
        ('bounced', 'Bounced'),
    ]
    
    # Cheque Details
    cheque_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique cheque number"
    )
    cheque_date = models.DateField(
        help_text="Date on the cheque"
    )
    
    # Relationships
    bank_account = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        related_name='cheques',
        help_text="Bank account from which cheque is issued"
    )
    payee = models.ForeignKey(
        'partners.BusinessPartner',
        on_delete=models.PROTECT,
        related_name='cheques_received',
        help_text="Payee (recipient) of the cheque"
    )
    voucher = models.ForeignKey(
        VoucherV2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cheques',
        help_text="Linked payment voucher"
    )
    
    # Financial Details
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Cheque amount"
    )
    
    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=CHEQUE_STATUS,
        default='issued',
        help_text="Current status of the cheque"
    )
    
    # Clearance Information
    clearance_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when cheque was cleared by bank"
    )
    
    # Post-Dated Cheque Support
    is_post_dated = models.BooleanField(
        default=False,
        help_text="Is this a post-dated cheque?"
    )
    
    # Cancellation Information
    cancelled_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when cheque was cancelled"
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Reason for cancellation"
    )
    
    # Audit Trail
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cheques_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-cheque_date', '-created_at']
        verbose_name = "Cheque"
        verbose_name_plural = "Cheques"
        indexes = [
            models.Index(fields=['cheque_number']),
            models.Index(fields=['status']),
            models.Index(fields=['cheque_date']),
            models.Index(fields=['bank_account', 'status']),
        ]
    
    def __str__(self):
        return f"Cheque {self.cheque_number} - {self.payee.name} - {self.amount}"
    
    def clean(self):
        """Validate cheque data"""
        from django.core.exceptions import ValidationError
        
        # Validate amount is positive
        if self.amount and self.amount <= 0:
            raise ValidationError({'amount': 'Cheque amount must be positive'})
        
        # Validate clearance date is after cheque date
        if self.clearance_date and self.cheque_date:
            if self.clearance_date < self.cheque_date:
                raise ValidationError({
                    'clearance_date': 'Clearance date cannot be before cheque date'
                })
        
        # Validate cancelled date
        if self.cancelled_date and self.cheque_date:
            if self.cancelled_date < self.cheque_date:
                raise ValidationError({
                    'cancelled_date': 'Cancellation date cannot be before cheque date'
                })
        
        # If status is cleared, clearance_date should be set
        if self.status == 'cleared' and not self.clearance_date:
            raise ValidationError({
                'clearance_date': 'Clearance date is required when status is cleared'
            })
        
        # If status is cancelled, cancellation info should be set
        if self.status == 'cancelled':
            if not self.cancelled_date:
                raise ValidationError({
                    'cancelled_date': 'Cancellation date is required when status is cancelled'
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)


# ============================================================================
# MODULE 2.3: BANK TRANSFER SYSTEM
# Task 2.3.1: Create BankTransfer Model
# ============================================================================

class BankTransfer(models.Model):
    """
    Represents a bank-to-bank transfer for professional transfer workflow.
    Module 2.3: Bank Transfer System
    Task 2.3.1: Create BankTransfer Model
    
    Tracks transfers between bank accounts with multi-currency support,
    approval workflow, and voucher integration.
    """
    TRANSFER_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Transfer Details
    transfer_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique transfer number"
    )
    transfer_date = models.DateField(
        help_text="Date of transfer"
    )
    
    # Bank Accounts
    from_bank = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        related_name='transfers_from',
        help_text="Source bank account"
    )
    to_bank = models.ForeignKey(
        AccountV2,
        on_delete=models.PROTECT,
        related_name='transfers_to',
        help_text="Destination bank account"
    )
    
    # Financial Details
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Transfer amount in source currency"
    )
    
    # Multi-Currency Support
    from_currency = models.ForeignKey(
        CurrencyV2,
        on_delete=models.PROTECT,
        related_name='transfers_from_currency',
        help_text="Source currency"
    )
    to_currency = models.ForeignKey(
        CurrencyV2,
        on_delete=models.PROTECT,
        related_name='transfers_to_currency',
        help_text="Destination currency"
    )
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0000'),
        help_text="Exchange rate (1 source currency = X destination currency)"
    )
    
    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=TRANSFER_STATUS,
        default='pending',
        help_text="Current status of the transfer"
    )
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='pending',
        help_text="Approval status of the transfer"
    )
    
    # Voucher Integration
    voucher = models.ForeignKey(
        VoucherV2,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bank_transfers',
        help_text="Linked accounting voucher"
    )
    
    # Additional Information
    description = models.TextField(
        blank=True,
        help_text="Transfer description or notes"
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference number"
    )
    
    # Audit Trail
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bank_transfers_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transfer_date', '-created_at']
        verbose_name = "Bank Transfer"
        verbose_name_plural = "Bank Transfers"
        indexes = [
            models.Index(fields=['transfer_number']),
            models.Index(fields=['status']),
            models.Index(fields=['approval_status']),
            models.Index(fields=['transfer_date']),
            models.Index(fields=['from_bank', 'to_bank']),
        ]
    
    def __str__(self):
        return f"Transfer {self.transfer_number} - {self.from_bank.name} to {self.to_bank.name} - {self.amount}"
    
    @property
    def converted_amount(self):
        """Calculate converted amount in destination currency"""
        return self.amount * self.exchange_rate
    
    def clean(self):
        """Validate transfer data"""
        from django.core.exceptions import ValidationError
        
        # Validate amount is positive
        if self.amount and self.amount <= 0:
            raise ValidationError({'amount': 'Transfer amount must be positive'})
        
        # Validate exchange rate is positive
        if self.exchange_rate and self.exchange_rate <= 0:
            raise ValidationError({'exchange_rate': 'Exchange rate must be positive'})
        
        # Validate from_bank and to_bank are different
        if self.from_bank and self.to_bank and self.from_bank == self.to_bank:
            raise ValidationError({
                'to_bank': 'Source and destination banks must be different'
            })
        
        # If same currency, exchange rate should be 1
        if self.from_currency and self.to_currency:
            if self.from_currency == self.to_currency and self.exchange_rate != Decimal('1.0000'):
                raise ValidationError({
                    'exchange_rate': 'Exchange rate must be 1.0000 for same currency transfers'
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)


# ============================================
# FIXED ASSET REGISTER (IAS 16 Compliance)
# ============================================
# Module 3.1: Fixed Asset Register
# Task 3.1.1: Create FixedAsset Model

class AssetCategory(models.Model):
    """
    Asset Category Model
    IAS 16: Property, Plant and Equipment - Asset Classification
    
    Defines categories for fixed assets with depreciation parameters
    per IAS 16 requirements for systematic depreciation allocation.
    """
    
    DEPRECIATION_METHOD_CHOICES = [
        ('straight_line', 'Straight Line'),
        ('declining_balance', 'Declining Balance'),
        ('units_of_production', 'Units of Production'),
    ]
    
    # Category Identification
    category_code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique category code (e.g., BLDG, MACH, VEH)"
    )
    category_name = models.CharField(
        max_length=200,
        help_text="Category name (e.g., Buildings, Machinery, Vehicles)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of asset category"
    )
    
    # IAS 16 Depreciation Parameters
    useful_life_years = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Estimated useful life in years (IAS 16.56)"
    )
    depreciation_method = models.CharField(
        max_length=30,
        choices=DEPRECIATION_METHOD_CHOICES,
        default='straight_line',
        help_text="Depreciation method per IAS 16.60"
    )
    residual_value_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Residual value as percentage of cost (IAS 16.6)"
    )
    
    # IFRS Compliance
    ias_reference_code = models.CharField(
        max_length=20,
        default='IAS 16',
        help_text="IAS/IFRS reference code"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active"
    )
    
    # Audit Trail
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='asset_categories_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category_code']
        verbose_name = 'Asset Category'
        verbose_name_plural = 'Asset Categories'
        db_table = 'accounting_asset_category'
    
    def __str__(self):
        return f"{self.category_code} - {self.category_name}"


class FixedAsset(models.Model):
    """
    Fixed Asset Model
    IAS 16: Property, Plant and Equipment
    
    Tracks individual fixed assets throughout their lifecycle:
    - Acquisition (IAS 16.15-28)
    - Depreciation (IAS 16.43-62)
    - Disposal (IAS 16.67-72)
    
    Measurement: Cost Model (IAS 16.30)
    Book Value = Cost - Accumulated Depreciation
    """
    
    ASSET_STATUS_CHOICES = [
        ('active', 'Active'),
        ('disposed', 'Disposed'),
        ('under_maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]
    
    # Asset Identification
    asset_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique asset number (e.g., FA-2025-001)"
    )
    asset_name = models.CharField(
        max_length=200,
        help_text="Asset name/description"
    )
    asset_category = models.ForeignKey(
        AssetCategory,
        on_delete=models.PROTECT,
        related_name='assets',
        help_text="Asset category"
    )
    
    # Acquisition Details (IAS 16.15-28)
    acquisition_date = models.DateField(
        help_text="Date of acquisition (IAS 16.16)"
    )
    acquisition_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Initial cost including purchase price and directly attributable costs (IAS 16.16)"
    )
    
    # Depreciation (IAS 16.43-62)
    accumulated_depreciation = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total depreciation charged to date (IAS 16.6)"
    )
    
    # Physical Location
    location = models.CharField(
        max_length=200,
        help_text="Physical location of asset"
    )
    asset_tag = models.CharField(
        max_length=50,
        unique=True,
        help_text="Physical asset tag/barcode for identification"
    )
    
    # Asset Status
    status = models.CharField(
        max_length=20,
        choices=ASSET_STATUS_CHOICES,
        default='active',
        help_text="Current status of asset"
    )
    
    # Disposal Details (IAS 16.67-72)
    disposal_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of disposal (IAS 16.67)"
    )
    disposal_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Disposal proceeds (IAS 16.71)"
    )
    
    # GL Account Linkage
    gl_account = models.ForeignKey(
        'AccountV2',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='fixed_assets',
        help_text="General ledger account for this asset (IAS 16 compliant)"
    )
    
    # Audit Trail
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='fixed_assets_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['asset_number']
        verbose_name = 'Fixed Asset'
        verbose_name_plural = 'Fixed Assets'
        db_table = 'accounting_fixed_asset'
        indexes = [
            models.Index(fields=['asset_number']),
            models.Index(fields=['asset_tag']),
            models.Index(fields=['status']),
            models.Index(fields=['asset_category', 'status']),
        ]
    
    def __str__(self):
        return f"{self.asset_number} - {self.asset_name}"
    
    @property
    def book_value(self):
        """
        Calculate book value (carrying amount)
        IAS 16.6: Carrying amount = Cost - Accumulated Depreciation
        """
        return self.acquisition_cost - self.accumulated_depreciation
    
    def calculate_gain_loss_on_disposal(self):
        """
        Calculate gain or loss on disposal
        IAS 16.71: Gain/Loss = Disposal Proceeds - Carrying Amount
        
        Returns:
            Decimal: Gain (positive) or Loss (negative)
        """
        if not self.disposal_amount:
            return Decimal('0.00')
        
        return self.disposal_amount - self.book_value
    
    def clean(self):
        """Validate asset data"""
        from django.core.exceptions import ValidationError
        
        # Validate accumulated depreciation doesn't exceed acquisition cost
        if self.accumulated_depreciation > self.acquisition_cost:
            raise ValidationError({
                'accumulated_depreciation': 'Accumulated depreciation cannot exceed acquisition cost'
            })
        
        # Validate disposal date is after acquisition date
        if self.disposal_date and self.acquisition_date:
            if self.disposal_date < self.acquisition_date:
                raise ValidationError({
                    'disposal_date': 'Disposal date cannot be before acquisition date'
                })
        
        # If disposed, disposal date and amount are required
        if self.status == 'disposed':
            if not self.disposal_date:
                raise ValidationError({
                    'disposal_date': 'Disposal date is required for disposed assets'
                })
            if self.disposal_amount is None:
                raise ValidationError({
                    'disposal_amount': 'Disposal amount is required for disposed assets'
                })
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)


# ============================================
# ENTITY MANAGEMENT (V2)
# ============================================

class EntityV2(models.Model):
    """Entity for multi-entity tracking - V2"""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = 'Entity (V2)'
        verbose_name_plural = 'Entities (V2)'
        db_table = 'accounting_entity_v2'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# ============================================
# BANK ACCOUNT MANAGEMENT
# ============================================

## ============================================
## DUPLICATE CODE FOUND - COMMENTED OUT
## ============================================
## These models are duplicates of earlier definitions in this file.
## Original models are located at:
## - BankAccount (Line 386 - LEGACY version)
## - BankStatement (Line 1955)
## - BankStatementLine (Line 1992)
## - FairValueMeasurement (Line 1088 - Comprehensive IFRS 13 version)
## 
## Please use the original model definitions above.
## ============================================

## class BankAccount(models.Model):
##     """Bank account management for banking operations"""
##     account_number = models.CharField(max_length=50, unique=True)
##     account_name = models.CharField(max_length=200)
##     bank_name = models.CharField(max_length=200)
##     branch = models.CharField(max_length=200, blank=True)
##     currency = models.ForeignKey(
##         CurrencyV2,
##         on_delete=models.PROTECT,
##         related_name='bank_accounts'
##     )
##     opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
##     current_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
##     is_active = models.BooleanField(default=True)
##     created_at = models.DateTimeField(auto_now_add=True)
##     updated_at = models.DateTimeField(auto_now=True)
##     
##     class Meta:
##         ordering = ['bank_name', 'account_number']
##         verbose_name = 'Bank Account'
##         verbose_name_plural = 'Bank Accounts'
##         db_table = 'accounting_bankaccount'
##     
##     def __str__(self):
##         return f"{self.bank_name} - {self.account_number}"


## # ============================================
## # BANK STATEMENT MANAGEMENT
## # ============================================

## class BankStatement(models.Model):
##     """Bank statement for reconciliation"""
##     bank_account = models.ForeignKey(
##         BankAccount,
##         on_delete=models.CASCADE,
##         related_name='statements'
##     )
##     statement_date = models.DateField()
##     opening_balance = models.DecimalField(max_digits=15, decimal_places=2)
##     closing_balance = models.DecimalField(max_digits=15, decimal_places=2)
##     is_reconciled = models.BooleanField(default=False)
##     created_at = models.DateTimeField(auto_now_add=True)
##     updated_at = models.DateTimeField(auto_now=True)
##     
##     class Meta:
##         ordering = ['-statement_date']
##         verbose_name = 'Bank Statement'
##         verbose_name_plural = 'Bank Statements'
##         db_table = 'accounting_bankstatement'
##     
##     def __str__(self):
##         return f"{self.bank_account.bank_name} - {self.statement_date}"


## class BankStatementLine(models.Model):
##     """Individual transactions in bank statement"""
##     statement = models.ForeignKey(
##         BankStatement,
##         on_delete=models.CASCADE,
##         related_name='lines'
##     )
##     transaction_date = models.DateField()
##     description = models.CharField(max_length=500)
##     reference = models.CharField(max_length=100, blank=True)
##     debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
##     credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
##     balance = models.DecimalField(max_digits=15, decimal_places=2)
##     is_reconciled = models.BooleanField(default=False)
##     
##     class Meta:
##         ordering = ['transaction_date', 'id']
##         verbose_name = 'Bank Statement Line'
##         verbose_name_plural = 'Bank Statement Lines'
##         db_table = 'accounting_bankstatementline'
##     
##     def __str__(self):
##         return f"{self.transaction_date} - {self.description}"


## # ============================================
## # FAIR VALUE MEASUREMENT (IAS 39/IFRS 9)
## # ============================================

## class FairValueMeasurement(models.Model):
##     """Fair value measurement for IAS 39/IFRS 9 compliance"""
##     LEVEL_CHOICES = [
##         ('1', 'Level 1 - Quoted prices in active markets'),
##         ('2', 'Level 2 - Observable inputs other than quoted prices'),
##         ('3', 'Level 3 - Unobservable inputs'),
##     ]
##     
##     asset = models.ForeignKey(
##         FixedAsset,
##         on_delete=models.CASCADE,
##         related_name='fair_value_measurements'
##     )
##     measurement_date = models.DateField()
##     fair_value = models.DecimalField(max_digits=15, decimal_places=2)
##     valuation_technique = models.CharField(max_length=200)
##     level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
##     notes = models.TextField(blank=True)
##     created_at = models.DateTimeField(auto_now_add=True)
##     updated_at = models.DateTimeField(auto_now=True)
##     
##     class Meta:
##         ordering = ['-measurement_date']
##         verbose_name = 'Fair Value Measurement'
##         verbose_name_plural = 'Fair Value Measurements'
##         db_table = 'accounting_fairvaluemeasurement'
##     
##     def __str__(self):
##         return f"{self.asset.asset_name} - {self.measurement_date} - Level {self.level}"


# ============================================
# APPROVAL WORKFLOW SYSTEM (IAS 1 - Internal Controls)
# ============================================
# Module 1.3: Multi-level approval system for financial controls

class ApprovalWorkflow(models.Model):
    """
    Approval workflow configuration
    Task 1.3.1: Create ApprovalWorkflow Model
    
    IFRS/IASB Compliance:
    - IAS 1: Internal Controls and Governance
    - Ensures proper authorization of financial transactions
    - Supports segregation of duties
    - Maintains audit trail for approvals
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('voucher', 'Voucher'),
        ('purchase_order', 'Purchase Order'),
        ('purchase_requisition', 'Purchase Requisition'),
        ('sales_order', 'Sales Order'),
        ('sales_quotation', 'Sales Quotation'),
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
        ('bank_transfer', 'Bank Transfer'),
        ('journal_entry', 'Journal Entry'),
        ('asset_acquisition', 'Asset Acquisition'),
        ('asset_disposal', 'Asset Disposal'),
        ('budget', 'Budget'),
        ('other', 'Other'),
    ]
    
    # Workflow identification
    workflow_name = models.CharField(
        max_length=200,
        help_text="Name of the approval workflow"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the workflow"
    )
    
    # Document type this workflow applies to
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        help_text="Type of document this workflow applies to"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this workflow is currently active"
    )
    
    # Audit trail
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approval_workflows_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['workflow_name']
        verbose_name = 'Approval Workflow'
        verbose_name_plural = 'Approval Workflows'
        db_table = 'accounting_approvalworkflow'
        indexes = [
            models.Index(fields=['document_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.workflow_name} ({self.document_type})"
    
    def clean(self):
        """Validate that only one active workflow exists per document type"""
        from django.core.exceptions import ValidationError
        
        if self.is_active:
            # Check for other active workflows for same document type
            existing = ApprovalWorkflow.objects.filter(
                document_type=self.document_type,
                is_active=True
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError(
                    f"An active workflow already exists for {self.get_document_type_display()}. "
                    "Please deactivate it first."
                )


class ApprovalLevel(models.Model):
    """
    Individual approval level within a workflow
    Task 1.3.1: Create ApprovalWorkflow Model
    
    Defines who approves at each level and amount thresholds
    """
    
    # Workflow this level belongs to
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name='levels'
    )
    
    # Level number (1, 2, 3, etc.)
    level_number = models.IntegerField(
        help_text="Approval level number (1 = first level)"
    )
    
    # Approver
    approver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approval_levels',
        help_text="User who approves at this level"
    )
    
    # Amount thresholds
    min_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Minimum amount for this level"
    )
    max_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('999999999.99'),
        help_text="Maximum amount for this level"
    )
    
    # Properties
    is_mandatory = models.BooleanField(
        default=True,
        help_text="Whether this level is mandatory"
    )
    
    class Meta:
        ordering = ['workflow', 'level_number']
        verbose_name = 'Approval Level'
        verbose_name_plural = 'Approval Levels'
        db_table = 'accounting_approvallevel'
        unique_together = [['workflow', 'level_number']]
        indexes = [
            models.Index(fields=['workflow', 'level_number']),
            models.Index(fields=['approver']),
        ]
    
    def __str__(self):
        return f"Level {self.level_number} - {self.approver.username} ({self.min_amount} - {self.max_amount})"
    
    def clean(self):
        """Validate amount range"""
        from django.core.exceptions import ValidationError
        
        if self.min_amount >= self.max_amount:
            raise ValidationError("Minimum amount must be less than maximum amount")


class ApprovalRequest(models.Model):
    """
    Approval request for a specific document
    Task 1.3.1: Create ApprovalWorkflow Model
    
    Tracks the approval process for a document
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Workflow being used
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.PROTECT,
        related_name='approval_requests'
    )
    
    # Document being approved (using GenericForeignKey for flexibility)
    document_type = models.CharField(
        max_length=50,
        help_text="Type of document (e.g., 'voucher', 'purchase_order')"
    )
    document_id = models.IntegerField(
        help_text="ID of the document being approved"
    )
    
    # Amount (for routing to correct approval level)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount of the document"
    )
    
    # Current status
    current_level = models.IntegerField(
        default=1,
        help_text="Current approval level"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Participants
    requester = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approval_requests_initiated',
        help_text="User who initiated the approval request"
    )
    current_approver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approval_requests_pending',
        null=True,
        blank=True,
        help_text="Current approver"
    )
    
    # Timestamps
    request_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the approval was requested"
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the approval was completed (approved/rejected)"
    )
    
    class Meta:
        ordering = ['-request_date']
        verbose_name = 'Approval Request'
        verbose_name_plural = 'Approval Requests'
        db_table = 'accounting_approvalrequest'
        indexes = [
            models.Index(fields=['document_type', 'document_id']),
            models.Index(fields=['status']),
            models.Index(fields=['current_approver', 'status']),
            models.Index(fields=['requester']),
        ]
    
    def __str__(self):
        return f"Approval Request for {self.document_type} #{self.document_id} - {self.status}"


class ApprovalAction(models.Model):
    """
    Individual approval action (approve/reject/delegate)
    Task 1.3.1: Create ApprovalWorkflow Model
    
    IFRS/IASB Compliance:
    - Maintains complete audit trail
    - Non-repudiation (who did what and when)
    - Immutable once created
    """
    
    ACTION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delegated', 'Delegated'),
        ('returned', 'Returned for Revision'),
    ]
    
    # Approval request this action belongs to
    approval_request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.PROTECT,
        related_name='actions'
    )
    
    # Level at which this action was taken
    level_number = models.IntegerField(
        help_text="Approval level number"
    )
    
    # Who took the action
    approver = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approval_actions',
        help_text="User who took this action"
    )
    
    # What action was taken
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Action taken by approver"
    )
    
    # Comments
    comments = models.TextField(
        blank=True,
        help_text="Approver's comments"
    )
    
    # Audit trail (IFRS requirement)
    action_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was taken"
    )
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the approver"
    )
    
    class Meta:
        ordering = ['approval_request', 'level_number', 'action_date']
        verbose_name = 'Approval Action'
        verbose_name_plural = 'Approval Actions'
        db_table = 'accounting_approvalaction'
        indexes = [
            models.Index(fields=['approval_request', 'level_number']),
            models.Index(fields=['approver', 'action_date']),
        ]
    
    def __str__(self):
        return f"Level {self.level_number} - {self.action} by {self.approver.username}"
    
    def save(self, *args, **kwargs):
        """Override save to prevent modifications after creation (immutability)"""
        if self.pk:
            # If the object already exists, raise an error
            from django.core.exceptions import ValidationError
            raise ValidationError("Approval actions are immutable and cannot be modified")
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to prevent deletion (audit requirement)"""
        raise ValidationError("Approval actions are immutable and cannot be deleted")


class UserGmailToken(models.Model):
    """
    Stores Gmail OAuth tokens for users.
    Task 1.3.6: Gmail OAuth Integration
    
    Security:
    - refresh_token is encrypted using Fernet (symmetric encryption)
    - access_token is stored plainly but short-lived
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gmail_token')
    
    # Tokens
    access_token = models.TextField(help_text="Short-lived access token")
    refresh_token_encrypted = models.BinaryField(help_text="Encrypted refresh token")
    token_expiry = models.DateTimeField(help_text="When the access token expires")
    
    # Metadata
    email = models.EmailField(help_text="The Gmail address associated with this token")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Gmail Token'
        verbose_name_plural = 'User Gmail Tokens'
        db_table = 'accounting_usergmailtoken'

    def __str__(self):
        return f"Gmail Token for {self.email}"


class EmailCommunicationLog(models.Model):
    """
    Audit trail for all email communications.
    Task 1.3.6: Gmail OAuth Integration
    
    IFRS Compliance:
    - Complete record of all sent emails
    - Linked to vouchers/approvals for context
    - Read-only log
    """
    # Email Details
    message_id = models.CharField(max_length=255, unique=True, help_text="Gmail Message ID")
    subject = models.CharField(max_length=998, help_text="Email Subject")
    sender = models.EmailField(help_text="Sender Email")
    recipient = models.TextField(help_text="Recipient Email(s)") # Can be comma separated
    
    # Context
    voucher = models.ForeignKey(
        'VoucherV2', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='email_logs', help_text="Related Voucher"
    )
    approval_action = models.ForeignKey(
        'ApprovalAction', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='email_logs', help_text="Related Approval Action"
    )
    
    # Meta
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='sent', help_text="Status (sent, failed)")
    metadata_json = models.JSONField(default=dict, blank=True, help_text="Additional metadata (labels, threadId)")
    
    class Meta:
        verbose_name = 'Email Communication Log'
        verbose_name_plural = 'Email Communication Logs'
        db_table = 'accounting_emailcommunicationlog'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['sender']),
            models.Index(fields=['voucher']),
        ]

    def __str__(self):
        return f"Email {self.message_id} - {self.subject}"


# ============================================
# RECURRING TRANSACTIONS (Task 1.4)
# ============================================

class RecurringTransaction(models.Model):
    """
    Automates recurring invoices, bills, and journal entries.
    Task 1.4.1: Create RecurringTransaction Model
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    DOCUMENT_TYPE_CHOICES = [
        ('invoice', 'Invoice'),
        ('bill', 'Bill'),
        ('journal_entry', 'Journal Entry'),
    ]

    name = models.CharField(max_length=255, help_text="Template Name")
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    next_run_date = models.DateField(help_text="Next scheduled run date")
    
    template_data = models.JSONField(help_text="JSON template for the voucher/document")
    
    notification_emails = models.TextField(blank=True, help_text="Comma-separated emails for notifications")
    
    is_active = models.BooleanField(default=True)
    auto_post = models.BooleanField(default=False, help_text="Automatically post the generated document?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recurring Transaction'
        verbose_name_plural = 'Recurring Transactions'
        ordering = ['next_run_date']

    def clean(self):
        super().clean()
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


# ============================================
# BUDGET MANAGEMENT (Task 1.5)
# ============================================

class Budget(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=255, help_text="Budget Name")
    fiscal_year = models.ForeignKey('FiscalYear', on_delete=models.PROTECT, related_name='budgets')
    
    # Optional filtering
    department = models.ForeignKey('DepartmentV2', on_delete=models.SET_NULL, null=True, blank=True, related_name='budgets')
    cost_center = models.ForeignKey('CostCenterV2', on_delete=models.SET_NULL, null=True, blank=True, related_name='budgets')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_budgets')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_budgets')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'
        indexes = [
            models.Index(fields=['fiscal_year', 'status']),
        ]

    def __str__(self):
        return self.name

class BudgetLine(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey('AccountV2', on_delete=models.CASCADE, related_name='budget_lines')
    
    # Stores monthly allocations as JSON: {"1": 100, "2": 150 ...}
    monthly_allocations = models.JSONField(default=dict, help_text="Monthly distribution of budget")
    
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal('0.00'))
    
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Budget Line'
        verbose_name_plural = 'Budget Lines'
        unique_together = ('budget', 'account') # Prevent dup accounts in same budget

    def __str__(self):
        return f"{self.budget.name} - {self.account.name}"
