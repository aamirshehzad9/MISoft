"""
Management command to populate sample invoices and payments

Usage:
    python manage.py populate_sample_invoices [--clear-existing]

This command creates comprehensive sample invoices and payments
for MI Industries representing sales and purchase cycles
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from accounting.models import (
    Invoice, InvoiceItem, Payment, PaymentAllocation,
    ChartOfAccounts, FiscalYear, BankAccount
)
from partners.models import BusinessPartner
from products.models import Product
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate sample invoices and payments for MI Industries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing invoices and payments before populating',
        )
        parser.add_argument(
            '--random-ids',
            action='store_true',
            help='Use random IDs to avoid collisions',
        )

    def handle(self, *args, **options):
        self.clear_existing = options['clear_existing']
        self.random_ids = options['random_ids']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Populating Sample Invoices & Payments'))
        self.stdout.write(self.style.SUCCESS('Company: MI Industries'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        # Clear existing
        if self.clear_existing:
            self.stdout.write('\n🗑️  Clearing existing data...')
            PaymentAllocation.objects.all().delete()
            Payment.objects.all().delete()
            InvoiceItem.objects.all().delete()
            Invoice.objects.all().delete()
            self.stdout.write(self.style.WARNING('   Deleted existing invoices and payments'))

        # Setup dependencies
        self.admin_user = User.objects.filter(is_superuser=True).first()
        self.fiscal_year = FiscalYear.objects.first()
        
        # Get Partners
        self.customers = BusinessPartner.objects.filter(is_customer=True)
        self.vendors = BusinessPartner.objects.filter(is_vendor=True)
        
        if not self.customers.exists() or not self.vendors.exists():
            self.stdout.write(self.style.ERROR('❌ No partners found. Run populate_sample_transactions first.'))
            return

        # Get Products (Create if not exist)
        self.products = self.get_or_create_products()
        
        # Get Bank Account (Create if not exist)
        self.bank_account = self.get_or_create_bank_account()

        # Create Invoices
        self.stdout.write('\n📝 Step 1: Creating Invoices...')
        self.create_invoices()
        
        # Create Payments
        self.stdout.write('\n💰 Step 2: Creating Payments...')
        self.create_payments()

        self.stdout.write(self.style.SUCCESS('\n✅ Sample invoices and payments populated successfully!'))

    def get_or_create_products(self):
        from products.models import UnitOfMeasure, ProductCategory
        
        # Create UoM
        uom, _ = UnitOfMeasure.objects.get_or_create(
            name='Unit',
            defaults={'symbol': 'pcs', 'uom_type': 'unit'}
        )
        
        # Create Category
        category, _ = ProductCategory.objects.get_or_create(
            name='General',
            defaults={'code': 'GEN'}
        )
        
        products = []
        product_data = [
            {'name': 'Industrial Adhesive X100', 'price': 5000, 'type': 'finished_good'},
            {'name': 'Super Glue 50g', 'price': 200, 'type': 'finished_good'},
            {'name': 'Resin Drum 200L', 'price': 45000, 'type': 'raw_material'},
            {'name': 'Hardener 50L', 'price': 12000, 'type': 'raw_material'},
        ]
        
        for p_data in product_data:
            sku = f"SKU-{random.randint(1000, 9999)}"
            product, _ = Product.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    'product_type': p_data['type'],
                    'selling_price': p_data['price'],
                    'standard_cost': p_data['price'] * 0.7,
                    'code': sku,
                    'base_uom': uom,
                    'category': category
                }
            )
            products.append(product)
        return products

    def get_or_create_bank_account(self):
        # Need a GL account for bank - Explicitly get 1013
        try:
            bank_gl = ChartOfAccounts.objects.get(account_code='1013')
        except ChartOfAccounts.DoesNotExist:
            # Fallback (should not happen in this phase)
            bank_gl = ChartOfAccounts.objects.filter(account_name__icontains='Bank').first()

        bank, created = BankAccount.objects.get_or_create(
            account_number='PK-HBL-123456789',
            defaults={
                'account_name': 'HBL Main Account',
                'bank_name': 'Habib Bank Limited',
                'gl_account': bank_gl,
                'currency': 'PKR'
            }
        )
        
        # Ensure GL account is correct (fix if it was wrong)
        if bank.gl_account != bank_gl:
            self.stdout.write(self.style.WARNING(f"   Fixing Bank GL Account from {bank.gl_account.account_code} to {bank_gl.account_code}"))
            bank.gl_account = bank_gl
            bank.save()
            
        return bank
        return bank

    def create_invoices(self):
        # 1. Sales Invoices
        for i in range(5):
            customer = random.choice(self.customers)
            if self.random_ids:
                suffix = str(int(timezone.now().timestamp() * 1000))[-6:] + str(random.randint(10,99))
                inv_num = f"INV-R-{suffix}"
            else:
                inv_num = f"INV-2025-{100+i}"
                
            invoice = Invoice.objects.create(
                invoice_number=inv_num,
                invoice_type='sales',
                invoice_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                due_date=timezone.now().date() + timedelta(days=30),
                partner=customer,
                status='submitted',
                created_by=self.admin_user
            )
            
            # Add items
            total = 0
            for _ in range(random.randint(1, 3)):
                product = random.choice(self.products)
                qty = random.randint(1, 10)
                price = product.selling_price
                
                item = InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    description=f"Sale of {product.name}",
                    quantity=qty,
                    unit_price=price,
                    tax_percentage=Decimal('17')
                )
                total += Decimal(item.line_total)
            
            invoice.total_amount = total
            invoice.subtotal = total / Decimal('1.17') # Approx
            invoice.tax_amount = total - invoice.subtotal
            invoice.save()
            
            self.create_invoice_journal(invoice)
            self.stdout.write(f"   Created Sales Invoice {invoice.invoice_number}: {invoice.total_amount}")

        # 2. Purchase Invoices
        for i in range(3):
            vendor = random.choice(self.vendors)
            if self.random_ids:
                suffix = str(int(timezone.now().timestamp() * 1000))[-6:] + str(random.randint(10,99))
                inv_num = f"BILL-R-{suffix}"
            else:
                inv_num = f"BILL-2025-{100+i}"
                
            invoice = Invoice.objects.create(
                invoice_number=inv_num,
                invoice_type='purchase',
                invoice_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                due_date=timezone.now().date() + timedelta(days=30),
                partner=vendor,
                status='submitted',
                created_by=self.admin_user
            )
            
            # Add items
            total = 0
            for _ in range(random.randint(1, 3)):
                product = random.choice(self.products)
                qty = random.randint(10, 50)
                price = product.standard_cost
                
                item = InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    description=f"Purchase of {product.name}",
                    quantity=qty,
                    unit_price=price,
                    tax_percentage=Decimal('17')
                )
                total += Decimal(item.line_total)
            
            invoice.total_amount = total
            invoice.subtotal = total / Decimal('1.17')
            invoice.tax_amount = total - invoice.subtotal
            invoice.save()
            
            self.create_invoice_journal(invoice)
            self.stdout.write(f"   Created Purchase Invoice {invoice.invoice_number}: {invoice.total_amount}")

    def create_payments(self):
        # 1. Receive Payment for a random Sales Invoice
        sales_invoice = Invoice.objects.filter(invoice_type='sales', status='submitted').first()
        if sales_invoice:
            amount = sales_invoice.total_amount / 2 # Partial payment
            if self.random_ids:
                suffix = str(int(timezone.now().timestamp() * 1000))[-6:] + str(random.randint(10,99))
                pay_num = f"RCPT-R-{suffix}"
            else:
                pay_num = f"RCPT-2025-001"
                
            payment = Payment.objects.create(
                payment_number=pay_num,
                payment_type='receipt',
                payment_date=timezone.now().date(),
                partner=sales_invoice.partner,
                amount=amount,
                payment_mode='bank_transfer',
                bank_account=self.bank_account,
                created_by=self.admin_user
            )
            
            PaymentAllocation.objects.create(
                payment=payment,
                invoice=sales_invoice,
                allocated_amount=amount
            )
            
            sales_invoice.paid_amount += amount
            sales_invoice.status = 'partially_paid'
            sales_invoice.save()
            
            self.create_payment_journal(payment)
            self.stdout.write(f"   Created Receipt {payment.payment_number} for Invoice {sales_invoice.invoice_number}")

        # 2. Make Payment for a random Purchase Invoice
        purchase_invoice = Invoice.objects.filter(invoice_type='purchase', status='submitted').first()
        if purchase_invoice:
            amount = purchase_invoice.total_amount # Full payment
            if self.random_ids:
                suffix = str(int(timezone.now().timestamp() * 1000))[-6:] + str(random.randint(10,99))
                pay_num = f"PAY-R-{suffix}"
            else:
                pay_num = f"PAY-2025-001"

            payment = Payment.objects.create(
                payment_number=pay_num,
                payment_type='payment',
                payment_date=timezone.now().date(),
                partner=purchase_invoice.partner,
                amount=amount,
                payment_mode='cheque',
                bank_account=self.bank_account,
                created_by=self.admin_user
            )
            
            PaymentAllocation.objects.create(
                payment=payment,
                invoice=purchase_invoice,
                allocated_amount=amount
            )
            
            purchase_invoice.paid_amount += amount
            purchase_invoice.status = 'paid'
            purchase_invoice.save()
            
            self.create_payment_journal(payment)
            self.stdout.write(f"   Created Payment {payment.payment_number} for Bill {purchase_invoice.invoice_number}")

    def create_invoice_journal(self, invoice):
        from accounting.models import JournalEntry, JournalEntryLine
        
        # Accounts
        acc_debtors = ChartOfAccounts.objects.get(account_code='1021')
        acc_creditors = ChartOfAccounts.objects.get(account_code='2011')
        acc_sales = ChartOfAccounts.objects.get(account_code='4011')
        acc_purchases = ChartOfAccounts.objects.get(account_code='5011')
        acc_tax = ChartOfAccounts.objects.get(account_code='2021') # Sales Tax Payable
        
        je = JournalEntry.objects.create(
            entry_number=invoice.invoice_number, # Use same number for simplicity
            entry_type='sales' if invoice.invoice_type == 'sales' else 'purchase',
            entry_date=invoice.invoice_date,
            fiscal_year=self.fiscal_year,
            description=f"Journal for {invoice.invoice_number}",
            status='posted',
            posted_date=timezone.now(),
            created_by=self.admin_user
        )
        
        if invoice.invoice_type == 'sales':
            # Dr Customer (Total)
            JournalEntryLine.objects.create(journal_entry=je, account=acc_debtors, debit_amount=invoice.total_amount, credit_amount=0, description="Customer Invoice")
            # Cr Sales (Net)
            JournalEntryLine.objects.create(journal_entry=je, account=acc_sales, debit_amount=0, credit_amount=invoice.subtotal, description="Sales Revenue")
            # Cr Tax (Tax)
            if invoice.tax_amount > 0:
                JournalEntryLine.objects.create(journal_entry=je, account=acc_tax, debit_amount=0, credit_amount=invoice.tax_amount, description="Sales Tax")
        else:
            # Cr Vendor (Total)
            JournalEntryLine.objects.create(journal_entry=je, account=acc_creditors, debit_amount=0, credit_amount=invoice.total_amount, description="Vendor Bill")
            # Dr Purchases (Net)
            JournalEntryLine.objects.create(journal_entry=je, account=acc_purchases, debit_amount=invoice.subtotal, credit_amount=0, description="Purchases")
            # Dr Tax (Input Tax) - Using same tax account for simplicity in legacy
            if invoice.tax_amount > 0:
                JournalEntryLine.objects.create(journal_entry=je, account=acc_tax, debit_amount=invoice.tax_amount, credit_amount=0, description="Input Tax")

    def create_payment_journal(self, payment):
        from accounting.models import JournalEntry, JournalEntryLine
        
        # Accounts
        acc_debtors = ChartOfAccounts.objects.get(account_code='1021')
        acc_creditors = ChartOfAccounts.objects.get(account_code='2011')
        acc_bank = self.bank_account.gl_account
        
        je = JournalEntry.objects.create(
            entry_number=payment.payment_number,
            entry_type='cash_receipt' if payment.payment_type == 'receipt' else 'cash_payment',
            entry_date=payment.payment_date,
            fiscal_year=self.fiscal_year,
            description=f"Journal for {payment.payment_number}",
            status='posted',
            posted_date=timezone.now(),
            created_by=self.admin_user
        )
        
        if payment.payment_type == 'receipt':
            # Dr Bank
            JournalEntryLine.objects.create(journal_entry=je, account=acc_bank, debit_amount=payment.amount, credit_amount=0, description="Payment Received")
            # Cr Customer
            JournalEntryLine.objects.create(journal_entry=je, account=acc_debtors, debit_amount=0, credit_amount=payment.amount, description="Customer Payment")
        else:
            # Dr Vendor
            JournalEntryLine.objects.create(journal_entry=je, account=acc_creditors, debit_amount=payment.amount, credit_amount=0, description="Vendor Payment")
            # Cr Bank
            JournalEntryLine.objects.create(journal_entry=je, account=acc_bank, debit_amount=0, credit_amount=payment.amount, description="Payment Made")
