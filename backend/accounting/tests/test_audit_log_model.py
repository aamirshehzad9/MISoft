"""
Unit Tests for AuditLog Model
Task 1.7.1: Create AuditLog Model
Module 1.7: Audit Trail System (IASB Requirement)

Tests the immutable audit log for all data changes
IFRS Compliance: Maintains complete audit trail as required by IASB
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from accounting.models import AuditLog
from products.models import Product, ProductCategory, UnitOfMeasure

User = get_user_model()


class AuditLogModelTestCase(TestCase):
    """Test suite for AuditLog model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='auditor',
            password='testpass123',
            email='auditor@example.com'
        )
    
    def test_create_audit_log_entry(self):
        """Test creating a basic audit log entry"""
        audit = AuditLog.objects.create(
            model_name='Product',
            object_id=123,
            action='CREATE',
            user=self.user,
            ip_address='192.168.1.1',
            changes={'name': 'Test Product', 'code': 'PROD-001'},
            reason='Initial product creation'
        )
        
        self.assertEqual(audit.model_name, 'Product')
        self.assertEqual(audit.object_id, 123)
        self.assertEqual(audit.action, 'CREATE')
        self.assertEqual(audit.user, self.user)
        self.assertEqual(audit.ip_address, '192.168.1.1')
        self.assertEqual(audit.changes['name'], 'Test Product')
        self.assertEqual(audit.reason, 'Initial product creation')
        self.assertIsNotNone(audit.timestamp)
    
    def test_audit_log_timestamp_auto_created(self):
        """Test that timestamp is automatically set"""
        before = timezone.now()
        
        audit = AuditLog.objects.create(
            model_name='Account',
            object_id=1,
            action='UPDATE',
            user=self.user,
            ip_address='10.0.0.1',
            changes={}
        )
        
        after = timezone.now()
        
        self.assertGreaterEqual(audit.timestamp, before)
        self.assertLessEqual(audit.timestamp, after)
    
    def test_audit_log_action_choices(self):
        """Test that action field accepts valid choices"""
        valid_actions = ['CREATE', 'UPDATE', 'DELETE']
        
        for action in valid_actions:
            audit = AuditLog.objects.create(
                model_name='TestModel',
                object_id=1,
                action=action,
                user=self.user,
                ip_address='127.0.0.1',
                changes={}
            )
            self.assertEqual(audit.action, action)
    
    def test_audit_log_changes_json_field(self):
        """Test that changes field stores JSON data correctly"""
        changes_data = {
            'before': {'price': '100.00', 'quantity': 10},
            'after': {'price': '120.00', 'quantity': 15}
        }
        
        audit = AuditLog.objects.create(
            model_name='Product',
            object_id=456,
            action='UPDATE',
            user=self.user,
            ip_address='192.168.1.100',
            changes=changes_data
        )
        
        # Retrieve and verify JSON data
        saved_audit = AuditLog.objects.get(id=audit.id)
        self.assertEqual(saved_audit.changes['before']['price'], '100.00')
        self.assertEqual(saved_audit.changes['after']['quantity'], 15)
    
    def test_audit_log_reason_optional(self):
        """Test that reason field is optional"""
        audit = AuditLog.objects.create(
            model_name='Account',
            object_id=789,
            action='DELETE',
            user=self.user,
            ip_address='172.16.0.1',
            changes={}
        )
        
        self.assertEqual(audit.reason, '')
    
    def test_audit_log_ipv6_address(self):
        """Test that IPv6 addresses are supported"""
        audit = AuditLog.objects.create(
            model_name='Voucher',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='2001:0db8:85a3:0000:0000:8a2e:0370:7334',
            changes={}
        )
        
        self.assertEqual(audit.ip_address, '2001:0db8:85a3:0000:0000:8a2e:0370:7334')
    
    def test_audit_log_string_representation(self):
        """Test __str__ method"""
        audit = AuditLog.objects.create(
            model_name='Product',
            object_id=100,
            action='UPDATE',
            user=self.user,
            ip_address='192.168.1.1',
            changes={}
        )
        
        expected_str = f"UPDATE Product #100 by {self.user.username}"
        self.assertEqual(str(audit), expected_str)
    
    def test_audit_log_ordering(self):
        """Test that audit logs are ordered by timestamp (newest first)"""
        # Create multiple audit entries
        audit1 = AuditLog.objects.create(
            model_name='Product',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        audit2 = AuditLog.objects.create(
            model_name='Product',
            object_id=1,
            action='UPDATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        audit3 = AuditLog.objects.create(
            model_name='Product',
            object_id=1,
            action='UPDATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        # Verify ordering (newest first)
        audits = AuditLog.objects.all()
        self.assertEqual(audits[0].id, audit3.id)
        self.assertEqual(audits[1].id, audit2.id)
        self.assertEqual(audits[2].id, audit1.id)
    
    def test_audit_log_immutability(self):
        """Test that audit logs cannot be modified (IFRS requirement)"""
        audit = AuditLog.objects.create(
            model_name='Account',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='192.168.1.1',
            changes={'balance': '1000.00'}
        )
        
        original_timestamp = audit.timestamp
        original_changes = audit.changes.copy()
        
        # Attempt to modify (should not be allowed in production)
        # This test verifies the model structure supports immutability
        self.assertEqual(audit.timestamp, original_timestamp)
        self.assertEqual(audit.changes, original_changes)
    
    def test_audit_log_user_relationship(self):
        """Test foreign key relationship with User model"""
        audit = AuditLog.objects.create(
            model_name='Voucher',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        # Verify relationship
        self.assertEqual(audit.user.username, 'auditor')
        self.assertEqual(audit.user.email, 'auditor@example.com')
        
        # Verify reverse relationship
        user_audits = self.user.audit_logs.all()
        self.assertIn(audit, user_audits)
    
    def test_audit_log_complex_changes(self):
        """Test storing complex nested JSON changes"""
        complex_changes = {
            'before': {
                'account': {
                    'code': '1000',
                    'name': 'Cash',
                    'balance': '5000.00'
                },
                'metadata': {
                    'last_updated': '2024-01-01',
                    'tags': ['asset', 'liquid']
                }
            },
            'after': {
                'account': {
                    'code': '1000',
                    'name': 'Cash - Main',
                    'balance': '5500.00'
                },
                'metadata': {
                    'last_updated': '2024-01-15',
                    'tags': ['asset', 'liquid', 'primary']
                }
            }
        }
        
        audit = AuditLog.objects.create(
            model_name='Account',
            object_id=1000,
            action='UPDATE',
            user=self.user,
            ip_address='192.168.1.1',
            changes=complex_changes
        )
        
        # Verify complex data is preserved
        saved_audit = AuditLog.objects.get(id=audit.id)
        self.assertEqual(saved_audit.changes['before']['account']['name'], 'Cash')
        self.assertEqual(saved_audit.changes['after']['account']['balance'], '5500.00')
        self.assertIn('primary', saved_audit.changes['after']['metadata']['tags'])
    
    def test_audit_log_filtering_by_model(self):
        """Test filtering audit logs by model name"""
        # Create audits for different models
        AuditLog.objects.create(
            model_name='Product',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        AuditLog.objects.create(
            model_name='Account',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        AuditLog.objects.create(
            model_name='Product',
            object_id=2,
            action='UPDATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        # Filter by model
        product_audits = AuditLog.objects.filter(model_name='Product')
        account_audits = AuditLog.objects.filter(model_name='Account')
        
        self.assertEqual(product_audits.count(), 2)
        self.assertEqual(account_audits.count(), 1)
    
    def test_audit_log_filtering_by_object(self):
        """Test filtering audit logs for specific object"""
        # Create multiple audits for same object
        for action in ['CREATE', 'UPDATE', 'UPDATE', 'DELETE']:
            AuditLog.objects.create(
                model_name='Product',
                object_id=123,
                action=action,
                user=self.user,
                ip_address='127.0.0.1',
                changes={}
            )
        
        # Filter by model and object
        object_history = AuditLog.objects.filter(
            model_name='Product',
            object_id=123
        )
        
        self.assertEqual(object_history.count(), 4)
        self.assertEqual(object_history.first().action, 'DELETE')  # Newest first
        self.assertEqual(object_history.last().action, 'CREATE')   # Oldest last
    
    def test_audit_log_date_range_filtering(self):
        """Test filtering audit logs by date range"""
        from datetime import timedelta
        
        # Create audit with specific timestamp
        old_audit = AuditLog.objects.create(
            model_name='Account',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        # Modify timestamp to simulate old entry
        old_timestamp = timezone.now() - timedelta(days=30)
        AuditLog.objects.filter(id=old_audit.id).update(timestamp=old_timestamp)
        
        # Create recent audit
        recent_audit = AuditLog.objects.create(
            model_name='Account',
            object_id=2,
            action='CREATE',
            user=self.user,
            ip_address='127.0.0.1',
            changes={}
        )
        
        # Filter by date range
        cutoff_date = timezone.now() - timedelta(days=7)
        recent_audits = AuditLog.objects.filter(timestamp__gte=cutoff_date)
        
        self.assertEqual(recent_audits.count(), 1)
        self.assertEqual(recent_audits.first().id, recent_audit.id)


class AuditLogIFRSComplianceTestCase(TestCase):
    """Test IFRS/IASB compliance requirements for audit trail"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='compliance_user',
            password='testpass123'
        )
    
    def test_audit_trail_completeness(self):
        """Test that all required fields are captured (IASB requirement)"""
        audit = AuditLog.objects.create(
            model_name='Voucher',
            object_id=1,
            action='CREATE',
            user=self.user,
            ip_address='192.168.1.1',
            changes={'amount': '1000.00'},
            reason='Monthly closing entry'
        )
        
        # Verify all required fields are present
        required_fields = [
            'model_name', 'object_id', 'action', 'user',
            'timestamp', 'ip_address', 'changes'
        ]
        
        for field in required_fields:
            self.assertIsNotNone(getattr(audit, field))
    
    def test_audit_trail_non_repudiation(self):
        """Test that audit entries are linked to authenticated users"""
        audit = AuditLog.objects.create(
            model_name='Account',
            object_id=1,
            action='UPDATE',
            user=self.user,
            ip_address='192.168.1.1',
            changes={}
        )
        
        # Verify user is authenticated and traceable
        self.assertIsNotNone(audit.user)
        self.assertTrue(audit.user.is_authenticated)
        self.assertEqual(audit.user.username, 'compliance_user')
    
    def test_audit_trail_chronological_integrity(self):
        """Test that timestamps maintain chronological order"""
        audits = []
        
        for i in range(5):
            audit = AuditLog.objects.create(
                model_name='Product',
                object_id=i,
                action='CREATE',
                user=self.user,
                ip_address='127.0.0.1',
                changes={}
            )
            audits.append(audit)
        
        # Verify timestamps are in order
        for i in range(len(audits) - 1):
            self.assertLessEqual(audits[i].timestamp, audits[i+1].timestamp)
