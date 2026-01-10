from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from accounting.models import Budget, BudgetLine, VoucherEntryV2, VoucherV2

class BudgetService:
    """
    Service for managing budgets, variance analysis, and availability checks.
    Task 1.5.2
    """
    
    @staticmethod
    @transaction.atomic
    def create_budget(name, fiscal_year, user, lines_data, department=None, cost_center=None):
        """
        Create a new budget with lines.
        """
        budget = Budget.objects.create(
            name=name,
            fiscal_year=fiscal_year,
            department=department,
            cost_center=cost_center,
            created_by=user,
            status='draft'
        )
        
        for line in lines_data:
            BudgetLine.objects.create(
                budget=budget,
                account_id=line['account_id'],
                monthly_allocations=line.get('monthly_allocations', {}),
                total_amount=Decimal(str(line['total_amount'])),
                notes=line.get('notes', '')
            )
            
        return budget

    @staticmethod
    @transaction.atomic
    def copy_from_previous_year(source_budget_id, target_fiscal_year, new_name, user, adjustment_percentage=0.0):
        """
        Copy budget from a previous year/version with optional adjustment.
        """
        source_budget = Budget.objects.get(id=source_budget_id)
        
        new_budget = Budget.objects.create(
            name=new_name,
            fiscal_year=target_fiscal_year, # Different year
            department=source_budget.department,
            cost_center=source_budget.cost_center,
            created_by=user,
            status='draft'
        )
        
        factor = 1 + (adjustment_percentage / 100.0)
        
        for line in source_budget.lines.all():
            new_allocations = {}
            for month, amount in line.monthly_allocations.items():
                new_allocations[month] = float(Decimal(str(amount)) * Decimal(str(factor)))
            
            new_total = line.total_amount * Decimal(str(factor))
            
            BudgetLine.objects.create(
                budget=new_budget,
                account=line.account,
                monthly_allocations=new_allocations,
                total_amount=new_total,
                notes=f"Copied from {source_budget.name}"
            )
            
        return new_budget

    @staticmethod
    def calculate_variance(budget_id):
        """
        Compare budget vs actuals (VoucherV2).
        Returns list of dicts per account line.
        """
        budget = Budget.objects.get(id=budget_id)
        report = []
        
        # Get start/end date from fiscal year logic or just match lines
        # Assuming we check full fiscal year actuals
        start_date = budget.fiscal_year.start_date
        end_date = budget.fiscal_year.end_date
        
        for line in budget.lines.all():
            # Sum actuals (Debits usually for expenses)
            # Logic: If Expense/Asset -> Limit to Debits - Credits? Or just Net?
            # Variance Analysis usually compares Net Activity.
            # Using VoucherEntryV2
            
            actuals_qs = VoucherEntryV2.objects.filter(
                account=line.account,
                voucher__status='posted',
                voucher__voucher_date__range=(start_date, end_date)
            )
            
            # Simple Net: Debit - Credit (for Expense)
            # If Revenue: Credit - Debit.
            # We check account type
            
            aggregates = actuals_qs.aggregate(
                total_debit=Sum('debit_amount'), 
                total_credit=Sum('credit_amount')
            )
            
            debit = aggregates['total_debit'] or Decimal('0.00')
            credit = aggregates['total_credit'] or Decimal('0.00')
            
            if line.account.account_type in ['asset', 'expense']:
                actual_amount = debit - credit
            else:
                actual_amount = credit - debit
            
            variance = line.total_amount - actual_amount
            if line.total_amount != 0:
                pct = (variance / line.total_amount) * 100
            else:
                pct = 0.0
                
            report.append({
                'account_id': line.account.id,
                'account_code': line.account.code,
                'account_name': line.account.name,
                'budget_amount': float(line.total_amount),
                'actual_amount': float(actual_amount),
                'variance': float(variance),
                'variance_percentage': float(round(pct, 2))
            })
            
        return report

    @staticmethod
    def check_budget_availability(account_id, fiscal_year, amount):
        """
        Check if transaction amount is within budget.
        Used before posting vouchers.
        """
        # Find active budget
        # Warning: Mulitple budgets? Assume one active/approved per FY/Dept
        # For simplicity, finding first approved budget containing the account
        
        budget_line = BudgetLine.objects.filter(
            budget__fiscal_year=fiscal_year,
            budget__status__in=['approved', 'active'],
            account_id=account_id
        ).first()
        
        if not budget_line:
            return {'available': True, 'warning': None} # No budget -> No limit (or strict?) Policy dependant. Default Allow.
            
        budget_amount = budget_line.total_amount
        
        # Calculate Used Amount (Actuals)
        start_date = fiscal_year.start_date
        end_date = fiscal_year.end_date
        
        actuals_qs = VoucherEntryV2.objects.filter(
            account_id=account_id,
            voucher__status='posted',
            voucher__voucher_date__range=(start_date, end_date)
        )
        
        aggregates = actuals_qs.aggregate(
            total_debit=Sum('debit_amount'), 
            total_credit=Sum('credit_amount')
        )
        
        debit = aggregates['total_debit'] or Decimal('0.00')
        credit = aggregates['total_credit'] or Decimal('0.00')
        
        # Account Type Logic
        from accounting.models import AccountV2
        account = AccountV2.objects.get(id=account_id)
        
        if account.account_type in ['asset', 'expense']:
            used = debit - credit
        else:
            used = credit - debit
            
        remaining = budget_amount - used
        
        if Decimal(str(amount)) > remaining:
            return {
                'available': False, 
                'warning': f"Over budget! Remaining: {remaining}, Requested: {amount}",
                'remaining': float(remaining)
            }
            
            
        return {'available': True, 'warning': None, 'remaining': float(remaining)}

    @staticmethod
    def get_budget_utilization(budget_id):
        """
        Calculate total utilization of the budget.
        """
        variance_data = BudgetService.calculate_variance(budget_id)
        
        total_budget = sum(item['budget_amount'] for item in variance_data)
        total_actual = sum(item['actual_amount'] for item in variance_data)
        
        if total_budget != 0:
            pct = (total_actual / total_budget) * 100
        else:
            pct = 0.0
            
        return {
            'total_budget': total_budget,
            'total_actual': total_actual,
            'utilization_percentage': float(round(pct, 2))
        }
