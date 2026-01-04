"""
Unit Tests for Fixed Asset Register (Task 3.1.1)
Module 3.1: Fixed Asset Register
IAS 16 Compliance: Property, Plant and Equipment

Test Coverage:
1. AssetCategory model creation and validation
2. FixedAsset model creation and validation
3. Asset lifecycle (acquisition, active, disposed)
4. Book value calculation
5. Asset numbering uniqueness
6. Asset tagging uniqueness
7. IAS 16 compliance fields
8. Status transitions
9. Disposal workflow
10. Relationships and foreign keys
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from accounting.models import AssetCategory, FixedAsset, AccountV2

User = get_user_model()


class AssetCategoryModelTestCase(TestCase):
    """Test AssetCategory model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_asset_category_creation(self):
        """Test creating an asset category"""
        category = AssetCategory.objects.create(
            category_code='BLDG',
            category_name='Buildings',
            description='Office and warehouse buildings',
            useful_life_years=40,
            depreciation_method='straight_line',
            residual_value_percentage=Decimal('10.00'),
            ias_reference_code='IAS 16',
            created_by=self.user
        )
        
        self.assertEqual(category.category_code, 'BLDG')
        self.assertEqual(category.category_name, 'Buildings')
        self.assertEqual(category.useful_life_years, 40)
        self.assertEqual(category.depreciation_method, 'straight_line')
        self.assertEqual(category.residual_value_percentage, Decimal('10.00'))
        self.assertEqual(category.ias_reference_code, 'IAS 16')
        self.assertTrue(category.is_active)
    
    def test_asset_category_unique_code(self):
        """Test that category codes must be unique"""
        AssetCategory.objects.create(
            category_code='MACH',
            category_name='Machinery',
            useful_life_years=10,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        # Attempt to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            AssetCategory.objects.create(
                category_code='MACH',
                category_name='Machinery 2',
                useful_life_years=10,
                depreciation_method='straight_line',
                created_by=self.user
            )
    
    def test_asset_category_depreciation_methods(self):
        """Test all depreciation methods are available"""
        methods = ['straight_line', 'declining_balance', 'units_of_production']
        
        for method in methods:
            category = AssetCategory.objects.create(
                category_code=f'TEST{method[:4].upper()}',
                category_name=f'Test {method}',
                useful_life_years=5,
                depreciation_method=method,
                created_by=self.user
            )
            self.assertEqual(category.depreciation_method, method)
    
    def test_asset_category_string_representation(self):
        """Test string representation"""
        category = AssetCategory.objects.create(
            category_code='VEH',
            category_name='Vehicles',
            useful_life_years=5,
            depreciation_method='straight_line',
            created_by=self.user
        )
        
        self.assertEqual(str(category), 'VEH - Vehicles')


class FixedAssetModelTestCase(TestCase):
    """Test FixedAsset model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create asset category
        self.category = AssetCategory.objects.create(
            category_code='COMP',
            category_name='Computer Equipment',
            description='Computers, laptops, servers',
            useful_life_years=3,
            depreciation_method='straight_line',
            residual_value_percentage=Decimal('5.00'),
            ias_reference_code='IAS 16',
            created_by=self.user
        )
        
        # Create GL account for fixed assets
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
    
    def test_fixed_asset_creation(self):
        """Test creating a fixed asset"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-001',
            asset_name='Dell Laptop',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('150000.00'),
            accumulated_depreciation=Decimal('0.00'),
            location='Head Office - IT Department',
            asset_tag='TAG-001',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        self.assertEqual(asset.asset_number, 'FA-2025-001')
        self.assertEqual(asset.asset_name, 'Dell Laptop')
        self.assertEqual(asset.asset_category, self.category)
        self.assertEqual(asset.acquisition_cost, Decimal('150000.00'))
        self.assertEqual(asset.accumulated_depreciation, Decimal('0.00'))
        self.assertEqual(asset.status, 'active')
        self.assertIsNotNone(asset.created_at)
    
    def test_fixed_asset_book_value_calculation(self):
        """Test automatic book value calculation"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-002',
            asset_name='HP Printer',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('50000.00'),
            accumulated_depreciation=Decimal('10000.00'),
            location='Head Office',
            asset_tag='TAG-002',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        # Book value should be acquisition_cost - accumulated_depreciation
        expected_book_value = Decimal('40000.00')
        self.assertEqual(asset.book_value, expected_book_value)
    
    def test_fixed_asset_unique_asset_number(self):
        """Test that asset numbers must be unique"""
        FixedAsset.objects.create(
            asset_number='FA-2025-003',
            asset_name='Asset 1',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-003',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        # Attempt to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            FixedAsset.objects.create(
                asset_number='FA-2025-003',
                asset_name='Asset 2',
                asset_category=self.category,
                acquisition_date=date(2025, 1, 1),
                acquisition_cost=Decimal('100000.00'),
                location='Office',
                asset_tag='TAG-004',
                status='active',
                gl_account=self.asset_account,
                created_by=self.user
            )
    
    def test_fixed_asset_unique_asset_tag(self):
        """Test that asset tags must be unique"""
        FixedAsset.objects.create(
            asset_number='FA-2025-004',
            asset_name='Asset 1',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-UNIQUE',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        # Attempt to create duplicate tag
        with self.assertRaises(Exception):  # IntegrityError
            FixedAsset.objects.create(
                asset_number='FA-2025-005',
                asset_name='Asset 2',
                asset_category=self.category,
                acquisition_date=date(2025, 1, 1),
                acquisition_cost=Decimal('100000.00'),
                location='Office',
                asset_tag='TAG-UNIQUE',
                status='active',
                gl_account=self.asset_account,
                created_by=self.user
            )
    
    def test_fixed_asset_status_choices(self):
        """Test all asset status choices"""
        statuses = ['active', 'disposed', 'under_maintenance', 'retired']
        
        for idx, status in enumerate(statuses, start=1):
            # For disposed status, we need disposal_date and disposal_amount
            if status == 'disposed':
                asset = FixedAsset.objects.create(
                    asset_number=f'FA-2025-{100+idx}',
                    asset_name=f'Asset {status}',
                    asset_category=self.category,
                    acquisition_date=date(2025, 1, 1),
                    acquisition_cost=Decimal('100000.00'),
                    location='Office',
                    asset_tag=f'TAG-{100+idx}',
                    status=status,
                    disposal_date=date(2025, 12, 31),
                    disposal_amount=Decimal('50000.00'),
                    gl_account=self.asset_account,
                    created_by=self.user
                )
            else:
                asset = FixedAsset.objects.create(
                    asset_number=f'FA-2025-{100+idx}',
                    asset_name=f'Asset {status}',
                    asset_category=self.category,
                    acquisition_date=date(2025, 1, 1),
                    acquisition_cost=Decimal('100000.00'),
                    location='Office',
                    asset_tag=f'TAG-{100+idx}',
                    status=status,
                    gl_account=self.asset_account,
                    created_by=self.user
                )
            self.assertEqual(asset.status, status)
    
    def test_fixed_asset_disposal(self):
        """Test asset disposal workflow"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-006',
            asset_name='Old Computer',
            asset_category=self.category,
            acquisition_date=date(2022, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            accumulated_depreciation=Decimal('80000.00'),
            location='Office',
            asset_tag='TAG-006',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        # Dispose the asset
        disposal_date = date(2025, 12, 31)
        disposal_amount = Decimal('15000.00')
        
        asset.status = 'disposed'
        asset.disposal_date = disposal_date
        asset.disposal_amount = disposal_amount
        asset.save()
        
        self.assertEqual(asset.status, 'disposed')
        self.assertEqual(asset.disposal_date, disposal_date)
        self.assertEqual(asset.disposal_amount, disposal_amount)
        
        # Calculate gain/loss on disposal
        book_value_at_disposal = asset.acquisition_cost - asset.accumulated_depreciation
        gain_loss = disposal_amount - book_value_at_disposal
        
        # In this case: 15,000 - 20,000 = -5,000 (loss)
        self.assertEqual(gain_loss, Decimal('-5000.00'))
    
    def test_fixed_asset_string_representation(self):
        """Test string representation"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-007',
            asset_name='MacBook Pro',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('200000.00'),
            location='Office',
            asset_tag='TAG-007',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        self.assertEqual(str(asset), 'FA-2025-007 - MacBook Pro')
    
    def test_fixed_asset_ordering(self):
        """Test default ordering by asset_number"""
        FixedAsset.objects.create(
            asset_number='FA-2025-010',
            asset_name='Asset C',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-010',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-2025-008',
            asset_name='Asset A',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-008',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        FixedAsset.objects.create(
            asset_number='FA-2025-009',
            asset_name='Asset B',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            location='Office',
            asset_tag='TAG-009',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        assets = list(FixedAsset.objects.all().values_list('asset_number', flat=True))
        # Should be ordered by asset_number
        self.assertTrue(assets.index('FA-2025-008') < assets.index('FA-2025-009'))
        self.assertTrue(assets.index('FA-2025-009') < assets.index('FA-2025-010'))


class FixedAssetIAS16ComplianceTestCase(TestCase):
    """Test IAS 16 compliance features"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = AssetCategory.objects.create(
            category_code='BLDG',
            category_name='Buildings',
            useful_life_years=40,
            depreciation_method='straight_line',
            residual_value_percentage=Decimal('10.00'),
            ias_reference_code='IAS 16',
            created_by=self.user
        )
        
        self.asset_account = AccountV2.objects.create(
            code='1520',
            name='Buildings',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            measurement_basis='cost',
            is_active=True
        )
    
    def test_ias16_cost_model(self):
        """Test IAS 16 cost model measurement"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-020',
            asset_name='Office Building',
            asset_category=self.category,
            acquisition_date=date(2025, 1, 1),
            acquisition_cost=Decimal('10000000.00'),
            accumulated_depreciation=Decimal('0.00'),
            location='Karachi',
            asset_tag='BLDG-001',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        # IAS 16 requires cost model: Cost - Accumulated Depreciation
        self.assertEqual(asset.book_value, Decimal('10000000.00'))
        
        # After 1 year depreciation (assuming straight-line over 40 years)
        # Annual depreciation = (Cost - Residual Value) / Useful Life
        # Residual = 10,000,000 * 10% = 1,000,000
        # Annual = (10,000,000 - 1,000,000) / 40 = 225,000
        asset.accumulated_depreciation = Decimal('225000.00')
        asset.save()
        
        self.assertEqual(asset.book_value, Decimal('9775000.00'))
    
    def test_ias16_category_has_useful_life(self):
        """Test that asset categories have useful life (IAS 16 requirement)"""
        self.assertIsNotNone(self.category.useful_life_years)
        self.assertGreater(self.category.useful_life_years, 0)
    
    def test_ias16_category_has_depreciation_method(self):
        """Test that asset categories have depreciation method (IAS 16 requirement)"""
        self.assertIsNotNone(self.category.depreciation_method)
        self.assertIn(self.category.depreciation_method, 
                     ['straight_line', 'declining_balance', 'units_of_production'])
    
    def test_ias16_category_has_residual_value(self):
        """Test that asset categories have residual value (IAS 16 requirement)"""
        self.assertIsNotNone(self.category.residual_value_percentage)
        self.assertGreaterEqual(self.category.residual_value_percentage, Decimal('0.00'))
        self.assertLessEqual(self.category.residual_value_percentage, Decimal('100.00'))


class FixedAssetBusinessLogicTestCase(TestCase):
    """Test business logic and calculations"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.category = AssetCategory.objects.create(
            category_code='VEH',
            category_name='Vehicles',
            useful_life_years=5,
            depreciation_method='straight_line',
            residual_value_percentage=Decimal('20.00'),
            ias_reference_code='IAS 16',
            created_by=self.user
        )
        
        self.asset_account = AccountV2.objects.create(
            code='1530',
            name='Vehicles',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            measurement_basis='cost',
            is_active=True
        )
    
    def test_calculate_gain_on_disposal(self):
        """Test calculation of gain on disposal"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-030',
            asset_name='Toyota Corolla',
            asset_category=self.category,
            acquisition_date=date(2020, 1, 1),
            acquisition_cost=Decimal('2000000.00'),
            accumulated_depreciation=Decimal('1600000.00'),
            location='Head Office',
            asset_tag='VEH-001',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        # Book value = 2,000,000 - 1,600,000 = 400,000
        book_value = asset.book_value
        self.assertEqual(book_value, Decimal('400000.00'))
        
        # Sold for 500,000 (gain of 100,000)
        disposal_amount = Decimal('500000.00')
        gain = disposal_amount - book_value
        
        self.assertEqual(gain, Decimal('100000.00'))
    
    def test_calculate_loss_on_disposal(self):
        """Test calculation of loss on disposal"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-031',
            asset_name='Honda Civic',
            asset_category=self.category,
            acquisition_date=date(2020, 1, 1),
            acquisition_cost=Decimal('2500000.00'),
            accumulated_depreciation=Decimal('1500000.00'),
            location='Branch Office',
            asset_tag='VEH-002',
            status='active',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        # Book value = 2,500,000 - 1,500,000 = 1,000,000
        book_value = asset.book_value
        self.assertEqual(book_value, Decimal('1000000.00'))
        
        # Sold for 800,000 (loss of 200,000)
        disposal_amount = Decimal('800000.00')
        loss = disposal_amount - book_value
        
        self.assertEqual(loss, Decimal('-200000.00'))
    
    def test_zero_book_value_fully_depreciated(self):
        """Test fully depreciated asset (book value = 0)"""
        asset = FixedAsset.objects.create(
            asset_number='FA-2025-032',
            asset_name='Old Laptop',
            asset_category=self.category,
            acquisition_date=date(2015, 1, 1),
            acquisition_cost=Decimal('100000.00'),
            accumulated_depreciation=Decimal('100000.00'),
            location='Storage',
            asset_tag='COMP-OLD-001',
            status='retired',
            gl_account=self.asset_account,
            created_by=self.user
        )
        
        self.assertEqual(asset.book_value, Decimal('0.00'))
