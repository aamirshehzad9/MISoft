"""
Unit Tests for Bank Transfer Reports
Module 2.3: Bank Transfer System
Task 2.3.3: Transfer Reports

Tests the report generation methods for Bank Transfer System.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import AccountV2, CurrencyV2, BankTransfer
from accounting.services.bank_transfer_service import BankTransferService
import datetime

User = get_user_model()


class BankTransferReportsTestCase(TestCase):
    """Test suite for Bank Transfer Reports"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Currencies
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        
        self.eur = CurrencyV2.objects.create(
            currency_code='EUR',
            currency_name='Euro',
            symbol='€'
        )

        # Bank Accounts
        self.bank_usd = AccountV2.objects.create(
            name="USD Bank Account",
            code="1001",
            account_type="asset",
            account_group="current_asset",
            is_active=True
        )

        self.bank_eur = AccountV2.objects.create(
            name="EUR Bank Account",
            code="1002",
            account_type="asset",
            account_group="current_asset",
            is_active=True
        )

        # Create sample transfers with different statuses
        self._create_sample_transfers()

    def _create_sample_transfers(self):
        """Create sample transfers for testing"""
        # Pending transfer
        self.pending_transfer = BankTransferService.create_transfer(
            transfer_number="TRF-PEND-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user,
            description="Pending transfer"
        )

        # Approved but not executed transfer
        self.approved_transfer = BankTransferService.create_transfer(
            transfer_number="TRF-APP-001",
            transfer_date=datetime.date(2025, 1, 16),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('3000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user,
            description="Approved transfer"
        )
        BankTransferService.approve_transfer(self.approved_transfer, self.user)

        # Completed transfer
        self.completed_transfer = BankTransferService.create_transfer(
            transfer_number="TRF-COMP-001",
            transfer_date=datetime.date(2025, 1, 10),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user,
            description="Completed transfer"
        )
        BankTransferService.approve_transfer(self.completed_transfer, self.user)
        BankTransferService.execute_transfer(self.completed_transfer, self.user)

        # Multi-currency completed transfer
        self.multi_currency_transfer = BankTransferService.create_transfer(
            transfer_number="TRF-MULTI-001",
            transfer_date=datetime.date(2025, 1, 12),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('8000.00'),
            from_currency=self.usd,
            to_currency=self.eur,
            exchange_rate=Decimal('0.9200'),
            user=self.user,
            description="Multi-currency transfer"
        )
        BankTransferService.approve_transfer(self.multi_currency_transfer, self.user)
        BankTransferService.execute_transfer(self.multi_currency_transfer, self.user)

        # Rejected transfer
        self.rejected_transfer = BankTransferService.create_transfer(
            transfer_number="TRF-REJ-001",
            transfer_date=datetime.date(2025, 1, 14),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('2000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user,
            description="Rejected transfer"
        )
        BankTransferService.reject_transfer(self.rejected_transfer, self.user)

    def test_generate_transfer_register(self):
        """Test Bank Transfer Register generation"""
        report = BankTransferService.generate_transfer_register()

        self.assertIsNotNone(report)
        self.assertIn('transfers', report)
        self.assertIn('total_amount', report)
        self.assertIn('count', report)

        # Should include all transfers (5 total)
        self.assertEqual(report['count'], 5)

        # Verify total amount
        expected_total = (
            Decimal('5000.00') +  # pending
            Decimal('3000.00') +  # approved
            Decimal('10000.00') + # completed
            Decimal('8000.00') +  # multi-currency
            Decimal('2000.00')    # rejected
        )
        self.assertEqual(report['total_amount'], expected_total)

        # Verify transfers are in the list
        transfer_numbers = [t['transfer_number'] for t in report['transfers']]
        self.assertIn("TRF-PEND-001", transfer_numbers)
        self.assertIn("TRF-COMP-001", transfer_numbers)

    def test_generate_transfer_register_with_date_range(self):
        """Test Transfer Register with date filtering"""
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2025, 1, 13)

        report = BankTransferService.generate_transfer_register(
            start_date=start_date,
            end_date=end_date
        )

        # Should only include transfers within date range
        self.assertLessEqual(report['count'], 5)
        
        # Verify all transfers in report are within date range
        for transfer in report['transfers']:
            transfer_date = transfer['transfer_date']
            self.assertGreaterEqual(transfer_date, start_date)
            self.assertLessEqual(transfer_date, end_date)

    def test_generate_transfer_register_by_status(self):
        """Test Transfer Register filtered by status"""
        report = BankTransferService.generate_transfer_register(status='completed')

        # Should only include completed transfers (2)
        self.assertEqual(report['count'], 2)
        
        # Verify all are completed
        for transfer in report['transfers']:
            self.assertEqual(transfer['status'], 'completed')

    def test_generate_pending_transfers_report(self):
        """Test Pending Transfers Report generation"""
        report = BankTransferService.generate_pending_transfers_report()

        self.assertIsNotNone(report)
        self.assertIn('transfers', report)
        self.assertIn('total_amount', report)
        self.assertIn('count', report)

        # Should include pending and approved (not executed) transfers (2)
        self.assertEqual(report['count'], 2)

        # Verify total amount
        expected_total = Decimal('5000.00') + Decimal('3000.00')
        self.assertEqual(report['total_amount'], expected_total)

        # Verify transfers are pending execution
        transfer_numbers = [t['transfer_number'] for t in report['transfers']]
        self.assertIn("TRF-PEND-001", transfer_numbers)
        self.assertIn("TRF-APP-001", transfer_numbers)

    def test_generate_pending_transfers_report_by_approval_status(self):
        """Test Pending Transfers Report filtered by approval status"""
        report = BankTransferService.generate_pending_transfers_report(
            approval_status='pending'
        )

        # Should only include transfers with pending approval (1)
        self.assertEqual(report['count'], 1)
        self.assertEqual(report['transfers'][0]['transfer_number'], "TRF-PEND-001")

    def test_transfer_register_empty(self):
        """Test Transfer Register when no transfers exist"""
        # Delete all transfers
        BankTransfer.objects.all().delete()

        report = BankTransferService.generate_transfer_register()

        self.assertEqual(report['count'], 0)
        self.assertEqual(report['total_amount'], Decimal('0.00'))
        self.assertEqual(len(report['transfers']), 0)

    def test_pending_transfers_report_empty(self):
        """Test Pending Transfers Report when no pending transfers exist"""
        # Delete all pending transfers
        BankTransfer.objects.filter(status='pending').delete()

        report = BankTransferService.generate_pending_transfers_report()

        self.assertEqual(report['count'], 0)
        self.assertEqual(report['total_amount'], Decimal('0.00'))
        self.assertEqual(len(report['transfers']), 0)

    def test_reports_include_required_fields(self):
        """Test that all reports include required fields"""
        # Transfer Register
        register_report = BankTransferService.generate_transfer_register()
        if register_report['count'] > 0:
            transfer = register_report['transfers'][0]
            self.assertIn('transfer_number', transfer)
            self.assertIn('transfer_date', transfer)
            self.assertIn('from_bank_name', transfer)
            self.assertIn('to_bank_name', transfer)
            self.assertIn('amount', transfer)
            self.assertIn('status', transfer)
            self.assertIn('approval_status', transfer)

        # Pending Transfers Report
        pending_report = BankTransferService.generate_pending_transfers_report()
        if pending_report['count'] > 0:
            transfer = pending_report['transfers'][0]
            self.assertIn('transfer_number', transfer)
            self.assertIn('approval_status', transfer)

    def test_quality_gate_transfers_create_vouchers(self):
        """Quality Gate: Test that transfers create correct vouchers"""
        # Create and execute a transfer
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-QG-001",
            transfer_date=datetime.date(2025, 1, 20),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )
        
        BankTransferService.approve_transfer(transfer, self.user)
        executed_transfer = BankTransferService.execute_transfer(transfer, self.user)

        # Verify voucher was created
        self.assertIsNotNone(executed_transfer.voucher)
        self.assertEqual(executed_transfer.voucher.status, 'posted')
        
        # Verify voucher entries are correct
        from accounting.models import VoucherEntryV2
        entries = VoucherEntryV2.objects.filter(voucher=executed_transfer.voucher)
        self.assertEqual(entries.count(), 2)

    def test_quality_gate_multi_currency_transfers(self):
        """Quality Gate: Test that multi-currency transfers work correctly"""
        # Create and execute a multi-currency transfer
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-QG-MULTI",
            transfer_date=datetime.date(2025, 1, 20),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.eur,
            exchange_rate=Decimal('0.9200'),
            user=self.user
        )
        
        BankTransferService.approve_transfer(transfer, self.user)
        executed_transfer = BankTransferService.execute_transfer(transfer, self.user)

        # Verify converted amount is correct
        self.assertEqual(executed_transfer.converted_amount, Decimal('9200.00'))
        
        # Verify voucher was created
        self.assertIsNotNone(executed_transfer.voucher)

    def test_quality_gate_approval_workflow(self):
        """Quality Gate: Test that approval workflow is functional"""
        # Create a transfer
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-QG-APPR",
            transfer_date=datetime.date(2025, 1, 20),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        # Verify initial status
        self.assertEqual(transfer.approval_status, 'pending')
        self.assertEqual(transfer.status, 'pending')

        # Approve
        approved_transfer = BankTransferService.approve_transfer(transfer, self.user)
        self.assertEqual(approved_transfer.approval_status, 'approved')

        # Execute
        executed_transfer = BankTransferService.execute_transfer(approved_transfer, self.user)
        self.assertEqual(executed_transfer.status, 'completed')

        # Verify cannot execute unapproved transfers
        unapproved_transfer = BankTransferService.create_transfer(
            transfer_number="TRF-QG-UNAPPR",
            transfer_date=datetime.date(2025, 1, 20),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('3000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        with self.assertRaises(ValueError):
            BankTransferService.execute_transfer(unapproved_transfer, self.user)
