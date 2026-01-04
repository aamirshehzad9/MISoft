"""
Unit Tests for NumberingService

Tests cover:
- Thread-safe number generation
- Automatic reset logic
- Multi-entity support
- Concurrent number generation
- Error handling

Target: 100% pass rate
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from threading import Thread
from time import sleep

from accounting.models import NumberingScheme, Entity, CurrencyV2
from accounting.services import NumberingService

User = get_user_model()


class NumberingServiceTestCase(TestCase):
    """Test NumberingService functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create currency
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        
        # Create entity
        self.entity = Entity.objects.create(
            entity_code='TEST',
            entity_name='Test Entity',
            country='USA',
            functional_currency=self.usd,
            created_by=self.user
        )
        
        # Create global numbering scheme
        self.invoice_scheme = NumberingScheme.objects.create(
            scheme_name='Invoice Numbering',
            document_type='invoice',
            prefix='INV',
            date_format='YYYY',
            separator='-',
            padding=4,
            reset_frequency='yearly',
            created_by=self.user
        )
    
    def test_generate_number_basic(self):
        """Test basic number generation"""
        number = NumberingService.generate_number('invoice')
        
        current_year = date.today().year
        expected = f'INV-{current_year}-0001'
        self.assertEqual(number, expected)
    
    def test_generate_number_increments(self):
        """Test that numbers increment correctly"""
        num1 = NumberingService.generate_number('invoice')
        num2 = NumberingService.generate_number('invoice')
        num3 = NumberingService.generate_number('invoice')
        
        current_year = date.today().year
        self.assertEqual(num1, f'INV-{current_year}-0001')
        self.assertEqual(num2, f'INV-{current_year}-0002')
        self.assertEqual(num3, f'INV-{current_year}-0003')
    
    def test_generate_number_with_entity(self):
        """Test entity-specific number generation"""
        # Create entity-specific scheme
        entity_scheme = NumberingScheme.objects.create(
            scheme_name='Entity Invoice Numbering',
            document_type='voucher',
            prefix='VCH',
            entity=self.entity,
            padding=5,
            created_by=self.user
        )
        
        number = NumberingService.generate_number('voucher', entity=self.entity)
        self.assertEqual(number, 'VCH-00001')
    
    def test_generate_number_fallback_to_global(self):
        """Test fallback to global scheme when entity-specific not found"""
        # Create global voucher scheme
        global_scheme = NumberingScheme.objects.create(
            scheme_name='Global Voucher',
            document_type='voucher',
            prefix='GVCH',
            padding=3,
            created_by=self.user
        )
        
        # Request with entity but no entity-specific scheme exists
        number = NumberingService.generate_number('voucher', entity=self.entity)
        self.assertEqual(number, 'GVCH-001')
    
    def test_generate_number_no_scheme_raises_error(self):
        """Test that error is raised when no scheme exists"""
        with self.assertRaises(ValidationError) as context:
            NumberingService.generate_number('nonexistent_type')
        
        self.assertIn('No active numbering scheme found', str(context.exception))
    
    def test_automatic_reset_yearly(self):
        """Test automatic yearly reset"""
        # Set last reset to previous year
        self.invoice_scheme.last_reset_date = date(2024, 12, 31)
        self.invoice_scheme.next_number = 500
        self.invoice_scheme.save()
        
        # Generate number - should reset to 1
        number = NumberingService.generate_number('invoice')
        current_year = date.today().year
        self.assertEqual(number, f'INV-{current_year}-0001')
        
        # Verify scheme was updated
        self.invoice_scheme.refresh_from_db()
        self.assertEqual(self.invoice_scheme.next_number, 2)  # Incremented after generation
    
    def test_preview_next_number(self):
        """Test preview without generating"""
        preview = NumberingService.preview_next_number('invoice')
        
        current_year = date.today().year
        expected = f'INV-{current_year}-0001'
        self.assertEqual(preview, expected)
        
        # Verify counter wasn't incremented
        self.invoice_scheme.refresh_from_db()
        self.assertEqual(self.invoice_scheme.next_number, 1)
    
    def test_preview_next_number_no_scheme(self):
        """Test preview returns None when no scheme exists"""
        preview = NumberingService.preview_next_number('nonexistent')
        self.assertIsNone(preview)
    
    def test_reset_counter_manual(self):
        """Test manual counter reset"""
        # Generate some numbers
        NumberingService.generate_number('invoice')
        NumberingService.generate_number('invoice')
        NumberingService.generate_number('invoice')
        
        # Reset counter
        result = NumberingService.reset_counter('invoice', reset_to=1)
        self.assertTrue(result)
        
        # Next number should be 1
        number = NumberingService.generate_number('invoice')
        current_year = date.today().year
        self.assertEqual(number, f'INV-{current_year}-0001')
    
    def test_reset_counter_no_scheme(self):
        """Test reset returns False when no scheme exists"""
        result = NumberingService.reset_counter('nonexistent')
        self.assertFalse(result)
    
    def test_get_scheme_info(self):
        """Test getting scheme information"""
        info = NumberingService.get_scheme_info('invoice')
        
        self.assertIsNotNone(info)
        self.assertEqual(info['scheme_name'], 'Invoice Numbering')
        self.assertEqual(info['document_type'], 'invoice')
        self.assertEqual(info['next_number'], 1)
        self.assertEqual(info['reset_frequency'], 'yearly')
        self.assertIsNone(info['entity'])
    
    def test_get_scheme_info_no_scheme(self):
        """Test get_scheme_info returns None when no scheme exists"""
        info = NumberingService.get_scheme_info('nonexistent')
        self.assertIsNone(info)
    
    def test_custom_date_formatting(self):
        """Test number generation with custom date"""
        custom_date = date(2024, 6, 15)
        
        # Create scheme with date format
        scheme = NumberingScheme.objects.create(
            scheme_name='Date Test',
            document_type='payment',
            prefix='PAY',
            date_format='YYYYMMDD',
            separator='-',
            padding=3,
            created_by=self.user
        )
        
        number = NumberingService.generate_number('payment', custom_date=custom_date)
        self.assertEqual(number, 'PAY-20240615-001')


class NumberingServiceConcurrencyTestCase(TransactionTestCase):
    """Test concurrent number generation (thread safety)"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create numbering scheme
        self.scheme = NumberingScheme.objects.create(
            scheme_name='Concurrent Test',
            document_type='test_doc',
            prefix='TEST',
            padding=4,
            reset_frequency='never',
            created_by=self.user
        )
    
    def test_concurrent_number_generation(self):
        """Test that concurrent requests generate unique numbers"""
        generated_numbers = []
        
        def generate_and_store():
            try:
                number = NumberingService.generate_number('test_doc')
                generated_numbers.append(number)
            except Exception as e:
                generated_numbers.append(f"ERROR: {e}")
        
        # Create 10 threads to generate numbers concurrently
        threads = []
        for i in range(10):
            thread = Thread(target=generate_and_store)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all numbers are unique
        self.assertEqual(len(generated_numbers), 10)
        self.assertEqual(len(set(generated_numbers)), 10)  # All unique
        
        # Verify numbers are sequential
        numbers = sorted(generated_numbers)
        expected = [f'TEST-{str(i).zfill(4)}' for i in range(1, 11)]
        self.assertEqual(numbers, expected)
