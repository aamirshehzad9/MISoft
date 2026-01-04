"""
API Tests for Audit Log Viewer
Task 1.7.3: Audit Viewer UI
Module 1.7: Audit Trail System (IASB Requirement)

Tests the audit log API endpoints for viewing and filtering
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from accounting.models import AuditLog, AccountV2

User = get_user_model()


class AuditLogAPITestCase(TestCase):
    """Test suite for Audit Log API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123',
            email='user1@example.com'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123',
            email='user2@example.com'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user1)
        
        # Create sample audit logs
        self.create_sample_audit_logs()
    
    def create_sample_audit_logs(self):
        """Create sample audit logs for testing"""
        # User 1 creates account
        self.audit1 = AuditLog.objects.create(
            model_name='AccountV2',
            object_id=1,
            action='CREATE',
            user=self.user1,
            ip_address='192.168.1.1',
            changes={'name': 'Cash', 'code': '1000'},
            reason='Initial setup'
        )
        
        # User 1 updates account
        self.audit2 = AuditLog.objects.create(
            model_name='AccountV2',
            object_id=1,
            action='UPDATE',
            user=self.user1,
            ip_address='192.168.1.1',
            changes={
                'before': {'balance': '1000.00'},
                'after': {'balance': '1500.00'}
            }
        )
        
        # User 2 creates product
        self.audit3 = AuditLog.objects.create(
            model_name='Product',
            object_id=10,
            action='CREATE',
            user=self.user2,
            ip_address='10.0.0.1',
            changes={'name': 'Product A', 'code': 'PROD-001'}
        )
        
        # User 2 deletes product
        self.audit4 = AuditLog.objects.create(
            model_name='Product',
            object_id=10,
            action='DELETE',
            user=self.user2,
            ip_address='10.0.0.1',
            changes={'deleted_object': {'name': 'Product A'}}
        )
    
    def test_list_audit_logs(self):
        """Test listing all audit logs"""
        response = self.client.get('/api/accounting/audit-logs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 4)
    
    def test_list_audit_logs_pagination(self):
        """Test pagination of audit logs"""
        response = self.client.get('/api/accounting/audit-logs/?page_size=2')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIn('next', response.data)
    
    def test_filter_by_model_name(self):
        """Test filtering audit logs by model name"""
        response = self.client.get('/api/accounting/audit-logs/?model_name=AccountV2')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        
        for audit in results:
            self.assertEqual(audit['model_name'], 'AccountV2')
    
    def test_filter_by_user(self):
        """Test filtering audit logs by user"""
        response = self.client.get(f'/api/accounting/audit-logs/?user={self.user2.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        
        for audit in results:
            self.assertEqual(audit['user']['id'], self.user2.id)
    
    def test_filter_by_action(self):
        """Test filtering audit logs by action"""
        response = self.client.get('/api/accounting/audit-logs/?action=CREATE')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        
        for audit in results:
            self.assertEqual(audit['action'], 'CREATE')
    
    def test_filter_by_object_id(self):
        """Test filtering audit logs by object ID"""
        response = self.client.get('/api/accounting/audit-logs/?object_id=1')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)  # CREATE and UPDATE for object 1
        
        for audit in results:
            self.assertEqual(audit['object_id'], 1)
    
    def test_filter_by_date_range(self):
        """Test filtering audit logs by date range"""
        # Set timestamp for one audit to be older
        old_date = timezone.now() - timedelta(days=10)
        AuditLog.objects.filter(id=self.audit1.id).update(timestamp=old_date)
        
        # Filter for recent logs only (use simple date format)
        start_date = (timezone.now() - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%S')
        response = self.client.get(f'/api/accounting/audit-logs/?start_date={start_date}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 3)  # Excludes the old one
    
    def test_combined_filters(self):
        """Test combining multiple filters"""
        response = self.client.get(
            f'/api/accounting/audit-logs/?model_name=AccountV2&user={self.user1.id}&action=UPDATE'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], self.audit2.id)
    
    def test_retrieve_audit_log_detail(self):
        """Test retrieving a single audit log"""
        response = self.client.get(f'/api/accounting/audit-logs/{self.audit1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.audit1.id)
        self.assertEqual(response.data['model_name'], 'AccountV2')
        self.assertEqual(response.data['action'], 'CREATE')
        self.assertIn('user', response.data)
        self.assertIn('timestamp', response.data)
        self.assertIn('changes', response.data)
    
    def test_audit_log_includes_user_details(self):
        """Test that audit log includes user details"""
        response = self.client.get(f'/api/accounting/audit-logs/{self.audit1.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data['user']
        self.assertEqual(user_data['id'], self.user1.id)
        self.assertEqual(user_data['username'], 'user1')
        self.assertIn('email', user_data)
    
    def test_audit_log_changes_field(self):
        """Test that changes field is properly serialized"""
        response = self.client.get(f'/api/accounting/audit-logs/{self.audit2.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        changes = response.data['changes']
        self.assertIn('before', changes)
        self.assertIn('after', changes)
        self.assertEqual(changes['before']['balance'], '1000.00')
        self.assertEqual(changes['after']['balance'], '1500.00')
    
    def test_audit_log_ordering(self):
        """Test that audit logs are ordered by timestamp (newest first)"""
        response = self.client.get('/api/accounting/audit-logs/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        
        # Verify ordering (newest first)
        for i in range(len(results) - 1):
            current_time = datetime.fromisoformat(results[i]['timestamp'].replace('Z', '+00:00'))
            next_time = datetime.fromisoformat(results[i+1]['timestamp'].replace('Z', '+00:00'))
            self.assertGreaterEqual(current_time, next_time)
    
    def test_unauthorized_access(self):
        """Test that unauthenticated users cannot access audit logs"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/accounting/audit-logs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_search_functionality(self):
        """Test searching audit logs"""
        response = self.client.get('/api/accounting/audit-logs/?search=Cash')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertGreater(len(results), 0)
    
    def test_audit_log_immutability_via_api(self):
        """Test that audit logs cannot be modified via API"""
        # Try to update an audit log
        response = self.client.put(
            f'/api/accounting/audit-logs/{self.audit1.id}/',
            {'reason': 'Modified reason'},
            format='json'
        )
        
        # Should not allow updates (method not allowed or forbidden)
        self.assertIn(response.status_code, [
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_403_FORBIDDEN
        ])
    
    def test_audit_log_cannot_be_deleted_via_api(self):
        """Test that audit logs cannot be deleted via API"""
        response = self.client.delete(f'/api/accounting/audit-logs/{self.audit1.id}/')
        
        # Should not allow deletion
        self.assertIn(response.status_code, [
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_403_FORBIDDEN
        ])
        
        # Verify audit log still exists
        self.assertTrue(AuditLog.objects.filter(id=self.audit1.id).exists())


class AuditLogExportTestCase(TestCase):
    """Test suite for audit log export functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='exportuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create sample audit log
        AuditLog.objects.create(
            model_name='AccountV2',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={'name': 'Test Account'}
        )
    
    def test_export_pdf_endpoint_exists(self):
        """Test that export PDF endpoint exists"""
        response = self.client.get('/api/accounting/audit-logs/export-pdf/')
        
        # Should return 200 or appropriate response (not 404)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_export_pdf_with_filters(self):
        """Test exporting PDF with filters applied"""
        response = self.client.get('/api/accounting/audit-logs/export-pdf/?model_name=AccountV2')
        
        # Should return PDF or success response
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_201_CREATED
        ])
