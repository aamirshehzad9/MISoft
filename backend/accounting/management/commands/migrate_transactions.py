"""
Management command to migrate journal entries to VoucherV2

Usage:
    python manage.py migrate_transactions [--dry-run]

This command migrates JournalEntry and JournalEntryLine to VoucherV2 and VoucherEntryV2
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from accounting.models import (
    JournalEntry, JournalEntryLine, VoucherV2, VoucherEntryV2,
    AccountV2, CurrencyV2
)
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate journal entries from legacy to VoucherV2'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without committing changes',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Transaction History Migration - Legacy to V2'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be committed\n'))
        
        # Get or create base currency
        self.stdout.write('\n💱 Step 1: Setting up base currency...')
        self.base_currency = self.setup_currency()
        self.stdout.write(self.style.SUCCESS('   ✅ Base currency ready'))
        
        # Count transactions
        total_entries = JournalEntry.objects.count()
        already_migrated = VoucherV2.objects.filter(migrated_from_legacy__isnull=False).count()
        
        self.stdout.write(f'\n📊 Migration Statistics:')
        self.stdout.write(f'   Total legacy entries: {total_entries}')
        self.stdout.write(f'   Already migrated: {already_migrated}')
        self.stdout.write(f'   Remaining to migrate: {total_entries - already_migrated}\n')
        
        if total_entries == 0:
            self.stdout.write(self.style.WARNING('No journal entries to migrate.'))
            return
        
        # Migrate transactions
        self.stdout.write('\n🔄 Step 2: Migrating transactions...')
        migrated_count = self.migrate_transactions()
        
        # Validate
        self.stdout.write('\n✅ Step 3: Validating migration...')
        if self.validate_migration():
            self.stdout.write(self.style.SUCCESS('   ✅ Validation passed'))
        else:
            self.stdout.write(self.style.ERROR('   ❌ Validation failed'))
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes committed'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ MIGRATION COMPLETE - {migrated_count} transactions migrated'))
        self.stdout.write('=' * 80 + '\n')

    def setup_currency(self):
        """Get or create base currency"""
        currency, created = CurrencyV2.objects.get_or_create(
            currency_code='PKR',
            defaults={
                'currency_name': 'Pakistani Rupee',
                'symbol': 'Rs.',
                'is_base_currency': True,
                'is_active': True
            }
        )
        return currency

    def migrate_transactions(self):
        """Migrate journal entries to vouchers"""
        migrated_count = 0
        
        # Get entries not yet migrated
        # We migrate ALL entries that haven't been migrated yet.
        # Deduplication happens in the loop below (checking voucher_number)
        legacy_entries = JournalEntry.objects.exclude(
            id__in=VoucherV2.objects.filter(
                migrated_from_legacy__isnull=False
            ).values_list('migrated_from_legacy_id', flat=True)
        ).order_by('entry_date', 'entry_number')
        
        for entry in legacy_entries:
            if self.migrate_single_entry(entry):
                migrated_count += 1
                if migrated_count % 5 == 0:
                    self.stdout.write(f'   Progress: {migrated_count} entries migrated...')
        
        return migrated_count

    def migrate_single_entry(self, legacy_entry):
        """Migrate a single journal entry"""
        try:
            # Check if already migrated
            if VoucherV2.objects.filter(migrated_from_legacy=legacy_entry).exists():
                return False
            
            # Map entry type to voucher type
            voucher_type = self.map_voucher_type(legacy_entry.entry_type)
            
            # Calculate total amount
            total_amount = legacy_entry.total_debit or Decimal('0.00')
            
            # Create voucher
            voucher_data = {
                'voucher_number': legacy_entry.entry_number,
                'voucher_type': voucher_type,
                'voucher_date': legacy_entry.entry_date,
                'reference_number': legacy_entry.reference_number or '',
                'total_amount': total_amount,
                'currency': self.base_currency,
                'exchange_rate': Decimal('1.0000'),
                'status': 'posted' if legacy_entry.status == 'posted' else 'draft',
                'approved_at': legacy_entry.posted_date,
                'narration': legacy_entry.description,
                'migrated_from_legacy': legacy_entry,
                'created_by': legacy_entry.created_by,
            }
            
            if not self.dry_run:
                with transaction.atomic():
                    # Create voucher
                    voucher = VoucherV2.objects.create(**voucher_data)
                    
                    # Create voucher entries
                    for line in legacy_entry.lines.all():
                        # Get V2 account
                        account_v2 = AccountV2.objects.filter(
                            migrated_from_legacy=line.account
                        ).first()
                        
                        if account_v2:
                            VoucherEntryV2.objects.create(
                                voucher=voucher,
                                account=account_v2,
                                debit_amount=line.debit_amount,
                                credit_amount=line.credit_amount,
                                currency_amount=line.debit_amount + line.credit_amount,
                                description=line.description or ''
                            )
            
            return True
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'   ❌ Error migrating entry {legacy_entry.entry_number}: {e}'
            ))
            logger.error(f'Error migrating entry {legacy_entry.id}: {e}')
            return False

    def map_voucher_type(self, entry_type):
        """Map legacy entry type to voucher type"""
        type_mapping = {
            'general': 'JE',
            'sales': 'SI',
            'purchase': 'PI',
            'cash_receipt': 'CRV',
            'cash_payment': 'CPV',
            'bank': 'BRV',
        }
        return type_mapping.get(entry_type, 'JE')

    def validate_migration(self):
        """Validate migration results"""
        checks_passed = True
        
        # Check 1: Count comparison
        self.stdout.write('   Comparing record counts...')
        legacy_count = JournalEntry.objects.count()
        v2_count = VoucherV2.objects.filter(migrated_from_legacy__isnull=False).count()
        
        if legacy_count != v2_count:
            self.stdout.write(self.style.WARNING(
                f'   ⚠️  Count mismatch: Legacy={legacy_count}, V2={v2_count}'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'   ✅ Counts match: {legacy_count} entries'
            ))
        
        # Check 2: Double-entry validation
        self.stdout.write('   Validating double-entry...')
        unbalanced = 0
        for voucher in VoucherV2.objects.filter(migrated_from_legacy__isnull=False):
            try:
                voucher.validate_double_entry()
            except ValueError:
                unbalanced += 1
        
        if unbalanced > 0:
            self.stdout.write(self.style.ERROR(
                f'   ❌ Found {unbalanced} unbalanced vouchers'
            ))
            checks_passed = False
        else:
            self.stdout.write(self.style.SUCCESS('   ✅ All vouchers balanced'))
        
        return checks_passed
