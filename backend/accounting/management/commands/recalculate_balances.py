"""
Management command to recalculate AccountV2 balances

Usage:
    python manage.py recalculate_balances

This command:
1. Resets all AccountV2 current_balances to their opening_balance.
2. Iterates through all POSTED VoucherEntryV2 records.
3. Updates account balances based on debits and credits.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum
from accounting.models import AccountV2, VoucherEntryV2

class Command(BaseCommand):
    help = 'Recalculate AccountV2 balances from vouchers'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('RECALCULATING ACCOUNT BALANCES'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        with transaction.atomic():
            # 1. Reset Balances
            self.stdout.write('\n🔄 Step 1: Resetting balances...')
            accounts = AccountV2.objects.all()
            for acc in accounts:
                acc.current_balance = acc.opening_balance
                acc.save()
            self.stdout.write(f"   Reset {accounts.count()} accounts to opening balance")
            
            # 2. Calculate Net Movement
            self.stdout.write('\n🧮 Step 2: Calculating movements...')
            
            # We can do this efficiently by aggregating VoucherEntryV2
            # Group by Account
            
            entries = VoucherEntryV2.objects.filter(voucher__status='posted').values('account').annotate(
                total_debit=Sum('debit_amount'),
                total_credit=Sum('credit_amount')
            )
            
            count = 0
            for entry in entries:
                account_id = entry['account']
                total_debit = entry['total_debit'] or 0
                total_credit = entry['total_credit'] or 0
                
                try:
                    account = AccountV2.objects.get(id=account_id)
                    
                    if account.account_type in ['asset', 'expense']:
                        # Dr increases, Cr decreases
                        net_change = total_debit - total_credit
                    else:
                        # Cr increases, Dr decreases
                        net_change = total_credit - total_debit
                    
                    account.current_balance += net_change
                    account.save()
                    count += 1
                    
                except AccountV2.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"   ❌ Account {account_id} not found"))
            
            self.stdout.write(f"   Updated balances for {count} accounts")
        
        self.stdout.write(self.style.SUCCESS('\n✅ RECALCULATION COMPLETE'))
        self.stdout.write('=' * 80 + '\n')
