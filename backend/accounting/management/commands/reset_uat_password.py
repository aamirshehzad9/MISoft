from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Reset UAT admin password'

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            user = User.objects.get(username='uat_admin')
            user.set_password('uat_password_123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Successfully reset password for uat_admin'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User uat_admin does not exist'))
