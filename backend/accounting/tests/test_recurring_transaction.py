from django.test import TestCase
from django.utils import timezone
from accounting.models import RecurringTransaction
from datetime import date, timedelta
from django.core.exceptions import ValidationError

class RecurringTransactionModelTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'Monthly Rent',
            'document_type': 'bill',
            'frequency': 'monthly',
            'start_date': date.today(),
            'next_run_date': date.today(),
            'template_data': {'amount': 1000, 'description': 'Office Rent'},
            'is_active': True,
            'auto_post': False
        }

    def test_create_recurring_transaction(self):
        """Test creating a valid recurring transaction"""
        rt = RecurringTransaction.objects.create(**self.valid_data)
        self.assertEqual(rt.name, 'Monthly Rent')
        self.assertEqual(rt.frequency, 'monthly')

    def test_invalid_frequency(self):
        """Test that invalid frequency raises ValidationError"""
        self.valid_data['frequency'] = 'hourly'
        rt = RecurringTransaction(**self.valid_data)
        with self.assertRaises(ValidationError):
            rt.full_clean()

    def test_next_run_date_required(self):
        """Test that next_run_date is required"""
        self.valid_data['next_run_date'] = None
        rt = RecurringTransaction(**self.valid_data)
        with self.assertRaises(ValidationError):
            rt.full_clean()
    
    def test_end_date_validation(self):
        """Test start_date cannot be after end_date"""
        self.valid_data['end_date'] = date.today() - timedelta(days=1)
        rt = RecurringTransaction(**self.valid_data)
        with self.assertRaises(ValidationError):
            rt.full_clean()
