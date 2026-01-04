"""
Bank Transfer Service
Module 2.3: Bank Transfer System
Task 2.3.2: Transfer Service

Handles professional bank-to-bank transfer workflow including creation,
approval, execution, and multi-currency support.
"""
from django.db import transaction
from accounting.models import BankTransfer, VoucherV2, VoucherEntryV2
from decimal import Decimal
import datetime


class BankTransferService:
    """Service class for bank transfer management"""

    @staticmethod
    def create_transfer(transfer_number, transfer_date, from_bank, to_bank, amount,
                       from_currency, to_currency, exchange_rate, user,
                       description="", reference=""):
        """
        Create a new bank transfer
        
        Args:
            transfer_number: Unique transfer number
            transfer_date: Date of transfer
            from_bank: Source bank account (AccountV2 instance)
            to_bank: Destination bank account (AccountV2 instance)
            amount: Transfer amount in source currency
            from_currency: Source currency (CurrencyV2 instance)
            to_currency: Destination currency (CurrencyV2 instance)
            exchange_rate: Exchange rate
            user: User creating the transfer
            description: Optional description
            reference: Optional external reference
            
        Returns:
            BankTransfer instance
        """
        with transaction.atomic():
            transfer = BankTransfer.objects.create(
                transfer_number=transfer_number,
                transfer_date=transfer_date,
                from_bank=from_bank,
                to_bank=to_bank,
                amount=amount,
                from_currency=from_currency,
                to_currency=to_currency,
                exchange_rate=exchange_rate,
                status='pending',
                approval_status='pending',
                description=description,
                reference=reference,
                created_by=user
            )
            
            return transfer

    @staticmethod
    def approve_transfer(transfer, user):
        """
        Approve a bank transfer
        
        Args:
            transfer: BankTransfer instance
            user: User approving the transfer
            
        Returns:
            Updated BankTransfer instance
            
        Raises:
            ValueError: If transfer is not in pending approval status
        """
        if transfer.approval_status != 'pending':
            raise ValueError(f"Only pending transfers can be approved. Current status: {transfer.approval_status}")
        
        with transaction.atomic():
            transfer.approval_status = 'approved'
            transfer.save()
            
            return transfer

    @staticmethod
    def reject_transfer(transfer, user):
        """
        Reject a bank transfer
        
        Args:
            transfer: BankTransfer instance
            user: User rejecting the transfer
            
        Returns:
            Updated BankTransfer instance
            
        Raises:
            ValueError: If transfer is not in pending approval status
        """
        if transfer.approval_status != 'pending':
            raise ValueError(f"Only pending transfers can be rejected. Current status: {transfer.approval_status}")
        
        with transaction.atomic():
            transfer.approval_status = 'rejected'
            transfer.status = 'failed'
            transfer.save()
            
            return transfer

    @staticmethod
    def execute_transfer(transfer, user, fx_account=None):
        """
        Execute a bank transfer (creates accounting voucher)
        
        Args:
            transfer: BankTransfer instance
            user: User executing the transfer
            fx_account: Optional FX gain/loss account for multi-currency transfers
            
        Returns:
            Updated BankTransfer instance with voucher
            
        Raises:
            ValueError: If transfer is not approved or already completed
        """
        if transfer.approval_status != 'approved':
            raise ValueError("Transfer must be approved before execution")
        
        if transfer.status == 'completed':
            raise ValueError("Transfer has already been completed")
        
        with transaction.atomic():
            # Create voucher
            voucher = VoucherV2.objects.create(
                voucher_number=f"VCH-{transfer.transfer_number}",
                voucher_type="JV",  # Journal Voucher
                voucher_date=transfer.transfer_date,
                total_amount=transfer.amount,
                currency=transfer.from_currency,
                status='posted',
                created_by=user
            )
            
            # Same currency transfer
            if transfer.from_currency == transfer.to_currency:
                # Debit destination bank
                VoucherEntryV2.objects.create(
                    voucher=voucher,
                    account=transfer.to_bank,
                    debit_amount=transfer.amount,
                    credit_amount=Decimal('0.00'),
                    description=f"Transfer from {transfer.from_bank.name}"
                )
                
                # Credit source bank
                VoucherEntryV2.objects.create(
                    voucher=voucher,
                    account=transfer.from_bank,
                    debit_amount=Decimal('0.00'),
                    credit_amount=transfer.amount,
                    description=f"Transfer to {transfer.to_bank.name}"
                )
            else:
                # Multi-currency transfer
                converted_amount = transfer.converted_amount
                
                # Debit destination bank (in destination currency)
                VoucherEntryV2.objects.create(
                    voucher=voucher,
                    account=transfer.to_bank,
                    debit_amount=converted_amount,
                    credit_amount=Decimal('0.00'),
                    description=f"Transfer from {transfer.from_bank.name} (FX: {transfer.exchange_rate})"
                )
                
                # Credit source bank (in source currency)
                VoucherEntryV2.objects.create(
                    voucher=voucher,
                    account=transfer.from_bank,
                    debit_amount=Decimal('0.00'),
                    credit_amount=transfer.amount,
                    description=f"Transfer to {transfer.to_bank.name}"
                )
                
                # Handle FX difference if needed
                fx_difference = transfer.amount - converted_amount
                if fx_difference != 0 and fx_account:
                    if fx_difference > 0:
                        # FX Loss (debit)
                        VoucherEntryV2.objects.create(
                            voucher=voucher,
                            account=fx_account,
                            debit_amount=abs(fx_difference),
                            credit_amount=Decimal('0.00'),
                            description="FX Loss on transfer"
                        )
                    else:
                        # FX Gain (credit)
                        VoucherEntryV2.objects.create(
                            voucher=voucher,
                            account=fx_account,
                            debit_amount=Decimal('0.00'),
                            credit_amount=abs(fx_difference),
                            description="FX Gain on transfer"
                        )
            
            # Update transfer
            transfer.voucher = voucher
            transfer.status = 'completed'
            transfer.save()
            
            return transfer

    @staticmethod
    def get_pending_transfers():
        """
        Get all pending transfers
        
        Returns:
            QuerySet of BankTransfer instances
        """
        return BankTransfer.objects.filter(status='pending').order_by('-transfer_date')

    @staticmethod
    def get_transfers_by_status(status):
        """
        Get transfers by status
        
        Args:
            status: Transfer status ('pending', 'completed', 'failed')
            
        Returns:
            QuerySet of BankTransfer instances
        """
        return BankTransfer.objects.filter(status=status).order_by('-transfer_date')

    @staticmethod
    def get_transfers_by_approval_status(approval_status):
        """
        Get transfers by approval status
        
        Args:
            approval_status: Approval status ('pending', 'approved', 'rejected')
            
        Returns:
            QuerySet of BankTransfer instances
        """
        return BankTransfer.objects.filter(approval_status=approval_status).order_by('-transfer_date')

    @staticmethod
    def generate_transfer_register(start_date=None, end_date=None, status=None):
        """
        Generate Bank Transfer Register
        Task 2.3.3: Transfer Reports
        
        Lists all bank transfers with optional filtering
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            status: Optional status filter ('pending', 'completed', 'failed')
            
        Returns:
            dict: Report with list of transfers and summary
        """
        transfers = BankTransfer.objects.select_related(
            'from_bank', 'to_bank', 'from_currency', 'to_currency', 'voucher', 'created_by'
        )
        
        if start_date:
            transfers = transfers.filter(transfer_date__gte=start_date)
        if end_date:
            transfers = transfers.filter(transfer_date__lte=end_date)
        if status:
            transfers = transfers.filter(status=status)
        
        transfers = transfers.order_by('-transfer_date')
        
        transfers_list = []
        total_amount = Decimal('0.00')
        
        for transfer in transfers:
            transfers_list.append({
                'transfer_number': transfer.transfer_number,
                'transfer_date': transfer.transfer_date,
                'from_bank_name': transfer.from_bank.name,
                'from_bank_code': transfer.from_bank.code,
                'to_bank_name': transfer.to_bank.name,
                'to_bank_code': transfer.to_bank.code,
                'amount': transfer.amount,
                'from_currency_code': transfer.from_currency.currency_code,
                'to_currency_code': transfer.to_currency.currency_code,
                'exchange_rate': transfer.exchange_rate,
                'converted_amount': transfer.converted_amount,
                'status': transfer.status,
                'approval_status': transfer.approval_status,
                'voucher_number': transfer.voucher.voucher_number if transfer.voucher else None,
                'description': transfer.description,
                'reference': transfer.reference,
                'created_by': transfer.created_by.username
            })
            total_amount += transfer.amount
        
        return {
            'report_type': 'Bank Transfer Register',
            'start_date': start_date,
            'end_date': end_date,
            'status_filter': status,
            'transfers': transfers_list,
            'count': len(transfers_list),
            'total_amount': total_amount
        }

    @staticmethod
    def generate_pending_transfers_report(approval_status=None):
        """
        Generate Pending Transfers Report
        Task 2.3.3: Transfer Reports
        
        Lists all pending transfers (not yet executed)
        
        Args:
            approval_status: Optional approval status filter ('pending', 'approved')
            
        Returns:
            dict: Report with list of pending transfers and summary
        """
        # Get transfers that are pending execution
        transfers = BankTransfer.objects.filter(status='pending').select_related(
            'from_bank', 'to_bank', 'from_currency', 'to_currency', 'created_by'
        )
        
        if approval_status:
            transfers = transfers.filter(approval_status=approval_status)
        
        transfers = transfers.order_by('-transfer_date')
        
        transfers_list = []
        total_amount = Decimal('0.00')
        
        for transfer in transfers:
            transfers_list.append({
                'transfer_number': transfer.transfer_number,
                'transfer_date': transfer.transfer_date,
                'from_bank_name': transfer.from_bank.name,
                'to_bank_name': transfer.to_bank.name,
                'amount': transfer.amount,
                'from_currency_code': transfer.from_currency.currency_code,
                'to_currency_code': transfer.to_currency.currency_code,
                'exchange_rate': transfer.exchange_rate,
                'converted_amount': transfer.converted_amount,
                'status': transfer.status,
                'approval_status': transfer.approval_status,
                'description': transfer.description,
                'reference': transfer.reference,
                'created_by': transfer.created_by.username
            })
            total_amount += transfer.amount
        
        return {
            'report_type': 'Pending Transfers Report',
            'approval_status_filter': approval_status,
            'transfers': transfers_list,
            'count': len(transfers_list),
            'total_amount': total_amount
        }

