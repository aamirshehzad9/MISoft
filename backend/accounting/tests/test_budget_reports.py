from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import Budget, BudgetLine, AccountV2, FiscalYear, VoucherV2, VoucherEntryV2
from accounting.services.budget_service import BudgetService

User = get_user_model()

class BudgetReportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.fiscal_year = FiscalYear.objects.create(
            name="FY2025",
            start_date="2025-01-01",
            end_date="2025-12-31",
            is_closed=False
        )
        
        self.account = AccountV2.objects.create(
            name="Travel Expenses",
            code="6001",
            account_type="expense"
        )
        
        # Create Budget
        self.budget = Budget.objects.create(
            name="Report Test Budget 2025",
            fiscal_year=self.fiscal_year,
            status='active',
            created_by=self.user
        )
        BudgetLine.objects.create(
            budget=self.budget,
            account=self.account,
            monthly_allocations={"1": 1000},
            total_amount=Decimal('12000.00') # 12 months * 1000 ideally, but simplifed
        )
        
        # Create Actuals
        voucher = VoucherV2.objects.create(
            voucher_number="PV001",
            voucher_type="BPV",
            voucher_date="2025-01-15",
            total_amount=Decimal('5000.00'),
            status='posted'
        )
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.account,
            debit_amount=Decimal('5000.00'),
            credit_amount=0
        )

    def test_budget_vs_actual_report(self):
        """Test budget vs actual report endpoint"""
        # GET /api/accounting/reports/budget/budget-vs-actual/?budget_id=X
        url = reverse('budget-reports-budget-vs-actual')
        response = self.client.get(url, {'budget_id': self.budget.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['budget_amount'], 12000.00)
        self.assertEqual(data[0]['actual_amount'], 5000.00)

    def test_variance_analysis_report(self):
        """Test variance analysis report"""
        # GET /api/accounting/reports/budget/variance-analysis/?budget_id=X
        url = reverse('budget-reports-variance-analysis')
        response = self.client.get(url, {'budget_id': self.budget.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        item = data[0]
        # Variance = 12000 - 5000 = 7000
        self.assertEqual(item['variance'], 7000.00)
        self.assertIn('variance_percentage', item)

    def test_budget_utilization_report(self):
        """Test budget utilization summary"""
        # GET /api/accounting/reports/budget/utilization/?budget_id=X
        url = reverse('budget-reports-utilization')
        response = self.client.get(url, {'budget_id': self.budget.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Utilization % = (5000 / 12000) * 100 = 41.67%
        self.assertAlmostEqual(data['utilization_percentage'], 41.67, places=2)
        self.assertEqual(data['total_budget'], 12000.00)
        self.assertEqual(data['total_actual'], 5000.00)
