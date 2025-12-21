from rest_framework import serializers
from .models import (FiscalYear, AccountType, ChartOfAccounts, JournalEntry, JournalEntryLine,
                     Invoice, InvoiceItem, Payment, PaymentAllocation, BankAccount, TaxCode, AccountV2,
                     VoucherV2, VoucherEntryV2)

class FiscalYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalYear
        fields = '__all__'

class AccountTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountType
        fields = '__all__'

class ChartOfAccountsSerializer(serializers.ModelSerializer):
    account_type_name = serializers.CharField(source='account_type.name', read_only=True)
    type_category = serializers.CharField(source='account_type.type_category', read_only=True)
    current_balance = serializers.ReadOnlyField()
    
    class Meta:
        model = ChartOfAccounts
        fields = '__all__'

class AccountV2Serializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = AccountV2
        fields = '__all__'

class JournalEntryLineSerializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    
    class Meta:
        model = JournalEntryLine
        fields = '__all__'

class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(many=True, read_only=True)
    fiscal_year_name = serializers.CharField(source='fiscal_year.name', read_only=True)
    total_debit = serializers.ReadOnlyField()
    total_credit = serializers.ReadOnlyField()
    is_balanced = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

class InvoiceItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.code', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    outstanding_amount = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    outstanding_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = ('id', 'invoice_number', 'invoice_type', 'partner_name', 'invoice_date', 
                  'total_amount', 'outstanding_amount', 'status')

class PaymentAllocationSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    
    class Meta:
        model = PaymentAllocation
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    allocations = PaymentAllocationSerializer(many=True, read_only=True)
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    bank_account_name = serializers.CharField(source='bank_account.account_name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None

class BankAccountSerializer(serializers.ModelSerializer):
    gl_account_name = serializers.CharField(source='gl_account.account_name', read_only=True)
    current_balance = serializers.ReadOnlyField()
    
    class Meta:
        model = BankAccount
        fields = '__all__'

class TaxCodeSerializer(serializers.ModelSerializer):
    sales_tax_account_name = serializers.CharField(source='sales_tax_account.account_name', read_only=True)
    purchase_tax_account_name = serializers.CharField(source='purchase_tax_account.account_name', read_only=True)
    
    class Meta:
        model = TaxCode
        fields = '__all__'

class VoucherEntryV2Serializer(serializers.ModelSerializer):
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    cost_center_name = serializers.CharField(source='cost_center.name', read_only=True)
    
    class Meta:
        model = VoucherEntryV2
        fields = '__all__'

class VoucherV2Serializer(serializers.ModelSerializer):
    entries = VoucherEntryV2Serializer(source='entries_v2', many=True, read_only=True)
    party_name = serializers.CharField(source='party.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = VoucherV2
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by', 'updated_at', 'approved_by', 'approved_at')
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None
