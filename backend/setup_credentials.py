"""
MISoft Standard Credentials Setup
Creates exactly 2 user accounts for the system
"""
from accounts.models import CustomUser

# Remove all test users, keep only 2 standard accounts
print("=== Cleaning up test users ===")
CustomUser.objects.filter(username__startswith='testuser_').delete()
print("Test users removed")

# Ensure we have exactly 2 users: admin and user
print("\n=== Setting up standard credentials ===")

# 1. Admin account
admin, created = CustomUser.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@misoft.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)
if created or not admin.check_password('admin123'):
    admin.set_password('admin123')
    admin.save()
    print("✓ Admin account created/updated")
else:
    print("✓ Admin account exists")

# 2. Regular user account
user, created = CustomUser.objects.get_or_create(
    username='user',
    defaults={
        'email': 'user@misoft.com',
        'is_staff': False,
        'is_superuser': False,
        'is_active': True
    }
)
if created or not user.check_password('user123'):
    user.set_password('user123')
    user.save()
    print("✓ User account created/updated")
else:
    print("✓ User account exists")

# Remove other accounts except these 2
print("\n=== Removing unnecessary accounts ===")
CustomUser.objects.exclude(username__in=['admin', 'user']).delete()

print("\n=== FINAL CREDENTIALS ===")
print("1. Admin Account:")
print("   Username: admin")
print("   Password: admin123")
print("   Role: Administrator (Full Access)")
print("\n2. User Account:")
print("   Username: user")
print("   Password: user123")
print("   Role: Regular User")

print(f"\nTotal active users: {CustomUser.objects.count()}")
