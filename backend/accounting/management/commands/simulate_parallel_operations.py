"""
Management command to simulate parallel operations (Legacy + V2)

Usage:
    python manage.py simulate_parallel_operations --iterations 5

This command:
1. Generates a random Legacy transaction (Invoice/Payment).
2. Migrates it to V2 immediately.
3. Recalculates V2 balances.
4. Verifies Trial Balance parity.
5. Repeats for N iterations.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from accounting.models import Invoice, Payment, AccountV2, ChartOfAccounts, JournalEntry, PaymentAllocation, InvoiceItem, JournalEntryLine
from decimal import Decimal
import random
import time

class Command(BaseCommand):
    help = 'Simulate parallel operations and verify parity'

    def add_arguments(self, parser):
        parser.add_argument('--iterations', type=int, default=5, help='Number of simulation cycles')
        parser.add_argument('--reset', action='store_true', help='Reset all data before starting')

    def handle(self, *args, **options):
        iterations = options['iterations']
        
        if options['reset']:
            self.stdout.write(self.style.WARNING('🗑️  RESETTING SYSTEM...'))
            # 1. Rollback V2
            call_command('rollback_migration', confirm=True, verbosity=0)
            
            # 2. Clear Legacy Data
            PaymentAllocation.objects.all().delete()
            InvoiceItem.objects.all().delete()
            Payment.objects.all().delete()
            Invoice.objects.all().delete()
            JournalEntryLine.objects.all().delete()
            JournalEntry.objects.all().delete()
            
            # 3. Populate Base Data
            self.stdout.write('   📝 Populating base transactions...')
            call_command('populate_sample_transactions', verbosity=0)
            
            # 4. Base Migrations
            self.stdout.write('   🚀 Running base migrations...')
            call_command('migrate_accounts', verbosity=0)
            call_command('migrate_taxes', verbosity=0)
            call_command('migrate_transactions', verbosity=0)
            
            self.stdout.write(self.style.SUCCESS('✅ System Reset Complete'))

        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS(f'🚀 STARTING PARALLEL OPERATION SIMULATION ({iterations} cycles)'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        for i in range(1, iterations + 1):
            self.stdout.write(f"\n🔄 Cycle {i}/{iterations}...")
            
            # 1. Generate Legacy Data
            # We'll use populate_sample_invoices but modify it to create just ONE transaction if possible,
            # or just call it and let it create a batch. A batch is fine.
            # Actually, let's just call populate_sample_invoices without clearing.
            # It creates 5 sales, 3 purchases, 2 payments.
            
            self.stdout.write("   📝 Generating Legacy Transactions...")
            call_command('populate_sample_invoices', random_ids=True)
            
            # 2. Migrate
            self.stdout.write("   🚀 Migrating to V2...")
            # We need to run all migrations to catch everything
            call_command('migrate_invoices', verbosity=0)
            call_command('migrate_transactions', verbosity=0)
            
            # 3. Recalculate
            self.stdout.write("   🧮 Recalculating Balances...")
            call_command('recalculate_balances', verbosity=0)
            
            # 4. Verify
            self.stdout.write("   🔍 Verifying Parity...")
            try:
                self.verify_parity()
                self.stdout.write(self.style.SUCCESS("   ✅ Parity Confirmed"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ PARITY CHECK FAILED: {str(e)}"))
                # Stop on failure
                return

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('✅ SIMULATION COMPLETED SUCCESSFULLY'))
        self.stdout.write('=' * 80 + '\n')

    def verify_parity(self):
        """Check total trial balance match"""
        legacy_total = Decimal('0.00')
        v2_total = Decimal('0.00')
        
        # Legacy Total
        # We can sum up all accounts opening balance + net movement
        for acc in ChartOfAccounts.objects.filter(is_header=False):
            debits = acc.journal_lines.aggregate(debit=models.Sum('debit_amount'))['debit'] or 0
            credits = acc.journal_lines.aggregate(credit=models.Sum('credit_amount'))['credit'] or 0
            
            if acc.account_type.type_category in ['asset', 'expense']:
                legacy_total += acc.opening_balance + (debits - credits)
            else:
                legacy_total += acc.opening_balance + (credits - debits)
                
        # V2 Total
        v2_total = AccountV2.objects.aggregate(total=models.Sum('current_balance'))['total'] or 0
        
        # Compare
        # Note: Trial balance total should be 0 if we sum debits and credits correctly (Dr - Cr).
        # But here I summed absolute balances.
        # Let's use the compare_financial_reports logic but simplified.
        
        # Actually, let's just call compare_financial_reports and capture output?
        # No, that's hard to parse.
        # Let's just check if any account mismatches.
        
        mismatches = []
        for legacy_acc in ChartOfAccounts.objects.filter(is_header=False):
            debits = legacy_acc.journal_lines.aggregate(debit=models.Sum('debit_amount'))['debit'] or 0
            credits = legacy_acc.journal_lines.aggregate(credit=models.Sum('credit_amount'))['credit'] or 0
            
            if legacy_acc.account_type.type_category in ['asset', 'expense']:
                legacy_bal = legacy_acc.opening_balance + (debits - credits)
            else:
                legacy_bal = legacy_acc.opening_balance + (credits - debits)
            
            try:
                v2_acc = AccountV2.objects.get(code=legacy_acc.account_code)
                v2_bal = v2_acc.current_balance
            except AccountV2.DoesNotExist:
                v2_bal = Decimal('0.00')
            
            if legacy_acc.account_code == '1013':
                self.stdout.write(f"   DEBUG: Bank (1013) JEs: {legacy_acc.journal_lines.count()}")
                for line in legacy_acc.journal_lines.all():
                    self.stdout.write(f"      - {line.journal_entry.entry_date} | {line.description} | Dr: {line.debit_amount} | Cr: {line.credit_amount}")
                self.stdout.write(f"   DEBUG: Bank Dr: {debits}, Cr: {credits}")
                self.stdout.write(f"   DEBUG: Bank Op: {legacy_acc.opening_balance}")
                self.stdout.write(f"   DEBUG: Bank Calc: {legacy_bal}")
                
                # Debug specific missing JE
                try:
                    missing_je = JournalEntry.objects.filter(entry_number__startswith='RCPT-R-').last()
                    if missing_je:
                        self.stdout.write(f"   DEBUG: Found JE {missing_je.entry_number}")
                        for line in missing_je.lines.all():
                            self.stdout.write(f"      - Line: {line.account.account_code} | {line.debit_amount}/{line.credit_amount}")
                    else:
                        self.stdout.write("   DEBUG: No RCPT-R- found")
                except Exception as e:
                    self.stdout.write(f"   DEBUG: Error inspecting JE: {e}")

            if abs(legacy_bal - v2_bal) > Decimal('0.01'):
                mismatches.append(f"{legacy_acc.account_code}: Legacy={legacy_bal}, V2={v2_bal}")
        
        if mismatches:
            raise Exception(f"Found {len(mismatches)} mismatches: {', '.join(mismatches[:3])}...")

from django.db import models
