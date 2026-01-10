from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import CostCenterV2, VoucherV2, VoucherEntryV2, AccountV2, CurrencyV2

User = get_user_model()

class CostCenterReportTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        
        # Setup Data
        self.cc_sales = CostCenterV2.objects.create(name="Sales", code="SL01", is_profit_center=True)
        self.cc_it = CostCenterV2.objects.create(name="IT", code="IT01", is_profit_center=False)
        
        self.revenue_acc = AccountV2.objects.create(name="Sales Rev", code="4001", account_type="revenue")
        self.expense_acc = AccountV2.objects.create(name="Office Exp", code="6001", account_type="expense")
        self.currency = CurrencyV2.objects.create(currency_code="USD", currency_name="US Dollar", symbol="$")
        
        # Voucher
        self.voucher = VoucherV2.objects.create(
            voucher_number="V001", voucher_type="SI", voucher_date="2025-01-01", 
            total_amount=Decimal('1000.00'), status='posted', currency=self.currency
        )
        
        # Revenue for Sales profit center
        VoucherEntryV2.objects.create(
            voucher=self.voucher, account=self.revenue_acc, cost_center=self.cc_sales,
            credit_amount=Decimal('1000.00'), debit_amount=0
        )
        
        # Expense for IT cost center
        VoucherEntryV2.objects.create(
            voucher=self.voucher, account=self.expense_acc, cost_center=self.cc_it,
            debit_amount=Decimal('200.00'), credit_amount=0
        )

    def test_profit_center_performance(self):
        """Test Profit Center P&L/Performance report"""
        # GET /api/accounting/reports/cost-centers/profitability/
        url = reverse('costcenter-reports-profitability')
        response = self.client.get(url, {
            'cost_center_id': self.cc_sales.id,
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['revenue'], 1000.00)
        self.assertEqual(data['profit'], 1000.00)

    def test_cost_allocation_report(self):
        """Test Cost Allocation / Expense Report"""
        # GET /api/accounting/reports/cost-centers/allocation/
        url = reverse('costcenter-reports-allocation')
        response = self.client.get(url, {
            'cost_center_id': self.cc_it.id,
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        # Should return list of expenses or aggregated expense
        # For this test, let's assume it returns a summary dict
        self.assertEqual(data['total_expense'], 200.00)
