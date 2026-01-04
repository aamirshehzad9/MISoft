"""
Unit Tests for Bank Transfer Service
Module 2.3: Bank Transfer System
Task 2.3.2: Transfer Service

Tests the BankTransferService class for professional bank transfer workflow.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import AccountV2, VoucherV2, VoucherEntryV2, CurrencyV2, BankTransfer
from accounting.services.bank_transfer_service import BankTransferService
import datetime

User = get_user_model()


class BankTransferServiceTestCase(TestCase):
    """Test suite for Bank Transfer Service"""

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

        # Exchange gain/loss account
        self.fx_gain_loss = AccountV2.objects.create(
            name="FX Gain/Loss",
            code="7001",
            account_type="expense",
            account_group="operating_expense",
            is_active=True
        )

    def test_create_transfer_basic(self):
        """Test basic transfer creation"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        self.assertIsNotNone(transfer)
        self.assertEqual(transfer.transfer_number, "TRF-001")
        self.assertEqual(transfer.status, 'pending')
        self.assertEqual(transfer.approval_status, 'pending')
        self.assertEqual(transfer.amount, Decimal('10000.00'))
        self.assertIsNone(transfer.voucher)

    def test_create_transfer_with_description(self):
        """Test transfer creation with description and reference"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-002",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user,
            description="Monthly transfer",
            reference="REF-12345"
        )

        self.assertEqual(transfer.description, "Monthly transfer")
        self.assertEqual(transfer.reference, "REF-12345")

    def test_create_multi_currency_transfer(self):
        """Test multi-currency transfer creation"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-MULTI-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.eur,
            exchange_rate=Decimal('0.9200'),
            user=self.user
        )

        self.assertEqual(transfer.from_currency, self.usd)
        self.assertEqual(transfer.to_currency, self.eur)
        self.assertEqual(transfer.exchange_rate, Decimal('0.9200'))
        self.assertEqual(transfer.converted_amount, Decimal('9200.00'))

    def test_approve_transfer(self):
        """Test transfer approval"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-APP-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        approved_transfer = BankTransferService.approve_transfer(transfer, self.user)

        self.assertEqual(approved_transfer.approval_status, 'approved')
        self.assertEqual(approved_transfer.status, 'pending')  # Still pending execution

    def test_reject_transfer(self):
        """Test transfer rejection"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-REJ-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        rejected_transfer = BankTransferService.reject_transfer(transfer, self.user)

        self.assertEqual(rejected_transfer.approval_status, 'rejected')
        self.assertEqual(rejected_transfer.status, 'failed')

    def test_execute_transfer_same_currency(self):
        """Test executing transfer with same currency (creates voucher)"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-EXEC-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        # Approve first
        BankTransferService.approve_transfer(transfer, self.user)

        # Execute
        executed_transfer = BankTransferService.execute_transfer(transfer, self.user)

        self.assertEqual(executed_transfer.status, 'completed')
        self.assertIsNotNone(executed_transfer.voucher)
        
        # Verify voucher entries
        voucher = executed_transfer.voucher
        self.assertEqual(voucher.status, 'posted')
        
        entries = VoucherEntryV2.objects.filter(voucher=voucher)
        self.assertEqual(entries.count(), 2)
        
        # Check debit entry (to_bank)
        debit_entry = entries.filter(account=self.bank_eur).first()
        self.assertEqual(debit_entry.debit_amount, Decimal('10000.00'))
        self.assertEqual(debit_entry.credit_amount, Decimal('0.00'))
        
        # Check credit entry (from_bank)
        credit_entry = entries.filter(account=self.bank_usd).first()
        self.assertEqual(credit_entry.debit_amount, Decimal('0.00'))
        self.assertEqual(credit_entry.credit_amount, Decimal('10000.00'))

    def test_execute_transfer_multi_currency(self):
        """Test executing multi-currency transfer (creates voucher with FX)"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-EXEC-MULTI-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.eur,
            exchange_rate=Decimal('0.9200'),
            user=self.user
        )

        # Approve first
        BankTransferService.approve_transfer(transfer, self.user)

        # Execute
        executed_transfer = BankTransferService.execute_transfer(
            transfer, 
            self.user,
            fx_account=self.fx_gain_loss
        )

        self.assertEqual(executed_transfer.status, 'completed')
        self.assertIsNotNone(executed_transfer.voucher)
        
        # Verify voucher entries (should have 3: debit to_bank, credit from_bank, FX difference)
        voucher = executed_transfer.voucher
        entries = VoucherEntryV2.objects.filter(voucher=voucher)
        self.assertGreaterEqual(entries.count(), 2)

    def test_execute_transfer_not_approved(self):
        """Test that unapproved transfers cannot be executed"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-NOAPP-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        # Try to execute without approval
        with self.assertRaises(ValueError):
            BankTransferService.execute_transfer(transfer, self.user)

    def test_execute_transfer_already_completed(self):
        """Test that completed transfers cannot be executed again"""
        transfer = BankTransferService.create_transfer(
            transfer_number="TRF-DUP-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        # Approve and execute
        BankTransferService.approve_transfer(transfer, self.user)
        BankTransferService.execute_transfer(transfer, self.user)

        # Try to execute again
        with self.assertRaises(ValueError):
            BankTransferService.execute_transfer(transfer, self.user)

    def test_get_pending_transfers(self):
        """Test retrieving pending transfers"""
        # Create some transfers
        transfer1 = BankTransferService.create_transfer(
            transfer_number="TRF-PEND-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        transfer2 = BankTransferService.create_transfer(
            transfer_number="TRF-PEND-002",
            transfer_date=datetime.date(2025, 1, 16),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('3000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        pending_transfers = BankTransferService.get_pending_transfers()

        self.assertEqual(len(pending_transfers), 2)
        self.assertIn(transfer1, pending_transfers)
        self.assertIn(transfer2, pending_transfers)

    def test_get_transfers_by_status(self):
        """Test retrieving transfers by status"""
        # Create transfers with different statuses
        pending_transfer = BankTransferService.create_transfer(
            transfer_number="TRF-ST-PEND",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        completed_transfer = BankTransferService.create_transfer(
            transfer_number="TRF-ST-COMP",
            transfer_date=datetime.date(2025, 1, 16),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('3000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )
        BankTransferService.approve_transfer(completed_transfer, self.user)
        BankTransferService.execute_transfer(completed_transfer, self.user)

        # Get pending transfers
        pending = BankTransferService.get_transfers_by_status('pending')
        self.assertIn(pending_transfer, pending)
        self.assertNotIn(completed_transfer, pending)

        # Get completed transfers
        completed = BankTransferService.get_transfers_by_status('completed')
        self.assertIn(completed_transfer, completed)
        self.assertNotIn(pending_transfer, completed)

    def test_create_transfer_duplicate_number(self):
        """Test that duplicate transfer numbers are not allowed"""
        BankTransferService.create_transfer(
            transfer_number="TRF-DUP",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_usd,
            to_bank=self.bank_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            user=self.user
        )

        # Try to create with same number
        with self.assertRaises(Exception):  # IntegrityError
            BankTransferService.create_transfer(
                transfer_number="TRF-DUP",
                transfer_date=datetime.date(2025, 1, 16),
                from_bank=self.bank_usd,
                to_bank=self.bank_eur,
                amount=Decimal('3000.00'),
                from_currency=self.usd,
                to_currency=self.usd,
                exchange_rate=Decimal('1.0000'),
                user=self.user
            )
