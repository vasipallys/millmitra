#!/usr/bin/env python3

import requests
import json

def test_finance_endpoints():
    """Test finance endpoints that the frontend is trying to access"""
    
    print("💰 Testing Finance Endpoints")
    print("=" * 40)
    
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
    
    # Test finance endpoints that frontend is calling
    endpoints = [
        '/api/finance/invoices?limit=10',
        '/api/finance/cash-flow?period=monthly',
        '/api/finance/accounts-receivable',
        '/api/finance/financial-summary?period_days=30'
    ]
    
    print("\n📊 Testing finance endpoints...")
    for endpoint in endpoints:
        url = f"http://localhost:5000{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Response keys: {list(data.keys())}")
            else:
                print(f"❌ Failed! Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n🏁 Finance endpoints test completed!")

if __name__ == "__main__":
    test_finance_endpoints()
