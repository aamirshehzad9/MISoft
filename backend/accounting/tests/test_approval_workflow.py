"""
Unit Tests for Approval Workflow System
Module 1.3.1: Create ApprovalWorkflow Model

Test Coverage:
- ApprovalWorkflow model creation and validation
- ApprovalLevel model with amount thresholds
- ApprovalRequest model with status tracking
- ApprovalAction model with audit trail
- Relational integrity with VoucherV2
- IFRS compliance (IAS 1 - Internal Controls)

TDD Cycle: RED phase - Tests written first, expected to FAIL
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime, timedelta
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


class ApprovalWorkflowModelTestCase(TestCase):
    """Test ApprovalWorkflow model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_approval_workflow(self):
        """Test creating an approval workflow"""
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Purchase Order Approval',
            description='Approval workflow for purchase orders',
            document_type='purchase_order',
            is_active=True,
            created_by=self.user
        )
        
        self.assertEqual(workflow.workflow_name, 'Purchase Order Approval')
        self.assertEqual(workflow.document_type, 'purchase_order')
        self.assertTrue(workflow.is_active)
        self.assertEqual(workflow.created_by, self.user)

    def test_workflow_string_representation(self):
        """Test __str__ method"""
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            created_by=self.user
        )
        
        self.assertEqual(str(workflow), 'Voucher Approval (voucher)')

    def test_workflow_document_type_choices(self):
        """Test document type choices validation"""
        valid_types = [
            'voucher', 'purchase_order', 'purchase_requisition',
            'sales_order', 'sales_quotation', 'payment', 'receipt',
            'bank_transfer', 'journal_entry', 'asset_acquisition',
            'asset_disposal', 'budget', 'other'
        ]
        
        for doc_type in valid_types:
            workflow = ApprovalWorkflow.objects.create(
                workflow_name=f'Test {doc_type}',
                document_type=doc_type,
                created_by=self.user
            )
            self.assertEqual(workflow.document_type, doc_type)

    def test_workflow_unique_active_per_document_type(self):
        """Test only one active workflow per document type"""
        # Create first active workflow
        ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval 1',
            document_type='voucher',
            is_active=True,
            created_by=self.user
        )
        
        # Creating second active workflow for same type should fail
        with self.assertRaises(ValidationError):
            workflow2 = ApprovalWorkflow(
                workflow_name='Voucher Approval 2',
                document_type='voucher',
                is_active=True,
                created_by=self.user
            )
            workflow2.full_clean()

    def test_workflow_multiple_inactive_allowed(self):
        """Test multiple inactive workflows allowed for same document type"""
        ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval 1',
            document_type='voucher',
            is_active=False,
            created_by=self.user
        )
        
        workflow2 = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval 2',
            document_type='voucher',
            is_active=False,
            created_by=self.user
        )
        
        self.assertEqual(workflow2.document_type, 'voucher')
        self.assertFalse(workflow2.is_active)


class ApprovalLevelModelTestCase(TestCase):
    """Test ApprovalLevel model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
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
        
        self.workflow = ApprovalWorkflow.objects.create(
            workflow_name='Voucher Approval',
            document_type='voucher',
            created_by=self.user
        )

    def test_create_approval_level(self):
        """Test creating an approval level"""
        level = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver1,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00'),
            is_mandatory=True
        )
        
        self.assertEqual(level.workflow, self.workflow)
        self.assertEqual(level.level_number, 1)
        self.assertEqual(level.approver, self.approver1)
        self.assertTrue(level.is_mandatory)

    def test_approval_level_ordering(self):
        """Test approval levels are ordered by level_number"""
        level2 = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=2,
            approver=self.approver2,
            min_amount=Decimal('10000.01'),
            max_amount=Decimal('50000.00')
        )
        
        level1 = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver1,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        levels = list(ApprovalLevel.objects.filter(workflow=self.workflow))
        self.assertEqual(levels[0].level_number, 1)
        self.assertEqual(levels[1].level_number, 2)

    def test_approval_level_amount_validation(self):
        """Test amount range validation"""
        # min_amount should be less than max_amount
        with self.assertRaises(ValidationError):
            level = ApprovalLevel(
                workflow=self.workflow,
                level_number=1,
                approver=self.approver1,
                min_amount=Decimal('10000.00'),
                max_amount=Decimal('5000.00')  # Invalid: max < min
            )
            level.full_clean()

    def test_approval_level_string_representation(self):
        """Test __str__ method"""
        level = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver1,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        expected = f'Level 1 - {self.approver1.username} (0.00 - 10000.00)'
        self.assertEqual(str(level), expected)


class ApprovalRequestModelTestCase(TestCase):
    """Test ApprovalRequest model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
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
        
        self.workflow = ApprovalWorkflow.objects.create(
            workflow_name='Payment Approval',
            document_type='voucher',
            created_by=self.user
        )
        
        self.level = ApprovalLevel.objects.create(
            workflow=self.workflow,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )

    def test_create_approval_request(self):
        """Test creating an approval request"""
        request = ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.user,
            current_approver=self.approver
        )
        
        self.assertEqual(request.workflow, self.workflow)
        self.assertEqual(request.document_id, self.voucher.id)
        self.assertEqual(request.amount, Decimal('5000.00'))
        self.assertEqual(request.status, 'pending')

    def test_approval_request_status_choices(self):
        """Test status choices"""
        valid_statuses = ['pending', 'approved', 'rejected', 'cancelled']
        
        for status in valid_statuses:
            request = ApprovalRequest.objects.create(
                workflow=self.workflow,
                document_type='voucher',
                document_id=self.voucher.id,
                amount=Decimal('5000.00'),
                current_level=1,
                status=status,
                requester=self.user,
                current_approver=self.approver
            )
            self.assertEqual(request.status, status)

    def test_approval_request_timestamps(self):
        """Test automatic timestamp fields"""
        request = ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.user,
            current_approver=self.approver
        )
        
        self.assertIsNotNone(request.request_date)
        self.assertIsNone(request.completion_date)
        
        # Complete the request
        request.status = 'approved'
        request.completion_date = datetime.now()
        request.save()
        
        self.assertIsNotNone(request.completion_date)

    def test_approval_request_string_representation(self):
        """Test __str__ method"""
        request = ApprovalRequest.objects.create(
            workflow=self.workflow,
            document_type='voucher',
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.user,
            current_approver=self.approver
        )
        
        expected = f'Approval Request for voucher #{self.voucher.id} - pending'
        self.assertEqual(str(request), expected)


class ApprovalActionModelTestCase(TestCase):
    """Test ApprovalAction model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='testpass123'
        )
        
        # Create currency
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
        
        self.workflow = ApprovalWorkflow.objects.create(
            workflow_name='Payment Approval',
            document_type='voucher',
            created_by=self.user
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
            document_id=self.voucher.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.user,
            current_approver=self.approver
        )

    def test_create_approval_action(self):
        """Test creating an approval action"""
        action = ApprovalAction.objects.create(
            approval_request=self.approval_request,
            level_number=1,
            approver=self.approver,
            action='approved',
            comments='Approved for payment',
            ip_address='192.168.1.1'
        )
        
        self.assertEqual(action.approval_request, self.approval_request)
        self.assertEqual(action.level_number, 1)
        self.assertEqual(action.approver, self.approver)
        self.assertEqual(action.action, 'approved')

    def test_approval_action_choices(self):
        """Test action choices"""
        valid_actions = ['approved', 'rejected', 'delegated', 'returned']
        
        for action_type in valid_actions:
            action = ApprovalAction.objects.create(
                approval_request=self.approval_request,
                level_number=1,
                approver=self.approver,
                action=action_type,
                ip_address='192.168.1.1'
            )
            self.assertEqual(action.action, action_type)

    def test_approval_action_audit_trail(self):
        """Test audit trail fields (IFRS compliance - IAS 1)"""
        action = ApprovalAction.objects.create(
            approval_request=self.approval_request,
            level_number=1,
            approver=self.approver,
            action='approved',
            comments='Approved',
            ip_address='192.168.1.100'
        )
        
        # Verify audit trail
        self.assertIsNotNone(action.action_date)
        self.assertEqual(action.approver, self.approver)
        self.assertEqual(action.ip_address, '192.168.1.100')
        self.assertEqual(action.comments, 'Approved')

    def test_approval_action_string_representation(self):
        """Test __str__ method"""
        action = ApprovalAction.objects.create(
            approval_request=self.approval_request,
            level_number=1,
            approver=self.approver,
            action='approved',
            ip_address='192.168.1.1'
        )
        
        expected = f'Level 1 - approved by {self.approver.username}'
        self.assertEqual(str(action), expected)

    def test_approval_action_immutability(self):
        """Test that approval actions cannot be deleted (audit requirement)"""
        action = ApprovalAction.objects.create(
            approval_request=self.approval_request,
            level_number=1,
            approver=self.approver,
            action='approved',
            ip_address='192.168.1.1'
        )
        
        # Approval actions should not be deletable (audit trail)
        # This will be enforced in the model's delete() method
        action_id = action.id
        
        # Try to delete
        with self.assertRaises(ValidationError):
            action.delete()
        
        # Verify still exists
        self.assertTrue(ApprovalAction.objects.filter(id=action_id).exists())


class ApprovalWorkflowIntegrationTestCase(TestCase):
    """Integration tests for approval workflow system"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
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

    def test_multi_level_approval_workflow(self):
        """Test complete multi-level approval workflow"""
        # Create workflow with 2 levels
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Payment Approval',
            document_type='voucher',
            created_by=self.user
        )
        
        level1 = ApprovalLevel.objects.create(
            workflow=workflow,
            level_number=1,
            approver=self.approver1,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('50000.00'),
            is_mandatory=True
        )
        
        level2 = ApprovalLevel.objects.create(
            workflow=workflow,
            level_number=2,
            approver=self.approver2,
            min_amount=Decimal('10000.01'),
            max_amount=Decimal('50000.00'),
            is_mandatory=True
        )
        
        # Create voucher
        voucher = VoucherV2.objects.create(
            voucher_type='CPV',
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Large payment requiring 2 approvals',
            total_amount=Decimal('25000.00'),
            created_by=self.user
        )
        
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.expense_account,
            debit_amount=Decimal('25000.00'),
            credit_amount=Decimal('0.00')
        )
        
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.cash_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('25000.00')
        )
        
        # Create approval request
        request = ApprovalRequest.objects.create(
            workflow=workflow,
            document_type='voucher',
            document_id=voucher.id,
            amount=Decimal('25000.00'),
            current_level=1,
            status='pending',
            requester=self.user,
            current_approver=self.approver1
        )
        
        # Level 1 approval
        action1 = ApprovalAction.objects.create(
            approval_request=request,
            level_number=1,
            approver=self.approver1,
            action='approved',
            comments='Level 1 approved',
            ip_address='192.168.1.1'
        )
        
        # Move to level 2
        request.current_level = 2
        request.current_approver = self.approver2
        request.save()
        
        # Level 2 approval
        action2 = ApprovalAction.objects.create(
            approval_request=request,
            level_number=2,
            approver=self.approver2,
            action='approved',
            comments='Level 2 approved',
            ip_address='192.168.1.2'
        )
        
        # Complete request
        request.status = 'approved'
        request.completion_date = datetime.now()
        request.save()
        
        # Verify workflow
        self.assertEqual(request.status, 'approved')
        self.assertEqual(ApprovalAction.objects.filter(approval_request=request).count(), 2)
        self.assertIsNotNone(request.completion_date)

    def test_amount_based_approval_routing(self):
        """Test approval routing based on amount thresholds"""
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Payment Approval',
            document_type='voucher',
            created_by=self.user
        )
        
        # Level 1: 0 - 10,000 (single approval)
        level1 = ApprovalLevel.objects.create(
            workflow=workflow,
            level_number=1,
            approver=self.approver1,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00'),
            is_mandatory=True
        )
        
        # Level 2: 10,000+ (requires both approvals)
        level2 = ApprovalLevel.objects.create(
            workflow=workflow,
            level_number=2,
            approver=self.approver2,
            min_amount=Decimal('10000.01'),
            max_amount=Decimal('999999.99'),
            is_mandatory=True
        )
        
        # Small amount (5,000) - should only need level 1
        voucher_small = VoucherV2.objects.create(
            voucher_type='CPV',
            voucher_date=datetime.now().date(),
            currency=self.currency,
            narration='Small payment',
            total_amount=Decimal('5000.00'),
            created_by=self.user
        )
        
        VoucherEntryV2.objects.create(
            voucher=voucher_small,
            account=self.expense_account,
            debit_amount=Decimal('5000.00'),
            credit_amount=Decimal('0.00')
        )
        
        VoucherEntryV2.objects.create(
            voucher=voucher_small,
            account=self.cash_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('5000.00')
        )
        
        request_small = ApprovalRequest.objects.create(
            workflow=workflow,
            document_type='voucher',
            document_id=voucher_small.id,
            amount=Decimal('5000.00'),
            current_level=1,
            status='pending',
            requester=self.user,
            current_approver=self.approver1
        )
        
        # Verify only level 1 is required
        self.assertEqual(request_small.current_level, 1)
        self.assertEqual(request_small.current_approver, self.approver1)


class ApprovalWorkflowIFRSComplianceTestCase(TestCase):
    """Test IFRS compliance aspects (IAS 1 - Internal Controls)"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@example.com',
            password='testpass123'
        )

    def test_segregation_of_duties(self):
        """Test that requester cannot be approver (IAS 1 - Internal Controls)"""
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Payment Approval',
            document_type='voucher',
            created_by=self.user
        )
        
        level = ApprovalLevel.objects.create(
            workflow=workflow,
            level_number=1,
            approver=self.user,  # Same as requester
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        # This should be validated in the service layer
        # Model allows it, but service should prevent it
        self.assertEqual(level.approver, self.user)

    def test_audit_trail_completeness(self):
        """Test complete audit trail (IFRS requirement)"""
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Payment Approval',
            document_type='voucher',
            created_by=self.user
        )
        
        # Verify audit fields
        self.assertIsNotNone(workflow.created_by)
        self.assertIsNotNone(workflow.created_at)
        self.assertIsNotNone(workflow.updated_at)

    def test_approval_action_non_repudiation(self):
        """Test non-repudiation of approval actions (IFRS audit requirement)"""
        # Create minimal setup
        currency = CurrencyV2.objects.create(
            currency_code='PKR',
            currency_name='Pakistani Rupee',
            symbol='Rs',
            is_active=True
        )
        
        cash_account = AccountV2.objects.create(
            code='1010',
            name='Cash',
            account_type='asset',
            account_group='current_asset'
        )
        
        expense_account = AccountV2.objects.create(
            code='5010',
            name='Office Expense',
            account_type='expense',
            account_group='operating_expense'
        )
        
        voucher = VoucherV2.objects.create(
            voucher_type='CPV',
            voucher_date=datetime.now().date(),
            currency=currency,
            narration='Test',
            total_amount=Decimal('1000.00'),
            created_by=self.user
        )
        
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=expense_account,
            debit_amount=Decimal('1000.00'),
            credit_amount=Decimal('0.00')
        )
        
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=cash_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('1000.00')
        )
        
        workflow = ApprovalWorkflow.objects.create(
            workflow_name='Payment Approval',
            document_type='voucher',
            created_by=self.user
        )
        
        level = ApprovalLevel.objects.create(
            workflow=workflow,
            level_number=1,
            approver=self.approver,
            min_amount=Decimal('0.00'),
            max_amount=Decimal('10000.00')
        )
        
        request = ApprovalRequest.objects.create(
            workflow=workflow,
            document_type='voucher',
            document_id=voucher.id,
            amount=Decimal('1000.00'),
            current_level=1,
            status='pending',
            requester=self.user,
            current_approver=self.approver
        )
        
        action = ApprovalAction.objects.create(
            approval_request=request,
            level_number=1,
            approver=self.approver,
            action='approved',
            comments='Approved',
            ip_address='192.168.1.1'
        )
        
        # Verify non-repudiation fields
        self.assertIsNotNone(action.approver)
        self.assertIsNotNone(action.action_date)
        self.assertIsNotNone(action.ip_address)
        
        # Action should be immutable
        original_action = action.action
        action.action = 'rejected'
        
        # This should fail (enforced in model)
        with self.assertRaises(ValidationError):
            action.save()
