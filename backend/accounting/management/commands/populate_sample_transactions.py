"""
Management command to populate sample journal entries

Usage:
    python manage.py populate_sample_transactions [--clear-existing]

This command creates comprehensive sample journal entries
for MI Industries representing typical business transactions
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from accounting.models import (
    JournalEntry, JournalEntryLine, ChartOfAccounts, FiscalYear
)
from partners.models import BusinessPartner
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Populate sample journal entries for MI Industries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing journal entries before populating',
        )

    def handle(self, *args, **options):
        self.clear_existing = options['clear_existing']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Populating Sample Journal Entries'))
        self.stdout.write(self.style.SUCCESS('Company: MI Industries'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        # Clear existing if requested
        if self.clear_existing:
            self.stdout.write('\n🗑️  Clearing existing journal entries...')
            count = JournalEntry.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'   Deleted {count} existing entries'))
        
        # Get or create admin user
        self.stdout.write('\n👤 Step 1: Getting admin user...')
        self.admin_user = self.get_admin_user()
        self.stdout.write(self.style.SUCCESS('   ✅ Admin user ready'))
        
        # Get fiscal year
        self.stdout.write('\n📅 Step 2: Getting fiscal year...')
        self.fiscal_year = FiscalYear.objects.first()
        if not self.fiscal_year:
            self.stdout.write(self.style.ERROR('   ❌ No fiscal year found. Run populate_sample_accounts first.'))
            return
        self.stdout.write(self.style.SUCCESS(f'   ✅ Using fiscal year: {self.fiscal_year.name}'))
        
        # Get accounts
        self.stdout.write('\n💰 Step 3: Loading accounts...')
        self.accounts = self.load_accounts()
        self.stdout.write(self.style.SUCCESS(f'   ✅ Loaded {len(self.accounts)} accounts'))
        
        # Get or create partners
        self.stdout.write('\n🤝 Step 4: Creating business partners...')
        self.partners = self.create_partners()
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created {len(self.partners)} partners'))
        
        # Create journal entries
        self.stdout.write('\n📝 Step 5: Creating journal entries...')
        created_count = self.create_journal_entries()
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created {created_count} journal entries'))
        
        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('SUMMARY')
        self.stdout.write('=' * 80)
        self.stdout.write(f'Total Journal Entries: {JournalEntry.objects.count()}')
        self.stdout.write(f'Total Journal Lines: {JournalEntryLine.objects.count()}')
        
        # By type
        self.stdout.write('\nEntries by Type:')
        for entry_type, name in JournalEntry.ENTRY_TYPE_CHOICES:
            count = JournalEntry.objects.filter(entry_type=entry_type).count()
            if count > 0:
                self.stdout.write(f'  {name}: {count}')
        
        # By status
        self.stdout.write('\nEntries by Status:')
        for status, name in JournalEntry.STATUS_CHOICES:
            count = JournalEntry.objects.filter(status=status).count()
            if count > 0:
                self.stdout.write(f'  {name}: {count}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample transactions populated successfully!'))
        self.stdout.write('=' * 80 + '\n')

    def get_admin_user(self):
        """Get or create admin user"""
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user = User.objects.create_superuser(
                username='admin',
                email='admin@miindustries.com',
                password='admin123'
            )
        return user

    def load_accounts(self):
        """Load all accounts into a dictionary"""
        accounts = {}
        for account in ChartOfAccounts.objects.all():
            accounts[account.account_code] = account
        return accounts

    def create_partners(self):
        """Create sample business partners"""
        partners_data = [
            {'name': 'ABC Chemicals Ltd', 'is_vendor': True, 'email': 'sales@abcchemicals.com'},
            {'name': 'XYZ Industries', 'is_customer': True, 'email': 'purchase@xyzind.com'},
            {'name': 'Global Polymers Inc', 'is_vendor': True, 'email': 'info@globalpolymers.com'},
            {'name': 'Premium Adhesives Co', 'is_customer': True, 'email': 'orders@premiumadhesives.com'},
            {'name': 'Local Hardware Store', 'is_customer': True, 'email': 'sales@localhardware.com'},
        ]
        
        partners = {}
        for partner_data in partners_data:
            partner, created = BusinessPartner.objects.get_or_create(
                name=partner_data['name'],
                defaults={
                    'is_customer': partner_data.get('is_customer', False),
                    'is_vendor': partner_data.get('is_vendor', False),
                    'email': partner_data['email'],
                    'phone': '+92-300-1234567',
                    'address_line1': 'Karachi, Pakistan',
                    'is_active': True
                }
            )
            partners[partner_data['name']] = partner
        
        return partners

    def create_journal_entries(self):
        """Create comprehensive journal entries"""
        created_count = 0
        base_date = timezone.now().date() - timedelta(days=30)
        
        entries = [
            # 1. Cash Sales
            {
                'number': 'JE-2025-001',
                'type': 'sales',
                'date': base_date,
                'description': 'Cash sales of adhesive products',
                'lines': [
                    {'account': '1011', 'debit': Decimal('120000.00'), 'credit': Decimal('0'), 'desc': 'Cash received'},
                    {'account': '4011', 'debit': Decimal('0'), 'credit': Decimal('100000.00'), 'desc': 'Sales revenue'},
                    {'account': '2021', 'debit': Decimal('0'), 'credit': Decimal('20000.00'), 'desc': 'Sales tax 20%'},
                ]
            },
            
            # 2. Purchase of Raw Materials
            {
                'number': 'JE-2025-002',
                'type': 'purchase',
                'date': base_date + timedelta(days=1),
                'description': 'Purchase of resin and polymers',
                'partner': 'ABC Chemicals Ltd',
                'lines': [
                    {'account': '1031', 'debit': Decimal('500000.00'), 'credit': Decimal('0'), 'desc': 'Raw materials purchased'},
                    {'account': '2011', 'debit': Decimal('0'), 'credit': Decimal('500000.00'), 'desc': 'Trade creditors'},
                ]
            },
            
            # 3. Payment to Supplier
            {
                'number': 'JE-2025-003',
                'type': 'cash_payment',
                'date': base_date + timedelta(days=2),
                'description': 'Payment to ABC Chemicals Ltd',
                'partner': 'ABC Chemicals Ltd',
                'lines': [
                    {'account': '2011', 'debit': Decimal('500000.00'), 'credit': Decimal('0'), 'desc': 'Payment to supplier'},
                    {'account': '1013', 'debit': Decimal('0'), 'credit': Decimal('500000.00'), 'desc': 'Bank payment'},
                ]
            },
            
            # 4. Salary Payment
            {
                'number': 'JE-2025-004',
                'type': 'cash_payment',
                'date': base_date + timedelta(days=5),
                'description': 'Monthly salary payment',
                'lines': [
                    {'account': '2031', 'debit': Decimal('400000.00'), 'credit': Decimal('0'), 'desc': 'Salaries cleared'},
                    {'account': '1014', 'debit': Decimal('0'), 'credit': Decimal('400000.00'), 'desc': 'Bank - Payroll'},
                ]
            },
            
            # 5. Credit Sales
            {
                'number': 'JE-2025-005',
                'type': 'sales',
                'date': base_date + timedelta(days=7),
                'description': 'Credit sales to XYZ Industries',
                'partner': 'XYZ Industries',
                'lines': [
                    {'account': '1021', 'debit': Decimal('600000.00'), 'credit': Decimal('0'), 'desc': 'Trade debtors'},
                    {'account': '4012', 'debit': Decimal('0'), 'credit': Decimal('500000.00'), 'desc': 'Sales revenue'},
                    {'account': '2021', 'debit': Decimal('0'), 'credit': Decimal('100000.00'), 'desc': 'Sales tax'},
                ]
            },
            
            # 6. Receipt from Customer
            {
                'number': 'JE-2025-006',
                'type': 'cash_receipt',
                'date': base_date + timedelta(days=10),
                'description': 'Receipt from XYZ Industries',
                'partner': 'XYZ Industries',
                'lines': [
                    {'account': '1013', 'debit': Decimal('600000.00'), 'credit': Decimal('0'), 'desc': 'Bank receipt'},
                    {'account': '1021', 'debit': Decimal('0'), 'credit': Decimal('600000.00'), 'desc': 'Trade debtors cleared'},
                ]
            },
            
            # 7. Utility Bill Payment
            {
                'number': 'JE-2025-007',
                'type': 'cash_payment',
                'date': base_date + timedelta(days=12),
                'description': 'Factory utility bill payment',
                'lines': [
                    {'account': '5031', 'debit': Decimal('50000.00'), 'credit': Decimal('0'), 'desc': 'Factory utilities expense'},
                    {'account': '1013', 'debit': Decimal('0'), 'credit': Decimal('50000.00'), 'desc': 'Bank payment'},
                ]
            },
            
            # 8. Office Rent Payment
            {
                'number': 'JE-2025-008',
                'type': 'cash_payment',
                'date': base_date + timedelta(days=15),
                'description': 'Monthly office rent',
                'lines': [
                    {'account': '6012', 'debit': Decimal('75000.00'), 'credit': Decimal('0'), 'desc': 'Office rent expense'},
                    {'account': '1013', 'debit': Decimal('0'), 'credit': Decimal('75000.00'), 'desc': 'Bank payment'},
                ]
            },
            
            # 9. Purchase of Packaging Materials
            {
                'number': 'JE-2025-009',
                'type': 'purchase',
                'date': base_date + timedelta(days=17),
                'description': 'Purchase of packaging materials',
                'lines': [
                    {'account': '1034', 'debit': Decimal('100000.00'), 'credit': Decimal('0'), 'desc': 'Packaging materials'},
                    {'account': '1013', 'debit': Decimal('0'), 'credit': Decimal('100000.00'), 'desc': 'Bank payment'},
                ]
            },
            
            # 10. Marketing Expense
            {
                'number': 'JE-2025-010',
                'type': 'general',
                'date': base_date + timedelta(days=20),
                'description': 'Marketing and advertising expense',
                'lines': [
                    {'account': '6022', 'debit': Decimal('80000.00'), 'credit': Decimal('0'), 'desc': 'Marketing expense'},
                    {'account': '1013', 'debit': Decimal('0'), 'credit': Decimal('80000.00'), 'desc': 'Bank payment'},
                ]
            },
            
            # 11. Production Wages
            {
                'number': 'JE-2025-011',
                'type': 'general',
                'date': base_date + timedelta(days=22),
                'description': 'Production wages for the month',
                'lines': [
                    {'account': '5021', 'debit': Decimal('300000.00'), 'credit': Decimal('0'), 'desc': 'Production wages'},
                    {'account': '2032', 'debit': Decimal('0'), 'credit': Decimal('300000.00'), 'desc': 'Wages payable'},
                ]
            },
            
            # 12. Depreciation Entry
            {
                'number': 'JE-2025-012',
                'type': 'general',
                'date': base_date + timedelta(days=25),
                'description': 'Monthly depreciation on fixed assets',
                'lines': [
                    {'account': '6032', 'debit': Decimal('150000.00'), 'credit': Decimal('0'), 'desc': 'Depreciation expense'},
                    {'account': '1521', 'debit': Decimal('0'), 'credit': Decimal('150000.00'), 'desc': 'Accumulated depreciation'},
                ]
            },
            
            # 13. Bank Interest Income
            {
                'number': 'JE-2025-013',
                'type': 'general',
                'date': base_date + timedelta(days=27),
                'description': 'Bank interest received',
                'lines': [
                    {'account': '1013', 'debit': Decimal('15000.00'), 'credit': Decimal('0'), 'desc': 'Bank account'},
                    {'account': '4021', 'debit': Decimal('0'), 'credit': Decimal('15000.00'), 'desc': 'Interest income'},
                ]
            },
            
            # 14. Insurance Payment
            {
                'number': 'JE-2025-014',
                'type': 'cash_payment',
                'date': base_date + timedelta(days=28),
                'description': 'Annual insurance premium',
                'lines': [
                    {'account': '6031', 'debit': Decimal('120000.00'), 'credit': Decimal('0'), 'desc': 'Insurance expense'},
                    {'account': '1013', 'debit': Decimal('0'), 'credit': Decimal('120000.00'), 'desc': 'Bank payment'},
                ]
            },
            
            # 15. Sales Commission
            {
                'number': 'JE-2025-015',
                'type': 'general',
                'date': base_date + timedelta(days=29),
                'description': 'Sales commission payment',
                'lines': [
                    {'account': '6023', 'debit': Decimal('45000.00'), 'credit': Decimal('0'), 'desc': 'Sales commission'},
                    {'account': '1011', 'debit': Decimal('0'), 'credit': Decimal('45000.00'), 'desc': 'Cash payment'},
                ]
            },
        ]
        
        with transaction.atomic():
            for entry_data in entries:
                # Create journal entry
                partner = None
                if 'partner' in entry_data:
                    partner = self.partners.get(entry_data['partner'])
                
                journal_entry = JournalEntry.objects.create(
                    entry_number=entry_data['number'],
                    entry_type=entry_data['type'],
                    entry_date=entry_data['date'],
                    fiscal_year=self.fiscal_year,
                    reference_number=f"REF-{entry_data['number']}",
                    description=entry_data['description'],
                    status='posted',
                    posted_date=timezone.now(),
                    created_by=self.admin_user
                )
                
                # Create journal entry lines
                line_number = 1
                for line_data in entry_data['lines']:
                    account = self.accounts.get(line_data['account'])
                    if account:
                        JournalEntryLine.objects.create(
                            journal_entry=journal_entry,
                            line_number=line_number,
                            account=account,
                            description=line_data['desc'],
                            debit_amount=line_data['debit'],
                            credit_amount=line_data['credit'],
                            partner=partner
                        )
                        line_number += 1
                
                created_count += 1
                
                # Verify double-entry
                if not journal_entry.is_balanced:
                    self.stdout.write(self.style.ERROR(
                        f'   ⚠️  Entry {entry_data["number"]} is not balanced!'
                    ))
        
        return created_count
