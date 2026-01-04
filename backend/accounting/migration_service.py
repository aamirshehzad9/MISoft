"""
Data Migration Service - V1 to V2 Migration
Migrates legacy models to IFRS-compliant V2 models
"""

from django.db import transaction
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import datetime
import logging

from .models import (
    ChartOfAccounts, AccountV2,
    JournalEntry, JournalEntryLine,
    VoucherV2, VoucherEntryV2,
    AccountType
)

User = get_user_model()
logger = logging.getLogger(__name__)


class DataMigrationService:
    """Service to migrate legacy V1 data to V2 IFRS-compliant models"""
    
    def __init__(self, user=None):
        self.user = user or User.objects.filter(is_superuser=True).first()
        self.migration_log = []
        self.errors = []
        
    def log(self, message, level='INFO'):
        """Log migration progress"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.migration_log.append(log_entry)
        
        if level == 'ERROR':
            logger.error(message)
            self.errors.append(message)
        else:
            logger.info(message)
    
    def map_account_type_to_v2(self, legacy_account):
        """Map legacy account type to V2 account type and group"""
        type_mapping = {
            'asset': {
                'account_type': 'asset',
                'account_group': 'current_asset'  # Default, can be refined
            },
            'liability': {
                'account_type': 'liability',
                'account_group': 'current_liability'
            },
            'equity': {
                'account_type': 'equity',
                'account_group': 'capital'
            },
            'revenue': {
                'account_type': 'revenue',
                'account_group': 'sales'
            },
            'expense': {
                'account_type': 'expense',
                'account_group': 'operating_expense'
            }
        }
        
        legacy_type = legacy_account.account_type.type_category
        return type_mapping.get(legacy_type, {
            'account_type': 'asset',
            'account_group': 'other_asset'
        })
    
    @transaction.atomic
    def migrate_accounts(self):
        """Migrate ChartOfAccounts to AccountV2"""
        self.log("=" * 80)
        self.log("Starting Account Migration (ChartOfAccounts → AccountV2)")
        self.log("=" * 80)
        
        legacy_accounts = ChartOfAccounts.objects.all().order_by('account_code')
        total_accounts = legacy_accounts.count()
        
        self.log(f"Found {total_accounts} legacy accounts to migrate")
        
        migrated_count = 0
        skipped_count = 0
        
        for legacy_account in legacy_accounts:
            try:
                # Check if already migrated
                if AccountV2.objects.filter(code=legacy_account.account_code).exists():
                    self.log(f"SKIP: Account {legacy_account.account_code} already exists in V2", 'WARNING')
                    skipped_count += 1
                    continue
                
                # Map account type
                type_mapping = self.map_account_type_to_v2(legacy_account)
                
                # Create V2 account
                account_v2 = AccountV2.objects.create(
                    code=legacy_account.account_code,
                    name=legacy_account.account_name,
                    account_type=type_mapping['account_type'],
                    account_group=type_mapping['account_group'],
                    is_group=legacy_account.is_header,
                    is_active=legacy_account.is_active,
                    allow_direct_posting=not legacy_account.is_header,
                    opening_balance=legacy_account.opening_balance,
                    current_balance=legacy_account.opening_balance,
                    description=legacy_account.description,
                    migrated_from_legacy=legacy_account,
                    created_by=self.user
                )
                
                migrated_count += 1
                self.log(f"✓ Migrated: {legacy_account.account_code} - {legacy_account.account_name}")
                
            except Exception as e:
                self.log(f"ERROR migrating account {legacy_account.account_code}: {str(e)}", 'ERROR')
        
        # Second pass: Map parent relationships
        self.log("\nMapping parent-child relationships...")
        for legacy_account in legacy_accounts:
            if legacy_account.parent_account:
                try:
                    child_v2 = AccountV2.objects.get(code=legacy_account.account_code)
                    parent_v2 = AccountV2.objects.get(code=legacy_account.parent_account.account_code)
                    child_v2.parent = parent_v2
                    child_v2.save()
                    self.log(f"✓ Linked: {child_v2.code} → Parent: {parent_v2.code}")
                except Exception as e:
                    self.log(f"ERROR linking parent for {legacy_account.account_code}: {str(e)}", 'ERROR')
        
        self.log("\n" + "=" * 80)
        self.log(f"Account Migration Complete!")
        self.log(f"Total: {total_accounts} | Migrated: {migrated_count} | Skipped: {skipped_count}")
        self.log("=" * 80)
        
        return {
            'total': total_accounts,
            'migrated': migrated_count,
            'skipped': skipped_count,
            'errors': len(self.errors)
        }
    
    def map_voucher_type(self, entry_type):
        """Map legacy journal entry type to V2 voucher type"""
        type_mapping = {
            'general': 'JE',
            'sales': 'SI',
            'purchase': 'PI',
            'cash_receipt': 'CRV',
            'cash_payment': 'CPV',
            'bank': 'BPV',
        }
        return type_mapping.get(entry_type, 'JE')
    
    @transaction.atomic
    def migrate_journal_entries(self):
        """Migrate JournalEntry to VoucherV2"""
        self.log("\n" + "=" * 80)
        self.log("Starting Journal Entry Migration (JournalEntry → VoucherV2)")
        self.log("=" * 80)
        
        legacy_entries = JournalEntry.objects.all().order_by('entry_date', 'entry_number')
        total_entries = legacy_entries.count()
        
        self.log(f"Found {total_entries} legacy journal entries to migrate")
        
        migrated_count = 0
        skipped_count = 0
        
        for legacy_entry in legacy_entries:
            try:
                # Check if already migrated
                if VoucherV2.objects.filter(voucher_number=legacy_entry.entry_number).exists():
                    self.log(f"SKIP: Entry {legacy_entry.entry_number} already exists in V2", 'WARNING')
                    skipped_count += 1
                    continue
                
                # Calculate total amount (use debit total)
                total_amount = sum(line.debit_amount for line in legacy_entry.lines.all())
                
                # Create V2 voucher
                voucher_v2 = VoucherV2.objects.create(
                    voucher_number=legacy_entry.entry_number,
                    voucher_type=self.map_voucher_type(legacy_entry.entry_type),
                    voucher_date=legacy_entry.entry_date,
                    reference_number=legacy_entry.reference_number,
                    total_amount=total_amount,
                    status='posted' if legacy_entry.status == 'posted' else 'draft',
                    narration=legacy_entry.description,
                    migrated_from_legacy=legacy_entry,
                    created_by=self.user
                )
                
                # Migrate entry lines
                for line in legacy_entry.lines.all():
                    # Find corresponding V2 account
                    try:
                        account_v2 = AccountV2.objects.get(code=line.account.account_code)
                        
                        VoucherEntryV2.objects.create(
                            voucher=voucher_v2,
                            account=account_v2,
                            debit_amount=line.debit_amount,
                            credit_amount=line.credit_amount,
                            description=line.description or legacy_entry.description
                        )
                    except AccountV2.DoesNotExist:
                        self.log(f"ERROR: Account {line.account.account_code} not found in V2", 'ERROR')
                
                migrated_count += 1
                self.log(f"✓ Migrated: {legacy_entry.entry_number} ({legacy_entry.entry_date})")
                
            except Exception as e:
                self.log(f"ERROR migrating entry {legacy_entry.entry_number}: {str(e)}", 'ERROR')
        
        self.log("\n" + "=" * 80)
        self.log(f"Journal Entry Migration Complete!")
        self.log(f"Total: {total_entries} | Migrated: {migrated_count} | Skipped: {skipped_count}")
        self.log("=" * 80)
        
        return {
            'total': total_entries,
            'migrated': migrated_count,
            'skipped': skipped_count,
            'errors': len(self.errors)
        }
    
    def verify_balances(self):
        """Verify that opening balances match between V1 and V2"""
        self.log("\n" + "=" * 80)
        self.log("Verifying Account Balances")
        self.log("=" * 80)
        
        mismatches = []
        
        for legacy_account in ChartOfAccounts.objects.all():
            try:
                v2_account = AccountV2.objects.get(code=legacy_account.account_code)
                
                if legacy_account.opening_balance != v2_account.opening_balance:
                    mismatch = {
                        'code': legacy_account.account_code,
                        'name': legacy_account.account_name,
                        'v1_balance': legacy_account.opening_balance,
                        'v2_balance': v2_account.opening_balance,
                        'difference': v2_account.opening_balance - legacy_account.opening_balance
                    }
                    mismatches.append(mismatch)
                    self.log(
                        f"MISMATCH: {legacy_account.account_code} - "
                        f"V1: {legacy_account.opening_balance}, "
                        f"V2: {v2_account.opening_balance}",
                        'ERROR'
                    )
            except AccountV2.DoesNotExist:
                self.log(f"Account {legacy_account.account_code} not found in V2", 'WARNING')
        
        if not mismatches:
            self.log("✓ All balances match! Migration successful.")
        else:
            self.log(f"✗ Found {len(mismatches)} balance mismatches", 'ERROR')
        
        self.log("=" * 80)
        
        return mismatches
    
    def generate_report(self):
        """Generate migration report"""
        report = "\n".join(self.migration_log)
        
        # Save to file
        filename = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(report)
        
        self.log(f"\nMigration report saved to: {filename}")
        
        return report
    
    def run_full_migration(self):
        """Run complete migration process"""
        self.log("=" * 80)
        self.log("STARTING FULL DATA MIGRATION")
        self.log("=" * 80)
        
        # Step 1: Migrate Accounts
        account_result = self.migrate_accounts()
        
        # Step 2: Migrate Journal Entries
        entry_result = self.migrate_journal_entries()
        
        # Step 3: Verify Balances
        mismatches = self.verify_balances()
        
        # Step 4: Generate Report
        report = self.generate_report()
        
        # Summary
        self.log("\n" + "=" * 80)
        self.log("MIGRATION SUMMARY")
        self.log("=" * 80)
        self.log(f"Accounts Migrated: {account_result['migrated']}/{account_result['total']}")
        self.log(f"Entries Migrated: {entry_result['migrated']}/{entry_result['total']}")
        self.log(f"Balance Mismatches: {len(mismatches)}")
        self.log(f"Total Errors: {len(self.errors)}")
        self.log("=" * 80)
        
        return {
            'accounts': account_result,
            'entries': entry_result,
            'mismatches': mismatches,
            'errors': self.errors,
            'report_file': report
        }
