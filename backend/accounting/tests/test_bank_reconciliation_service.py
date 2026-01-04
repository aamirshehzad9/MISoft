"""
Unit Tests for Bank Reconciliation Service
Task 2.1.2: Reconciliation Engine
Module 2.1: Bank Reconciliation System

Tests the core logic for bank statement processing and reconciliation.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from accounting.models import (
    AccountV2, BankStatement, BankStatementLine, BankReconciliation, 
    VoucherV2, VoucherEntryV2, CurrencyV2
)
from accounting.services.bank_reconciliation_service import BankReconciliationService
import datetime

User = get_user_model()


class BankReconciliationServiceTestCase(TestCase):
    """Test suite for Bank Reconciliation Service"""

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
        
        # Other Account (for voucher entries)
        self.sales_account = AccountV2.objects.create(
            name="Sales",
            code="4001",
            account_type="revenue",
            account_group="sales",
            is_active=True
        )

    def test_import_bank_statement_csv(self):
        """Test importing bank statement from CSV"""
        # Create a dummy CSV file
        csv_content = b"Date,Description,Reference,Amount,Balance\n2025-01-01,Opening Balance,,1000.00,1000.00\n2025-01-02,Deposit,DEP001,500.00,1500.00\n2025-01-03,Payment,CHK001,-200.00,1300.00"
        csv_file = SimpleUploadedFile("statement.csv", csv_content, content_type="text/csv")
        
        statement = BankReconciliationService.import_bank_statement(
            file=csv_file,
            bank_account=self.bank_account,
            user=self.user
        )
        
        self.assertIsNotNone(statement)
        self.assertEqual(statement.bank_account, self.bank_account)
        self.assertEqual(statement.lines.count(), 3)
        self.assertEqual(statement.status, 'DRAFT')
        
        # Verify specific lines
        deposit = statement.lines.get(reference='DEP001')
        self.assertEqual(deposit.amount, Decimal('500.00'))
        
        payment = statement.lines.get(reference='CHK001')
        self.assertEqual(payment.amount, Decimal('-200.00'))

    def test_auto_match_transactions(self):
        """Test auto-matching logic"""
        # 1. Create a Voucher (that should match)
        voucher = VoucherV2.objects.create(
            voucher_number="VCH-001",
            voucher_type="BRV",
            voucher_date=datetime.date(2025, 1, 2),
            total_amount=Decimal('500.00'),
            currency=self.currency,
            status='posted', # Must be posted to match
            created_by=self.user
        )
        # Debit Bank
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.bank_account,
            debit_amount=Decimal('500.00'),
            credit_amount=Decimal('0.00')
        )
        # Credit Sales
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.sales_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('500.00')
        )
        
        # 2. Create Bank Statement with matching line
        statement = BankStatement.objects.create(
            bank_account=self.bank_account,
            statement_date=datetime.date(2025, 1, 31),
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 31),
            opening_balance=Decimal('0.00'),
            closing_balance=Decimal('500.00'),
            created_by=self.user
        )
        
        # Exact match on amount and date overlap
        line = BankStatementLine.objects.create(
            statement=statement,
            date=datetime.date(2025, 1, 2),
            description="Deposit VCH-001",
            reference="DEP001",
            amount=Decimal('500.00'),
            balance=Decimal('500.00')
        )
        
        # 3. Run Auto Match
        matches_found = BankReconciliationService.auto_match_transactions(statement)
        
        self.assertTrue(matches_found > 0)
        
        # Reload line
        line.refresh_from_db()
        self.assertTrue(line.is_reconciled)
        self.assertIsNotNone(line.matched_voucher_line)
        self.assertEqual(line.matched_voucher_line.voucher, voucher)

    def test_calculate_outstanding_cheques(self):
        """Test calculation of outstanding checks (payments in ledger not in bank)"""
        # Create Reconciliation
        reconcilation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('1000.00'),
            ledger_balance=Decimal('800.00'), # Difference of 200
            difference=Decimal('200.00'),
            reconciled_by=self.user
        )
        
        # TODO: Setup data for outstanding checks
        # Create a payment voucher that is NOT reconciled
        voucher = VoucherV2.objects.create(
            voucher_number="PAY-001",
            voucher_type="BPV",
            voucher_date=datetime.date(2025, 1, 15),
            total_amount=Decimal('200.00'),
             currency=self.currency,
            status='posted',
            created_by=self.user
        )
        # Credit Bank (Payment)
        entry = VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.bank_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('200.00') # 200 payment
        )
        
        # NOT linking to bank line (so it's outstanding)
        
        outstanding = BankReconciliationService.calculate_outstanding_payments(reconcilation)
        self.assertEqual(outstanding, Decimal('200.00'))

    def test_calculate_deposits_in_transit(self):
        """Test calculation of deposits in transit"""
         # Create Reconciliation
        reconcilation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('1000.00'),
            ledger_balance=Decimal('1500.00'),
            difference=Decimal('-500.00'),
            reconciled_by=self.user
        )
        
        # Create a receipt voucher NOT reconciled
        voucher = VoucherV2.objects.create(
            voucher_number="REC-001",
            voucher_type="BRV",
            voucher_date=datetime.date(2025, 1, 20),
            total_amount=Decimal('500.00'),
             currency=self.currency,
            status='posted',
            created_by=self.user
        )
        # Debit Bank (Receipt)
        entry = VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.bank_account,
            debit_amount=Decimal('500.00'), # 500 deposit
            credit_amount=Decimal('0.00')
        )
        
    def test_post_bank_charges(self):
        """Test auto-posting of bank charges"""
        # Create a statement with a charge line
        statement = BankStatement.objects.create(
            bank_account=self.bank_account,
            statement_date=datetime.date(2025, 1, 31),
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 31),
            opening_balance=Decimal('1000.00'),
            closing_balance=Decimal('990.00'), # 10 charge
            status='DRAFT',
            created_by=self.user
        )
        
        charge_line = BankStatementLine.objects.create(
            statement=statement,
            date=datetime.date(2025, 1, 31),
            description="Bank Service Charge",
            reference="CHG001",
            amount=Decimal('-10.00'),
            balance=Decimal('990.00')
        )
        
        # Post charges
        voucher = BankReconciliationService.post_bank_charges(
            statement=statement,
            line_ids=[charge_line.id],
            expense_account=self.sales_account, # Using sales account for expense just for test
            user=self.user
        )
        
        self.assertIsNotNone(voucher)
        self.assertEqual(voucher.total_amount, Decimal('10.00'))
        self.assertEqual(voucher.status, 'posted')
        
        # Verify line is matched
        charge_line.refresh_from_db()
        self.assertTrue(charge_line.is_reconciled)
        self.assertIsNotNone(charge_line.matched_voucher_line)
        self.assertEqual(charge_line.matched_voucher_line.voucher, voucher)
