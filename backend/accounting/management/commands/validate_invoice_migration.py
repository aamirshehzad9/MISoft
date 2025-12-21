"""
Management command to validate invoice and payment migration

Usage:
    python manage.py validate_invoice_migration

This command checks:
1. Invoice Counts and Amounts (Legacy vs V2)
2. Payment Counts and Amounts (Legacy vs V2)
3. Voucher Integrity (Balanced Debits/Credits)
"""

from django.core.management.base import BaseCommand
from django.db.models import Sum
from accounting.models import Invoice, Payment, VoucherV2, VoucherEntryV2

class Command(BaseCommand):
    help = 'Validate invoice and payment migration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('VALIDATING INVOICE & PAYMENT MIGRATION'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        errors = []
        
        # 1. Validate Invoices
        self.stdout.write('\n📄 Validating Invoices...')
        
        # Sales Invoices
        legacy_si_count = Invoice.objects.filter(invoice_type='sales').count()
        legacy_si_amount = Invoice.objects.filter(invoice_type='sales').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Only count vouchers migrated from Invoices (not JEs)
        v2_si_qs = VoucherV2.objects.filter(voucher_type='SI', migrated_from_legacy__isnull=True)
        v2_si_count = v2_si_qs.count()
        v2_si_amount = v2_si_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        self.print_comparison("Sales Invoices Count", legacy_si_count, v2_si_count)
        self.print_comparison("Sales Invoices Amount", legacy_si_amount, v2_si_amount)
        
        if legacy_si_count != v2_si_count: errors.append("Sales Invoice count mismatch")
        if legacy_si_amount != v2_si_amount: errors.append("Sales Invoice amount mismatch")

        # Purchase Invoices
        legacy_pi_count = Invoice.objects.filter(invoice_type='purchase').count()
        legacy_pi_amount = Invoice.objects.filter(invoice_type='purchase').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        v2_pi_qs = VoucherV2.objects.filter(voucher_type='PI', migrated_from_legacy__isnull=True)
        v2_pi_count = v2_pi_qs.count()
        v2_pi_amount = v2_pi_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        self.print_comparison("Purchase Invoices Count", legacy_pi_count, v2_pi_count)
        self.print_comparison("Purchase Invoices Amount", legacy_pi_amount, v2_pi_amount)
        
        if legacy_pi_count != v2_pi_count: errors.append("Purchase Invoice count mismatch")
        if legacy_pi_amount != v2_pi_amount: errors.append("Purchase Invoice amount mismatch")

        # 2. Validate Payments
        self.stdout.write('\n💰 Validating Payments...')
        
        # Receipts
        legacy_rcpt_count = Payment.objects.filter(payment_type='receipt').count()
        legacy_rcpt_amount = Payment.objects.filter(payment_type='receipt').aggregate(Sum('amount'))['amount__sum'] or 0
        
        v2_rcpt_qs = VoucherV2.objects.filter(voucher_type__in=['CRV', 'BRV'], migrated_from_legacy__isnull=True)
        v2_rcpt_count = v2_rcpt_qs.count()
        v2_rcpt_amount = v2_rcpt_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        self.print_comparison("Receipts Count", legacy_rcpt_count, v2_rcpt_count)
        self.print_comparison("Receipts Amount", legacy_rcpt_amount, v2_rcpt_amount)
        
        if legacy_rcpt_count != v2_rcpt_count: errors.append("Receipt count mismatch")
        if legacy_rcpt_amount != v2_rcpt_amount: errors.append("Receipt amount mismatch")

        # Payments
        legacy_pay_count = Payment.objects.filter(payment_type='payment').count()
        legacy_pay_amount = Payment.objects.filter(payment_type='payment').aggregate(Sum('amount'))['amount__sum'] or 0
        
        v2_pay_qs = VoucherV2.objects.filter(voucher_type__in=['CPV', 'BPV'], migrated_from_legacy__isnull=True)
        v2_pay_count = v2_pay_qs.count()
        v2_pay_amount = v2_pay_qs.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        self.print_comparison("Payments Count", legacy_pay_count, v2_pay_count)
        self.print_comparison("Payments Amount", legacy_pay_amount, v2_pay_amount)
        
        if legacy_pay_count != v2_pay_count: errors.append("Payment count mismatch")
        if legacy_pay_amount != v2_pay_amount: errors.append("Payment amount mismatch")

        # 3. Validate Voucher Integrity
        self.stdout.write('\n⚖️  Validating Voucher Integrity...')
        unbalanced_vouchers = 0
        for voucher in VoucherV2.objects.all():
            try:
                voucher.validate_double_entry()
            except ValueError:
                unbalanced_vouchers += 1
                self.stdout.write(self.style.ERROR(f"   Unbalanced Voucher: {voucher.voucher_number}"))
        
        if unbalanced_vouchers == 0:
            self.stdout.write(self.style.SUCCESS("   All vouchers are balanced."))
        else:
            errors.append(f"{unbalanced_vouchers} unbalanced vouchers found")

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
        self.stdout.write(f"   {label:<30} Legacy: {str(legacy):<15} V2: {str(v2):<15} {style(status)}")
