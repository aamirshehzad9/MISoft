from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from accounting.models import Budget, BudgetLine, AccountV2, FiscalYear
from decimal import Decimal
import json

User = get_user_model()

class BudgetModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create dependencies
        self.fiscal_year = FiscalYear.objects.create(
            name="FY2025",
            start_date="2025-01-01",
            end_date="2025-12-31",
            is_closed=False
        )
        
        self.account = AccountV2.objects.create(
            name="Travel Expenses",
            code="6001",
            account_type="EXPENSE"
        )
        
        # Create Budget
        self.budget = Budget.objects.create(
            name="IT Department Budget 2025",
            fiscal_year=self.fiscal_year,
            status='draft',
            created_by=self.user
        )

    def test_budget_creation(self):
        """Test basic budget property"""
        self.assertEqual(self.budget.name, "IT Department Budget 2025")
        self.assertEqual(self.budget.status, 'draft')
        self.assertEqual(str(self.budget), "IT Department Budget 2025")

    def test_budget_line_creation(self):
        """Test budget line creation with allocations"""
        allocations = {str(i): 1000.00 for i in range(1, 13)} # 12 months
        total = sum(allocations.values())
        
        line = BudgetLine.objects.create(
            budget=self.budget,
            account=self.account,
            monthly_allocations=allocations,
            total_amount=Decimal(total),
            notes="Estimated travel costs"
        )
        
        self.assertEqual(line.total_amount, 12000.00)
        self.assertEqual(len(line.monthly_allocations), 12)
        
    def test_budget_approval(self):
        """Test status change and approver"""
        self.budget.status = 'approved'
        self.budget.approved_by = self.user
        self.budget.save()
        
        updated = Budget.objects.get(id=self.budget.id)
        self.assertEqual(updated.status, 'approved')
        self.assertEqual(updated.approved_by, self.user)
