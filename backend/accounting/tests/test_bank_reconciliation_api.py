"""
API Tests for Bank Reconciliation System
Task 2.1.2: Reconciliation Engine
Module 2.1: Bank Reconciliation System

Tests the API endpoints for Bank Statements and Reconciliation.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounting.models import AccountV2, BankStatement, CurrencyV2
from accounting.serializers import BankStatementSerializer # Will fail initially
import datetime
from decimal import Decimal

User = get_user_model()

class BankReconciliationAPITestCase(APITestCase):
    """Test suite for Bank Reconciliation APIs"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        self.currency = CurrencyV2.objects.create(
            currency_code='USD', currency_name='US Dollar', symbol='$'
        )
        
        self.bank_account = AccountV2.objects.create(
            name="Test Bank Account",
            code="1001",
            account_type="asset",
            account_group="current_asset",
            is_active=True
        )

    def test_create_bank_statement_api(self):
        """Test creating a bank statement via API"""
        url = reverse('bank-statements-list')
        
        data = {
            'bank_account': self.bank_account.id,
            'statement_date': '2025-01-31',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31',
            'opening_balance': '1000.00',
            'closing_balance': '2000.00',
            'status': 'DRAFT'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BankStatement.objects.count(), 1)
        self.assertEqual(response.data['status'], 'DRAFT')

    def test_auto_match_api(self):
        """Test auto-match endpoint"""
        # Create Statement
        statement = BankStatement.objects.create(
            bank_account=self.bank_account,
            statement_date=datetime.date(2025, 1, 31),
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 31),
            opening_balance=Decimal('1000.00'),
            closing_balance=Decimal('2000.00'),
            created_by=self.user
        )
        
        url = reverse('bank-statements-auto-match', kwargs={'pk': statement.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('matches_found', response.data)

    def test_serializer_fields(self):
        """Test Valid Serializer"""
        from accounting.serializers import BankStatementSerializer
        
        data = {
            'bank_account': self.bank_account.id,
            'statement_date': '2025-01-31',
            'start_date': '2025-01-01',
            'end_date': '2025-01-31',
            'opening_balance': '1000.00',
            'closing_balance': '2000.00',
            'status': 'DRAFT'
        }
        serializer = BankStatementSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
