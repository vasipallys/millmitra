#!/usr/bin/env python3

import requests
import json

def test_metrics_endpoints():
    """Test all metrics endpoints that the frontend is trying to access"""
    
    # Login first
    login_url = "http://localhost:5000/api/auth/login"
    login_data = {
        "username": "admin@ricemill.com",
        "password": "admin123"
    }
    
    print("🔐 Logging in...")
    response = requests.post(login_url, json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("✅ Login successful!")
    print(f"Token: {token[:50]}...")
    print()
    
    # Test metrics endpoints
    endpoints = [
        '/api/dashboard/metrics/production',
        '/api/dashboard/metrics/quality', 
        '/api/dashboard/metrics/financial',
        '/api/dashboard/metrics/inventory',
        '/api/dashboard/alerts'
    ]
    
    print("📊 Testing metrics endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints:
        url = f"http://localhost:5000{endpoint}"
        print(f"🔍 Testing: {endpoint}")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Response keys: {list(data.keys())}")
            else:
                print(f"❌ Failed! Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        print()
    
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_metrics_endpoints()
