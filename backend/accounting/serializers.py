```
"""
Serializers for Accounting App
Includes AuditLog serializer for audit viewer
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounting.models import (
    AuditLog, BankStatement, BankStatementLine, BankReconciliation,
    Cheque, BankTransfer, Invoice, InvoiceItem, VoucherV2, VoucherEntryV2,
    AccountV2, AssetCategory, FixedAsset, FiscalYear, TaxCode, TaxMasterV2,
    TaxGroupV2, TaxGroupItemV2, CurrencyV2, ExchangeRateV2, CostCenterV2, DepartmentV2, EntityV2, 
    BankAccount, FairValueMeasurement, FXRevaluationLog
)

# ... (Existing code) ...

class BankStatementLineSerializer(serializers.ModelSerializer):
    """Serializer for Bank Statement Lines"""
    class Meta:
        model = BankStatementLine
        fields = ['id', 'date', 'description', 'reference', 'amount', 'balance', 'is_reconciled', 'matched_voucher_line']
        read_only_fields = ['is_reconciled', 'matched_voucher_line']

class BankStatementSerializer(serializers.ModelSerializer):
    """Serializer for Bank Statements"""
    lines = BankStatementLineSerializer(many=True, read_only=True)
    
    class Meta:
        model = BankStatement
        fields = [
            'id', 'bank_account', 'statement_date', 'start_date', 'end_date', 
            'opening_balance', 'closing_balance', 'status', 'file_upload', 'created_at', 'lines'
        ]
        read_only_fields = ['created_at', 'status'] # Status handled via actions

class BankReconciliationSerializer(serializers.ModelSerializer):
    """Serializer for Bank Reconciliation sessions"""
    class Meta:
        model = BankReconciliation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'difference', 'status']


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (for audit logs)"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditLog model
    Task 1.7.3: Audit Viewer UI
    
    Provides read-only access to audit logs with user details
    """
    user = UserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'model_name',
            'object_id',
            'action',
            'action_display',
            'user',
            'timestamp',
            'ip_address',
            'changes',
            'reason'
        ]
        read_only_fields = fields  # All fields are read-only (immutable)
    
    def to_representation(self, instance):
        """
        Customize representation to include formatted timestamp
        """
        data = super().to_representation(instance)
        
        # Add formatted timestamp for display
        data['timestamp_formatted'] = instance.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        return data


# ============================================================================
# MODULE 2.2: CHEQUE MANAGEMENT SYSTEM - API SERIALIZERS
# ============================================================================

class ChequeSerializer(serializers.ModelSerializer):
    """
    Serializer for Cheque model
    Module 2.2: Cheque Management System
    """
    bank_account_name = serializers.CharField(source='bank_account.name', read_only=True)
    payee_name = serializers.CharField(source='payee.name', read_only=True)
    voucher_number = serializers.CharField(source='voucher.voucher_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Cheque
        fields = [
            'id', 'cheque_number', 'cheque_date', 'bank_account', 'bank_account_name',
            'payee', 'payee_name', 'amount', 'status', 'status_display', 'voucher',
            'voucher_number', 'clearance_date', 'is_post_dated', 'cancelled_date',
            'cancellation_reason', 'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class ChequeListSerializer(serializers.ModelSerializer):
    """Optimized serializer for Cheque list views"""
    bank_account_name = serializers.CharField(source='bank_account.name', read_only=True)
    payee_name = serializers.CharField(source='payee.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Cheque
        fields = [
            'id', 'cheque_number', 'cheque_date', 'bank_account_name', 'payee_name',
            'amount', 'status', 'status_display', 'is_post_dated', 'clearance_date'
        ]


# ============================================================================
# MODULE 2.3: BANK TRANSFER SYSTEM - API SERIALIZERS
# ============================================================================

class BankTransferSerializer(serializers.ModelSerializer):
    """
    Serializer for BankTransfer model
    Module 2.3: Bank Transfer System
    """
    from_bank_name = serializers.CharField(source='from_bank.name', read_only=True)
    to_bank_name = serializers.CharField(source='to_bank.name', read_only=True)
    from_currency_code = serializers.CharField(source='from_currency.currency_code', read_only=True)
    to_currency_code = serializers.CharField(source='to_currency.currency_code', read_only=True)
    voucher_number = serializers.CharField(source='voucher.voucher_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approval_status_display = serializers.CharField(source='get_approval_status_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    converted_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = BankTransfer
        fields = [
            'id', 'transfer_number', 'transfer_date', 'from_bank', 'from_bank_name',
            'to_bank', 'to_bank_name', 'amount', 'from_currency', 'from_currency_code',
            'to_currency', 'to_currency_code', 'exchange_rate', 'converted_amount',
            'status', 'status_display', 'approval_status', 'approval_status_display',
            'voucher', 'voucher_number', 'description', 'reference',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'converted_amount']


class BankTransferListSerializer(serializers.ModelSerializer):
    """Optimized serializer for BankTransfer list views"""
    from_bank_name = serializers.CharField(source='from_bank.name', read_only=True)
    to_bank_name = serializers.CharField(source='to_bank.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approval_status_display = serializers.CharField(source='get_approval_status_display', read_only=True)
    
    class Meta:
        model = BankTransfer
        fields = [
            'id', 'transfer_number', 'transfer_date', 'from_bank_name', 'to_bank_name',
            'amount', 'status', 'status_display', 'approval_status', 'approval_status_display'
        ]


# ============================================================================
# INVOICE SERIALIZERS - LEGACY MODEL
# ============================================================================

class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for Invoice Items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'line_number', 'product', 'product_name', 'description',
            'quantity', 'unit_price', 'discount_percentage', 'tax_percentage', 'line_total'
        ]
        read_only_fields = ['line_total']


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Invoice model (Legacy)
    Supports Sales and Purchase Invoices
    """
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    outstanding_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'invoice_type_display', 'invoice_date',
            'due_date', 'partner', 'partner_name', 'subtotal', 'tax_amount', 'discount_amount',
            'total_amount', 'paid_amount', 'outstanding_amount', 'status', 'status_display',
            'user_references', 'reference_number', 'journal_entry', 'notes', 'terms_and_conditions',
            'created_at', 'created_by', 'created_by_username', 'items', 'is_overdue'
        ]
        read_only_fields = ['created_at', 'created_by', 'outstanding_amount', 'is_overdue']


class InvoiceListSerializer(serializers.ModelSerializer):
    """Optimized serializer for Invoice list views"""
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    invoice_type_display = serializers.CharField(source='get_invoice_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    outstanding_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'invoice_type_display', 'invoice_date',
            'due_date', 'partner_name', 'total_amount', 'paid_amount', 'outstanding_amount',
            'status', 'status_display'
        ]


# ============================================================================
# VOUCHER V2 SERIALIZERS - ENHANCED MODEL
# ============================================================================

class VoucherEntryV2Serializer(serializers.ModelSerializer):
    """Serializer for Voucher Entries V2"""
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = VoucherEntryV2
        fields = [
            'id', 'line_number', 'account', 'account_code', 'account_name',
            'description', 'debit_amount', 'credit_amount', 'cost_center', 'department'
        ]


class VoucherV2Serializer(serializers.ModelSerializer):
    """
    Serializer for VoucherV2 model (Enhanced)
    Universal voucher for all accounting transactions
    """
    party_name = serializers.CharField(source='party.name', read_only=True)
    voucher_type_display = serializers.CharField(source='get_voucher_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    currency_code = serializers.CharField(source='currency.currency_code', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)
    entries = VoucherEntryV2Serializer(many=True, read_only=True, source='entries_v2')
    
    class Meta:
        model = VoucherV2
        fields = [
            'id', 'voucher_number', 'voucher_type', 'voucher_type_display', 'voucher_date',
            'reference_number', 'user_references', 'party', 'party_name', 'total_amount',
            'currency', 'currency_code', 'exchange_rate', 'status', 'status_display',
            'approved_by', 'approved_by_username', 'approved_at', 'narration',
            'created_at', 'created_by', 'created_by_username', 'updated_at', 'entries'
        ]
        read_only_fields = ['created_at', 'created_by', 'updated_at']


class VoucherV2ListSerializer(serializers.ModelSerializer):
    """Optimized serializer for VoucherV2 list views"""
    party_name = serializers.CharField(source='party.name', read_only=True)
    voucher_type_display = serializers.CharField(source='get_voucher_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = VoucherV2
        fields = [
            'id', 'voucher_number', 'voucher_type', 'voucher_type_display', 'voucher_date',
            'party_name', 'total_amount', 'status', 'status_display'
        ]


# ============================================================================
# ACCOUNT V2 SERIALIZERS - ENHANCED CHART OF ACCOUNTS
# ============================================================================

class AccountV2Serializer(serializers.ModelSerializer):
    """
    Serializer for AccountV2 model (Enhanced)
    Hierarchical Chart of Accounts with IFRS compliance
    """
    parent_code = serializers.CharField(source='parent.code', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    account_group_display = serializers.CharField(source='get_account_group_display', read_only=True)
    ifrs_category_display = serializers.CharField(source='get_ifrs_category_display', read_only=True)
    measurement_basis_display = serializers.CharField(source='get_measurement_basis_display', read_only=True)
    ias_reference_display = serializers.CharField(source='get_ias_reference_code_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    
    class Meta:
        model = AccountV2
        fields = [
            'id', 'code', 'name', 'parent', 'parent_code', 'parent_name', 'full_path',
            'account_type', 'account_type_display', 'account_group', 'account_group_display',
            'ias_reference_code', 'ias_reference_display', 'ifrs_category', 'ifrs_category_display',
            'ifrs_subcategory', 'measurement_basis', 'measurement_basis_display',
            'is_group', 'is_active', 'allow_direct_posting', 'opening_balance', 'current_balance',
            'description', 'created_at', 'updated_at', 'created_by', 'created_by_username'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'current_balance', 'full_path']


class AccountV2ListSerializer(serializers.ModelSerializer):
    """Optimized serializer for AccountV2 list views"""
    parent_code = serializers.CharField(source='parent.code', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    
    class Meta:
        model = AccountV2
        fields = [
            'id', 'code', 'name', 'parent_code', 'account_type', 'account_type_display',
            'is_group', 'is_active', 'current_balance'
        ]


class AccountV2HierarchySerializer(serializers.ModelSerializer):
    """
    Hierarchical serializer for AccountV2 tree structure
    Used for Chart of Accounts hierarchy display
    """
    children = serializers.SerializerMethodField()
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    
    class Meta:
        model = AccountV2
        fields = [
            'id', 'code', 'name', 'account_type', 'account_type_display',
            'is_group', 'is_active', 'current_balance', 'children'
        ]
    
    def get_children(self, obj):
        """Recursively get children accounts"""
        if obj.is_group:
            children = obj.children.filter(is_active=True).order_by('code')
            return AccountV2HierarchySerializer(children, many=True, context=self.context).data
        return []

# ============================================
# FIXED ASSET SERIALIZERS (IAS 16 Compliance)
# ============================================
# Module 3.1: Fixed Asset Register
# Task 3.1.2: Asset Acquisition Form

class AssetCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for AssetCategory
    IAS 16: Asset classification with depreciation parameters
    """
    depreciation_method_display = serializers.CharField(
        source='get_depreciation_method_display',
        read_only=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    
    class Meta:
        model = AssetCategory
        fields = [
            'id', 'category_code', 'category_name', 'description',
            'useful_life_years', 'depreciation_method', 'depreciation_method_display',
            'residual_value_percentage', 'ias_reference_code', 'is_active',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class FixedAssetSerializer(serializers.ModelSerializer):
    """
    Serializer for FixedAsset
    IAS 16: Property, Plant and Equipment
    
    Includes book value calculation and category details
    """
    book_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    category_name = serializers.CharField(
        source='asset_category.category_name',
        read_only=True
    )
    category_code = serializers.CharField(
        source='asset_category.category_code',
        read_only=True
    )
    gl_account_code = serializers.CharField(
        source='gl_account.code',
        read_only=True,
        allow_null=True
    )
    gl_account_name = serializers.CharField(
        source='gl_account.name',
        read_only=True,
        allow_null=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    
    class Meta:
        model = FixedAsset
        fields = [
            'id', 'asset_number', 'asset_name', 'asset_category', 'category_name',
            'category_code', 'acquisition_date', 'acquisition_cost',
            'accumulated_depreciation', 'book_value', 'location', 'asset_tag',
            'status', 'status_display', 'disposal_date', 'disposal_amount',
            'gl_account', 'gl_account_code', 'gl_account_name',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['book_value', 'created_at', 'updated_at', 'created_by']


class FixedAssetListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for listing fixed assets
    Includes minimal fields for performance
    """
    book_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    category_name = serializers.CharField(
        source='asset_category.category_name',
        read_only=True
    )
    
    class Meta:
        model = FixedAsset
        fields = [
            'id', 'asset_number', 'asset_name', 'category_name',
            'acquisition_date', 'acquisition_cost', 'accumulated_depreciation',
            'book_value', 'location', 'asset_tag', 'status', 'status_display'
        ]


# ============================================================================
# FISCAL YEAR SERIALIZER
# ============================================================================

class FiscalYearSerializer(serializers.ModelSerializer):
    """Serializer for Fiscal Year"""
    
    class Meta:
        model = FiscalYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_closed']
        read_only_fields = ['id']
    
    def validate(self, data):
        """Validate fiscal year dates"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError("End date must be after start date")
        return data


# ============================================================================
# TAX CODE SERIALIZER
# ============================================================================

class TaxCodeSerializer(serializers.ModelSerializer):
    """Serializer for Tax Code"""
    
    class Meta:
        model = TaxCode
        fields = ['id', 'code', 'description', 'tax_percentage', 
                  'sales_tax_account', 'purchase_tax_account', 'is_active']
        read_only_fields = ['id']
    
    def validate_tax_percentage(self, value):
        """Validate tax percentage"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Tax percentage must be between 0 and 100")
        return value


# ============================================================================
# TAX MASTER V2 SERIALIZER
# ============================================================================

class TaxMasterV2Serializer(serializers.ModelSerializer):
    """Serializer for Tax Master V2 - IAS 12 Compliant"""
    tax_type_display = serializers.CharField(source='get_tax_type_display', read_only=True)
    
    class Meta:
        model = TaxMasterV2
        fields = ['id', 'tax_code', 'tax_name', 'tax_type', 'tax_type_display', 
                  'tax_rate', 'tax_collected_account', 'tax_paid_account', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_tax_rate(self, value):
        """Validate tax rate"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Tax rate must be between 0 and 100")
        return value


# ============================================================================
# TAX GROUP V2 SERIALIZERS
# ============================================================================

class TaxGroupItemV2Serializer(serializers.ModelSerializer):
    """Serializer for Tax Group Item V2"""
    tax_name = serializers.CharField(source='tax.tax_name', read_only=True)
    tax_code = serializers.CharField(source='tax.tax_code', read_only=True)
    tax_rate = serializers.DecimalField(source='tax.tax_rate', max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = TaxGroupItemV2
        fields = ['id', 'tax', 'tax_name', 'tax_code', 'tax_rate', 'sequence', 'apply_on_previous']
        read_only_fields = ['id']


class TaxGroupV2Serializer(serializers.ModelSerializer):
    """Serializer for Tax Group V2"""
    items = TaxGroupItemV2Serializer(source='items_v2', many=True, read_only=True)
    total_tax_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = TaxGroupV2
        fields = ['id', 'group_name', 'description', 'is_active', 'items', 'total_tax_rate', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_total_tax_rate(self, obj):
        """Calculate total tax rate (simple sum, not compound)"""
        total = sum(item.tax.tax_rate for item in obj.items_v2.all())
        return float(total)


# ============================================================================
# CURRENCY V2 SERIALIZER
# ============================================================================

class CurrencyV2Serializer(serializers.ModelSerializer):
    """Serializer for Currency V2 - IAS 21 Compliant"""
    
    class Meta:
        model = CurrencyV2
        fields = ['id', 'currency_code', 'currency_name', 'symbol', 
                  'is_base_currency', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_currency_code(self, value):
        """Validate currency code is 3 characters and uppercase"""
        if len(value) != 3:
            raise serializers.ValidationError("Currency code must be exactly 3 characters")
        return value.upper()


# ============================================================================
# EXCHANGE RATE V2 SERIALIZER
# ============================================================================

class ExchangeRateV2Serializer(serializers.ModelSerializer):
    """Serializer for Exchange Rate V2 - IAS 21 Compliant"""
    from_currency_code = serializers.CharField(source='from_currency.currency_code', read_only=True)
    to_currency_code = serializers.CharField(source='to_currency.currency_code', read_only=True)
    from_currency_name = serializers.CharField(source='from_currency.currency_name', read_only=True)
    to_currency_name = serializers.CharField(source='to_currency.currency_name', read_only=True)
    
    class Meta:
        model = ExchangeRateV2
        fields = ['id', 'from_currency', 'to_currency', 'from_currency_code', 'to_currency_code',
                  'from_currency_name', 'to_currency_name', 'rate_date', 'exchange_rate', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_exchange_rate(self, value):
        """Validate exchange rate is positive"""
        if value <= 0:
            raise serializers.ValidationError("Exchange rate must be greater than 0")
        return value


# ============================================================================
# COST CENTER V2 SERIALIZER
# ============================================================================

class CostCenterV2Serializer(serializers.ModelSerializer):
    """Serializer for Cost Center V2"""
    
    class Meta:
        model = CostCenterV2
        fields = ['id', 'code', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# DEPARTMENT V2 SERIALIZER
# ============================================================================

class DepartmentV2Serializer(serializers.ModelSerializer):
    """Serializer for Department V2"""
    
    class Meta:
        model = DepartmentV2
        fields = ['id', 'code', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# ENTITY V2 SERIALIZER
# ============================================================================

class EntityV2Serializer(serializers.ModelSerializer):
    """Serializer for Entity V2"""
    
    class Meta:
        model = EntityV2
        fields = ['id', 'code', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# BANK ACCOUNT SERIALIZER
# ============================================================================

class BankAccountSerializer(serializers.ModelSerializer):
    """Serializer for Bank Account"""
    currency_code = serializers.CharField(source='currency.currency_code', read_only=True)
    currency_name = serializers.CharField(source='currency.currency_name', read_only=True)
    
    class Meta:
        model = BankAccount
        fields = ['id', 'account_number', 'account_name', 'bank_name', 'branch', 
                  'currency', 'currency_code', 'currency_name', 'opening_balance', 
                  'current_balance', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'current_balance', 'created_at', 'updated_at']


# ============================================================================
# BANK STATEMENT SERIALIZERS
# ============================================================================

class BankStatementLineSerializer(serializers.ModelSerializer):
    """Serializer for Bank Statement Line"""
    
    class Meta:
        model = BankStatementLine
        fields = ['id', 'transaction_date', 'description', 'reference', 
                  'debit', 'credit', 'balance', 'is_reconciled']
        read_only_fields = ['id']


class BankStatementSerializer(serializers.ModelSerializer):
    """Serializer for Bank Statement"""
    lines = BankStatementLineSerializer(many=True, read_only=True)
    bank_account_name = serializers.CharField(source='bank_account.account_name', read_only=True)
    bank_name = serializers.CharField(source='bank_account.bank_name', read_only=True)
    
    class Meta:
        model = BankStatement
        fields = ['id', 'bank_account', 'bank_account_name', 'bank_name', 
                  'statement_date', 'opening_balance', 'closing_balance', 
                  'is_reconciled', 'lines', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# FAIR VALUE MEASUREMENT SERIALIZER (IAS 39/IFRS 9)
# ============================================================================

class FairValueMeasurementSerializer(serializers.ModelSerializer):
    """Serializer for Fair Value Measurement"""
    asset_name = serializers.CharField(source='asset.asset_name', read_only=True)
    asset_code = serializers.CharField(source='asset.asset_code', read_only=True)
    
    class Meta:
        model = FairValueMeasurement
        fields = ['id', 'asset', 'asset_name', 'asset_code', 'measurement_date', 
                  'fair_value', 'valuation_technique', 'level', 'notes', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# FX REVALUATION LOG SERIALIZER (IAS 21)
# ============================================================================

class FXRevaluationLogSerializer(serializers.ModelSerializer):
    """Serializer for FX Revaluation Log"""
    entity_code = serializers.CharField(source='entity.entity_code', read_only=True)
    entity_name = serializers.CharField(source='entity.entity_name', read_only=True)
    currency_code = serializers.CharField(source='functional_currency.currency_code', read_only=True)
    
    class Meta:
        model = FXRevaluationLog
        fields = ['id', 'revaluation_id', 'entity', 'entity_code', 'entity_name', 
                  'revaluation_date', 'functional_currency', 'currency_code',
                  'accounts_revalued', 'total_gain', 'total_loss', 'net_fx_gain_loss',
                  'voucher', 'reversal_voucher', 'status', 'execution_method',
                  'auto_posted', 'reversal_created', 'revaluation_details',
                  'error_message', 'notes', 'created_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'created_by']
