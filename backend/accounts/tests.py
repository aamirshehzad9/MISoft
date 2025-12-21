from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationTests(TestCase):
    """Test suite for authentication module"""

    def setUp(self):
        """Set up test client and test user"""
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'manager'
        }
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPass123!',
            role='admin'
        )

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post('/api/accounts/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], self.user_data['username'])
        self.assertEqual(response.data['user']['email'], self.user_data['email'])

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email fails"""
        duplicate_data = self.user_data.copy()
        duplicate_data['email'] = 'existing@example.com'
        duplicate_data['username'] = 'newuser'
        response = self.client.post('/api/accounts/register/', duplicate_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_required_fields(self):
        """Test registration with missing required fields fails"""
        incomplete_data = {'username': 'testuser'}
        response = self.client.post('/api/accounts/register/', incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """Test successful user login"""
        login_data = {
            'username': 'existinguser',
            'password': 'ExistingPass123!'
        }
        response = self.client.post('/api/accounts/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_user_login_incorrect_password(self):
        """Test login with incorrect password fails"""
        login_data = {
            'username': 'existinguser',
            'password': 'WrongPassword123!'
        }
        response = self.client.post('/api/accounts/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_nonexistent_user(self):
        """Test login with non-existent user fails"""
        login_data = {
            'username': 'nonexistent',
            'password': 'SomePassword123!'
        }
        response = self.client.post('/api/accounts/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_generation(self):
        """Test JWT token is generated on login"""
        login_data = {
            'username': 'existinguser',
            'password': 'ExistingPass123!'
        }
        response = self.client.post('/api/accounts/login/', login_data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(len(response.data['access']) > 0)
        self.assertTrue(len(response.data['refresh']) > 0)

    def test_jwt_token_refresh(self):
        """Test JWT token refresh"""
        # First login to get refresh token
        login_data = {
            'username': 'existinguser',
            'password': 'ExistingPass123!'
        }
        login_response = self.client.post('/api/accounts/login/', login_data)
        refresh_token = login_response.data['refresh']

        # Use refresh token to get new access token
        refresh_data = {'refresh': refresh_token}
        response = self.client.post('/api/accounts/token/refresh/', refresh_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token fails"""
        response = self.client.get('/api/accounts/user/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token succeeds"""
        # Login to get token
        login_data = {
            'username': 'existinguser',
            'password': 'ExistingPass123!'
        }
        login_response = self.client.post('/api/accounts/login/', login_data)
        access_token = login_response.data['access']

        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/accounts/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'existinguser')

    def test_user_logout(self):
        """Test user logout"""
        # Login first
        login_data = {
            'username': 'existinguser',
            'password': 'ExistingPass123!'
        }
        login_response = self.client.post('/api/accounts/login/', login_data)
        access_token = login_response.data['access']

        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.post('/api/accounts/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_role_assignment(self):
        """Test user role is correctly assigned"""
        response = self.client.post('/api/accounts/register/', self.user_data)
        self.assertEqual(response.data['user']['role'], 'manager')

    def test_user_model_string_representation(self):
        """Test user model __str__ method"""
        self.assertEqual(str(self.user), 'existinguser')

    def test_user_full_name_property(self):
        """Test user full name property"""
        user = User.objects.create_user(
            username='fullnametest',
            email='fullname@example.com',
            password='Pass123!',
            first_name='John',
            last_name='Doe'
        )
        expected_full_name = 'John Doe'
        self.assertEqual(user.get_full_name(), expected_full_name)
