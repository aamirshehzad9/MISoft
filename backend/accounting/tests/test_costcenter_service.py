from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from accounting.models import CostCenterV2, VoucherV2, VoucherEntryV2, AccountV2, FiscalYear, CurrencyV2
from accounting.services.cost_center_service import CostCenterService

class CostCenterServiceTestCase(TestCase):
    def setUp(self):
        # Setup Data
        self.cc_it = CostCenterV2.objects.create(name="IT", code="IT01", is_profit_center=False)
        self.cc_sales = CostCenterV2.objects.create(name="Sales", code="SL01", is_profit_center=True)
        
        self.revenue_acc = AccountV2.objects.create(name="Sales Rev", code="4001", account_type="revenue")
        self.expense_acc = AccountV2.objects.create(name="Office Exp", code="6001", account_type="expense")
        self.currency = CurrencyV2.objects.create(currency_code="USD", currency_name="US Dollar", symbol="$")
        
        # Voucher for Profitability
        self.voucher = VoucherV2.objects.create(
            voucher_number="V001", 
            voucher_type="SI", 
            voucher_date="2025-01-01", 
            total_amount=Decimal('1000.00'),
            status='posted',
            currency=self.currency
        )
        
        self.voucher_exp = VoucherV2.objects.create(
            voucher_number="V002", 
            voucher_type="BPV", 
            voucher_date="2025-01-02", 
            total_amount=Decimal('500.00'),
            status='posted',
            currency=self.currency
        )

    def test_allocate_costs_percentage(self):
        """Test allocating costs by percentage"""
        targets = [
            {'cost_center': self.cc_it, 'percentage': 60},
            {'cost_center': self.cc_sales, 'percentage': 40}
        ]
        
        allocations = CostCenterService.allocate_costs(
            amount=Decimal('1000.00'),
            method='percentage',
            targets=targets
        )
        
        self.assertEqual(len(allocations), 2)
        self.assertEqual(allocations[0]['amount'], 600.00)
        self.assertEqual(allocations[0]['cost_center_code'], 'IT01')
        self.assertEqual(allocations[1]['amount'], 400.00)

    def test_allocate_costs_fixed(self):
        """Test allocating costs by fixed amount"""
        targets = [
            {'cost_center': self.cc_it, 'amount': 300.00},
            {'cost_center': self.cc_sales, 'amount': 700.00}
        ]
        
        allocations = CostCenterService.allocate_costs(
            amount=Decimal('1000.00'),
            method='fixed',
            targets=targets
        )
        
        self.assertEqual(allocations[0]['amount'], 300.00)
        self.assertEqual(allocations[1]['amount'], 700.00)

    def test_calculate_profitability(self):
        """Test profitability for profit center"""
        # Add Revenue (Credit)
        VoucherEntryV2.objects.create(
            voucher=self.voucher,
            account=self.revenue_acc,
            cost_center=self.cc_sales,
            credit_amount=Decimal('1000.00'),
            debit_amount=0
        )
        
        # Add Expense (Debit)
        VoucherEntryV2.objects.create(
            voucher=self.voucher_exp,
            account=self.expense_acc,
            cost_center=self.cc_sales,
            debit_amount=Decimal('400.00'),
            credit_amount=0
        )
        
        report = CostCenterService.calculate_profitability(
            cost_center_id=self.cc_sales.id,
            start_date="2025-01-01",
            end_date="2025-01-31"
        )
        
        self.assertEqual(report['revenue'], 1000.00)
        self.assertEqual(report['expense'], 400.00)
        self.assertEqual(report['profit'], 600.00)
        self.assertEqual(report['margin_percentage'], 60.0)
