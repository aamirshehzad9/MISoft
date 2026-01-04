import os
import sys
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

try:
    from accounting import urls
    print("✓ Accounting URLs loaded successfully")
except Exception as e:
    print("✗ Error loading accounting URLs:")
    print(traceback.format_exc())
    sys.exit(1)
