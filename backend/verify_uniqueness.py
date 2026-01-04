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
    print("Setting up uniqueness test...")
    # Cleanup
    ReferenceDefinition.objects.filter(field_key__in=['unique_po', 'po_num']).delete()
    VoucherV2.objects.filter(voucher_number__startswith='TEST-UQ').delete()
    
    # 1. Create Definition
    ReferenceDefinition.objects.create(
        model_name='voucher', 
        field_key='unique_po', 
        data_type='text', 
        is_required=True, 
        is_unique=True,
        field_label='Unique PO'
    )
    
    # 2. Create Voucher 1
    v1 = VoucherV2(
        voucher_number='TEST-UQ-1',
        voucher_type='JE', 
        voucher_date='2025-01-01',
        user_references={'unique_po': 'U123'},
        total_amount=100
    )
    v1.clean()
    v1.save()
    print("V1 created successfully.")
    
    # 3. Create Voucher 2 with SAME value
    v2 = VoucherV2(
        voucher_number='TEST-UQ-2',
        voucher_type='JE', 
        voucher_date='2025-01-01',
        user_references={'unique_po': 'U123'},
        total_amount=100
    )
    
    try:
        print("Attempting to create V2 with duplicate value...")
        v2.clean()
        print("FAILED: Duplicate value accepted!")
    except ValidationError as e:
        print(f"SUCCESS: Caught Expected Duplicate Error: {e}")

    # 4. Create Voucher 2 with DIFFERENT value
    v2.user_references['unique_po'] = 'U456'
    v2.clean()
    v2.save()
    print("V2 created successfully with different value.")
    
    # 5. Update V1 with SAME value (should pass)
    v1.clean()
    print("V1 self-update validation passed.")
    
except Exception as e:
    print(f"ERROR: Unexpected error: {e}")
    import traceback
    traceback.print_exc()
