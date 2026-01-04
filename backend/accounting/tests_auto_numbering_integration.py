"""
Unit Tests for Auto-Numbering Integration with Models

Tests cover:
- VoucherV2 auto-numbering
- Manual number override
- Entity-specific numbering
- Fallback numbering
- Integration with NumberingService

Target: 100% pass rate
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date

from accounting.models import VoucherV2, NumberingScheme, Entity, CurrencyV2, BusinessPartner
from accounting.services import NumberingService

User = get_user_model()


class VoucherAutoNumberingTestCase(TestCase):
    """Test auto-numbering integration with VoucherV2"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create currency
        self.usd = CurrencyV2.objects.create(
            currency_code='USD',
            currency_name='US Dollar',
            symbol='$'
        )
        
        # Create numbering scheme for journal entries
        self.journal_scheme = NumberingScheme.objects.create(
            scheme_name='Journal Entry Numbering',
            document_type='journal',
            prefix='JE',
            date_format='YYYY',
            separator='-',
            padding=4,
            reset_frequency='yearly',
            created_by=self.user
        )
        
        # Create numbering scheme for invoices
        self.invoice_scheme = NumberingScheme.objects.create(
            scheme_name='Invoice Numbering',
            document_type='invoice',
            prefix='INV',
            date_format='YYYYMM',
            separator='-',
            padding=5,
            reset_frequency='monthly',
            created_by=self.user
        )
    
    def test_voucher_auto_numbering_journal(self):
        """Test automatic number generation for journal entry"""
        voucher = VoucherV2.objects.create(
            voucher_type='JE',
            voucher_date=date.today(),
            total_amount=1000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        # Should have auto-generated number
        self.assertIsNotNone(voucher.voucher_number)
        current_year = date.today().year
        self.assertTrue(voucher.voucher_number.startswith(f'JE-{current_year}'))
    
    def test_voucher_auto_numbering_invoice(self):
        """Test automatic number generation for sales invoice"""
        voucher = VoucherV2.objects.create(
            voucher_type='SI',
            voucher_date=date.today(),
            total_amount=5000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        # Should have auto-generated number
        self.assertIsNotNone(voucher.voucher_number)
        today = date.today()
        expected_prefix = f'INV-{today.year}{today.month:02d}'
        self.assertTrue(voucher.voucher_number.startswith(expected_prefix))
    
    def test_voucher_manual_number_override(self):
        """Test that manual number is preserved"""
        manual_number = 'MANUAL-001'
        
        voucher = VoucherV2.objects.create(
            voucher_number=manual_number,
            voucher_type='JE',
            voucher_date=date.today(),
            total_amount=1000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        # Should keep manual number
        self.assertEqual(voucher.voucher_number, manual_number)
    
    def test_voucher_sequential_numbering(self):
        """Test that vouchers get sequential numbers"""
        voucher1 = VoucherV2.objects.create(
            voucher_type='JE',
            voucher_date=date.today(),
            total_amount=1000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        voucher2 = VoucherV2.objects.create(
            voucher_type='JE',
            voucher_date=date.today(),
            total_amount=2000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        voucher3 = VoucherV2.objects.create(
            voucher_type='JE',
            voucher_date=date.today(),
            total_amount=3000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        # Extract sequence numbers
        seq1 = voucher1.voucher_number.split('-')[-1]
        seq2 = voucher2.voucher_number.split('-')[-1]
        seq3 = voucher3.voucher_number.split('-')[-1]
        
        # Should be sequential
        self.assertEqual(int(seq1) + 1, int(seq2))
        self.assertEqual(int(seq2) + 1, int(seq3))
    
    def test_voucher_fallback_numbering(self):
        """Test fallback numbering when no scheme exists"""
        # Create voucher with type that has no scheme
        voucher = VoucherV2.objects.create(
            voucher_type='CPV',  # Cash Payment Voucher - maps to 'payment' but no scheme exists
            voucher_date=date.today(),
            total_amount=500.00,
            currency=self.usd,
            created_by=self.user
        )
        
        # Should have fallback number
        self.assertIsNotNone(voucher.voucher_number)
        self.assertTrue(voucher.voucher_number.startswith('CPV-'))
    
    def test_voucher_different_types_different_sequences(self):
        """Test that different voucher types have different sequences"""
        journal = VoucherV2.objects.create(
            voucher_type='JE',
            voucher_date=date.today(),
            total_amount=1000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        invoice = VoucherV2.objects.create(
            voucher_type='SI',
            voucher_date=date.today(),
            total_amount=2000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        # Should have different prefixes
        self.assertTrue(journal.voucher_number.startswith('JE-'))
        self.assertTrue(invoice.voucher_number.startswith('INV-'))
    
    def test_voucher_update_preserves_number(self):
        """Test that updating voucher preserves the number"""
        voucher = VoucherV2.objects.create(
            voucher_type='JE',
            voucher_date=date.today(),
            total_amount=1000.00,
            currency=self.usd,
            created_by=self.user
        )
        
        original_number = voucher.voucher_number
        
        # Update voucher
        voucher.total_amount = 1500.00
        voucher.save()
        
        # Number should remain the same
        self.assertEqual(voucher.voucher_number, original_number)
