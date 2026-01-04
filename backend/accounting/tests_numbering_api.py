"""
API Tests for Auto-Numbering System

Tests cover:
- CRUD operations on numbering schemes
- Number generation API
- Preview API
- Reset counter API
- Scheme info API
- Permissions and error handling

Target: 100% pass rate
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date

from accounting.models import NumberingScheme, Entity, CurrencyV2

User = get_user_model()


class NumberingSchemeAPITestCase(TestCase):
    """Test NumberingScheme API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        # Create currency
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        
        # Create entity
        self.entity = Entity.objects.create(
            entity_code='TEST',
            entity_name='Test Entity',
            country='USA',
            functional_currency=self.usd,
            created_by=self.user
        )
        
        # Create numbering scheme
        self.scheme = NumberingScheme.objects.create(
            scheme_name='Invoice Numbering',
            document_type='invoice',
            prefix='INV',
            date_format='YYYY',
            separator='-',
            padding=4,
            reset_frequency='yearly',
            created_by=self.user
        )
    
    def test_list_numbering_schemes(self):
        """Test GET /api/accounting/numbering-schemes/"""
        response = self.client.get('/api/accounting/numbering-schemes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # API returns list response (not paginated)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['scheme_name'], 'Invoice Numbering')
    
    def test_create_numbering_scheme(self):
        """Test POST /api/accounting/numbering-schemes/"""
        data = {
            'scheme_name': 'Voucher Numbering',
            'document_type': 'voucher',
            'prefix': 'VCH',
            'date_format': 'YYYYMM',
            'separator': '/',
            'padding': 5,
            'reset_frequency': 'monthly'
        }
        
        response = self.client.post('/api/accounting/numbering-schemes/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['scheme_name'], 'Voucher Numbering')
        self.assertEqual(response.data['document_type'], 'voucher')
        self.assertIsNotNone(response.data['preview_number'])
    
    def test_retrieve_numbering_scheme(self):
        """Test GET /api/accounting/numbering-schemes/{id}/"""
        response = self.client.get(f'/api/accounting/numbering-schemes/{self.scheme.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['scheme_name'], 'Invoice Numbering')
        self.assertIn('preview_number', response.data)
    
    def test_update_numbering_scheme(self):
        """Test PUT /api/accounting/numbering-schemes/{id}/"""
        data = {
            'scheme_name': 'Updated Invoice Numbering',
            'document_type': 'invoice',
            'prefix': 'INV',
            'padding': 5,
            'reset_frequency': 'monthly'
        }
        
        response = self.client.put(f'/api/accounting/numbering-schemes/{self.scheme.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['scheme_name'], 'Updated Invoice Numbering')
        self.assertEqual(response.data['padding'], 5)
    
    def test_delete_numbering_scheme(self):
        """Test DELETE /api/accounting/numbering-schemes/{id}/"""
        response = self.client.delete(f'/api/accounting/numbering-schemes/{self.scheme.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(NumberingScheme.objects.filter(id=self.scheme.id).exists())
    
    def test_generate_number_api(self):
        """Test POST /api/accounting/numbering-schemes/generate/"""
        data = {
            'document_type': 'invoice'
        }
        
        response = self.client.post('/api/accounting/numbering-schemes/generate/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('number', response.data)
        self.assertIn('document_type', response.data)
        current_year = date.today().year
        self.assertTrue(response.data['number'].startswith(f'INV-{current_year}'))
    
    def test_generate_number_with_entity(self):
        """Test number generation with entity"""
        # Create entity-specific scheme
        entity_scheme = NumberingScheme.objects.create(
            scheme_name='Entity Invoice',
            document_type='voucher',
            prefix='EVCH',
            entity=self.entity,
            padding=3,
            created_by=self.user
        )
        
        data = {
            'document_type': 'voucher',
            'entity_id': self.entity.id
        }
        
        response = self.client.post('/api/accounting/numbering-schemes/generate/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['number'].startswith('EVCH-'))
    
    def test_generate_number_no_scheme(self):
        """Test error when no scheme exists"""
        data = {
            'document_type': 'payment'
        }
        
        response = self.client.post('/api/accounting/numbering-schemes/generate/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_preview_number_api(self):
        """Test POST /api/accounting/numbering-schemes/preview/"""
        data = {
            'document_type': 'invoice'
        }
        
        response = self.client.post('/api/accounting/numbering-schemes/preview/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('preview', response.data)
        current_year = date.today().year
        self.assertTrue(response.data['preview'].startswith(f'INV-{current_year}'))
    
    def test_preview_number_no_scheme(self):
        """Test preview returns 404 when no scheme exists"""
        data = {
            'document_type': 'payment'
        }
        
        response = self.client.post('/api/accounting/numbering-schemes/preview/', data)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_reset_counter_api(self):
        """Test POST /api/accounting/numbering-schemes/{id}/reset/"""
        # Generate some numbers first
        self.client.post('/api/accounting/numbering-schemes/generate/', {'document_type': 'invoice'})
        self.client.post('/api/accounting/numbering-schemes/generate/', {'document_type': 'invoice'})
        
        # Reset counter
        data = {'reset_to': 1}
        response = self.client.post(f'/api/accounting/numbering-schemes/{self.scheme.id}/reset/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['next_number'], 1)
        self.assertIn('message', response.data)
    
    def test_scheme_info_api(self):
        """Test GET /api/accounting/numbering-schemes/info/"""
        response = self.client.get('/api/accounting/numbering-schemes/info/?document_type=invoice')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['scheme_name'], 'Invoice Numbering')
        self.assertEqual(response.data['document_type'], 'invoice')
        self.assertIn('format_preview', response.data)
    
    def test_scheme_info_no_document_type(self):
        """Test scheme info requires document_type parameter"""
        response = self.client.get('/api/accounting/numbering-schemes/info/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_filter_by_document_type(self):
        """Test filtering schemes by document type"""
        # Create another scheme
        NumberingScheme.objects.create(
            scheme_name='Payment Numbering',
            document_type='payment',
            prefix='PAY',
            padding=3,
            created_by=self.user
        )
        
        response = self.client.get('/api/accounting/numbering-schemes/?document_type=invoice')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # API returns list response (not paginated)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['document_type'], 'invoice')
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/accounting/numbering-schemes/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
