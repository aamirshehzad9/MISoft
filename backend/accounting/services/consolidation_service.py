"""
Consolidation Service for Multi-Entity Consolidation

Implements IFRS 10 consolidation logic including:
- Entity consolidation
- Intercompany elimination
- Minority interest calculation
- Consolidation adjustments
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import date
from typing import List, Dict, Optional

from accounting.models import Entity, AccountV2, VoucherV2, VoucherEntryV2


class ConsolidationService:
    """
    Service for multi-entity consolidation per IFRS 10
    
    Handles:
    - Full consolidation (>50% ownership)
    - Proportionate consolidation
    - Equity method (20-50% ownership)
    - Intercompany elimination
    - Minority interest calculation
    """
    
    def __init__(self, user=None):
        self.user = user
    
    def consolidate_entities(
        self,
        parent_entity: Entity,
        consolidation_date: date,
        include_children: bool = True
    ) -> Dict:
        """
        Consolidate financial statements for a parent entity and its subsidiaries
        
        Args:
            parent_entity: The parent entity to consolidate
            consolidation_date: Date for consolidation
            include_children: Whether to include all child entities recursively
            
        Returns:
            Dict containing consolidated balances and adjustments
        """
        # Get all entities to consolidate
        entities_to_consolidate = [parent_entity]
        
        if include_children:
            entities_to_consolidate.extend(parent_entity.get_all_children())
        
        # Filter active entities only
        entities_to_consolidate = [e for e in entities_to_consolidate if e.is_active]
        
        # Initialize consolidation data
        consolidated_balances = {}
        consolidation_adjustments = []
        minority_interests = {}
        
        # Consolidate each entity based on method
        for entity in entities_to_consolidate:
            if entity == parent_entity:
                # Parent entity - 100% consolidation
                entity_balances = self._get_entity_balances(entity, consolidation_date)
                self._add_to_consolidated_balances(
                    consolidated_balances,
                    entity_balances,
                    Decimal('100.00')
                )
            else:
                # Subsidiary - apply consolidation method
                if entity.consolidation_method == 'full':
                    # Full consolidation - include 100% of subsidiary
                    entity_balances = self._get_entity_balances(entity, consolidation_date)
                    self._add_to_consolidated_balances(
                        consolidated_balances,
                        entity_balances,
                        Decimal('100.00')
                    )
                    
                    # Calculate minority interest
                    if entity.consolidation_percentage < Decimal('100.00'):
                        minority_pct = Decimal('100.00') - entity.consolidation_percentage
                        minority_interests[entity.entity_code] = self._calculate_minority_interest(
                            entity,
                            entity_balances,
                            minority_pct
                        )
                
                elif entity.consolidation_method == 'proportionate':
                    # Proportionate consolidation
                    entity_balances = self._get_entity_balances(entity, consolidation_date)
                    self._add_to_consolidated_balances(
                        consolidated_balances,
                        entity_balances,
                        entity.consolidation_percentage
                    )
                
                elif entity.consolidation_method == 'equity':
                    # Equity method - only include investment account
                    equity_adjustment = self._calculate_equity_method_adjustment(
                        entity,
                        consolidation_date
                    )
                    consolidation_adjustments.append(equity_adjustment)
        
        # Eliminate intercompany transactions
        if len(entities_to_consolidate) > 1:
            intercompany_eliminations = self.eliminate_intercompany_transactions(
                entities_to_consolidate,
                consolidation_date
            )
            consolidation_adjustments.extend(intercompany_eliminations)
        
        return {
            'consolidation_date': consolidation_date,
            'parent_entity': parent_entity.entity_code,
            'entities_consolidated': [e.entity_code for e in entities_to_consolidate],
            'consolidated_balances': consolidated_balances,
            'consolidation_adjustments': consolidation_adjustments,
            'minority_interests': minority_interests,
            'total_entities': len(entities_to_consolidate)
        }
    
    def eliminate_intercompany_transactions(
        self,
        entities: List[Entity],
        consolidation_date: date
    ) -> List[Dict]:
        """
        Identify and eliminate intercompany transactions
        
        Args:
            entities: List of entities in the consolidation group
            consolidation_date: Date for consolidation
            
        Returns:
            List of elimination entries
        """
        eliminations = []
        entity_codes = [e.entity_code for e in entities]
        
        # Get all vouchers between entities in the group
        # This is a simplified version - in production, you'd have entity tracking on vouchers
        
        # Common intercompany accounts to eliminate:
        # - Intercompany receivables/payables
        # - Intercompany sales/purchases
        # - Intercompany dividends
        
        intercompany_account_patterns = [
            'intercompany',
            'inter-company',
            'inter company',
            'due from',
            'due to'
        ]
        
        # Find intercompany accounts
        intercompany_accounts = AccountV2.objects.filter(
            Q(name__icontains='intercompany') |
            Q(name__icontains='inter-company') |
            Q(code__icontains='IC')
        )
        
        for account in intercompany_accounts:
            if account.current_balance != Decimal('0.00'):
                eliminations.append({
                    'type': 'intercompany_elimination',
                    'account_code': account.code,
                    'account_name': account.name,
                    'balance_to_eliminate': account.current_balance,
                    'description': f'Eliminate intercompany balance for {account.name}'
                })
        
        return eliminations
    
    def _calculate_minority_interest(
        self,
        entity: Entity,
        entity_balances: Dict,
        minority_percentage: Decimal
    ) -> Dict:
        """
        Calculate minority interest (non-controlling interest) per IFRS 10
        
        Args:
            entity: The subsidiary entity
            entity_balances: Balances of the subsidiary
            minority_percentage: Percentage owned by minority shareholders
            
        Returns:
            Dict with minority interest calculation
        """
        # Calculate net assets (equity)
        total_assets = entity_balances.get('total_assets', Decimal('0.00'))
        total_liabilities = entity_balances.get('total_liabilities', Decimal('0.00'))
        net_assets = total_assets - total_liabilities
        
        # Minority interest = Net Assets × Minority %
        minority_interest_amount = net_assets * (minority_percentage / Decimal('100.00'))
        
        return {
            'entity_code': entity.entity_code,
            'entity_name': entity.entity_name,
            'minority_percentage': minority_percentage,
            'net_assets': net_assets,
            'minority_interest_amount': minority_interest_amount,
            'description': f'Minority interest in {entity.entity_name} ({minority_percentage}%)'
        }
    
    def _calculate_equity_method_adjustment(
        self,
        entity: Entity,
        consolidation_date: date
    ) -> Dict:
        """
        Calculate equity method adjustment for associates (IAS 28)
        
        Args:
            entity: The associate entity
            consolidation_date: Date for consolidation
            
        Returns:
            Dict with equity method adjustment
        """
        # Get entity's net income for the period
        # This is simplified - in production, you'd calculate actual net income
        
        return {
            'type': 'equity_method',
            'entity_code': entity.entity_code,
            'entity_name': entity.entity_name,
            'ownership_percentage': entity.consolidation_percentage,
            'description': f'Equity method adjustment for {entity.entity_name}'
        }
    
    def _get_entity_balances(
        self,
        entity: Entity,
        as_of_date: date
    ) -> Dict:
        """
        Get account balances for an entity
        
        Note: This is simplified. In production, you'd filter accounts by entity
        and calculate balances as of the consolidation date.
        
        Args:
            entity: The entity
            as_of_date: Date to get balances
            
        Returns:
            Dict with account balances by category
        """
        # In production, you'd have entity field on AccountV2 or VoucherV2
        # For now, return structure for demonstration
        
        balances = {
            'total_assets': Decimal('0.00'),
            'total_liabilities': Decimal('0.00'),
            'total_equity': Decimal('0.00'),
            'total_revenue': Decimal('0.00'),
            'total_expenses': Decimal('0.00'),
            'accounts': {}
        }
        
        # This would be implemented when entity field is added to vouchers/accounts
        
        return balances
    
    def _add_to_consolidated_balances(
        self,
        consolidated: Dict,
        entity_balances: Dict,
        percentage: Decimal
    ):
        """
        Add entity balances to consolidated balances
        
        Args:
            consolidated: Consolidated balances dict (modified in place)
            entity_balances: Entity balances to add
            percentage: Percentage to consolidate (0-100)
        """
        factor = percentage / Decimal('100.00')
        
        for key in ['total_assets', 'total_liabilities', 'total_equity', 
                    'total_revenue', 'total_expenses']:
            if key not in consolidated:
                consolidated[key] = Decimal('0.00')
            
            consolidated[key] += entity_balances.get(key, Decimal('0.00')) * factor
    
    @transaction.atomic
    def apply_consolidation_adjustments(
        self,
        consolidation_data: Dict,
        create_voucher: bool = True
    ) -> Optional[VoucherV2]:
        """
        Apply consolidation adjustments as journal entries
        
        Args:
            consolidation_data: Output from consolidate_entities()
            create_voucher: Whether to create a voucher for adjustments
            
        Returns:
            VoucherV2 if created, None otherwise
        """
        if not create_voucher:
            return None
        
        adjustments = consolidation_data.get('consolidation_adjustments', [])
        
        if not adjustments:
            return None
        
        # Create consolidation adjustment voucher
        voucher = VoucherV2.objects.create(
            voucher_number=self._generate_consolidation_voucher_number(),
            voucher_type='journal',
            voucher_date=consolidation_data['consolidation_date'],
            narration=f"Consolidation adjustments for {consolidation_data['parent_entity']}",
            status='draft',
            created_by=self.user
        )
        
        # Create entries for each adjustment
        # This would be implemented based on specific adjustment types
        
        return voucher
    
    def _generate_consolidation_voucher_number(self) -> str:
        """Generate unique voucher number for consolidation"""
        from django.utils import timezone
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f'CONS-{timestamp}'
    
    def get_consolidation_hierarchy(self, root_entity: Entity) -> Dict:
        """
        Get the full consolidation hierarchy for an entity
        
        Args:
            root_entity: The root entity
            
        Returns:
            Dict representing the hierarchy tree
        """
        def build_tree(entity: Entity) -> Dict:
            children = entity.subsidiaries.filter(is_active=True)
            
            return {
                'entity_code': entity.entity_code,
                'entity_name': entity.entity_name,
                'entity_type': entity.entity_type,
                'consolidation_method': entity.consolidation_method,
                'consolidation_percentage': str(entity.consolidation_percentage),
                'functional_currency': entity.functional_currency.currency_code,
                'children': [build_tree(child) for child in children]
            }
        
        return build_tree(root_entity)
    
    # ============================================
    # CONSOLIDATION REPORTS (IFRS 10)
    # ============================================
    
    def generate_consolidated_balance_sheet(
        self,
        parent_entity: Entity,
        as_of_date: date
    ) -> Dict:
        """
        Generate Consolidated Balance Sheet per IFRS 10
        
        Args:
            parent_entity: The parent entity
            as_of_date: Balance sheet date
            
        Returns:
            Dict with consolidated balance sheet
        """
        # Get consolidation data
        consolidation_data = self.consolidate_entities(
            parent_entity,
            as_of_date,
            include_children=True
        )
        
        balances = consolidation_data['consolidated_balances']
        minority_interests = consolidation_data['minority_interests']
        
        # Calculate total minority interest
        total_minority_interest = sum(
            mi['minority_interest_amount'] 
            for mi in minority_interests.values()
        )
        
        # Build balance sheet
        return {
            'report_title': 'Consolidated Balance Sheet',
            'entity': parent_entity.entity_name,
            'as_of_date': as_of_date,
            'currency': parent_entity.functional_currency.currency_code,
            
            # Assets
            'assets': {
                'total_assets': balances.get('total_assets', Decimal('0.00')),
                # Detailed breakdown would go here
            },
            
            # Liabilities
            'liabilities': {
                'total_liabilities': balances.get('total_liabilities', Decimal('0.00')),
                # Detailed breakdown would go here
            },
            
            # Equity
            'equity': {
                'total_equity': balances.get('total_equity', Decimal('0.00')),
                'minority_interest': total_minority_interest,
                'equity_attributable_to_parent': balances.get('total_equity', Decimal('0.00')) - total_minority_interest,
            },
            
            # Balancing
            'total_liabilities_and_equity': (
                balances.get('total_liabilities', Decimal('0.00')) +
                balances.get('total_equity', Decimal('0.00'))
            ),
            
            # Metadata
            'entities_consolidated': consolidation_data['entities_consolidated'],
            'total_entities': consolidation_data['total_entities'],
            'minority_interests_detail': minority_interests
        }
    
    def generate_consolidated_pnl(
        self,
        parent_entity: Entity,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Generate Consolidated Profit & Loss Statement per IFRS 10
        
        Args:
            parent_entity: The parent entity
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Dict with consolidated P&L
        """
        # Get consolidation data
        consolidation_data = self.consolidate_entities(
            parent_entity,
            end_date,
            include_children=True
        )
        
        balances = consolidation_data['consolidated_balances']
        
        # Calculate net income
        total_revenue = balances.get('total_revenue', Decimal('0.00'))
        total_expenses = balances.get('total_expenses', Decimal('0.00'))
        net_income = total_revenue - total_expenses
        
        # Calculate minority interest in net income
        minority_interests = consolidation_data['minority_interests']
        minority_share_of_income = Decimal('0.00')
        for mi in minority_interests.values():
            # Simplified - would calculate actual share of income
            minority_share_of_income += Decimal('0.00')
        
        return {
            'report_title': 'Consolidated Statement of Profit or Loss',
            'entity': parent_entity.entity_name,
            'period_start': start_date,
            'period_end': end_date,
            'currency': parent_entity.functional_currency.currency_code,
            
            # Revenue
            'revenue': {
                'total_revenue': total_revenue,
                # Detailed breakdown would go here
            },
            
            # Expenses
            'expenses': {
                'total_expenses': total_expenses,
                # Detailed breakdown would go here
            },
            
            # Net Income
            'net_income': net_income,
            'minority_interest_in_income': minority_share_of_income,
            'net_income_attributable_to_parent': net_income - minority_share_of_income,
            
            # Metadata
            'entities_consolidated': consolidation_data['entities_consolidated'],
            'total_entities': consolidation_data['total_entities']
        }
    
    def generate_intercompany_elimination_report(
        self,
        parent_entity: Entity,
        as_of_date: date
    ) -> Dict:
        """
        Generate Intercompany Elimination Report
        
        Shows all intercompany balances that need to be eliminated
        in consolidation per IFRS 10
        
        Args:
            parent_entity: The parent entity
            as_of_date: Report date
            
        Returns:
            Dict with intercompany elimination details
        """
        # Get all entities
        entities = [parent_entity] + parent_entity.get_all_children()
        entities = [e for e in entities if e.is_active]
        
        # Get intercompany eliminations
        eliminations = self.eliminate_intercompany_transactions(
            entities,
            as_of_date
        )
        
        # Calculate totals
        total_eliminations = sum(
            abs(e['balance_to_eliminate']) 
            for e in eliminations
        )
        
        return {
            'report_title': 'Intercompany Elimination Report',
            'entity': parent_entity.entity_name,
            'as_of_date': as_of_date,
            'currency': parent_entity.functional_currency.currency_code,
            
            # Eliminations
            'eliminations': eliminations,
            'total_eliminations': total_eliminations,
            'elimination_count': len(eliminations),
            
            # Entities
            'entities_in_group': [e.entity_code for e in entities],
            'total_entities': len(entities),
            
            # Summary by type
            'summary_by_type': self._summarize_eliminations_by_type(eliminations)
        }
    
    def generate_fx_gainloss_report(
        self,
        parent_entity: Entity,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Generate FX Gain/Loss Report for consolidated group
        
        Shows unrealized and realized FX gains/losses across all entities
        
        Args:
            parent_entity: The parent entity
            start_date: Period start date
            end_date: Period end date
            
        Returns:
            Dict with FX gain/loss details
        """
        from accounting.models import FXRevaluationLog
        
        # Get all entities
        entities = [parent_entity] + parent_entity.get_all_children()
        entities = [e for e in entities if e.is_active]
        
        # Get FX revaluation logs for the period
        fx_logs = FXRevaluationLog.objects.filter(
            entity__in=entities,
            revaluation_date__gte=start_date,
            revaluation_date__lte=end_date,
            status__in=['calculated', 'posted']
        )
        
        # Aggregate FX gains/losses
        total_unrealized_gain = Decimal('0.00')
        total_unrealized_loss = Decimal('0.00')
        entity_fx_summary = {}
        
        for log in fx_logs:
            entity_code = log.entity.entity_code
            
            if entity_code not in entity_fx_summary:
                entity_fx_summary[entity_code] = {
                    'entity_name': log.entity.entity_name,
                    'total_gain': Decimal('0.00'),
                    'total_loss': Decimal('0.00'),
                    'net_fx': Decimal('0.00'),
                    'revaluation_count': 0
                }
            
            entity_fx_summary[entity_code]['total_gain'] += log.total_gain
            entity_fx_summary[entity_code]['total_loss'] += log.total_loss
            entity_fx_summary[entity_code]['net_fx'] += log.net_fx_gain_loss
            entity_fx_summary[entity_code]['revaluation_count'] += 1
            
            total_unrealized_gain += log.total_gain
            total_unrealized_loss += log.total_loss
        
        return {
            'report_title': 'Consolidated FX Gain/Loss Report',
            'entity': parent_entity.entity_name,
            'period_start': start_date,
            'period_end': end_date,
            'currency': parent_entity.functional_currency.currency_code,
            
            # Totals
            'total_unrealized_gain': total_unrealized_gain,
            'total_unrealized_loss': total_unrealized_loss,
            'net_fx_gain_loss': total_unrealized_gain - total_unrealized_loss,
            
            # By Entity
            'entity_fx_summary': entity_fx_summary,
            
            # Metadata
            'entities_in_group': [e.entity_code for e in entities],
            'total_entities': len(entities),
            'total_revaluations': fx_logs.count()
        }
    
    def _summarize_eliminations_by_type(self, eliminations: List[Dict]) -> Dict:
        """Summarize eliminations by type"""
        summary = {}
        
        for elim in eliminations:
            elim_type = elim.get('type', 'other')
            
            if elim_type not in summary:
                summary[elim_type] = {
                    'count': 0,
                    'total_amount': Decimal('0.00')
                }
            
            summary[elim_type]['count'] += 1
            summary[elim_type]['total_amount'] += abs(elim.get('balance_to_eliminate', Decimal('0.00')))
        
        return summary

