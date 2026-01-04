"""
API Tests for Bank Transfer System
Task 1.2: Create Bank Transfer API Tests
Module 2.3: Bank Transfer System

Tests all API endpoints for Bank Transfer CRUD operations and custom actions.
Follows TDD principles and IFRS/IAS 7 & IAS 21 compliance.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounting.models import AccountV2, BankTransfer, VoucherV2, CurrencyV2, ExchangeRateV2
from decimal import Decimal
import datetime

User = get_user_model()


class BankTransferAPITestCase(APITestCase):
    """
    Comprehensive test suite for Bank Transfer API endpoints
    
    Tests:
    - CRUD operations (5 tests)
    - Custom actions (4 tests)
    - Multi-currency (2 tests)
    - Filtering (2 tests)
    - Validation (3 tests)
    
    Total: 16 tests
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
        
        # Create currencies
        self.pkr = CurrencyV2.objects.create(
            currency_code='PKR',
            currency_name='Pakistani Rupee',
            symbol='₨',
            is_base_currency=True
        )
        
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$',
            is_base_currency=False
        )
        
        # Create exchange rate
        self.exchange_rate = ExchangeRateV2.objects.create(
            from_currency=self.pkr,
            to_currency=self.usd,
            rate_date=datetime.date(2025, 1, 15),
            exchange_rate=Decimal('0.0036')  # 1 PKR = 0.0036 USD
        )
        
        # Create bank accounts
        self.from_bank = AccountV2.objects.create(
            code='1010',
            name='Bank Account - HBL',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 7',
            ifrs_category='financial_assets',
            measurement_basis='fair_value',
            is_active=True,
            current_balance=Decimal('1000000.00'),
            created_by=self.user
        )
        
        self.to_bank = AccountV2.objects.create(
            code='1020',
            name='Bank Account - MCB',
            account_type='asset',
            account_group='current_asset',
            ias_reference_code='IAS 7',
            ifrs_category='financial_assets',
            measurement_basis='fair_value',
            is_active=True,
            current_balance=Decimal('500000.00'),
            created_by=self.user
        )
        
        # Create FX gain/loss account for multi-currency tests
        self.fx_account = AccountV2.objects.create(
            code='7200',
            name='FX Gain/Loss',
            account_type='revenue',
            account_group='other_income',
            ias_reference_code='IAS 21',
            ifrs_category='revenue',
            measurement_basis='fair_value',
            is_active=True,
            created_by=self.user
        )
        
        # Create a test transfer
        self.transfer = BankTransfer.objects.create(
            transfer_number='TRF-001',
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.from_bank,
            to_bank=self.to_bank,
            amount=Decimal('100000.00'),
            from_currency=self.pkr,
            to_currency=self.pkr,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='pending',
            description='Test transfer',
            created_by=self.user
        )

    # ========================================================================
    # CRUD OPERATIONS TESTS (5 tests)
    # ========================================================================

    def test_list_transfers(self):
        """Test GET /api/accounting/bank-transfers/ - List all transfers"""
        url = reverse('bank-transfer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['transfer_number'], 'TRF-001')

    def test_create_transfer(self):
        """Test POST /api/accounting/bank-transfers/ - Create new transfer"""
        url = reverse('bank-transfer-list')
        
        data = {
            'transfer_number': 'TRF-002',
            'transfer_date': '2025-01-20',
            'from_bank': self.from_bank.id,
            'to_bank': self.to_bank.id,
            'amount': '150000.00',
            'from_currency': self.pkr.id,
            'to_currency': self.pkr.id,
            'exchange_rate': '1.0000',
            'status': 'pending',
            'approval_status': 'pending',
            'description': 'New test transfer'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BankTransfer.objects.count(), 2)
        self.assertEqual(response.data['transfer_number'], 'TRF-002')
        self.assertEqual(Decimal(response.data['amount']), Decimal('150000.00'))

    def test_retrieve_transfer(self):
        """Test GET /api/accounting/bank-transfers/{id}/ - Get transfer details"""
        url = reverse('bank-transfer-detail', kwargs={'pk': self.transfer.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['transfer_number'], 'TRF-001')
        self.assertEqual(response.data['from_bank_name'], 'Bank Account - HBL')
        self.assertEqual(response.data['to_bank_name'], 'Bank Account - MCB')
        self.assertEqual(Decimal(response.data['converted_amount']), Decimal('100000.00'))

    def test_update_transfer(self):
        """Test PUT /api/accounting/bank-transfers/{id}/ - Update transfer"""
        url = reverse('bank-transfer-detail', kwargs={'pk': self.transfer.id})
        
        data = {
            'transfer_number': 'TRF-001',
            'transfer_date': '2025-01-15',
            'from_bank': self.from_bank.id,
            'to_bank': self.to_bank.id,
            'amount': '120000.00',  # Updated amount
            'from_currency': self.pkr.id,
            'to_currency': self.pkr.id,
            'exchange_rate': '1.0000',
            'status': 'pending',
            'approval_status': 'pending',
            'description': 'Updated description'
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transfer.refresh_from_db()
        self.assertEqual(self.transfer.amount, Decimal('120000.00'))
        self.assertEqual(self.transfer.description, 'Updated description')

    def test_delete_transfer(self):
        """Test DELETE /api/accounting/bank-transfers/{id}/ - Delete transfer"""
        url = reverse('bank-transfer-detail', kwargs={'pk': self.transfer.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(BankTransfer.objects.count(), 0)

    # ========================================================================
    # CUSTOM ACTIONS TESTS (4 tests)
    # ========================================================================

    def test_approve_transfer_action(self):
        """Test POST /api/accounting/bank-transfers/{id}/approve/ - Approve transfer"""
        url = reverse('bank-transfer-approve', kwargs={'pk': self.transfer.id})
        
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transfer.refresh_from_db()
        self.assertEqual(self.transfer.approval_status, 'approved')

    def test_reject_transfer_action(self):
        """Test POST /api/accounting/bank-transfers/{id}/reject/ - Reject transfer"""
        url = reverse('bank-transfer-reject', kwargs={'pk': self.transfer.id})
        
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transfer.refresh_from_db()
        self.assertEqual(self.transfer.approval_status, 'rejected')

    def test_execute_transfer_action(self):
        """Test POST /api/accounting/bank-transfers/{id}/execute/ - Execute transfer"""
        # First approve the transfer
        self.transfer.approval_status = 'approved'
        self.transfer.save()
        
        url = reverse('bank-transfer-execute', kwargs={'pk': self.transfer.id})
        
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transfer.refresh_from_db()
        self.assertEqual(self.transfer.status, 'completed')
        # Verify voucher was created
        self.assertIsNotNone(self.transfer.voucher)

    def test_pending_transfers_action(self):
        """Test GET /api/accounting/bank-transfers/pending/ - Get pending transfers"""
        # Create additional transfers with different statuses
        BankTransfer.objects.create(
            transfer_number='TRF-COMP-001',
            transfer_date=datetime.date(2025, 1, 10),
            from_bank=self.from_bank,
            to_bank=self.to_bank,
            amount=Decimal('50000.00'),
            from_currency=self.pkr,
            to_currency=self.pkr,
            exchange_rate=Decimal('1.0000'),
            status='completed',
            approval_status='approved',
            created_by=self.user
        )
        
        url = reverse('bank-transfer-pending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        # Verify only pending transfers are returned
        for transfer in response.data:
            self.assertEqual(transfer['status'], 'pending')

    # ========================================================================
    # MULTI-CURRENCY TESTS (2 tests)
    # ========================================================================

    def test_create_multi_currency_transfer(self):
        """Test creating a multi-currency transfer with exchange rate"""
        url = reverse('bank-transfer-list')
        
        data = {
            'transfer_number': 'TRF-MC-001',
            'transfer_date': '2025-01-15',
            'from_bank': self.from_bank.id,
            'to_bank': self.to_bank.id,
            'amount': '100000.00',  # PKR
            'from_currency': self.pkr.id,
            'to_currency': self.usd.id,
            'exchange_rate': '0.0036',  # 1 PKR = 0.0036 USD
            'status': 'pending',
            'approval_status': 'pending',
            'description': 'Multi-currency transfer'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['from_currency_code'], 'PKR')
        self.assertEqual(response.data['to_currency_code'], 'USD')
        # Verify converted amount calculation
        expected_converted = Decimal('100000.00') * Decimal('0.0036')
        self.assertEqual(Decimal(response.data['converted_amount']), expected_converted)

    def test_execute_multi_currency_transfer_with_fx_account(self):
        """Test executing multi-currency transfer with FX account"""
        # Create multi-currency transfer
        mc_transfer = BankTransfer.objects.create(
            transfer_number='TRF-MC-002',
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.from_bank,
            to_bank=self.to_bank,
            amount=Decimal('100000.00'),
            from_currency=self.pkr,
            to_currency=self.usd,
            exchange_rate=Decimal('0.0036'),
            status='pending',
            approval_status='approved',  # Pre-approved
            created_by=self.user
        )
        
        url = reverse('bank-transfer-execute', kwargs={'pk': mc_transfer.id})
        
        data = {
            'fx_account_id': self.fx_account.id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mc_transfer.refresh_from_db()
        self.assertEqual(mc_transfer.status, 'completed')
        # Verify voucher created with FX entries
        self.assertIsNotNone(mc_transfer.voucher)

    # ========================================================================
    # FILTERING TESTS (2 tests)
    # ========================================================================

    def test_filter_by_status(self):
        """Test filtering transfers by status"""
        # Create transfers with different statuses
        BankTransfer.objects.create(
            transfer_number='TRF-COMP-002',
            transfer_date=datetime.date(2025, 1, 12),
            from_bank=self.from_bank,
            to_bank=self.to_bank,
            amount=Decimal('75000.00'),
            from_currency=self.pkr,
            to_currency=self.pkr,
            exchange_rate=Decimal('1.0000'),
            status='completed',
            approval_status='approved',
            created_by=self.user
        )
        
        url = reverse('bank-transfer-list')
        response = self.client.get(url, {'status': 'completed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        # Verify all returned transfers have 'completed' status
        for transfer in response.data:
            self.assertEqual(transfer['status'], 'completed')

    def test_filter_by_approval_status(self):
        """Test filtering transfers by approval status"""
        # Create transfer with approved status
        BankTransfer.objects.create(
            transfer_number='TRF-APP-001',
            transfer_date=datetime.date(2025, 1, 14),
            from_bank=self.from_bank,
            to_bank=self.to_bank,
            amount=Decimal('60000.00'),
            from_currency=self.pkr,
            to_currency=self.pkr,
            exchange_rate=Decimal('1.0000'),
            status='pending',
            approval_status='approved',
            created_by=self.user
        )
        
        url = reverse('bank-transfer-list')
        response = self.client.get(url, {'approval_status': 'approved'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        # Verify all returned transfers have 'approved' approval status
        for transfer in response.data:
            self.assertEqual(transfer['approval_status'], 'approved')

    # ========================================================================
    # VALIDATION TESTS (3 tests)
    # ========================================================================

    def test_approve_already_approved_transfer_fails(self):
        """Test that approving an already approved transfer fails"""
        # First approve the transfer
        self.transfer.approval_status = 'approved'
        self.transfer.save()
        
        url = reverse('bank-transfer-approve', kwargs={'pk': self.transfer.id})
        
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_execute_pending_transfer_fails(self):
        """Test that executing a pending (not approved) transfer fails"""
        # Transfer is pending approval
        self.assertEqual(self.transfer.approval_status, 'pending')
        
        url = reverse('bank-transfer-execute', kwargs={'pk': self.transfer.id})
        
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_transfer_without_required_fields_fails(self):
        """Test that creating transfer without required fields fails"""
        url = reverse('bank-transfer-list')
        
        data = {
            'transfer_number': 'TRF-INVALID',
            # Missing required fields: transfer_date, from_bank, to_bank, amount, currencies
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ============================================================================
# ADDITIONAL TEST COVERAGE
# ============================================================================

class BankTransferSerializerTestCase(APITestCase):
    """Test Bank Transfer serializers"""
    
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
        
        self.from_bank = AccountV2.objects.create(
            code='1010',
            name='From Bank',
            account_type='asset',
            account_group='current_asset',
            created_by=self.user
        )
        
        self.to_bank = AccountV2.objects.create(
            code='1020',
            name='To Bank',
            account_type='asset',
            account_group='current_asset',
            created_by=self.user
        )

    def test_bank_transfer_serializer_fields(self):
        """Test BankTransferSerializer includes all required fields"""
        from accounting.serializers import BankTransferSerializer
        
        data = {
            'transfer_number': 'TRF-SER-001',
            'transfer_date': '2025-01-15',
            'from_bank': self.from_bank.id,
            'to_bank': self.to_bank.id,
            'amount': '100000.00',
            'from_currency': self.currency.id,
            'to_currency': self.currency.id,
            'exchange_rate': '1.0000',
            'status': 'pending',
            'approval_status': 'pending'
        }
        
        serializer = BankTransferSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        # Verify required fields are present
        self.assertIn('transfer_number', serializer.validated_data)
        self.assertIn('amount', serializer.validated_data)
        self.assertIn('from_bank', serializer.validated_data)
        self.assertIn('to_bank', serializer.validated_data)

    def test_converted_amount_calculation(self):
        """Test that converted_amount is calculated correctly"""
        transfer = BankTransfer.objects.create(
            transfer_number='TRF-CALC-001',
            transfer_date=datetime.date(2025, 1, 15),
            from_bank=self.from_bank,
            to_bank=self.to_bank,
            amount=Decimal('100000.00'),
            from_currency=self.currency,
            to_currency=self.currency,
            exchange_rate=Decimal('1.5000'),
            status='pending',
            approval_status='pending',
            created_by=self.user
        )
        
        expected_converted = Decimal('100000.00') * Decimal('1.5000')
        self.assertEqual(transfer.converted_amount, expected_converted)
