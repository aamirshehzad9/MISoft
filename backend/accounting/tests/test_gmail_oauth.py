from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from accounting.models import UserGmailToken, EmailCommunicationLog

User = get_user_model()

class GmailOAuthTestCase(TestCase):
    """Test Suite for Gmail OAuth Integration (Task 1.3.6)"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.client.force_authenticate(user=self.user)

    def test_authorization_url_generation(self):
        """Test generating Google OAuth authorization URL"""
        response = self.client.get('/api/accounting/auth/google/login/')
        if response.status_code != 200:
            print(f"Auth URL Error: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('authorization_url', response.data)
        self.assertTrue(response.data['authorization_url'].startswith('https://accounts.google.com'))

    @patch('accounting.services.gmail_service.GmailAuthService.exchange_code')
    def test_oauth_callback_success(self, mock_exchange):
        """Test successful token exchange callback"""
        mock_token = MagicMock()
        mock_token.email = 'test@example.com'
        mock_exchange.return_value = mock_token
        
        response = self.client.get('/api/accounting/auth/google/callback/?code=fake_code&state=fake_state')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify successful response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify Service was called
        mock_exchange.assert_called_once()

    def test_email_log_creation(self):
        """Test that sending email creates an audit log"""
        # This requires Service implementation to test fully, mock for now or test model directly
        log = EmailCommunicationLog.objects.create(
            message_id='<123@google.com>',
            subject='Invoice #123',
            sender='test@example.com',
            recipient='client@example.com',
            metadata_json={'voucher_id': 1}
        )
        self.assertEqual(log.subject, 'Invoice #123')
