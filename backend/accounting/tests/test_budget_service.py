from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import Budget, BudgetLine, AccountV2, FiscalYear, VoucherV2, VoucherEntryV2
from accounting.services.budget_service import BudgetService

User = get_user_model()

class BudgetServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Fiscal Years
        self.fy_2024 = FiscalYear.objects.create(
            name="FY2024",
            start_date="2024-01-01",
            end_date="2024-12-31",
            is_closed=True
        )
        self.fy_2025 = FiscalYear.objects.create(
            name="FY2025",
            start_date="2025-01-01",
            end_date="2025-12-31",
            is_closed=False
        )
        
        # Account
        self.account = AccountV2.objects.create(
            name="Travel Expenses",
            code="6001",
            account_type="expense"
        )
        
        # Budget 2024 (Source for copy)
        self.budget_2024 = Budget.objects.create(
            name="IT Budget 2024",
            fiscal_year=self.fy_2024,
            status='approved',
            created_by=self.user
        )
        BudgetLine.objects.create(
            budget=self.budget_2024,
            account=self.account,
            monthly_allocations={"1": 1000, "2": 1000},
            total_amount=Decimal('12000.00')
        )

    def test_create_budget(self):
        """Test creating a new budget via service"""
        budget = BudgetService.create_budget(
            name="Marketing Budget 2025",
            fiscal_year=self.fy_2025,
            user=self.user,
            lines_data=[
                {
                    'account_id': self.account.id,
                    'monthly_allocations': {"1": 2000, "2": 2000},
                    'total_amount': 24000
                }
            ]
        )
        self.assertEqual(budget.name, "Marketing Budget 2025")
        self.assertEqual(budget.lines.count(), 1)
        self.assertEqual(budget.lines.first().total_amount, 24000)

    def test_copy_from_previous_year(self):
        """Test copying budget from previous year"""
        new_budget = BudgetService.copy_from_previous_year(
            source_budget_id=self.budget_2024.id,
            target_fiscal_year=self.fy_2025,
            new_name="IT Budget 2025 (Copy)",
            user=self.user,
            adjustment_percentage=10.0 # 10% increase
        )
        
        self.assertEqual(new_budget.name, "IT Budget 2025 (Copy)")
        self.assertEqual(new_budget.fiscal_year, self.fy_2025)
        
        line = new_budget.lines.first()
        # Original 12000 + 10% = 13200
        self.assertEqual(line.total_amount, Decimal('13200.00')) 

    def test_calculate_variance(self):
        """Test variance calculation against actuals (VoucherV2)"""
        # Create Budget 2025
        budget = Budget.objects.create(
            name="Variance Test 2025", 
            fiscal_year=self.fy_2025,
            status='active'
        )
        BudgetLine.objects.create(
            budget=budget,
            account=self.account,
            monthly_allocations={"1": 1000}, # Jan
            total_amount=Decimal('1000.00')
        )
        
        # Create Actual (VoucherV2) in Jan 2025
        voucher = VoucherV2.objects.create(
            voucher_number="PV001",
            voucher_type="BPV",
            voucher_date="2025-01-15",
            total_amount=Decimal('800.00'),
            status='posted'
        )
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.account,
            debit_amount=Decimal('800.00'), # Actual Expense
            credit_amount=0
        )
        
        # Calculate
        variance_report = BudgetService.calculate_variance(budget.id)
        
        # Validate
        line_report = next(r for r in variance_report if r['account_code'] == '6001')
        self.assertEqual(line_report['budget_amount'], 1000.00)
        self.assertEqual(line_report['actual_amount'], 800.00)
        self.assertEqual(line_report['variance'], 200.00) 
        self.assertEqual(line_report['variance_percentage'], 20.0)

    def test_check_budget_availability(self):
        """Test budget check before expense"""
        # Budget line: 1000
        budget = Budget.objects.create(name="Check 2025", fiscal_year=self.fy_2025, status='active')
        BudgetLine.objects.create(
            budget=budget,
            account=self.account,
            monthly_allocations={"1": 1000},
            total_amount=Decimal('1000.00')
        )
        
        # Check 500 (Available)
        result = BudgetService.check_budget_availability(
            account_id=self.account.id,
            fiscal_year=self.fy_2025,
            amount=500
        )
        self.assertTrue(result['available'])
        
        # Check 1500 (Over budget)
        result = BudgetService.check_budget_availability(
            account_id=self.account.id,
            fiscal_year=self.fy_2025,
            amount=1500
        )
        self.assertFalse(result['available'])
        self.assertIn("Over budget", result['warning'])
