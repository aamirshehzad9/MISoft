from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.utils import timezone
from accounting.models import (
    ApprovalWorkflow, ApprovalLevel, ApprovalRequest, ApprovalAction,
    VoucherV2, CurrencyV2
)

User = get_user_model()

class ApprovalReportsTestCase(TestCase):
    """Test Suite for Approval Reports (Task 1.3.5)"""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
        self.user = User.objects.create_user('user', 'user@example.com', 'userpass')
        self.approver = User.objects.create_user('approver', 'approver@example.com', 'approverpass')
        
        self.client.force_authenticate(user=self.admin)
        
        # Setup Workflow
        self.workflow = ApprovalWorkflow.objects.create(
            workflow_name='Test Workflow',
            document_type='voucher',
            is_active=True,
            created_by=self.admin
        )
        
        self.level = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('1000000.00')
        )
        
        self.currency = CurrencyV2.objects.create(currency_code='USD', currency_name='US Dollar', symbol='$')
        
        # Create Data for Reports
        # 1. Pending Request
        self.v1 = VoucherV2.objects.create(
            voucher_type='CPV', voucher_number='V-001', voucher_date=date.today(),
            currency=self.currency, total_amount=Decimal('100.00'), status='draft',
            created_by=self.user, approval_status='pending'
        )
        self.req_pending = ApprovalRequest.objects.create(
            workflow=self.workflow, document_type='voucher', document_id=self.v1.id,
            amount=self.v1.total_amount, requester=self.user, status='pending',
            current_level=1, current_approver=self.approver
        )
        self.v1.approval_request = self.req_pending
        self.v1.save()
        
        # 2. Approved Request (Completed)
        self.v2 = VoucherV2.objects.create(
            voucher_type='CPV', voucher_number='V-002', voucher_date=date.today(),
            currency=self.currency, total_amount=Decimal('200.00'), status='draft',
            created_by=self.user, approval_status='approved'
        )
        
        created_time = timezone.now() - timedelta(hours=2)
        completed_time = timezone.now()
        
        self.req_approved = ApprovalRequest.objects.create(
            workflow=self.workflow, document_type='voucher', document_id=self.v2.id,
            amount=self.v2.total_amount, requester=self.user, status='approved',
            current_level=1, request_date=created_time, completion_date=completed_time
        )
        # Hack to set request_date (auto_now_add usually prevents it, but we can update after create or use mock)
        ApprovalRequest.objects.filter(id=self.req_approved.id).update(request_date=created_time)
        
        self.v2.approval_request = self.req_approved
        self.v2.save()
        
        # Log Action
        ApprovalAction.objects.create(
            approval_request=self.req_approved, action='approved', approver=self.approver,
            level_number=1, action_date=completed_time, comments='Approved',
            ip_address='127.0.0.1'
        )

    def test_pending_approvals_report(self):
        """Test retrieving pending approvals report"""
        response = self.client.get('/api/accounting/reports/approvals/pending/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain summary
        self.assertIn('total_pending_amount', response.data)
        self.assertIn('total_count', response.data)
        self.assertEqual(response.data['total_count'], 1)
        self.assertEqual(Decimal(response.data['total_pending_amount']), Decimal('100.00'))
        
        # Should contain details
        self.assertIn('details', response.data)
        self.assertEqual(len(response.data['details']), 1)
        self.assertEqual(response.data['details'][0]['document_number'], str(self.v1.id))

    def test_approval_history_report(self):
        """Test retrieving approval history log"""
        response = self.client.get('/api/accounting/reports/approvals/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['action_type'], 'approved')
        self.assertEqual(response.data['results'][0]['actor_name'], 'approver')

    def test_turnaround_time_report(self):
        """Test turnaround time calculation"""
        response = self.client.get('/api/accounting/reports/approvals/turnaround/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Workflow level stats
        workflow_stats = [w for w in response.data if w['workflow_name'] == 'Test Workflow'][0]
        self.assertAlmostEqual(workflow_stats['avg_hours'], 2.0, delta=0.1)
        self.assertEqual(workflow_stats['completed_count'], 1)

    def test_permissions(self):
        """Test that only admins/authorized users can access reports"""
        self.client.force_authenticate(user=self.user) # Ordinary user
        response = self.client.get('/api/accounting/reports/approvals/pending/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
