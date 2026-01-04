from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date
from .models import Invoice, VoucherV2, ReferenceDefinition, Entity, AccountV2, CurrencyV2
from partners.models import BusinessPartner

User = get_user_model()

class ReferenceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('testuser', 'test@example.com', 'password')
        
        self.currency = CurrencyV2.objects.create(currency_code="USD", currency_name="US Dollar", symbol="$", is_active=True)
        self.entity = Entity.objects.create(
            entity_name="Test Entity", 
            entity_code="ENT-1", 
            country="US", 
            functional_currency=self.currency
        )
        self.partner = BusinessPartner.objects.create(name="Test Partner", email="p@p.com")
        self.account = AccountV2.objects.create(code="1001", name="Cash", account_type="asset")

        self.po_def = ReferenceDefinition.objects.create(
            model_name='voucher',
            field_key='po_number',
            field_label='PO Number',
            data_type='text',
            is_required=True,
            is_unique=True
        )
        self.date_def = ReferenceDefinition.objects.create(
            model_name='voucher',
            field_key='project_date',
            field_label='Project Date',
            data_type='date'
        )

    def test_jsonb_storage_and_retrieval(self):
        """Test that user_references are correctly stored and retrieved"""
        refs = {'po_number': 'PO-100', 'project_date': '2023-01-01'}
        voucher = VoucherV2.objects.create(
            voucher_number='V-001',
            voucher_date=date.today(),
            voucher_type='JE',
            status='draft',
            created_by=self.user,
            user_references=refs,
            total_amount=Decimal('100.00'),
            exchange_rate=Decimal('1.00')
        )
        voucher.refresh_from_db()
        self.assertEqual(voucher.user_references['po_number'], 'PO-100')
        self.assertEqual(voucher.user_references['project_date'], '2023-01-01')

    def test_validation_required(self):
        """Test required field validation"""
        refs = {'project_date': '2023-01-01'} 
        voucher = VoucherV2(
            voucher_number='V-002',
            voucher_date=date.today(),
            voucher_type='JE',
            status='draft',
            created_by=self.user,
            user_references=refs,
            total_amount=Decimal('100.00'),
            exchange_rate=Decimal('1.00')
        )
        with self.assertRaises(Exception) as context:
            voucher.clean() 
        
        msg = str(context.exception)
        self.assertTrue('required' in msg.lower() or 'field' in msg.lower())

    def test_validation_unique(self):
        """Test uniqueness validation"""
        VoucherV2.objects.create(
            voucher_number='V-U1',
            voucher_date=date.today(),
            voucher_type='JE',
            created_by=self.user,
            user_references={'po_number': 'UNIQUE-123'},
            total_amount=Decimal('100.00'),
            exchange_rate=Decimal('1.00')
        )
        
        voucher2 = VoucherV2(
            voucher_number='V-U2',
            voucher_date=date.today(),
            voucher_type='JE',
            created_by=self.user,
            user_references={'po_number': 'UNIQUE-123'},
            total_amount=Decimal('100.00'),
            exchange_rate=Decimal('1.00')
        )
        with self.assertRaises(Exception) as context:
            voucher2.clean()
        self.assertTrue('must be unique' in str(context.exception))

class ReferenceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser('apiuser', 'test@test.com', 'password')
        self.client.force_authenticate(user=self.user)
        self.currency = CurrencyV2.objects.create(currency_code="USD", currency_name="US Dollar", symbol="$", is_active=True)
        
        self.ref_def = ReferenceDefinition.objects.create(
            model_name='voucher',
            field_key='contract_id',
            field_label='Contract ID',
            data_type='text'
        )
        
        VoucherV2.objects.create(voucher_number='V-A1', voucher_date=date.today(), voucher_type='JE', created_by=self.user, user_references={'contract_id': 'CTR-100'}, total_amount=Decimal('100.00'), exchange_rate=Decimal('1.00'))
        VoucherV2.objects.create(voucher_number='V-A2', voucher_date=date.today(), voucher_type='JE', created_by=self.user, user_references={'contract_id': 'CTR-200'}, total_amount=Decimal('100.00'), exchange_rate=Decimal('1.00'))
        VoucherV2.objects.create(voucher_number='V-A3', voucher_date=date.today(), voucher_type='JE', created_by=self.user, user_references={'contract_id': 'CTR-100'}, total_amount=Decimal('100.00'), exchange_rate=Decimal('1.00'))

    def test_search_filter(self):
        url = reverse('voucherv2-list')
        response = self.client.get(url, {'ref_contract_id': 'CTR-200'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        if isinstance(data, dict):
            results = data.get('results', data)
        else:
            results = data
            
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['voucher_number'], 'V-A2')

    def test_export_action(self):
        url = reverse('voucherv2-export')
        
        # Test Excel export (using export_format)
        response = self.client.get(url, {'export_format': 'xlsx'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('spreadsheet', response['Content-Type'])

        # Test PDF export
        response_pdf = self.client.get(url, {'export_format': 'pdf'})
        self.assertEqual(response_pdf.status_code, status.HTTP_200_OK)
        self.assertEqual(response_pdf['Content-Type'], 'application/pdf')
