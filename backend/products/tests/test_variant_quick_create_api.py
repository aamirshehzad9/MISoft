"""
Unit Tests for Product Variant Quick-Create API
Task 1.6.2: AJAX Variant Creation
TDD Cycle - Step 1: Write Failing Tests First

Tests the /api/products/variants/quick-create/ endpoint
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from products.models import Product, ProductCategory, ProductVariant, UnitOfMeasure

User = get_user_model()


class ProductVariantQuickCreateAPITestCase(TestCase):
    """Test suite for quick-create variant API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Create API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create category and UoM
        self.category = ProductCategory.objects.create(
            name='Test Category',
            code='TEST-CAT'
        )
        
        self.uom = UnitOfMeasure.objects.create(
            name='Unit',
            symbol='pcs',
            uom_type='unit'
        )
        
        # Create base product
        self.product = Product.objects.create(
            name='Test Product',
            code='PROD-001',
            category=self.category,
            base_uom=self.uom,
            product_type='finished_good'
        )
        
        self.url = '/api/products/variants/quick-create/'
    
    def test_create_variant_success(self):
        """Test successful variant creation"""
        data = {
            'product': self.product.id,
            'variant_name': 'Size: Large',
            'variant_code': 'PROD-001-L',
            'price_adjustment': '10.50',
            'barcode': '1234567890'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['variant_name'], 'Size: Large')
        self.assertEqual(response.data['variant_code'], 'PROD-001-L')
        self.assertEqual(Decimal(response.data['price_adjustment']), Decimal('10.50'))
        self.assertEqual(response.data['barcode'], '1234567890')
        
        # Verify variant was created in database
        variant = ProductVariant.objects.get(variant_code='PROD-001-L')
        self.assertEqual(variant.product, self.product)
        self.assertEqual(variant.variant_name, 'Size: Large')
    
    def test_create_variant_without_barcode(self):
        """Test variant creation without optional barcode"""
        data = {
            'product': self.product.id,
            'variant_name': 'Color: Red',
            'variant_code': 'PROD-001-R',
            'price_adjustment': '0.00'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['variant_name'], 'Color: Red')
        self.assertIn('barcode', response.data)  # Field should exist but be null/empty
    
    def test_create_variant_negative_price_adjustment(self):
        """Test variant with negative price adjustment (discount)"""
        data = {
            'product': self.product.id,
            'variant_name': 'Size: Small',
            'variant_code': 'PROD-001-S',
            'price_adjustment': '-5.00'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data['price_adjustment']), Decimal('-5.00'))
    
    def test_create_variant_missing_required_fields(self):
        """Test validation for missing required fields"""
        # Missing variant_name
        data = {
            'product': self.product.id,
            'variant_code': 'PROD-001-X'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('variant_name', response.data)
    
    def test_create_variant_missing_variant_code(self):
        """Test validation for missing variant code"""
        data = {
            'product': self.product.id,
            'variant_name': 'Test Variant'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('variant_code', response.data)
    
    def test_create_variant_duplicate_code(self):
        """Test validation for duplicate variant code"""
        # Create first variant
        ProductVariant.objects.create(
            product=self.product,
            variant_name='Existing Variant',
            variant_code='PROD-001-DUP'
        )
        
        # Try to create duplicate
        data = {
            'product': self.product.id,
            'variant_name': 'New Variant',
            'variant_code': 'PROD-001-DUP'  # Duplicate code
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('variant_code', response.data)
    
    def test_create_variant_duplicate_barcode(self):
        """Test validation for duplicate barcode"""
        # Create first variant with barcode
        ProductVariant.objects.create(
            product=self.product,
            variant_name='Existing Variant',
            variant_code='PROD-001-BC1',
            barcode='BARCODE123'
        )
        
        # Try to create variant with duplicate barcode
        data = {
            'product': self.product.id,
            'variant_name': 'New Variant',
            'variant_code': 'PROD-001-BC2',
            'barcode': 'BARCODE123'  # Duplicate barcode
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('barcode', response.data)
    
    def test_create_variant_invalid_product(self):
        """Test validation for non-existent product"""
        data = {
            'product': 99999,  # Non-existent product
            'variant_name': 'Test Variant',
            'variant_code': 'INVALID-001'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product', response.data)
    
    def test_create_variant_invalid_price_format(self):
        """Test validation for invalid price format"""
        data = {
            'product': self.product.id,
            'variant_name': 'Test Variant',
            'variant_code': 'PROD-001-P',
            'price_adjustment': 'invalid_price'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price_adjustment', response.data)
    
    def test_create_variant_unauthenticated(self):
        """Test that unauthenticated users cannot create variants"""
        self.client.force_authenticate(user=None)
        
        data = {
            'product': self.product.id,
            'variant_name': 'Test Variant',
            'variant_code': 'PROD-001-U'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_response_includes_product_details(self):
        """Test that response includes parent product details"""
        data = {
            'product': self.product.id,
            'variant_name': 'Size: Medium',
            'variant_code': 'PROD-001-M',
            'price_adjustment': '5.00'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('product', response.data)
        self.assertEqual(response.data['product'], self.product.id)
    
    def test_variant_is_active_by_default(self):
        """Test that created variant is active by default"""
        data = {
            'product': self.product.id,
            'variant_name': 'Test Variant',
            'variant_code': 'PROD-001-A'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        variant = ProductVariant.objects.get(variant_code='PROD-001-A')
        self.assertTrue(variant.is_active)
    
    def test_price_adjustment_defaults_to_zero(self):
        """Test that price_adjustment defaults to 0 if not provided"""
        data = {
            'product': self.product.id,
            'variant_name': 'Test Variant',
            'variant_code': 'PROD-001-Z'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data['price_adjustment']), Decimal('0.00'))
    
    def test_variant_code_uniqueness_across_products(self):
        """Test that variant codes must be unique across all products"""
        # Create another product
        product2 = Product.objects.create(
            name='Another Product',
            code='PROD-002',
            category=self.category,
            base_uom=self.uom,
            product_type='finished_good'
        )
        
        # Create variant for first product
        ProductVariant.objects.create(
            product=self.product,
            variant_name='Variant 1',
            variant_code='UNIQUE-CODE-001'
        )
        
        # Try to create variant with same code for different product
        data = {
            'product': product2.id,
            'variant_name': 'Variant 2',
            'variant_code': 'UNIQUE-CODE-001'  # Same code
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('variant_code', response.data)
    
    def test_response_format(self):
        """Test that response includes all expected fields"""
        data = {
            'product': self.product.id,
            'variant_name': 'Complete Variant',
            'variant_code': 'PROD-001-COMPLETE',
            'price_adjustment': '15.75',
            'barcode': '9876543210'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check all expected fields are in response
        expected_fields = ['id', 'product', 'variant_name', 'variant_code', 
                          'price_adjustment', 'barcode', 'is_active']
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_multiple_variants_for_same_product(self):
        """Test creating multiple variants for the same product"""
        variants_data = [
            {
                'product': self.product.id,
                'variant_name': 'Size: Small',
                'variant_code': 'PROD-001-S'
            },
            {
                'product': self.product.id,
                'variant_name': 'Size: Medium',
                'variant_code': 'PROD-001-M'
            },
            {
                'product': self.product.id,
                'variant_name': 'Size: Large',
                'variant_code': 'PROD-001-L'
            }
        ]
        
        for variant_data in variants_data:
            response = self.client.post(self.url, variant_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify all variants were created
        variants = ProductVariant.objects.filter(product=self.product)
        self.assertEqual(variants.count(), 3)
