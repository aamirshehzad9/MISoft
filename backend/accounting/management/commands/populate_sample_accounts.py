"""
Management command to populate sample Chart of Accounts data

Usage:
    python manage.py populate_sample_accounts [--clear-existing]

This command creates a comprehensive sample Chart of Accounts
for a manufacturing company (MI Industries - Adhesive Manufacturing)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from accounting.models import ChartOfAccounts, AccountType, FiscalYear
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate sample Chart of Accounts for MI Industries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing accounts before populating',
        )

    def handle(self, *args, **options):
        self.clear_existing = options['clear_existing']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Populating Sample Chart of Accounts'))
        self.stdout.write(self.style.SUCCESS('Company: MI Industries (Adhesive Manufacturing)'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        # Clear existing if requested
        if self.clear_existing:
            self.stdout.write('\n🗑️  Clearing existing accounts...')
            count = ChartOfAccounts.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'   Deleted {count} existing accounts'))
        
        # Create account types
        self.stdout.write('\n📋 Step 1: Creating account types...')
        self.create_account_types()
        self.stdout.write(self.style.SUCCESS('   ✅ Account types created'))
        
        # Create fiscal year
        self.stdout.write('\n📅 Step 2: Creating fiscal year...')
        self.create_fiscal_year()
        self.stdout.write(self.style.SUCCESS('   ✅ Fiscal year created'))
        
        # Create accounts
        self.stdout.write('\n💰 Step 3: Creating accounts...')
        created_count = self.create_accounts()
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created {created_count} accounts'))
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('SUMMARY')
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total Accounts: {ChartOfAccounts.objects.count()}')
        self.stdout.write(f'Account Types: {AccountType.objects.count()}')
        self.stdout.write(f'Fiscal Years: {FiscalYear.objects.count()}')
        
        # By type
        self.stdout.write('\nAccounts by Type:')
        for acc_type in AccountType.objects.all():
            count = ChartOfAccounts.objects.filter(account_type=acc_type).count()
            self.stdout.write(f'  {acc_type.name}: {count}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data populated successfully!'))
        self.stdout.write('=' * 80 + '\n')

    def create_account_types(self):
        """Create account types"""
        account_types = [
            {'name': 'Current Assets', 'type_category': 'asset', 'description': 'Assets that can be converted to cash within one year'},
            {'name': 'Fixed Assets', 'type_category': 'asset', 'description': 'Long-term tangible assets'},
            {'name': 'Current Liabilities', 'type_category': 'liability', 'description': 'Obligations due within one year'},
            {'name': 'Long-term Liabilities', 'type_category': 'liability', 'description': 'Obligations due after one year'},
            {'name': 'Equity', 'type_category': 'equity', 'description': 'Owner\'s equity and retained earnings'},
            {'name': 'Revenue', 'type_category': 'revenue', 'description': 'Income from business operations'},
            {'name': 'Cost of Goods Sold', 'type_category': 'expense', 'description': 'Direct costs of production'},
            {'name': 'Operating Expenses', 'type_category': 'expense', 'description': 'Indirect business expenses'},
        ]
        
        for acc_type_data in account_types:
            AccountType.objects.get_or_create(
                name=acc_type_data['name'],
                defaults={
                    'type_category': acc_type_data['type_category'],
                    'description': acc_type_data['description']
                }
            )

    def create_fiscal_year(self):
        """Create fiscal year"""
        FiscalYear.objects.get_or_create(
            name='FY 2025',
            defaults={
                'start_date': timezone.now().date().replace(month=1, day=1),
                'end_date': timezone.now().date().replace(month=12, day=31),
                'is_closed': False
            }
        )

    def create_accounts(self):
        """Create comprehensive chart of accounts"""
        created_count = 0
        
        # Get account types
        current_assets = AccountType.objects.get(name='Current Assets')
        fixed_assets = AccountType.objects.get(name='Fixed Assets')
        current_liabilities = AccountType.objects.get(name='Current Liabilities')
        long_term_liabilities = AccountType.objects.get(name='Long-term Liabilities')
        equity = AccountType.objects.get(name='Equity')
        revenue = AccountType.objects.get(name='Revenue')
        cogs = AccountType.objects.get(name='Cost of Goods Sold')
        operating_expenses = AccountType.objects.get(name='Operating Expenses')
        
        accounts = [
            # ============================================
            # ASSETS
            # ============================================
            
            # Current Assets - Header
            {'code': '1000', 'name': 'Current Assets', 'type': current_assets, 'is_header': True, 'parent': None, 'balance': Decimal('0')},
            
            # Cash & Bank
            {'code': '1010', 'name': 'Cash & Bank', 'type': current_assets, 'is_header': True, 'parent': '1000', 'balance': Decimal('0')},
            {'code': '1011', 'name': 'Cash in Hand', 'type': current_assets, 'is_header': False, 'parent': '1010', 'balance': Decimal('50000.00')},
            {'code': '1012', 'name': 'Petty Cash', 'type': current_assets, 'is_header': False, 'parent': '1010', 'balance': Decimal('10000.00')},
            {'code': '1013', 'name': 'Bank - HBL Main Account', 'type': current_assets, 'is_header': False, 'parent': '1010', 'balance': Decimal('2500000.00')},
            {'code': '1014', 'name': 'Bank - MCB Payroll Account', 'type': current_assets, 'is_header': False, 'parent': '1010', 'balance': Decimal('500000.00')},
            
            # Accounts Receivable
            {'code': '1020', 'name': 'Accounts Receivable', 'type': current_assets, 'is_header': True, 'parent': '1000', 'balance': Decimal('0')},
            {'code': '1021', 'name': 'Trade Debtors', 'type': current_assets, 'is_header': False, 'parent': '1020', 'balance': Decimal('1500000.00')},
            {'code': '1022', 'name': 'Other Receivables', 'type': current_assets, 'is_header': False, 'parent': '1020', 'balance': Decimal('250000.00')},
            
            # Inventory
            {'code': '1030', 'name': 'Inventory', 'type': current_assets, 'is_header': True, 'parent': '1000', 'balance': Decimal('0')},
            {'code': '1031', 'name': 'Raw Materials', 'type': current_assets, 'is_header': False, 'parent': '1030', 'balance': Decimal('800000.00')},
            {'code': '1032', 'name': 'Work in Progress', 'type': current_assets, 'is_header': False, 'parent': '1030', 'balance': Decimal('300000.00')},
            {'code': '1033', 'name': 'Finished Goods', 'type': current_assets, 'is_header': False, 'parent': '1030', 'balance': Decimal('1200000.00')},
            {'code': '1034', 'name': 'Packaging Materials', 'type': current_assets, 'is_header': False, 'parent': '1030', 'balance': Decimal('150000.00')},
            
            # Fixed Assets - Header
            {'code': '1500', 'name': 'Fixed Assets', 'type': fixed_assets, 'is_header': True, 'parent': None, 'balance': Decimal('0')},
            
            # Property
            {'code': '1510', 'name': 'Property', 'type': fixed_assets, 'is_header': True, 'parent': '1500', 'balance': Decimal('0')},
            {'code': '1511', 'name': 'Land', 'type': fixed_assets, 'is_header': False, 'parent': '1510', 'balance': Decimal('5000000.00')},
            {'code': '1512', 'name': 'Building', 'type': fixed_assets, 'is_header': False, 'parent': '1510', 'balance': Decimal('8000000.00')},
            
            # Plant & Machinery
            {'code': '1520', 'name': 'Plant & Machinery', 'type': fixed_assets, 'is_header': True, 'parent': '1500', 'balance': Decimal('0')},
            {'code': '1521', 'name': 'Production Machinery', 'type': fixed_assets, 'is_header': False, 'parent': '1520', 'balance': Decimal('3000000.00')},
            {'code': '1522', 'name': 'Mixing Equipment', 'type': fixed_assets, 'is_header': False, 'parent': '1520', 'balance': Decimal('1500000.00')},
            {'code': '1523', 'name': 'Packaging Machinery', 'type': fixed_assets, 'is_header': False, 'parent': '1520', 'balance': Decimal('800000.00')},
            
            # Vehicles & Equipment
            {'code': '1530', 'name': 'Vehicles & Equipment', 'type': fixed_assets, 'is_header': True, 'parent': '1500', 'balance': Decimal('0')},
            {'code': '1531', 'name': 'Delivery Vehicles', 'type': fixed_assets, 'is_header': False, 'parent': '1530', 'balance': Decimal('1200000.00')},
            {'code': '1532', 'name': 'Office Equipment', 'type': fixed_assets, 'is_header': False, 'parent': '1530', 'balance': Decimal('300000.00')},
            {'code': '1533', 'name': 'Computer Equipment', 'type': fixed_assets, 'is_header': False, 'parent': '1530', 'balance': Decimal('200000.00')},
            
            # ============================================
            # LIABILITIES
            # ============================================
            
            # Current Liabilities - Header
            {'code': '2000', 'name': 'Current Liabilities', 'type': current_liabilities, 'is_header': True, 'parent': None, 'balance': Decimal('0')},
            
            # Accounts Payable
            {'code': '2010', 'name': 'Accounts Payable', 'type': current_liabilities, 'is_header': True, 'parent': '2000', 'balance': Decimal('0')},
            {'code': '2011', 'name': 'Trade Creditors', 'type': current_liabilities, 'is_header': False, 'parent': '2010', 'balance': Decimal('900000.00')},
            {'code': '2012', 'name': 'Other Payables', 'type': current_liabilities, 'is_header': False, 'parent': '2010', 'balance': Decimal('150000.00')},
            
            # Taxes Payable
            {'code': '2020', 'name': 'Taxes Payable', 'type': current_liabilities, 'is_header': True, 'parent': '2000', 'balance': Decimal('0')},
            {'code': '2021', 'name': 'Sales Tax Payable', 'type': current_liabilities, 'is_header': False, 'parent': '2020', 'balance': Decimal('180000.00')},
            {'code': '2022', 'name': 'Income Tax Payable', 'type': current_liabilities, 'is_header': False, 'parent': '2020', 'balance': Decimal('250000.00')},
            
            # Salaries & Wages Payable
            {'code': '2030', 'name': 'Salaries & Wages Payable', 'type': current_liabilities, 'is_header': True, 'parent': '2000', 'balance': Decimal('0')},
            {'code': '2031', 'name': 'Salaries Payable', 'type': current_liabilities, 'is_header': False, 'parent': '2030', 'balance': Decimal('400000.00')},
            {'code': '2032', 'name': 'Wages Payable', 'type': current_liabilities, 'is_header': False, 'parent': '2030', 'balance': Decimal('200000.00')},
            
            # Long-term Liabilities - Header
            {'code': '2500', 'name': 'Long-term Liabilities', 'type': long_term_liabilities, 'is_header': True, 'parent': None, 'balance': Decimal('0')},
            {'code': '2510', 'name': 'Bank Loans', 'type': long_term_liabilities, 'is_header': False, 'parent': '2500', 'balance': Decimal('5000000.00')},
            {'code': '2520', 'name': 'Mortgage Payable', 'type': long_term_liabilities, 'is_header': False, 'parent': '2500', 'balance': Decimal('3000000.00')},
            
            # ============================================
            # EQUITY
            # ============================================
            
            {'code': '3000', 'name': 'Equity', 'type': equity, 'is_header': True, 'parent': None, 'balance': Decimal('0')},
            {'code': '3010', 'name': 'Owner\'s Capital', 'type': equity, 'is_header': False, 'parent': '3000', 'balance': Decimal('15000000.00')},
            {'code': '3020', 'name': 'Retained Earnings', 'type': equity, 'is_header': False, 'parent': '3000', 'balance': Decimal('2500000.00')},
            {'code': '3030', 'name': 'Current Year Profit/Loss', 'type': equity, 'is_header': False, 'parent': '3000', 'balance': Decimal('0')},
            
            # ============================================
            # REVENUE
            # ============================================
            
            {'code': '4000', 'name': 'Revenue', 'type': revenue, 'is_header': True, 'parent': None, 'balance': Decimal('0')},
            
            # Sales Revenue
            {'code': '4010', 'name': 'Sales Revenue', 'type': revenue, 'is_header': True, 'parent': '4000', 'balance': Decimal('0')},
            {'code': '4011', 'name': 'Adhesive Sales - Industrial', 'type': revenue, 'is_header': False, 'parent': '4010', 'balance': Decimal('0')},
            {'code': '4012', 'name': 'Adhesive Sales - Commercial', 'type': revenue, 'is_header': False, 'parent': '4010', 'balance': Decimal('0')},
            {'code': '4013', 'name': 'Adhesive Sales - Retail', 'type': revenue, 'is_header': False, 'parent': '4010', 'balance': Decimal('0')},
            
            # Other Income
            {'code': '4020', 'name': 'Other Income', 'type': revenue, 'is_header': True, 'parent': '4000', 'balance': Decimal('0')},
            {'code': '4021', 'name': 'Interest Income', 'type': revenue, 'is_header': False, 'parent': '4020', 'balance': Decimal('0')},
            {'code': '4022', 'name': 'Miscellaneous Income', 'type': revenue, 'is_header': False, 'parent': '4020', 'balance': Decimal('0')},
            
            # ============================================
            # COST OF GOODS SOLD
            # ============================================
            
            {'code': '5000', 'name': 'Cost of Goods Sold', 'type': cogs, 'is_header': True, 'parent': None, 'balance': Decimal('0')},
            
            # Direct Materials
            {'code': '5010', 'name': 'Direct Materials', 'type': cogs, 'is_header': True, 'parent': '5000', 'balance': Decimal('0')},
            {'code': '5011', 'name': 'Resin & Polymers', 'type': cogs, 'is_header': False, 'parent': '5010', 'balance': Decimal('0')},
            {'code': '5012', 'name': 'Solvents & Chemicals', 'type': cogs, 'is_header': False, 'parent': '5010', 'balance': Decimal('0')},
            {'code': '5013', 'name': 'Additives & Fillers', 'type': cogs, 'is_header': False, 'parent': '5010', 'balance': Decimal('0')},
            
            # Direct Labor
            {'code': '5020', 'name': 'Direct Labor', 'type': cogs, 'is_header': True, 'parent': '5000', 'balance': Decimal('0')},
            {'code': '5021', 'name': 'Production Wages', 'type': cogs, 'is_header': False, 'parent': '5020', 'balance': Decimal('0')},
            {'code': '5022', 'name': 'Production Overtime', 'type': cogs, 'is_header': False, 'parent': '5020', 'balance': Decimal('0')},
            
            # Manufacturing Overhead
            {'code': '5030', 'name': 'Manufacturing Overhead', 'type': cogs, 'is_header': True, 'parent': '5000', 'balance': Decimal('0')},
            {'code': '5031', 'name': 'Factory Utilities', 'type': cogs, 'is_header': False, 'parent': '5030', 'balance': Decimal('0')},
            {'code': '5032', 'name': 'Factory Maintenance', 'type': cogs, 'is_header': False, 'parent': '5030', 'balance': Decimal('0')},
            {'code': '5033', 'name': 'Quality Control', 'type': cogs, 'is_header': False, 'parent': '5030', 'balance': Decimal('0')},
            
            # ============================================
            # OPERATING EXPENSES
            # ============================================
            
            {'code': '6000', 'name': 'Operating Expenses', 'type': operating_expenses, 'is_header': True, 'parent': None, 'balance': Decimal('0')},
            
            # Administrative Expenses
            {'code': '6010', 'name': 'Administrative Expenses', 'type': operating_expenses, 'is_header': True, 'parent': '6000', 'balance': Decimal('0')},
            {'code': '6011', 'name': 'Salaries - Admin', 'type': operating_expenses, 'is_header': False, 'parent': '6010', 'balance': Decimal('0')},
            {'code': '6012', 'name': 'Office Rent', 'type': operating_expenses, 'is_header': False, 'parent': '6010', 'balance': Decimal('0')},
            {'code': '6013', 'name': 'Office Supplies', 'type': operating_expenses, 'is_header': False, 'parent': '6010', 'balance': Decimal('0')},
            {'code': '6014', 'name': 'Telephone & Internet', 'type': operating_expenses, 'is_header': False, 'parent': '6010', 'balance': Decimal('0')},
            
            # Selling Expenses
            {'code': '6020', 'name': 'Selling Expenses', 'type': operating_expenses, 'is_header': True, 'parent': '6000', 'balance': Decimal('0')},
            {'code': '6021', 'name': 'Salaries - Sales', 'type': operating_expenses, 'is_header': False, 'parent': '6020', 'balance': Decimal('0')},
            {'code': '6022', 'name': 'Marketing & Advertising', 'type': operating_expenses, 'is_header': False, 'parent': '6020', 'balance': Decimal('0')},
            {'code': '6023', 'name': 'Sales Commission', 'type': operating_expenses, 'is_header': False, 'parent': '6020', 'balance': Decimal('0')},
            {'code': '6024', 'name': 'Delivery Expenses', 'type': operating_expenses, 'is_header': False, 'parent': '6020', 'balance': Decimal('0')},
            
            # General Expenses
            {'code': '6030', 'name': 'General Expenses', 'type': operating_expenses, 'is_header': True, 'parent': '6000', 'balance': Decimal('0')},
            {'code': '6031', 'name': 'Insurance', 'type': operating_expenses, 'is_header': False, 'parent': '6030', 'balance': Decimal('0')},
            {'code': '6032', 'name': 'Depreciation', 'type': operating_expenses, 'is_header': False, 'parent': '6030', 'balance': Decimal('0')},
            {'code': '6033', 'name': 'Bank Charges', 'type': operating_expenses, 'is_header': False, 'parent': '6030', 'balance': Decimal('0')},
            {'code': '6034', 'name': 'Professional Fees', 'type': operating_expenses, 'is_header': False, 'parent': '6030', 'balance': Decimal('0')},
        ]
        
        # Create accounts with proper parent relationships
        account_objects = {}
        
        with transaction.atomic():
            for acc_data in accounts:
                parent_obj = None
                if acc_data['parent']:
                    parent_obj = account_objects.get(acc_data['parent'])
                
                account = ChartOfAccounts.objects.create(
                    account_code=acc_data['code'],
                    account_name=acc_data['name'],
                    account_type=acc_data['type'],
                    parent_account=parent_obj,
                    is_header=acc_data['is_header'],
                    is_active=True,
                    opening_balance=acc_data['balance'],
                    opening_balance_date=timezone.now().date(),
                    description=f"Account for {acc_data['name']}"
                )
                
                account_objects[acc_data['code']] = account
                created_count += 1
        
        return created_count
