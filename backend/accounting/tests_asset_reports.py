"""
Unit Tests for Asset Reports (Task 3.1.3)
Module 3.1: Fixed Asset Register
IAS 16 Compliance: Asset Reporting and Disclosure

Test Coverage:
1. Fixed Asset Register (FAR) - Complete asset listing with book values
2. Asset by Category Report - Grouped by asset category
3. Asset by Location Report - Grouped by location
4. Report data accuracy and calculations
5. IAS 16 disclosure requirements
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date
from accounting.models import AssetCategory, FixedAsset, AccountV2

User = get_user_model()


class FixedAssetRegisterReportTestCase(TestCase):
    """Test Fixed Asset Register (FAR) Report"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create asset categories
        self.category_computer = AssetCategory.objects.create(
            category_code='COMP',
            category_name='Computer Equipment',
            useful_life_years=3,
            depreciation_method='straight_line',
            residual_value_percentage=Decimal('5.00'),
            created_by=self.user
        )
        
        self.category_vehicle = AssetCategory.objects.create(
            category_code='VEH',
            category_name='Vehicles',
            useful_life_years=5,
            depreciation_method='straight_line',
            residual_value_percentage=Decimal('20.00'),
            created_by=self.user
        )
        
        # Create GL accounts
        self.asset_account = AccountV2.objects.create(
            code='1510',
            name='Fixed Assets',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            measurement_basis='cost',
            is_active=True
        )
        
        # Create test assets
        FixedAsset.objects.create(
            asset_number='FA-2025-001',
            asset_name='Dell Laptop',
            asset_category=self.category_computer,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('150000.00'),
            accumulated_depreciation=Decimal('10000.00'),
            location='Head Office - IT Department',
            asset_tag='TAG-001',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-2025-002',
            asset_name='HP Printer',
            asset_category=self.category_computer,
            acquisition_date=date(2025, 1, 15),
            acquisition_cost=Decimal('50000.00'),
            accumulated_depreciation=Decimal('5000.00'),
            location='Head Office - Admin',
            asset_tag='TAG-002',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-2025-003',
            asset_name='Toyota Corolla',
            asset_category=self.category_vehicle,
            acquisition_date=date(2024, 1, 1),
            acquisition_cost=Decimal('2000000.00'),
            accumulated_depreciation=Decimal('400000.00'),
            location='Head Office - Parking',
            asset_tag='VEH-001',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
    
    def test_far_report_endpoint_exists(self):
        """Test that FAR report endpoint exists"""
        response = self.client.get('/api/accounting/reports/fixed-asset-register/')
        
        # Should return 200 or 404, not 500
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
    
    def test_far_report_returns_all_assets(self):
        """Test that FAR report returns all assets"""
        response = self.client.get('/api/accounting/reports/fixed-asset-register/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('assets', response.data)
        self.assertEqual(len(response.data['assets']), 3)
    
    def test_far_report_includes_required_fields(self):
        """Test that FAR report includes all required IAS 16 fields"""
        response = self.client.get('/api/accounting/reports/fixed-asset-register/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        asset = response.data['assets'][0]
        required_fields = [
            'asset_number', 'asset_name', 'category_name', 'acquisition_date',
            'acquisition_cost', 'accumulated_depreciation', 'book_value',
            'location', 'status'
        ]
        
        for field in required_fields:
            self.assertIn(field, asset)
    
    def test_far_report_book_value_calculation(self):
        """Test that FAR report correctly calculates book values"""
        response = self.client.get('/api/accounting/reports/fixed-asset-register/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find the laptop asset
        laptop = next(a for a in response.data['assets'] if a['asset_number'] == 'FA-2025-001')
        
        expected_book_value = Decimal('140000.00')  # 150000 - 10000
        self.assertEqual(Decimal(laptop['book_value']), expected_book_value)
    
    def test_far_report_summary_totals(self):
        """Test that FAR report includes summary totals"""
        response = self.client.get('/api/accounting/reports/fixed-asset-register/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        
        summary = response.data['summary']
        self.assertIn('total_acquisition_cost', summary)
        self.assertIn('total_accumulated_depreciation', summary)
        self.assertIn('total_book_value', summary)
        self.assertIn('total_assets', summary)
        
        # Verify totals
        self.assertEqual(summary['total_assets'], 3)
        self.assertEqual(Decimal(summary['total_acquisition_cost']), Decimal('2200000.00'))
        self.assertEqual(Decimal(summary['total_accumulated_depreciation']), Decimal('415000.00'))
        self.assertEqual(Decimal(summary['total_book_value']), Decimal('1785000.00'))
    
    def test_far_report_filter_by_status(self):
        """Test filtering FAR report by asset status"""
        # Create a disposed asset
        FixedAsset.objects.create(
            asset_number='FA-2025-004',
            asset_name='Old Computer',
            asset_category=self.category_computer,
            acquisition_date=date(2020, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            accumulated_depreciation=Decimal('100000.00'),
            location='Storage',
            asset_tag='TAG-OLD',
            status='disposed',
            disposal_date=date(2025, 1, 1),
            disposal_amount=Decimal('5000.00'),
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/reports/fixed-asset-register/?status=active')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['assets']), 3)  # Only active assets
    
    def test_far_report_filter_by_category(self):
        """Test filtering FAR report by category"""
        response = self.client.get(
            f'/api/accounting/reports/fixed-asset-register/?category={self.category_computer.id}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['assets']), 2)  # Only computer assets
    
    def test_far_report_filter_by_date_range(self):
        """Test filtering FAR report by acquisition date range"""
        response = self.client.get(
            '/api/accounting/reports/fixed-asset-register/?start_date=2025-01-01&end_date=2025-12-31'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['assets']), 2)  # Only 2025 acquisitions


class AssetByCategoryReportTestCase(TestCase):
    """Test Asset by Category Report"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create asset categories
        self.category_computer = AssetCategory.objects.create(
            category_code='COMP',
            category_name='Computer Equipment',
            useful_life_years=3,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        self.category_furniture = AssetCategory.objects.create(
            category_code='FURN',
            category_name='Furniture',
            useful_life_years=7,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        # Create GL account
        self.asset_account = AccountV2.objects.create(
            code='1510',
            name='Fixed Assets',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            measurement_basis='cost',
            is_active=True
        )
        
        # Create assets in different categories
        FixedAsset.objects.create(
            asset_number='FA-COMP-001',
            asset_name='Laptop 1',
            asset_category=self.category_computer,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('150000.00'),
            accumulated_depreciation=Decimal('10000.00'),
            location='Office',
            asset_tag='TAG-C1',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-COMP-002',
            asset_name='Laptop 2',
            asset_category=self.category_computer,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('160000.00'),
            accumulated_depreciation=Decimal('15000.00'),
            location='Office',
            asset_tag='TAG-C2',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-FURN-001',
            asset_name='Desk',
            asset_category=self.category_furniture,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('50000.00'),
            accumulated_depreciation=Decimal('5000.00'),
            location='Office',
            asset_tag='TAG-F1',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
    
    def test_category_report_endpoint_exists(self):
        """Test that category report endpoint exists"""
        response = self.client.get('/api/accounting/reports/assets-by-category/')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
    
    def test_category_report_groups_by_category(self):
        """Test that report groups assets by category"""
        response = self.client.get('/api/accounting/reports/assets-by-category/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categories', response.data)
        self.assertEqual(len(response.data['categories']), 2)
    
    def test_category_report_includes_category_details(self):
        """Test that report includes category details"""
        response = self.client.get('/api/accounting/reports/assets-by-category/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        category = response.data['categories'][0]
        required_fields = [
            'category_code', 'category_name', 'asset_count',
            'total_acquisition_cost', 'total_accumulated_depreciation',
            'total_book_value'
        ]
        
        for field in required_fields:
            self.assertIn(field, category)
    
    def test_category_report_calculations(self):
        """Test that category report calculations are correct"""
        response = self.client.get('/api/accounting/reports/assets-by-category/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find computer category
        comp_category = next(
            c for c in response.data['categories'] 
            if c['category_code'] == 'COMP'
        )
        
        self.assertEqual(comp_category['asset_count'], 2)
        self.assertEqual(Decimal(comp_category['total_acquisition_cost']), Decimal('310000.00'))
        self.assertEqual(Decimal(comp_category['total_accumulated_depreciation']), Decimal('25000.00'))
        self.assertEqual(Decimal(comp_category['total_book_value']), Decimal('285000.00'))
    
    def test_category_report_summary(self):
        """Test that category report includes overall summary"""
        response = self.client.get('/api/accounting/reports/assets-by-category/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        
        summary = response.data['summary']
        self.assertEqual(summary['total_categories'], 2)
        self.assertEqual(summary['total_assets'], 3)


class AssetByLocationReportTestCase(TestCase):
    """Test Asset by Location Report"""
    
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
            created_by=self.user
        )
        
        # Create GL account
        self.asset_account = AccountV2.objects.create(
            code='1510',
            name='Fixed Assets',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            measurement_basis='cost',
            is_active=True
        )
        
        # Create assets in different locations
        FixedAsset.objects.create(
            asset_number='FA-HO-001',
            asset_name='Laptop HO 1',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('150000.00'),
            accumulated_depreciation=Decimal('10000.00'),
            location='Head Office',
            asset_tag='TAG-HO1',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-HO-002',
            asset_name='Laptop HO 2',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('160000.00'),
            accumulated_depreciation=Decimal('15000.00'),
            location='Head Office',
            asset_tag='TAG-HO2',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-BR-001',
            asset_name='Laptop Branch',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('140000.00'),
            accumulated_depreciation=Decimal('12000.00'),
            location='Branch Office',
            asset_tag='TAG-BR1',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
    
    def test_location_report_endpoint_exists(self):
        """Test that location report endpoint exists"""
        response = self.client.get('/api/accounting/reports/assets-by-location/')
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
    
    def test_location_report_groups_by_location(self):
        """Test that report groups assets by location"""
        response = self.client.get('/api/accounting/reports/assets-by-location/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('locations', response.data)
        self.assertEqual(len(response.data['locations']), 2)
    
    def test_location_report_includes_location_details(self):
        """Test that report includes location details"""
        response = self.client.get('/api/accounting/reports/assets-by-location/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        location = response.data['locations'][0]
        required_fields = [
            'location', 'asset_count', 'total_acquisition_cost',
            'total_accumulated_depreciation', 'total_book_value'
        ]
        
        for field in required_fields:
            self.assertIn(field, location)
    
    def test_location_report_calculations(self):
        """Test that location report calculations are correct"""
        response = self.client.get('/api/accounting/reports/assets-by-location/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find Head Office location
        head_office = next(
            loc for loc in response.data['locations']
            if loc['location'] == 'Head Office'
        )
        
        self.assertEqual(head_office['asset_count'], 2)
        self.assertEqual(Decimal(head_office['total_acquisition_cost']), Decimal('310000.00'))
        self.assertEqual(Decimal(head_office['total_accumulated_depreciation']), Decimal('25000.00'))
        self.assertEqual(Decimal(head_office['total_book_value']), Decimal('285000.00'))
    
    def test_location_report_summary(self):
        """Test that location report includes overall summary"""
        response = self.client.get('/api/accounting/reports/assets-by-location/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        
        summary = response.data['summary']
        self.assertEqual(summary['total_locations'], 2)
        self.assertEqual(summary['total_assets'], 3)
    
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access reports"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/accounting/reports/assets-by-location/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
