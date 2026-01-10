from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import transaction, models
from accounting.models import RecurringTransaction
from accounting.services.voucher_service import VoucherService
from accounting.services.gmail_service import GmailSenderService
from django.contrib.auth import get_user_model

User = get_user_model()

class RecurringTransactionService:
    @staticmethod
    def generate_due_transactions():
        """
        Generates vouchers for all due recurring transactions.
        Returns list of generated voucher numbers.
        """
        today = timezone.now().date()
        due_transactions = RecurringTransaction.objects.filter(
            is_active=True,
            next_run_date__lte=today
        )
        
        generated_vouchers = []
        
        for rt in due_transactions:
            if rt.end_date and rt.next_run_date > rt.end_date:
                rt.is_active = False
                rt.save()
                continue
                
            with transaction.atomic():
                try:
                    # prepare voucher data from template
                    voucher_data = rt.template_data.copy()
                    # Ensure date mapping if template uses generic 'date' or we just override
                    voucher_data['voucher_date'] = str(rt.next_run_date)
                    voucher_data['reference_number'] = f"REC-{rt.id}-{rt.next_run_date}"
                    if 'description' not in voucher_data:
                        voucher_data['narration'] = f"{rt.name} - {rt.next_run_date}"
                    else:
                        voucher_data['narration'] = voucher_data.pop('description')
                    
                    # Create Voucher
                    # Trying to fetch a system user
                    system_user = User.objects.filter(is_superuser=True).first()
                    
                    voucher = VoucherService.create_voucher(voucher_data, system_user)
                    
                    if rt.auto_post:
                        pass

                    generated_vouchers.append(voucher.voucher_number)

                    # Update Next Run Date
                    rt.next_run_date = RecurringTransactionService.calculate_next_date(rt.next_run_date, rt.frequency)
                    rt.save()

                    if rt.notification_emails:
                        try:
                            GmailSenderService.send_email(
                                sender_email='system@misoft.com', # Or configured default
                                recipient_list=rt.notification_emails.split(','),
                                subject=f"Recurring Transaction Generated: {rt.name}",
                                body=f"Recurring transaction {rt.name} has been processed. Voucher: {voucher.voucher_number}"
                            )
                        except Exception as email_err:
                            print(f"Failed to send recurring notification: {email_err}")

                except Exception as e:
                    # Log error
                    print(f"Error processing RecurringTransaction {rt.id}: {e}")
                    # Don't break loop, try next
                    continue

        return generated_vouchers

    @staticmethod
    def calculate_next_date(current_date, frequency):
        if frequency == 'daily':
            return current_date + timedelta(days=1)
        elif frequency == 'weekly':
            return current_date + timedelta(weeks=1)
        elif frequency == 'monthly':
            return current_date + relativedelta(months=1)
        elif frequency == 'quarterly':
            return current_date + relativedelta(months=3)
        elif frequency == 'yearly':
            return current_date + relativedelta(years=1)
        return current_date
