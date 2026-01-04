"""
Comprehensive test suite for Dynamic Pricing Matrix (Module 1.4)
Quality Gate Requirements:
- Price calculations accurate
- Priority logic works correctly  
- Date range validation works
- >90% test coverage (financial critical)
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


class PricingEngineTestCase(TestCase):
    """Test suite for PricingEngine calculation logic"""
    
    def setUp(self):
        """Set up test data"""
        # Create user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create UOM
        self.uom = UnitOfMeasure.objects.create(
            name='Piece',
            symbol='pc',
            uom_type='unit'
        )
        
        # Create category
        self.category = ProductCategory.objects.create(
            name='Test Category',
            code='TEST'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            code='PROD001',
            product_type='finished_good',
            category=self.category,
            base_uom=self.uom,
            selling_price=Decimal('100.00'),
            is_active=True
        )
        
        # Create test customers
        self.customer_lahore = BusinessPartner.objects.create(
            name='Lahore Customer',
            city='Lahore',
            is_customer=True,
            created_by=self.user
        )
        
        self.customer_karachi = BusinessPartner.objects.create(
            name='Karachi Customer',
            city='Karachi',
            is_customer=True,
            created_by=self.user
        )
        
        # Date references
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.next_week = self.today + timedelta(days=7)
        self.last_week = self.today - timedelta(days=7)

    def test_base_price_no_rules(self):
        """Test 1: Base price returned when no rules exist"""
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        self.assertEqual(result['original_price'], Decimal('100.00'))
        self.assertEqual(result['final_price'], Decimal('100.00'))
        self.assertIsNone(result['applied_rule'])
        self.assertEqual(result['product_id'], self.product.id)

    def test_simple_price_rule(self):
        """Test 2: Simple price rule application"""
        rule = PriceRule.objects.create(
            product=self.product,
            rule_name='Standard Discount',
            priority=10,
            valid_from=self.yesterday,
            valid_to=self.next_week,
            price=Decimal('85.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        self.assertEqual(result['final_price'], Decimal('85.00'))
        self.assertEqual(result['applied_rule'], 'Standard Discount')
        self.assertEqual(result['rule_id'], rule.id)

    def test_discount_percentage_rule(self):
        """Test 3: Discount percentage calculation"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='10% Off',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('0.00'),  # No fixed price
            discount_percentage=Decimal('10.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        # 100 - 10% = 90
        self.assertEqual(result['final_price'], Decimal('90.00'))
        self.assertEqual(result['applied_rule'], '10% Off')

    def test_priority_logic_highest_wins(self):
        """Test 4: Highest priority rule wins"""
        # Lower priority rule
        PriceRule.objects.create(
            product=self.product,
            rule_name='Low Priority',
            priority=5,
            valid_from=self.yesterday,
            price=Decimal('80.00'),
            is_active=True
        )
        
        # Higher priority rule
        PriceRule.objects.create(
            product=self.product,
            rule_name='High Priority',
            priority=20,
            valid_from=self.yesterday,
            price=Decimal('75.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        # Should apply high priority rule
        self.assertEqual(result['final_price'], Decimal('75.00'))
        self.assertEqual(result['applied_rule'], 'High Priority')

    def test_date_range_validation_future_rule(self):
        """Test 5: Future rule not applied"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Future Sale',
            priority=10,
            valid_from=self.tomorrow,
            price=Decimal('70.00'),
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

    def test_date_range_validation_expired_rule(self):
        """Test 6: Expired rule not applied"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Past Sale',
            priority=10,
            valid_from=self.last_week,
            valid_to=self.yesterday,
            price=Decimal('70.00'),
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

    def test_date_range_validation_active_rule(self):
        """Test 7: Active rule within date range"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Active Sale',
            priority=10,
            valid_from=self.yesterday,
            valid_to=self.tomorrow,
            price=Decimal('85.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1,
            date=self.today
        )
        
        self.assertEqual(result['final_price'], Decimal('85.00'))
        self.assertEqual(result['applied_rule'], 'Active Sale')

    def test_quantity_based_pricing_min(self):
        """Test 8: Minimum quantity threshold"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Bulk Discount',
            priority=10,
            valid_from=self.yesterday,
            min_quantity=Decimal('10'),
            price=Decimal('90.00'),
            is_active=True
        )
        
        # Below minimum
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=5
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
        
        # At minimum
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=10
        )
        self.assertEqual(result['final_price'], Decimal('90.00'))
        
        # Above minimum
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=15
        )
        self.assertEqual(result['final_price'], Decimal('90.00'))

    def test_quantity_based_pricing_range(self):
        """Test 9: Quantity range (min and max)"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Medium Bulk',
            priority=10,
            valid_from=self.yesterday,
            min_quantity=Decimal('10'),
            max_quantity=Decimal('50'),
            price=Decimal('90.00'),
            is_active=True
        )
        
        # Below range
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=5
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
        
        # Within range
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=25
        )
        self.assertEqual(result['final_price'], Decimal('90.00'))
        
        # Above range
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=100
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))

    def test_customer_specific_pricing(self):
        """Test 10: Customer-specific pricing"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='VIP Customer Price',
            priority=10,
            valid_from=self.yesterday,
            customer=self.customer_lahore,
            price=Decimal('85.00'),
            is_active=True
        )
        
        # Correct customer
        result = PricingEngine.calculate_price(
            product=self.product,
            customer=self.customer_lahore,
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('85.00'))
        
        # Different customer
        result = PricingEngine.calculate_price(
            product=self.product,
            customer=self.customer_karachi,
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
        
        # No customer
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))

    def test_city_based_pricing(self):
        """Test 11: City-based pricing"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Lahore Special',
            priority=10,
            valid_from=self.yesterday,
            city='Lahore',
            price=Decimal('88.00'),
            is_active=True
        )
        
        # Matching city
        result = PricingEngine.calculate_price(
            product=self.product,
            customer=self.customer_lahore,
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('88.00'))
        
        # Different city
        result = PricingEngine.calculate_price(
            product=self.product,
            customer=self.customer_karachi,
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))

    def test_city_case_insensitive(self):
        """Test 12: City matching is case-insensitive"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='City Rule',
            priority=10,
            valid_from=self.yesterday,
            city='LAHORE',  # Uppercase
            price=Decimal('88.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            customer=self.customer_lahore,  # city='Lahore'
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('88.00'))

    def test_inactive_rule_ignored(self):
        """Test 13: Inactive rules are not applied"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Inactive Rule',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('70.00'),
            is_active=False  # Inactive
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        self.assertEqual(result['final_price'], Decimal('100.00'))
        self.assertIsNone(result['applied_rule'])

    def test_complex_scenario_multiple_rules(self):
        """Test 14: Complex scenario with multiple overlapping rules"""
        # General discount
        PriceRule.objects.create(
            product=self.product,
            rule_name='General 5% Off',
            priority=5,
            valid_from=self.yesterday,
            discount_percentage=Decimal('5.00'),
            is_active=True
        )
        
        # City-specific
        PriceRule.objects.create(
            product=self.product,
            rule_name='Lahore 10% Off',
            priority=10,
            valid_from=self.yesterday,
            city='Lahore',
            discount_percentage=Decimal('10.00'),
            is_active=True
        )
        
        # Customer-specific (highest priority)
        PriceRule.objects.create(
            product=self.product,
            rule_name='VIP Fixed Price',
            priority=20,
            valid_from=self.yesterday,
            customer=self.customer_lahore,
            price=Decimal('80.00'),
            is_active=True
        )
        
        # Should apply highest priority (VIP)
        result = PricingEngine.calculate_price(
            product=self.product,
            customer=self.customer_lahore,
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('80.00'))
        self.assertEqual(result['applied_rule'], 'VIP Fixed Price')

    def test_open_ended_date_range(self):
        """Test 15: Rules with no end date (valid_to=None)"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Permanent Discount',
            priority=10,
            valid_from=self.yesterday,
            valid_to=None,  # No end date
            price=Decimal('92.00'),
            is_active=True
        )
        
        # Should work today
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1,
            date=self.today
        )
        self.assertEqual(result['final_price'], Decimal('92.00'))
        
        # Should work in future
        future_date = self.today + timedelta(days=365)
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1,
            date=future_date
        )
        self.assertEqual(result['final_price'], Decimal('92.00'))

    def test_decimal_precision(self):
        """Test 16: Decimal precision in calculations"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Precise Discount',
            priority=10,
            valid_from=self.yesterday,
            discount_percentage=Decimal('12.50'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        # 100 - 12.5% = 87.50
        self.assertEqual(result['final_price'], Decimal('87.50'))
        self.assertIsInstance(result['final_price'], Decimal)

    def test_quantity_as_decimal(self):
        """Test 17: Quantity handling as Decimal"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Fractional Quantity',
            priority=10,
            valid_from=self.yesterday,
            min_quantity=Decimal('2.5'),
            price=Decimal('95.00'),
            is_active=True
        )
        
        # Below threshold
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=2.0
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
        
        # At threshold
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=2.5
        )
        self.assertEqual(result['final_price'], Decimal('95.00'))

    def test_result_structure(self):
        """Test 18: Verify result dictionary structure"""
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=5
        )
        
        # Check all required keys
        self.assertIn('product_id', result)
        self.assertIn('product_name', result)
        self.assertIn('original_price', result)
        self.assertIn('final_price', result)
        self.assertIn('applied_rule', result)
        self.assertIn('rule_id', result)
        self.assertIn('quantity', result)
        self.assertIn('currency', result)
        
        # Check types
        self.assertIsInstance(result['product_id'], int)
        self.assertIsInstance(result['product_name'], str)
        self.assertIsInstance(result['original_price'], Decimal)
        self.assertIsInstance(result['final_price'], Decimal)
        self.assertIsInstance(result['quantity'], Decimal)

    def test_bulk_price_update(self):
        """Test 19: Bulk price update functionality"""
        # Create additional products
        product2 = Product.objects.create(
            name='Product 2',
            code='PROD002',
            product_type='finished_good',
            category=self.category,
            base_uom=self.uom,
            selling_price=Decimal('200.00'),
            is_active=True
        )
        
        product_ids = [self.product.id, product2.id]
        
        # Apply 10% increase
        count = PricingEngine.bulk_update_prices(product_ids, 10)
        
        self.assertEqual(count, 2)
        
        # Verify updates
        self.product.refresh_from_db()
        product2.refresh_from_db()
        
        self.assertEqual(self.product.selling_price, Decimal('110.00'))
        self.assertEqual(product2.selling_price, Decimal('220.00'))

    def test_negative_discount_not_applied(self):
        """Test 20: Edge case - negative discount should not increase price"""
        # This tests data integrity - negative discounts shouldn't exist
        # but if they do, the logic should handle gracefully
        PriceRule.objects.create(
            product=self.product,
            rule_name='Invalid Negative',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('0.00'),
            discount_percentage=Decimal('-10.00'),  # Invalid
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        # Should fallback to base price (rule not applied due to price=0)
        # The engine only applies discount if price > 0 OR discount > 0
        # Negative discount is not applied, so base price is used
        self.assertEqual(result['final_price'], Decimal('100.00'))
        self.assertIsNone(result['applied_rule'])


class PriceRuleModelTestCase(TestCase):
    """Test PriceRule model validation and constraints"""
    
    def setUp(self):
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

    def test_price_rule_creation(self):
        """Test 21: Basic PriceRule creation"""
        rule = PriceRule.objects.create(
            product=self.product,
            rule_name='Test Rule',
            priority=10,
            valid_from=date.today(),
            price=Decimal('95.00'),
            is_active=True
        )
        
        self.assertEqual(str(rule), f"Test Rule - {self.product.code}")
        self.assertTrue(rule.is_active)
        self.assertEqual(rule.priority, 10)

    def test_price_rule_ordering(self):
        """Test 22: PriceRule default ordering"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        rule1 = PriceRule.objects.create(
            product=self.product,
            rule_name='Rule 1',
            priority=5,
            valid_from=today,
            price=Decimal('95.00'),
            is_active=True
        )
        
        rule2 = PriceRule.objects.create(
            product=self.product,
            rule_name='Rule 2',
            priority=10,
            valid_from=yesterday,
            price=Decimal('90.00'),
            is_active=True
        )
        
        # Should order by -priority, -valid_from
        rules = list(PriceRule.objects.all())
        self.assertEqual(rules[0], rule2)  # Higher priority first
        self.assertEqual(rules[1], rule1)
