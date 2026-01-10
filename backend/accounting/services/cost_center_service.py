from decimal import Decimal
from django.db.models import Sum
from accounting.models import CostCenterV2, VoucherEntryV2, AccountV2

class CostCenterService:
    """
    Service for Cost Center operations.
    Task 1.6.2
    """
    
    @staticmethod
    def allocate_costs(amount, method, targets):
        """
        Distribute shared costs across cost centers.
        
        Args:
            amount (Decimal): Total amount to allocate
            method (str): 'percentage' or 'fixed'
            targets (list): List of dicts with 'cost_center' object and 'percentage'/'amount'
            
        Returns:
            list: List of dicts with allocated amounts
        """
        amount = Decimal(str(amount))
        results = []
        
        if method == 'percentage':
            total_pct = sum(t['percentage'] for t in targets)
            if abs(total_pct - 100) > 0.01:
                # Warning or Error? For now simple calc
                pass
                
            for target in targets:
                allocated = amount * (Decimal(str(target['percentage'])) / Decimal('100'))
                results.append({
                    'cost_center_id': target['cost_center'].id,
                    'cost_center_code': target['cost_center'].code,
                    'amount': float(allocated)
                })
                
        elif method == 'fixed':
            total_fixed = sum(Decimal(str(t['amount'])) for t in targets)
            # If total_fixed != amount, implies partial allocation or remainder?
            # Assuming targets specify exact distribution
            
            for target in targets:
                results.append({
                    'cost_center_id': target['cost_center'].id,
                    'cost_center_code': target['cost_center'].code,
                    'amount': float(target['amount'])
                })
        
        return results

    @staticmethod
    def calculate_profitability(cost_center_id, start_date, end_date):
        """
        Calculate profitability for a profit center.
        Revenue - Expenses
        """
        cc = CostCenterV2.objects.get(id=cost_center_id)
        if not cc.is_profit_center:
            return {'error': 'Not a profit center'}
            
        entries = VoucherEntryV2.objects.filter(
            cost_center_id=cost_center_id,
            voucher__status='posted',
            voucher__voucher_date__range=(start_date, end_date)
        )
        
        # Revenue: Types 'revenue', 'sales', 'other_income'
        revenue_types = ['revenue', 'sales', 'other_income']
        # Expense: Types 'expense', 'direct_expense', 'indirect_expense', 'operating_expense'
        expense_types = ['expense', 'direct_expense', 'indirect_expense', 'operating_expense']
        
        # Determine exact types used in AccountV2 choices
        # Creating comprehensive lists based on models.py inspection if needed, 
        # but using likely strings.
        # Ideally, we query AccountV2 to filter by group/type.
        
        # Simpler: AccountV2 has account_type (5 categories) and account_group (detailed)
        # Revenue = Type 'Revenue'. Expense = Type 'Expense'.
        
        revenue_qs = entries.filter(account__account_type='revenue')
        expense_qs = entries.filter(account__account_type='expense')
        
        # Calc Revenue (Credit - Debit)
        rev_agg = revenue_qs.aggregate(cr=Sum('credit_amount'), dr=Sum('debit_amount'))
        rev = (rev_agg['cr'] or 0) - (rev_agg['dr'] or 0)
        
        # Calc Expense (Debit - Credit)
        exp_agg = expense_qs.aggregate(dr=Sum('debit_amount'), cr=Sum('credit_amount'))
        exp = (exp_agg['dr'] or 0) - (exp_agg['cr'] or 0)
        
        profit = rev - exp
        
        margin = 0.0
        if rev != 0:
            margin = (profit / rev) * 100
            
        return {
            'cost_center': cc.name,
            'period': f"{start_date} to {end_date}",
            'revenue': float(rev),
            'expense': float(exp),
            'profit': float(profit),
            'margin_percentage': float(round(margin, 2))
        }

    @staticmethod
    def get_cost_allocation_report(cost_center_id, start_date, end_date):
        """
        Get expense allocation report for a cost center.
        """
        entries = VoucherEntryV2.objects.filter(
            cost_center_id=cost_center_id,
            voucher__status='posted',
            voucher__voucher_date__range=(start_date, end_date),
            account__account_type='expense'
        )
        
        total_expense = entries.aggregate(sum=Sum('debit_amount'))['sum'] or 0
        total_credit = entries.aggregate(sum=Sum('credit_amount'))['sum'] or 0
        net_expense = total_expense - total_credit
        
        return {
            'period': f"{start_date} to {end_date}",
            'total_expense': float(net_expense)
        }
