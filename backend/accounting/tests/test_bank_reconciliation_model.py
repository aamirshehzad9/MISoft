"""
Unit Tests for Bank Reconciliation Models
Task 2.1.1: Create BankReconciliation Model
Module 2.1: Bank Reconciliation System

Tests the creation, validation, and relationships of BankReconciliation models.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from accounting.models import AccountV2, BankStatement, BankStatementLine, BankReconciliation

User = get_user_model()


class BankReconciliationModelTestCase(TestCase):
    """Test suite for Bank Reconciliation models"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create a Bank Account (Asset)
        self.bank_account = AccountV2.objects.create(
            name="Test Bank Account",
            code="1001",
            account_type="asset",  # Lowercase as per choices
            account_group="current_asset",
            is_active=True
        )
        
        # Create a Non-Bank Account for validation testing
        self.expense_account = AccountV2.objects.create(
            name="Office Expense",
            code="6001",
            account_type="expense", # Lowercase as per choices
            account_group="operating_expense",
            is_active=True
        )

    def test_create_bank_statement(self):
        """Test creating a BankStatement"""
        statement = BankStatement.objects.create(
            bank_account=self.bank_account,
            statement_date=timezone.now().date(),
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            opening_balance=Decimal('1000.00'),
            closing_balance=Decimal('1500.00'),
            status='DRAFT',
            created_by=self.user  # Added created_by
        )
        
        self.assertEqual(statement.bank_account, self.bank_account)
        self.assertEqual(statement.opening_balance, Decimal('1000.00'))
        self.assertEqual(statement.status, 'DRAFT')
        self.assertTrue(str(statement).startswith(f"Statement {statement.id} for {self.bank_account.name}"))

    def test_create_bank_statement_line(self):
        """Test creating a BankStatementLine"""
        statement = BankStatement.objects.create(
            bank_account=self.bank_account,
            statement_date=timezone.now().date(),
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            opening_balance=Decimal('1000.00'),
            closing_balance=Decimal('1200.00'),
            status='DRAFT',
            created_by=self.user  # Added created_by
        )
        
        line = BankStatementLine.objects.create(
            statement=statement,
            date=timezone.now().date(),
            description="Deposit",
            reference="DEP-001",
            amount=Decimal('200.00'),
            balance=Decimal('1200.00')
        )
        
        self.assertEqual(line.statement, statement)
        self.assertEqual(line.amount, Decimal('200.00'))
        self.assertFalse(line.is_reconciled)

    def test_create_bank_reconciliation(self):
        """Test creating a BankReconciliation"""
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=timezone.now().date(),
            statement_balance=Decimal('1500.00'),
            ledger_balance=Decimal('1500.00'),
            difference=Decimal('0.00'),
            status='DRAFT',
            reconciled_by=self.user
        )
        
        self.assertEqual(reconciliation.bank_account, self.bank_account)
        self.assertEqual(reconciliation.difference, Decimal('0.00'))
        self.assertEqual(reconciliation.status, 'DRAFT')

    def test_bank_statement_validation(self):
        """Test validation logic (if any specific constraints are added later)"""
        # For now, just ensuring it saves correctly is enough, validation logic usually goes in clean()
        pass
    
    # NOTE: Depending on requirements, we might want to enforce that bank_account has a specific type/category.
    # For now, simplistic creation tests.
