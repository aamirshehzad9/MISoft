"""
Django Management Command for Automated Month-End FX Revaluation

This command can be scheduled to run automatically on the last day of each month
to revalue all foreign currency balances and post unrealized FX gain/loss.

Usage:
    python manage.py run_monthend_fx_revaluation
    python manage.py run_monthend_fx_revaluation --entity=HQ
    python manage.py run_monthend_fx_revaluation --auto-post --send-email
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import date
from decimal import Decimal

from accounting.models import Entity
from accounting.services import ExchangeGainLossService


class Command(BaseCommand):
    help = 'Run month-end FX revaluation for all entities'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--entity',
            type=str,
            help='Specific entity code to revalue (optional, defaults to all active entities)'
        )
        
        parser.add_argument(
            '--auto-post',
            action='store_true',
            help='Automatically post FX revaluation entries'
        )
        
        parser.add_argument(
            '--send-email',
            action='store_true',
            help='Send email notification after revaluation'
        )
        
        parser.add_argument(
            '--revaluation-date',
            type=str,
            help='Revaluation date (YYYY-MM-DD), defaults to today'
        )
        
        parser.add_argument(
            '--create-reversal',
            action='store_true',
            help='Create reversal entries for next period'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('MONTH-END FX REVALUATION'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Get revaluation date
        if options['revaluation_date']:
            try:
                revaluation_date = date.fromisoformat(options['revaluation_date'])
            except ValueError:
                raise CommandError('Invalid date format. Use YYYY-MM-DD')
        else:
            revaluation_date = date.today()
        
        self.stdout.write(f'Revaluation Date: {revaluation_date}')
        self.stdout.write('')
        
        # Get entities to revalue
        if options['entity']:
            try:
                entities = [Entity.objects.get(entity_code=options['entity'], is_active=True)]
                self.stdout.write(f'Revaluing single entity: {options["entity"]}')
            except Entity.DoesNotExist:
                raise CommandError(f'Entity {options["entity"]} not found or inactive')
        else:
            entities = Entity.objects.filter(is_active=True)
            self.stdout.write(f'Revaluing all active entities: {entities.count()} entities')
        
        self.stdout.write('')
        
        # Initialize service
        service = ExchangeGainLossService()
        
        # Track results
        results = []
        total_gain = Decimal('0.00')
        total_loss = Decimal('0.00')
        total_vouchers_created = 0
        
        # Process each entity
        for entity in entities:
            self.stdout.write(self.style.HTTP_INFO(f'\nProcessing: {entity.entity_code} - {entity.entity_name}'))
            self.stdout.write('-' * 70)
            
            try:
                # Revalue monetary items
                result = service.revalue_monetary_items(
                    entity=entity,
                    revaluation_date=revaluation_date,
                    auto_post=options['auto_post']
                )
                
                # Display results
                self.stdout.write(f'  Accounts Revalued: {result["accounts_revalued"]}')
                self.stdout.write(f'  Total Gain: {result["total_gain"]:,.2f}')
                self.stdout.write(f'  Total Loss: {result["total_loss"]:,.2f}')
                self.stdout.write(f'  Net FX Gain/Loss: {result["net_fx_gain_loss"]:,.2f}')
                
                if result['voucher_created']:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Voucher Created: {result["voucher_number"]}'))
                    total_vouchers_created += 1
                    
                    # Create reversal if requested
                    if options['create_reversal']:
                        from accounting.models import VoucherV2
                        voucher = VoucherV2.objects.get(voucher_number=result['voucher_number'])
                        reversal_info = service.schedule_automatic_reversal(
                            entity=entity,
                            revaluation_voucher=voucher,
                            create_immediately=True
                        )
                        self.stdout.write(self.style.SUCCESS(
                            f'  ✓ Reversal Scheduled: {reversal_info["reversal_voucher_number"]} '
                            f'for {reversal_info["scheduled_reversal_date"]}'
                        ))
                else:
                    self.stdout.write('  No voucher created (zero FX gain/loss)')
                
                # Accumulate totals
                total_gain += result['total_gain']
                total_loss += result['total_loss']
                
                results.append({
                    'entity': entity,
                    'result': result,
                    'status': 'success'
                })
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error: {str(e)}'))
                results.append({
                    'entity': entity,
                    'error': str(e),
                    'status': 'error'
                })
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(f'Entities Processed: {len(entities)}')
        self.stdout.write(f'Successful: {sum(1 for r in results if r["status"] == "success")}')
        self.stdout.write(f'Errors: {sum(1 for r in results if r["status"] == "error")}')
        self.stdout.write(f'Vouchers Created: {total_vouchers_created}')
        self.stdout.write(f'Total Gain: {total_gain:,.2f}')
        self.stdout.write(f'Total Loss: {total_loss:,.2f}')
        self.stdout.write(f'Net FX Gain/Loss: {(total_gain - total_loss):,.2f}')
        self.stdout.write('')
        
        # Send email notification if requested
        if options['send_email']:
            self._send_email_notification(results, revaluation_date, total_gain, total_loss)
            self.stdout.write(self.style.SUCCESS('✓ Email notification sent'))
        
        self.stdout.write(self.style.SUCCESS('Month-end FX revaluation completed!'))
    
    def _send_email_notification(self, results, revaluation_date, total_gain, total_loss):
        """Send email notification to accountant"""
        
        # Build email content
        subject = f'Month-End FX Revaluation Report - {revaluation_date}'
        
        message = f"""
Month-End FX Revaluation Report
Date: {revaluation_date}

SUMMARY:
========
Entities Processed: {len(results)}
Successful: {sum(1 for r in results if r['status'] == 'success')}
Errors: {sum(1 for r in results if r['status'] == 'error')}

Total Gain: {total_gain:,.2f}
Total Loss: {total_loss:,.2f}
Net FX Gain/Loss: {(total_gain - total_loss):,.2f}

DETAILS:
========
"""
        
        for item in results:
            entity = item['entity']
            if item['status'] == 'success':
                result = item['result']
                message += f"""
{entity.entity_code} - {entity.entity_name}:
  Accounts Revalued: {result['accounts_revalued']}
  Net FX Gain/Loss: {result['net_fx_gain_loss']:,.2f}
  Voucher: {result.get('voucher_number', 'N/A')}
"""
            else:
                message += f"""
{entity.entity_code} - {entity.entity_name}:
  Status: ERROR
  Error: {item['error']}
"""
        
        message += """
This is an automated notification from MISoft ERP.
Please review the FX revaluation entries in the system.
"""
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ACCOUNTANT_EMAIL] if hasattr(settings, 'ACCOUNTANT_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Email notification failed: {str(e)}'))
