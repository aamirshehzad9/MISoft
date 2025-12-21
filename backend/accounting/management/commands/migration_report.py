"""
Management command to generate comprehensive migration reports

Usage:
    python manage.py migration_report [--format=text|json|html] [--output=filename]

This command generates detailed reports about the migration status,
data integrity, and system health.
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Sum, Q
from decimal import Decimal
from accounting.models import (
    ChartOfAccounts, AccountV2, JournalEntry, VoucherV2,
    TaxCode, TaxMasterV2, CurrencyV2
)
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Generate comprehensive migration reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='text',
            choices=['text', 'json', 'html'],
            help='Output format (text, json, or html)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output filename (optional)',
        )
        parser.add_argument(
            '--include-details',
            action='store_true',
            help='Include detailed account listings',
        )

    def handle(self, *args, **options):
        self.format = options['format']
        self.output_file = options['output']
        self.include_details = options['include_details']
        
        # Generate report data
        report_data = self.generate_report_data()
        
        # Format and output report
        if self.format == 'text':
            output = self.format_text_report(report_data)
        elif self.format == 'json':
            output = self.format_json_report(report_data)
        elif self.format == 'html':
            output = self.format_html_report(report_data)
        
        # Output to file or stdout
        if self.output_file:
            with open(self.output_file, 'w') as f:
                f.write(output)
            self.stdout.write(self.style.SUCCESS(f'Report saved to: {self.output_file}'))
        else:
            self.stdout.write(output)

    def generate_report_data(self):
        """Generate all report data"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'migration_status': self.get_migration_status(),
            'account_statistics': self.get_account_statistics(),
            'balance_summary': self.get_balance_summary(),
            'data_quality': self.get_data_quality_metrics(),
            'system_health': self.get_system_health(),
        }
        
        if self.include_details:
            data['account_details'] = self.get_account_details()
        
        return data

    def get_migration_status(self):
        """Get overall migration status"""
        legacy_count = ChartOfAccounts.objects.count()
        v2_total = AccountV2.objects.count()
        v2_migrated = AccountV2.objects.filter(migrated_from_legacy__isnull=False).count()
        v2_new = v2_total - v2_migrated
        
        migration_percentage = (v2_migrated / legacy_count * 100) if legacy_count > 0 else 0
        
        return {
            'legacy_accounts': legacy_count,
            'v2_total_accounts': v2_total,
            'v2_migrated_accounts': v2_migrated,
            'v2_new_accounts': v2_new,
            'migration_percentage': round(migration_percentage, 2),
            'migration_complete': legacy_count == v2_migrated,
        }

    def get_account_statistics(self):
        """Get account statistics"""
        stats = {}
        
        # Legacy statistics
        stats['legacy'] = {
            'total': ChartOfAccounts.objects.count(),
            'active': ChartOfAccounts.objects.filter(is_active=True).count(),
            'inactive': ChartOfAccounts.objects.filter(is_active=False).count(),
            'headers': ChartOfAccounts.objects.filter(is_header=True).count(),
            'ledgers': ChartOfAccounts.objects.filter(is_header=False).count(),
        }
        
        # V2 statistics
        stats['v2'] = {
            'total': AccountV2.objects.count(),
            'active': AccountV2.objects.filter(is_active=True).count(),
            'inactive': AccountV2.objects.filter(is_active=False).count(),
            'groups': AccountV2.objects.filter(is_group=True).count(),
            'ledgers': AccountV2.objects.filter(is_group=False).count(),
        }
        
        # By account type
        stats['by_type'] = {}
        for acc_type in ['asset', 'liability', 'equity', 'revenue', 'expense']:
            stats['by_type'][acc_type] = AccountV2.objects.filter(
                account_type=acc_type
            ).count()
        
        return stats

    def get_balance_summary(self):
        """Get balance summary"""
        legacy_balance = ChartOfAccounts.objects.aggregate(
            total=Sum('opening_balance')
        )['total'] or Decimal('0.00')
        
        v2_balance = AccountV2.objects.aggregate(
            opening=Sum('opening_balance'),
            current=Sum('current_balance')
        )
        
        return {
            'legacy_opening_balance': float(legacy_balance),
            'v2_opening_balance': float(v2_balance['opening'] or Decimal('0.00')),
            'v2_current_balance': float(v2_balance['current'] or Decimal('0.00')),
            'balance_difference': float(abs(legacy_balance - (v2_balance['opening'] or Decimal('0.00')))),
        }

    def get_data_quality_metrics(self):
        """Get data quality metrics"""
        metrics = {}
        
        # Check for missing data
        metrics['missing_codes'] = AccountV2.objects.filter(
            Q(code__isnull=True) | Q(code='')
        ).count()
        
        metrics['missing_names'] = AccountV2.objects.filter(
            Q(name__isnull=True) | Q(name='')
        ).count()
        
        # Check for duplicates
        from django.db.models import Count
        duplicates = AccountV2.objects.values('code').annotate(
            count=Count('code')
        ).filter(count__gt=1)
        metrics['duplicate_codes'] = duplicates.count()
        
        # Check hierarchy
        orphaned = AccountV2.objects.filter(
            parent__isnull=False
        ).exclude(
            parent__in=AccountV2.objects.all()
        )
        metrics['orphaned_accounts'] = orphaned.count()
        
        # Overall quality score
        total_issues = sum([
            metrics['missing_codes'],
            metrics['missing_names'],
            metrics['duplicate_codes'],
            metrics['orphaned_accounts']
        ])
        
        total_accounts = AccountV2.objects.count()
        quality_score = 100 - (total_issues / total_accounts * 100) if total_accounts > 0 else 100
        metrics['quality_score'] = round(quality_score, 2)
        
        return metrics

    def get_system_health(self):
        """Get system health indicators"""
        health = {}
        
        # Database connectivity
        try:
            AccountV2.objects.count()
            health['database'] = 'healthy'
        except Exception as e:
            health['database'] = f'error: {e}'
        
        # Migration tracking
        health['migration_tracking'] = AccountV2.objects.filter(
            migrated_from_legacy__isnull=False
        ).exists()
        
        # V2 models available
        health['v2_models_available'] = {
            'AccountV2': AccountV2.objects.exists(),
            'CurrencyV2': CurrencyV2.objects.model._meta.db_table is not None,
            'TaxMasterV2': TaxMasterV2.objects.model._meta.db_table is not None,
        }
        
        return health

    def get_account_details(self):
        """Get detailed account listings"""
        details = []
        
        for account in AccountV2.objects.all()[:100]:  # Limit to 100 for performance
            details.append({
                'code': account.code,
                'name': account.name,
                'type': account.account_type,
                'group': account.account_group,
                'balance': float(account.current_balance),
                'is_migrated': account.migrated_from_legacy is not None,
            })
        
        return details

    def format_text_report(self, data):
        """Format report as text"""
        lines = []
        lines.append('=' * 80)
        lines.append('MIGRATION REPORT')
        lines.append('=' * 80)
        lines.append(f"Generated: {data['generated_at']}")
        lines.append('')
        
        # Migration Status
        lines.append('MIGRATION STATUS')
        lines.append('-' * 80)
        status = data['migration_status']
        lines.append(f"Legacy Accounts: {status['legacy_accounts']}")
        lines.append(f"V2 Total Accounts: {status['v2_total_accounts']}")
        lines.append(f"V2 Migrated: {status['v2_migrated_accounts']}")
        lines.append(f"V2 New: {status['v2_new_accounts']}")
        lines.append(f"Migration Progress: {status['migration_percentage']}%")
        lines.append(f"Migration Complete: {'Yes' if status['migration_complete'] else 'No'}")
        lines.append('')
        
        # Account Statistics
        lines.append('ACCOUNT STATISTICS')
        lines.append('-' * 80)
        stats = data['account_statistics']
        lines.append(f"Legacy Total: {stats['legacy']['total']}")
        lines.append(f"  Active: {stats['legacy']['active']}")
        lines.append(f"  Headers: {stats['legacy']['headers']}")
        lines.append(f"  Ledgers: {stats['legacy']['ledgers']}")
        lines.append('')
        lines.append(f"V2 Total: {stats['v2']['total']}")
        lines.append(f"  Active: {stats['v2']['active']}")
        lines.append(f"  Groups: {stats['v2']['groups']}")
        lines.append(f"  Ledgers: {stats['v2']['ledgers']}")
        lines.append('')
        lines.append('By Account Type:')
        for acc_type, count in stats['by_type'].items():
            lines.append(f"  {acc_type.capitalize()}: {count}")
        lines.append('')
        
        # Balance Summary
        lines.append('BALANCE SUMMARY')
        lines.append('-' * 80)
        balance = data['balance_summary']
        lines.append(f"Legacy Opening Balance: {balance['legacy_opening_balance']}")
        lines.append(f"V2 Opening Balance: {balance['v2_opening_balance']}")
        lines.append(f"V2 Current Balance: {balance['v2_current_balance']}")
        lines.append(f"Balance Difference: {balance['balance_difference']}")
        lines.append('')
        
        # Data Quality
        lines.append('DATA QUALITY METRICS')
        lines.append('-' * 80)
        quality = data['data_quality']
        lines.append(f"Quality Score: {quality['quality_score']}%")
        lines.append(f"Missing Codes: {quality['missing_codes']}")
        lines.append(f"Missing Names: {quality['missing_names']}")
        lines.append(f"Duplicate Codes: {quality['duplicate_codes']}")
        lines.append(f"Orphaned Accounts: {quality['orphaned_accounts']}")
        lines.append('')
        
        # System Health
        lines.append('SYSTEM HEALTH')
        lines.append('-' * 80)
        health = data['system_health']
        lines.append(f"Database: {health['database']}")
        lines.append(f"Migration Tracking: {'Enabled' if health['migration_tracking'] else 'Disabled'}")
        lines.append('')
        
        lines.append('=' * 80)
        
        return '\n'.join(lines)

    def format_json_report(self, data):
        """Format report as JSON"""
        return json.dumps(data, indent=2, default=str)

    def format_html_report(self, data):
        """Format report as HTML"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Migration Report - {data['generated_at']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .metric {{ background-color: #e8f4f8; padding: 10px; margin: 10px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Migration Report</h1>
    <p>Generated: {data['generated_at']}</p>
    
    <h2>Migration Status</h2>
    <div class="metric">
        <p><strong>Migration Progress:</strong> {data['migration_status']['migration_percentage']}%</p>
        <p><strong>Legacy Accounts:</strong> {data['migration_status']['legacy_accounts']}</p>
        <p><strong>V2 Migrated:</strong> {data['migration_status']['v2_migrated_accounts']}</p>
        <p><strong>V2 New:</strong> {data['migration_status']['v2_new_accounts']}</p>
    </div>
    
    <h2>Data Quality</h2>
    <div class="metric">
        <p><strong>Quality Score:</strong> {data['data_quality']['quality_score']}%</p>
        <p><strong>Issues:</strong> {data['data_quality']['missing_codes'] + data['data_quality']['duplicate_codes']} total</p>
    </div>
    
    <h2>Balance Summary</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Amount</th>
        </tr>
        <tr>
            <td>Legacy Opening Balance</td>
            <td>{data['balance_summary']['legacy_opening_balance']}</td>
        </tr>
        <tr>
            <td>V2 Opening Balance</td>
            <td>{data['balance_summary']['v2_opening_balance']}</td>
        </tr>
        <tr>
            <td>V2 Current Balance</td>
            <td>{data['balance_summary']['v2_current_balance']}</td>
        </tr>
    </table>
</body>
</html>
"""
        return html
