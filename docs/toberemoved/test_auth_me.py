#!/usr/bin/env python3

import requests
import json

def test_auth_me():
    """Test the new /me endpoint"""
    
    print("🔐 Testing Auth /me Endpoint")
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
    
    # Test the /me endpoint
    url = "http://localhost:5000/api/auth/me"
    print(f"\n🔍 Testing: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response keys: {list(data.keys())}")
            if 'user' in data:
                user = data['user']
                print(f"User: {user.get('username')} ({user.get('email')})")
        else:
            print(f"❌ Failed! Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_auth_me()
