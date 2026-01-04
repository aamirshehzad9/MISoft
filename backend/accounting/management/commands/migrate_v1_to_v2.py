"""
Django Management Command to run data migration
Usage: python manage.py migrate_v1_to_v2
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounting.migration_service import DataMigrationService

User = get_user_model()


class Command(BaseCommand):
    help = 'Migrate legacy V1 data to V2 IFRS-compliant models'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run migration in dry-run mode (no actual changes)',
        )
        parser.add_argument(
            '--accounts-only',
            action='store_true',
            help='Migrate accounts only',
        )
        parser.add_argument(
            '--entries-only',
            action='store_true',
            help='Migrate journal entries only',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Data Migration: V1 → V2'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        # Get superuser for migration
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(self.style.ERROR('No superuser found! Please create one first.'))
            return
        
        self.stdout.write(f'Migration will be performed by: {user.username}')
        
        # Create migration service
        migration_service = DataMigrationService(user=user)
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN MODE - No actual changes will be made\n'))
        
        # Run migration
        if options['accounts_only']:
            self.stdout.write('Migrating accounts only...\n')
            result = migration_service.migrate_accounts()
        elif options['entries_only']:
            self.stdout.write('Migrating journal entries only...\n')
            result = migration_service.migrate_journal_entries()
        else:
            self.stdout.write('Running full migration...\n')
            result = migration_service.run_full_migration()
        
        # Display results
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('MIGRATION COMPLETED'))
        self.stdout.write('=' * 80)
        
        if 'accounts' in result:
            self.stdout.write(f"Accounts: {result['accounts']['migrated']}/{result['accounts']['total']} migrated")
        if 'entries' in result:
            self.stdout.write(f"Entries: {result['entries']['migrated']}/{result['entries']['total']} migrated")
        if 'errors' in result:
            if result['errors']:
                self.stdout.write(self.style.ERROR(f"Errors: {len(result['errors'])}"))
                for error in result['errors'][:5]:  # Show first 5 errors
                    self.stdout.write(self.style.ERROR(f"  - {error}"))
            else:
                self.stdout.write(self.style.SUCCESS('✓ No errors!'))
        
        self.stdout.write('=' * 80)
