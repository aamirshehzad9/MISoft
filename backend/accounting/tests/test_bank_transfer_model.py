"""
Unit Tests for BankTransfer Model
Module 2.3: Bank Transfer System
Task 2.3.1: Create BankTransfer Model

Tests the BankTransfer model for professional bank-to-bank transfer workflow.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from accounting.models import AccountV2, VoucherV2, CurrencyV2
import datetime

User = get_user_model()


class BankTransferModelTestCase(TestCase):
    """Test suite for BankTransfer Model"""

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
        self.bank_account_usd = AccountV2.objects.create(
            name="USD Bank Account",
            code="1001",
            account_type="asset",
            account_group="current_asset",
            is_active=True
        )

        self.bank_account_eur = AccountV2.objects.create(
            name="EUR Bank Account",
            code="1002",
            account_type="asset",
            account_group="current_asset",
            is_active=True
        )

        # Voucher for linking
        self.voucher = VoucherV2.objects.create(
            voucher_number="VCH-TRANS-001",
            voucher_type="JV",
            voucher_date=datetime.date(2025, 1, 15),
            total_amount=Decimal('10000.00'),
            currency=self.usd,
            status='posted',
            created_by=self.user
        )

    def test_create_bank_transfer_basic(self):
        """Test creating a basic bank transfer"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        self.assertIsNotNone(transfer)
        self.assertEqual(transfer.transfer_number, "TRF-001")
        self.assertEqual(transfer.amount, Decimal('10000.00'))
        self.assertEqual(transfer.status, 'pending')
        self.assertEqual(transfer.approval_status, 'pending')
        self.assertEqual(transfer.from_bank, self.bank_account_usd)
        self.assertEqual(transfer.to_bank, self.bank_account_eur)

    def test_transfer_number_unique(self):
        """Test that transfer number must be unique"""
        from accounting.models import BankTransfer
        
        BankTransfer.objects.create(
            transfer_number="TRF-UNIQUE",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            BankTransfer.objects.create(
                transfer_number="TRF-UNIQUE",
                transfer_date=datetime.date(2025, 1, 16),
                from_bank=self.bank_account_usd,
                to_bank=self.bank_account_eur,
                amount=Decimal('3000.00'),
                from_currency=self.usd,
                to_currency=self.usd,
                exchange_rate=Decimal('1.0000'),
                status='pending',
                approval_status='pending',
                created_by=self.user
            )

    def test_transfer_status_choices(self):
        """Test all transfer status choices"""
        from accounting.models import BankTransfer
        
        statuses = ['pending', 'completed', 'failed']
        
        for idx, status in enumerate(statuses):
            transfer = BankTransfer.objects.create(
                transfer_number=f"TRF-{status.upper()}-{idx}",
                transfer_date=datetime.date(2025, 1, 15),
                from_bank=self.bank_account_usd,
                to_bank=self.bank_account_eur,
                amount=Decimal('1000.00'),
                from_currency=self.usd,
                to_currency=self.usd,
                exchange_rate=Decimal('1.0000'),
                status=status,
                approval_status='approved',
                created_by=self.user
            )
            self.assertEqual(transfer.status, status)

    def test_approval_status_choices(self):
        """Test all approval status choices"""
        from accounting.models import BankTransfer
        
        approval_statuses = ['pending', 'approved', 'rejected']
        
        for idx, approval_status in enumerate(approval_statuses):
            transfer = BankTransfer.objects.create(
                transfer_number=f"TRF-APP-{approval_status.upper()}-{idx}",
                transfer_date=datetime.date(2025, 1, 15),
                from_bank=self.bank_account_usd,
                to_bank=self.bank_account_eur,
                amount=Decimal('1000.00'),
                from_currency=self.usd,
                to_currency=self.usd,
                exchange_rate=Decimal('1.0000'),
                status='pending',
                approval_status=approval_status,
                created_by=self.user
            )
            self.assertEqual(transfer.approval_status, approval_status)

    def test_multi_currency_transfer(self):
        """Test multi-currency transfer with exchange rate"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-MULTI-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.eur,
            exchange_rate=Decimal('0.9200'),  # 1 USD = 0.92 EUR
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        self.assertEqual(transfer.from_currency, self.usd)
        self.assertEqual(transfer.to_currency, self.eur)
        self.assertEqual(transfer.exchange_rate, Decimal('0.9200'))

    def test_transfer_with_voucher_link(self):
        """Test transfer linked to voucher"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-VCH-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='completed',
            approval_status='approved',
            voucher=self.voucher,
            created_by=self.user
        )

        self.assertIsNotNone(transfer.voucher)
        self.assertEqual(transfer.voucher, self.voucher)

    def test_transfer_without_voucher(self):
        """Test transfer can be created without voucher (optional)"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-NOVCH-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        self.assertIsNone(transfer.voucher)

    def test_transfer_str_representation(self):
        """Test string representation of transfer"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-STR-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('7500.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        str_repr = str(transfer)
        self.assertIn("TRF-STR-001", str_repr)

    def test_transfer_ordering(self):
        """Test default ordering by transfer_date descending"""
        from accounting.models import BankTransfer
        
        transfer1 = BankTransfer.objects.create(
            transfer_number="TRF-ORD-001",
            transfer_date=datetime.date(2025, 1, 10),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('1000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        transfer2 = BankTransfer.objects.create(
            transfer_number="TRF-ORD-002",
            transfer_date=datetime.date(2025, 1, 20),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('2000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        transfers = list(BankTransfer.objects.all())
        # Should be ordered by transfer_date descending (newest first)
        self.assertEqual(transfers[0].transfer_number, "TRF-ORD-002")
        self.assertEqual(transfers[1].transfer_number, "TRF-ORD-001")

    def test_transfer_amount_positive(self):
        """Test that transfer amount must be positive"""
        from accounting.models import BankTransfer
        
        # This should work
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-POS-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('100.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )
        self.assertGreater(transfer.amount, 0)

    def test_transfer_meta_verbose_names(self):
        """Test model meta verbose names"""
        from accounting.models import BankTransfer
        
        self.assertEqual(BankTransfer._meta.verbose_name, "Bank Transfer")
        self.assertEqual(BankTransfer._meta.verbose_name_plural, "Bank Transfers")

    def test_transfer_audit_trail(self):
        """Test audit trail fields (created_by, created_at, updated_at)"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-AUD-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('5000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        self.assertIsNotNone(transfer.created_at)
        self.assertIsNotNone(transfer.updated_at)
        self.assertEqual(transfer.created_by, self.user)

    def test_transfer_status_transition_pending_to_completed(self):
        """Test status transition from pending to completed"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-TRANS-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('3000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='approved',
            created_by=self.user
        )

        # Transition to completed
        transfer.status = 'completed'
        transfer.save()

        transfer.refresh_from_db()
        self.assertEqual(transfer.status, 'completed')

    def test_transfer_status_transition_pending_to_failed(self):
        """Test status transition from pending to failed"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-TRANS-002",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('3000.00'),
            from_currency=self.usd,
            to_currency=self.usd,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='approved',
            created_by=self.user
        )

        # Transition to failed
        transfer.status = 'failed'
        transfer.save()

        transfer.refresh_from_db()
        self.assertEqual(transfer.status, 'failed')

    def test_calculated_converted_amount(self):
        """Test calculated converted amount property"""
        from accounting.models import BankTransfer
        
        transfer = BankTransfer.objects.create(
            transfer_number="TRF-CALC-001",
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.bank_account_usd,
            to_bank=self.bank_account_eur,
            amount=Decimal('10000.00'),
            from_currency=self.usd,
            to_currency=self.eur,
            exchange_rate=Decimal('0.9200'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )

        # Converted amount should be amount * exchange_rate
        expected_converted = Decimal('10000.00') * Decimal('0.9200')
        self.assertEqual(transfer.converted_amount, expected_converted)
