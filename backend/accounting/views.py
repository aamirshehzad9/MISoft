from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Q
from .models import (FiscalYear, AccountType, ChartOfAccounts, JournalEntry, JournalEntryLine,
                     Invoice, InvoiceItem, Payment, PaymentAllocation, BankAccount, TaxCode, AccountV2,
                     VoucherV2)
from .serializers import (FiscalYearSerializer, AccountTypeSerializer, ChartOfAccountsSerializer,
                          JournalEntrySerializer, JournalEntryLineSerializer,
                          InvoiceSerializer, InvoiceListSerializer, InvoiceItemSerializer,
                          PaymentSerializer, PaymentAllocationSerializer,
                          BankAccountSerializer, TaxCodeSerializer, AccountV2Serializer,
                          VoucherV2Serializer)
from .services import VoucherService

class FiscalYearViewSet(viewsets.ModelViewSet):
    queryset = FiscalYear.objects.all()
    serializer_class = FiscalYearSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_closed']

class AccountTypeViewSet(viewsets.ModelViewSet):
    queryset = AccountType.objects.all()
    serializer_class = AccountTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type_category']

class ChartOfAccountsViewSet(viewsets.ModelViewSet):
    queryset = ChartOfAccounts.objects.select_related('account_type').all()
    serializer_class = ChartOfAccountsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'is_active', 'is_header']
    search_fields = ['account_code', 'account_name']
    ordering_fields = ['account_code', 'account_name']
    ordering = ['account_code']
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get accounts grouped by type"""
        account_type = request.query_params.get('type')
        if account_type:
            accounts = self.queryset.filter(account_type__type_category=account_type, is_active=True)
            serializer = self.get_serializer(accounts, many=True)
            return Response(serializer.data)
        return Response({'error': 'Type parameter required'}, status=status.HTTP_400_BAD_REQUEST)

class AccountV2ViewSet(viewsets.ModelViewSet):
    """ViewSet for Enhanced Hierarchical Chart of Accounts"""
    queryset = AccountV2.objects.all()
    serializer_class = AccountV2Serializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'account_group', 'is_group', 'is_active', 'parent']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
    ordering = ['code']

    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Get accounts in a flat list optimized for hierarchy building"""
        accounts = self.queryset.filter(is_active=True).order_by('code')
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)

class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.select_related('fiscal_year').prefetch_related('lines').all()
    serializer_class = JournalEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['entry_type', 'status', 'fiscal_year']
    search_fields = ['entry_number', 'reference_number', 'description']
    ordering_fields = ['entry_date', 'entry_number']
    ordering = ['-entry_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def post_entry(self, request, pk=None):
        """Post journal entry"""
        entry = self.get_object()
        if entry.status == 'draft':
            if entry.is_balanced:
                entry.status = 'posted'
                entry.posted_date = timezone.now()
                entry.save()
                return Response({'message': 'Entry posted successfully'})
            return Response({'error': 'Entry is not balanced'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Entry is not in draft status'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel_entry(self, request, pk=None):
        """Cancel journal entry"""
        entry = self.get_object()
        if entry.status == 'posted':
            entry.status = 'cancelled'
            entry.save()
            return Response({'message': 'Entry cancelled'})
        return Response({'error': 'Only posted entries can be cancelled'}, status=status.HTTP_400_BAD_REQUEST)

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('partner').prefetch_related('items').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['invoice_type', 'status', 'partner']
    search_fields = ['invoice_number', 'partner__name', 'reference_number']
    ordering_fields = ['invoice_date', 'invoice_number', 'total_amount']
    ordering = ['-invoice_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def sales_invoices(self, request):
        """Get sales invoices"""
        invoices = self.queryset.filter(invoice_type='sales')
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def purchase_invoices(self, request):
        """Get purchase invoices"""
        invoices = self.queryset.filter(invoice_type='purchase')
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue invoices"""
        today = timezone.now().date()
        invoices = self.queryset.filter(
            due_date__lt=today,
            status__in=['submitted', 'partially_paid']
        ).exclude(paid_amount__gte=models.F('total_amount'))
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit_invoice(self, request, pk=None):
        """Submit invoice"""
        invoice = self.get_object()
        if invoice.status == 'draft':
            invoice.status = 'submitted'
            invoice.save()
            return Response({'message': 'Invoice submitted'})
        return Response({'error': 'Invoice is not in draft status'}, status=status.HTTP_400_BAD_REQUEST)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('partner', 'bank_account').prefetch_related('allocations').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_type', 'payment_mode', 'partner']
    search_fields = ['payment_number', 'partner__name', 'reference_number']
    ordering_fields = ['payment_date', 'payment_number', 'amount']
    ordering = ['-payment_date']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def receipts(self, request):
        """Get all receipts"""
        receipts = self.queryset.filter(payment_type='receipt')
        serializer = self.get_serializer(receipts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def payments_made(self, request):
        """Get all payments made"""
        payments = self.queryset.filter(payment_type='payment')
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.select_related('gl_account').all()
    serializer_class = BankAccountSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'currency']
    search_fields = ['account_name', 'account_number', 'bank_name', 'iban']
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get bank account transactions"""
        bank_account = self.get_object()
        transactions = Payment.objects.filter(bank_account=bank_account).order_by('-payment_date')
        serializer = PaymentSerializer(transactions, many=True)
        return Response(serializer.data)

class TaxCodeViewSet(viewsets.ModelViewSet):
    queryset = TaxCode.objects.select_related('sales_tax_account', 'purchase_tax_account').all()
    serializer_class = TaxCodeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'description']

class VoucherV2ViewSet(viewsets.ModelViewSet):
    """ViewSet for Double-Entry Vouchers (V2)"""
    queryset = VoucherV2.objects.select_related('party', 'currency', 'created_by', 'approved_by').prefetch_related('entries_v2__account').all()
    serializer_class = VoucherV2Serializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['voucher_type', 'status', 'voucher_date']
    search_fields = ['voucher_number', 'reference_number', 'narration']
    ordering_fields = ['voucher_date', 'voucher_number']
    ordering = ['-voucher_date']
    
    def create(self, request, *args, **kwargs):
        """Create voucher via service"""
        try:
            voucher = VoucherService.create_voucher(request.data, user=request.user)
            serializer = self.get_serializer(voucher)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """Post voucher via service"""
        try:
            voucher = VoucherService.post_voucher(pk, user=request.user)
            serializer = self.get_serializer(voucher)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
