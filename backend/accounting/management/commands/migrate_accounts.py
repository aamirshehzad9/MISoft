"""
Management command to migrate Chart of Accounts from legacy to V2

Usage:
    python manage.py migrate_accounts [--dry-run] [--batch-size=100]

This command carefully migrates accounts from ChartOfAccounts to AccountV2
while preserving hierarchy, balances, and all relationships.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from decimal import Decimal
from accounting.models import ChartOfAccounts, AccountV2, AccountType
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate Chart of Accounts from legacy to V2 models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without committing changes',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of accounts to migrate in each batch',
        )
        parser.add_argument(
            '--skip-validation',
            action='store_true',
            help='Skip pre-migration validation (not recommended)',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.batch_size = options['batch_size']
        self.skip_validation = options['skip_validation']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Chart of Accounts Migration - Legacy to V2'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be committed\n'))
        
        # Step 1: Pre-migration validation
        if not self.skip_validation:
            self.stdout.write('\n📋 Step 1: Pre-migration validation...')
            if not self.validate_pre_migration():
                raise CommandError('Pre-migration validation failed. Aborting.')
            self.stdout.write(self.style.SUCCESS('✅ Pre-migration validation passed\n'))
        
        # Step 2: Count accounts to migrate
        total_accounts = ChartOfAccounts.objects.count()
        already_migrated = AccountV2.objects.filter(migrated_from_legacy__isnull=False).count()
        
        self.stdout.write(f'\n📊 Migration Statistics:')
        self.stdout.write(f'   Total legacy accounts: {total_accounts}')
        self.stdout.write(f'   Already migrated: {already_migrated}')
        self.stdout.write(f'   Remaining to migrate: {total_accounts - already_migrated}\n')
        
        if total_accounts == 0:
            self.stdout.write(self.style.WARNING('No accounts to migrate.'))
            return
        
        # Step 3: Migrate accounts
        self.stdout.write('\n🔄 Step 2: Migrating accounts...')
        migrated_count = self.migrate_accounts()
        
        # Step 4: Post-migration validation
        if not self.skip_validation:
            self.stdout.write('\n✅ Step 3: Post-migration validation...')
            if not self.validate_post_migration():
                raise CommandError('Post-migration validation failed!')
            self.stdout.write(self.style.SUCCESS('✅ Post-migration validation passed\n'))
        
        # Step 5: Generate report
        self.stdout.write('\n📄 Step 4: Generating migration report...')
        self.generate_report(migrated_count)
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes committed'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ MIGRATION COMPLETE - {migrated_count} accounts migrated'))
        self.stdout.write(self.style.SUCCESS('=' * 80 + '\n'))

    def validate_pre_migration(self):
        """Validate system state before migration"""
        checks_passed = True
        
        # Check 1: Verify legacy data integrity
        self.stdout.write('   Checking legacy data integrity...')
        legacy_accounts = ChartOfAccounts.objects.all()
        for account in legacy_accounts:
            if not account.account_code or not account.account_name:
                self.stdout.write(self.style.ERROR(
                    f'   ❌ Account {account.id} has missing code or name'
                ))
                checks_passed = False
        
        if checks_passed:
            self.stdout.write(self.style.SUCCESS('   ✅ Legacy data integrity OK'))
        
        # Check 2: Check for duplicate codes
        self.stdout.write('   Checking for duplicate account codes...')
        from django.db.models import Count
        duplicates = ChartOfAccounts.objects.values('account_code').annotate(
            count=Count('account_code')
        ).filter(count__gt=1)
        
        if duplicates.exists():
            self.stdout.write(self.style.ERROR(
                f'   ❌ Found {duplicates.count()} duplicate account codes'
            ))
            checks_passed = False
        else:
            self.stdout.write(self.style.SUCCESS('   ✅ No duplicate codes found'))
        
        # Check 3: Verify V2 tables exist
        self.stdout.write('   Checking V2 tables...')
        try:
            AccountV2.objects.count()
            self.stdout.write(self.style.SUCCESS('   ✅ V2 tables accessible'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ V2 tables error: {e}'))
            checks_passed = False
        
        return checks_passed

    def migrate_accounts(self):
        """Migrate accounts from legacy to V2"""
        migrated_count = 0
        
        # Get accounts that haven't been migrated yet
        legacy_accounts = ChartOfAccounts.objects.exclude(
            id__in=AccountV2.objects.filter(
                migrated_from_legacy__isnull=False
            ).values_list('migrated_from_legacy_id', flat=True)
        ).order_by('account_code')
        
        # First pass: Migrate root accounts (no parent)
        root_accounts = legacy_accounts.filter(parent_account__isnull=True)
        self.stdout.write(f'   Migrating {root_accounts.count()} root accounts...')
        
        for account in root_accounts:
            if self.migrate_single_account(account):
                migrated_count += 1
                if migrated_count % 10 == 0:
                    self.stdout.write(f'   Progress: {migrated_count} accounts migrated...')
        
        # Second pass: Migrate child accounts
        child_accounts = legacy_accounts.filter(parent_account__isnull=False)
        self.stdout.write(f'   Migrating {child_accounts.count()} child accounts...')
        
        for account in child_accounts:
            if self.migrate_single_account(account):
                migrated_count += 1
                if migrated_count % 10 == 0:
                    self.stdout.write(f'   Progress: {migrated_count} accounts migrated...')
        
        return migrated_count

    def migrate_single_account(self, legacy_account):
        """Migrate a single account from legacy to V2"""
        try:
            # Check if already migrated
            if AccountV2.objects.filter(migrated_from_legacy=legacy_account).exists():
                return False
            
            # Map account type
            account_type = self.map_account_type(legacy_account)
            account_group = self.map_account_group(legacy_account, account_type)
            
            # Find parent in V2 if exists
            parent_v2 = None
            if legacy_account.parent_account:
                parent_v2 = AccountV2.objects.filter(
                    migrated_from_legacy=legacy_account.parent_account
                ).first()
            
            # Create V2 account
            account_v2_data = {
                'code': legacy_account.account_code,
                'name': legacy_account.account_name,
                'account_type': account_type,
                'account_group': account_group,
                'parent': parent_v2,
                'is_group': legacy_account.is_header,
                'is_active': legacy_account.is_active,
                'allow_direct_posting': not legacy_account.is_header,
                'opening_balance': legacy_account.opening_balance or Decimal('0.00'),
                'current_balance': legacy_account.opening_balance or Decimal('0.00'),
                'description': legacy_account.description or '',
                'migrated_from_legacy': legacy_account,
            }
            
            if not self.dry_run:
                with transaction.atomic():
                    AccountV2.objects.create(**account_v2_data)
            
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'   ❌ Error migrating account {legacy_account.account_code}: {e}'
            ))
            logger.error(f'Error migrating account {legacy_account.id}: {e}')
            return False

    def map_account_type(self, legacy_account):
        """Map legacy account type to V2 account type"""
        if not legacy_account.account_type:
            return 'asset'  # Default
        
        type_category = legacy_account.account_type.type_category.lower()
        
        type_mapping = {
            'asset': 'asset',
            'liability': 'liability',
            'equity': 'equity',
            'revenue': 'revenue',
            'expense': 'expense',
        }
        
        return type_mapping.get(type_category, 'asset')

    def map_account_group(self, legacy_account, account_type):
        """Map to appropriate account group based on type"""
        # Default groups by type
        default_groups = {
            'asset': 'current_asset',
            'liability': 'current_liability',
            'equity': 'capital',
            'revenue': 'sales',
            'expense': 'operating_expense',
        }
        
        return default_groups.get(account_type, 'current_asset')

    def validate_post_migration(self):
        """Validate migration results"""
        checks_passed = True
        
        # Check 1: Count comparison
        self.stdout.write('   Comparing record counts...')
        legacy_count = ChartOfAccounts.objects.count()
        v2_count = AccountV2.objects.filter(migrated_from_legacy__isnull=False).count()
        
        if legacy_count != v2_count:
            self.stdout.write(self.style.WARNING(
                f'   ⚠️  Count mismatch: Legacy={legacy_count}, V2={v2_count}'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'   ✅ Counts match: {legacy_count} accounts'
            ))
        
        # Check 2: Balance verification
        self.stdout.write('   Verifying balances...')
        total_legacy_balance = sum(
            acc.opening_balance or Decimal('0.00')
            for acc in ChartOfAccounts.objects.all()
        )
        total_v2_balance = sum(
            acc.opening_balance
            for acc in AccountV2.objects.filter(migrated_from_legacy__isnull=False)
        )
        
        if abs(total_legacy_balance - total_v2_balance) > Decimal('0.01'):
            self.stdout.write(self.style.ERROR(
                f'   ❌ Balance mismatch: Legacy={total_legacy_balance}, V2={total_v2_balance}'
            ))
            checks_passed = False
        else:
            self.stdout.write(self.style.SUCCESS(
                f'   ✅ Balances match: {total_legacy_balance}'
            ))
        
        # Check 3: Hierarchy verification
        self.stdout.write('   Verifying hierarchy...')
        hierarchy_errors = 0
        for legacy_acc in ChartOfAccounts.objects.filter(parent_account__isnull=False):
            v2_acc = AccountV2.objects.filter(migrated_from_legacy=legacy_acc).first()
            if v2_acc and legacy_acc.parent_account:
                expected_parent = AccountV2.objects.filter(
                    migrated_from_legacy=legacy_acc.parent_account
                ).first()
                if v2_acc.parent != expected_parent:
                    hierarchy_errors += 1
        
        if hierarchy_errors > 0:
            self.stdout.write(self.style.ERROR(
                f'   ❌ Found {hierarchy_errors} hierarchy errors'
            ))
            checks_passed = False
        else:
            self.stdout.write(self.style.SUCCESS('   ✅ Hierarchy preserved'))
        
        return checks_passed

    def generate_report(self, migrated_count):
        """Generate migration report"""
        report = []
        report.append('\n' + '=' * 80)
        report.append('MIGRATION REPORT')
        report.append('=' * 80)
        report.append(f'\nAccounts Migrated: {migrated_count}')
        report.append(f'Total Legacy Accounts: {ChartOfAccounts.objects.count()}')
        report.append(f'Total V2 Accounts: {AccountV2.objects.count()}')
        
        # Account type breakdown
        report.append('\nAccount Type Breakdown:')
        for acc_type in ['asset', 'liability', 'equity', 'revenue', 'expense']:
            count = AccountV2.objects.filter(
                account_type=acc_type,
                migrated_from_legacy__isnull=False
            ).count()
            report.append(f'  {acc_type.capitalize()}: {count}')
        
        # Balance summary
        total_balance = sum(
            acc.current_balance
            for acc in AccountV2.objects.filter(migrated_from_legacy__isnull=False)
        )
        report.append(f'\nTotal Opening Balance: {total_balance}')
        
        report.append('\n' + '=' * 80)
        
        for line in report:
            self.stdout.write(line)
