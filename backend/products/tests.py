from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, ProductCategory, UnitOfMeasure

User = get_user_model()


class ProductTests(TestCase):
    """Test suite for Products module"""

    def setUp(self):
        """Set up test client, user, and test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role='admin'
        )
        self.client.force_authenticate(user=self.user)

        # Create UOM
        self.uom = UnitOfMeasure.objects.create(
            name='Kilogram',
            symbol='kg',
            uom_type='weight'
        )

        # Create Category
        self.category = ProductCategory.objects.create(
            name='Test Category',
            code='TEST'
        )

        self.product_data = {
            'code': 'PROD001',
            'name': 'Test Product',
            'description': 'Test product description',
            'product_type': 'raw_material',
            'category': self.category.id,
            'base_uom': self.uom.id,
            'standard_cost': 100.00,
            'selling_price': 150.00,
            'minimum_stock': 10,
            'maximum_stock': 100,
            'reorder_point': 20,
            'is_active': True,
            'can_be_sold': True,
            'can_be_purchased': True
        }

        self.product = Product.objects.create(
            code='EXISTING001',
            name='Existing Product',
            product_type='finished_good',
            base_uom=self.uom,
            standard_cost=200.00,
            selling_price=300.00
        )

    def test_create_product_success(self):
        """Test creating a product with valid data"""
        response = self.client.post('/api/products/', self.product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], self.product_data['code'])
        self.assertEqual(response.data['name'], self.product_data['name'])

    def test_create_product_duplicate_code(self):
        """Test creating product with duplicate code fails"""
        duplicate_data = self.product_data.copy()
        duplicate_data['code'] = 'EXISTING001'
        response = self.client.post('/api/products/', duplicate_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_product_list(self):
        """Test retrieving list of products"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_product_detail(self):
        """Test retrieving a single product"""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], self.product.code)

    def test_update_product(self):
        """Test updating product information"""
        update_data = {'selling_price': 350.00}
        response = self.client.patch(f'/api/products/{self.product.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['selling_price']), 350.00)

    def test_delete_product(self):
        """Test deleting a product"""
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_filter_raw_materials(self):
        """Test filtering products by raw material type"""
        response = self.client.get('/api/products/raw_materials/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_finished_goods(self):
        """Test filtering products by finished goods type"""
        response = self.client.get('/api/products/finished_goods/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_product_by_code(self):
        """Test searching products by code"""
        response = self.client.get('/api/products/', {'search': 'EXISTING001'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_search_product_by_name(self):
        """Test searching products by name"""
        response = self.client.get('/api/products/', {'search': 'Existing'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_product_model_string_representation(self):
        """Test product model __str__ method"""
        self.assertEqual(str(self.product), 'EXISTING001 - Existing Product')

    def test_product_category_creation(self):
        """Test creating a product category"""
        category_data = {
            'name': 'New Category',
            'code': 'NEWCAT'
        }
        response = self.client.post('/api/products/categories/', category_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], category_data['name'])

    def test_uom_creation(self):
        """Test creating a unit of measure"""
        uom_data = {
            'name': 'Liter',
            'symbol': 'L',
            'uom_type': 'volume'
        }
        response = self.client.post('/api/products/uoms/', uom_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], uom_data['name'])

    def test_product_stock_levels(self):
        """Test product stock level fields"""
        product = Product.objects.create(
            code='STOCK001',
            name='Stock Test Product',
            base_uom=self.uom,
            minimum_stock=5,
            maximum_stock=50,
            reorder_point=10
        )
        self.assertEqual(product.minimum_stock, 5)
        self.assertEqual(product.maximum_stock, 50)
        self.assertEqual(product.reorder_point, 10)

    def test_product_pricing(self):
        """Test product pricing fields"""
        self.assertEqual(self.product.standard_cost, 200.00)
        self.assertEqual(self.product.selling_price, 300.00)

    def test_product_settings_flags(self):
        """Test product settings flags"""
        product = Product.objects.create(
            code='FLAGS001',
            name='Flags Test',
            base_uom=self.uom,
            can_be_sold=True,
            can_be_purchased=False,
            can_be_manufactured=True
        )
        self.assertTrue(product.can_be_sold)
        self.assertFalse(product.can_be_purchased)
        self.assertTrue(product.can_be_manufactured)
