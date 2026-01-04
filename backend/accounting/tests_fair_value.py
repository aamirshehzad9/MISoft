"""
Unit Tests for Fair Value Measurement (IFRS 13 / IAS 40)
Tests fair value calculations, service methods, API endpoints, and business logic
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta

from accounting.models import AccountV2, FairValueMeasurement, VoucherV2
from accounting.services.fair_value_service import FairValueService

User = get_user_model()


class FairValueCalculationTestCase(TestCase):
    """Test fair value calculation methods"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.service = FairValueService(user=self.user)
    
    def test_market_approach_calculation(self):
        """Test market approach valuation"""
        inputs = {
            'technique': 'market_approach',
            'comparable_price': 1000000,
            'location_adjustment': 1.1,
            'size_adjustment': 0.95,
            'condition_adjustment': 1.05
        }
        
        fair_value = self.service.calculate_fair_value(None, date.today(), inputs)
        expected = Decimal('1000000') * Decimal('1.1') * Decimal('0.95') * Decimal('1.05')
        
        self.assertEqual(fair_value, expected.quantize(Decimal('0.01')))
    
    def test_income_approach_calculation(self):
        """Test income approach (DCF) valuation"""
        inputs = {
            'technique': 'income_approach',
            'annual_income': 100000,
            'discount_rate': 0.10,
            'projection_years': 5,
            'terminal_value': 500000
        }
        
        fair_value = self.service.calculate_fair_value(None, date.today(), inputs)
        
        # Fair value should be positive and reasonable
        self.assertGreater(fair_value, Decimal('0'))
        self.assertLess(fair_value, Decimal('1000000'))
    
    def test_cost_approach_calculation(self):
        """Test cost approach valuation"""
        inputs = {
            'technique': 'cost_approach',
            'replacement_cost': 500000,
            'depreciation_rate': 0.05,
            'age_years': 10
        }
        
        fair_value = self.service.calculate_fair_value(None, date.today(), inputs)
        expected = Decimal('500000') - (Decimal('500000') * Decimal('0.05') * Decimal('10'))
        
        self.assertEqual(fair_value, expected.quantize(Decimal('0.01')))
    
    def test_cost_approach_minimum_zero(self):
        """Test that cost approach doesn't return negative values"""
        inputs = {
            'technique': 'cost_approach',
            'replacement_cost': 100000,
            'depreciation_rate': 0.20,
            'age_years': 10  # Would result in negative without floor
        }
        
        fair_value = self.service.calculate_fair_value(None, date.today(), inputs)
        self.assertGreaterEqual(fair_value, Decimal('0'))


class FairValueGainLossTestCase(TestCase):
    """Test gain/loss calculation"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.service = FairValueService(user=self.user)
    
    def test_calculate_gain(self):
        """Test gain calculation"""
        fair_value = Decimal('150000')
        carrying_amount = Decimal('100000')
        
        gain_loss = self.service.calculate_gain_loss(fair_value, carrying_amount)
        
        self.assertEqual(gain_loss, Decimal('50000.00'))
    
    def test_calculate_loss(self):
        """Test loss calculation"""
        fair_value = Decimal('80000')
        carrying_amount = Decimal('100000')
        
        gain_loss = self.service.calculate_gain_loss(fair_value, carrying_amount)
        
        self.assertEqual(gain_loss, Decimal('-20000.00'))
    
    def test_no_gain_loss(self):
        """Test when fair value equals carrying amount"""
        fair_value = Decimal('100000')
        carrying_amount = Decimal('100000')
        
        gain_loss = self.service.calculate_gain_loss(fair_value, carrying_amount)
        
        self.assertEqual(gain_loss, Decimal('0.00'))


class FairValueMeasurementModelTestCase(TestCase):
    """Test FairValueMeasurement model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.account = AccountV2.objects.create(
            code='1500',
            name='Investment Property',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 40',
            created_by=self.user
        )
    
    def test_create_measurement(self):
        """Test creating fair value measurement"""
        measurement = FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=date.today(),
            fair_value_level='level_2',
            valuation_technique='market_approach',
            fair_value=Decimal('150000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('50000'),
            created_by=self.user
        )
        
        self.assertEqual(measurement.account, self.account)
        self.assertEqual(measurement.fair_value, Decimal('150000'))
        self.assertTrue(measurement.is_gain)
        self.assertFalse(measurement.is_loss)
    
    def test_auto_calculate_gain_loss(self):
        """Test that gain/loss is auto-calculated on save"""
        measurement = FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=date.today(),
            fair_value_level='level_3',
            valuation_technique='income_approach',
            fair_value=Decimal('120000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('0'),  # Will be overwritten
            created_by=self.user
        )
        
        self.assertEqual(measurement.gain_loss, Decimal('20000'))
    
    def test_is_approved_property(self):
        """Test is_approved property"""
        measurement = FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=date.today(),
            fair_value_level='level_1',
            valuation_technique='market_approach',
            fair_value=Decimal('100000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('0'),
            created_by=self.user
        )
        
        self.assertFalse(measurement.is_approved)
        
        # Approve it
        from django.utils import timezone
        measurement.approved_by = self.user
        measurement.approved_at = timezone.now()
        measurement.save()
        
        self.assertTrue(measurement.is_approved)


class FairValueServiceTestCase(TestCase):
    """Test FairValueService business logic"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.service = FairValueService(user=self.user)
        self.account = AccountV2.objects.create(
            code='1510',
            name='Building',
            account_type='asset',
            account_group='fixed_asset',
            current_balance=Decimal('100000'),
            created_by=self.user
        )
    
    def test_create_fair_value_measurement(self):
        """Test creating measurement via service"""
        data = {
            'account': self.account,
            'measurement_date': date.today(),
            'fair_value_level': 'level_2',
            'valuation_technique': 'market_approach',
            'fair_value': Decimal('150000'),
            'inputs_used': {'comparable_price': 150000}
        }
        
        measurement = self.service.create_fair_value_measurement(data)
        
        self.assertIsNotNone(measurement.id)
        self.assertEqual(measurement.fair_value, Decimal('150000'))
        self.assertEqual(measurement.gain_loss, Decimal('50000'))
    
    def test_validate_hierarchy_level_1(self):
        """Test Level 1 hierarchy validation"""
        # Should pass with quoted price
        inputs = {'quoted_price': 100000}
        try:
            self.service.validate_fair_value_hierarchy('level_1', inputs)
        except ValidationError:
            self.fail("Level 1 validation should pass with quoted_price")
        
        # Should fail without quoted price
        inputs = {'comparable_price': 100000}
        with self.assertRaises(ValidationError):
            self.service.validate_fair_value_hierarchy('level_1', inputs)
    
    def test_validate_hierarchy_level_2(self):
        """Test Level 2 hierarchy validation"""
        # Should pass with observable inputs
        inputs = {'comparable_price': 100000}
        try:
            self.service.validate_fair_value_hierarchy('level_2', inputs)
        except ValidationError:
            self.fail("Level 2 validation should pass with observable inputs")
        
        # Should fail without observable inputs
        inputs = {'internal_estimate': 100000}
        with self.assertRaises(ValidationError):
            self.service.validate_fair_value_hierarchy('level_2', inputs)
    
    def test_check_revaluation_frequency_no_previous(self):
        """Test revaluation check with no previous measurement"""
        result = self.service.check_revaluation_frequency(self.account)
        
        self.assertTrue(result['is_due'])
        self.assertIn('No previous', result['reason'])
    
    def test_check_revaluation_frequency_overdue(self):
        """Test revaluation check when overdue"""
        # Create old measurement
        old_date = date.today() - timedelta(days=400)
        FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=old_date,
            fair_value_level='level_2',
            valuation_technique='market_approach',
            fair_value=Decimal('100000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('0'),
            created_by=self.user
        )
        
        result = self.service.check_revaluation_frequency(self.account)
        
        self.assertTrue(result['is_due'])
        self.assertGreater(result['days_overdue'], 0)
    
    def test_check_revaluation_frequency_not_due(self):
        """Test revaluation check when not due"""
        # Create recent measurement
        recent_date = date.today() - timedelta(days=30)
        FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=recent_date,
            fair_value_level='level_2',
            valuation_technique='market_approach',
            fair_value=Decimal('100000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('0'),
            created_by=self.user
        )
        
        result = self.service.check_revaluation_frequency(self.account)
        
        self.assertFalse(result['is_due'])
        self.assertGreater(result['days_until_due'], 0)


class FairValueVoucherPostingTestCase(TestCase):
    """Test automatic voucher posting"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.service = FairValueService(user=self.user)
        self.account = AccountV2.objects.create(
            code='1520',
            name='Land',
            account_type='asset',
            account_group='fixed_asset',
            current_balance=Decimal('100000'),
            created_by=self.user
        )
    
    def test_post_fair_value_gain(self):
        """Test posting fair value gain"""
        measurement = FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=date.today(),
            fair_value_level='level_2',
            valuation_technique='market_approach',
            fair_value=Decimal('150000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('50000'),
            created_by=self.user
        )
        
        voucher = self.service.post_fair_value_adjustment(measurement, auto_approve=True)
        
        self.assertIsNotNone(voucher)
        self.assertEqual(voucher.total_amount, Decimal('50000'))
        self.assertEqual(voucher.status, 'posted')
        self.assertEqual(measurement.voucher, voucher)
    
    def test_post_fair_value_loss(self):
        """Test posting fair value loss"""
        measurement = FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=date.today(),
            fair_value_level='level_3',
            valuation_technique='income_approach',
            fair_value=Decimal('80000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('-20000'),
            created_by=self.user
        )
        
        voucher = self.service.post_fair_value_adjustment(measurement, auto_approve=True)
        
        self.assertIsNotNone(voucher)
        self.assertEqual(voucher.total_amount, Decimal('20000'))
        self.assertEqual(voucher.status, 'posted')
    
    def test_cannot_post_zero_gain_loss(self):
        """Test that zero gain/loss cannot be posted"""
        measurement = FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=date.today(),
            fair_value_level='level_1',
            valuation_technique='market_approach',
            fair_value=Decimal('100000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('0'),
            created_by=self.user
        )
        
        with self.assertRaises(ValidationError):
            self.service.post_fair_value_adjustment(measurement)
    
    def test_cannot_post_twice(self):
        """Test that measurement cannot be posted twice"""
        measurement = FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=date.today(),
            fair_value_level='level_2',
            valuation_technique='market_approach',
            fair_value=Decimal('120000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('20000'),
            created_by=self.user
        )
        
        # Post once
        self.service.post_fair_value_adjustment(measurement, auto_approve=True)
        
        # Try to post again
        with self.assertRaises(ValidationError):
            self.service.post_fair_value_adjustment(measurement)


class FairValueAPITestCase(APITestCase):
    """Test Fair Value API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='apipass123')
        self.client.force_authenticate(user=self.user)
        
        self.account = AccountV2.objects.create(
            code='1530',
            name='Investment Property',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 40',
            created_by=self.user
        )
    
    def test_create_measurement_via_api(self):
        """Test creating measurement via API"""
        data = {
            'account': self.account.id,
            'measurement_date': str(date.today()),
            'fair_value_level': 'level_2',
            'valuation_technique': 'market_approach',
            'fair_value': '150000.00',
            'carrying_amount': '100000.00',
            'inputs_used': {'comparable_price': 150000}
        }
        
        response = self.client.post('/api/accounting/fair-value-measurements/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['fair_value'], '150000.00')
        self.assertEqual(response.data['gain_loss'], '50000.00')
    
    def test_list_measurements(self):
        """Test listing measurements"""
        FairValueMeasurement.objects.create(
            account=self.account,
            measurement_date=date.today(),
            fair_value_level='level_2',
            valuation_technique='market_approach',
            fair_value=Decimal('150000'),
            carrying_amount=Decimal('100000'),
            gain_loss=Decimal('50000'),
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/fair-value-measurements/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_hierarchy_report(self):
        """Test hierarchy report endpoint"""
        response = self.client.get('/api/accounting/fair-value-measurements/hierarchy_report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('hierarchy_breakdown', response.data)
        self.assertIn('totals', response.data)
    
    def test_gain_loss_report(self):
        """Test gain/loss report endpoint"""
        response = self.client.get('/api/accounting/fair-value-measurements/gain_loss_report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('by_recognition', response.data)


class FairValueCoverageTestCase(TestCase):
    """Test coverage of fair value features"""
    
    def test_all_hierarchy_levels_available(self):
        """Test all IFRS 13 hierarchy levels are available"""
        levels = [choice[0] for choice in FairValueMeasurement.FAIR_VALUE_HIERARCHY]
        
        self.assertIn('level_1', levels)
        self.assertIn('level_2', levels)
        self.assertIn('level_3', levels)
        self.assertEqual(len(levels), 3)
    
    def test_all_valuation_techniques_available(self):
        """Test all valuation techniques are available"""
        techniques = [choice[0] for choice in FairValueMeasurement.VALUATION_TECHNIQUES]
        
        self.assertIn('market_approach', techniques)
        self.assertIn('income_approach', techniques)
        self.assertIn('cost_approach', techniques)
        self.assertEqual(len(techniques), 3)
    
    def test_all_measurement_purposes_available(self):
        """Test all measurement purposes are available"""
        purposes = [choice[0] for choice in FairValueMeasurement.MEASUREMENT_PURPOSE]
        
        required_purposes = [
            'initial_recognition',
            'subsequent_measurement',
            'revaluation',
            'impairment_testing',
            'disposal'
        ]
        
        for purpose in required_purposes:
            self.assertIn(purpose, purposes)
