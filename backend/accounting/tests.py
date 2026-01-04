"""
Unit Tests for IFRS Compliance Fields in AccountV2 Model
Tests IAS code validation, IFRS categories, measurement basis, and API responses
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal

from accounting.models import AccountV2
from accounting.serializers import AccountV2Serializer

User = get_user_model()


class AccountV2IFRSFieldsTestCase(TestCase):
    """Test IFRS compliance fields in AccountV2 model"""
    
    def setUp(self):
        """Create test user and sample accounts"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test account with IFRS fields
        self.cash_account = AccountV2.objects.create(
            code='1010',
            name='Cash in Hand',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 7',
            ifrs_category='financial_assets',
            measurement_basis='fair_value',
            created_by=self.user
        )
        
        self.inventory_account = AccountV2.objects.create(
            code='1030',
            name='Inventory',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 2',
            ifrs_category='financial_assets',
            measurement_basis='net_realizable_value',
            created_by=self.user
        )
    
    def test_ias_code_validation_valid_codes(self):
        """Test that valid IAS/IFRS codes are accepted"""
        valid_codes = ['IAS 1', 'IAS 7', 'IAS 16', 'IFRS 9', 'IFRS 15', 'IFRS 16']
        
        for code in valid_codes:
            account = AccountV2(
                code=f'TEST{code.replace(" ", "")}',
                name=f'Test Account for {code}',
                account_type='asset',
                account_group='current_asset',
                ias_reference_code=code,
                created_by=self.user
            )
            account.save()
            self.assertEqual(account.ias_reference_code, code)
    
    def test_ias_code_blank_allowed(self):
        """Test that blank IAS code is allowed"""
        account = AccountV2.objects.create(
            code='9999',
            name='Test Account No IAS',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='',  # Blank is allowed
            created_by=self.user
        )
        self.assertEqual(account.ias_reference_code, '')
    
    def test_ifrs_category_assignment(self):
        """Test IFRS category assignment"""
        categories = [
            'financial_assets',
            'financial_liabilities',
            'equity',
            'revenue',
            'expenses',
            'other_comprehensive_income'
        ]
        
        for idx, category in enumerate(categories):
            account = AccountV2.objects.create(
                code=f'CAT{idx}',
                name=f'Test {category}',
                account_type='asset',
                account_group='current_asset',
                ifrs_category=category,
                created_by=self.user
            )
            self.assertEqual(account.ifrs_category, category)
    
    def test_measurement_basis_options(self):
        """Test all measurement basis options"""
        bases = [
            'cost',
            'fair_value',
            'amortized_cost',
            'net_realizable_value',
            'value_in_use'
        ]
        
        for idx, basis in enumerate(bases):
            account = AccountV2.objects.create(
                code=f'MB{idx}',
                name=f'Test {basis}',
                account_type='asset',
                account_group='current_asset',
                measurement_basis=basis,
                created_by=self.user
            )
            self.assertEqual(account.measurement_basis, basis)
    
    def test_default_measurement_basis(self):
        """Test that default measurement basis is 'cost'"""
        account = AccountV2.objects.create(
            code='DEF001',
            name='Test Default Basis',
            account_type='asset',
            account_group='current_asset',
            created_by=self.user
        )
        self.assertEqual(account.measurement_basis, 'cost')
    
    def test_ifrs_subcategory_optional(self):
        """Test that IFRS subcategory is optional"""
        account = AccountV2.objects.create(
            code='SUB001',
            name='Test Subcategory',
            account_type='asset',
            account_group='current_asset',
            ifrs_subcategory='Property, Plant and Equipment',
            created_by=self.user
        )
        self.assertEqual(account.ifrs_subcategory, 'Property, Plant and Equipment')
        
        # Test blank subcategory
        account2 = AccountV2.objects.create(
            code='SUB002',
            name='Test No Subcategory',
            account_type='asset',
            account_group='current_asset',
            ifrs_subcategory='',
            created_by=self.user
        )
        self.assertEqual(account2.ifrs_subcategory, '')
    
    def test_ias_code_choices_comprehensive(self):
        """Test that all 41 IAS/IFRS codes are available"""
        # Get all choices from model
        ias_codes = [choice[0] for choice in AccountV2.IAS_IFRS_CODES]
        
        # Should have 41 IAS codes + 2 additional + 1 blank option = 44 total
        self.assertEqual(len(ias_codes), 44)
        
        # Check specific important codes
        self.assertIn('IAS 1', ias_codes)
        self.assertIn('IAS 2', ias_codes)
        self.assertIn('IAS 7', ias_codes)
        self.assertIn('IAS 16', ias_codes)
        self.assertIn('IFRS 9', ias_codes)
        self.assertIn('IFRS 15', ias_codes)
        self.assertIn('IFRS 16', ias_codes)
        self.assertIn('', ias_codes)  # Blank option


class AccountV2IFRSAPITestCase(APITestCase):
    """Test IFRS fields through API endpoints"""
    
    def setUp(self):
        """Create test user and authenticate"""
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_account_with_ifrs_fields(self):
        """Test creating account with IFRS fields via API"""
        data = {
            'code': 'API001',
            'name': 'API Test Account',
            'account_type': 'asset',
            'account_group': 'current_asset',
            'ias_reference_code': 'IAS 7',
            'ifrs_category': 'financial_assets',
            'ifrs_subcategory': 'Cash and Cash Equivalents',
            'measurement_basis': 'fair_value'
        }
        
        response = self.client.post('/api/accounting/accounts-v2/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ias_reference_code'], 'IAS 7')
        self.assertEqual(response.data['ifrs_category'], 'financial_assets')
        self.assertEqual(response.data['measurement_basis'], 'fair_value')
    
    def test_update_account_ifrs_fields(self):
        """Test updating IFRS fields via API"""
        account = AccountV2.objects.create(
            code='UPD001',
            name='Update Test',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 2',
            created_by=self.user
        )
        
        data = {
            'ias_reference_code': 'IAS 16',
            'ifrs_category': 'financial_assets',
            'measurement_basis': 'cost'
        }
        
        response = self.client.patch(
            f'/api/accounting/accounts-v2/{account.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ias_reference_code'], 'IAS 16')
    
    def test_get_account_with_ifrs_fields(self):
        """Test retrieving account with IFRS fields"""
        account = AccountV2.objects.create(
            code='GET001',
            name='Get Test',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IFRS 9',
            ifrs_category='financial_assets',
            measurement_basis='amortized_cost',
            created_by=self.user
        )
        
        response = self.client.get(f'/api/accounting/accounts-v2/{account.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ias_reference_code'], 'IFRS 9')
        self.assertEqual(response.data['ifrs_category'], 'financial_assets')
        self.assertEqual(response.data['measurement_basis'], 'amortized_cost')
    
    def test_list_accounts_with_ifrs_fields(self):
        """Test listing accounts includes IFRS fields"""
        AccountV2.objects.create(
            code='LIST001',
            name='List Test 1',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 7',
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/accounts-v2/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
        
        # Check that IFRS fields are in response
        first_account = response.data[0]
        self.assertIn('ias_reference_code', first_account)
        self.assertIn('ifrs_category', first_account)
        self.assertIn('measurement_basis', first_account)


class AccountV2SerializerTestCase(TestCase):
    """Test AccountV2Serializer with IFRS fields"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='serializeruser',
            password='serpass123'
        )
    
    def test_serializer_includes_ifrs_fields(self):
        """Test that serializer includes all IFRS fields"""
        account = AccountV2.objects.create(
            code='SER001',
            name='Serializer Test',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            ifrs_subcategory='Property, Plant and Equipment',
            measurement_basis='cost',
            created_by=self.user
        )
        
        serializer = AccountV2Serializer(account)
        data = serializer.data
        
        self.assertEqual(data['ias_reference_code'], 'IAS 16')
        self.assertEqual(data['ifrs_category'], 'financial_assets')
        self.assertEqual(data['ifrs_subcategory'], 'Property, Plant and Equipment')
        self.assertEqual(data['measurement_basis'], 'cost')
    
    def test_serializer_validation_valid_data(self):
        """Test serializer validation with valid IFRS data"""
        data = {
            'code': 'VAL001',
            'name': 'Validation Test',
            'account_type': 'asset',
            'account_group': 'current_asset',
            'ias_reference_code': 'IFRS 15',
            'ifrs_category': 'revenue',
            'measurement_basis': 'cost'
        }
        
        serializer = AccountV2Serializer(data=data)
        self.assertTrue(serializer.is_valid())


class IFRSBusinessLogicTestCase(TestCase):
    """Test IFRS-specific business logic"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='logicuser',
            password='logicpass123'
        )
    
    def test_cash_account_ifrs_mapping(self):
        """Test that cash accounts follow IAS 7"""
        cash = AccountV2.objects.create(
            code='1010',
            name='Cash',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 7',
            ifrs_category='financial_assets',
            measurement_basis='fair_value',
            created_by=self.user
        )
        
        self.assertEqual(cash.ias_reference_code, 'IAS 7')
        self.assertEqual(cash.measurement_basis, 'fair_value')
    
    def test_inventory_account_ifrs_mapping(self):
        """Test that inventory accounts follow IAS 2"""
        inventory = AccountV2.objects.create(
            code='1030',
            name='Inventory',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 2',
            ifrs_category='financial_assets',
            measurement_basis='net_realizable_value',
            created_by=self.user
        )
        
        self.assertEqual(inventory.ias_reference_code, 'IAS 2')
        self.assertEqual(inventory.measurement_basis, 'net_realizable_value')
    
    def test_ppe_account_ifrs_mapping(self):
        """Test that PPE accounts follow IAS 16"""
        building = AccountV2.objects.create(
            code='1510',
            name='Buildings',
            account_type='asset',
            account_group='fixed_asset',
            ias_reference_code='IAS 16',
            ifrs_category='financial_assets',
            measurement_basis='cost',
            created_by=self.user
        )
        
        self.assertEqual(building.ias_reference_code, 'IAS 16')
        self.assertEqual(building.measurement_basis, 'cost')
    
    def test_revenue_account_ifrs_mapping(self):
        """Test that revenue accounts follow IFRS 15"""
        sales = AccountV2.objects.create(
            code='4000',
            name='Sales Revenue',
            account_type='revenue',
            account_group='sales',
            ias_reference_code='IFRS 15',
            ifrs_category='revenue',
            measurement_basis='cost',
            created_by=self.user
        )
        
        self.assertEqual(sales.ias_reference_code, 'IFRS 15')
        self.assertEqual(sales.ifrs_category, 'revenue')


class IFRSCoverageTestCase(TestCase):
    """Test coverage of IFRS standards"""
    
    def test_all_ias_standards_available(self):
        """Test that all major IAS standards are in choices"""
        ias_codes = [choice[0] for choice in AccountV2.IAS_IFRS_CODES]
        
        major_ias = [
            'IAS 1', 'IAS 2', 'IAS 7', 'IAS 8', 'IAS 10',
            'IAS 12', 'IAS 16', 'IAS 19', 'IAS 21', 'IAS 36',
            'IAS 37', 'IAS 38', 'IAS 40'
        ]
        
        for code in major_ias:
            self.assertIn(code, ias_codes, f"{code} should be in IAS_IFRS_CODES")
    
    def test_all_ifrs_standards_available(self):
        """Test that all major IFRS standards are in choices"""
        ias_codes = [choice[0] for choice in AccountV2.IAS_IFRS_CODES]
        
        major_ifrs = [
            'IFRS 1', 'IFRS 2', 'IFRS 3', 'IFRS 7', 'IFRS 9',
            'IFRS 10', 'IFRS 13', 'IFRS 15', 'IFRS 16', 'IFRS 17'
        ]
        
        for code in major_ifrs:
            self.assertIn(code, ias_codes, f"{code} should be in IAS_IFRS_CODES")
    
    def test_measurement_basis_coverage(self):
        """Test that all IFRS measurement bases are covered"""
        bases = [choice[0] for choice in AccountV2.MEASUREMENT_BASIS]
        
        required_bases = [
            'cost',
            'fair_value',
            'amortized_cost',
            'net_realizable_value',
            'value_in_use'
        ]
        
        for basis in required_bases:
            self.assertIn(basis, bases, f"{basis} should be in MEASUREMENT_BASIS")
    
    def test_ifrs_category_coverage(self):
        """Test that all IFRS categories are covered"""
        categories = [choice[0] for choice in AccountV2.IFRS_CATEGORIES]
        
        required_categories = [
            'financial_assets',
            'financial_liabilities',
            'equity',
            'revenue',
            'expenses',
            'other_comprehensive_income'
        ]
        
        for category in required_categories:
            self.assertIn(category, categories, f"{category} should be in IFRS_CATEGORIES")
