"""
Management command to validate migration data integrity

Usage:
    python manage.py validate_migration [--detailed] [--fix-issues]

This command validates that data migrated from legacy to V2 models
maintains integrity, accuracy, and completeness.
"""

from django.core.management.base import BaseCommand
from django.db.models import Sum
from decimal import Decimal
from accounting.models import ChartOfAccounts, AccountV2, JournalEntry, VoucherV2
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Validate migration data integrity between legacy and V2 models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed validation results',
        )
        parser.add_argument(
            '--fix-issues',
            action='store_true',
            help='Attempt to automatically fix detected issues',
        )

    def handle(self, *args, **options):
        self.detailed = options['detailed']
        self.fix_issues = options['fix_issues']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Migration Data Validation'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        warnings = 0
        
        # Run all validation checks
        checks = [
            ('Record Count Validation', self.validate_record_counts),
            ('Balance Validation', self.validate_balances),
            ('Hierarchy Validation', self.validate_hierarchy),
            ('Code Uniqueness', self.validate_unique_codes),
            ('Data Completeness', self.validate_data_completeness),
            ('Referential Integrity', self.validate_referential_integrity),
        ]
        
        for check_name, check_func in checks:
            self.stdout.write(f'\n🔍 {check_name}...')
            total_checks += 1
            
            try:
                result = check_func()
                if result['status'] == 'pass':
                    self.stdout.write(self.style.SUCCESS(f'   ✅ {result["message"]}'))
                    passed_checks += 1
                elif result['status'] == 'warning':
                    self.stdout.write(self.style.WARNING(f'   ⚠️  {result["message"]}'))
                    warnings += 1
                else:
                    self.stdout.write(self.style.ERROR(f'   ❌ {result["message"]}'))
                    failed_checks += 1
                    
                    if self.detailed and 'details' in result:
                        for detail in result['details']:
                            self.stdout.write(f'      • {detail}')
                    
                    if self.fix_issues and 'fix_func' in result:
                        self.stdout.write('   🔧 Attempting to fix...')
                        fix_result = result['fix_func']()
                        if fix_result:
                            self.stdout.write(self.style.SUCCESS('   ✅ Issue fixed'))
                        else:
                            self.stdout.write(self.style.ERROR('   ❌ Could not fix automatically'))
                            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Check failed with error: {e}'))
                failed_checks += 1
                logger.error(f'Validation check {check_name} failed: {e}')
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('VALIDATION SUMMARY')
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total Checks: {total_checks}')
        self.stdout.write(self.style.SUCCESS(f'Passed: {passed_checks}'))
        if warnings > 0:
            self.stdout.write(self.style.WARNING(f'Warnings: {warnings}'))
        if failed_checks > 0:
            self.stdout.write(self.style.ERROR(f'Failed: {failed_checks}'))
        
        if failed_checks == 0:
            self.stdout.write(self.style.SUCCESS('\n✅ ALL VALIDATIONS PASSED'))
        else:
            self.stdout.write(self.style.ERROR('\n❌ VALIDATION FAILED - Issues detected'))
        
        self.stdout.write('=' * 80 + '\n')

    def validate_record_counts(self):
        """Validate that record counts match"""
        legacy_count = ChartOfAccounts.objects.count()
        v2_migrated_count = AccountV2.objects.filter(migrated_from_legacy__isnull=False).count()
        v2_total_count = AccountV2.objects.count()
        
        if legacy_count == v2_migrated_count:
            return {
                'status': 'pass',
                'message': f'Record counts match: {legacy_count} accounts'
            }
        else:
            return {
                'status': 'fail',
                'message': f'Count mismatch - Legacy: {legacy_count}, V2 Migrated: {v2_migrated_count}, V2 Total: {v2_total_count}',
                'details': [
                    f'Missing migrations: {legacy_count - v2_migrated_count}',
                    f'New V2 accounts: {v2_total_count - v2_migrated_count}'
                ]
            }

    def validate_balances(self):
        """Validate that balances match"""
        legacy_total = ChartOfAccounts.objects.aggregate(
            total=Sum('opening_balance')
        )['total'] or Decimal('0.00')
        
        v2_total = AccountV2.objects.filter(
            migrated_from_legacy__isnull=False
        ).aggregate(
            total=Sum('opening_balance')
        )['total'] or Decimal('0.00')
        
        difference = abs(legacy_total - v2_total)
        
        if difference < Decimal('0.01'):
            return {
                'status': 'pass',
                'message': f'Balances match: {legacy_total}'
            }
        else:
            return {
                'status': 'fail',
                'message': f'Balance mismatch - Difference: {difference}',
                'details': [
                    f'Legacy total: {legacy_total}',
                    f'V2 total: {v2_total}',
                    f'Difference: {difference}'
                ]
            }

    def validate_hierarchy(self):
        """Validate parent-child relationships"""
        errors = []
        
        for legacy_acc in ChartOfAccounts.objects.filter(parent_account__isnull=False):
            v2_acc = AccountV2.objects.filter(migrated_from_legacy=legacy_acc).first()
            
            if not v2_acc:
                errors.append(f'Account {legacy_acc.account_code} not migrated')
                continue
            
            if legacy_acc.parent_account:
                expected_parent = AccountV2.objects.filter(
                    migrated_from_legacy=legacy_acc.parent_account
                ).first()
                
                if v2_acc.parent != expected_parent:
                    errors.append(
                        f'Account {legacy_acc.account_code}: '
                        f'Parent mismatch (expected {expected_parent.code if expected_parent else "None"}, '
                        f'got {v2_acc.parent.code if v2_acc.parent else "None"})'
                    )
        
        if not errors:
            return {
                'status': 'pass',
                'message': 'All hierarchies preserved correctly'
            }
        else:
            return {
                'status': 'fail',
                'message': f'Found {len(errors)} hierarchy errors',
                'details': errors[:10]  # Show first 10 errors
            }

    def validate_unique_codes(self):
        """Validate that account codes are unique"""
        from django.db.models import Count
        
        duplicates_v2 = AccountV2.objects.values('code').annotate(
            count=Count('code')
        ).filter(count__gt=1)
        
        if not duplicates_v2.exists():
            return {
                'status': 'pass',
                'message': 'All account codes are unique'
            }
        else:
            duplicate_codes = [d['code'] for d in duplicates_v2]
            return {
                'status': 'fail',
                'message': f'Found {duplicates_v2.count()} duplicate codes',
                'details': [f'Duplicate code: {code}' for code in duplicate_codes]
            }

    def validate_data_completeness(self):
        """Validate that all required fields are populated"""
        issues = []
        
        # Check for missing codes
        missing_codes = AccountV2.objects.filter(code__isnull=True) | AccountV2.objects.filter(code='')
        if missing_codes.exists():
            issues.append(f'{missing_codes.count()} accounts with missing codes')
        
        # Check for missing names
        missing_names = AccountV2.objects.filter(name__isnull=True) | AccountV2.objects.filter(name='')
        if missing_names.exists():
            issues.append(f'{missing_names.count()} accounts with missing names')
        
        # Check for invalid account types
        invalid_types = AccountV2.objects.exclude(
            account_type__in=['asset', 'liability', 'equity', 'revenue', 'expense']
        )
        if invalid_types.exists():
            issues.append(f'{invalid_types.count()} accounts with invalid types')
        
        if not issues:
            return {
                'status': 'pass',
                'message': 'All required fields are complete'
            }
        else:
            return {
                'status': 'fail',
                'message': 'Data completeness issues detected',
                'details': issues
            }

    def validate_referential_integrity(self):
        """Validate that all references are valid"""
        issues = []
        
        # Check for orphaned V2 accounts (parent doesn't exist)
        orphaned = AccountV2.objects.filter(
            parent__isnull=False
        ).exclude(
            parent__in=AccountV2.objects.all()
        )
        
        if orphaned.exists():
            issues.append(f'{orphaned.count()} orphaned accounts (invalid parent)')
        
        # Check for circular references
        for account in AccountV2.objects.filter(parent__isnull=False):
            if self.has_circular_reference(account):
                issues.append(f'Circular reference detected for account {account.code}')
        
        if not issues:
            return {
                'status': 'pass',
                'message': 'All references are valid'
            }
        else:
            return {
                'status': 'fail',
                'message': 'Referential integrity issues detected',
                'details': issues
            }

    def has_circular_reference(self, account, visited=None):
        """Check if account has circular parent reference"""
        if visited is None:
            visited = set()
        
        if account.id in visited:
            return True
        
        if not account.parent:
            return False
        
        visited.add(account.id)
        return self.has_circular_reference(account.parent, visited)
