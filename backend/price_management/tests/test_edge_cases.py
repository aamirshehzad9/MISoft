"""
Edge case tests for pricing module
Tests boundary conditions and error scenarios
"""
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone

from products.models import Product, ProductCategory, UnitOfMeasure
from partners.models import BusinessPartner
from accounts.models import CustomUser
from price_management.models import PriceRule
from price_management.services.pricing_engine import PricingEngine


class PricingEdgeCasesTestCase(TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.uom = UnitOfMeasure.objects.create(
            name='Piece',
            symbol='pc',
            uom_type='unit'
        )
        
        self.category = ProductCategory.objects.create(
            name='Test Category',
            code='TEST'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            code='PROD001',
            product_type='finished_good',
            category=self.category,
            base_uom=self.uom,
            selling_price=Decimal('100.00'),
            is_active=True
        )
        
        self.customer = BusinessPartner.objects.create(
            name='Test Customer',
            city='Lahore',
            is_customer=True,
            created_by=self.user
        )
        
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)

    def test_edge_case_zero_quantity(self):
        """Test 18: Zero quantity should still return pricing info"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Test Rule',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('85.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=0
        )
        
        # Should still return pricing information
        self.assertEqual(result['final_price'], Decimal('85.00'))
        self.assertEqual(result['quantity'], Decimal('0'))

    def test_edge_case_very_large_quantity(self):
        """Test 19: Very large quantity should work correctly"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Mega Bulk',
            priority=10,
            valid_from=self.yesterday,
            min_quantity=Decimal('1000'),
            price=Decimal('75.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=10000
        )
        
        self.assertEqual(result['final_price'], Decimal('75.00'))

    def test_edge_case_fractional_quantity(self):
        """Test 20: Fractional quantities should work"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Fractional Rule',
            priority=10,
            valid_from=self.yesterday,
            min_quantity=Decimal('0.5'),
            price=Decimal('95.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=0.75
        )
        
        self.assertEqual(result['final_price'], Decimal('95.00'))

    def test_edge_case_expired_rule_not_applied(self):
        """Test 21: Expired rules should not be applied"""
        last_week = self.today - timedelta(days=7)
        
        PriceRule.objects.create(
            product=self.product,
            rule_name='Expired Rule',
            priority=10,
            valid_from=last_week,
            valid_to=self.yesterday,
            price=Decimal('80.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1,
            date=self.today
        )
        
        # Should use base price
        self.assertEqual(result['final_price'], Decimal('100.00'))
        self.assertIsNone(result['applied_rule'])

    def test_edge_case_future_rule_not_applied(self):
        """Test 22: Future rules should not be applied to current date"""
        next_month = self.today + timedelta(days=30)
        
        PriceRule.objects.create(
            product=self.product,
            rule_name='Future Rule',
            priority=10,
            valid_from=next_month,
            price=Decimal('80.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1,
            date=self.today
        )
        
        # Should use base price
        self.assertEqual(result['final_price'], Decimal('100.00'))
        self.assertIsNone(result['applied_rule'])

    def test_edge_case_no_end_date_rule(self):
        """Test 23: Rules with no end date should work indefinitely"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Permanent Rule',
            priority=10,
            valid_from=self.yesterday,
            valid_to=None,  # No end date
            price=Decimal('92.00'),
            is_active=True
        )
        
        # Should work far in the future
        far_future = self.today + timedelta(days=3650)  # 10 years
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1,
            date=far_future
        )
        
        self.assertEqual(result['final_price'], Decimal('92.00'))

    def test_edge_case_same_priority_rules(self):
        """Test 24: When priorities are equal, first rule wins"""
        rule1 = PriceRule.objects.create(
            product=self.product,
            rule_name='Rule A',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('90.00'),
            is_active=True
        )
        
        rule2 = PriceRule.objects.create(
            product=self.product,
            rule_name='Rule B',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('85.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        # Should apply one of them (implementation dependent)
        self.assertIn(result['final_price'], [Decimal('90.00'), Decimal('85.00')])

    def test_edge_case_100_percent_discount(self):
        """Test 25: 100% discount should result in zero price"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Free Item',
            priority=10,
            valid_from=self.yesterday,
            discount_percentage=Decimal('100.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        self.assertEqual(result['final_price'], Decimal('0.00'))

    def test_edge_case_very_small_discount(self):
        """Test 26: Very small discount percentages should work"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Tiny Discount',
            priority=10,
            valid_from=self.yesterday,
            discount_percentage=Decimal('0.01'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        # 100 - 0.01% = 99.99
        self.assertEqual(result['final_price'], Decimal('99.99'))

    def test_edge_case_customer_without_city(self):
        """Test 27: Customer without city should still work"""
        customer_no_city = BusinessPartner.objects.create(
            name='No City Customer',
            city='',  # Empty city
            is_customer=True,
            created_by=self.user
        )
        
        # City-specific rule
        PriceRule.objects.create(
            product=self.product,
            rule_name='City Rule',
            priority=10,
            valid_from=self.yesterday,
            city='Lahore',
            price=Decimal('85.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            customer=customer_no_city,
            quantity=1
        )
        
        # Should not match city rule, use base price
        self.assertEqual(result['final_price'], Decimal('100.00'))

    def test_edge_case_quantity_boundary(self):
        """Test 28: Quantity exactly at min/max boundaries"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Range Rule',
            priority=10,
            valid_from=self.yesterday,
            min_quantity=Decimal('10'),
            max_quantity=Decimal('50'),
            price=Decimal('90.00'),
            is_active=True
        )
        
        # Exactly at minimum
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=10
        )
        self.assertEqual(result['final_price'], Decimal('90.00'))
        
        # Exactly at maximum
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=50
        )
        self.assertEqual(result['final_price'], Decimal('90.00'))
        
        # Just below minimum
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=9.99
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
        
        # Just above maximum
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=50.01
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
