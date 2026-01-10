from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounting.models import CostCenterV2

User = get_user_model()

class CostCenterModelTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='manager', password='password')
        
    def test_create_enhanced_costcenter(self):
        """Test creation of cost center with new fields"""
        cc = CostCenterV2.objects.create(
            name="IT Department",
            code="CC-IT-001",
            budget_allocation=Decimal('50000.00'),
            is_profit_center=False,
            manager=self.manager
        )
        
        self.assertEqual(cc.name, "IT Department")
        self.assertEqual(cc.budget_allocation, 50000.00)
        self.assertFalse(cc.is_profit_center)
        self.assertEqual(cc.manager, self.manager)

    def test_profit_center_flag(self):
        """Test profit center flag logic"""
        pc = CostCenterV2.objects.create(
            name="Sales Department",
            code="CC-SALES-001",
            is_profit_center=True
        )
        self.assertTrue(pc.is_profit_center)
        # Check default budget allocation is 0 if not specified
        self.assertEqual(pc.budget_allocation, Decimal('0.00'))

    def test_manager_link(self):
        """Test manager foreign key"""
        cc = CostCenterV2.objects.create(
            name="HR Department",
            code="CC-HR-001",
            manager=self.manager
        )
        self.assertEqual(cc.manager.username, 'manager')
