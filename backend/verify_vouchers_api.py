import requests
import json
from decouple import config

# Use environment variable for base URL
BASE_URL = config('BACKEND_URL', default='http://localhost:8000') + '/api'
AUTH_URL = f'{BASE_URL}/auth/login/'
VOUCHERS_URL = f'{BASE_URL}/accounting/vouchers-v2/'
ACCOUNTS_URL = f'{BASE_URL}/accounting/accounts-v2/hierarchy/'

def get_token():
    # Use environment variables for test credentials
    username = config('TEST_USERNAME', default='uat_admin')
    password = config('TEST_PASSWORD', default='uat_password_123')
    
    response = requests.post(AUTH_URL, json={'username': username, 'password': password})
    if response.status_code == 200:
        return response.json()['access']
    raise Exception(f"Login failed: {response.text}")


def get_account_ids(headers):
    response = requests.get(ACCOUNTS_URL, headers=headers)
    if response.status_code == 200:
        accounts = response.json()
        # Find a cash account and an equity/capital account for testing
        cash_acc = next((a for a in accounts if 'Cash' in a['name'] and not a['is_group']), None)
        capital_acc = next((a for a in accounts if 'Capital' in a['name'] and not a['is_group']), None)
        
        # Fallback if specific names not found, just pick any two leaf accounts
        if not cash_acc or not capital_acc:
            leaf_accounts = [a for a in accounts if not a['is_group']]
            if len(leaf_accounts) >= 2:
                cash_acc = leaf_accounts[0]
                capital_acc = leaf_accounts[1]
                
        return cash_acc, capital_acc
    raise Exception(f"Failed to fetch accounts: {response.text}")

def test_voucher_lifecycle():
    try:
        token = get_token()
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        print("✅ Login Successful")
        
        # 1. Get Accounts
        acc1, acc2 = get_account_ids(headers)
        if not acc1 or not acc2:
            print("❌ Could not find suitable accounts for testing")
            return

        print(f"Using Accounts: {acc1['name']} (ID: {acc1['id']}) and {acc2['name']} (ID: {acc2['id']})")
        
        # 2. Create Draft Voucher (Capital Injection)
        # Debit Cash, Credit Capital
        payload = {
            "voucher_type": "JE",
            "voucher_date": "2025-01-01",
            "reference_number": "TEST-001",
            "narration": "Test Capital Injection",
            "total_amount": 1000.00,
            "entries": [
                {"account_id": acc1['id'], "debit": 1000, "credit": 0},
                {"account_id": acc2['id'], "debit": 0, "credit": 1000}
            ]
        }
        
        response = requests.post(VOUCHERS_URL, json=payload, headers=headers)
        if response.status_code == 201:
            voucher = response.json()
            print(f"✅ Draft Voucher Created: {voucher['voucher_number']} (ID: {voucher['id']})")
        else:
            print(f"❌ Create Failed: {response.text}")
            return

        # 3. Post Voucher
        post_url = f"{VOUCHERS_URL}{voucher['id']}/post/"
        response = requests.post(post_url, headers=headers)
        if response.status_code == 200:
            print("✅ Voucher Posted Successfully")
            updated_voucher = response.json()
            print(f"   Status: {updated_voucher['status']}")
        else:
            print(f"❌ Post Failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    test_voucher_lifecycle()
