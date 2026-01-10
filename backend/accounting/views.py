"""
Views for Accounting App
Includes AuditLog ViewSet for audit viewer
"""
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter, DateTimeFilter
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from accounting.models import (
    AuditLog, BankStatement, BankReconciliation, AccountV2,
    Cheque, BankTransfer, Invoice, VoucherV2,
    ApprovalWorkflow, ApprovalLevel, ApprovalRequest, ApprovalAction,
    Budget, RecurringTransaction,
)
from accounting.serializers import (
    AuditLogSerializer, BankStatementSerializer, BankReconciliationSerializer,
    ChequeSerializer, ChequeListSerializer,
    BankTransferSerializer, BankTransferListSerializer,
    InvoiceSerializer, InvoiceListSerializer,
    VoucherV2Serializer, VoucherV2ListSerializer,
    AccountV2Serializer, AccountV2ListSerializer, AccountV2HierarchySerializer,
    ApprovalWorkflowSerializer, ApprovalLevelSerializer, ApprovalRequestSerializer,
    ApprovalActionSerializer, ApprovalRequestActionSerializer,
    RecurringTransactionSerializer,
)
from accounting.services.audit_service import AuditService
from accounting.services.bank_reconciliation_service import BankReconciliationService
from accounting.services.cheque_service import ChequeService
from accounting.services.approval_report_service import ApprovalReportService
from accounting.services.gmail_service import GmailAuthService, GmailSenderService
from accounting.services.bank_transfer_service import BankTransferService
from accounting.services.recurring_service import RecurringTransactionService
from accounting.services.budget_service import BudgetService
from accounting.services.cost_center_service import CostCenterService
from django.contrib.auth import get_user_model
import datetime
from decimal import Decimal

User = get_user_model()

# ... (Existing ViewSets) ...

class BankStatementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bank Statements
    Task 2.1.2: Reconciliation Engine
    IAS 7: Cash Flow Statement Support
    """
    queryset = BankStatement.objects.all().order_by('-statement_date')
    serializer_class = BankStatementSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    # Remove DjangoFilterBackend to prevent auto-filtering errors
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['bank_account__name', 'statement_date']
    ordering_fields = ['statement_date', 'created_at']
    ordering = ['-statement_date']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """Filter by bank account if provided"""
        queryset = super().get_queryset()
        bank_account_id = self.request.query_params.get('bank_account')
        status_filter = self.request.query_params.get('status')
        
        if bank_account_id:
            queryset = queryset.filter(bank_account_id=bank_account_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    @action(detail=True, methods=['post'], url_path='auto-match')
    def auto_match(self, request, pk=None):
        """
        Trigger auto-matching for this statement
        POST /api/accounting/bank-statements/{id}/auto-match/
        """
        statement = self.get_object()
        matches = BankReconciliationService.auto_match_transactions(statement)
        return Response({
            'message': f'Auto-matching completed. {matches} transactions matched.',
            'matches_found': matches
        })
        
    @action(detail=True, methods=['post'], url_path='post-charges')
    def post_charges(self, request, pk=None):
        """
        Post bank charges
        POST /api/accounting/bank-statements/{id}/post-charges/
        Body: { "line_ids": [1, 2], "expense_account_id": 55 }
        """
        statement = self.get_object()
        line_ids = request.data.get('line_ids', [])
        expense_account_id = request.data.get('expense_account_id')
        
        if not line_ids or not expense_account_id:
            return Response(
                {'error': 'line_ids and expense_account_id are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            expense_account = AccountV2.objects.get(id=expense_account_id)
            voucher = BankReconciliationService.post_bank_charges(
                statement=statement,
                line_ids=line_ids,
                expense_account=expense_account,
                user=request.user
            )
            
            if voucher:
                return Response({'message': 'Bank charges posted successfully', 'voucher_id': voucher.id})
            else:
                return Response({'message': 'No eligible lines found or total is zero'}, status=status.HTTP_400_BAD_REQUEST)
                
        except AccountV2.DoesNotExist:
             return Response({'error': 'Expense account not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class BankReconciliationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bank Reconciliations
    Task 2.1.2: Reconciliation Engine
    """
    queryset = BankReconciliation.objects.all().order_by('-reconciliation_date')
    serializer_class = BankReconciliationSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reconciled_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Get reconciliation summary statistics
        GET /api/accounting/bank-reconciliations/{id}/summary/
        """
        reconciliation = self.get_object()
        
        outstanding_payments = BankReconciliationService.calculate_outstanding_payments(reconciliation)
        deposits_in_transit = BankReconciliationService.calculate_deposits_in_transit(reconciliation)
        
        # Recalculate difference just in case
        # Adjusted Bank Balance = Statement Balance - Outstanding Checks + Deposits in Transit
        adjusted_bank_balance = reconciliation.statement_balance - outstanding_payments + deposits_in_transit
        
        # Difference = Adjusted Bank Balance - Ledger Balance
        # Should be near zero
        difference = adjusted_bank_balance - reconciliation.ledger_balance
        
        return Response({
            'statement_balance': reconciliation.statement_balance,
            'ledger_balance': reconciliation.ledger_balance,
            'outstanding_payments': outstanding_payments,
            'deposits_in_transit': deposits_in_transit,
            'adjusted_bank_balance': adjusted_bank_balance,
            'difference': difference,
            'is_balanced': abs(difference) < 0.01
        })

    @action(detail=True, methods=['get'], url_path='brs-report')
    def brs_report(self, request, pk=None):
        """
        Generate Bank Reconciliation Statement (BRS) Report
        Task 2.1.3: BRS Report
        
        GET /api/accounting/bank-reconciliations/{id}/brs-report/
        
        Returns comprehensive BRS report with all reconciliation details
        """
        reconciliation = self.get_object()
        report = BankReconciliationService.generate_brs_report(reconciliation)
        return Response(report)

    @action(detail=True, methods=['get'], url_path='outstanding-cheques')
    def outstanding_cheques(self, request, pk=None):
        """
        Generate Outstanding Cheques Report
        Task 2.1.3: BRS Report
        
        GET /api/accounting/bank-reconciliations/{id}/outstanding-cheques/
        
        Returns list of all checks issued but not yet cleared
        """
        reconciliation = self.get_object()
        report = BankReconciliationService.generate_outstanding_cheques_report(reconciliation)
        return Response(report)

    @action(detail=True, methods=['get'], url_path='deposits-in-transit')
    def deposits_in_transit(self, request, pk=None):
        """
        Generate Deposits in Transit Report
        Task 2.1.3: BRS Report
        
        GET /api/accounting/bank-reconciliations/{id}/deposits-in-transit/
        
        Returns list of all deposits recorded but not yet in bank statement
        """
        reconciliation = self.get_object()
        report = BankReconciliationService.generate_deposits_in_transit_report(reconciliation)
        return Response(report)



class AuditLogPagination(PageNumberPagination):
    """Pagination class for audit logs"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100



class AuditLogFilter(FilterSet):
    """
    Filter class for AuditLog
    Supports filtering by model, user, action, object_id, and date range
    """
    model_name = CharFilter(field_name='model_name', lookup_expr='iexact')
    user = NumberFilter(field_name='user__id')
    action = CharFilter(field_name='action', lookup_expr='iexact')
    object_id = NumberFilter(field_name='object_id')
    start_date = DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    end_date = DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    class Meta:
        model = AuditLog
        fields = ['model_name', 'user', 'action', 'object_id', 'start_date', 'end_date']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs
    Task 1.7.3: Audit Viewer UI
    
    Provides read-only access to audit logs with filtering and search
    
    Endpoints:
        GET /api/accounting/audit-logs/              - List with filters
        GET /api/accounting/audit-logs/{id}/         - Detail view
        GET /api/accounting/audit-logs/export-pdf/   - Export to PDF
    
    Query Parameters:
        - model_name: Filter by model name
        - user: Filter by user ID
        - action: Filter by CREATE/UPDATE/DELETE
        - object_id: Filter by specific object
        - start_date: Filter from date (ISO format)
        - end_date: Filter to date (ISO format)
        - search: Search in changes field
        - page: Page number
        - page_size: Items per page
    """
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AuditLogPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuditLogFilter
    search_fields = ['model_name', 'changes', 'reason']
    ordering_fields = ['timestamp', 'model_name', 'action']
    ordering = ['-timestamp']  # Newest first by default
    
    # Disable create, update, delete (read-only)
    http_method_names = ['get', 'head', 'options']
    
    @action(detail=False, methods=['get'], url_path='export-pdf')
    def export_pdf(self, request):
        """
        Export audit logs to PDF
        
        GET /api/accounting/audit-logs/export-pdf/
        
        Applies the same filters as the list view
        Returns a PDF file with audit log report
        """
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        # For now, return a simple response
        # TODO: Implement actual PDF generation
        return Response({
            'message': 'PDF export functionality',
            'total_records': queryset.count(),
            'note': 'PDF generation to be implemented'
        }, status=status.HTTP_200_OK)
    @action(detail=False, methods=['get'], url_path='user-activity-report')
    def user_activity_report(self, request):
        """
        Generate user activity report
        
        GET /api/accounting/audit-logs/user-activity-report/
        """
        user_id = request.query_params.get('user')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        report = AuditService.generate_user_activity_report(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response(report)

    @action(detail=False, methods=['get'], url_path='change-history-report')
    def change_history_report(self, request):
        """
        Generate change history report
        
        GET /api/accounting/audit-logs/change-history-report/
        """
        model_name = request.query_params.get('model_name')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        report = AuditService.generate_change_history_report(
            model_name=model_name,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response(report)

        return Response(report)

    @action(detail=False, methods=['get'], url_path='object-history-report')
    def object_history_report(self, request):
        """
        Generate audit trail report for a specific object
        
        GET /api/accounting/audit-logs/object-history-report/?model_name=X&object_id=Y
        """
        model_name = request.query_params.get('model_name')
        object_id = request.query_params.get('object_id')
        
        if not model_name or not object_id:
            return Response(
                {'error': 'model_name and object_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        report = AuditService.generate_object_audit_report(
            model_name=model_name,
            object_id=object_id
        )
        return Response(report)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Get complete history for a specific object
        
        GET /api/accounting/audit-logs/{id}/history/
        
        Returns all audit logs for the same model and object_id
        """
        audit_log = self.get_object()
        
        # Get all logs for this object
        history = AuditLog.objects.filter(
            model_name=audit_log.model_name,
            object_id=audit_log.object_id
        ).select_related('user').order_by('-timestamp')
        
        serializer = self.get_serializer(history, many=True)
        
        return Response({
            'model_name': audit_log.model_name,
            'object_id': audit_log.object_id,
            'total_changes': history.count(),
            'history': serializer.data
        })


# ============================================================================
# MODULE 2.2: CHEQUE MANAGEMENT SYSTEM - API VIEWSETS
# ============================================================================

class ChequeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cheque Management
    Module 2.2: Cheque Management System
    
    Endpoints:
        GET    /api/accounting/cheques/              - List cheques
        POST   /api/accounting/cheques/              - Create cheque
        GET    /api/accounting/cheques/{id}/         - Get cheque details
        PUT    /api/accounting/cheques/{id}/         - Update cheque
        DELETE /api/accounting/cheques/{id}/         - Delete cheque
        POST   /api/accounting/cheques/{id}/clear/   - Clear cheque
        POST   /api/accounting/cheques/{id}/cancel/  - Cancel cheque
        GET    /api/accounting/cheques/{id}/print/   - Print cheque (PDF)
        GET    /api/accounting/cheques/post-dated/   - Get post-dated cheques
    """
    queryset = Cheque.objects.all().select_related('bank_account', 'payee', 'voucher', 'created_by').order_by('-cheque_date')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChequeListSerializer
        return ChequeSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """Filter by status, date range, etc."""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        is_post_dated = self.request.query_params.get('is_post_dated')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if is_post_dated:
            queryset = queryset.filter(is_post_dated=is_post_dated.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        """
        Clear a cheque
        POST /api/accounting/cheques/{id}/clear/
        Body: { "clearance_date": "2025-01-20" }
        """
        cheque = self.get_object()
        clearance_date_str = request.data.get('clearance_date')
        
        if not clearance_date_str:
            return Response(
                {'error': 'clearance_date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            clearance_date = datetime.datetime.strptime(clearance_date_str, '%Y-%m-%d').date()
            cleared_cheque = ChequeService.clear_cheque(cheque, clearance_date)
            serializer = self.get_serializer(cleared_cheque)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a cheque
        POST /api/accounting/cheques/{id}/cancel/
        Body: { "cancelled_date": "2025-01-18", "cancellation_reason": "Payment terms changed" }
        """
        cheque = self.get_object()
        cancelled_date_str = request.data.get('cancelled_date')
        cancellation_reason = request.data.get('cancellation_reason')
        
        if not cancelled_date_str or not cancellation_reason:
            return Response(
                {'error': 'cancelled_date and cancellation_reason are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cancelled_date = datetime.datetime.strptime(cancelled_date_str, '%Y-%m-%d').date()
            cancelled_cheque = ChequeService.cancel_cheque(cheque, cancelled_date, cancellation_reason)
            serializer = self.get_serializer(cancelled_cheque)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def print(self, request, pk=None):
        """
        Print cheque as PDF
        GET /api/accounting/cheques/{id}/print/
        """
        cheque = self.get_object()
        pdf_buffer = ChequeService.print_cheque(cheque)
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cheque_{cheque.cheque_number}.pdf"'
        return response
    
    @action(detail=False, methods=['get'], url_path='post-dated')
    def post_dated(self, request):
        """
        Get all post-dated cheques
        GET /api/accounting/cheques/post-dated/
        """
        cheques = ChequeService.get_post_dated_cheques()
        serializer = ChequeListSerializer(cheques, many=True)
        return Response(serializer.data)


# ============================================================================
# MODULE 2.3: BANK TRANSFER SYSTEM - API VIEWSETS
# ============================================================================

class BankTransferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bank Transfer Management
    Module 2.3: Bank Transfer System
    
    Endpoints:
        GET    /api/accounting/bank-transfers/                - List transfers
        POST   /api/accounting/bank-transfers/                - Create transfer
        GET    /api/accounting/bank-transfers/{id}/           - Get transfer details
        PUT    /api/accounting/bank-transfers/{id}/           - Update transfer
        DELETE /api/accounting/bank-transfers/{id}/           - Delete transfer
        POST   /api/accounting/bank-transfers/{id}/approve/   - Approve transfer
        POST   /api/accounting/bank-transfers/{id}/reject/    - Reject transfer
        POST   /api/accounting/bank-transfers/{id}/execute/   - Execute transfer
        GET    /api/accounting/bank-transfers/pending/        - Get pending transfers
    """
    queryset = BankTransfer.objects.all().select_related(
        'from_bank', 'to_bank', 'from_currency', 'to_currency', 'voucher', 'created_by'
    ).order_by('-transfer_date')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BankTransferListSerializer
        return BankTransferSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """Filter by status, approval status, etc."""
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        approval_status_filter = self.request.query_params.get('approval_status')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if approval_status_filter:
            queryset = queryset.filter(approval_status=approval_status_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a transfer
        POST /api/accounting/bank-transfers/{id}/approve/
        """
        transfer = self.get_object()
        
        try:
            approved_transfer = BankTransferService.approve_transfer(transfer, request.user)
            serializer = self.get_serializer(approved_transfer)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a transfer
        POST /api/accounting/bank-transfers/{id}/reject/
        """
        transfer = self.get_object()
        
        try:
            rejected_transfer = BankTransferService.reject_transfer(transfer, request.user)
            serializer = self.get_serializer(rejected_transfer)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Execute a transfer (creates voucher)
        POST /api/accounting/bank-transfers/{id}/execute/
        Body: { "fx_account_id": 123 } (optional, for multi-currency)
        """
        transfer = self.get_object()
        fx_account_id = request.data.get('fx_account_id')
        fx_account = None
        
        if fx_account_id:
            try:
                fx_account = AccountV2.objects.get(id=fx_account_id)
            except AccountV2.DoesNotExist:
                return Response(
                    {'error': 'FX account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        try:
            executed_transfer = BankTransferService.execute_transfer(transfer, request.user, fx_account)
            serializer = self.get_serializer(executed_transfer)
            return Response(serializer.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending transfers
        GET /api/accounting/bank-transfers/pending/
        """
        transfers = BankTransferService.get_pending_transfers()
        serializer = BankTransferListSerializer(transfers, many=True)
        return Response(serializer.data)

# ============================================================================
# INVOICE VIEWSET - LEGACY MODEL
# ============================================================================

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Invoice Management (Legacy)
    Supports Sales and Purchase Invoices
    
    Endpoints:
        GET    /api/accounting/invoices/              - List invoices
        POST   /api/accounting/invoices/              - Create invoice
        GET    /api/accounting/invoices/{id}/         - Get invoice details
        PUT    /api/accounting/invoices/{id}/         - Update invoice
        DELETE /api/accounting/invoices/{id}/         - Delete invoice
    """
    queryset = Invoice.objects.all().select_related('partner', 'created_by', 'journal_entry').prefetch_related('items').order_by('-invoice_date')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['invoice_number', 'partner__name', 'reference_number']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount', 'created_at']
    ordering = ['-invoice_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """Filter by invoice type, status, partner, date range"""
        queryset = super().get_queryset()
        invoice_type = self.request.query_params.get('invoice_type')
        status_filter = self.request.query_params.get('status')
        partner_id = self.request.query_params.get('partner')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if partner_id:
            queryset = queryset.filter(partner_id=partner_id)
        if start_date:
            queryset = queryset.filter(invoice_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(invoice_date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='sales_invoices')
    def sales_invoices(self, request):
        """Get all sales invoices (IFRS 15 - Revenue from Contracts with Customers)"""
        queryset = self.get_queryset().filter(invoice_type='sales')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='purchase_invoices')
    def purchase_invoices(self, request):
        """Get all purchase invoices (IAS 2 - Inventories / IAS 16 - PPE)"""
        queryset = self.get_queryset().filter(invoice_type='purchase')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        """Get all overdue invoices (IAS 1 - Presentation of Financial Statements)"""
        from django.utils import timezone
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            due_date__lt=today,
            status__in=['draft', 'submitted', 'partially_paid']
        ).exclude(status='paid')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================================
# VOUCHER V2 VIEWSET - ENHANCED MODEL
# ============================================================================

class VoucherV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VoucherV2 Management (Enhanced)
    Universal voucher for all accounting transactions
    
    Endpoints:
        GET    /api/accounting/vouchers-v2/              - List vouchers
        POST   /api/accounting/vouchers-v2/              - Create voucher
        GET    /api/accounting/vouchers-v2/{id}/         - Get voucher details
        PUT    /api/accounting/vouchers-v2/{id}/         - Update voucher
        DELETE /api/accounting/vouchers-v2/{id}/         - Delete voucher
        POST   /api/accounting/vouchers-v2/{id}/post/    - Post voucher
    """
    queryset = VoucherV2.objects.all().select_related('party', 'currency', 'created_by', 'approved_by').prefetch_related('entries_v2').order_by('-voucher_date')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['voucher_number', 'party__name', 'reference_number', 'narration']
    ordering_fields = ['voucher_date', 'total_amount', 'created_at']
    ordering = ['-voucher_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VoucherV2ListSerializer
        return VoucherV2Serializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """Filter by voucher type, status, party, date range"""
        queryset = super().get_queryset()
        voucher_type = self.request.query_params.get('voucher_type')
        status_filter = self.request.query_params.get('status')
        party_id = self.request.query_params.get('party')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if voucher_type:
            queryset = queryset.filter(voucher_type=voucher_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if party_id:
            queryset = queryset.filter(party_id=party_id)
        if start_date:
            queryset = queryset.filter(voucher_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(voucher_date__lte=end_date)
            
        # Approval status filtering (Task 1.3.4)
        approval_status = self.request.query_params.get('approval_status')
        if approval_status:
            try:
                # Handle list of statuses if provided (e.g. ?approval_status=pending,approved)
                if ',' in approval_status:
                    statuses = approval_status.split(',')
                    queryset = queryset.filter(approval_status__in=statuses)
                else:
                    queryset = queryset.filter(approval_status=approval_status)
            except Exception:
                pass
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def post(self, request, pk=None):
        """
        Post a voucher (change status from draft to posted)
        POST /api/accounting/vouchers-v2/{id}/post/
        """
        voucher = self.get_object()
        
        if voucher.status != 'draft':
            return Response(
                {'error': 'Only draft vouchers can be posted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Task 1.3.4: Approval workflow integration
        # Check approval before posting
        can_post, reason = voucher.can_be_posted()
        if not can_post:
            return Response(
                {'error': f'Cannot post voucher: {reason}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Implement balance validation and posting logic
        try:
            with transaction.atomic():
                voucher.status = 'posted'
                # Don't overwrite approved_by if already set by approval workflow
                if not voucher.approved_by:
                    voucher.approved_by = request.user
                    voucher.approved_at = timezone.now()
                voucher.save()
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error posting voucher: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = self.get_serializer(voucher)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def initiate_approval(self, request, pk=None):
        """
        Initiate approval workflow for a voucher
        POST /api/accounting/vouchers-v2/{id}/initiate_approval/
        """
        voucher = self.get_object()
        
        if voucher.status == 'posted':
            return Response(
                {'error': 'Cannot initiate approval for posted vouchers'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if voucher.approval_status in ['approved', 'rejected']:
             return Response(
                {'error': f'Voucher is already {voucher.approval_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            approval_request = voucher.initiate_approval_workflow()
            
            from .serializers import ApprovalRequestSerializer
            serializer = self.get_serializer(voucher)
            
            return Response({
                'message': 'Approval workflow initiated',
                'voucher': serializer.data,
                'approval_request': approval_request.id
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    @action(detail=True, methods=['get'])
    def check_approval_status(self, request, pk=None):
        """
        Check voucher approval status
        GET /api/accounting/vouchers-v2/{id}/check_approval_status/
        """
        voucher = self.get_object()
        
        can_post, reason = voucher.can_be_posted()
        
        return Response({
            'voucher_id': voucher.id,
            'approval_status': voucher.approval_status,
            'requires_approval': voucher.requires_approval(),
            'can_be_posted': can_post,
            'reason': reason,
            'approval_request_id': voucher.approval_request.id if voucher.approval_request else None
        })


# ============================================================================
# ACCOUNT V2 VIEWSET - ENHANCED CHART OF ACCOUNTS
# ============================================================================

class AccountV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AccountV2 Management (Enhanced)
    Hierarchical Chart of Accounts with IFRS compliance
    
    Endpoints:
        GET    /api/accounting/accounts-v2/                - List accounts
        POST   /api/accounting/accounts-v2/                - Create account
        GET    /api/accounting/accounts-v2/{id}/           - Get account details
        PUT    /api/accounting/accounts-v2/{id}/           - Update account
        DELETE /api/accounting/accounts-v2/{id}/           - Delete account
        GET    /api/accounting/accounts-v2/hierarchy/      - Get hierarchical tree
    """
    queryset = AccountV2.objects.all().select_related('parent', 'created_by').order_by('code')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'account_type', 'current_balance']
    ordering = ['code']
    
    def get_serializer_class(self):
        if self.action == 'hierarchy':
            return AccountV2HierarchySerializer
        elif self.action == 'list':
            return AccountV2ListSerializer
        return AccountV2Serializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """Filter by account type, parent, is_active, is_group"""
        queryset = super().get_queryset()
        account_type = self.request.query_params.get('account_type')
        parent_id = self.request.query_params.get('parent')
        is_active = self.request.query_params.get('is_active')
        is_group = self.request.query_params.get('is_group')
        
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if is_group is not None:
            queryset = queryset.filter(is_group=is_group.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """
        Get hierarchical tree structure of accounts
        GET /api/accounting/accounts-v2/hierarchy/
        
        Returns root accounts with nested children
        """
        # Get only root accounts (no parent)
        root_accounts = self.get_queryset().filter(parent__isnull=True, is_active=True)
        serializer = self.get_serializer(root_accounts, many=True)
        return Response(serializer.data)

# ============================================
# FIXED ASSET VIEWSETS (IAS 16 Compliance)
# ============================================
# Module 3.1: Fixed Asset Register
# Task 3.1.2: Asset Acquisition Form

from accounting.models import AssetCategory, FixedAsset
from accounting.serializers import (
    AssetCategorySerializer, FixedAssetSerializer, FixedAssetListSerializer
)
from django_filters.rest_framework import DjangoFilterBackend


class AssetCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AssetCategory
    IAS 16: Asset classification management
    
    Provides CRUD operations for asset categories with depreciation parameters
    """
    queryset = AssetCategory.objects.all().select_related('created_by').order_by('category_code')
    serializer_class = AssetCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'depreciation_method']
    search_fields = ['category_code', 'category_name', 'description']
    ordering_fields = ['category_code', 'category_name', 'useful_life_years', 'created_at']
    ordering = ['category_code']
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)


class FixedAssetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FixedAsset
    IAS 16: Property, Plant and Equipment
    
    Provides CRUD operations for fixed assets with:
    - Asset acquisition workflow
    - Asset tagging and numbering
    - Location tracking
    - Purchase voucher linking
    - Book value calculation
    """
    queryset = FixedAsset.objects.all().select_related(
        'asset_category', 'gl_account', 'created_by'
    ).order_by('-asset_number')
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'asset_category', 'location']
    search_fields = ['asset_number', 'asset_name', 'asset_tag', 'location']
    ordering_fields = [
        'asset_number', 'asset_name', 'acquisition_date', 
        'acquisition_cost', 'status', 'created_at'
    ]
    ordering = ['-asset_number']
    
    def get_serializer_class(self):
        """Use optimized serializer for list view"""
        if self.action == 'list':
            return FixedAssetListSerializer
        return FixedAssetSerializer
    
    def perform_create(self, serializer):
        """Set created_by to current user"""
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """
        Optionally filter assets by additional parameters
        """
        queryset = super().get_queryset()
        
        # Filter by acquisition date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(acquisition_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(acquisition_date__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def dispose(self, request, pk=None):
        """
        Dispose an asset
        IAS 16.67-72: Derecognition
        
        Requires disposal_date and disposal_amount
        Calculates gain/loss on disposal
        """
        asset = self.get_object()
        
        disposal_date = request.data.get('disposal_date')
        disposal_amount = request.data.get('disposal_amount')
        
        if not disposal_date or disposal_amount is None:
            return Response(
                {'error': 'disposal_date and disposal_amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        asset.status = 'disposed'
        asset.disposal_date = disposal_date
        asset.disposal_amount = Decimal(str(disposal_amount))
        asset.save()
        
        gain_loss = asset.calculate_gain_loss_on_disposal()
        
        serializer = self.get_serializer(asset)
        return Response({
            'asset': serializer.data,
            'gain_loss': gain_loss,
            'message': f'Asset disposed. {"Gain" if gain_loss > 0 else "Loss"}: {abs(gain_loss)}'
        })
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """
        Get assets grouped by location
        Useful for location-based asset tracking
        """
        from django.db.models import Count, Sum
        
        locations = FixedAsset.objects.values('location').annotate(
            count=Count('id'),
            total_cost=Sum('acquisition_cost'),
            total_depreciation=Sum('accumulated_depreciation')
        ).order_by('location')
        
        return Response(locations)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get assets grouped by category
        Useful for category-based reporting
        """
        from django.db.models import Count, Sum
        
        categories = FixedAsset.objects.values(
            'asset_category__category_code',
            'asset_category__category_name'
        ).annotate(
            count=Count('id'),
            total_cost=Sum('acquisition_cost'),
            total_depreciation=Sum('accumulated_depreciation')
        ).order_by('asset_category__category_code')
        
        return Response(categories)

# ============================================
# ASSET REPORTS (IAS 16 Compliance)
# ============================================
# Module 3.1: Fixed Asset Register
# Task 3.1.3: Asset Reports

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fixed_asset_register_report(request):
    """
    Fixed Asset Register (FAR) Report
    IAS 16: Complete listing of all fixed assets with book values
    
    Query Parameters:
    - status: Filter by asset status (active, disposed, etc.)
    - category: Filter by asset category ID
    - start_date: Filter by acquisition date (from)
    - end_date: Filter by acquisition date (to)
    """
    # Get query parameters
    status_filter = request.query_params.get('status')
    category_filter = request.query_params.get('category')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    # Build queryset
    queryset = FixedAsset.objects.select_related(
        'asset_category', 'gl_account'
    ).all()
    
    # Apply filters
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    if category_filter:
        queryset = queryset.filter(asset_category_id=category_filter)
    if start_date:
        queryset = queryset.filter(acquisition_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(acquisition_date__lte=end_date)
    
    # Order by asset number
    queryset = queryset.order_by('asset_number')
    
    # Build asset list
    assets = []
    for asset in queryset:
        assets.append({
            'asset_number': asset.asset_number,
            'asset_name': asset.asset_name,
            'category_code': asset.asset_category.category_code,
            'category_name': asset.asset_category.category_name,
            'acquisition_date': asset.acquisition_date,
            'acquisition_cost': str(asset.acquisition_cost),
            'accumulated_depreciation': str(asset.accumulated_depreciation),
            'book_value': str(asset.book_value),
            'location': asset.location,
            'asset_tag': asset.asset_tag,
            'status': asset.status,
        })
    
    # Calculate summary totals
    aggregates = queryset.aggregate(
        total_acquisition_cost=Sum('acquisition_cost'),
        total_accumulated_depreciation=Sum('accumulated_depreciation'),
        total_assets=Count('id')
    )
    
    # Calculate total book value
    total_book_value = Decimal('0.00')
    if aggregates['total_acquisition_cost'] and aggregates['total_accumulated_depreciation']:
        total_book_value = aggregates['total_acquisition_cost'] - aggregates['total_accumulated_depreciation']
    
    summary = {
        'total_assets': aggregates['total_assets'] or 0,
        'total_acquisition_cost': str(aggregates['total_acquisition_cost'] or Decimal('0.00')),
        'total_accumulated_depreciation': str(aggregates['total_accumulated_depreciation'] or Decimal('0.00')),
        'total_book_value': str(total_book_value),
    }
    
    return Response({
        'assets': assets,
        'summary': summary,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assets_by_category_report(request):
    """
    Assets by Category Report
    IAS 16: Grouping of assets by category with totals
    
    Shows asset count and financial totals for each category
    """
    # Get all categories with assets
    categories_data = FixedAsset.objects.values(
        'asset_category__id',
        'asset_category__category_code',
        'asset_category__category_name'
    ).annotate(
        asset_count=Count('id'),
        total_acquisition_cost=Sum('acquisition_cost'),
        total_accumulated_depreciation=Sum('accumulated_depreciation')
    ).order_by('asset_category__category_code')
    
    # Build category list with book values
    categories = []
    total_assets = 0
    
    for cat in categories_data:
        book_value = Decimal('0.00')
        if cat['total_acquisition_cost'] and cat['total_accumulated_depreciation']:
            book_value = cat['total_acquisition_cost'] - cat['total_accumulated_depreciation']
        
        categories.append({
            'category_id': cat['asset_category__id'],
            'category_code': cat['asset_category__category_code'],
            'category_name': cat['asset_category__category_name'],
            'asset_count': cat['asset_count'],
            'total_acquisition_cost': str(cat['total_acquisition_cost'] or Decimal('0.00')),
            'total_accumulated_depreciation': str(cat['total_accumulated_depreciation'] or Decimal('0.00')),
            'total_book_value': str(book_value),
        })
        
        total_assets += cat['asset_count']
    
    summary = {
        'total_categories': len(categories),
        'total_assets': total_assets,
    }
    
    return Response({
        'categories': categories,
        'summary': summary,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assets_by_location_report(request):
    """
    Assets by Location Report
    IAS 16: Grouping of assets by physical location with totals
    
    Shows asset count and financial totals for each location
    """
    # Get all locations with assets
    locations_data = FixedAsset.objects.values('location').annotate(
        asset_count=Count('id'),
        total_acquisition_cost=Sum('acquisition_cost'),
        total_accumulated_depreciation=Sum('accumulated_depreciation')
    ).order_by('location')
    
    # Build location list with book values
    locations = []
    total_assets = 0
    
    for loc in locations_data:
        book_value = Decimal('0.00')
        if loc['total_acquisition_cost'] and loc['total_accumulated_depreciation']:
            book_value = loc['total_acquisition_cost'] - loc['total_accumulated_depreciation']
        
        locations.append({
            'location': loc['location'],
            'asset_count': loc['asset_count'],
            'total_acquisition_cost': str(loc['total_acquisition_cost'] or Decimal('0.00')),
            'total_accumulated_depreciation': str(loc['total_accumulated_depreciation'] or Decimal('0.00')),
            'total_book_value': str(book_value),
        })
        
        total_assets += loc['asset_count']
    
    summary = {
        'total_locations': len(locations),
        'total_assets': total_assets,
    }
    
    return Response({
        'locations': locations,
        'summary': summary,
    })


# ============================================================================
# FISCAL YEAR VIEWSET
# ============================================================================

from accounting.models import FiscalYear
from accounting.serializers import FiscalYearSerializer

class FiscalYearViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fiscal Year Management
    Provides CRUD operations for fiscal years
    """
    queryset = FiscalYear.objects.all()
    serializer_class = FiscalYearSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_closed']
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'name']
    ordering = ['-start_date']


# ============================================================================
# TAX CODE VIEWSET
# ============================================================================

from accounting.models import TaxCode
from accounting.serializers import TaxCodeSerializer

class TaxCodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tax Code Management
    Provides CRUD operations for tax codes
    """
    queryset = TaxCode.objects.all()
    serializer_class = TaxCodeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'description']
    ordering_fields = ['code', 'tax_percentage']
    ordering = ['code']


# ============================================================================
# TAX MASTER V2 VIEWSET
# ============================================================================

from accounting.models import TaxMasterV2
from accounting.serializers import TaxMasterV2Serializer

class TaxMasterV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tax Master V2 Management - IAS 12 Compliant
    Provides CRUD operations for tax masters
    """
    queryset = TaxMasterV2.objects.all()
    serializer_class = TaxMasterV2Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'tax_type']
    search_fields = ['tax_code', 'tax_name']
    ordering_fields = ['tax_code', 'tax_rate', 'created_at']
    ordering = ['tax_code']


# ============================================================================
# TAX GROUP V2 VIEWSET
# ============================================================================

from accounting.models import TaxGroupV2, TaxGroupItemV2
from accounting.serializers import TaxGroupV2Serializer, TaxGroupItemV2Serializer

class TaxGroupV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tax Group V2 Management
    Provides CRUD operations for tax groups with compound tax support
    """
    queryset = TaxGroupV2.objects.all()
    serializer_class = TaxGroupV2Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['group_name', 'description']
    ordering_fields = ['group_name', 'created_at']
    ordering = ['group_name']


# ============================================================================
# CURRENCY V2 VIEWSET
# ============================================================================

from accounting.models import CurrencyV2
from accounting.serializers import CurrencyV2Serializer

class CurrencyV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Currency V2 Management - IAS 21 Compliant
    Provides CRUD operations for currencies
    """
    queryset = CurrencyV2.objects.all()
    serializer_class = CurrencyV2Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_base_currency']
    search_fields = ['currency_code', 'currency_name']
    ordering_fields = ['currency_code', 'currency_name', 'created_at']
    ordering = ['currency_code']


# ============================================================================
# EXCHANGE RATE V2 VIEWSET
# ============================================================================

from accounting.models import ExchangeRateV2
from accounting.serializers import ExchangeRateV2Serializer

class ExchangeRateV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Exchange Rate V2 Management - IAS 21 Compliant
    Provides CRUD operations for exchange rates
    """
    queryset = ExchangeRateV2.objects.all()
    serializer_class = ExchangeRateV2Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['from_currency', 'to_currency', 'rate_date']
    search_fields = ['from_currency__currency_code', 'to_currency__currency_code']
    ordering_fields = ['rate_date', 'exchange_rate', 'created_at']
    ordering = ['-rate_date']


# ============================================================================
# COST CENTER V2 VIEWSET
# ============================================================================

from accounting.models import CostCenterV2
from accounting.serializers import CostCenterV2Serializer

class CostCenterV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Cost Center V2 Management
    Provides CRUD operations for cost centers
    """
    queryset = CostCenterV2.objects.all()
    serializer_class = CostCenterV2Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']


# ============================================================================
# DEPARTMENT V2 VIEWSET
# ============================================================================

from accounting.models import DepartmentV2
from accounting.serializers import DepartmentV2Serializer

class DepartmentV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Department V2 Management
    Provides CRUD operations for departments
    """
    queryset = DepartmentV2.objects.all()
    serializer_class = DepartmentV2Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']


# ============================================================================
# ENTITY V2 VIEWSET
# ============================================================================

from accounting.models import EntityV2
from accounting.serializers import EntityV2Serializer

class EntityV2ViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Entity V2 Management
    Provides CRUD operations for entities
    IAS 21: Foreign Currency Transactions
    IFRS 10: Consolidated Financial Statements
    """
    queryset = EntityV2.objects.all().order_by('code')
    serializer_class = EntityV2Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['code']
    
    def get_queryset(self):
        """Filter by is_active if provided"""
        queryset = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset



# ============================================================================
# BANK ACCOUNT VIEWSET
# ============================================================================

from accounting.models import BankAccount
from accounting.serializers import BankAccountSerializer

class BankAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bank Account Management
    Provides CRUD operations for bank accounts
    """
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'currency', 'bank_name']
    search_fields = ['account_number', 'account_name', 'bank_name', 'branch']
    ordering_fields = ['bank_name', 'account_number', 'created_at']
    ordering = ['bank_name', 'account_number']


# ============================================================================
# BANK STATEMENT VIEWSET
# ============================================================================

from accounting.models import BankStatement, BankStatementLine
from accounting.serializers import BankStatementSerializer

class BankStatementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bank Statement Management
    Provides CRUD operations for bank statements
    """
    queryset = BankStatement.objects.all()
    serializer_class = BankStatementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['bank_account', 'is_reconciled', 'statement_date']
    search_fields = ['bank_account__account_name', 'bank_account__bank_name']
    ordering_fields = ['statement_date', 'created_at']
    ordering = ['-statement_date']


# ============================================================================
# FAIR VALUE MEASUREMENT VIEWSET (IAS 39/IFRS 9)
# ============================================================================

from accounting.models import FairValueMeasurement
from accounting.serializers import FairValueMeasurementSerializer

class FairValueMeasurementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fair Value Measurement Management
    Provides CRUD operations for fair value measurements (IFRS 13)
    IFRS 13: Fair Value Measurement - Three-level hierarchy
    """
    queryset = FairValueMeasurement.objects.all().select_related('account', 'created_by').order_by('-measurement_date')
    serializer_class = FairValueMeasurementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['account__code', 'account__name', 'external_valuer', 'valuation_technique']
    ordering_fields = ['measurement_date', 'fair_value', 'created_at']
    ordering = ['-measurement_date']
    
    def get_queryset(self):
        """Filter by fair_value_level, measurement_date if provided"""
        queryset = super().get_queryset()
        fair_value_level = self.request.query_params.get('fair_value_level')
        measurement_date = self.request.query_params.get('measurement_date')
        account_id = self.request.query_params.get('account')
        
        if fair_value_level:
            queryset = queryset.filter(fair_value_level=fair_value_level)
        if measurement_date:
            queryset = queryset.filter(measurement_date=measurement_date)
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        return queryset



# ============================================================================
# FX REVALUATION LOG VIEWSET (IAS 21)
# ============================================================================

from accounting.models import FXRevaluationLog
from accounting.serializers import FXRevaluationLogSerializer

class FXRevaluationLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FX Revaluation Log Management
    Provides CRUD operations for FX revaluation logs (IAS 21)
    """
    queryset = FXRevaluationLog.objects.all()
    serializer_class = FXRevaluationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['entity', 'status', 'revaluation_date', 'functional_currency']
    search_fields = ['revaluation_id', 'entity__entity_code', 'entity__entity_name']
    ordering_fields = ['revaluation_date', 'created_at', 'net_fx_gain_loss']
    ordering = ['-revaluation_date', '-created_at']


# ============================================================================
# REFERENCE DEFINITION VIEWSET
# ============================================================================

from accounting.models import ReferenceDefinition
from accounting.serializers import ReferenceDefinitionSerializer

class ReferenceDefinitionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Reference Definition Management
    Provides CRUD operations for user-defined reference fields
    Used for dynamic form field configuration in Invoices and Vouchers
    
    Endpoints:
        GET    /api/accounting/reference-definitions/              - List definitions
        POST   /api/accounting/reference-definitions/              - Create definition
        GET    /api/accounting/reference-definitions/{id}/         - Get definition details
        PUT    /api/accounting/reference-definitions/{id}/         - Update definition
        DELETE /api/accounting/reference-definitions/{id}/         - Delete definition
    """
    queryset = ReferenceDefinition.objects.all().order_by('model_name', 'field_label')
    serializer_class = ReferenceDefinitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['model_name', 'data_type', 'is_required', 'is_active']
    search_fields = ['field_key', 'field_label']
    ordering_fields = ['model_name', 'field_label', 'created_at']
    ordering = ['model_name', 'field_label']
    
    def get_queryset(self):
        """Filter by model_name if provided"""
        queryset = super().get_queryset()
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name, is_active=True)
        return queryset


# ============================================================================
# MODULE 1.3: APPROVAL WORKFLOW SYSTEM - API VIEWSETS
# ============================================================================

class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ApprovalWorkflow
    Module 1.3.3: Approval API & UI
    
    Endpoints:
    - GET /api/accounting/approval-workflows/ - List all workflows
    - POST /api/accounting/approval-workflows/ - Create new workflow (admin only)
    - GET /api/accounting/approval-workflows/{id}/ - Retrieve workflow
    - PUT /api/accounting/approval-workflows/{id}/ - Update workflow (admin only)
    - DELETE /api/accounting/approval-workflows/{id}/ - Delete workflow (admin only)
    
    Filters:
    - document_type: Filter by document type
    - is_active: Filter by active status
    """
    
    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'is_active']
    search_fields = ['workflow_name', 'description']
    ordering_fields = ['created_at', 'workflow_name']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Admin users can create/update/delete workflows
        Regular users can only view
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [IsAuthenticated()]


class ApprovalLevelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ApprovalLevel
    Module 1.3.3: Approval API & UI
    
    Endpoints:
    - GET /api/accounting/approval-levels/ - List all levels
    - POST /api/accounting/approval-levels/ - Create new level (admin only)
    - GET /api/accounting/approval-levels/{id}/ - Retrieve level
    - PUT /api/accounting/approval-levels/{id}/ - Update level (admin only)
    - DELETE /api/accounting/approval-levels/{id}/ - Delete level (admin only)
    
    Filters:
    - workflow: Filter by workflow ID
    - approver: Filter by approver user ID
    - level_number: Filter by level number
    """
    
    queryset = ApprovalLevel.objects.all()
    serializer_class = ApprovalLevelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workflow', 'approver', 'level_number', 'is_mandatory']
    ordering_fields = ['level_number', 'created_at']
    ordering = ['level_number']
    
    def get_permissions(self):
        """
        Admin users can create/update/delete levels
        Regular users can only view
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [IsAuthenticated()]


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ApprovalRequest
    Module 1.3.3: Approval API & UI
    
    Endpoints:
    - GET /api/accounting/approval-requests/ - List all requests
    - POST /api/accounting/approval-requests/ - Create new request
    - GET /api/accounting/approval-requests/{id}/ - Retrieve request
    - PUT /api/accounting/approval-requests/{id}/ - Update request (limited)
    - DELETE /api/accounting/approval-requests/{id}/ - Delete request (limited)
    
    Custom Actions:
    - POST /api/accounting/approval-requests/{id}/approve/ - Approve request
    - POST /api/accounting/approval-requests/{id}/reject/ - Reject request
    - POST /api/accounting/approval-requests/{id}/delegate/ - Delegate request
    - GET /api/accounting/approval-requests/pending_approvals/ - Get pending approvals for current user
    
    Filters:
    - status: Filter by status (pending, approved, rejected)
    - document_type: Filter by document type
    - current_approver: Filter by current approver user ID
    - requester: Filter by requester user ID
    """
    
    queryset = ApprovalRequest.objects.all()
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'document_type', 'current_approver', 'requester']
    search_fields = ['document_type']
    ordering_fields = ['request_date', 'completion_date', 'amount']
    ordering = ['-request_date']
    
    def get_queryset(self):
        """
        Optionally filter by current user's pending approvals
        """
        queryset = super().get_queryset()
        
        # Select related for performance
        queryset = queryset.select_related(
            'workflow',
            'requester',
            'current_approver'
        ).prefetch_related('actions')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve an approval request
        
        POST /api/accounting/approval-requests/{id}/approve/
        
        Body:
        {
            "comments": "Approved for payment",
            "ip_address": "192.168.1.1"
        }
        """
        approval_request = self.get_object()
        serializer = ApprovalRequestActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        from accounting.services import ApprovalService
        service = ApprovalService()
        
        try:
            result = service.approve(
                approval_request_id=approval_request.id,
                approver=request.user,
                comments=serializer.validated_data.get('comments', ''),
                ip_address=serializer.validated_data.get('ip_address', request.META.get('REMOTE_ADDR', '0.0.0.0'))
            )
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject an approval request
        
        POST /api/accounting/approval-requests/{id}/reject/
        
        Body:
        {
            "comments": "Insufficient documentation",
            "ip_address": "192.168.1.1"
        }
        """
        approval_request = self.get_object()
        serializer = ApprovalRequestActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        from accounting.services import ApprovalService
        service = ApprovalService()
        
        try:
            result = service.reject(
                approval_request_id=approval_request.id,
                approver=request.user,
                comments=serializer.validated_data.get('comments', ''),
                ip_address=serializer.validated_data.get('ip_address', request.META.get('REMOTE_ADDR', '0.0.0.0'))
            )
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def delegate(self, request, pk=None):
        """
        Delegate an approval request to another user
        
        POST /api/accounting/approval-requests/{id}/delegate/
        
        Body:
        {
            "delegate_to": 5,  // User ID
            "comments": "Delegating while on leave",
            "ip_address": "192.168.1.1"
        }
        """
        approval_request = self.get_object()
        serializer = ApprovalRequestActionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        delegate_to_id = serializer.validated_data.get('delegate_to')
        if not delegate_to_id:
            return Response(
                {'error': 'delegate_to field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            delegate_to = User.objects.get(id=delegate_to_id)
        except User.DoesNotExist:
            return Response(
                {'error': f'User with ID {delegate_to_id} does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from accounting.services import ApprovalService
        service = ApprovalService()
        
        try:
            result = service.delegate(
                approval_request_id=approval_request.id,
                approver=request.user,
                delegate_to=delegate_to,
                comments=serializer.validated_data.get('comments', ''),
                ip_address=serializer.validated_data.get('ip_address', request.META.get('REMOTE_ADDR', '0.0.0.0'))
            )
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """
        Get all pending approvals for the current user
        
        GET /api/accounting/approval-requests/pending_approvals/
        """
        from accounting.services import ApprovalService
        service = ApprovalService()
        pending = service.get_pending_approvals(request.user)
        
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApprovalActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ApprovalAction (Read-only)
    Module 1.3.3: Approval API & UI
    
    Endpoints:
    - GET /api/accounting/approval-actions/ - List all actions
    - GET /api/accounting/approval-actions/{id}/ - Retrieve action
    
    Filters:
    - approval_request: Filter by approval request ID
    - approver: Filter by approver user ID
    - action: Filter by action type (approved, rejected, delegated)
    
    Note: This is read-only to maintain audit trail integrity (IFRS IAS 1)
    """
    
    queryset = ApprovalAction.objects.all()
    serializer_class = ApprovalActionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['approval_request', 'approver', 'action', 'level_number']
    ordering_fields = ['action_date']
    ordering = ['-action_date']
    
    def get_queryset(self):
        """Select related for performance"""
        return super().get_queryset().select_related(
            'approval_request',
            'approver'
        )


# ============================================
# APPROVAL REPORT VIEW SET
# ============================================

class ApprovalReportViewSet(viewsets.ViewSet):
    """
    ViewSet for Approval Workflow Reports.
    Task 1.3.5: Approval Reports
    
    Provides specialized endpoints for reporting.
    """
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'], url_path='pending')
    def pending_summary(self, request):
        """
        Get summary of pending approvals.
        URL: /api/accounting/reports/approvals/pending/
        """
        filters = {}
        if 'workflow' in request.query_params:
            filters['workflow'] = request.query_params['workflow']
        if 'document_type' in request.query_params:
            filters['document_type'] = request.query_params['document_type']
            
        data = ApprovalReportService.get_pending_approvals_report(filters)
        return Response(data)

    @action(detail=False, methods=['get'], url_path='history')
    def history_log(self, request):
        """
        Get detailed approval history log.
        URL: /api/accounting/reports/approvals/history/
        """
        filters = {}
        if 'actor' in request.query_params:
            filters['actor'] = request.query_params['actor']
        if 'start_date' in request.query_params:
            filters['start_date'] = request.query_params['start_date']
        if 'end_date' in request.query_params:
            filters['end_date'] = request.query_params['end_date']
            
        data = ApprovalReportService.get_approval_history_report(filters)
        return Response(data)

    @action(detail=False, methods=['get'], url_path='turnaround')
    def turnaround_stats(self, request):
        """
        Get turnaround time statistics.
        URL: /api/accounting/reports/approvals/turnaround/
        """
        data = ApprovalReportService.get_turnaround_time_report()
        return Response(data)


# ============================================
# GMAIL OAUTH VIEW SET
# ============================================

class GoogleAuthViewSet(viewsets.ViewSet):
    """
    ViewSet for Gmail OAuth Flow.
    Task 1.3.6: Gmail OAuth Integration
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='login')
    def login(self, request):
        """
        Initiate OAuth flow.
        URL: /api/accounting/auth/google/login/
        """
        # Determine redirect URI based on environment (Host header)
        host = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        # For localhost testing, ensure http
        if 'localhost' in host or '127.0.0.1' in host:
            protocol = 'http'
            
        redirect_uri = f"{protocol}://{host}/api/accounting/auth/google/callback/"
        
        # User defined redirect URI from request if separate frontend?
        # For now, use backend callback
        
        try:
            auth_url, state = GmailAuthService.get_authorization_url(redirect_uri)
            # Store state in session if needed for CSRF
            return Response({'authorization_url': auth_url})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='callback')
    def callback(self, request):
        """
        Handle OAuth callback.
        URL: /api/accounting/auth/google/callback/
        """
        code = request.query_params.get('code')
        if not code:
            return Response({'error': 'Missing code'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Reconstruct redirect URI
        host = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        if 'localhost' in host or '127.0.0.1' in host:
            protocol = 'http'
        redirect_uri = f"{protocol}://{host}/api/accounting/auth/google/callback/"

        try:
            token = GmailAuthService.exchange_code(code, redirect_uri, request.user)
            return Response({
                'message': 'Gmail account linked successfully',
                'email': token.email
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ============================================
# RECURRING TRANSACTION VIEWS (Task 1.4)
# ============================================

class RecurringTransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing recurring transactions.
    Supports filtering and preview generation.
    """
    queryset = RecurringTransaction.objects.all()
    serializer_class = RecurringTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'frequency', 'is_active', 'start_date', 'next_run_date']
    search_fields = ['name']
    ordering_fields = ['next_run_date', 'name']

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview the next transaction generation"""
        rt = self.get_object()
        
        # Simulate generation logic
        preview_data = {
           'template': rt.template_data,
           'next_run_date': rt.next_run_date,
           'preview_voucher': {
               'voucher_date': rt.next_run_date,
               'narration': f"{rt.name} - {rt.next_run_date} (PREVIEW)",
           }
        }
        return Response(preview_data)

    @action(detail=False, methods=['post'])
    def process_due(self, request):
        """Manually trigger processing of due transactions (Admin only)"""
        if not request.user.is_staff:
             return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
             
        try:
            generated = RecurringTransactionService.generate_due_transactions()
            return Response({'message': f"Processed {len(generated)} transactions", 'generated': generated})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# BUDGET REPORTS (Task 1.5.3)
# ============================================

class BudgetReportViewSet(viewsets.ViewSet):
    """
    Budget reporting endpoints.
    Task 1.5.3
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='budget-vs-actual')
    def budget_vs_actual(self, request):
        """
        Budget vs Actual Report
        Parameters: budget_id
        """
        budget_id = request.query_params.get('budget_id')
        if not budget_id:
            return Response({'error': 'budget_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            report = BudgetService.calculate_variance(budget_id)
            return Response(report)
        except Budget.DoesNotExist:
            return Response({'error': 'Budget not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='variance-analysis')
    def variance_analysis(self, request):
        """
        Variance Analysis Report (Alias for budget-vs-actual but could have different filters)
        """
        return self.budget_vs_actual(request)

    @action(detail=False, methods=['get'], url_path='utilization')
    def utilization(self, request):
        """
        Budget Utilization Report
        Parameters: budget_id
        """
        budget_id = request.query_params.get('budget_id')
        if not budget_id:
            return Response({'error': 'budget_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            report = BudgetService.get_budget_utilization(budget_id)
            return Response(report)
        except Budget.DoesNotExist:
            return Response({'error': 'Budget not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================
# COST CENTER REPORTS (Task 1.6.3)
# ============================================

class CostCenterReportViewSet(viewsets.ViewSet):
    """
    Cost Center reporting endpoints.
    Task 1.6.3
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='profitability')
    def profitability(self, request):
        """
        Profit Center Performance Report (P&L)
        Params: cost_center_id, start_date, end_date
        """
        cost_center_id = request.query_params.get('cost_center_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not all([cost_center_id, start_date, end_date]):
            return Response({'error': 'Missing params'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            report = CostCenterService.calculate_profitability(cost_center_id, start_date, end_date)
            if 'error' in report:
                return Response(report, status=status.HTTP_400_BAD_REQUEST)
            return Response(report)
        except CostCenterV2.DoesNotExist:
             return Response({'error': 'Cost Center not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='allocation')
    def allocation(self, request):
        """
        Cost Allocation Report (Expenses for Cost Center)
        Params: cost_center_id, start_date, end_date
        """
        cost_center_id = request.query_params.get('cost_center_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not all([cost_center_id, start_date, end_date]):
            return Response({'error': 'Missing params'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            report = CostCenterService.get_cost_allocation_report(cost_center_id, start_date, end_date)
            return Response(report)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
