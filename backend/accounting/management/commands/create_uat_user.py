from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Create UAT admin user'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(username='uat_admin').exists():
            User.objects.create_superuser('uat_admin', 'uat@misoft.com', 'uat_password_123')
            self.stdout.write(self.style.SUCCESS('Successfully created uat_admin'))
        else:
            self.stdout.write(self.style.SUCCESS('uat_admin already exists'))
