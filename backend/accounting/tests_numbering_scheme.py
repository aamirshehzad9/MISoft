"""
Unit Tests for NumberingScheme Model

Tests cover:
- Model creation and validation
- Number generation and formatting
- Reset frequency logic
- Preview generation
- Unique constraints
- Multi-entity support

Target: 100% pass rate
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, timedelta

from accounting.models import NumberingScheme, Entity, CurrencyV2

User = get_user_model()


class NumberingSchemeModelTestCase(TestCase):
    """Test NumberingScheme model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create currency for entity
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
    
    def test_numbering_scheme_creation(self):
        """Test creating a numbering scheme"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Invoice Numbering',
            document_type='invoice',
            prefix='INV',
            date_format='YYYY',
            separator='-',
            padding=4,
            reset_frequency='yearly',
            created_by=self.user
        )
        
        self.assertEqual(scheme.scheme_name, 'Invoice Numbering')
        self.assertEqual(scheme.document_type, 'invoice')
        self.assertEqual(scheme.prefix, 'INV')
        self.assertEqual(scheme.next_number, 1)
        self.assertTrue(scheme.is_active)
    
    def test_generate_preview_with_prefix_year_sequence(self):
        """Test preview generation: INV-2025-0001"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Invoice Scheme',
            document_type='invoice',
            prefix='INV',
            date_format='YYYY',
            separator='-',
            padding=4,
            next_number=1,
            created_by=self.user
        )
        
        preview = scheme.generate_preview()
        current_year = date.today().year
        expected = f'INV-{current_year}-0001'
        self.assertEqual(preview, expected)
    
    def test_generate_preview_with_yearmonth(self):
        """Test preview generation: VCH/202501/00001"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Voucher Scheme',
            document_type='voucher',
            prefix='VCH',
            date_format='YYYYMM',
            separator='/',
            padding=5,
            next_number=1,
            created_by=self.user
        )
        
        preview = scheme.generate_preview()
        today = date.today()
        expected = f'VCH/{today.year}{today.month:02d}/00001'
        self.assertEqual(preview, expected)
    
    def test_generate_preview_with_suffix(self):
        """Test preview generation with suffix"""
        scheme = NumberingScheme.objects.create(
            scheme_name='PO Scheme',
            document_type='purchase_order',
            prefix='PO',
            suffix='END',
            separator='-',
            padding=3,
            next_number=5,
            created_by=self.user
        )
        
        preview = scheme.generate_preview()
        self.assertEqual(preview, 'PO-005-END')
    
    def test_should_reset_yearly(self):
        """Test yearly reset logic"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Yearly Reset',
            document_type='invoice',
            prefix='INV',
            reset_frequency='yearly',
            last_reset_date=date(2024, 12, 31),
            created_by=self.user
        )
        
        # Should reset if last reset was in previous year
        self.assertTrue(scheme.should_reset())
        
        # Should not reset if last reset was this year
        scheme.last_reset_date = date.today()
        self.assertFalse(scheme.should_reset())
    
    def test_should_reset_monthly(self):
        """Test monthly reset logic"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Monthly Reset',
            document_type='voucher',
            prefix='VCH',
            reset_frequency='monthly',
            last_reset_date=date.today() - timedelta(days=35),
            created_by=self.user
        )
        
        # Should reset if last reset was in previous month
        self.assertTrue(scheme.should_reset())
    
    def test_should_reset_daily(self):
        """Test daily reset logic"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Daily Reset',
            document_type='receipt',
            prefix='RCP',
            reset_frequency='daily',
            last_reset_date=date.today() - timedelta(days=1),
            created_by=self.user
        )
        
        # Should reset if last reset was yesterday
        self.assertTrue(scheme.should_reset())
        
        # Should not reset if last reset was today
        scheme.last_reset_date = date.today()
        self.assertFalse(scheme.should_reset())
    
    def test_should_reset_never(self):
        """Test never reset logic"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Never Reset',
            document_type='journal',
            prefix='JE',
            reset_frequency='never',
            last_reset_date=date(2020, 1, 1),
            created_by=self.user
        )
        
        # Should never reset
        self.assertFalse(scheme.should_reset())
    
    def test_validation_padding_range(self):
        """Test padding validation"""
        scheme = NumberingScheme(
            scheme_name='Invalid Padding',
            document_type='invoice',
            prefix='INV',
            padding=15,  # Invalid: > 10
            created_by=self.user
        )
        
        with self.assertRaises(ValidationError):
            scheme.clean()
    
    def test_validation_next_number_minimum(self):
        """Test next_number validation"""
        scheme = NumberingScheme(
            scheme_name='Invalid Next Number',
            document_type='invoice',
            prefix='INV',
            next_number=0,  # Invalid: < 1
            created_by=self.user
        )
        
        with self.assertRaises(ValidationError):
            scheme.clean()
    
    def test_validation_requires_component(self):
        """Test that at least one component is required"""
        scheme = NumberingScheme(
            scheme_name='No Components',
            document_type='invoice',
            # No prefix, date_format, or suffix
            created_by=self.user
        )
        
        with self.assertRaises(ValidationError):
            scheme.clean()
    
    def test_unique_active_scheme_per_document_type(self):
        """Test that only one active scheme per document type (global)"""
        # Create first active scheme
        NumberingScheme.objects.create(
            scheme_name='First Scheme',
            document_type='invoice',
            prefix='INV1',
            is_active=True,
            created_by=self.user
        )
        
        # Try to create second active scheme for same document type
        # This should fail due to unique constraint
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            NumberingScheme.objects.create(
                scheme_name='Second Scheme',
                document_type='invoice',
                prefix='INV2',
                is_active=True,
                created_by=self.user
            )
    
    def test_multiple_inactive_schemes_allowed(self):
        """Test that multiple inactive schemes are allowed"""
        NumberingScheme.objects.create(
            scheme_name='Inactive 1',
            document_type='invoice',
            prefix='INV1',
            is_active=False,
            created_by=self.user
        )
        
        NumberingScheme.objects.create(
            scheme_name='Inactive 2',
            document_type='invoice',
            prefix='INV2',
            is_active=False,
            created_by=self.user
        )
        
        # Should succeed - multiple inactive schemes allowed
        self.assertEqual(NumberingScheme.objects.filter(document_type='invoice', is_active=False).count(), 2)
    
    def test_entity_specific_scheme(self):
        """Test entity-specific numbering scheme"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Entity Specific',
            document_type='voucher',
            prefix='VCH',
            entity=self.entity,
            created_by=self.user
        )
        
        self.assertEqual(scheme.entity, self.entity)
        self.assertIn(scheme, self.entity.numbering_schemes.all())
    
    def test_str_representation(self):
        """Test string representation"""
        scheme = NumberingScheme.objects.create(
            scheme_name='Test Scheme',
            document_type='invoice',
            prefix='INV',
            created_by=self.user
        )
        
        self.assertEqual(str(scheme), 'Test Scheme (invoice)')
