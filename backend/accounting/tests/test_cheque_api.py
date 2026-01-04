"""
API Tests for Cheque Management System
Task 1.1: Create Cheque API Tests
Module 2.2: Cheque Management System

Tests all API endpoints for Cheque CRUD operations and custom actions.
Follows TDD principles and IFRS/IAS 7 compliance.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounting.models import AccountV2, Cheque, VoucherV2, CurrencyV2
from partners.models import BusinessPartner
from decimal import Decimal
import datetime

User = get_user_model()


class ChequeAPITestCase(APITestCase):
    """
    Comprehensive test suite for Cheque API endpoints
    
    Tests:
    - CRUD operations (5 tests)
    - Custom actions (4 tests)
    - Filtering (2 tests)
    - Validation (4 tests)
    
    Total: 15 tests
    """

    def setUp(self):
        """Set up test data for all tests"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create currency
        self.currency = CurrencyV2.objects.create(
            currency_code='PKR',
            currency_name='Pakistani Rupee',
            symbol='₨',
            is_base_currency=True
        )
        
        # Create bank account
        self.bank_account = AccountV2.objects.create(
            code='1010',
            name='Bank Account - HBL',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 7',
            ifrs_category='financial_assets',
            measurement_basis='fair_value',
            is_active=True,
            created_by=self.user
        )
        
        # Create payee (business partner)
        self.payee = BusinessPartner.objects.create(
            name='ABC Suppliers',
            partner_type='supplier',
            email='abc@example.com',
            phone='03001234567'
        )
        
        # Create a test cheque
        self.cheque = Cheque.objects.create(
            cheque_number='CHQ-001',
            cheque_date=datetime.date(2025, 1, 15),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('50000.00'),
            status='issued',
            is_post_dated=False,
            created_by=self.user
        )

    # ========================================================================
    # CRUD OPERATIONS TESTS (5 tests)
    # ========================================================================

    def test_list_cheques(self):
        """Test GET /api/accounting/cheques/ - List all cheques"""
        url = reverse('cheque-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['cheque_number'], 'CHQ-001')

    def test_create_cheque(self):
        """Test POST /api/accounting/cheques/ - Create new cheque"""
        url = reverse('cheque-list')
        
        data = {
            'cheque_number': 'CHQ-002',
            'cheque_date': '2025-01-20',
            'bank_account': self.bank_account.id,
            'payee': self.payee.id,
            'amount': '75000.00',
            'status': 'issued',
            'is_post_dated': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cheque.objects.count(), 2)
        self.assertEqual(response.data['cheque_number'], 'CHQ-002')
        self.assertEqual(Decimal(response.data['amount']), Decimal('75000.00'))

    def test_retrieve_cheque(self):
        """Test GET /api/accounting/cheques/{id}/ - Get cheque details"""
        url = reverse('cheque-detail', kwargs={'pk': self.cheque.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['cheque_number'], 'CHQ-001')
        self.assertEqual(response.data['bank_account_name'], 'Bank Account - HBL')
        self.assertEqual(response.data['payee_name'], 'ABC Suppliers')

    def test_update_cheque(self):
        """Test PUT /api/accounting/cheques/{id}/ - Update cheque"""
        url = reverse('cheque-detail', kwargs={'pk': self.cheque.id})
        
        data = {
            'cheque_number': 'CHQ-001',
            'cheque_date': '2025-01-15',
            'bank_account': self.bank_account.id,
            'payee': self.payee.id,
            'amount': '60000.00',  # Updated amount
            'status': 'issued',
            'is_post_dated': False
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cheque.refresh_from_db()
        self.assertEqual(self.cheque.amount, Decimal('60000.00'))

    def test_delete_cheque(self):
        """Test DELETE /api/accounting/cheques/{id}/ - Delete cheque"""
        url = reverse('cheque-detail', kwargs={'pk': self.cheque.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cheque.objects.count(), 0)

    # ========================================================================
    # CUSTOM ACTIONS TESTS (4 tests)
    # ========================================================================

    def test_clear_cheque_action(self):
        """Test POST /api/accounting/cheques/{id}/clear/ - Clear a cheque"""
        url = reverse('cheque-clear', kwargs={'pk': self.cheque.id})
        
        data = {
            'clearance_date': '2025-01-20'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cheque.refresh_from_db()
        self.assertEqual(self.cheque.status, 'cleared')
        self.assertEqual(self.cheque.clearance_date, datetime.date(2025, 1, 20))

    def test_cancel_cheque_action(self):
        """Test POST /api/accounting/cheques/{id}/cancel/ - Cancel a cheque"""
        url = reverse('cheque-cancel', kwargs={'pk': self.cheque.id})
        
        data = {
            'cancelled_date': '2025-01-18',
            'cancellation_reason': 'Payment terms changed'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cheque.refresh_from_db()
        self.assertEqual(self.cheque.status, 'cancelled')
        self.assertEqual(self.cheque.cancelled_date, datetime.date(2025, 1, 18))
        self.assertEqual(self.cheque.cancellation_reason, 'Payment terms changed')

    def test_print_cheque_action(self):
        """Test GET /api/accounting/cheques/{id}/print/ - Print cheque as PDF"""
        url = reverse('cheque-print', kwargs={'pk': self.cheque.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('cheque_CHQ-001.pdf', response['Content-Disposition'])

    def test_post_dated_cheques_action(self):
        """Test GET /api/accounting/cheques/post-dated/ - Get post-dated cheques"""
        # Create a post-dated cheque
        post_dated_cheque = Cheque.objects.create(
            cheque_number='CHQ-PD-001',
            cheque_date=datetime.date(2025, 2, 15),  # Future date
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('100000.00'),
            status='issued',
            is_post_dated=True,
            created_by=self.user
        )
        
        url = reverse('cheque-post-dated')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        # Verify only post-dated cheques are returned
        for cheque in response.data:
            self.assertTrue(cheque.get('is_post_dated', False))

    # ========================================================================
    # FILTERING TESTS (2 tests)
    # ========================================================================

    def test_filter_by_status(self):
        """Test filtering cheques by status"""
        # Create cheques with different statuses
        cleared_cheque = Cheque.objects.create(
            cheque_number='CHQ-CLR-001',
            cheque_date=datetime.date(2025, 1, 10),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('25000.00'),
            status='cleared',
            clearance_date=datetime.date(2025, 1, 15),
            created_by=self.user
        )
        
        url = reverse('cheque-list')
        response = self.client.get(url, {'status': 'cleared'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        # Verify all returned cheques have 'cleared' status
        for cheque in response.data:
            self.assertEqual(cheque['status'], 'cleared')

    def test_filter_by_post_dated(self):
        """Test filtering post-dated cheques"""
        # Create a post-dated cheque
        Cheque.objects.create(
            cheque_number='CHQ-PD-002',
            cheque_date=datetime.date(2025, 3, 1),
            bank_account=self.bank_account,
            payee=self.payee,
            amount=Decimal('80000.00'),
            status='issued',
            is_post_dated=True,
            created_by=self.user
        )
        
        url = reverse('cheque-list')
        response = self.client.get(url, {'is_post_dated': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify all returned cheques are post-dated
        for cheque in response.data:
            self.assertTrue(cheque.get('is_post_dated', False))

    # ========================================================================
    # VALIDATION TESTS (4 tests)
    # ========================================================================

    def test_clear_already_cleared_cheque_fails(self):
        """Test that clearing an already cleared cheque fails"""
        # First clear the cheque
        self.cheque.status = 'cleared'
        self.cheque.clearance_date = datetime.date(2025, 1, 20)
        self.cheque.save()
        
        url = reverse('cheque-clear', kwargs={'pk': self.cheque.id})
        data = {'clearance_date': '2025-01-25'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_cancel_already_cancelled_cheque_fails(self):
        """Test that cancelling an already cancelled cheque fails"""
        # First cancel the cheque
        self.cheque.status = 'cancelled'
        self.cheque.cancelled_date = datetime.date(2025, 1, 18)
        self.cheque.cancellation_reason = 'Original reason'
        self.cheque.save()
        
        url = reverse('cheque-cancel', kwargs={'pk': self.cheque.id})
        data = {
            'cancelled_date': '2025-01-19',
            'cancellation_reason': 'New reason'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_cheque_without_required_fields_fails(self):
        """Test that creating cheque without required fields fails"""
        url = reverse('cheque-list')
        
        data = {
            'cheque_number': 'CHQ-INVALID',
            # Missing required fields: cheque_date, bank_account, payee, amount
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clear_cheque_without_clearance_date_fails(self):
        """Test that clearing cheque without clearance date fails"""
        url = reverse('cheque-clear', kwargs={'pk': self.cheque.id})
        
        data = {}  # No clearance_date provided
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('clearance_date', response.data['error'].lower())


# ============================================================================
# ADDITIONAL TEST COVERAGE
# ============================================================================

class ChequeSerializerTestCase(APITestCase):
    """Test Cheque serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.currency = CurrencyV2.objects.create(
            currency_code='PKR',
            currency_name='Pakistani Rupee',
            symbol='₨'
        )
        
        self.bank_account = AccountV2.objects.create(
            code='1010',
            name='Bank Account',
            account_type='asset',
            account_group='current_asset',
            created_by=self.user
        )
        
        self.payee = BusinessPartner.objects.create(
            name='Test Supplier',
            partner_type='supplier'
        )

    def test_cheque_serializer_fields(self):
        """Test ChequeSerializer includes all required fields"""
        from accounting.serializers import ChequeSerializer
        
        data = {
            'cheque_number': 'CHQ-SER-001',
            'cheque_date': '2025-01-15',
            'bank_account': self.bank_account.id,
            'payee': self.payee.id,
            'amount': '50000.00',
            'status': 'issued',
            'is_post_dated': False
        }
        
        serializer = ChequeSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        # Verify required fields are present
        self.assertIn('cheque_number', serializer.validated_data)
        self.assertIn('amount', serializer.validated_data)
        self.assertIn('bank_account', serializer.validated_data)
