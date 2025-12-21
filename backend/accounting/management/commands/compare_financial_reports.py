"""
Management command to compare financial reports between Legacy and V2

Usage:
    python manage.py compare_financial_reports [--report-type {trial_balance,ledger}]

This command generates and compares:
1. Trial Balance (Legacy vs V2)
2. General Ledger (Legacy vs V2)
"""

from django.core.management.base import BaseCommand
from django.db.models import Sum, Q
from accounting.models import (
    ChartOfAccounts, AccountV2, JournalEntryLine, VoucherEntryV2
)
from decimal import Decimal

class Command(BaseCommand):
    help = 'Compare financial reports between Legacy and V2'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report-type',
            type=str,
            default='trial_balance',
            choices=['trial_balance', 'ledger'],
            help='Type of report to compare',
        )

    def handle(self, *args, **options):
        self.report_type = options['report_type']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS(f'FINANCIAL REPORT COMPARISON: {self.report_type.upper()}'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        if self.report_type == 'trial_balance':
            self.compare_trial_balance()
        elif self.report_type == 'ledger':
            self.compare_ledgers()

    def compare_trial_balance(self):
        """Compare Trial Balance"""
        self.stdout.write('\n📊 Comparing Trial Balance...')
        
        mismatches = []
        
        # Get all legacy accounts
        legacy_accounts = ChartOfAccounts.objects.filter(is_header=False)
        
        self.stdout.write(f"{'Account':<40} {'Legacy Balance':<20} {'V2 Balance':<20} {'Status':<10}")
        self.stdout.write('-' * 90)
        
        total_legacy = Decimal('0.00')
        total_v2 = Decimal('0.00')
        
        for legacy_acc in legacy_accounts:
            # Calculate Legacy Balance
            # Asset/Expense: Dr - Cr
            # Liability/Equity/Revenue: Cr - Dr
            
            debits = legacy_acc.journal_lines.aggregate(Sum('debit_amount'))['debit_amount__sum'] or 0
            credits = legacy_acc.journal_lines.aggregate(Sum('credit_amount'))['credit_amount__sum'] or 0
            
            # Simplified: Just check net movement for comparison, sign doesn't matter as long as logic is consistent
            # But let's try to be accurate to accounting types
            if legacy_acc.account_type.type_category in ['asset', 'expense']:
                legacy_bal = legacy_acc.opening_balance + (debits - credits)
            else:
                legacy_bal = legacy_acc.opening_balance + (credits - debits)
            
            # Get V2 Account
            try:
                v2_acc = AccountV2.objects.get(code=legacy_acc.account_code)
                v2_bal = v2_acc.current_balance
            except AccountV2.DoesNotExist:
                v2_bal = Decimal('0.00')
                mismatches.append(f"Missing V2 Account: {legacy_acc.account_code}")
            
            # Compare
            diff = abs(legacy_bal - v2_bal)
            match = diff < Decimal('0.01')
            status = "✅" if match else "❌"
            
            if not match:
                mismatches.append(f"Balance mismatch for {legacy_acc.account_code}: Legacy={legacy_bal}, V2={v2_bal}")
            
            self.stdout.write(f"{legacy_acc.account_name[:38]:<40} {str(legacy_bal):<20} {str(v2_bal):<20} {status}")
            
            total_legacy += legacy_bal
            total_v2 += v2_bal
            
        self.stdout.write('-' * 90)
        self.stdout.write(f"{'TOTAL':<40} {str(total_legacy):<20} {str(total_v2):<20}")
        
        if mismatches:
            self.stdout.write(self.style.ERROR('\n❌ TRIAL BALANCE MISMATCH FOUND'))
            for m in mismatches:
                self.stdout.write(self.style.ERROR(f"   - {m}"))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ TRIAL BALANCE MATCHED'))

    def compare_ledgers(self):
        """Compare General Ledgers (Transaction level)"""
        self.stdout.write('\n📚 Comparing General Ledgers...')
        
        # This is expensive, so we'll check aggregate debits/credits per account
        
        mismatches = []
        
        legacy_accounts = ChartOfAccounts.objects.filter(is_header=False)
        
        self.stdout.write(f"{'Account':<30} {'Legacy Dr/Cr':<25} {'V2 Dr/Cr':<25} {'Status':<10}")
        self.stdout.write('-' * 90)
        
        for legacy_acc in legacy_accounts:
            # Legacy Totals
            leg_dr = legacy_acc.journal_lines.aggregate(Sum('debit_amount'))['debit_amount__sum'] or 0
            leg_cr = legacy_acc.journal_lines.aggregate(Sum('credit_amount'))['credit_amount__sum'] or 0
            
            # V2 Totals
            try:
                v2_acc = AccountV2.objects.get(code=legacy_acc.account_code)
                v2_dr = v2_acc.voucher_entries_v2.aggregate(Sum('debit_amount'))['debit_amount__sum'] or 0
                v2_cr = v2_acc.voucher_entries_v2.aggregate(Sum('credit_amount'))['credit_amount__sum'] or 0
            except AccountV2.DoesNotExist:
                v2_dr = 0
                v2_cr = 0
            
            # Compare
            dr_match = abs(leg_dr - v2_dr) < Decimal('0.01')
            cr_match = abs(leg_cr - v2_cr) < Decimal('0.01')
            
            match = dr_match and cr_match
            status = "✅" if match else "❌"
            
            if not match:
                mismatches.append(f"{legacy_acc.account_code}: Dr {leg_dr}!={v2_dr} or Cr {leg_cr}!={v2_cr}")
            
            leg_str = f"{leg_dr}/{leg_cr}"
            v2_str = f"{v2_dr}/{v2_cr}"
            
            self.stdout.write(f"{legacy_acc.account_name[:28]:<30} {leg_str:<25} {v2_str:<25} {status}")
            
        if mismatches:
            self.stdout.write(self.style.ERROR('\n❌ LEDGER MISMATCH FOUND'))
            for m in mismatches:
                self.stdout.write(self.style.ERROR(f"   - {m}"))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ LEDGER MATCHED'))
