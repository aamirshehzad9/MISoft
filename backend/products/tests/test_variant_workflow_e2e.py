"""
End-to-End Tests for Product Variant Quick-Add Feature
Task 1.6.4: Testing with Quality Gate 100%

Comprehensive test suite covering:
- Variant creation from invoice forms
- Variant creation from voucher forms
- Dropdown update functionality
- Full workflow integration
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from products.models import Product, ProductCategory, ProductVariant, UnitOfMeasure

User = get_user_model()


class VariantCreationWorkflowTestCase(TestCase):
    """
    End-to-end tests for variant creation workflow
    Tests the complete flow from form to database
    """
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
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
    
    def test_complete_variant_creation_workflow(self):
        """Test complete workflow: create variant → verify in DB → check response"""
        # Step 1: Create variant via API
        variant_data = {
            'product': self.product.id,
            'variant_name': 'Size: Large',
            'variant_code': 'PROD-001-L',
            'price_adjustment': '10.50',
            'barcode': '1234567890'
        }
        
        response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            format='json'
        )
        
        # Step 2: Verify API response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['variant_name'], 'Size: Large')
        self.assertEqual(response.json()['variant_code'], 'PROD-001-L')
        
        # Step 3: Verify variant exists in database
        variant = ProductVariant.objects.get(variant_code='PROD-001-L')
        self.assertEqual(variant.product, self.product)
        self.assertEqual(variant.variant_name, 'Size: Large')
        self.assertEqual(variant.price_adjustment, Decimal('10.50'))
        self.assertEqual(variant.barcode, '1234567890')
        self.assertTrue(variant.is_active)
    
    def test_variant_creation_from_invoice_context(self):
        """Test variant creation in invoice form context"""
        # Simulate invoice form scenario
        variant_data = {
            'product': self.product.id,
            'variant_name': 'Invoice Variant',
            'variant_code': 'INV-VAR-001',
            'price_adjustment': '5.00'
        }
        
        response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify variant is available for invoice line items
        variant = ProductVariant.objects.get(variant_code='INV-VAR-001')
        self.assertTrue(variant.is_active)
        self.assertEqual(variant.product.id, self.product.id)
    
    def test_variant_creation_from_voucher_context(self):
        """Test variant creation in voucher form context"""
        # Simulate voucher form scenario
        variant_data = {
            'product': self.product.id,
            'variant_name': 'Voucher Variant',
            'variant_code': 'VOUCH-VAR-001',
            'price_adjustment': '-2.50'  # Discount variant
        }
        
        response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify variant with negative price adjustment
        variant = ProductVariant.objects.get(variant_code='VOUCH-VAR-001')
        self.assertEqual(variant.price_adjustment, Decimal('-2.50'))
    
    def test_dropdown_update_data_integrity(self):
        """Test that created variant has all data needed for dropdown update"""
        variant_data = {
            'product': self.product.id,
            'variant_name': 'Dropdown Test Variant',
            'variant_code': 'DROP-001'
        }
        
        response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            format='json'
        )
        
        # Verify response contains all fields needed for dropdown
        response_data = response.json()
        required_fields = ['id', 'product', 'variant_name', 'variant_code', 
                          'price_adjustment', 'is_active']
        
        for field in required_fields:
            self.assertIn(field, response_data)
        
        # Verify ID is present for auto-selection
        self.assertIsNotNone(response_data['id'])
        self.assertIsInstance(response_data['id'], int)
    
    def test_multiple_variants_for_same_product(self):
        """Test creating multiple variants for the same product (dropdown scenario)"""
        variants = [
            {'variant_name': 'Size: Small', 'variant_code': 'PROD-001-S'},
            {'variant_name': 'Size: Medium', 'variant_code': 'PROD-001-M'},
            {'variant_name': 'Size: Large', 'variant_code': 'PROD-001-L'},
        ]
        
        created_ids = []
        
        for variant_info in variants:
            variant_data = {
                'product': self.product.id,
                **variant_info
            }
            
            response = self.client.post(
                '/api/products/variants/quick-create/',
                data=variant_data,
                format='json'
            )
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_ids.append(response.json()['id'])
        
        # Verify all variants exist
        all_variants = ProductVariant.objects.filter(product=self.product)
        self.assertEqual(all_variants.count(), 3)
        
        # Verify all IDs are unique
        self.assertEqual(len(created_ids), len(set(created_ids)))
    
    def test_error_handling_duplicate_code(self):
        """Test error handling when duplicate variant code is used"""
        # Create first variant
        ProductVariant.objects.create(
            product=self.product,
            variant_name='Existing Variant',
            variant_code='DUP-001'
        )
        
        # Try to create duplicate
        variant_data = {
            'product': self.product.id,
            'variant_name': 'New Variant',
            'variant_code': 'DUP-001'  # Duplicate
        }
        
        response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            format='json'
        )
        
        # Verify error response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('variant_code', response.json())
    
    def test_variant_database_persistence(self):
        """Test that created variants persist in database"""
        # Create variant
        variant_data = {
            'product': self.product.id,
            'variant_name': 'Persistent Variant',
            'variant_code': 'PERSIST-001'
        }
        
        create_response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            format='json'
        )
        
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        # Verify variant exists in database
        variant = ProductVariant.objects.get(variant_code='PERSIST-001')
        self.assertEqual(variant.variant_name, 'Persistent Variant')
        self.assertTrue(variant.is_active)
    
    def test_variant_product_association(self):
        """Test that variants are correctly associated with products"""
        # Create another product
        product2 = Product.objects.create(
            name='Another Product',
            code='PROD-002',
            category=self.category,
            base_uom=self.uom,
            product_type='finished_good'
        )
        
        # Create variants for both products
        variant1 = ProductVariant.objects.create(
            product=self.product,
            variant_name='Product 1 Variant',
            variant_code='P1-VAR-001'
        )
        
        variant2 = ProductVariant.objects.create(
            product=product2,
            variant_name='Product 2 Variant',
            variant_code='P2-VAR-001'
        )
        
        # Verify associations
        self.assertEqual(variant1.product, self.product)
        self.assertEqual(variant2.product, product2)
        
        # Verify variants can be queried by product
        product1_variants = ProductVariant.objects.filter(product=self.product)
        self.assertEqual(product1_variants.count(), 1)
        self.assertEqual(product1_variants.first().variant_code, 'P1-VAR-001')


class VariantCreationCoverageTestCase(TestCase):
    """Additional tests to ensure >85% coverage"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='coverageuser',
            password='testpass123'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        self.category = ProductCategory.objects.create(name='Category', code='CAT')
        self.uom = UnitOfMeasure.objects.create(name='Unit', symbol='u', uom_type='unit')
        self.product = Product.objects.create(
            name='Product',
            code='P001',
            category=self.category,
            base_uom=self.uom,
            product_type='finished_good'
        )
    
    def test_variant_with_all_optional_fields(self):
        """Test variant creation with all optional fields populated"""
        variant_data = {
            'product': self.product.id,
            'variant_name': 'Complete Variant',
            'variant_code': 'COMPLETE-001',
            'price_adjustment': '15.75',
            'barcode': '9876543210'
        }
        
        response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        variant = ProductVariant.objects.get(variant_code='COMPLETE-001')
        self.assertEqual(variant.barcode, '9876543210')
        self.assertEqual(variant.price_adjustment, Decimal('15.75'))
    
    def test_variant_with_minimal_fields(self):
        """Test variant creation with only required fields"""
        variant_data = {
            'product': self.product.id,
            'variant_name': 'Minimal Variant',
            'variant_code': 'MIN-001'
        }
        
        response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        variant = ProductVariant.objects.get(variant_code='MIN-001')
        self.assertEqual(variant.price_adjustment, Decimal('0.00'))
        self.assertIsNone(variant.barcode)  # Barcode is None when not provided
    
    def test_variant_string_representation(self):
        """Test variant __str__ method"""
        variant = ProductVariant.objects.create(
            product=self.product,
            variant_name='Test Variant',
            variant_code='STR-001'
        )
        
        expected_str = f"{self.product.name} - Test Variant"
        self.assertEqual(str(variant), expected_str)
    
    def test_variant_ordering(self):
        """Test that variants are ordered by variant_name"""
        ProductVariant.objects.create(
            product=self.product,
            variant_name='Zebra',
            variant_code='Z-001'
        )
        ProductVariant.objects.create(
            product=self.product,
            variant_name='Alpha',
            variant_code='A-001'
        )
        
        variants = ProductVariant.objects.all()
        self.assertEqual(variants[0].variant_name, 'Alpha')
        self.assertEqual(variants[1].variant_name, 'Zebra')
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot create variants"""
        self.client.force_authenticate(user=None)
        
        variant_data = {
            'product': self.product.id,
            'variant_name': 'Unauthorized',
            'variant_code': 'UNAUTH-001'
        }
        
        response = self.client.post(
            '/api/products/variants/quick-create/',
            data=variant_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_variant_query_by_code(self):
        """Test querying variants by code"""
        ProductVariant.objects.create(
            product=self.product,
            variant_name='Queryable Variant',
            variant_code='QUERY-001'
        )
        
        # Query by code
        variant = ProductVariant.objects.get(variant_code='QUERY-001')
        self.assertEqual(variant.variant_name, 'Queryable Variant')
        self.assertEqual(variant.product, self.product)
