from django.test import TestCase
from django.utils import timezone
from accounting.models import RecurringTransaction, VoucherV2
from accounting.services.recurring_service import RecurringTransactionService
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

class RecurringServiceTestCase(TestCase):
    def setUp(self):
        self.template_data = {
            'voucher_number': 'REC-001', 
            'voucher_type': 'JV',
            'date': str(date.today()),
            'description': 'Monthly Rent Payment',
            'entries': [
                 # Simplified for service test, assuming VoucherService handles detailed validation
                {'account_id': 1, 'amount': 1000, 'type': 'debit'},
                {'account_id': 2, 'amount': 1000, 'type': 'credit'}
            ]
        }
        self.rt = RecurringTransaction.objects.create(
            name='Rent',
            document_type='bill',
            frequency='monthly',
            start_date=timezone.now().date(),
            next_run_date=timezone.now().date(), # Due today
            template_data=self.template_data,
            is_active=True,
            auto_post=True
        )

    def test_generate_due_transactions(self):
        """Test generation of due transactions"""
        # Mock VoucherService to avoid full voucher creation complexity if desired, 
        # or rely on integration if VoucherService is robust.
        # Here we test the ORCHESTRATION logic of RecurringService.
        
        with patch('accounting.services.voucher_service.VoucherService.create_voucher') as mock_create:
            mock_create.return_value = MagicMock(id=1, voucher_number='REC-GEN-001')
            
            generated = RecurringTransactionService.generate_due_transactions()
            
            self.assertEqual(len(generated), 1)
            self.assertEqual(generated[0], 'REC-GEN-001')
            
            # Check next_run_date updated
            self.rt.refresh_from_db()
            expected_next = date.today() + timedelta(days=31) # Approx for monthly, implies logic check
            # For exact month math, dateutil.relativedelta is better, assuming implementation uses it
            self.assertTrue(self.rt.next_run_date > date.today())
            
    def test_future_start_date_not_generated(self):
        self.rt.next_run_date = date.today() + timedelta(days=1)
        self.rt.save()
        
        generated = RecurringTransactionService.generate_due_transactions()
        self.assertEqual(len(generated), 0)

    def test_inactive_not_generated(self):
        self.rt.is_active = False
        self.rt.save()
        generated = RecurringTransactionService.generate_due_transactions()
        self.assertEqual(len(generated), 0)

    @patch('accounting.services.recurring_service.GmailSenderService.send_email')
    def test_notification_sent(self, mock_email):
        """Test that notification is sent if configured"""
        self.rt.notification_emails = 'test@example.com'
        self.rt.save()
        
        # Assuming service logic sends email if auto-post is successful
        with patch('accounting.services.voucher_service.VoucherService.create_voucher'):
             RecurringTransactionService.generate_due_transactions()
             # Logic dep: Does generate_due_transactions trigger email? 
             # Subtask 1.4.2 check: "Add email notification for generated documents"
             # Since it's a backend task, mock email service
             pass # Logic will be verified by implementation
             
        self.assertTrue(mock_email.called)

    def test_calculate_next_date(self):
        """Test frequency calculations"""
        base_date = date(2025, 1, 1)
        
        # Monthly
        next_date = RecurringTransactionService.calculate_next_date(base_date, 'monthly')
        self.assertEqual(next_date, date(2025, 2, 1))
        
        # Quarterly
        next_date = RecurringTransactionService.calculate_next_date(base_date, 'quarterly')
        self.assertEqual(next_date, date(2025, 4, 1))
        
        # Yearly
        next_date = RecurringTransactionService.calculate_next_date(base_date, 'yearly')
        self.assertEqual(next_date, date(2026, 1, 1))

