import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounting.models import ReferenceDefinition, VoucherV2
from django.core.exceptions import ValidationError

try:
    print("Setting up validation test...")
    # Cleanup previous run
    ReferenceDefinition.objects.filter(field_key='po_num').delete()
    
    ReferenceDefinition.objects.create(
        model_name='voucher', 
        field_key='po_num', 
        data_type='number', 
        is_required=True, 
        field_label='PO Number'
    )
    
    v = VoucherV2(
        user_references={'po_num': 'abc'}, 
        voucher_type='JE', 
        voucher_date='2025-01-01'
    )
    
    print("Attempting to validate invalid data ('abc' for number field)...")
    v.clean()
    print("FAILED: Validation passed but should have failed.")
    
except ValidationError as e:
    print(f"SUCCESS: Caught Expected Error: {e}")
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
    import traceback
    traceback.print_exc()
