from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth, TruncDate
from accounting.models import ApprovalRequest, ApprovalAction, ApprovalWorkflow
from django.utils import timezone
from decimal import Decimal

class ApprovalReportService:
    """
    Service for generating approval workflow reports.
    Task 1.3.5: Approval Reports
    """

    @staticmethod
    def get_pending_approvals_report(filters=None):
        """
        Generate report of pending approvals.
        Returns summary metrics and detailed list.
        """
        queryset = ApprovalRequest.objects.filter(status='pending')
        
        if filters:
            if 'workflow' in filters:
                queryset = queryset.filter(workflow_id=filters['workflow'])
            if 'document_type' in filters:
                queryset = queryset.filter(document_type=filters['document_type'])

        # Aggregation
        summary = queryset.aggregate(
            total_count=Count('id'),
            total_pending_amount=Sum('amount')
        )
        
        details = queryset.select_related('workflow', 'requester', 'current_approver').values(
            'id', 'document_type', 'document_id', 'amount', 
            'requester__username', 'current_approver__username', 'request_date',
            'workflow__workflow_name'
        )

        return {
            'total_count': summary['total_count'] or 0,
            'total_pending_amount': summary['total_pending_amount'] or Decimal('0.00'),
            'details': [
                {
                    'id': d['id'],
                    'document_number': str(d['document_id']), # Assuming ID for now, ideally fetch real number
                    'amount': d['amount'],
                    'requester': d['requester__username'],
                    'current_approver': d['current_approver__username'],
                    'request_date': d['request_date'],
                    'workflow': d['workflow__workflow_name']
                } for d in details
            ]
        }

    @staticmethod
    def get_approval_history_report(filters=None):
        """
        Generate detailed log of approval actions.
        """
        queryset = ApprovalAction.objects.select_related(
            'approval_request', 'approver'
        ).order_by('-action_date')
        
        if filters:
            if 'actor' in filters:
                queryset = queryset.filter(approver_id=filters['actor'])
            if 'start_date' in filters:
                queryset = queryset.filter(action_date__gte=filters['start_date'])
            if 'end_date' in filters:
                queryset = queryset.filter(action_date__lte=filters['end_date'])

        results = []
        for action in queryset:
            results.append({
                'action_id': action.id,
                'action_type': action.action,
                'actor_name': action.approver.username,
                'action_date': action.action_date,
                'document_type': action.approval_request.document_type,
                'document_id': action.approval_request.document_id,
                'comments': action.comments,
                'ip_address': action.ip_address
            })
            
        return {'results': results}

    @staticmethod
    def get_turnaround_time_report(filters=None):
        """
        Calculate average turnaround time for workflows.
        Stats: Average duration between request_date and completion_date.
        """
        completed_requests = ApprovalRequest.objects.filter(
            status__in=['approved', 'rejected'],
            completion_date__isnull=False
        ).annotate(
            duration=ExpressionWrapper(
                F('completion_date') - F('request_date'),
                output_field=DurationField()
            )
        )

        # Group by workflow
        stats = completed_requests.values('workflow__workflow_name').annotate(
            avg_duration=Avg('duration'),
            completed_count=Count('id')
        )

        report_data = []
        for stat in stats:
            avg_hours = stat['avg_duration'].total_seconds() / 3600 if stat['avg_duration'] else 0
            report_data.append({
                'workflow_name': stat['workflow__workflow_name'],
                'avg_hours': round(avg_hours, 2),
                'completed_count': stat['completed_count']
            })
            
        return report_data
