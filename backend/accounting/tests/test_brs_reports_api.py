"""
API Tests for BRS Report Endpoints
Task 2.1.3: BRS Report
Module 2.1: Bank Reconciliation System

Tests the API endpoints for BRS reports.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounting.models import AccountV2, BankReconciliation, VoucherV2, VoucherEntryV2, CurrencyV2
import datetime
from decimal import Decimal

User = get_user_model()


class BRSReportAPITestCase(APITestCase):
    """Test suite for BRS Report API Endpoints"""

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

    def test_brs_report_endpoint(self):
        """Test BRS Report API endpoint"""
        # Create reconciliation
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('10000.00'),
            ledger_balance=Decimal('10000.00'),
            difference=Decimal('0.00'),
            reconciled_by=self.user,
            status='COMPLETED'
        )

        url = reverse('bank-reconciliations-brs-report', kwargs={'pk': reconciliation.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reconciliation_id', response.data)
        self.assertIn('statement_balance', response.data)
        self.assertIn('ledger_balance', response.data)
        self.assertIn('outstanding_payments', response.data)
        self.assertIn('deposits_in_transit', response.data)
        self.assertIn('adjusted_bank_balance', response.data)
        self.assertIn('difference', response.data)
        self.assertIn('is_balanced', response.data)
        self.assertIn('outstanding_cheques_detail', response.data)
        self.assertIn('deposits_in_transit_detail', response.data)

    def test_outstanding_cheques_endpoint(self):
        """Test Outstanding Cheques Report API endpoint"""
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('9500.00'),
            ledger_balance=Decimal('9000.00'),
            difference=Decimal('500.00'),
            reconciled_by=self.user
        )

        # Create outstanding payment
        voucher = VoucherV2.objects.create(
            voucher_number="CHK-001",
            voucher_type="BPV",
            voucher_date=datetime.date(2025, 1, 15),
            total_amount=Decimal('500.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user
        )
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.bank_account,
            debit_amount=Decimal('0.00'),
            credit_amount=Decimal('500.00')
        )

        url = reverse('bank-reconciliations-outstanding-cheques', kwargs={'pk': reconciliation.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('outstanding_cheques', response.data)
        self.assertIn('total_outstanding', response.data)
        self.assertEqual(response.data['total_outstanding'], Decimal('500.00'))
        self.assertEqual(len(response.data['outstanding_cheques']), 1)

    def test_deposits_in_transit_endpoint(self):
        """Test Deposits in Transit Report API endpoint"""
        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('8000.00'),
            ledger_balance=Decimal('9000.00'),
            difference=Decimal('-1000.00'),
            reconciled_by=self.user
        )

        # Create deposit in transit
        voucher = VoucherV2.objects.create(
            voucher_number="DEP-001",
            voucher_type="BRV",
            voucher_date=datetime.date(2025, 1, 30),
            total_amount=Decimal('1000.00'),
            currency=self.currency,
            status='posted',
            created_by=self.user
        )
        VoucherEntryV2.objects.create(
            voucher=voucher,
            account=self.bank_account,
            debit_amount=Decimal('1000.00'),
            credit_amount=Decimal('0.00')
        )

        url = reverse('bank-reconciliations-deposits-in-transit', kwargs={'pk': reconciliation.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deposits_in_transit', response.data)
        self.assertIn('total_deposits', response.data)
        self.assertEqual(response.data['total_deposits'], Decimal('1000.00'))
        self.assertEqual(len(response.data['deposits_in_transit']), 1)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access reports"""
        self.client.force_authenticate(user=None)

        reconciliation = BankReconciliation.objects.create(
            bank_account=self.bank_account,
            reconciliation_date=datetime.date(2025, 1, 31),
            statement_balance=Decimal('10000.00'),
            ledger_balance=Decimal('10000.00'),
            difference=Decimal('0.00'),
            reconciled_by=self.user
        )

        url = reverse('bank-reconciliations-brs-report', kwargs={'pk': reconciliation.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
