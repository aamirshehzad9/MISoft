"""
Cheque Service
Task 2.2.2: Cheque Service
Module 2.2: Cheque Management System

Handles complete cheque lifecycle management including issuance, clearance,
cancellation, and PDF generation.
"""
from django.db import transaction
from django.utils import timezone
from accounting.models import Cheque
from decimal import Decimal
import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


class ChequeService:
    """Service class for cheque lifecycle management"""

    @staticmethod
    def issue_cheque(cheque_number, cheque_date, bank_account, payee, amount, 
                     voucher, user, is_post_dated=False):
        """
        Issue a new cheque
        
        Args:
            cheque_number: Unique cheque number
            cheque_date: Date on the cheque
            bank_account: Bank account (AccountV2 instance)
            payee: Payee/recipient (BusinessPartner instance)
            amount: Cheque amount
            voucher: Linked voucher (VoucherV2 instance, optional)
            user: User issuing the cheque
            is_post_dated: Whether this is a post-dated cheque
            
        Returns:
            Cheque instance
        """
        with transaction.atomic():
            cheque = Cheque.objects.create(
                cheque_number=cheque_number,
                cheque_date=cheque_date,
                bank_account=bank_account,
                payee=payee,
                amount=amount,
                voucher=voucher,
                status='issued',
                is_post_dated=is_post_dated,
                created_by=user
            )
            
            return cheque

    @staticmethod
    def clear_cheque(cheque, clearance_date):
        """
        Clear a cheque (mark as cleared by bank)
        
        Args:
            cheque: Cheque instance
            clearance_date: Date when cheque was cleared
            
        Returns:
            Updated Cheque instance
            
        Raises:
            ValueError: If cheque is not in 'issued' status
        """
        if cheque.status != 'issued':
            raise ValueError(f"Only issued cheques can be cleared. Current status: {cheque.status}")
        
        with transaction.atomic():
            cheque.status = 'cleared'
            cheque.clearance_date = clearance_date
            cheque.save()
            
            return cheque

    @staticmethod
    def cancel_cheque(cheque, cancelled_date, cancellation_reason):
        """
        Cancel a cheque
        
        Args:
            cheque: Cheque instance
            cancelled_date: Date of cancellation
            cancellation_reason: Reason for cancellation
            
        Returns:
            Updated Cheque instance
            
        Raises:
            ValueError: If cheque is not in 'issued' status or reason is empty
        """
        if cheque.status != 'issued':
            raise ValueError(f"Only issued cheques can be cancelled. Current status: {cheque.status}")
        
        if not cancellation_reason or cancellation_reason.strip() == "":
            raise ValueError("Cancellation reason is required")
        
        with transaction.atomic():
            cheque.status = 'cancelled'
            cheque.cancelled_date = cancelled_date
            cheque.cancellation_reason = cancellation_reason
            cheque.save()
            
            return cheque

    @staticmethod
    def print_cheque(cheque):
        """
        Generate PDF for cheque printing
        
        Args:
            cheque: Cheque instance
            
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = BytesIO()
        
        # Create PDF canvas
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Set up fonts
        p.setFont("Helvetica-Bold", 16)
        
        # Title
        p.drawString(1 * inch, height - 1 * inch, "CHEQUE")
        
        # Cheque details
        p.setFont("Helvetica", 12)
        y_position = height - 1.5 * inch
        
        p.drawString(1 * inch, y_position, f"Cheque Number: {cheque.cheque_number}")
        y_position -= 0.3 * inch
        
        p.drawString(1 * inch, y_position, f"Date: {cheque.cheque_date.strftime('%B %d, %Y')}")
        y_position -= 0.5 * inch
        
        p.drawString(1 * inch, y_position, f"Pay to the Order of:")
        y_position -= 0.3 * inch
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1.5 * inch, y_position, cheque.payee.name)
        y_position -= 0.5 * inch
        
        p.setFont("Helvetica", 12)
        p.drawString(1 * inch, y_position, f"Amount: ${cheque.amount:,.2f}")
        y_position -= 0.3 * inch
        
        # Amount in words (simplified)
        amount_words = ChequeService._amount_to_words(cheque.amount)
        p.drawString(1 * inch, y_position, f"Amount in Words: {amount_words}")
        y_position -= 0.5 * inch
        
        p.drawString(1 * inch, y_position, f"Bank Account: {cheque.bank_account.name}")
        y_position -= 0.3 * inch
        
        p.drawString(1 * inch, y_position, f"Account Code: {cheque.bank_account.code}")
        y_position -= 0.5 * inch
        
        # Signature line
        p.line(5 * inch, y_position, 7 * inch, y_position)
        y_position -= 0.2 * inch
        p.drawString(5.5 * inch, y_position, "Authorized Signature")
        
        # Footer
        p.setFont("Helvetica", 8)
        p.drawString(1 * inch, 0.5 * inch, f"Status: {cheque.get_status_display()}")
        if cheque.is_post_dated:
            p.drawString(3 * inch, 0.5 * inch, "POST-DATED CHEQUE")
        
        # Finalize PDF
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer

    @staticmethod
    def _amount_to_words(amount):
        """
        Convert amount to words (simplified version)
        
        Args:
            amount: Decimal amount
            
        Returns:
            String representation in words
        """
        # Simplified implementation - just return formatted amount
        # In production, use a proper number-to-words library
        return f"{amount:,.2f} Dollars"

    @staticmethod
    def get_post_dated_cheques():
        """
        Get all post-dated cheques that are still issued
        
        Returns:
            QuerySet of Cheque instances
        """
        return Cheque.objects.filter(
            is_post_dated=True,
            status='issued'
        ).order_by('cheque_date')

    @staticmethod
    def get_post_dated_cheques_due_soon(days=7):
        """
        Get post-dated cheques due within specified days
        
        Args:
            days: Number of days to look ahead (default: 7)
            
        Returns:
            QuerySet of Cheque instances
        """
        today = datetime.date.today()
        due_date = today + datetime.timedelta(days=days)
        
        return Cheque.objects.filter(
            is_post_dated=True,
            status='issued',
            cheque_date__lte=due_date,
            cheque_date__gte=today
        ).order_by('cheque_date')

    @staticmethod
    def get_cheques_by_status(status):
        """
        Get cheques by status
        
        Args:
            status: Cheque status ('issued', 'cleared', 'cancelled', 'bounced')
            
        Returns:
            QuerySet of Cheque instances
        """
        return Cheque.objects.filter(status=status).order_by('-cheque_date')

    @staticmethod
    def generate_issued_cheques_register(start_date=None, end_date=None):
        """
        Generate Issued Cheques Register
        Task 2.2.3: Cheque Reports
        
        Lists all issued cheques (including post-dated)
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            dict: Report with list of issued cheques and summary
        """
        cheques = Cheque.objects.filter(status='issued').select_related(
            'bank_account', 'payee', 'voucher'
        )
        
        if start_date:
            cheques = cheques.filter(cheque_date__gte=start_date)
        if end_date:
            cheques = cheques.filter(cheque_date__lte=end_date)
        
        cheques = cheques.order_by('cheque_date')
        
        cheques_list = []
        total_amount = Decimal('0.00')
        
        for cheque in cheques:
            cheques_list.append({
                'cheque_number': cheque.cheque_number,
                'cheque_date': cheque.cheque_date,
                'payee_name': cheque.payee.name,
                'amount': cheque.amount,
                'bank_account_name': cheque.bank_account.name,
                'bank_account_code': cheque.bank_account.code,
                'is_post_dated': cheque.is_post_dated,
                'voucher_number': cheque.voucher.voucher_number if cheque.voucher else None
            })
            total_amount += cheque.amount
        
        return {
            'report_type': 'Issued Cheques Register',
            'start_date': start_date,
            'end_date': end_date,
            'cheques': cheques_list,
            'count': len(cheques_list),
            'total_amount': total_amount
        }

    @staticmethod
    def generate_cancelled_cheques_register(start_date=None, end_date=None):
        """
        Generate Cancelled Cheques Register
        Task 2.2.3: Cheque Reports
        
        Lists all cancelled cheques with cancellation details
        
        Args:
            start_date: Optional start date filter (by cancelled_date)
            end_date: Optional end date filter (by cancelled_date)
            
        Returns:
            dict: Report with list of cancelled cheques and summary
        """
        cheques = Cheque.objects.filter(status='cancelled').select_related(
            'bank_account', 'payee', 'voucher'
        )
        
        if start_date:
            cheques = cheques.filter(cancelled_date__gte=start_date)
        if end_date:
            cheques = cheques.filter(cancelled_date__lte=end_date)
        
        cheques = cheques.order_by('cancelled_date')
        
        cheques_list = []
        total_amount = Decimal('0.00')
        
        for cheque in cheques:
            cheques_list.append({
                'cheque_number': cheque.cheque_number,
                'cheque_date': cheque.cheque_date,
                'payee_name': cheque.payee.name,
                'amount': cheque.amount,
                'bank_account_name': cheque.bank_account.name,
                'bank_account_code': cheque.bank_account.code,
                'cancelled_date': cheque.cancelled_date,
                'cancellation_reason': cheque.cancellation_reason,
                'voucher_number': cheque.voucher.voucher_number if cheque.voucher else None
            })
            total_amount += cheque.amount
        
        return {
            'report_type': 'Cancelled Cheques Register',
            'start_date': start_date,
            'end_date': end_date,
            'cheques': cheques_list,
            'count': len(cheques_list),
            'total_amount': total_amount
        }

    @staticmethod
    def generate_post_dated_cheques_report(due_within_days=None):
        """
        Generate Post-Dated Cheques Report
        Task 2.2.3: Cheque Reports
        
        Lists all post-dated cheques
        
        Args:
            due_within_days: Optional filter for cheques due within N days
            
        Returns:
            dict: Report with list of post-dated cheques and summary
        """
        cheques = Cheque.objects.filter(
            is_post_dated=True,
            status='issued'
        ).select_related('bank_account', 'payee', 'voucher')
        
        if due_within_days is not None:
            today = datetime.date.today()
            due_date = today + datetime.timedelta(days=due_within_days)
            cheques = cheques.filter(
                cheque_date__lte=due_date,
                cheque_date__gte=today
            )
        
        cheques = cheques.order_by('cheque_date')
        
        cheques_list = []
        total_amount = Decimal('0.00')
        
        for cheque in cheques:
            days_until_due = (cheque.cheque_date - datetime.date.today()).days
            
            cheques_list.append({
                'cheque_number': cheque.cheque_number,
                'cheque_date': cheque.cheque_date,
                'payee_name': cheque.payee.name,
                'amount': cheque.amount,
                'bank_account_name': cheque.bank_account.name,
                'bank_account_code': cheque.bank_account.code,
                'is_post_dated': cheque.is_post_dated,
                'days_until_due': days_until_due,
                'voucher_number': cheque.voucher.voucher_number if cheque.voucher else None
            })
            total_amount += cheque.amount
        
        return {
            'report_type': 'Post-Dated Cheques Report',
            'due_within_days': due_within_days,
            'cheques': cheques_list,
            'count': len(cheques_list),
            'total_amount': total_amount
        }

    @staticmethod
    def generate_clearance_status_report(start_date=None, end_date=None):
        """
        Generate Cheque Clearance Status Report
        Task 2.2.3: Cheque Reports
        
        Comprehensive report showing all cheques grouped by status
        
        Args:
            start_date: Optional start date filter (by cheque_date)
            end_date: Optional end date filter (by cheque_date)
            
        Returns:
            dict: Report with cheques grouped by status and summary statistics
        """
        # Base queryset
        all_cheques = Cheque.objects.select_related('bank_account', 'payee', 'voucher')
        
        if start_date:
            all_cheques = all_cheques.filter(cheque_date__gte=start_date)
        if end_date:
            all_cheques = all_cheques.filter(cheque_date__lte=end_date)
        
        # Get cheques by status
        issued_cheques = all_cheques.filter(status='issued').order_by('cheque_date')
        cleared_cheques = all_cheques.filter(status='cleared').order_by('clearance_date')
        cancelled_cheques = all_cheques.filter(status='cancelled').order_by('cancelled_date')
        bounced_cheques = all_cheques.filter(status='bounced').order_by('cheque_date')
        
        # Helper function to format cheque data
        def format_cheque(cheque):
            return {
                'cheque_number': cheque.cheque_number,
                'cheque_date': cheque.cheque_date,
                'payee_name': cheque.payee.name,
                'amount': cheque.amount,
                'bank_account_name': cheque.bank_account.name,
                'status': cheque.status
            }
        
        # Calculate totals
        issued_amount = sum(c.amount for c in issued_cheques)
        cleared_amount = sum(c.amount for c in cleared_cheques)
        cancelled_amount = sum(c.amount for c in cancelled_cheques)
        bounced_amount = sum(c.amount for c in bounced_cheques)
        
        return {
            'report_type': 'Cheque Clearance Status Report',
            'start_date': start_date,
            'end_date': end_date,
            'issued_cheques': [format_cheque(c) for c in issued_cheques],
            'cleared_cheques': [format_cheque(c) for c in cleared_cheques],
            'cancelled_cheques': [format_cheque(c) for c in cancelled_cheques],
            'bounced_cheques': [format_cheque(c) for c in bounced_cheques],
            'summary': {
                'total_issued': issued_cheques.count(),
                'total_cleared': cleared_cheques.count(),
                'total_cancelled': cancelled_cheques.count(),
                'total_bounced': bounced_cheques.count(),
                'total_cheques': all_cheques.count(),
                'issued_amount': issued_amount,
                'cleared_amount': cleared_amount,
                'cancelled_amount': cancelled_amount,
                'bounced_amount': bounced_amount,
                'total_amount': issued_amount + cleared_amount + cancelled_amount + bounced_amount
            }
        }

