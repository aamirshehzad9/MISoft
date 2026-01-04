"""
Unit Tests for Module 1.1 Week 3: Multi-Entity Consolidation & IAS 21 FX Automation

Tests cover:
- Entity model and hierarchy
- Consolidation service
- FX gain/loss calculations (unrealized and realized)
- Automatic posting
- Intercompany elimination
- Consolidation reports

Target: >90% code coverage, 100% pass rate
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta

from accounting.models import (
    Entity, CurrencyV2, AccountV2, VoucherV2, VoucherEntryV2,
    FXRevaluationLog
)
from accounting.services import ConsolidationService, ExchangeGainLossService

User = get_user_model()


class EntityModelTestCase(TestCase):
    """Test Entity model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create currencies
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        self.eur = CurrencyV2.objects.create(
            currency_code='EUR',
            currency_name='Euro',
            symbol='€'
        )
    
    def test_entity_creation(self):
        """Test creating an entity"""
        entity = Entity.objects.create(
            entity_code='HQ',
            entity_name='Headquarters',
            country='USA',
            functional_currency=self.usd,
            entity_type='parent',
            created_by=self.user
        )
        
        self.assertEqual(entity.entity_code, 'HQ')
        self.assertEqual(entity.entity_name, 'Headquarters')
        self.assertEqual(entity.functional_currency, self.usd)
        self.assertTrue(entity.is_active)
        self.assertEqual(entity.consolidation_percentage, Decimal('100.00'))
    
    def test_entity_hierarchy(self):
        """Test entity parent-child relationships"""
        parent = Entity.objects.create(
            entity_code='PARENT',
            entity_name='Parent Company',
            country='USA',
            functional_currency=self.usd,
            entity_type='parent',
            created_by=self.user
        )
        
        child = Entity.objects.create(
            entity_code='CHILD1',
            entity_name='Subsidiary 1',
            country='Germany',
            functional_currency=self.eur,
            parent_entity=parent,
            entity_type='subsidiary',
            consolidation_percentage=Decimal('80.00'),
            created_by=self.user
        )
        
        self.assertEqual(child.parent_entity, parent)
        self.assertIn(child, parent.subsidiaries.all())
        self.assertTrue(parent.is_root_entity())  # Has no parent, so is root
        self.assertFalse(child.is_root_entity())  # Has parent, so not root
    
    def test_entity_hierarchy_path(self):
        """Test getting full hierarchy path"""
        grandparent = Entity.objects.create(
            entity_code='GP',
            entity_name='Grandparent',
            country='USA',
            functional_currency=self.usd,
            created_by=self.user
        )
        
        parent = Entity.objects.create(
            entity_code='P',
            entity_name='Parent',
            country='USA',
            functional_currency=self.usd,
            parent_entity=grandparent,
            created_by=self.user
        )
        
        child = Entity.objects.create(
            entity_code='C',
            entity_name='Child',
            country='USA',
            functional_currency=self.usd,
            parent_entity=parent,
            created_by=self.user
        )
        
        path = child.get_full_hierarchy_path()
        self.assertEqual(path, 'GP > P > C')
    
    def test_entity_requires_fx_translation(self):
        """Test FX translation requirement check"""
        entity_no_translation = Entity.objects.create(
            entity_code='E1',
            entity_name='Entity 1',
            country='USA',
            functional_currency=self.usd,
            created_by=self.user
        )
        
        entity_with_translation = Entity.objects.create(
            entity_code='E2',
            entity_name='Entity 2',
            country='Germany',
            functional_currency=self.eur,
            presentation_currency=self.usd,
            created_by=self.user
        )
        
        self.assertFalse(entity_no_translation.requires_fx_translation())
        self.assertTrue(entity_with_translation.requires_fx_translation())
    
    def test_entity_circular_reference_prevention(self):
        """Test that circular references are prevented"""
        entity1 = Entity.objects.create(
            entity_code='E1',
            entity_name='Entity 1',
            country='USA',
            functional_currency=self.usd,
            created_by=self.user
        )
        
        entity2 = Entity.objects.create(
            entity_code='E2',
            entity_name='Entity 2',
            country='USA',
            functional_currency=self.usd,
            parent_entity=entity1,
            created_by=self.user
        )
        
        # Try to create circular reference
        entity1.parent_entity = entity2
        
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            entity1.clean()


class ConsolidationServiceTestCase(TestCase):
    """Test Consolidation Service functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.service = ConsolidationService(user=self.user)
        
        # Create currency
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        
        # Create parent entity
        self.parent = Entity.objects.create(
            entity_code='PARENT',
            entity_name='Parent Company',
            country='USA',
            functional_currency=self.usd,
            entity_type='parent',
            created_by=self.user
        )
        
        # Create subsidiary
        self.subsidiary = Entity.objects.create(
            entity_code='SUB1',
            entity_name='Subsidiary 1',
            country='USA',
            functional_currency=self.usd,
            parent_entity=self.parent,
            entity_type='subsidiary',
            consolidation_method='full',
            consolidation_percentage=Decimal('80.00'),
            created_by=self.user
        )
    
    def test_consolidate_entities(self):
        """Test basic entity consolidation"""
        result = self.service.consolidate_entities(
            self.parent,
            date.today()
        )
        
        self.assertEqual(result['parent_entity'], 'PARENT')
        self.assertEqual(result['total_entities'], 2)
        self.assertIn('PARENT', result['entities_consolidated'])
        self.assertIn('SUB1', result['entities_consolidated'])
    
    def test_minority_interest_calculation(self):
        """Test minority interest calculation"""
        result = self.service.consolidate_entities(
            self.parent,
            date.today()
        )
        
        # Should have minority interest for SUB1 (20%)
        self.assertIn('SUB1', result['minority_interests'])
        mi = result['minority_interests']['SUB1']
        self.assertEqual(mi['minority_percentage'], Decimal('20.00'))
    
    def test_get_consolidation_hierarchy(self):
        """Test getting consolidation hierarchy"""
        hierarchy = self.service.get_consolidation_hierarchy(self.parent)
        
        self.assertEqual(hierarchy['entity_code'], 'PARENT')
        self.assertEqual(len(hierarchy['children']), 1)
        self.assertEqual(hierarchy['children'][0]['entity_code'], 'SUB1')
    
    def test_consolidated_balance_sheet_generation(self):
        """Test consolidated balance sheet generation"""
        report = self.service.generate_consolidated_balance_sheet(
            self.parent,
            date.today()
        )
        
        self.assertEqual(report['report_title'], 'Consolidated Balance Sheet')
        self.assertEqual(report['entity'], 'Parent Company')
        self.assertIn('assets', report)
        self.assertIn('liabilities', report)
        self.assertIn('equity', report)
    
    def test_consolidated_pnl_generation(self):
        """Test consolidated P&L generation"""
        report = self.service.generate_consolidated_pnl(
            self.parent,
            date.today() - timedelta(days=30),
            date.today()
        )
        
        self.assertEqual(report['report_title'], 'Consolidated Statement of Profit or Loss')
        self.assertIn('revenue', report)
        self.assertIn('expenses', report)
        self.assertIn('net_income', report)
    
    def test_intercompany_elimination_report(self):
        """Test intercompany elimination report"""
        report = self.service.generate_intercompany_elimination_report(
            self.parent,
            date.today()
        )
        
        self.assertEqual(report['report_title'], 'Intercompany Elimination Report')
        self.assertIn('eliminations', report)
        self.assertIn('total_eliminations', report)


class ExchangeGainLossServiceTestCase(TestCase):
    """Test FX Gain/Loss Service functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.service = ExchangeGainLossService(user=self.user)
        
        # Create currencies
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        self.eur = CurrencyV2.objects.create(
            currency_code='EUR',
            currency_name='Euro',
            symbol='€'
        )
        
        # Create entity
        self.entity = Entity.objects.create(
            entity_code='TEST',
            entity_name='Test Entity',
            country='USA',
            functional_currency=self.usd,
            created_by=self.user
        )
    
    def test_calculate_realized_fx_gain(self):
        """Test realized FX gain calculation"""
        result = self.service.calculate_realized_fx_gain_loss(
            original_transaction_amount=Decimal('1000.00'),
            original_exchange_rate=Decimal('1.10'),
            settlement_amount=Decimal('1000.00'),
            settlement_exchange_rate=Decimal('1.15'),
            currency_from=self.eur,
            currency_to=self.usd
        )
        
        # Gain = (1000 * 1.15) - (1000 * 1.10) = 1150 - 1100 = 50
        self.assertEqual(result['realized_fx_gain_loss'], Decimal('50.00'))
        self.assertTrue(result['is_gain'])
    
    def test_calculate_realized_fx_loss(self):
        """Test realized FX loss calculation"""
        result = self.service.calculate_realized_fx_gain_loss(
            original_transaction_amount=Decimal('1000.00'),
            original_exchange_rate=Decimal('1.15'),
            settlement_amount=Decimal('1000.00'),
            settlement_exchange_rate=Decimal('1.10'),
            currency_from=self.eur,
            currency_to=self.usd
        )
        
        # Loss = (1000 * 1.10) - (1000 * 1.15) = 1100 - 1150 = -50
        self.assertEqual(result['realized_fx_gain_loss'], Decimal('-50.00'))
        self.assertFalse(result['is_gain'])
    
    def test_revalue_monetary_items(self):
        """Test monetary items revaluation"""
        result = self.service.revalue_monetary_items(
            entity=self.entity,
            revaluation_date=date.today(),
            auto_post=False
        )
        
        self.assertEqual(result['entity_code'], 'TEST')
        self.assertIn('accounts_revalued', result)
        self.assertIn('total_gain', result)
        self.assertIn('total_loss', result)
        self.assertIn('net_fx_gain_loss', result)
    
    def test_fx_gain_account_creation(self):
        """Test FX gain account auto-creation"""
        account = self.service._get_fx_gain_account(unrealized=True)
        
        self.assertEqual(account.code, '7200')
        self.assertEqual(account.name, 'Unrealized FX Gain')
        self.assertEqual(account.account_type, 'income')
    
    def test_fx_loss_account_creation(self):
        """Test FX loss account auto-creation"""
        account = self.service._get_fx_loss_account(unrealized=True)
        
        self.assertEqual(account.code, '8200')
        self.assertEqual(account.name, 'Unrealized FX Loss')
        self.assertEqual(account.account_type, 'expense')


class FXRevaluationLogTestCase(TestCase):
    """Test FX Revaluation Log model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        
        self.entity = Entity.objects.create(
            entity_code='TEST',
            entity_name='Test Entity',
            country='USA',
            functional_currency=self.usd,
            created_by=self.user
        )
    
    def test_fx_revaluation_log_creation(self):
        """Test creating FX revaluation log"""
        log = FXRevaluationLog.objects.create(
            revaluation_id='REV-20250129-001',
            entity=self.entity,
            revaluation_date=date.today(),
            functional_currency=self.usd,
            accounts_revalued=5,
            total_gain=Decimal('100.00'),
            total_loss=Decimal('50.00'),
            net_fx_gain_loss=Decimal('50.00'),
            status='calculated',
            execution_method='manual',
            created_by=self.user
        )
        
        self.assertEqual(log.revaluation_id, 'REV-20250129-001')
        self.assertEqual(log.entity, self.entity)
        self.assertEqual(log.net_fx_gain_loss, Decimal('50.00'))
        self.assertTrue(log.is_successful)
        self.assertTrue(log.has_fx_impact)
    
    def test_fx_revaluation_log_no_impact(self):
        """Test FX revaluation log with no impact"""
        log = FXRevaluationLog.objects.create(
            revaluation_id='REV-20250129-002',
            entity=self.entity,
            revaluation_date=date.today(),
            functional_currency=self.usd,
            accounts_revalued=5,
            total_gain=Decimal('0.00'),
            total_loss=Decimal('0.00'),
            net_fx_gain_loss=Decimal('0.00'),
            status='calculated',
            created_by=self.user
        )
        
        self.assertFalse(log.has_fx_impact)


class ConsolidationReportsTestCase(TestCase):
    """Test consolidation report generation"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.service = ConsolidationService(user=self.user)
        
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        
        self.parent = Entity.objects.create(
            entity_code='PARENT',
            entity_name='Parent Company',
            country='USA',
            functional_currency=self.usd,
            entity_type='parent',
            created_by=self.user
        )
    
    def test_fx_gainloss_report_generation(self):
        """Test FX gain/loss report generation"""
        # Create FX revaluation log
        FXRevaluationLog.objects.create(
            revaluation_id='REV-001',
            entity=self.parent,
            revaluation_date=date.today(),
            functional_currency=self.usd,
            accounts_revalued=3,
            total_gain=Decimal('150.00'),
            total_loss=Decimal('75.00'),
            net_fx_gain_loss=Decimal('75.00'),
            status='posted',
            created_by=self.user
        )
        
        report = self.service.generate_fx_gainloss_report(
            self.parent,
            date.today() - timedelta(days=30),
            date.today()
        )
        
        self.assertEqual(report['report_title'], 'Consolidated FX Gain/Loss Report')
        self.assertEqual(report['total_unrealized_gain'], Decimal('150.00'))
        self.assertEqual(report['total_unrealized_loss'], Decimal('75.00'))
        self.assertEqual(report['net_fx_gain_loss'], Decimal('75.00'))
