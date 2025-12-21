"""
Management command to validate tax migration

Usage:
    python manage.py validate_tax_migration

This command checks:
1. Tax Code Counts (Legacy vs V2 Master vs V2 Group)
2. Data Integrity (Rates, Names, Codes)
3. Group Structure (1:1 Mapping)
"""

from django.core.management.base import BaseCommand
from accounting.models import TaxCode, TaxMasterV2, TaxGroupV2, TaxGroupItemV2

class Command(BaseCommand):
    help = 'Validate tax system migration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('VALIDATING TAX MIGRATION'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        errors = []
        
        # 1. Count Validation
        self.stdout.write('\n📊 Validating Counts...')
        legacy_count = TaxCode.objects.count()
        master_count = TaxMasterV2.objects.count()
        group_count = TaxGroupV2.objects.count()
        
        self.print_comparison("Tax Codes", legacy_count, master_count)
        self.print_comparison("Tax Groups", legacy_count, group_count)
        
        if legacy_count != master_count: errors.append("Tax Master count mismatch")
        if legacy_count != group_count: errors.append("Tax Group count mismatch")

        # 2. Data Integrity
        self.stdout.write('\n🔍 Validating Data Integrity...')
        for legacy in TaxCode.objects.all():
            # Check Master
            try:
                master = TaxMasterV2.objects.get(tax_code=legacy.code)
                if master.tax_rate != legacy.tax_percentage:
                    errors.append(f"Rate mismatch for {legacy.code}: {legacy.tax_percentage} vs {master.tax_rate}")
                if master.tax_name != legacy.description:
                    errors.append(f"Description mismatch for {legacy.code}")
            except TaxMasterV2.DoesNotExist:
                errors.append(f"Missing Tax Master for {legacy.code}")

            # Check Group
            try:
                group = TaxGroupV2.objects.get(group_name=legacy.code)
                # Check Item
                item = TaxGroupItemV2.objects.filter(tax_group=group).first()
                if not item:
                    errors.append(f"Empty Tax Group for {legacy.code}")
                elif item.tax.tax_code != legacy.code:
                    errors.append(f"Wrong Tax in Group for {legacy.code}")
            except TaxGroupV2.DoesNotExist:
                errors.append(f"Missing Tax Group for {legacy.code}")

        # Summary
        self.stdout.write('\n' + '=' * 80)
        if not errors:
            self.stdout.write(self.style.SUCCESS('✅ VALIDATION SUCCESSFUL - 100% Data Integrity'))
        else:
            self.stdout.write(self.style.ERROR('❌ VALIDATION FAILED'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f"   - {error}"))
        self.stdout.write('=' * 80 + '\n')

    def print_comparison(self, label, legacy, v2):
        match = legacy == v2
        status = "✅ MATCH" if match else "❌ MISMATCH"
        style = self.style.SUCCESS if match else self.style.ERROR
        self.stdout.write(f"   {label:<20} Legacy: {str(legacy):<10} V2: {str(v2):<10} {style(status)}")
