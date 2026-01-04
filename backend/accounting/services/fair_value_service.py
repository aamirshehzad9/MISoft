"""
Fair Value Service for IFRS 13 / IAS 40 Compliance

This service handles fair value measurements and adjustments for:
- Investment Property (IAS 40)
- Financial Instruments (IFRS 9)
- Biological Assets (IAS 41)
- Business Combinations (IFRS 3)
"""

from decimal import Decimal
from datetime import datetime, timedelta
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from accounting.models import (
    AccountV2, FairValueMeasurement, VoucherV2, VoucherEntryV2
)

User = get_user_model()


class FairValueService:
    """
    Service class for Fair Value Measurement operations
    Implements IFRS 13 fair value measurement framework
    """
    
    def __init__(self, user=None):
        """Initialize service with user context"""
        self.user = user
    
    def calculate_fair_value(self, account, measurement_date, valuation_inputs):
        """
        Calculate fair value based on valuation technique and inputs
        
        Args:
            account: AccountV2 instance
            measurement_date: Date of measurement
            valuation_inputs: Dict containing valuation parameters
            
        Returns:
            Decimal: Calculated fair value
        """
        technique = valuation_inputs.get('technique', 'market_approach')
        
        if technique == 'market_approach':
            return self._calculate_market_approach(valuation_inputs)
        elif technique == 'income_approach':
            return self._calculate_income_approach(valuation_inputs)
        elif technique == 'cost_approach':
            return self._calculate_cost_approach(valuation_inputs)
        else:
            raise ValidationError(f"Unknown valuation technique: {technique}")
    
    def _calculate_market_approach(self, inputs):
        """
        Market Approach: Comparable sales method
        
        Fair Value = Comparable Price × Adjustment Factors
        """
        comparable_price = Decimal(str(inputs.get('comparable_price', 0)))
        location_adjustment = Decimal(str(inputs.get('location_adjustment', 1.0)))
        size_adjustment = Decimal(str(inputs.get('size_adjustment', 1.0)))
        condition_adjustment = Decimal(str(inputs.get('condition_adjustment', 1.0)))
        
        fair_value = comparable_price * location_adjustment * size_adjustment * condition_adjustment
        return fair_value.quantize(Decimal('0.01'))
    
    def _calculate_income_approach(self, inputs):
        """
        Income Approach: Discounted Cash Flow (DCF)
        
        Fair Value = Σ (Cash Flow_t / (1 + r)^t)
        """
        annual_income = Decimal(str(inputs.get('annual_income', 0)))
        discount_rate = Decimal(str(inputs.get('discount_rate', 0.10)))
        years = int(inputs.get('projection_years', 10))
        terminal_value = Decimal(str(inputs.get('terminal_value', 0)))
        
        # Simple DCF calculation
        present_value = Decimal('0.00')
        for year in range(1, years + 1):
            pv_factor = (Decimal('1') + discount_rate) ** year
            present_value += annual_income / pv_factor
        
        # Add terminal value
        if terminal_value > 0:
            terminal_pv_factor = (Decimal('1') + discount_rate) ** years
            present_value += terminal_value / terminal_pv_factor
        
        return present_value.quantize(Decimal('0.01'))
    
    def _calculate_cost_approach(self, inputs):
        """
        Cost Approach: Replacement cost less depreciation
        
        Fair Value = Replacement Cost - Accumulated Depreciation
        """
        replacement_cost = Decimal(str(inputs.get('replacement_cost', 0)))
        depreciation_rate = Decimal(str(inputs.get('depreciation_rate', 0)))
        age_years = Decimal(str(inputs.get('age_years', 0)))
        
        accumulated_depreciation = replacement_cost * depreciation_rate * age_years
        fair_value = replacement_cost - accumulated_depreciation
        
        return max(fair_value, Decimal('0.00')).quantize(Decimal('0.01'))
    
    def calculate_gain_loss(self, fair_value, carrying_amount):
        """
        Calculate fair value gain or loss
        
        Args:
            fair_value: Fair value amount
            carrying_amount: Current carrying amount
            
        Returns:
            Decimal: Gain (positive) or Loss (negative)
        """
        return (Decimal(str(fair_value)) - Decimal(str(carrying_amount))).quantize(Decimal('0.01'))
    
    @transaction.atomic
    def create_fair_value_measurement(self, data):
        """
        Create a new fair value measurement record
        
        Args:
            data: Dict containing measurement data
            
        Returns:
            FairValueMeasurement instance
        """
        account = data['account']
        measurement_date = data['measurement_date']
        fair_value = Decimal(str(data['fair_value']))
        carrying_amount = Decimal(str(data.get('carrying_amount', account.current_balance)))
        
        # Calculate gain/loss
        gain_loss = self.calculate_gain_loss(fair_value, carrying_amount)
        
        # Create measurement record
        measurement = FairValueMeasurement.objects.create(
            account=account,
            measurement_date=measurement_date,
            measurement_purpose=data.get('measurement_purpose', 'subsequent_measurement'),
            fair_value_level=data['fair_value_level'],
            valuation_technique=data['valuation_technique'],
            valuation_description=data.get('valuation_description', ''),
            inputs_used=data.get('inputs_used', {}),
            fair_value=fair_value,
            carrying_amount=carrying_amount,
            gain_loss=gain_loss,
            recognized_in_pl=data.get('recognized_in_pl', True),
            external_valuer=data.get('external_valuer', ''),
            valuer_credentials=data.get('valuer_credentials', ''),
            valuation_report_ref=data.get('valuation_report_ref', ''),
            notes=data.get('notes', ''),
            created_by=self.user
        )
        
        return measurement
    
    @transaction.atomic
    def post_fair_value_adjustment(self, measurement, auto_approve=False):
        """
        Post fair value adjustment as a voucher entry
        
        Creates a journal voucher to record the fair value gain/loss
        
        Args:
            measurement: FairValueMeasurement instance
            auto_approve: Whether to auto-approve the voucher
            
        Returns:
            VoucherV2 instance
        """
        if measurement.gain_loss == 0:
            raise ValidationError("No gain/loss to post")
        
        if measurement.voucher:
            raise ValidationError("Fair value adjustment already posted")
        
        # Determine accounts for posting
        asset_account = measurement.account
        
        # Get or create fair value gain/loss account
        if measurement.is_gain:
            # Debit: Asset, Credit: Fair Value Gain
            gl_account = self._get_fair_value_gain_account()
            narration = f"Fair value gain on {asset_account.name}"
        else:
            # Debit: Fair Value Loss, Credit: Asset
            gl_account = self._get_fair_value_loss_account()
            narration = f"Fair value loss on {asset_account.name}"
        
        # Create voucher
        voucher = VoucherV2.objects.create(
            voucher_number=self._generate_voucher_number('FV'),
            voucher_type='journal',
            voucher_date=measurement.measurement_date,
            reference_number=f"FVM-{measurement.id}",
            narration=narration,
            total_amount=abs(measurement.gain_loss),
            status='posted' if auto_approve else 'draft',
            created_by=self.user
        )
        
        # Create voucher entries
        if measurement.is_gain:
            # Debit: Asset (increase)
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account=asset_account,
                debit_amount=abs(measurement.gain_loss),
                credit_amount=Decimal('0.00'),
                description=f"Fair value gain - {measurement.get_fair_value_level_display()}"
            )
            # Credit: Fair Value Gain
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account=gl_account,
                debit_amount=Decimal('0.00'),
                credit_amount=abs(measurement.gain_loss),
                description=f"Fair value gain - {measurement.get_fair_value_level_display()}"
            )
        else:
            # Debit: Fair Value Loss
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account=gl_account,
                debit_amount=abs(measurement.gain_loss),
                credit_amount=Decimal('0.00'),
                description=f"Fair value loss - {measurement.get_fair_value_level_display()}"
            )
            # Credit: Asset (decrease)
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account=asset_account,
                debit_amount=Decimal('0.00'),
                credit_amount=abs(measurement.gain_loss),
                description=f"Fair value loss - {measurement.get_fair_value_level_display()}"
            )
        
        # Link voucher to measurement
        measurement.voucher = voucher
        measurement.save()
        
        # Update account balance if posted
        if voucher.status == 'posted':
            if measurement.is_gain:
                asset_account.current_balance += abs(measurement.gain_loss)
            else:
                asset_account.current_balance -= abs(measurement.gain_loss)
            asset_account.save()
        
        return voucher
    
    def validate_fair_value_hierarchy(self, fair_value_level, inputs_used):
        """
        Validate that inputs match the declared fair value hierarchy level
        
        Args:
            fair_value_level: Level 1, 2, or 3
            inputs_used: Dict of valuation inputs
            
        Raises:
            ValidationError if inputs don't match hierarchy level
        """
        if fair_value_level == 'level_1':
            # Level 1: Must have quoted prices
            if 'quoted_price' not in inputs_used:
                raise ValidationError(
                    "Level 1 fair value requires quoted prices in active markets"
                )
        
        elif fair_value_level == 'level_2':
            # Level 2: Must have observable inputs
            observable_inputs = ['comparable_price', 'market_rate', 'observable_yield']
            if not any(inp in inputs_used for inp in observable_inputs):
                raise ValidationError(
                    "Level 2 fair value requires observable market inputs"
                )
        
        elif fair_value_level == 'level_3':
            # Level 3: Unobservable inputs allowed
            # More disclosure required but no validation needed
            pass
    
    def check_revaluation_frequency(self, account, last_measurement_date=None):
        """
        Check if revaluation is due based on business rules
        
        IFRS 13 / IAS 40 requires regular revaluation for fair value model
        
        Args:
            account: AccountV2 instance
            last_measurement_date: Date of last measurement
            
        Returns:
            Dict with revaluation status
        """
        if not last_measurement_date:
            # Get last measurement
            last_measurement = FairValueMeasurement.objects.filter(
                account=account
            ).order_by('-measurement_date').first()
            
            if last_measurement:
                last_measurement_date = last_measurement.measurement_date
            else:
                # No previous measurement
                return {
                    'is_due': True,
                    'reason': 'No previous fair value measurement found',
                    'days_overdue': None
                }
        
        # Calculate days since last measurement
        today = datetime.now().date()
        days_since = (today - last_measurement_date).days
        
        # Business rule: Revalue annually (365 days)
        revaluation_period = 365
        
        if days_since >= revaluation_period:
            return {
                'is_due': True,
                'reason': f'Last revaluation was {days_since} days ago',
                'days_overdue': days_since - revaluation_period,
                'last_measurement_date': last_measurement_date
            }
        else:
            return {
                'is_due': False,
                'reason': f'Revaluation due in {revaluation_period - days_since} days',
                'days_until_due': revaluation_period - days_since,
                'last_measurement_date': last_measurement_date
            }
    
    def _get_fair_value_gain_account(self):
        """Get or create Fair Value Gain account"""
        account, created = AccountV2.objects.get_or_create(
            code='7100',
            defaults={
                'name': 'Fair Value Gain',
                'account_type': 'revenue',
                'account_group': 'other_income',
                'ias_reference_code': 'IFRS 13',
                'ifrs_category': 'revenue',
                'measurement_basis': 'fair_value',
                'created_by': self.user
            }
        )
        return account
    
    def _get_fair_value_loss_account(self):
        """Get or create Fair Value Loss account"""
        account, created = AccountV2.objects.get_or_create(
            code='8100',
            defaults={
                'name': 'Fair Value Loss',
                'account_type': 'expense',
                'account_group': 'operating_expense',
                'ias_reference_code': 'IFRS 13',
                'ifrs_category': 'expenses',
                'measurement_basis': 'fair_value',
                'created_by': self.user
            }
        )
        return account
    
    def _generate_voucher_number(self, prefix='FV'):
        """Generate unique voucher number"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{prefix}-{timestamp}"
