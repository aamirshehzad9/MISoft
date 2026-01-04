"""
Unit Tests for Cheque Reports
Task 2.2.3: Cheque Reports
Module 2.2: Cheque Management System

Tests the report generation methods for Cheque Management System.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import AccountV2, VoucherV2, CurrencyV2, Cheque
from accounting.services.cheque_service import ChequeService
from partners.models import BusinessPartner
import datetime

User = get_user_model()


class ChequeReportsTestCase(TestCase):
    """Test suite for Cheque Reports"""

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
        self.payee1 = BusinessPartner.objects.create(
            name="Vendor A",
            email="vendora@test.com",
            is_vendor=True
        )

        self.payee2 = BusinessPartner.objects.create(
            name="Vendor B",
            email="vendorb@test.com",
            is_vendor=True
        )

        # Create sample cheques with different statuses
        self._create_sample_cheques()

    def _create_sample_cheques(self):
        """Create sample cheques for testing"""
        # Issued cheques
        self.issued_cheque1 = Cheque.objects.create(
            cheque_number="CHK-ISS-001",
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee1,
            amount=Decimal('5000.00'),
            status='issued',
            created_by=self.user
        )

        self.issued_cheque2 = Cheque.objects.create(
            cheque_number="CHK-ISS-002",
            cheque_date=datetime.date(2025, 1, 20),
            bank_account=self.bank_account,
            payee=self.payee2,
            amount=Decimal('3000.00'),
            status='issued',
            created_by=self.user
        )

        # Cleared cheques
        self.cleared_cheque1 = Cheque.objects.create(
            cheque_number="CHK-CLR-001",
            cheque_date=datetime.date(2025, 1, 10),
            bank_account=self.bank_account,
            payee=self.payee1,
            amount=Decimal('2000.00'),
            status='cleared',
            clearance_date=datetime.date(2025, 1, 15),
            created_by=self.user
        )

        self.cleared_cheque2 = Cheque.objects.create(
            cheque_number="CHK-CLR-002",
            cheque_date=datetime.date(2025, 1, 12),
            bank_account=self.bank_account,
            payee=self.payee2,
            amount=Decimal('1500.00'),
            status='cleared',
            clearance_date=datetime.date(2025, 1, 18),
            created_by=self.user
        )

        # Cancelled cheques
        self.cancelled_cheque1 = Cheque.objects.create(
            cheque_number="CHK-CAN-001",
            cheque_date=datetime.date(2025, 1, 8),
            bank_account=self.bank_account,
            payee=self.payee1,
            amount=Decimal('4000.00'),
            status='cancelled',
            cancelled_date=datetime.date(2025, 1, 10),
            cancellation_reason="Payment terms changed",
            created_by=self.user
        )

        self.cancelled_cheque2 = Cheque.objects.create(
            cheque_number="CHK-CAN-002",
            cheque_date=datetime.date(2025, 1, 14),
            bank_account=self.bank_account,
            payee=self.payee2,
            amount=Decimal('2500.00'),
            status='cancelled',
            cancelled_date=datetime.date(2025, 1, 16),
            cancellation_reason="Vendor request",
            created_by=self.user
        )

        # Post-dated cheques
        future_date1 = datetime.date.today() + datetime.timedelta(days=15)
        future_date2 = datetime.date.today() + datetime.timedelta(days=30)

        self.post_dated_cheque1 = Cheque.objects.create(
            cheque_number="CHK-PDC-001",
            cheque_date=future_date1,
            bank_account=self.bank_account,
            payee=self.payee1,
            amount=Decimal('7000.00'),
            status='issued',
            is_post_dated=True,
            created_by=self.user
        )

        self.post_dated_cheque2 = Cheque.objects.create(
            cheque_number="CHK-PDC-002",
            cheque_date=future_date2,
            bank_account=self.bank_account,
            payee=self.payee2,
            amount=Decimal('9000.00'),
            status='issued',
            is_post_dated=True,
            created_by=self.user
        )

    def test_generate_issued_cheques_register(self):
        """Test Issued Cheques Register generation"""
        report = ChequeService.generate_issued_cheques_register()

        self.assertIsNotNone(report)
        self.assertIn('cheques', report)
        self.assertIn('total_amount', report)
        self.assertIn('count', report)

        # Should include issued and post-dated cheques (4 total)
        self.assertEqual(report['count'], 4)
        
        # Verify total amount
        expected_total = (
            Decimal('5000.00') + Decimal('3000.00') +  # issued
            Decimal('7000.00') + Decimal('9000.00')    # post-dated
        )
        self.assertEqual(report['total_amount'], expected_total)

        # Verify cheques are in the list
        cheque_numbers = [c['cheque_number'] for c in report['cheques']]
        self.assertIn("CHK-ISS-001", cheque_numbers)
        self.assertIn("CHK-ISS-002", cheque_numbers)
        self.assertIn("CHK-PDC-001", cheque_numbers)
        self.assertIn("CHK-PDC-002", cheque_numbers)

    def test_generate_issued_cheques_register_with_date_range(self):
        """Test Issued Cheques Register with date filtering"""
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2025, 1, 31)

        report = ChequeService.generate_issued_cheques_register(
            start_date=start_date,
            end_date=end_date
        )

        self.assertIsNotNone(report)
        # Should only include issued cheques within date range (not post-dated)
        self.assertEqual(report['count'], 2)

    def test_generate_cancelled_cheques_register(self):
        """Test Cancelled Cheques Register generation"""
        report = ChequeService.generate_cancelled_cheques_register()

        self.assertIsNotNone(report)
        self.assertIn('cheques', report)
        self.assertIn('total_amount', report)
        self.assertIn('count', report)

        # Should include 2 cancelled cheques
        self.assertEqual(report['count'], 2)

        # Verify total amount
        expected_total = Decimal('4000.00') + Decimal('2500.00')
        self.assertEqual(report['total_amount'], expected_total)

        # Verify cheques are in the list
        cheque_numbers = [c['cheque_number'] for c in report['cheques']]
        self.assertIn("CHK-CAN-001", cheque_numbers)
        self.assertIn("CHK-CAN-002", cheque_numbers)

        # Verify cancellation details are included
        for cheque in report['cheques']:
            self.assertIn('cancellation_reason', cheque)
            self.assertIn('cancelled_date', cheque)

    def test_generate_cancelled_cheques_register_with_date_range(self):
        """Test Cancelled Cheques Register with date filtering"""
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2025, 1, 12)

        report = ChequeService.generate_cancelled_cheques_register(
            start_date=start_date,
            end_date=end_date
        )

        # Should only include CHK-CAN-001 (cancelled on 2025-01-10)
        self.assertEqual(report['count'], 1)

    def test_generate_post_dated_cheques_report(self):
        """Test Post-Dated Cheques Report generation"""
        report = ChequeService.generate_post_dated_cheques_report()

        self.assertIsNotNone(report)
        self.assertIn('cheques', report)
        self.assertIn('total_amount', report)
        self.assertIn('count', report)

        # Should include 2 post-dated cheques
        self.assertEqual(report['count'], 2)

        # Verify total amount
        expected_total = Decimal('7000.00') + Decimal('9000.00')
        self.assertEqual(report['total_amount'], expected_total)

        # Verify cheques are in the list
        cheque_numbers = [c['cheque_number'] for c in report['cheques']]
        self.assertIn("CHK-PDC-001", cheque_numbers)
        self.assertIn("CHK-PDC-002", cheque_numbers)

        # Verify post-dated flag is included
        for cheque in report['cheques']:
            self.assertTrue(cheque['is_post_dated'])

    def test_generate_post_dated_cheques_report_due_soon(self):
        """Test Post-Dated Cheques Report with due_soon filter"""
        report = ChequeService.generate_post_dated_cheques_report(due_within_days=20)

        # Should only include CHK-PDC-001 (due in 15 days)
        self.assertEqual(report['count'], 1)
        self.assertEqual(report['cheques'][0]['cheque_number'], "CHK-PDC-001")

    def test_generate_clearance_status_report(self):
        """Test Cheque Clearance Status Report generation"""
        report = ChequeService.generate_clearance_status_report()

        self.assertIsNotNone(report)
        self.assertIn('issued_cheques', report)
        self.assertIn('cleared_cheques', report)
        self.assertIn('cancelled_cheques', report)
        self.assertIn('summary', report)

        # Verify counts
        summary = report['summary']
        self.assertEqual(summary['total_issued'], 4)  # 2 issued + 2 post-dated
        self.assertEqual(summary['total_cleared'], 2)
        self.assertEqual(summary['total_cancelled'], 2)
        self.assertEqual(summary['total_cheques'], 8)

        # Verify amounts
        self.assertEqual(summary['issued_amount'], Decimal('24000.00'))  # 5000+3000+7000+9000
        self.assertEqual(summary['cleared_amount'], Decimal('3500.00'))   # 2000+1500
        self.assertEqual(summary['cancelled_amount'], Decimal('6500.00')) # 4000+2500

    def test_generate_clearance_status_report_with_date_range(self):
        """Test Clearance Status Report with date filtering"""
        start_date = datetime.date(2025, 1, 1)
        end_date = datetime.date(2025, 1, 15)

        report = ChequeService.generate_clearance_status_report(
            start_date=start_date,
            end_date=end_date
        )

        # Should only include cheques within date range
        summary = report['summary']
        self.assertLess(summary['total_cheques'], 8)

    def test_issued_cheques_register_empty(self):
        """Test Issued Cheques Register when no cheques exist"""
        # Delete all cheques
        Cheque.objects.all().delete()

        report = ChequeService.generate_issued_cheques_register()

        self.assertEqual(report['count'], 0)
        self.assertEqual(report['total_amount'], Decimal('0.00'))
        self.assertEqual(len(report['cheques']), 0)

    def test_cancelled_cheques_register_empty(self):
        """Test Cancelled Cheques Register when no cancelled cheques exist"""
        # Delete all cancelled cheques
        Cheque.objects.filter(status='cancelled').delete()

        report = ChequeService.generate_cancelled_cheques_register()

        self.assertEqual(report['count'], 0)
        self.assertEqual(report['total_amount'], Decimal('0.00'))
        self.assertEqual(len(report['cheques']), 0)

    def test_post_dated_cheques_report_empty(self):
        """Test Post-Dated Cheques Report when no post-dated cheques exist"""
        # Delete all post-dated cheques
        Cheque.objects.filter(is_post_dated=True).delete()

        report = ChequeService.generate_post_dated_cheques_report()

        self.assertEqual(report['count'], 0)
        self.assertEqual(report['total_amount'], Decimal('0.00'))
        self.assertEqual(len(report['cheques']), 0)

    def test_reports_include_required_fields(self):
        """Test that all reports include required fields"""
        # Issued Cheques Register
        issued_report = ChequeService.generate_issued_cheques_register()
        if issued_report['count'] > 0:
            cheque = issued_report['cheques'][0]
            self.assertIn('cheque_number', cheque)
            self.assertIn('cheque_date', cheque)
            self.assertIn('payee_name', cheque)
            self.assertIn('amount', cheque)
            self.assertIn('bank_account_name', cheque)

        # Cancelled Cheques Register
        cancelled_report = ChequeService.generate_cancelled_cheques_register()
        if cancelled_report['count'] > 0:
            cheque = cancelled_report['cheques'][0]
            self.assertIn('cancellation_reason', cheque)
            self.assertIn('cancelled_date', cheque)

        # Post-Dated Cheques Report
        pdc_report = ChequeService.generate_post_dated_cheques_report()
        if pdc_report['count'] > 0:
            cheque = pdc_report['cheques'][0]
            self.assertIn('is_post_dated', cheque)
            self.assertIn('cheque_date', cheque)
