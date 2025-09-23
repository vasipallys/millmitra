#!/usr/bin/env python3

import requests
import json

def test_auth():
    """Test authentication flow"""
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint first
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Health Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend is running!")
        else:
            print("❌ Backend health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")
        return
    
    print()
    
    # Test login endpoint
    print("🔐 Testing login endpoint...")
    login_data = {
        "username": "admin@ricemill.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print("✅ Login successful!")
                print(f"Token received: {token[:50]}...")
                
                # Test protected endpoint
                print()
                print("🔒 Testing protected endpoint...")
                headers = {'Authorization': f'Bearer {token}'}
                
                protected_response = requests.get(f"{base_url}/api/dashboard/overview", headers=headers)
                print(f"Protected endpoint status: {protected_response.status_code}")
                
                if protected_response.status_code == 200:
                    print("✅ Protected endpoint accessible!")
                else:
                    print(f"❌ Protected endpoint failed: {protected_response.text[:100]}")
            else:
                print("❌ No token in response")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Login exception: {e}")

if __name__ == "__main__":
    test_auth()
