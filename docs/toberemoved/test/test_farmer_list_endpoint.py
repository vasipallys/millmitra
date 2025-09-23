#!/usr/bin/env python3

import requests
import json

def test_farmer_list_endpoint():
    """Test the farmer list endpoint directly"""
    
    print("🔍 Testing Farmer List Endpoint")
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
    
    # Test farmer list endpoint
    print("\n📋 Testing: Get Farmers List")
    try:
        response = requests.get("http://localhost:5000/api/farmer/list", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Farmer list retrieved successfully!")
            print(f"Total farmers: {data.get('total_farmers', 0)}")
            print(f"Active farmers: {data.get('active_farmers', 0)}")
            
            farmers = data.get('farmers', [])
            if farmers:
                print(f"\nFirst few farmers:")
                for i, farmer in enumerate(farmers[:3]):
                    print(f"  {i+1}. {farmer.get('name')} ({farmer.get('farmer_code')})")
            else:
                print("No farmers found in database")
        else:
            print(f"❌ Failed! Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test with CORS headers
    print("\n🌐 Testing: CORS Headers")
    try:
        headers_with_cors = {
            'Authorization': f'Bearer {token}',
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'
        }
        
        response = requests.options("http://localhost:5000/api/farmer/list", headers=headers_with_cors)
        print(f"OPTIONS Status: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
    except Exception as e:
        print(f"❌ CORS test exception: {str(e)}")
    
    print("\n🏁 Farmer list endpoint test completed!")

if __name__ == "__main__":
    test_farmer_list_endpoint()
