"""
API Tests for Audit Reports
Task 1.7.4: Audit Reports
Module 1.7: Audit Trail System (IASB Requirement)

Tests the audit report generation endpoints
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta
from django.utils import timezone
from accounting.models import AuditLog

User = get_user_model()


class UserActivityReportTestCase(TestCase):
    """Test suite for User Activity Report"""
    
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
        # User 1 actions
        for i in range(5):
            AuditLog.objects.create(
                model_name='AccountV2',
                object_id=i,
                action='CREATE',
                user=self.user1,
                ip_address='192.168.1.1',
                changes={'name': f'Account {i}'}
            )
        
        # User 2 actions
        for i in range(3):
            AuditLog.objects.create(
                model_name='Product',
                object_id=i,
                action='UPDATE',
                user=self.user2,
                ip_address='10.0.0.1',
                changes={'name': f'Product {i}'}
            )
    
    def test_user_activity_report_endpoint_exists(self):
        """Test that user activity report endpoint exists"""
        response = self.client.get('/api/accounting/audit-logs/user-activity-report/')
        
        # Should return 200 (not 404)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_activity_report_structure(self):
        """Test user activity report structure"""
        response = self.client.get('/api/accounting/audit-logs/user-activity-report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('users', response.data)
    
    def test_user_activity_report_summary(self):
        """Test user activity report summary statistics"""
        response = self.client.get('/api/accounting/audit-logs/user-activity-report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        summary = response.data['summary']
        
        self.assertIn('total_users', summary)
        self.assertIn('total_actions', summary)
        self.assertIn('date_range', summary)
    
    def test_user_activity_report_by_user(self):
        """Test filtering user activity report by specific user"""
        response = self.client.get(f'/api/accounting/audit-logs/user-activity-report/?user={self.user1.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        users = response.data['users']
        
        # Should only include user1
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]['user']['id'], self.user1.id)
        self.assertEqual(users[0]['total_actions'], 5)
    
    def test_user_activity_report_date_range(self):
        """Test filtering user activity report by date range"""
        # Set one audit to be older
        old_date = timezone.now() - timedelta(days=10)
        AuditLog.objects.filter(id=AuditLog.objects.filter(user=self.user1).first().id).update(timestamp=old_date)
        
        # Filter for recent only
        start_date = (timezone.now() - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%S')
        response = self.client.get(f'/api/accounting/audit-logs/user-activity-report/?start_date={start_date}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_activity_report_action_breakdown(self):
        """Test that report includes action breakdown"""
        response = self.client.get(f'/api/accounting/audit-logs/user-activity-report/?user={self.user1.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data['users'][0]
        
        self.assertIn('actions_breakdown', user_data)
        self.assertIn('CREATE', user_data['actions_breakdown'])


class ChangeHistoryReportTestCase(TestCase):
    """Test suite for Change History Report"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Create sample audit logs for different models
        self.create_sample_audit_logs()
    
    def create_sample_audit_logs(self):
        """Create sample audit logs for testing"""
        # AccountV2 changes
        for i in range(4):
            AuditLog.objects.create(
                model_name='AccountV2',
                object_id=1,
                action='UPDATE',
                user=self.user,
                ip_address='127.0.0.1',
                changes={'balance': f'{1000 + i * 100}'}
            )
        
        # Product changes
        for i in range(2):
            AuditLog.objects.create(
                model_name='Product',
                object_id=1,
                action='UPDATE',
                user=self.user,
                ip_address='127.0.0.1',
                changes={'price': f'{100 + i * 10}'}
            )
    
    def test_change_history_report_endpoint_exists(self):
        """Test that change history report endpoint exists"""
        response = self.client.get('/api/accounting/audit-logs/change-history-report/')
        
        # Should return 200 (not 404)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_change_history_report_structure(self):
        """Test change history report structure"""
        response = self.client.get('/api/accounting/audit-logs/change-history-report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('models', response.data)
    
    def test_change_history_report_by_model(self):
        """Test filtering change history report by model"""
        response = self.client.get('/api/accounting/audit-logs/change-history-report/?model_name=AccountV2')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        models = response.data['models']
        
        # Should only include AccountV2
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]['model_name'], 'AccountV2')
        self.assertEqual(models[0]['total_changes'], 4)
    
    def test_change_history_report_summary(self):
        """Test change history report summary statistics"""
        response = self.client.get('/api/accounting/audit-logs/change-history-report/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        summary = response.data['summary']
        
        self.assertIn('total_models', summary)
        self.assertIn('total_changes', summary)
        self.assertIn('date_range', summary)
    
    def test_change_history_report_action_breakdown(self):
        """Test that report includes action breakdown by model"""
        response = self.client.get('/api/accounting/audit-logs/change-history-report/?model_name=AccountV2')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        model_data = response.data['models'][0]
        
        self.assertIn('actions_breakdown', model_data)
        self.assertIn('UPDATE', model_data['actions_breakdown'])
    
    def test_change_history_report_date_range(self):
        """Test filtering change history report by date range"""
        start_date = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
        response = self.client.get(f'/api/accounting/audit-logs/change-history-report/?start_date={start_date}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)


class AuditReportAuthorizationTestCase(TestCase):
    """Test authorization for audit reports"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
    
    def test_user_activity_report_requires_authentication(self):
        """Test that user activity report requires authentication"""
        response = self.client.get('/api/accounting/audit-logs/user-activity-report/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_change_history_report_requires_authentication(self):
        """Test that change history report requires authentication"""
        response = self.client.get('/api/accounting/audit-logs/change-history-report/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ObjectAuditTrailReportTestCase(TestCase):
    """Test suite for Object Audit Trail Report"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        # Create audit trail for a specific object
        self.model_name = "AccountV2"
        self.object_id = 999
        
        # 1. CREATE
        AuditLog.objects.create(
            model_name=self.model_name,
            object_id=self.object_id,
            action='CREATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={'name': 'Test Account', 'balance': '0.00'}
        )
        
        # 2. UPDATE
        AuditLog.objects.create(
            model_name=self.model_name,
            object_id=self.object_id,
            action='UPDATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={'before': {'balance': '0.00'}, 'after': {'balance': '100.00'}}
        )
        
        # 3. UPDATE again
        AuditLog.objects.create(
            model_name=self.model_name,
            object_id=self.object_id,
            action='UPDATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={'before': {'balance': '100.00'}, 'after': {'balance': '200.00'}}
        )
    
    def test_object_audit_trail_report_endpoint_exists(self):
        """Test that object audit trail report endpoint exists"""
        response = self.client.get(
            f'/api/accounting/audit-logs/object-history-report/?model_name={self.model_name}&object_id={self.object_id}'
        )
        # Should return 200 (not 404)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_object_audit_trail_report_structure(self):
        """Test structure of the object audit trail report"""
        response = self.client.get(
            f'/api/accounting/audit-logs/object-history-report/?model_name={self.model_name}&object_id={self.object_id}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('summary', response.data)
        self.assertIn('history', response.data)
        
        # Check summary
        summary = response.data['summary']
        self.assertEqual(summary['model_name'], self.model_name)
        self.assertEqual(int(summary['object_id']), self.object_id)
        self.assertEqual(summary['total_changes'], 3)
        
        # Check history
        history = response.data['history']
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['action'], 'UPDATE')  # Newest first

    def test_object_audit_trail_report_missing_params(self):
        """Test that missing params return 400"""
        response = self.client.get('/api/accounting/audit-logs/object-history-report/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
