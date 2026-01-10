"""
API Tests for Approval Workflow System
Module 1.3.3: Create Approval API & UI

Test Coverage:
- ApprovalWorkflow API (CRUD, filtering)
- ApprovalLevel API (CRUD, nested under workflow)
- ApprovalRequest API (CRUD, filtering, custom actions)
- ApprovalAction API (Read-only, audit trail)
- Custom actions: approve, reject, delegate
- Filtering by status, document type, approver
- Permissions and authentication
- IFRS compliance (IAS 1 - Internal Controls)

TDD Cycle: RED phase - Tests written first, expected to FAIL
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import datetime
from accounting.models import (
    ApprovalWorkflow,
    ApprovalLevel,
    ApprovalRequest,
    ApprovalAction,
    VoucherV2,
    AccountV2,
    VoucherEntryV2,
    CurrencyV2,
)

User = get_user_model()


def get_response_data(response):
    """
    Helper function to extract data from DRF response.
    Handles both paginated (dict with 'results' key) and non-paginated (list) responses.
    """
    if isinstance(response.data, dict) and 'results' in response.data:
        return response.data['results']
    return response.data



class ApprovalWorkflowAPITestCase(TestCase):
    """Test ApprovalWorkflow API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)

    def test_create_approval_workflow(self):
        """Test creating an approval workflow via API"""
        data = {
            'workflow_name': 'Purchase Order Approval',
            'description': 'Approval workflow for purchase orders',
            'document_type': 'purchase_order',
            'is_active': True
        }
        
        response = self.client.post('/api/accounting/approval-workflows/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['workflow_name'], 'Purchase Order Approval')
        self.assertEqual(response.data['document_type'], 'purchase_order')
        self.assertTrue(response.data['is_active'])

    def test_list_approval_workflows(self):
        """Test listing approval workflows"""
        # Create workflows
        ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            is_active=True,
            created_by=self.admin_user
        )
        
        ApprovalWorkflow.objects.create(
            workflow_name='PO Approval',
            document_type='purchase_order',
            is_active=True,
            created_by=self.admin_user
        )
        
        response = self.client.get('/api/accounting/approval-workflows/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 2)
        # Verify both workflows exist
        workflow_names = {w['workflow_name'] for w in data}
        self.assertIn('Voucher Approval', workflow_names)
        self.assertIn('PO Approval', workflow_names)

    def test_retrieve_approval_workflow(self):
        """Test retrieving a single approval workflow"""
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            is_active=True,
            created_by=self.admin_user
        )
        
        response = self.client.get(f'/api/accounting/approval-workflows/{workflow.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['workflow_name'], 'Voucher Approval')

    def test_update_approval_workflow(self):
        """Test updating an approval workflow"""
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            is_active=True,
            created_by=self.admin_user
        )
        
        data = {
            'workflow_name': 'Updated Voucher Approval',
            'description': 'Updated description',
            'document_type': 'voucher',
            'is_active': False
        }
        
        response = self.client.put(f'/api/accounting/approval-workflows/{workflow.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['workflow_name'], 'Updated Voucher Approval')
        self.assertFalse(response.data['is_active'])

    def test_delete_approval_workflow(self):
        """Test deleting an approval workflow"""
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            is_active=True,
            created_by=self.admin_user
        )
        
        response = self.client.delete(f'/api/accounting/approval-workflows/{workflow.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ApprovalWorkflow.objects.filter(id=workflow.id).exists())

    def test_filter_workflows_by_document_type(self):
        """Test filtering workflows by document type"""
        ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            is_active=True,
            created_by=self.admin_user
        )
        
        ApprovalWorkflow.objects.create(
            workflow_name='PO Approval',
            document_type='purchase_order',
            is_active=True,
            created_by=self.admin_user
        )
        
        response = self.client.get('/api/accounting/approval-workflows/?document_type=voucher')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)
        # Verify all returned workflows are voucher type
        for workflow in data:
            self.assertEqual(workflow['document_type'], 'voucher')

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access API"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/accounting/approval-workflows/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ApprovalLevelAPITestCase(TestCase):
    """Test ApprovalLevel API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='approver123'
        )
        
        self.workflow = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            is_active=True,
            created_by=self.admin_user
        )
        
        self.client.force_authenticate(user=self.admin_user)

    def test_create_approval_level(self):
        """Test creating an approval level"""
        data = {
            'workflow': self.workflow.id,
            'level_number': 1,
            'approver': self.approver.id,
            'min_amount': '0.00',
            'max_amount': '10000.00',
            'is_mandatory': True
        }
        
        response = self.client.post('/api/accounting/approval-levels/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['level_number'], 1)
        self.assertEqual(response.data['approver'], self.approver.id)

    def test_list_approval_levels(self):
        """Test listing approval levels"""
        ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        response = self.client.get('/api/accounting/approval-levels/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)

    def test_filter_levels_by_workflow(self):
        """Test filtering levels by workflow"""
        # Create another workflow
        workflow2 = ApprovalWorkflow.objects.create(
            workflow_name='PO Approval',
            document_type='purchase_order',
            is_active=True,
            created_by=self.admin_user
        )
        
        ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        ApprovalLevel.objects.create(
            workflow=workflow2,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('5000.00')
        )
        
        response = self.client.get(f'/api/accounting/approval-levels/?workflow={self.workflow.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)
        # Verify all returned levels belong to our workflow
        for level in data:
            self.assertEqual(level['workflow'], self.workflow.id)


class ApprovalRequestAPITestCase(TestCase):
    """Test ApprovalRequest API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        
        self.requester = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='requester123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='approver123'
        )
        
        # Create currency
        self.currency = CurrencyV2.objects.create(
            currency_code='PKR',
            currency_name='Pakistani Rupee',
            symbol='Rs',
            is_active=True
        )
        
        # Create accounts
        self.cash_account = AccountV2.objects.create(
            code='1010',
            name='Cash',
            account_type='asset',
            account_group='current_asset'
        )
        
        self.expense_account = AccountV2.objects.create(
            code='5010',
            name='Office Expense',
            account_type='expense',
            account_group='operating_expense'
        )
        
        # Create workflow
        self.workflow = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            is_active=True,
            created_by=self.admin_user
        )
        
        self.level = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        # Create voucher
        self.voucher = VoucherV2.objects.create(
            voucher_type='CPV',
            voucher_number='CPV-TEST-API-001',
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Test payment',
            total_amount=Decimal('5000.00'),
            created_by=self.requester
        )
        
        VoucherEntryV2.objects.create(
            voucher=self.voucher,
            account=self.expense_account,
            debit_amount=Decimal('5000.00'),
            credit_amount=Decimal('0.00')
        )
        
        VoucherEntryV2.objects.create(
            voucher=self.voucher,
            account=self.cash_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('5000.00')
        )
        
        self.client.force_authenticate(user=self.requester)

    def test_create_approval_request(self):
        """Test creating an approval request via API"""
        data = {
            'document_type': 'voucher',
            'document_id': self.voucher.id,
            'amount': '5000.00'
        }
        
        response = self.client.post('/api/accounting/approval-requests/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['document_type'], 'voucher')
        self.assertEqual(response.data['status'], 'pending')

    def test_list_approval_requests(self):
        """Test listing approval requests"""
        ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.requester,
            current_approver=self.approver
        )
        
        response = self.client.get('/api/accounting/approval-requests/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)

    def test_filter_requests_by_status(self):
        """Test filtering requests by status"""
        ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.requester,
            current_approver=self.approver
        )
        
        ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=999,
            amount=Decimal('3000.00'),
            current_level=1,
            status='approved',
            requester=self.requester,
            current_approver=self.approver
        )
        
        response = self.client.get('/api/accounting/approval-requests/?status=pending')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)
        # Verify all returned requests are pending
        for req in data:
            self.assertEqual(req['status'], 'pending')

    def test_filter_requests_by_approver(self):
        """Test filtering requests by current approver"""
        ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.requester,
            current_approver=self.approver
        )
        
        response = self.client.get(f'/api/accounting/approval-requests/?current_approver={self.approver.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)
        # Verify all returned requests have our approver
        for req in data:
            self.assertEqual(req['current_approver'], self.approver.id)

    def test_approve_action(self):
        """Test approve custom action"""
        request = ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.requester,
            current_approver=self.approver
        )
        
        # Authenticate as approver
        self.client.force_authenticate(user=self.approver)
        
        data = {
            'comments': 'Approved for payment',
            'ip_address': '192.168.1.1'
        }
        
        response = self.client.post(f'/api/accounting/approval-requests/{request.id}/approve/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['approved'])

    def test_reject_action(self):
        """Test reject custom action"""
        request = ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.requester,
            current_approver=self.approver
        )
        
        # Authenticate as approver
        self.client.force_authenticate(user=self.approver)
        
        data = {
            'comments': 'Insufficient documentation',
            'ip_address': '192.168.1.1'
        }
        
        response = self.client.post(f'/api/accounting/approval-requests/{request.id}/reject/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['rejected'])

    def test_delegate_action(self):
        """Test delegate custom action"""
        delegate = User.objects.create_user(
            username='delegate',
            email='delegate@example.com',
            password='delegate123'
        )
        
        request = ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.requester,
            current_approver=self.approver
        )
        
        # Authenticate as approver
        self.client.force_authenticate(user=self.approver)
        
        data = {
            'delegate_to': delegate.id,
            'comments': 'Delegating while on leave',
            'ip_address': '192.168.1.1'
        }
        
        response = self.client.post(f'/api/accounting/approval-requests/{request.id}/delegate/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['delegated'])

    def test_pending_approvals_action(self):
        """Test pending_approvals custom action"""
        ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.requester,
            current_approver=self.approver
        )
        
        # Authenticate as approver
        self.client.force_authenticate(user=self.approver)
        
        response = self.client.get('/api/accounting/approval-requests/pending_approvals/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)


class ApprovalActionAPITestCase(TestCase):
    """Test ApprovalAction API endpoints (read-only)"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        
        self.requester = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='requester123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='approver123'
        )
        
        # Create currency
        self.currency = CurrencyV2.objects.create(
            currency_code='PKR',
            currency_name='Pakistani Rupee',
            symbol='Rs',
            is_active=True
        )
        
        # Create workflow
        self.workflow = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            is_active=True,
            created_by=self.admin_user
        )
        
        self.level = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        self.approval_request = ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=123,
            amount=Decimal('5000.00'),
            current_level=1,
            status='approved',
            requester=self.requester,
            current_approver=self.approver
        )
        
        self.approval_action = ApprovalAction.objects.create(
            approval_request=self.approval_request,
            level_number=1,
            approver=self.approver,
            action='approved',
            comments='Approved for payment',
            ip_address='192.168.1.1'
        )
        
        self.client.force_authenticate(user=self.admin_user)

    def test_list_approval_actions(self):
        """Test listing approval actions"""
        response = self.client.get('/api/accounting/approval-actions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)

    def test_retrieve_approval_action(self):
        """Test retrieving a single approval action"""
        response = self.client.get(f'/api/accounting/approval-actions/{self.approval_action.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'approved')

    def test_cannot_create_approval_action(self):
        """Test that approval actions cannot be created directly via API"""
        data = {
            'approval_request': self.approval_request.id,
            'level_number': 1,
            'approver': self.approver.id,
            'action': 'approved',
            'comments': 'Test',
            'ip_address': '192.168.1.1'
        }
        
        response = self.client.post('/api/accounting/approval-actions/', data, format='json')
        
        # Should return 405 Method Not Allowed or 403 Forbidden
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])

    def test_cannot_delete_approval_action(self):
        """Test that approval actions cannot be deleted (audit trail)"""
        response = self.client.delete(f'/api/accounting/approval-actions/{self.approval_action.id}/')
        
        # Should return 405 Method Not Allowed or 403 Forbidden
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])

    def test_filter_actions_by_request(self):
        """Test filtering actions by approval request"""
        response = self.client.get(f'/api/accounting/approval-actions/?approval_request={self.approval_request.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = get_response_data(response)
        self.assertGreaterEqual(len(data), 1)


class ApprovalAPIPermissionsTestCase(TestCase):
    """Test API permissions and IFRS compliance"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )

    def test_regular_user_cannot_create_workflow(self):
        """Test that regular users cannot create workflows"""
        self.client.force_authenticate(user=self.regular_user)
        
        data = {
            'workflow_name': 'Test Workflow',
            'document_type': 'voucher',
            'is_active': True
        }
        
        response = self.client.post('/api/accounting/approval-workflows/', data, format='json')
        
        # Should return 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_workflow(self):
        """Test that admin users can create workflows"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'workflow_name': 'Test Workflow',
            'document_type': 'voucher',
            'is_active': True
        }
        
        response = self.client.post('/api/accounting/approval-workflows/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

