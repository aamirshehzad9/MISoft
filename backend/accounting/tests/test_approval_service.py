"""
Unit Tests for Approval Service
Module 1.3.2: Create ApprovalService

Test Coverage:
- Approval workflow initiation
- Approval action (approve)
- Rejection action (reject)
- Delegation action (delegate)
- Get pending approvals
- Email notification integration
- Multi-level approval routing
- Amount-based workflow selection
- IFRS compliance (IAS 1 - Internal Controls)

TDD Cycle: RED phase - Tests written first, expected to FAIL
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
from accounting.services.approval_service import ApprovalService

User = get_user_model()


class ApprovalServiceInitiationTestCase(TestCase):
    """Test approval workflow initiation"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpass123'
        )
        
        self.approver1 = User.objects.create_user(
            username='approver1',
            email='approver1@example.com',
            password='testpass123'
        )
        
        self.approver2 = User.objects.create_user(
            username='approver2',
            email='approver2@example.com',
            password='testpass123'
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
            created_by=self.user
        )
        
        # Create approval levels
        self.level1 = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver1,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00'),
            is_mandatory=True
        )
        
        self.level2 = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=2,
            approver=self.approver2,
            min_amount=Decimal('10000.01'),
            max_amount=Decimal('999999.99'),
            is_mandatory=True
        )
        
        # Create voucher
        self.voucher = VoucherV2.objects.create(
            voucher_type='CPV',
            voucher_number='CPV-TEST-INIT-001',
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Test payment',
            total_amount=Decimal('5000.00'),
            created_by=self.user
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
        
        self.service = ApprovalService()

    def test_initiate_approval_small_amount(self):
        """Test initiating approval for small amount (single level)"""
        request = self.service.initiate_approval(
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            requester=self.user
        )
        
        self.assertIsNotNone(request)
        self.assertEqual(request.workflow, self.workflow)
        self.assertEqual(request.document_type, 'voucher')
        self.assertEqual(request.document_id, self.voucher.id)
        self.assertEqual(request.amount, Decimal('5000.00'))
        self.assertEqual(request.current_level, 1)
        self.assertEqual(request.status, 'pending')
        self.assertEqual(request.requester, self.user)
        self.assertEqual(request.current_approver, self.approver1)

    def test_initiate_approval_large_amount(self):
        """Test initiating approval for large amount (multi-level)"""
        # Create large voucher
        large_voucher = VoucherV2.objects.create(
            voucher_type='CPV',
            voucher_number='CPV-TEST-LARGE-001',
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Large payment',
            total_amount=Decimal('25000.00'),
            created_by=self.user
        )
        
        request = self.service.initiate_approval(
            document_type='voucher',
            document_id=large_voucher.id,
            amount=Decimal('25000.00'),
            requester=self.user
        )
        
        self.assertEqual(request.current_level, 1)
        self.assertEqual(request.current_approver, self.approver1)

    def test_initiate_approval_no_workflow(self):
        """Test initiating approval when no workflow exists"""
        with self.assertRaises(ValidationError):
            self.service.initiate_approval(
                document_type='purchase_order',  # No workflow for this
                document_id=999,
                amount=Decimal('1000.00'),
                requester=self.user
            )

    def test_initiate_approval_duplicate(self):
        """Test that duplicate approval requests are prevented"""
        # Create first request
        self.service.initiate_approval(
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            requester=self.user
        )
        
        # Try to create duplicate
        with self.assertRaises(ValidationError):
            self.service.initiate_approval(
                document_type='voucher',
                document_id=self.voucher.id,
                amount=Decimal('5000.00'),
                requester=self.user
            )


class ApprovalServiceApproveTestCase(TestCase):
    """Test approval action"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpass123'
        )
        
        self.approver1 = User.objects.create_user(
            username='approver1',
            email='approver1@example.com',
            password='testpass123'
        )
        
        self.approver2 = User.objects.create_user(
            username='approver2',
            email='approver2@example.com',
            password='testpass123'
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
            created_by=self.user
        )
        
        self.level1 = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver1,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        self.level2 = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=2,
            approver=self.approver2,
            min_amount=Decimal('10000.01'),
            max_amount=Decimal('999999.99')
        )
        
        # Create voucher
        self.voucher = VoucherV2.objects.create(
            voucher_type='CPV',
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Test payment',
            total_amount=Decimal('5000.00'),
            created_by=self.user
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
        
        self.service = ApprovalService()
        
        # Create approval request
        self.approval_request = self.service.initiate_approval(
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            requester=self.user
        )

    def test_approve_single_level(self):
        """Test approving a single-level approval"""
        result = self.service.approve(
            approval_request_id=self.approval_request.id,
            approver=self.approver1,
            comments='Approved for payment',
            ip_address='192.168.1.1'
        )
        
        self.assertTrue(result['approved'])
        self.assertEqual(result['status'], 'approved')
        
        # Refresh from database
        self.approval_request.refresh_from_db()
        self.assertEqual(self.approval_request.status, 'approved')
        self.assertIsNotNone(self.approval_request.completion_date)
        
        # Check approval action created
        action = ApprovalAction.objects.get(approval_request=self.approval_request)
        self.assertEqual(action.approver, self.approver1)
        self.assertEqual(action.action, 'approved')
        self.assertEqual(action.comments, 'Approved for payment')

    def test_approve_multi_level_first_approval(self):
        """Test first approval in multi-level workflow"""
        # Create large voucher requiring 2 approvals
        large_voucher = VoucherV2.objects.create(
            voucher_type='CPV',
            voucher_number='CPV-TEST-MULTI-001',
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Large payment',
            total_amount=Decimal('25000.00'),
            created_by=self.user
        )
        
        VoucherEntryV2.objects.create(
            voucher=large_voucher,
            account=self.expense_account,
            debit_amount=Decimal('25000.00'),
            credit_amount=Decimal('0.00')
        )
        
        VoucherEntryV2.objects.create(
            voucher=large_voucher,
            account=self.cash_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('25000.00')
        )
        
        request = self.service.initiate_approval(
            document_type='voucher',
            document_id=large_voucher.id,
            amount=Decimal('25000.00'),
            requester=self.user
        )
        
        # First approval
        result = self.service.approve(
            approval_request_id=request.id,
            approver=self.approver1,
            comments='Level 1 approved',
            ip_address='192.168.1.1'
        )
        
        self.assertFalse(result['approved'])  # Not fully approved yet
        self.assertEqual(result['status'], 'pending')
        self.assertEqual(result['next_level'], 2)
        self.assertEqual(result['next_approver'], self.approver2)
        
        # Refresh and check
        request.refresh_from_db()
        self.assertEqual(request.current_level, 2)
        self.assertEqual(request.current_approver, self.approver2)
        self.assertEqual(request.status, 'pending')

    def test_approve_wrong_approver(self):
        """Test that only assigned approver can approve"""
        with self.assertRaises(ValidationError):
            self.service.approve(
                approval_request_id=self.approval_request.id,
                approver=self.approver2,  # Wrong approver
                comments='Trying to approve',
                ip_address='192.168.1.1'
            )

    def test_approve_already_approved(self):
        """Test that already approved request cannot be approved again"""
        # Approve first time
        self.service.approve(
            approval_request_id=self.approval_request.id,
            approver=self.approver1,
            comments='Approved',
            ip_address='192.168.1.1'
        )
        
        # Try to approve again
        with self.assertRaises(ValidationError):
            self.service.approve(
                approval_request_id=self.approval_request.id,
                approver=self.approver1,
                comments='Trying again',
                ip_address='192.168.1.1'
            )


class ApprovalServiceRejectTestCase(TestCase):
    """Test rejection action"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpass123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='testpass123'
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
            created_by=self.user
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
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Test payment',
            total_amount=Decimal('5000.00'),
            created_by=self.user
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
        
        self.service = ApprovalService()
        
        # Create approval request
        self.approval_request = self.service.initiate_approval(
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            requester=self.user
        )

    def test_reject_approval(self):
        """Test rejecting an approval request"""
        result = self.service.reject(
            approval_request_id=self.approval_request.id,
            approver=self.approver,
            comments='Insufficient documentation',
            ip_address='192.168.1.1'
        )
        
        self.assertTrue(result['rejected'])
        self.assertEqual(result['status'], 'rejected')
        
        # Refresh from database
        self.approval_request.refresh_from_db()
        self.assertEqual(self.approval_request.status, 'rejected')
        self.assertIsNotNone(self.approval_request.completion_date)
        
        # Check rejection action created
        action = ApprovalAction.objects.get(approval_request=self.approval_request)
        self.assertEqual(action.approver, self.approver)
        self.assertEqual(action.action, 'rejected')
        self.assertEqual(action.comments, 'Insufficient documentation')

    def test_reject_wrong_approver(self):
        """Test that only assigned approver can reject"""
        wrong_user = User.objects.create_user(
            username='wrong',
            email='wrong@example.com',
            password='testpass123'
        )
        
        with self.assertRaises(ValidationError):
            self.service.reject(
                approval_request_id=self.approval_request.id,
                approver=wrong_user,
                comments='Trying to reject',
                ip_address='192.168.1.1'
            )


class ApprovalServiceDelegateTestCase(TestCase):
    """Test delegation action"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpass123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='testpass123'
        )
        
        self.delegate = User.objects.create_user(
            username='delegate',
            email='delegate@example.com',
            password='testpass123'
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
            created_by=self.user
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
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Test payment',
            total_amount=Decimal('5000.00'),
            created_by=self.user
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
        
        self.service = ApprovalService()
        
        # Create approval request
        self.approval_request = self.service.initiate_approval(
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            requester=self.user
        )

    def test_delegate_approval(self):
        """Test delegating an approval to another user"""
        result = self.service.delegate(
            approval_request_id=self.approval_request.id,
            approver=self.approver,
            delegate_to=self.delegate,
            comments='Delegating while on leave',
            ip_address='192.168.1.1'
        )
        
        self.assertTrue(result['delegated'])
        self.assertEqual(result['new_approver'], self.delegate)
        
        # Refresh from database
        self.approval_request.refresh_from_db()
        self.assertEqual(self.approval_request.current_approver, self.delegate)
        self.assertEqual(self.approval_request.status, 'pending')
        
        # Check delegation action created
        action = ApprovalAction.objects.get(approval_request=self.approval_request)
        self.assertEqual(action.approver, self.approver)
        self.assertEqual(action.action, 'delegated')

    def test_delegate_to_self(self):
        """Test that user cannot delegate to themselves"""
        with self.assertRaises(ValidationError):
            self.service.delegate(
                approval_request_id=self.approval_request.id,
                approver=self.approver,
                delegate_to=self.approver,  # Same user
                comments='Trying to delegate to self',
                ip_address='192.168.1.1'
            )


class ApprovalServicePendingApprovalsTestCase(TestCase):
    """Test get pending approvals"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpass123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='testpass123'
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
            created_by=self.user
        )
        
        self.level = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        self.service = ApprovalService()

    def test_get_pending_approvals(self):
        """Test getting pending approvals for a user"""
        # Create 3 vouchers with approval requests
        for i in range(3):
            voucher = VoucherV2.objects.create(
                voucher_type='CPV',
                voucher_number=f'CPV-TEST-{i+1:04d}',  # Explicit number to avoid auto-numbering collision
                voucher_date=datetime.now().date(),
                currency=self.currency,
                narration=f'Test payment {i+1}',
                total_amount=Decimal('1000.00') * (i + 1),
                created_by=self.user
            )
            
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account=self.expense_account,
                debit_amount=Decimal('1000.00') * (i + 1),
                credit_amount=Decimal('0.00')
            )
            
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account=self.cash_account,
                debit_amount=Decimal('0.00'),
                credit_amount=Decimal('1000.00') * (i + 1)
            )
            
            self.service.initiate_approval(
                document_type='voucher',
                document_id=voucher.id,
                amount=Decimal('1000.00') * (i + 1),
                requester=self.user
            )
        
        # Get pending approvals
        pending = self.service.get_pending_approvals(self.approver)
        
        self.assertEqual(len(pending), 3)
        self.assertTrue(all(req.status == 'pending' for req in pending))
        self.assertTrue(all(req.current_approver == self.approver for req in pending))

    def test_get_pending_approvals_empty(self):
        """Test getting pending approvals when there are none"""
        pending = self.service.get_pending_approvals(self.approver)
        
        self.assertEqual(len(pending), 0)


class ApprovalServiceIFRSComplianceTestCase(TestCase):
    """Test IFRS compliance aspects (IAS 1 - Internal Controls)"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='requester',
            email='requester@example.com',
            password='testpass123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='testpass123'
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
            created_by=self.user
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
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Test payment',
            total_amount=Decimal('5000.00'),
            created_by=self.user
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
        
        self.service = ApprovalService()

    def test_segregation_of_duties_enforced(self):
        """Test that requester cannot approve their own request (IAS 1)"""
        request = self.service.initiate_approval(
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            requester=self.user
        )
        
        # Try to approve own request
        with self.assertRaises(ValidationError):
            self.service.approve(
                approval_request_id=request.id,
                approver=self.user,  # Same as requester
                comments='Self-approval attempt',
                ip_address='192.168.1.1'
            )

    def test_audit_trail_maintained(self):
        """Test that complete audit trail is maintained"""
        request = self.service.initiate_approval(
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            requester=self.user
        )
        
        self.service.approve(
            approval_request_id=request.id,
            approver=self.approver,
            comments='Approved',
            ip_address='192.168.1.100'
        )
        
        # Verify audit trail
        action = ApprovalAction.objects.get(approval_request=request)
        self.assertIsNotNone(action.approver)
        self.assertIsNotNone(action.action_date)
        self.assertIsNotNone(action.ip_address)
        self.assertEqual(action.ip_address, '192.168.1.100')
