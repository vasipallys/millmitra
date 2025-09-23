#!/usr/bin/env python3

import requests
import json

def test_all_endpoints():
    """Test all major endpoints to see current status"""
    
    print("🔍 Testing All Major Endpoints")
    print("=" * 50)
    
    # Login first
    print("🔐 Logging in...")
    login_data = {
        "username": "admin@ricemill.com",
        "password": "admin123",
        "method": "password",
        "device_info": {
            "browser": "test",
            "os": "test",
            "ip": "127.0.0.1"
        }
    }
    
    try:
        response = requests.post("http://localhost:5000/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print("✅ Login successful!")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login exception: {e}")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test all major endpoints
    endpoints = {
        'Dashboard': [
            '/api/dashboard/overview',
            '/api/dashboard/widgets',
            '/api/dashboard/insights',
            '/api/dashboard/alerts',
            '/api/dashboard/metrics/production',
            '/api/dashboard/metrics/quality',
            '/api/dashboard/metrics/financial'
        ],
        'Farmer': [
            '/api/farmer/list',
            '/api/farmer/analytics/overview'
        ],
        'Inventory': [
            '/api/inventory/paddy',
            '/api/inventory/products'
        ],
        'Production': [
            '/api/production/batches',
            '/api/production/current-status',
            '/api/production/recommendations'
        ],
        'Sales': [
            '/api/sales/orders',
            '/api/sales/analytics'
        ],
        'Finance': [
            '/api/finance/invoices',
            '/api/finance/cash-flow',
            '/api/finance/accounts-receivable',
            '/api/finance/financial-summary'
        ],
        'Customers': [
            '/api/customers',
            '/api/customers/analytics/overview',
            '/api/customers/analytics/segments'
        ]
    }
    
    print("\n📊 Testing all endpoints...")
    
    working_count = 0
    total_count = 0
    
    for category, endpoint_list in endpoints.items():
        print(f"\n🔍 {category} Endpoints:")
        
        for endpoint in endpoint_list:
            total_count += 1
            url = f"http://localhost:5000{endpoint}"
            
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ {endpoint}")
                    working_count += 1
                elif response.status_code == 404:
                    print(f"  ❌ {endpoint} (Not Found)")
                else:
                    print(f"  ⚠️  {endpoint} (Status: {response.status_code})")
                    
            except requests.exceptions.ConnectionError:
                print(f"  ❌ {endpoint} (Connection Error)")
            except requests.exceptions.Timeout:
                print(f"  ⏱️  {endpoint} (Timeout)")
            except Exception as e:
                print(f"  ❌ {endpoint} (Error: {str(e)[:50]})")
    
    print(f"\n📈 Summary:")
    print(f"Working endpoints: {working_count}/{total_count}")
    print(f"Success rate: {(working_count/total_count)*100:.1f}%")
    
    if working_count < total_count:
        print(f"\n🔧 {total_count - working_count} endpoints need to be enabled")
    else:
        print(f"\n🎉 All endpoints are working!")

if __name__ == "__main__":
    test_all_endpoints()
