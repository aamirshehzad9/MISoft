"""
Unit Tests for Cheque Service
Task 2.2.2: Cheque Service
Module 2.2: Cheque Management System

Tests the ChequeService class for complete cheque lifecycle management.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import AccountV2, VoucherV2, VoucherEntryV2, CurrencyV2, Cheque
from accounting.services.cheque_service import ChequeService
from partners.models import BusinessPartner
import datetime
from io import BytesIO

User = get_user_model()


class ChequeServiceTestCase(TestCase):
    """Test suite for Cheque Service"""

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

        # Expense Account
        self.expense_account = AccountV2.objects.create(
            name="Expenses",
            code="5001",
            account_type="expense",
            account_group="operating_expense",
            is_active=True
        )

        # Business Partner (Payee)
        self.payee = BusinessPartner.objects.create(
            name="Test Vendor",
            email="vendor@test.com",
            is_vendor=True
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
        
        # Add voucher entries
        VoucherEntryV2.objects.create(
            voucher=self.voucher,
            account=self.bank_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('5000.00')
        )
        VoucherEntryV2.objects.create(
            voucher=self.voucher,
            account=self.expense_account,
            debit_amount=Decimal('5000.00'),
            credit_amount=Decimal('0.00')
        )

    def test_issue_cheque_basic(self):
        """Test basic cheque issuance"""
        cheque = ChequeService.issue_cheque(
            cheque_number="CHK-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=self.voucher,
            user=self.user
        )

        self.assertIsNotNone(cheque)
        self.assertEqual(cheque.cheque_number, "CHK-001")
        self.assertEqual(cheque.status, 'issued')
        self.assertEqual(cheque.amount, Decimal('5000.00'))
        self.assertEqual(cheque.bank_account, self.bank_account)
        self.assertEqual(cheque.payee, self.payee)
        self.assertEqual(cheque.voucher, self.voucher)
        self.assertFalse(cheque.is_post_dated)

    def test_issue_post_dated_cheque(self):
        """Test issuing a post-dated cheque"""
        future_date = datetime.date.today() + datetime.timedelta(days=30)
        
        cheque = ChequeService.issue_cheque(
            cheque_number="CHK-PDC-001",
            cheque_date=future_date,
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('10000.00'),
            voucher=None,
            user=self.user,
            is_post_dated=True
        )

        self.assertTrue(cheque.is_post_dated)
        self.assertEqual(cheque.cheque_date, future_date)
        self.assertEqual(cheque.status, 'issued')

    def test_issue_cheque_without_voucher(self):
        """Test issuing cheque without voucher link"""
        cheque = ChequeService.issue_cheque(
            cheque_number="CHK-NOVCH-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('3000.00'),
            voucher=None,
            user=self.user
        )

        self.assertIsNone(cheque.voucher)
        self.assertEqual(cheque.status, 'issued')

    def test_clear_cheque(self):
        """Test clearing a cheque"""
        # First issue a cheque
        cheque = ChequeService.issue_cheque(
            cheque_number="CHK-CLR-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=self.voucher,
            user=self.user
        )

        # Clear the cheque
        clearance_date = datetime.date(2025, 1, 20)
        cleared_cheque = ChequeService.clear_cheque(
            cheque=cheque,
            clearance_date=clearance_date
        )

        self.assertEqual(cleared_cheque.status, 'cleared')
        self.assertEqual(cleared_cheque.clearance_date, clearance_date)

    def test_clear_cheque_invalid_status(self):
        """Test that only issued cheques can be cleared"""
        # Create a cancelled cheque
        cheque = Cheque.objects.create(
            cheque_number="CHK-CAN-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            status='cancelled',
            cancelled_date=datetime.date(2025, 1, 16),
            created_by=self.user
        )

        # Try to clear it
        with self.assertRaises(ValueError):
            ChequeService.clear_cheque(
                cheque=cheque,
                clearance_date=datetime.date(2025, 1, 20)
            )

    def test_cancel_cheque(self):
        """Test cancelling a cheque"""
        # First issue a cheque
        cheque = ChequeService.issue_cheque(
            cheque_number="CHK-CAN-002",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=self.voucher,
            user=self.user
        )

        # Cancel the cheque
        cancellation_date = datetime.date(2025, 1, 18)
        cancellation_reason = "Payment terms changed"
        
        cancelled_cheque = ChequeService.cancel_cheque(
            cheque=cheque,
            cancelled_date=cancellation_date,
            cancellation_reason=cancellation_reason
        )

        self.assertEqual(cancelled_cheque.status, 'cancelled')
        self.assertEqual(cancelled_cheque.cancelled_date, cancellation_date)
        self.assertEqual(cancelled_cheque.cancellation_reason, cancellation_reason)

    def test_cancel_cheque_invalid_status(self):
        """Test that only issued cheques can be cancelled"""
        # Create a cleared cheque
        cheque = Cheque.objects.create(
            cheque_number="CHK-CLR-002",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            status='cleared',
            clearance_date=datetime.date(2025, 1, 20),
            created_by=self.user
        )

        # Try to cancel it
        with self.assertRaises(ValueError):
            ChequeService.cancel_cheque(
                cheque=cheque,
                cancelled_date=datetime.date(2025, 1, 22),
                cancellation_reason="Test"
            )

    def test_cancel_cheque_requires_reason(self):
        """Test that cancellation requires a reason"""
        cheque = ChequeService.issue_cheque(
            cheque_number="CHK-CAN-003",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=None,
            user=self.user
        )

        # Try to cancel without reason
        with self.assertRaises(ValueError):
            ChequeService.cancel_cheque(
                cheque=cheque,
                cancelled_date=datetime.date(2025, 1, 18),
                cancellation_reason=""
            )

    def test_print_cheque_pdf(self):
        """Test PDF generation for cheque"""
        cheque = ChequeService.issue_cheque(
            cheque_number="CHK-PDF-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=self.voucher,
            user=self.user
        )

        # Generate PDF
        pdf_buffer = ChequeService.print_cheque(cheque)

        self.assertIsNotNone(pdf_buffer)
        self.assertIsInstance(pdf_buffer, BytesIO)
        
        # Check that PDF has content
        pdf_content = pdf_buffer.getvalue()
        self.assertGreater(len(pdf_content), 0)
        
        # Check PDF header (PDF files start with %PDF)
        self.assertTrue(pdf_content.startswith(b'%PDF'))

    def test_get_post_dated_cheques(self):
        """Test retrieving post-dated cheques"""
        # Create some post-dated cheques
        future_date1 = datetime.date.today() + datetime.timedelta(days=15)
        future_date2 = datetime.date.today() + datetime.timedelta(days=30)
        
        cheque1 = ChequeService.issue_cheque(
            cheque_number="CHK-PDC-001",
            cheque_date=future_date1,
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=None,
            user=self.user,
            is_post_dated=True
        )

        cheque2 = ChequeService.issue_cheque(
            cheque_number="CHK-PDC-002",
            cheque_date=future_date2,
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('7000.00'),
            voucher=None,
            user=self.user,
            is_post_dated=True
        )

        # Get post-dated cheques
        post_dated_cheques = ChequeService.get_post_dated_cheques()

        self.assertEqual(len(post_dated_cheques), 2)
        self.assertIn(cheque1, post_dated_cheques)
        self.assertIn(cheque2, post_dated_cheques)

    def test_get_post_dated_cheques_due_soon(self):
        """Test retrieving post-dated cheques due within specified days"""
        # Create post-dated cheques with different dates
        future_date_soon = datetime.date.today() + datetime.timedelta(days=5)
        future_date_later = datetime.date.today() + datetime.timedelta(days=20)
        
        cheque_soon = ChequeService.issue_cheque(
            cheque_number="CHK-PDC-SOON",
            cheque_date=future_date_soon,
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=None,
            user=self.user,
            is_post_dated=True
        )

        cheque_later = ChequeService.issue_cheque(
            cheque_number="CHK-PDC-LATER",
            cheque_date=future_date_later,
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('7000.00'),
            voucher=None,
            user=self.user,
            is_post_dated=True
        )

        # Get cheques due within 7 days
        cheques_due_soon = ChequeService.get_post_dated_cheques_due_soon(days=7)

        self.assertEqual(len(cheques_due_soon), 1)
        self.assertIn(cheque_soon, cheques_due_soon)
        self.assertNotIn(cheque_later, cheques_due_soon)

    def test_get_cheques_by_status(self):
        """Test retrieving cheques by status"""
        # Create cheques with different statuses
        issued_cheque = ChequeService.issue_cheque(
            cheque_number="CHK-ISS-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=None,
            user=self.user
        )

        cleared_cheque = Cheque.objects.create(
            cheque_number="CHK-CLR-003",
            cheque_date=datetime.date(2025, 1, 10),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('3000.00'),
            status='cleared',
            clearance_date=datetime.date(2025, 1, 15),
            created_by=self.user
        )

        # Get issued cheques
        issued_cheques = ChequeService.get_cheques_by_status('issued')
        self.assertIn(issued_cheque, issued_cheques)
        self.assertNotIn(cleared_cheque, issued_cheques)

        # Get cleared cheques
        cleared_cheques = ChequeService.get_cheques_by_status('cleared')
        self.assertIn(cleared_cheque, cleared_cheques)
        self.assertNotIn(issued_cheque, cleared_cheques)

    def test_issue_cheque_duplicate_number(self):
        """Test that duplicate cheque numbers are not allowed"""
        ChequeService.issue_cheque(
            cheque_number="CHK-DUP-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('5000.00'),
            voucher=None,
            user=self.user
        )

        # Try to issue with same number
        with self.assertRaises(Exception):  # IntegrityError
            ChequeService.issue_cheque(
                cheque_number="CHK-DUP-001",
                cheque_date=datetime.date(2025, 1, 16),
                bank_account=self.bank_account,
                payee=self.payee,
                amount=Decimal('3000.00'),
                voucher=None,
                user=self.user
            )
