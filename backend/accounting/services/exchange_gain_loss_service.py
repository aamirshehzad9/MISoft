"""
Exchange Gain/Loss Service for IAS 21 FX Automation

Implements IAS 21 foreign exchange gain/loss calculations:
- Unrealized FX gain/loss (revaluation)
- Realized FX gain/loss (settlement)
- Automatic month-end revaluation
- Translation adjustments
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Optional

from accounting.models import (
    Entity, AccountV2, VoucherV2, VoucherEntryV2,
    CurrencyV2, ExchangeRateV2
)


class ExchangeGainLossService:
    """
    Service for IAS 21 Foreign Exchange Gain/Loss Automation
    
    Handles:
    - Unrealized FX gain/loss (revaluation of monetary items)
    - Realized FX gain/loss (settlement of transactions)
    - Automatic month-end revaluation
    - Translation adjustments for foreign operations
    """
    
    def __init__(self, user=None):
        self.user = user
    
    def calculate_unrealized_fx_gain_loss(
        self,
        entity: Entity,
        revaluation_date: date,
        target_currency: Optional[CurrencyV2] = None
    ) -> Dict:
        """
        Calculate unrealized FX gain/loss for monetary items per IAS 21
        
        Monetary items include:
        - Cash and cash equivalents
        - Receivables
        - Payables
        - Loans
        
        Args:
            entity: Entity to revalue
            revaluation_date: Date for revaluation (usually month-end)
            target_currency: Currency to revalue to (defaults to functional currency)
            
        Returns:
            Dict with unrealized FX gain/loss details
        """
        if target_currency is None:
            target_currency = entity.functional_currency
        
        # Identify monetary accounts
        monetary_accounts = self._identify_monetary_accounts(entity)
        
        unrealized_gains_losses = []
        total_gain = Decimal('0.00')
        total_loss = Decimal('0.00')
        
        for account in monetary_accounts:
            # Skip if account is in functional currency
            if not hasattr(account, 'currency') or account.currency == target_currency:
                continue
            
            # Get current exchange rate
            current_rate = self._get_exchange_rate(
                account.currency,
                target_currency,
                revaluation_date
            )
            
            # Get original/book exchange rate (simplified - would track per transaction)
            book_rate = self._get_book_exchange_rate(account)
            
            # Calculate revalued amount
            foreign_currency_balance = account.current_balance
            revalued_amount = foreign_currency_balance * current_rate
            book_amount = foreign_currency_balance * book_rate
            
            # Calculate unrealized gain/loss
            fx_gain_loss = revalued_amount - book_amount
            
            if fx_gain_loss != Decimal('0.00'):
                unrealized_gains_losses.append({
                    'account_code': account.code,
                    'account_name': account.name,
                    'foreign_currency': account.currency.currency_code,
                    'foreign_currency_balance': foreign_currency_balance,
                    'book_rate': book_rate,
                    'current_rate': current_rate,
                    'book_amount': book_amount,
                    'revalued_amount': revalued_amount,
                    'fx_gain_loss': fx_gain_loss,
                    'is_gain': fx_gain_loss > 0
                })
                
                if fx_gain_loss > 0:
                    total_gain += fx_gain_loss
                else:
                    total_loss += abs(fx_gain_loss)
        
        return {
            'entity_code': entity.entity_code,
            'entity_name': entity.entity_name,
            'revaluation_date': revaluation_date,
            'target_currency': target_currency.currency_code,
            'unrealized_gains_losses': unrealized_gains_losses,
            'total_gain': total_gain,
            'total_loss': total_loss,
            'net_fx_gain_loss': total_gain - total_loss,
            'accounts_revalued': len(unrealized_gains_losses)
        }
    
    def calculate_realized_fx_gain_loss(
        self,
        original_transaction_amount: Decimal,
        original_exchange_rate: Decimal,
        settlement_amount: Decimal,
        settlement_exchange_rate: Decimal,
        currency_from: CurrencyV2,
        currency_to: CurrencyV2
    ) -> Dict:
        """
        Calculate realized FX gain/loss on settlement per IAS 21
        
        Realized FX gain/loss occurs when:
        - A foreign currency transaction is settled
        - Exchange rate differs from original transaction date
        
        Args:
            original_transaction_amount: Amount in foreign currency
            original_exchange_rate: Exchange rate at transaction date
            settlement_amount: Amount in foreign currency at settlement
            settlement_exchange_rate: Exchange rate at settlement date
            currency_from: Foreign currency
            currency_to: Functional currency
            
        Returns:
            Dict with realized FX gain/loss
        """
        # Calculate functional currency amounts
        original_functional_amount = original_transaction_amount * original_exchange_rate
        settlement_functional_amount = settlement_amount * settlement_exchange_rate
        
        # Realized FX gain/loss
        realized_fx_gain_loss = settlement_functional_amount - original_functional_amount
        
        return {
            'transaction_type': 'settlement',
            'foreign_currency': currency_from.currency_code,
            'functional_currency': currency_to.currency_code,
            'original_amount': original_transaction_amount,
            'original_rate': original_exchange_rate,
            'original_functional_amount': original_functional_amount,
            'settlement_amount': settlement_amount,
            'settlement_rate': settlement_exchange_rate,
            'settlement_functional_amount': settlement_functional_amount,
            'realized_fx_gain_loss': realized_fx_gain_loss,
            'is_gain': realized_fx_gain_loss > 0,
            'description': f'Realized FX {"gain" if realized_fx_gain_loss > 0 else "loss"} on settlement'
        }
    
    @transaction.atomic
    def post_fx_gain_loss(
        self,
        fx_data: Dict,
        fx_type: str = 'unrealized',
        auto_approve: bool = False
    ) -> VoucherV2:
        """
        Post FX gain/loss as journal entry
        
        Args:
            fx_data: Output from calculate_unrealized_fx_gain_loss or calculate_realized_fx_gain_loss
            fx_type: 'unrealized' or 'realized'
            auto_approve: Whether to auto-approve the voucher
            
        Returns:
            Created VoucherV2
        """
        if fx_type == 'unrealized':
            return self._post_unrealized_fx(fx_data, auto_approve)
        else:
            return self._post_realized_fx(fx_data, auto_approve)
    
    def _post_unrealized_fx(self, fx_data: Dict, auto_approve: bool) -> VoucherV2:
        """Post unrealized FX gain/loss"""
        net_fx = fx_data['net_fx_gain_loss']
        
        if net_fx == Decimal('0.00'):
            raise ValidationError("No FX gain/loss to post")
        
        # Create voucher
        voucher = VoucherV2.objects.create(
            voucher_number=self._generate_fx_voucher_number('UFX'),
            voucher_type='journal',
            voucher_date=fx_data['revaluation_date'],
            narration=f"Unrealized FX revaluation for {fx_data['entity_name']} - {fx_data['revaluation_date']}",
            total_amount=abs(net_fx),
            status='draft',
            created_by=self.user
        )
        
        # Get or create FX gain/loss accounts
        fx_gain_account = self._get_fx_gain_account(unrealized=True)
        fx_loss_account = self._get_fx_loss_account(unrealized=True)
        
        # Create entries for each account
        for item in fx_data['unrealized_gains_losses']:
            fx_amount = abs(item['fx_gain_loss'])
            
            # Get the account being revalued
            account = AccountV2.objects.get(code=item['account_code'])
            
            if item['is_gain']:
                # Debit: Asset/Receivable, Credit: FX Gain
                VoucherEntryV2.objects.create(
                    voucher=voucher,
                    account=account,
                    debit_amount=fx_amount,
                    credit_amount=Decimal('0.00'),
                    narration=f"FX revaluation gain"
                )
                VoucherEntryV2.objects.create(
                    voucher=voucher,
                    account=fx_gain_account,
                    debit_amount=Decimal('0.00'),
                    credit_amount=fx_amount,
                    narration=f"Unrealized FX gain on {item['account_code']}"
                )
            else:
                # Debit: FX Loss, Credit: Asset/Payable
                VoucherEntryV2.objects.create(
                    voucher=voucher,
                    account=fx_loss_account,
                    debit_amount=fx_amount,
                    credit_amount=Decimal('0.00'),
                    narration=f"Unrealized FX loss on {item['account_code']}"
                )
                VoucherEntryV2.objects.create(
                    voucher=voucher,
                    account=account,
                    debit_amount=Decimal('0.00'),
                    credit_amount=fx_amount,
                    narration=f"FX revaluation loss"
                )
        
        if auto_approve:
            voucher.status = 'posted'
            voucher.approved_by = self.user
            voucher.approved_at = timezone.now()
            voucher.save()
        
        return voucher
    
    def _post_realized_fx(self, fx_data: Dict, auto_approve: bool) -> VoucherV2:
        """Post realized FX gain/loss"""
        fx_amount = abs(fx_data['realized_fx_gain_loss'])
        
        if fx_amount == Decimal('0.00'):
            raise ValidationError("No realized FX gain/loss to post")
        
        # Create voucher
        voucher = VoucherV2.objects.create(
            voucher_number=self._generate_fx_voucher_number('RFX'),
            voucher_type='journal',
            voucher_date=date.today(),
            narration=fx_data['description'],
            total_amount=fx_amount,
            status='draft',
            created_by=self.user
        )
        
        # Get FX gain/loss accounts
        fx_gain_account = self._get_fx_gain_account(unrealized=False)
        fx_loss_account = self._get_fx_loss_account(unrealized=False)
        
        if fx_data['is_gain']:
            # Realized gain
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account=fx_gain_account,
                debit_amount=Decimal('0.00'),
                credit_amount=fx_amount,
                narration="Realized FX gain"
            )
        else:
            # Realized loss
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account=fx_loss_account,
                debit_amount=fx_amount,
                credit_amount=Decimal('0.00'),
                narration="Realized FX loss"
            )
        
        if auto_approve:
            voucher.status = 'posted'
            voucher.approved_by = self.user
            voucher.approved_at = timezone.now()
            voucher.save()
        
        return voucher
    
    def revalue_monetary_items(
        self,
        entity: Entity,
        revaluation_date: Optional[date] = None,
        auto_post: bool = False
    ) -> Dict:
        """
        Revalue all monetary items for an entity (month-end process)
        
        Args:
            entity: Entity to revalue
            revaluation_date: Date for revaluation (defaults to today)
            auto_post: Whether to automatically post the revaluation
            
        Returns:
            Dict with revaluation results
        """
        if revaluation_date is None:
            revaluation_date = date.today()
        
        # Calculate unrealized FX
        fx_data = self.calculate_unrealized_fx_gain_loss(
            entity,
            revaluation_date
        )
        
        voucher = None
        if auto_post and fx_data['net_fx_gain_loss'] != Decimal('0.00'):
            voucher = self.post_fx_gain_loss(
                fx_data,
                fx_type='unrealized',
                auto_approve=True
            )
        
        return {
            **fx_data,
            'voucher_created': voucher is not None,
            'voucher_number': voucher.voucher_number if voucher else None
        }
    
    @transaction.atomic
    def create_reversal_entry(
        self,
        original_voucher: VoucherV2,
        reversal_date: Optional[date] = None,
        auto_approve: bool = False
    ) -> VoucherV2:
        """
        Create reversal entry for unrealized FX gain/loss
        
        Per IAS 21 best practices, unrealized FX gain/loss entries are often
        reversed at the beginning of the next period to avoid double-counting
        when the next revaluation is performed.
        
        Args:
            original_voucher: The original FX revaluation voucher to reverse
            reversal_date: Date for reversal (defaults to first day of next month)
            auto_approve: Whether to auto-approve the reversal voucher
            
        Returns:
            Created reversal VoucherV2
        """
        from datetime import timedelta
        from calendar import monthrange
        
        # Validate that this is an unrealized FX voucher
        if not original_voucher.voucher_number.startswith('UFX-'):
            raise ValidationError("Only unrealized FX vouchers can be reversed")
        
        if original_voucher.status != 'posted':
            raise ValidationError("Only posted vouchers can be reversed")
        
        # Calculate reversal date if not provided
        if reversal_date is None:
            # First day of next month
            original_date = original_voucher.voucher_date
            # Get last day of current month
            last_day = monthrange(original_date.year, original_date.month)[1]
            # Add one day to get first day of next month
            reversal_date = date(original_date.year, original_date.month, last_day) + timedelta(days=1)
        
        # Create reversal voucher
        reversal_voucher = VoucherV2.objects.create(
            voucher_number=self._generate_fx_voucher_number('REV-UFX'),
            voucher_type='journal',
            voucher_date=reversal_date,
            narration=f"Reversal of {original_voucher.voucher_number} - {original_voucher.narration}",
            reference_number=original_voucher.voucher_number,
            total_amount=original_voucher.total_amount,
            status='draft',
            created_by=self.user
        )
        
        # Get original entries
        original_entries = VoucherEntryV2.objects.filter(voucher=original_voucher)
        
        # Create reversed entries (swap debit and credit)
        for entry in original_entries:
            VoucherEntryV2.objects.create(
                voucher=reversal_voucher,
                account=entry.account,
                debit_amount=entry.credit_amount,  # Swap
                credit_amount=entry.debit_amount,  # Swap
                cost_center=entry.cost_center,
                department=entry.department,
                narration=f"Reversal: {entry.narration}"
            )
        
        if auto_approve:
            reversal_voucher.status = 'posted'
            reversal_voucher.approved_by = self.user
            reversal_voucher.approved_at = timezone.now()
            reversal_voucher.save()
        
        return reversal_voucher
    
    def schedule_automatic_reversal(
        self,
        entity: Entity,
        revaluation_voucher: VoucherV2,
        create_immediately: bool = False
    ) -> Dict:
        """
        Schedule automatic reversal of unrealized FX revaluation
        
        This method can be used to set up automatic reversal entries
        for the next accounting period.
        
        Args:
            entity: Entity for the revaluation
            revaluation_voucher: The revaluation voucher to reverse
            create_immediately: If True, create reversal now; if False, return schedule info
            
        Returns:
            Dict with reversal information
        """
        from datetime import timedelta
        from calendar import monthrange
        
        # Calculate reversal date (first day of next month)
        original_date = revaluation_voucher.voucher_date
        last_day = monthrange(original_date.year, original_date.month)[1]
        reversal_date = date(original_date.year, original_date.month, last_day) + timedelta(days=1)
        
        reversal_info = {
            'entity_code': entity.entity_code,
            'entity_name': entity.entity_name,
            'original_voucher_number': revaluation_voucher.voucher_number,
            'original_voucher_date': revaluation_voucher.voucher_date,
            'scheduled_reversal_date': reversal_date,
            'reversal_amount': revaluation_voucher.total_amount,
            'status': 'scheduled'
        }
        
        if create_immediately:
            reversal_voucher = self.create_reversal_entry(
                revaluation_voucher,
                reversal_date=reversal_date,
                auto_approve=False  # Keep as draft for review
            )
            reversal_info['reversal_voucher_number'] = reversal_voucher.voucher_number
            reversal_info['reversal_voucher_id'] = reversal_voucher.id
            reversal_info['status'] = 'created'
        
        return reversal_info
    
    def _identify_monetary_accounts(self, entity: Entity) -> List[AccountV2]:

        """
        Identify monetary accounts per IAS 21
        
        Monetary items:
        - Cash and cash equivalents
        - Trade receivables
        - Trade payables
        - Loans and borrowings
        """
        # In production, you'd filter by entity
        # For now, identify by account type/group
        
        monetary_account_groups = [
            'cash_bank',
            'current_asset',  # Receivables
            'current_liability',  # Payables
            'long_term_liability'  # Loans
        ]
        
        monetary_accounts = AccountV2.objects.filter(
            account_group__in=monetary_account_groups,
            # In production: entity=entity
        ).exclude(current_balance=Decimal('0.00'))
        
        return list(monetary_accounts)
    
    def _get_exchange_rate(
        self,
        from_currency: CurrencyV2,
        to_currency: CurrencyV2,
        rate_date: date
    ) -> Decimal:
        """Get exchange rate for a specific date"""
        try:
            rate = ExchangeRateV2.objects.filter(
                from_currency=from_currency,
                to_currency=to_currency,
                effective_date__lte=rate_date
            ).order_by('-effective_date').first()
            
            if rate:
                return rate.rate
            else:
                # Default to 1.0 if no rate found
                return Decimal('1.00')
        except Exception:
            return Decimal('1.00')
    
    def _get_book_exchange_rate(self, account: AccountV2) -> Decimal:
        """
        Get the book exchange rate for an account
        
        In production, this would track the weighted average rate
        or specific transaction rates
        """
        # Simplified - return 1.0
        # In production, track historical rates per transaction
        return Decimal('1.00')
    
    def _get_fx_gain_account(self, unrealized: bool = False) -> AccountV2:
        """Get or create FX gain account"""
        code = '7200' if unrealized else '7210'
        name = 'Unrealized FX Gain' if unrealized else 'Realized FX Gain'
        
        account, created = AccountV2.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'account_type': 'income',
                'account_group': 'other_income',
                'ias_reference_code': 'IAS 21',
                'created_by': self.user
            }
        )
        return account
    
    def _get_fx_loss_account(self, unrealized: bool = False) -> AccountV2:
        """Get or create FX loss account"""
        code = '8200' if unrealized else '8210'
        name = 'Unrealized FX Loss' if unrealized else 'Realized FX Loss'
        
        account, created = AccountV2.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'account_type': 'expense',
                'account_group': 'other_expense',
                'ias_reference_code': 'IAS 21',
                'created_by': self.user
            }
        )
        return account
    
    def _generate_fx_voucher_number(self, prefix: str = 'FX') -> str:
        """Generate unique FX voucher number"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        return f'{prefix}-{timestamp}'
