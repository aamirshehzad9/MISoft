from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from accounting.models import RecurringTransaction
from django.contrib.auth import get_user_model
from datetime import date, timedelta

User = get_user_model()

class RecurringTransactionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.force_authenticate(user=self.user)
        
        self.rt_data = {
            'name': 'Monthly Rent',
            'document_type': 'bill',
            'frequency': 'monthly',
            'start_date': str(timezone.now().date()),
            'next_run_date': str(timezone.now().date()),
            'template_data': {
                'voucher_type': 'BP',
                'description': 'Rent',
                'amount': 5000
            },
            'is_active': True,
            'auto_post': False
        }
        self.rt = RecurringTransaction.objects.create(
            name='Existing Rent',
            document_type='bill',
            frequency='monthly',
            start_date=timezone.now().date(),
            next_run_date=timezone.now().date(),
            template_data={'voucher_type': 'BP'},
            is_active=True
        )
        self.list_url = reverse('recurringtransaction-list')
        self.detail_url = reverse('recurringtransaction-detail', args=[self.rt.id])

    def test_list_recurring_transactions(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should contain at least 1
        self.assertTrue(len(response.data['results']) >= 1)

    def test_create_recurring_transaction(self):
        response = self.client.post(self.list_url, self.rt_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RecurringTransaction.objects.count(), 2)
        self.assertEqual(response.data['name'], 'Monthly Rent')

    def test_update_recurring_transaction(self):
        update_data = {'name': 'Updated Rent', 'is_active': False}
        response = self.client.patch(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.rt.refresh_from_db()
        self.assertEqual(self.rt.name, 'Updated Rent')
        self.assertFalse(self.rt.is_active)

    def test_preview_generation(self):
        """Test the preview action"""
        url = reverse('recurringtransaction-preview', args=[self.rt.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('preview_voucher', response.data)
        self.assertIn('next_run_date', response.data)
        # Verify it didn't create a voucher
        # Note: Depending on backend implementation, it might not hit DB.
        # But we check response structure.
