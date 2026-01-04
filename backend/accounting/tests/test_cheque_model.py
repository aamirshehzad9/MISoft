"""
Unit Tests for Cheque Model
Task 2.2.1: Create Cheque Model
Module 2.2: Cheque Management System

Tests the Cheque model for complete cheque lifecycle management.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from accounting.models import AccountV2, VoucherV2, CurrencyV2
from partners.models import BusinessPartner
import datetime

User = get_user_model()


class ChequeModelTestCase(TestCase):
    """Test suite for Cheque Model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        self.currency = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )

        # Bank Account
        self.bank_account = AccountV2.objects.create(
            name="Test Bank Account",
            code="1001",
            account_type="asset",
            account_group="current_asset",
            is_active=True
        )

        # Business Partner (Payee)
        self.payee = BusinessPartner.objects.create(
            name="Test Vendor",
            email="vendor@test.com"
        )

        # Voucher for linking
        self.voucher = VoucherV2.objects.create(
            voucher_number="VCH-001",
            voucher_type="BPV",
            voucher_date=datetime.date(2025, 1, 15),
            total_amount=Decimal('5000.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user
        )

    def test_create_cheque_basic(self):
        """Test creating a basic cheque"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            status='issued',
            voucher=self.voucher,
            created_by=self.user
        )

        self.assertIsNotNone(cheque)
        self.assertEqual(cheque.cheque_number, "CHK-001")
        self.assertEqual(cheque.amount, Decimal('5000.00'))
        self.assertEqual(cheque.status, 'issued')
        self.assertEqual(cheque.bank_account, self.bank_account)
        self.assertEqual(cheque.payee, self.payee)
        self.assertFalse(cheque.is_post_dated)

    def test_cheque_number_unique(self):
        """Test that cheque number must be unique"""
        from accounting.models import Cheque
        
        Cheque.objects.create(
            cheque_number="CHK-UNIQUE",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('1000.00'),
            status='issued',
            created_by=self.user
        )

        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            Cheque.objects.create(
                cheque_number="CHK-UNIQUE",
                cheque_date=datetime.date(2025, 1, 16),
                bank_account=self.bank_account,
                payee=self.payee,
                amount=Decimal('2000.00'),
                status='issued',
                created_by=self.user
            )

    def test_cheque_status_choices(self):
        """Test all cheque status choices"""
        from accounting.models import Cheque
        
        # Test issued status
        cheque_issued = Cheque.objects.create(
            cheque_number="CHK-ISSUED-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('1000.00'),
            status='issued',
            created_by=self.user
        )
        self.assertEqual(cheque_issued.status, 'issued')
        
        # Test cleared status (requires clearance_date)
        cheque_cleared = Cheque.objects.create(
            cheque_number="CHK-CLEARED-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('1000.00'),
            status='cleared',
            clearance_date=datetime.date(2025, 1, 20),
            created_by=self.user
        )
        self.assertEqual(cheque_cleared.status, 'cleared')
        
        # Test cancelled status (requires cancelled_date)
        cheque_cancelled = Cheque.objects.create(
            cheque_number="CHK-CANCELLED-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('1000.00'),
            status='cancelled',
            cancelled_date=datetime.date(2025, 1, 16),
            created_by=self.user
        )
        self.assertEqual(cheque_cancelled.status, 'cancelled')
        
        # Test bounced status
        cheque_bounced = Cheque.objects.create(
            cheque_number="CHK-BOUNCED-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('1000.00'),
            status='bounced',
            created_by=self.user
        )
        self.assertEqual(cheque_bounced.status, 'bounced')

    def test_post_dated_cheque(self):
        """Test post-dated cheque creation"""
        from accounting.models import Cheque
        
        future_date = datetime.date.today() + datetime.timedelta(days=30)
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-PDC-001",
            cheque_date=future_date,
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('10000.00'),
            status='issued',
            is_post_dated=True,
            created_by=self.user
        )

        self.assertTrue(cheque.is_post_dated)
        self.assertEqual(cheque.cheque_date, future_date)
        self.assertEqual(cheque.status, 'issued')

    def test_cheque_clearance(self):
        """Test cheque clearance with clearance date"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-CLR-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('3000.00'),
            status='issued',
            created_by=self.user
        )

        # Clear the cheque
        cheque.status = 'cleared'
        cheque.clearance_date = datetime.date(2025, 1, 20)
        cheque.save()

        self.assertEqual(cheque.status, 'cleared')
        self.assertIsNotNone(cheque.clearance_date)
        self.assertEqual(cheque.clearance_date, datetime.date(2025, 1, 20))

    def test_cheque_cancellation(self):
        """Test cheque cancellation with reason"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-CAN-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('2000.00'),
            status='issued',
            created_by=self.user
        )

        # Cancel the cheque
        cheque.status = 'cancelled'
        cheque.cancelled_date = datetime.date(2025, 1, 18)
        cheque.cancellation_reason = "Payment terms changed"
        cheque.save()

        self.assertEqual(cheque.status, 'cancelled')
        self.assertIsNotNone(cheque.cancelled_date)
        self.assertEqual(cheque.cancellation_reason, "Payment terms changed")

    def test_bounced_cheque(self):
        """Test bounced cheque status"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-BNC-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('15000.00'),
            status='issued',
            created_by=self.user
        )

        # Mark as bounced
        cheque.status = 'bounced'
        cheque.save()

        self.assertEqual(cheque.status, 'bounced')

    def test_cheque_with_voucher_link(self):
        """Test cheque linked to voucher"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-VCH-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            status='issued',
            voucher=self.voucher,
            created_by=self.user
        )

        self.assertIsNotNone(cheque.voucher)
        self.assertEqual(cheque.voucher, self.voucher)
        self.assertEqual(cheque.amount, self.voucher.total_amount)

    def test_cheque_without_voucher(self):
        """Test cheque can be created without voucher (optional)"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-NOVCH-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('1000.00'),
            status='issued',
            created_by=self.user
        )

        self.assertIsNone(cheque.voucher)

    def test_cheque_str_representation(self):
        """Test string representation of cheque"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-STR-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('7500.00'),
            status='issued',
            created_by=self.user
        )

        str_repr = str(cheque)
        self.assertIn("CHK-STR-001", str_repr)

    def test_cheque_ordering(self):
        """Test default ordering by cheque_date descending"""
        from accounting.models import Cheque
        
        cheque1 = Cheque.objects.create(
            cheque_number="CHK-ORD-001",
            cheque_date=datetime.date(2025, 1, 10),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('1000.00'),
            status='issued',
            created_by=self.user
        )

        cheque2 = Cheque.objects.create(
            cheque_number="CHK-ORD-002",
            cheque_date=datetime.date(2025, 1, 20),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('2000.00'),
            status='issued',
            created_by=self.user
        )

        cheques = list(Cheque.objects.all())
        # Should be ordered by cheque_date descending (newest first)
        self.assertEqual(cheques[0].cheque_number, "CHK-ORD-002")
        self.assertEqual(cheques[1].cheque_number, "CHK-ORD-001")

    def test_cheque_amount_positive(self):
        """Test that cheque amount must be positive"""
        from accounting.models import Cheque
        
        # This should work
        cheque = Cheque.objects.create(
            cheque_number="CHK-POS-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('100.00'),
            status='issued',
            created_by=self.user
        )
        self.assertGreater(cheque.amount, 0)

    def test_cheque_meta_verbose_names(self):
        """Test model meta verbose names"""
        from accounting.models import Cheque
        
        self.assertEqual(Cheque._meta.verbose_name, "Cheque")
        self.assertEqual(Cheque._meta.verbose_name_plural, "Cheques")

    def test_cheque_audit_trail(self):
        """Test audit trail fields (created_by, created_at, updated_at)"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-AUD-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            status='issued',
            created_by=self.user
        )

        self.assertIsNotNone(cheque.created_at)
        self.assertIsNotNone(cheque.updated_at)
        self.assertEqual(cheque.created_by, self.user)

    def test_cheque_status_transition_issued_to_cleared(self):
        """Test status transition from issued to cleared"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-TRANS-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('3000.00'),
            status='issued',
            created_by=self.user
        )

        # Transition to cleared
        cheque.status = 'cleared'
        cheque.clearance_date = datetime.date.today()
        cheque.save()

        cheque.refresh_from_db()
        self.assertEqual(cheque.status, 'cleared')

    def test_cheque_status_transition_issued_to_cancelled(self):
        """Test status transition from issued to cancelled"""
        from accounting.models import Cheque
        
        cheque = Cheque.objects.create(
            cheque_number="CHK-TRANS-002",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('3000.00'),
            status='issued',
            created_by=self.user
        )

        # Transition to cancelled
        cheque.status = 'cancelled'
        cheque.cancelled_date = datetime.date.today()
        cheque.cancellation_reason = "Vendor request"
        cheque.save()

        cheque.refresh_from_db()
        self.assertEqual(cheque.status, 'cancelled')
        self.assertIsNotNone(cheque.cancelled_date)
