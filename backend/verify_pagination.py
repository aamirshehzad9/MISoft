"""
Verification script for DRF Pagination
Tests that pagination is properly configured and working
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from accounting.views import AssetCategoryViewSet, FixedAssetViewSet

User = get_user_model()

def test_pagination():
    """Test that pagination is working correctly"""
    
    # Get a user for authentication
    user = User.objects.first()
    if not user:
        print("❌ No users found. Please create a user first.")
        return
    
    # Create request factory
    factory = APIRequestFactory()
    
    # Test AssetCategory pagination
    print("\n" + "="*60)
    print("Testing AssetCategory Pagination")
    print("="*60)
    
    request = factory.get('/api/accounting/asset-categories/')
    force_authenticate(request, user=user)
    
    view = AssetCategoryViewSet.as_view({'get': 'list'})
    response = view(request)
    
    print(f"✅ Response status: {response.status_code}")
    print(f"✅ Response type: {type(response.data)}")
    
    if isinstance(response.data, dict):
        print(f"✅ Has 'results' key: {'results' in response.data}")
        print(f"✅ Has 'count' key: {'count' in response.data}")
        print(f"✅ Has 'next' key: {'next' in response.data}")
        print(f"✅ Has 'previous' key: {'previous' in response.data}")
        
        if 'results' in response.data:
            print(f"✅ Number of results: {len(response.data['results'])}")
            print(f"✅ Total count: {response.data.get('count', 'N/A')}")
    else:
        print(f"❌ Response is not paginated (type: {type(response.data)})")
    
    # Test FixedAsset pagination
    print("\n" + "="*60)
    print("Testing FixedAsset Pagination")
    print("="*60)
    
    request = factory.get('/api/accounting/fixed-assets/')
    force_authenticate(request, user=user)
    
    view = FixedAssetViewSet.as_view({'get': 'list'})
    response = view(request)
    
    print(f"✅ Response status: {response.status_code}")
    print(f"✅ Response type: {type(response.data)}")
    
    if isinstance(response.data, dict):
        print(f"✅ Has 'results' key: {'results' in response.data}")
        print(f"✅ Has 'count' key: {'count' in response.data}")
        print(f"✅ Has 'next' key: {'next' in response.data}")
        print(f"✅ Has 'previous' key: {'previous' in response.data}")
        
        if 'results' in response.data:
            print(f"✅ Number of results: {len(response.data['results'])}")
            print(f"✅ Total count: {response.data.get('count', 'N/A')}")
    else:
        print(f"❌ Response is not paginated (type: {type(response.data)})")
    
    print("\n" + "="*60)
    print("✅ Pagination Verification Complete!")
    print("="*60)

if __name__ == '__main__':
    test_pagination()
