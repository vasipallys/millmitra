#!/usr/bin/env python3
"""
Test script to debug dashboard API issues
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000/api"
LOGIN_URL = f"{BASE_URL}/auth/login"
DASHBOARD_URLS = {
    "overview": f"{BASE_URL}/dashboard/overview?days=7",
    "widgets": f"{BASE_URL}/dashboard/widgets",
    "insights": f"{BASE_URL}/dashboard/insights",
    "alerts": f"{BASE_URL}/dashboard/alerts"
}

def test_login():
    """Test login and get JWT token"""
    print("🔐 Testing login...")
    
    login_data = {
        "username": "admin@ricemill.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user = data.get('user')
            print(f"✅ Login successful!")
            print(f"User: {user.get('email')} ({user.get('role')})")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_dashboard_endpoints(token):
    """Test all dashboard endpoints"""
    print("\n📊 Testing dashboard endpoints...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    results = {}
    
    for name, url in DASHBOARD_URLS.items():
        print(f"\n🔍 Testing {name}: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name} - Success!")
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                results[name] = {"status": "success", "data": data}
            else:
                print(f"❌ {name} - Failed!")
                print(f"Error: {response.text}")
                results[name] = {"status": "failed", "error": response.text}
                
        except Exception as e:
            print(f"❌ {name} - Exception: {e}")
            results[name] = {"status": "exception", "error": str(e)}
    
    return results

def main():
    print("🚀 Rice Mill Dashboard API Test")
    print("=" * 50)
    
    # Test login
    token = test_login()
    
    if not token:
        print("\n❌ Cannot proceed without valid token")
        return
    
    # Test dashboard endpoints
    results = test_dashboard_endpoints(token)
    
    # Summary
    print("\n📋 SUMMARY")
    print("=" * 50)
    
    for endpoint, result in results.items():
        status = result["status"]
        if status == "success":
            print(f"✅ {endpoint}: Working")
        else:
            print(f"❌ {endpoint}: {status}")
            if "error" in result:
                print(f"   Error: {result['error'][:100]}...")
    
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    main()
