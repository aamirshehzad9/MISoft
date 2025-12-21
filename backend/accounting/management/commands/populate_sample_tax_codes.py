"""
Management command to populate sample tax codes

Usage:
    python manage.py populate_sample_tax_codes [--clear-existing]

This command creates standard tax codes for MI Industries:
1. GST 17% (Standard)
2. VAT 5% (Reduced)
3. Service Tax 10%
4. Zero Rated 0%
"""

from django.core.management.base import BaseCommand
from accounting.models import TaxCode, ChartOfAccounts
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate sample tax codes for MI Industries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing tax codes before populating',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Populating Sample Tax Codes'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        if options['clear_existing']:
            TaxCode.objects.all().delete()
            self.stdout.write(self.style.WARNING('🗑️  Deleted existing tax codes'))

        # Get Tax Accounts (Legacy)
        # We need Sales Tax Payable (Liability) and Input Tax (Asset)
        # Assuming they exist from populate_sample_accounts
        
        try:
            sales_tax_acc = ChartOfAccounts.objects.get(account_code='2021') # Sales Tax Payable
            input_tax_acc = ChartOfAccounts.objects.get(account_code='1022') # Input Tax / Receivable
        except ChartOfAccounts.DoesNotExist:
            # Fallback if specific codes don't exist, search by name or use first available
            sales_tax_acc = ChartOfAccounts.objects.filter(account_type='liability').first()
            input_tax_acc = ChartOfAccounts.objects.filter(account_type='asset').first()
            self.stdout.write(self.style.WARNING('⚠️  Specific tax accounts not found, using fallbacks'))

        tax_data = [
            {
                'code': 'GST-17',
                'description': 'General Sales Tax 17%',
                'rate': Decimal('17.00'),
            },
            {
                'code': 'VAT-5',
                'description': 'Value Added Tax 5%',
                'rate': Decimal('5.00'),
            },
            {
                'code': 'SRV-10',
                'description': 'Service Tax 10%',
                'rate': Decimal('10.00'),
            },
            {
                'code': 'ZERO-0',
                'description': 'Zero Rated Supply',
                'rate': Decimal('0.00'),
            }
        ]
        
        for data in tax_data:
            tax, created = TaxCode.objects.get_or_create(
                code=data['code'],
                defaults={
                    'description': data['description'],
                    'tax_percentage': data['rate'],
                    'sales_tax_account': sales_tax_acc,
                    'purchase_tax_account': input_tax_acc,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"   Created {tax.code} - {tax.tax_percentage}%"))
            else:
                self.stdout.write(f"   Skipped {tax.code} (already exists)")

        self.stdout.write(self.style.SUCCESS('\n✅ Sample tax codes populated successfully!'))
