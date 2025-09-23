#!/usr/bin/env python3
"""
Test API Login Directly
"""

import requests
import json

def test_api_login():
    """Test the login API directly"""
    print("🔍 Testing Login API Directly")
    print("=" * 40)
    
    # Test data
    login_data = {
        'username': 'admin@ricemill.com',
        'password': 'admin123',
        'method': 'password',
        'device_info': {
            'user_agent': 'Test Agent',
            'ip_address': '127.0.0.1'
        }
    }
    
    print(f"📧 Testing login with: {login_data['username']}")
    print(f"🔑 Password: {login_data['password']}")
    print()
    
    try:
        # Make the API call
        response = requests.post(
            'http://localhost:5000/api/auth/login',
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📋 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📋 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ LOGIN SUCCESSFUL!")
        else:
            print(f"❌ LOGIN FAILED: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend not running or not accessible")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_api_login()
