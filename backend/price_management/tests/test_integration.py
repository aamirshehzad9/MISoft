"""
Integration tests for pricing module with sales documents
Tests pricing integration with invoices and quotations
"""
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from products.models import Product, ProductCategory, UnitOfMeasure
from partners.models import BusinessPartner
from accounts.models import CustomUser
from price_management.models import PriceRule
from price_management.services.pricing_engine import PricingEngine


class PricingInvoiceIntegrationTestCase(TestCase):
    """Test pricing integration with sales invoices"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
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
        
        # Create products
        self.product1 = Product.objects.create(
            name='Product A',
            code='PROD-A',
            product_type='finished_good',
            category=self.category,
            base_uom=self.uom,
            selling_price=Decimal('100.00'),
            is_active=True
        )
        
        self.product2 = Product.objects.create(
            name='Product B',
            code='PROD-B',
            product_type='finished_good',
            category=self.category,
            base_uom=self.uom,
            selling_price=Decimal('200.00'),
            is_active=True
        )
        
        # Create customers
        self.customer_vip = BusinessPartner.objects.create(
            name='VIP Customer',
            city='Lahore',
            is_customer=True,
            created_by=self.user
        )
        
        self.customer_regular = BusinessPartner.objects.create(
            name='Regular Customer',
            city='Karachi',
            is_customer=True,
            created_by=self.user
        )
        
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.next_week = self.today + timedelta(days=7)

    def test_invoice_with_customer_specific_pricing(self):
        """Test 1: Invoice should use customer-specific pricing"""
        # Create VIP customer rule
        PriceRule.objects.create(
            product=self.product1,
            rule_name='VIP Discount',
            priority=20,
            valid_from=self.yesterday,
            customer=self.customer_vip,
            price=Decimal('85.00'),
            is_active=True
        )
        
        # Calculate price for VIP customer
        result = PricingEngine.calculate_price(
            product=self.product1,
            customer=self.customer_vip,
            quantity=1
        )
        
        self.assertEqual(result['final_price'], Decimal('85.00'))
        self.assertEqual(result['applied_rule'], 'VIP Discount')
        
        # Regular customer should get base price
        result = PricingEngine.calculate_price(
            product=self.product1,
            customer=self.customer_regular,
            quantity=1
        )
        
        self.assertEqual(result['final_price'], Decimal('100.00'))
        self.assertIsNone(result['applied_rule'])

    def test_invoice_with_quantity_based_pricing(self):
        """Test 2: Invoice should apply quantity-based pricing"""
        # Create bulk pricing rule
        PriceRule.objects.create(
            product=self.product1,
            rule_name='Bulk Discount',
            priority=10,
            valid_from=self.yesterday,
            min_quantity=Decimal('10'),
            price=Decimal('90.00'),
            is_active=True
        )
        
        # Small quantity - base price
        result = PricingEngine.calculate_price(
            product=self.product1,
            quantity=5
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
        
        # Bulk quantity - discounted price
        result = PricingEngine.calculate_price(
            product=self.product1,
            quantity=10
        )
        self.assertEqual(result['final_price'], Decimal('90.00'))

    def test_invoice_with_date_based_pricing(self):
        """Test 3: Invoice should respect date-based pricing rules"""
        future_date = self.today + timedelta(days=5)
        
        # Create future promotion
        PriceRule.objects.create(
            product=self.product1,
            rule_name='Future Sale',
            priority=15,
            valid_from=future_date,
            price=Decimal('80.00'),
            is_active=True
        )
        
        # Today - should not apply
        result = PricingEngine.calculate_price(
            product=self.product1,
            quantity=1,
            date=self.today
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
        
        # Future date - should apply
        result = PricingEngine.calculate_price(
            product=self.product1,
            quantity=1,
            date=future_date
        )
        self.assertEqual(result['final_price'], Decimal('80.00'))

    def test_invoice_multi_line_with_different_rules(self):
        """Test 4: Multi-line invoice with different pricing rules"""
        # Product A - VIP pricing
        PriceRule.objects.create(
            product=self.product1,
            rule_name='Product A VIP',
            priority=20,
            valid_from=self.yesterday,
            customer=self.customer_vip,
            price=Decimal('85.00'),
            is_active=True
        )
        
        # Product B - Bulk pricing
        PriceRule.objects.create(
            product=self.product2,
            rule_name='Product B Bulk',
            priority=10,
            valid_from=self.yesterday,
            min_quantity=Decimal('5'),
            price=Decimal('180.00'),
            is_active=True
        )
        
        # Calculate for both products
        result1 = PricingEngine.calculate_price(
            product=self.product1,
            customer=self.customer_vip,
            quantity=1
        )
        
        result2 = PricingEngine.calculate_price(
            product=self.product2,
            customer=self.customer_vip,
            quantity=5
        )
        
        self.assertEqual(result1['final_price'], Decimal('85.00'))
        self.assertEqual(result2['final_price'], Decimal('180.00'))
        
        # Calculate invoice total
        total = result1['final_price'] * result1['quantity'] + result2['final_price'] * result2['quantity']
        self.assertEqual(total, Decimal('985.00'))  # 85 + (180 * 5)


class PricingMultipleRulesTestCase(TestCase):
    """Test scenarios with multiple overlapping pricing rules"""
    
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

    def test_multiple_rules_priority_selection(self):
        """Test 5: Highest priority rule wins among multiple applicable rules"""
        # Create multiple overlapping rules
        PriceRule.objects.create(
            product=self.product,
            rule_name='Low Priority',
            priority=5,
            valid_from=self.yesterday,
            price=Decimal('95.00'),
            is_active=True
        )
        
        PriceRule.objects.create(
            product=self.product,
            rule_name='Medium Priority',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('90.00'),
            is_active=True
        )
        
        PriceRule.objects.create(
            product=self.product,
            rule_name='High Priority',
            priority=20,
            valid_from=self.yesterday,
            price=Decimal('85.00'),
            is_active=True
        )
        
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        
        # Should select highest priority
        self.assertEqual(result['final_price'], Decimal('85.00'))
        self.assertEqual(result['applied_rule'], 'High Priority')

    def test_overlapping_customer_city_quantity_rules(self):
        """Test 6: Complex scenario with customer, city, and quantity rules"""
        # General rule
        PriceRule.objects.create(
            product=self.product,
            rule_name='General',
            priority=5,
            valid_from=self.yesterday,
            discount_percentage=Decimal('5.00'),
            is_active=True
        )
        
        # City rule
        PriceRule.objects.create(
            product=self.product,
            rule_name='Lahore Special',
            priority=10,
            valid_from=self.yesterday,
            city='Lahore',
            discount_percentage=Decimal('10.00'),
            is_active=True
        )
        
        # Customer rule (highest priority)
        PriceRule.objects.create(
            product=self.product,
            rule_name='Customer VIP',
            priority=20,
            valid_from=self.yesterday,
            customer=self.customer,
            price=Decimal('80.00'),
            is_active=True
        )
        
        # Should apply customer rule (highest priority)
        result = PricingEngine.calculate_price(
            product=self.product,
            customer=self.customer,
            quantity=1
        )
        
        self.assertEqual(result['final_price'], Decimal('80.00'))
        self.assertEqual(result['applied_rule'], 'Customer VIP')

    def test_rule_activation_deactivation(self):
        """Test 7: Deactivating a rule should exclude it from selection"""
        rule = PriceRule.objects.create(
            product=self.product,
            rule_name='Test Rule',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('85.00'),
            is_active=True
        )
        
        # Active rule should apply
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('85.00'))
        
        # Deactivate rule
        rule.is_active = False
        rule.save()
        
        # Should fallback to base price
        result = PricingEngine.calculate_price(
            product=self.product,
            quantity=1
        )
        self.assertEqual(result['final_price'], Decimal('100.00'))
        self.assertIsNone(result['applied_rule'])
