from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import BusinessPartner

User = get_user_model()


class BusinessPartnerTests(TestCase):
    """Test suite for Business Partners module"""

    def setUp(self):
        """Set up test client, user, and test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role='admin'
        )
        self.client.force_authenticate(user=self.user)

        self.partner_data = {
            'name': 'Test Partner',
            'email': 'partner@example.com',
            'phone': '+1234567890',
            'address': '123 Test Street',
            'city': 'Test City',
            'state': 'TS',
            'country': 'Test Country',
            'postal_code': '12345',
            'is_customer': True,
            'is_vendor': False,
            'credit_limit': 10000.00,
            'payment_terms': 'Net 30',
            'tax_id': 'TAX123456'
        }

        self.partner = BusinessPartner.objects.create(
            name='Existing Partner',
            email='existing@example.com',
            phone='+0987654321',
            is_customer=True,
            is_vendor=True
        )

    def test_create_partner_success(self):
        """Test creating a partner with valid data"""
        response = self.client.post('/api/partners/', self.partner_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.partner_data['name'])
        self.assertEqual(response.data['email'], self.partner_data['email'])

    def test_create_partner_missing_required_fields(self):
        """Test creating partner with missing required fields fails"""
        incomplete_data = {'name': 'Incomplete Partner'}
        response = self.client.post('/api/partners/', incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_partner_list(self):
        """Test retrieving list of partners"""
        response = self.client.get('/api/partners/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_partner_detail(self):
        """Test retrieving a single partner"""
        response = self.client.get(f'/api/partners/{self.partner.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.partner.name)

    def test_update_partner(self):
        """Test updating partner information"""
        update_data = {'name': 'Updated Partner Name'}
        response = self.client.patch(f'/api/partners/{self.partner.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Partner Name')

    def test_delete_partner(self):
        """Test deleting a partner"""
        response = self.client.delete(f'/api/partners/{self.partner.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BusinessPartner.objects.filter(id=self.partner.id).exists())

    def test_filter_customers(self):
        """Test filtering partners by customer type"""
        response = self.client.get('/api/partners/customers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for partner in response.data:
            self.assertTrue(partner['is_customer'])

    def test_filter_vendors(self):
        """Test filtering partners by vendor type"""
        response = self.client.get('/api/partners/vendors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for partner in response.data:
            self.assertTrue(partner['is_vendor'])

    def test_search_partner_by_name(self):
        """Test searching partners by name"""
        response = self.client.get('/api/partners/', {'search': 'Existing'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_search_partner_by_email(self):
        """Test searching partners by email"""
        response = self.client.get('/api/partners/', {'search': 'existing@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_toggle_partner_active_status(self):
        """Test toggling partner active status"""
        response = self.client.post(f'/api/partners/{self.partner.id}/toggle_active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.partner.refresh_from_db()
        self.assertFalse(self.partner.is_active)

    def test_partner_type_display(self):
        """Test partner type display property"""
        customer_only = BusinessPartner.objects.create(
            name='Customer Only',
            email='customer@example.com',
            is_customer=True,
            is_vendor=False
        )
        self.assertEqual(customer_only.partner_type_display, 'Customer')

        vendor_only = BusinessPartner.objects.create(
            name='Vendor Only',
            email='vendor@example.com',
            is_customer=False,
            is_vendor=True
        )
        self.assertEqual(vendor_only.partner_type_display, 'Vendor')

        both = BusinessPartner.objects.create(
            name='Both',
            email='both@example.com',
            is_customer=True,
            is_vendor=True
        )
        self.assertEqual(both.partner_type_display, 'Customer, Vendor')

    def test_partner_model_string_representation(self):
        """Test partner model __str__ method"""
        self.assertEqual(str(self.partner), 'Existing Partner')

    def test_partner_balance_calculation(self):
        """Test partner balance field"""
        partner = BusinessPartner.objects.create(
            name='Balance Test',
            email='balance@example.com',
            is_customer=True,
            balance=5000.00
        )
        self.assertEqual(partner.balance, 5000.00)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access partners"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/partners/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
