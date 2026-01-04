"""
Unit Tests for BRS Reports
Task 2.1.3: BRS Report
Module 2.1: Bank Reconciliation System

Tests the report generation methods for Bank Reconciliation Statement,
Outstanding Cheques Report, and Deposits in Transit Report.

IFRS Compliance: IAS 7 (Statement of Cash Flows)
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import (
    AccountV2, BankStatement, BankStatementLine, BankReconciliation,
    VoucherV2, VoucherEntryV2, CurrencyV2
)
from accounting.services.bank_reconciliation_service import BankReconciliationService
import datetime

User = get_user_model()


class BRSReportTestCase(TestCase):
    """Test suite for Bank Reconciliation Statement Reports"""

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

        # Other Accounts
        self.sales_account = AccountV2.objects.create(
            name="Sales",
            code="4001",
            account_type="revenue",
            account_group="sales",
            is_active=True
        )

        self.expense_account = AccountV2.objects.create(
            name="Expenses",
            code="5001",
            account_type="expense",
            account_group="operating_expense",
            is_active=True
        )

    def test_generate_brs_report_basic(self):
        """Test basic Bank Reconciliation Statement generation"""
        # Create reconciliation
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('10000.00'),
            ledger_balance=Decimal('9500.00'),
            difference=Decimal('500.00'),
            reconciled_by=self.user,
            status='COMPLETED'
        )

        # Create some outstanding payments (checks issued but not cleared)
        voucher1 = VoucherV2.objects.create(
            voucher_number="CHK-001",
            voucher_type="BPV",
            voucher_date=datetime.date(2025, 1, 15),
            total_amount=Decimal('300.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user
        )
        VoucherEntryV2.objects.create(
            voucher=voucher1,
            account=self.bank_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('300.00')  # Payment (reduces bank)
        )

        voucher2 = VoucherV2.objects.create(
            voucher_number="CHK-002",
            voucher_type="BPV",
            voucher_date=datetime.date(2025, 1, 20),
            total_amount=Decimal('200.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user
        )
        VoucherEntryV2.objects.create(
            voucher=voucher2,
            account=self.bank_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('200.00')  # Payment (reduces bank)
        )

        # Generate BRS Report
        report = BankReconciliationService.generate_brs_report(reconciliation)

        # Assertions
        self.assertIsNotNone(report)
        self.assertIn('reconciliation_date', report)
        self.assertIn('bank_account', report)
        self.assertIn('statement_balance', report)
        self.assertIn('ledger_balance', report)
        self.assertIn('outstanding_payments', report)
        self.assertIn('deposits_in_transit', report)
        self.assertIn('adjusted_bank_balance', report)
        self.assertIn('difference', report)

        # Verify calculations
        self.assertEqual(report['statement_balance'], Decimal('10000.00'))
        self.assertEqual(report['ledger_balance'], Decimal('9500.00'))
        self.assertEqual(report['outstanding_payments'], Decimal('500.00'))  # 300 + 200
        self.assertEqual(report['deposits_in_transit'], Decimal('0.00'))

        # Adjusted Bank Balance = Statement Balance - Outstanding Payments + Deposits in Transit
        expected_adjusted = Decimal('10000.00') - Decimal('500.00') + Decimal('0.00')
        self.assertEqual(report['adjusted_bank_balance'], expected_adjusted)

        # Difference = Adjusted Bank Balance - Ledger Balance
        expected_difference = expected_adjusted - Decimal('9500.00')
        self.assertEqual(report['difference'], expected_difference)

    def test_generate_brs_report_with_deposits_in_transit(self):
        """Test BRS report with deposits in transit"""
        # Create reconciliation
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('8000.00'),
            ledger_balance=Decimal('9000.00'),
            difference=Decimal('-1000.00'),
            reconciled_by=self.user,
            status='COMPLETED'
        )

        # Create deposits in transit (receipts recorded but not yet in bank)
        voucher = VoucherV2.objects.create(
            voucher_number="REC-001",
            voucher_type="BRV",
            voucher_date=datetime.date(2025, 1, 30),
            total_amount=Decimal('1000.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user
        )
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.bank_account,
            debit_amount=Decimal('1000.00'),  # Receipt (increases bank)
            credit_amount=Decimal('0.00')
        )

        # Generate BRS Report
        report = BankReconciliationService.generate_brs_report(reconciliation)

        # Verify
        self.assertEqual(report['deposits_in_transit'], Decimal('1000.00'))
        self.assertEqual(report['outstanding_payments'], Decimal('0.00'))

        # Adjusted Bank Balance = 8000 - 0 + 1000 = 9000
        self.assertEqual(report['adjusted_bank_balance'], Decimal('9000.00'))
        # Difference = 9000 - 9000 = 0 (balanced!)
        self.assertEqual(report['difference'], Decimal('0.00'))

    def test_generate_brs_report_balanced(self):
        """Test BRS report when perfectly balanced"""
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('5000.00'),
            ledger_balance=Decimal('5000.00'),
            difference=Decimal('0.00'),
            reconciled_by=self.user,
            status='COMPLETED'
        )

        report = BankReconciliationService.generate_brs_report(reconciliation)

        self.assertEqual(report['difference'], Decimal('0.00'))
        self.assertTrue(report['is_balanced'])

    def test_generate_outstanding_cheques_report(self):
        """Test Outstanding Cheques Report generation"""
        # Create reconciliation
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('10000.00'),
            ledger_balance=Decimal('9000.00'),
            difference=Decimal('1000.00'),
            reconciled_by=self.user
        )

        # Create outstanding payments
        voucher1 = VoucherV2.objects.create(
            voucher_number="CHK-101",
            voucher_type="BPV",
            voucher_date=datetime.date(2025, 1, 10),
            total_amount=Decimal('600.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user,
            narration="Payment to Vendor A"
        )
        entry1 = VoucherEntryV2.objects.create(
            voucher=voucher1,
            account=self.bank_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('600.00')
        )

        voucher2 = VoucherV2.objects.create(
            voucher_number="CHK-102",
            voucher_type="BPV",
            voucher_date=datetime.date(2025, 1, 25),
            total_amount=Decimal('400.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user,
            narration="Payment to Vendor B"
        )
        entry2 = VoucherEntryV2.objects.create(
            voucher=voucher2,
            account=self.bank_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('400.00')
        )

        # Generate Outstanding Cheques Report
        report = BankReconciliationService.generate_outstanding_cheques_report(reconciliation)

        # Assertions
        self.assertIsNotNone(report)
        self.assertIn('reconciliation_date', report)
        self.assertIn('bank_account', report)
        self.assertIn('outstanding_cheques', report)
        self.assertIn('total_outstanding', report)

        # Verify data
        self.assertEqual(len(report['outstanding_cheques']), 2)
        self.assertEqual(report['total_outstanding'], Decimal('1000.00'))

        # Verify individual cheque details
        cheques = report['outstanding_cheques']
        self.assertEqual(cheques[0]['voucher_number'], "CHK-101")
        self.assertEqual(cheques[0]['amount'], Decimal('600.00'))
        self.assertEqual(cheques[0]['voucher_date'], datetime.date(2025, 1, 10))
        self.assertIn('narration', cheques[0])

        self.assertEqual(cheques[1]['voucher_number'], "CHK-102")
        self.assertEqual(cheques[1]['amount'], Decimal('400.00'))

    def test_generate_deposits_in_transit_report(self):
        """Test Deposits in Transit Report generation"""
        # Create reconciliation
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('7000.00'),
            ledger_balance=Decimal('9000.00'),
            difference=Decimal('-2000.00'),
            reconciled_by=self.user
        )

        # Create deposits in transit
        voucher1 = VoucherV2.objects.create(
            voucher_number="DEP-201",
            voucher_type="BRV",
            voucher_date=datetime.date(2025, 1, 28),
            total_amount=Decimal('1200.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user,
            narration="Customer Payment - Invoice 001"
        )
        entry1 = VoucherEntryV2.objects.create(
            voucher=voucher1,
            account=self.bank_account,
            debit_amount=Decimal('1200.00'),
            credit_amount=Decimal('0.00')
        )

        voucher2 = VoucherV2.objects.create(
            voucher_number="DEP-202",
            voucher_type="BRV",
            voucher_date=datetime.date(2025, 1, 30),
            total_amount=Decimal('800.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user,
            narration="Customer Payment - Invoice 002"
        )
        entry2 = VoucherEntryV2.objects.create(
            voucher=voucher2,
            account=self.bank_account,
            debit_amount=Decimal('800.00'),
            credit_amount=Decimal('0.00')
        )

        # Generate Deposits in Transit Report
        report = BankReconciliationService.generate_deposits_in_transit_report(reconciliation)

        # Assertions
        self.assertIsNotNone(report)
        self.assertIn('reconciliation_date', report)
        self.assertIn('bank_account', report)
        self.assertIn('deposits_in_transit', report)
        self.assertIn('total_deposits', report)

        # Verify data
        self.assertEqual(len(report['deposits_in_transit']), 2)
        self.assertEqual(report['total_deposits'], Decimal('2000.00'))

        # Verify individual deposit details
        deposits = report['deposits_in_transit']
        self.assertEqual(deposits[0]['voucher_number'], "DEP-201")
        self.assertEqual(deposits[0]['amount'], Decimal('1200.00'))
        self.assertEqual(deposits[0]['voucher_date'], datetime.date(2025, 1, 28))
        self.assertIn('narration', deposits[0])

        self.assertEqual(deposits[1]['voucher_number'], "DEP-202")
        self.assertEqual(deposits[1]['amount'], Decimal('800.00'))

    def test_outstanding_cheques_report_empty(self):
        """Test Outstanding Cheques Report when no outstanding cheques"""
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('5000.00'),
            ledger_balance=Decimal('5000.00'),
            difference=Decimal('0.00'),
            reconciled_by=self.user
        )

        report = BankReconciliationService.generate_outstanding_cheques_report(reconciliation)

        self.assertEqual(len(report['outstanding_cheques']), 0)
        self.assertEqual(report['total_outstanding'], Decimal('0.00'))

    def test_deposits_in_transit_report_empty(self):
        """Test Deposits in Transit Report when no deposits in transit"""
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('5000.00'),
            ledger_balance=Decimal('5000.00'),
            difference=Decimal('0.00'),
            reconciled_by=self.user
        )

        report = BankReconciliationService.generate_deposits_in_transit_report(reconciliation)

        self.assertEqual(len(report['deposits_in_transit']), 0)
        self.assertEqual(report['total_deposits'], Decimal('0.00'))

    def test_brs_report_includes_detailed_items(self):
        """Test that BRS report includes detailed lists of outstanding items"""
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('10000.00'),
            ledger_balance=Decimal('9300.00'),
            difference=Decimal('700.00'),
            reconciled_by=self.user
        )

        # Create outstanding payment
        voucher1 = VoucherV2.objects.create(
            voucher_number="CHK-999",
            voucher_type="BPV",
            voucher_date=datetime.date(2025, 1, 29),
            total_amount=Decimal('500.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user
        )
        VoucherEntryV2.objects.create(
            voucher=voucher1,
            account=self.bank_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('500.00')
        )

        # Create deposit in transit
        voucher2 = VoucherV2.objects.create(
            voucher_number="DEP-999",
            voucher_type="BRV",
            voucher_date=datetime.date(2025, 1, 30),
            total_amount=Decimal('200.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user
        )
        VoucherEntryV2.objects.create(
            voucher=voucher2,
            account=self.bank_account,
            debit_amount=Decimal('200.00'),
            credit_amount=Decimal('0.00')
        )

        # Generate BRS Report
        report = BankReconciliationService.generate_brs_report(reconciliation)

        # Verify detailed items are included
        self.assertIn('outstanding_cheques_detail', report)
        self.assertIn('deposits_in_transit_detail', report)

        self.assertEqual(len(report['outstanding_cheques_detail']), 1)
        self.assertEqual(len(report['deposits_in_transit_detail']), 1)

        # Verify amounts match
        self.assertEqual(report['outstanding_payments'], Decimal('500.00'))
        self.assertEqual(report['deposits_in_transit'], Decimal('200.00'))
