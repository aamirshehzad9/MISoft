from django.db import transaction
from django.core.exceptions import ValidationError
from .models import VoucherV2, VoucherEntryV2, AccountV2

class VoucherService:
    @staticmethod
    @transaction.atomic
    def create_voucher(data, user=None):
        """
        Create a new voucher with entries.
        data format:
        {
            'voucher_type': 'JE',
            'voucher_date': '2025-01-01',
            'reference_number': 'REF123',
            'narration': '...',
            'entries': [
                {'account_id': 1, 'debit': 100, 'credit': 0},
                {'account_id': 2, 'debit': 0, 'credit': 100}
            ]
        }
        """
        entries_data = data.pop('entries', [])
        
        # Create Voucher Header
        voucher = VoucherV2.objects.create(
            created_by=user,
            **data
        )
        
        # Create Entries
        for entry in entries_data:
            VoucherEntryV2.objects.create(
                voucher=voucher,
                account_id=entry['account_id'],
                debit_amount=entry.get('debit', 0),
                credit_amount=entry.get('credit', 0),
                cost_center_id=entry.get('cost_center_id'),
                department_id=entry.get('department_id')
            )
            
        return voucher

    @staticmethod
    def post_voucher(voucher_id, user=None):
        """
        Validate and post a voucher.
        """
        try:
            voucher = VoucherV2.objects.get(id=voucher_id)
        except VoucherV2.DoesNotExist:
            raise ValidationError("Voucher not found")
            
        if voucher.status == 'posted':
            raise ValidationError("Voucher is already posted")
            
        # Validate Double Entry
        try:
            voucher.validate_double_entry()
        except ValueError as e:
            raise ValidationError(str(e))
            
        # Post (updates balances and status)
        voucher.approved_by = user
        voucher.post()
        
        return voucher
