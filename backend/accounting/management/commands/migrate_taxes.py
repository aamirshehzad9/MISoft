"""
Management command to migrate tax codes to V2 Tax System

Usage:
    python manage.py migrate_taxes [--dry-run]

This command migrates:
1. Legacy TaxCode -> TaxMasterV2
2. Legacy TaxCode -> TaxGroupV2 (1:1 mapping for backward compatibility)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from accounting.models import (
    TaxCode, TaxMasterV2, TaxGroupV2, TaxGroupItemV2, AccountV2
)

class Command(BaseCommand):
    help = 'Migrate legacy tax codes to V2 Tax System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without committing changes',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Tax System Migration - Legacy to V2'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be committed\n'))
        
        # Load Accounts
        self.load_accounts()
        
        # Migrate Taxes
        self.stdout.write('\n🔄 Migrating Tax Codes...')
        self.migrate_taxes()
        
        self.stdout.write('\n' + '=' * 80)
        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes committed'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ MIGRATION COMPLETE'))
        self.stdout.write('=' * 80 + '\n')

    def load_accounts(self):
        """Load required V2 accounts for tax mapping"""
        # In a real scenario, we would map legacy accounts to V2 accounts
        # For this migration, we'll use standard tax accounts
        try:
            self.acc_tax_payable = AccountV2.objects.get(code='2021') # Sales Tax Payable
            self.acc_input_tax = AccountV2.objects.get(code='1022') # Input Tax
        except AccountV2.DoesNotExist:
            # Fallback
            self.acc_tax_payable = AccountV2.objects.filter(account_type='liability').first()
            self.acc_input_tax = AccountV2.objects.filter(account_type='asset').first()
            self.stdout.write(self.style.WARNING('⚠️  Specific tax accounts not found, using fallbacks'))

    def migrate_taxes(self):
        tax_codes = TaxCode.objects.all()
        count = 0
        
        for tax_code in tax_codes:
            if TaxMasterV2.objects.filter(tax_code=tax_code.code).exists():
                self.stdout.write(f"   Skipping {tax_code.code} (already migrated)")
                continue

            if self.migrate_single_tax(tax_code):
                count += 1
                self.stdout.write(f"   Migrated {tax_code.code}")
        
        self.stdout.write(f"   Total Taxes Migrated: {count}")

    def migrate_single_tax(self, tax_code):
        try:
            # Determine Tax Type
            tax_type = 'sales_tax'
            if 'VAT' in tax_code.code: tax_type = 'vat'
            elif 'GST' in tax_code.code: tax_type = 'gst'
            elif 'SRV' in tax_code.code: tax_type = 'service_tax'
            
            if not self.dry_run:
                with transaction.atomic():
                    # 1. Create Tax Master
                    master = TaxMasterV2.objects.create(
                        tax_code=tax_code.code,
                        tax_name=tax_code.description,
                        tax_type=tax_type,
                        tax_rate=tax_code.tax_percentage,
                        tax_collected_account=self.acc_tax_payable,
                        tax_paid_account=self.acc_input_tax,
                        is_active=tax_code.is_active
                    )
                    
                    # 2. Create Tax Group (1:1)
                    group = TaxGroupV2.objects.create(
                        group_name=tax_code.code, # Use same code for easy lookup
                        description=f"Standard Group for {tax_code.code}",
                        is_active=tax_code.is_active
                    )
                    
                    # 3. Link Master to Group
                    TaxGroupItemV2.objects.create(
                        tax_group=group,
                        tax=master,
                        sequence=1
                    )
            
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error migrating {tax_code.code}: {e}"))
            return False
