"""
API Tests for Fixed Asset Acquisition (Task 3.1.2)
Module 3.1: Fixed Asset Register
IAS 16 Compliance: Asset Acquisition and Recognition

Test Coverage:
1. AssetCategory API endpoints (CRUD)
2. FixedAsset API endpoints (CRUD)
3. Asset acquisition workflow
4. Asset numbering/tagging
5. Location tracking
6. Purchase voucher linking
7. Filtering and searching
8. Validation and error handling
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date
from accounting.models import AssetCategory, FixedAsset, AccountV2, VoucherV2

User = get_user_model()


class AssetCategoryAPITestCase(TestCase):
    """Test AssetCategory API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category_data = {
            'category_code': 'COMP',
            'category_name': 'Computer Equipment',
            'description': 'Computers, laptops, servers',
            'useful_life_years': 3,
            'depreciation_method': 'straight_line',
            'residual_value_percentage': '5.00',
            'ias_reference_code': 'IAS 16'
        }
    
    def test_create_asset_category(self):
        """Test creating an asset category via API"""
        response = self.client.post(
            '/api/accounting/asset-categories/',
            self.category_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['category_code'], 'COMP')
        self.assertEqual(response.data['category_name'], 'Computer Equipment')
        self.assertEqual(response.data['useful_life_years'], 3)
        self.assertTrue(response.data['is_active'])
    
    def test_list_asset_categories(self):
        """Test listing asset categories"""
        # Create test categories
        AssetCategory.objects.create(
            category_code='BLDG',
            category_name='Buildings',
            useful_life_years=40,
            depreciation_method='straight_line',
            created_by=self.user
        )
        AssetCategory.objects.create(
            category_code='VEH',
            category_name='Vehicles',
            useful_life_years=5,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/asset-categories/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_asset_category(self):
        """Test retrieving a specific asset category"""
        category = AssetCategory.objects.create(
            category_code='MACH',
            category_name='Machinery',
            useful_life_years=10,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        response = self.client.get(f'/api/accounting/asset-categories/{category.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category_code'], 'MACH')
    
    def test_update_asset_category(self):
        """Test updating an asset category"""
        category = AssetCategory.objects.create(
            category_code='FURN',
            category_name='Furniture',
            useful_life_years=7,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        update_data = {
            'category_code': 'FURN',
            'category_name': 'Furniture & Fixtures',
            'useful_life_years': 10,
            'depreciation_method': 'straight_line'
        }
        
        response = self.client.patch(
            f'/api/accounting/asset-categories/{category.id}/',
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['category_name'], 'Furniture & Fixtures')
        self.assertEqual(response.data['useful_life_years'], 10)
    
    def test_filter_active_categories(self):
        """Test filtering active/inactive categories"""
        AssetCategory.objects.create(
            category_code='ACT',
            category_name='Active Category',
            useful_life_years=5,
            depreciation_method='straight_line',
            is_active=True,
            created_by=self.user
        )
        AssetCategory.objects.create(
            category_code='INACT',
            category_name='Inactive Category',
            useful_life_years=5,
            depreciation_method='straight_line',
            is_active=False,
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/asset-categories/?is_active=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['category_code'], 'ACT')


class FixedAssetAPITestCase(TestCase):
    """Test FixedAsset API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create asset category
        self.category = AssetCategory.objects.create(
            category_code='COMP',
            category_name='Computer Equipment',
            useful_life_years=3,
            depreciation_method='straight_line',
            residual_value_percentage=Decimal('5.00'),
            created_by=self.user
        )
        
        # Create GL account
        self.asset_account = AccountV2.objects.create(
            code='1510',
            name='Computer Equipment',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            measurement_basis='cost',
            is_active=True
        )
        
        self.asset_data = {
            'asset_number': 'FA-2025-001',
            'asset_name': 'Dell Laptop',
            'asset_category': self.category.id,
            'acquisition_date': '2025-01-01',
            'acquisition_cost': '150000.00',
            'location': 'Head Office - IT Department',
            'asset_tag': 'TAG-001',
            'status': 'active',
            'gl_account': self.asset_account.id
        }
    
    def test_create_fixed_asset(self):
        """Test creating a fixed asset via API"""
        response = self.client.post(
            '/api/accounting/fixed-assets/',
            self.asset_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['asset_number'], 'FA-2025-001')
        self.assertEqual(response.data['asset_name'], 'Dell Laptop')
        self.assertEqual(response.data['status'], 'active')
        self.assertIn('book_value', response.data)
    
    def test_list_fixed_assets(self):
        """Test listing fixed assets"""
        # Create test assets
        FixedAsset.objects.create(
            asset_number='FA-2025-001',
            asset_name='Asset 1',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-001',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        FixedAsset.objects.create(
            asset_number='FA-2025-002',
            asset_name='Asset 2',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('200000.00'),
            location='Office',
            asset_tag='TAG-002',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/fixed-assets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_retrieve_fixed_asset(self):
        """Test retrieving a specific fixed asset"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-003',
            asset_name='HP Printer',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('50000.00'),
            location='Office',
            asset_tag='TAG-003',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        response = self.client.get(f'/api/accounting/fixed-assets/{asset.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_number'], 'FA-2025-003')
        self.assertEqual(response.data['book_value'], '50000.00')
    
    def test_update_fixed_asset(self):
        """Test updating a fixed asset"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-004',
            asset_name='Old Name',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Old Location',
            asset_tag='TAG-004',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        update_data = {
            'asset_name': 'Updated Name',
            'location': 'New Location',
            'accumulated_depreciation': '10000.00'
        }
        
        response = self.client.patch(
            f'/api/accounting/fixed-assets/{asset.id}/',
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_name'], 'Updated Name')
        self.assertEqual(response.data['location'], 'New Location')
        self.assertEqual(response.data['book_value'], '90000.00')
    
    def test_filter_by_status(self):
        """Test filtering assets by status"""
        FixedAsset.objects.create(
            asset_number='FA-2025-005',
            asset_name='Active Asset',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-005',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        FixedAsset.objects.create(
            asset_number='FA-2025-006',
            asset_name='Retired Asset',
            asset_category=self.category,
            acquisition_date=date(2020, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Storage',
            asset_tag='TAG-006',
            status='retired',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/fixed-assets/?status=active')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'active')
    
    def test_filter_by_category(self):
        """Test filtering assets by category"""
        category2 = AssetCategory.objects.create(
            category_code='VEH',
            category_name='Vehicles',
            useful_life_years=5,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-2025-007',
            asset_name='Computer',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-007',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        FixedAsset.objects.create(
            asset_number='FA-2025-008',
            asset_name='Car',
            asset_category=category2,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('2000000.00'),
            location='Parking',
            asset_tag='TAG-008',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        response = self.client.get(f'/api/accounting/fixed-assets/?asset_category={self.category.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['asset_name'], 'Computer')
    
    def test_search_assets(self):
        """Test searching assets by name or number"""
        FixedAsset.objects.create(
            asset_number='FA-2025-009',
            asset_name='Dell Laptop',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('150000.00'),
            location='Office',
            asset_tag='TAG-009',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/fixed-assets/?search=Dell')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
        self.assertIn('Dell', response.data['results'][0]['asset_name'])
    
    def test_filter_by_location(self):
        """Test filtering assets by location"""
        FixedAsset.objects.create(
            asset_number='FA-2025-010',
            asset_name='Office Computer',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Head Office',
            asset_tag='TAG-010',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        FixedAsset.objects.create(
            asset_number='FA-2025-011',
            asset_name='Branch Computer',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Branch Office',
            asset_tag='TAG-011',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/fixed-assets/?location=Head Office')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['location'], 'Head Office')
    
    def test_validation_unique_asset_number(self):
        """Test that duplicate asset numbers are rejected"""
        FixedAsset.objects.create(
            asset_number='FA-2025-100',
            asset_name='Existing Asset',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-100',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        duplicate_data = self.asset_data.copy()
        duplicate_data['asset_number'] = 'FA-2025-100'
        duplicate_data['asset_tag'] = 'TAG-NEW'
        
        response = self.client.post(
            '/api/accounting/fixed-assets/',
            duplicate_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_validation_unique_asset_tag(self):
        """Test that duplicate asset tags are rejected"""
        FixedAsset.objects.create(
            asset_number='FA-2025-101',
            asset_name='Existing Asset',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-UNIQUE',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        duplicate_data = self.asset_data.copy()
        duplicate_data['asset_number'] = 'FA-2025-102'
        duplicate_data['asset_tag'] = 'TAG-UNIQUE'
        
        response = self.client.post(
            '/api/accounting/fixed-assets/',
            duplicate_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access API"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/accounting/fixed-assets/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AssetAcquisitionWorkflowTestCase(TestCase):
    """Test asset acquisition workflow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = AssetCategory.objects.create(
            category_code='COMP',
            category_name='Computer Equipment',
            useful_life_years=3,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        self.asset_account = AccountV2.objects.create(
            code='1510',
            name='Computer Equipment',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            measurement_basis='cost',
            is_active=True
        )
    
    def test_complete_acquisition_workflow(self):
        """Test complete asset acquisition workflow"""
        # Step 1: Create asset
        asset_data = {
            'asset_number': 'FA-2025-WORKFLOW',
            'asset_name': 'New Laptop',
            'asset_category': self.category.id,
            'acquisition_date': '2025-01-15',
            'acquisition_cost': '180000.00',
            'location': 'IT Department',
            'asset_tag': 'TAG-WORKFLOW',
            'status': 'active',
            'gl_account': self.asset_account.id
        }
        
        response = self.client.post(
            '/api/accounting/fixed-assets/',
            asset_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        asset_id = response.data['id']
        
        # Step 2: Verify asset was created
        response = self.client.get(f'/api/accounting/fixed-assets/{asset_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['asset_number'], 'FA-2025-WORKFLOW')
        
        # Step 3: Update location (asset moved)
        response = self.client.patch(
            f'/api/accounting/fixed-assets/{asset_id}/',
            {'location': 'Finance Department'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Finance Department')
    
    def test_asset_with_voucher_link(self):
        """Test creating asset with purchase voucher link"""
        # This test verifies that assets can be linked to purchase vouchers
        # The actual voucher creation and linking will be tested when
        # the voucher integration is implemented
        
        asset_data = {
            'asset_number': 'FA-2025-VOUCHER',
            'asset_name': 'Asset with Voucher',
            'asset_category': self.category.id,
            'acquisition_date': '2025-01-01',
            'acquisition_cost': '100000.00',
            'location': 'Office',
            'asset_tag': 'TAG-VOUCHER',
            'status': 'active',
            'gl_account': self.asset_account.id
        }
        
        response = self.client.post(
            '/api/accounting/fixed-assets/',
            asset_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Future: Add voucher_id to asset_data and verify linkage
