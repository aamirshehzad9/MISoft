"""
Management command to migrate invoices and payments to VoucherV2

Usage:
    python manage.py migrate_invoices [--dry-run]

This command migrates:
1. Sales Invoices -> VoucherV2 (Type: SI)
2. Purchase Invoices -> VoucherV2 (Type: PI)
3. Payments -> VoucherV2 (Type: CRV, CPV, BRV, BPV)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from accounting.models import (
    Invoice, Payment, VoucherV2, VoucherEntryV2,
    AccountV2, CurrencyV2
)
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate invoices and payments from legacy to VoucherV2'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration without committing changes',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Invoice & Payment Migration - Legacy to V2'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 DRY RUN MODE - No changes will be committed\n'))
        
        # Setup
        self.base_currency = CurrencyV2.objects.get(currency_code='PKR')
        self.load_accounts()
        
        # Migrate Invoices
        self.stdout.write('\n🔄 Step 1: Migrating Invoices...')
        self.migrate_invoices()
        
        # Migrate Payments
        self.stdout.write('\n🔄 Step 2: Migrating Payments...')
        self.migrate_payments()
        
        self.stdout.write('\n' + '=' * 80)
        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - No changes committed'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ MIGRATION COMPLETE'))
        self.stdout.write('=' * 80 + '\n')

    def load_accounts(self):
        """Load required V2 accounts"""
        try:
            self.acc_debtors = AccountV2.objects.get(code='1021') # Trade Debtors
            self.acc_creditors = AccountV2.objects.get(code='2011') # Trade Creditors
            self.acc_sales = AccountV2.objects.get(code='4011') # Sales
            self.acc_purchases = AccountV2.objects.get(code='5011') # Purchases (Materials)
            self.acc_tax_payable = AccountV2.objects.get(code='2021') # Sales Tax Payable
            self.acc_bank = AccountV2.objects.get(code='1013') # Bank
            self.acc_cash = AccountV2.objects.get(code='1011') # Cash
        except AccountV2.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'❌ Critical Account Missing: {e}'))
            raise

    def migrate_invoices(self):
        invoices = Invoice.objects.all()
        count = 0
        
        for invoice in invoices:
            # Check if already migrated (by checking voucher number match)
            # Since we don't have a direct link field on VoucherV2 for Invoice (only JournalEntry),
            # we'll use voucher_number = invoice_number
            if VoucherV2.objects.filter(voucher_number=invoice.invoice_number).exists():
                continue

            if self.migrate_single_invoice(invoice):
                count += 1
                self.stdout.write(f"   Migrated {invoice.invoice_number}")
        
        self.stdout.write(f"   Total Invoices Migrated: {count}")

    def migrate_single_invoice(self, invoice):
        try:
            voucher_type = 'SI' if invoice.invoice_type == 'sales' else 'PI'
            
            if not self.dry_run:
                with transaction.atomic():
                    voucher = VoucherV2.objects.create(
                        voucher_number=invoice.invoice_number,
                        voucher_type=voucher_type,
                        voucher_date=invoice.invoice_date,
                        party=invoice.partner,
                        total_amount=invoice.total_amount,
                        currency=self.base_currency,
                        status='posted' if invoice.status != 'draft' else 'draft',
                        narration=f"Migrated {invoice.invoice_type} invoice",
                        created_by=invoice.created_by
                    )
                    
                    # 1. Party Entry (Dr for SI, Cr for PI)
                    party_account = self.acc_debtors if voucher_type == 'SI' else self.acc_creditors
                    debit = invoice.total_amount if voucher_type == 'SI' else 0
                    credit = invoice.total_amount if voucher_type == 'PI' else 0
                    
                    VoucherEntryV2.objects.create(
                        voucher=voucher,
                        account=party_account,
                        debit_amount=debit,
                        credit_amount=credit,
                        currency_amount=invoice.total_amount
                    )
                    
                    # 2. Line Items (Revenue/Expense)
                    # For simplicity in migration, we aggregate by tax/net
                    # Ideally we iterate items, but let's do summary for now to ensure balance
                    
                    net_amount = invoice.subtotal
                    tax_amount = invoice.tax_amount
                    
                    # Revenue/Expense Entry
                    income_account = self.acc_sales if voucher_type == 'SI' else self.acc_purchases
                    debit = net_amount if voucher_type == 'PI' else 0
                    credit = net_amount if voucher_type == 'SI' else 0
                    
                    VoucherEntryV2.objects.create(
                        voucher=voucher,
                        account=income_account,
                        debit_amount=debit,
                        credit_amount=credit,
                        currency_amount=net_amount,
                        description="Invoice Subtotal"
                    )
                    
                    # Tax Entry
                    if tax_amount > 0:
                        # For SI: Cr Tax Payable
                        # For PI: Dr Tax Receivable (or Expense if not recoverable) -> Let's use Tax Payable (offset) for now
                        tax_account = self.acc_tax_payable
                        debit = tax_amount if voucher_type == 'PI' else 0
                        credit = tax_amount if voucher_type == 'SI' else 0
                        
                        VoucherEntryV2.objects.create(
                            voucher=voucher,
                            account=tax_account,
                            debit_amount=debit,
                            credit_amount=credit,
                            currency_amount=tax_amount,
                            description="Tax Amount"
                        )
            
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error migrating {invoice.invoice_number}: {e}"))
            return False

    def migrate_payments(self):
        payments = Payment.objects.all()
        count = 0
        
        for payment in payments:
            if VoucherV2.objects.filter(voucher_number=payment.payment_number).exists():
                continue

            if self.migrate_single_payment(payment):
                count += 1
                self.stdout.write(f"   Migrated {payment.payment_number}")
        
        self.stdout.write(f"   Total Payments Migrated: {count}")

    def migrate_single_payment(self, payment):
        try:
            # Determine Voucher Type
            if payment.payment_type == 'receipt':
                voucher_type = 'BRV' if payment.payment_mode in ['cheque', 'bank_transfer', 'online'] else 'CRV'
            else:
                voucher_type = 'BPV' if payment.payment_mode in ['cheque', 'bank_transfer', 'online'] else 'CPV'
            
            if not self.dry_run:
                with transaction.atomic():
                    voucher = VoucherV2.objects.create(
                        voucher_number=payment.payment_number,
                        voucher_type=voucher_type,
                        voucher_date=payment.payment_date,
                        party=payment.partner,
                        total_amount=payment.amount,
                        currency=self.base_currency,
                        status='posted',
                        narration=f"Migrated {payment.payment_type}",
                        created_by=payment.created_by
                    )
                    
                    # 1. Bank/Cash Entry
                    is_bank = voucher_type in ['BRV', 'BPV']
                    bank_cash_account = self.acc_bank if is_bank else self.acc_cash
                    
                    # Receipt: Dr Bank/Cash
                    # Payment: Cr Bank/Cash
                    debit = payment.amount if payment.payment_type == 'receipt' else 0
                    credit = payment.amount if payment.payment_type == 'payment' else 0
                    
                    VoucherEntryV2.objects.create(
                        voucher=voucher,
                        account=bank_cash_account,
                        debit_amount=debit,
                        credit_amount=credit,
                        currency_amount=payment.amount
                    )
                    
                    # 2. Party Entry
                    # Receipt: Cr Customer (Trade Debtors)
                    # Payment: Dr Vendor (Trade Creditors)
                    party_account = self.acc_debtors if payment.partner.is_customer else self.acc_creditors
                    
                    debit = payment.amount if payment.payment_type == 'payment' else 0
                    credit = payment.amount if payment.payment_type == 'receipt' else 0
                    
                    VoucherEntryV2.objects.create(
                        voucher=voucher,
                        account=party_account,
                        debit_amount=debit,
                        credit_amount=credit,
                        currency_amount=payment.amount
                    )
            
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error migrating {payment.payment_number}: {e}"))
            return False
