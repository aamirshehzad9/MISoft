"""
API endpoint tests for pricing module
Tests all REST API endpoints for correctness
"""
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import io

from products.models import Product, ProductCategory, UnitOfMeasure
from partners.models import BusinessPartner
from accounts.models import CustomUser
from price_management.models import PriceRule


class PricingAPITestCase(TestCase):
    """Test pricing REST API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create and authenticate user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test data
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

    def test_api_list_rules(self):
        """Test 8: GET /api/pricing/rules/ - List all rules"""
        # Create test rules
        PriceRule.objects.create(
            product=self.product,
            rule_name='Test Rule 1',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('95.00'),
            is_active=True
        )
        
        PriceRule.objects.create(
            product=self.product,
            rule_name='Test Rule 2',
            priority=20,
            valid_from=self.yesterday,
            price=Decimal('90.00'),
            is_active=True
        )
        
        response = self.client.get('/api/pricing/rules/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response may be paginated or direct list
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 2)

    def test_api_create_rule(self):
        """Test 9: POST /api/pricing/rules/ - Create new rule"""
        data = {
            'product': self.product.id,
            'rule_name': 'API Test Rule',
            'priority': 15,
            'valid_from': self.yesterday.isoformat(),
            'price': '88.00',
            'is_active': True
        }
        
        response = self.client.post('/api/pricing/rules/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rule_name'], 'API Test Rule')
        self.assertEqual(PriceRule.objects.count(), 1)

    def test_api_calculate_price(self):
        """Test 10: POST /api/pricing/rules/calculate/ - Calculate price"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Test Rule',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('85.00'),
            is_active=True
        )
        
        data = {
            'product_id': self.product.id,
            'quantity': 1
        }
        
        response = self.client.post('/api/pricing/rules/calculate/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['final_price']), Decimal('85.00'))
        self.assertEqual(response.data['applied_rule'], 'Test Rule')

    def test_api_report_by_product(self):
        """Test 11: GET /api/pricing/rules/report_by_product/"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Test Rule',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('85.00'),
            is_active=True
        )
        
        response = self.client.get('/api/pricing/rules/report_by_product/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['report_type'], 'price_list_by_product')
        self.assertGreater(response.data['count'], 0)

    def test_api_report_by_customer(self):
        """Test 12: GET /api/pricing/rules/report_by_customer/"""
        PriceRule.objects.create(
            product=self.product,
            customer=self.customer,
            rule_name='Customer Rule',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('85.00'),
            is_active=True
        )
        
        response = self.client.get(f'/api/pricing/rules/report_by_customer/?customer_id={self.customer.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['report_type'], 'price_list_by_customer')

    def test_api_report_price_history(self):
        """Test 13: GET /api/pricing/rules/report_price_history/"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Historical Rule',
            priority=10,
            valid_from=self.yesterday,
            valid_to=self.today,
            price=Decimal('85.00'),
            is_active=True
        )
        
        response = self.client.get(f'/api/pricing/rules/report_price_history/?product_id={self.product.id}&days=30')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['report_type'], 'price_history')

    def test_api_report_price_variance(self):
        """Test 14: GET /api/pricing/rules/report_price_variance/"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Variance Test',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('85.00'),
            is_active=True
        )
        
        response = self.client.get('/api/pricing/rules/report_price_variance/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['report_type'], 'price_variance')
        self.assertIn('summary', response.data)

    def test_api_export_template(self):
        """Test 15: GET /api/pricing/rules/export_template/ - Download template"""
        response = self.client.get('/api/pricing/rules/export_template/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment', response['Content-Disposition'])

    def test_api_filter_by_product(self):
        """Test 16: Filter rules by product"""
        product2 = Product.objects.create(
            name='Product 2',
            code='PROD002',
            product_type='finished_good',
            category=self.category,
            base_uom=self.uom,
            selling_price=Decimal('150.00'),
            is_active=True
        )
        
        PriceRule.objects.create(
            product=self.product,
            rule_name='Rule for Product 1',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('95.00'),
            is_active=True
        )
        
        PriceRule.objects.create(
            product=product2,
            rule_name='Rule for Product 2',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('140.00'),
            is_active=True
        )
        
        response = self.client.get(f'/api/pricing/rules/?product={self.product.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['product'], self.product.id)

    def test_api_search_rules(self):
        """Test 17: Search rules by name"""
        PriceRule.objects.create(
            product=self.product,
            rule_name='Special Promotion',
            priority=10,
            valid_from=self.yesterday,
            price=Decimal('95.00'),
            is_active=True
        )
        
        PriceRule.objects.create(
            product=self.product,
            rule_name='Regular Discount',
            priority=5,
            valid_from=self.yesterday,
            price=Decimal('98.00'),
            is_active=True
        )
        
        response = self.client.get('/api/pricing/rules/?search=Promotion')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        self.assertEqual(len(results), 1)
        self.assertIn('Promotion', results[0]['rule_name'])
