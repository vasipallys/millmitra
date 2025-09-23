#!/usr/bin/env python3

import requests
import json

def test_dashboard_endpoints():
    """Test dashboard endpoints after fixing QualityTest attribute error"""
    
    print("📊 Testing Dashboard Endpoints")
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
    
    # Test dashboard widgets endpoint
    print("\n📊 Testing: Dashboard Widgets")
    try:
        response = requests.get("http://localhost:5000/api/dashboard/widgets", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard widgets retrieved successfully!")
            print(f"Widgets count: {len(data.get('widgets', []))}")
        else:
            print(f"❌ Failed! Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test dashboard alerts endpoint
    print("\n🚨 Testing: Dashboard Alerts")
    try:
        response = requests.get("http://localhost:5000/api/dashboard/alerts", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard alerts retrieved successfully!")
            print(f"Alerts count: {len(data.get('alerts', []))}")
            
            # Show first few alerts if any
            alerts = data.get('alerts', [])
            if alerts:
                print("First few alerts:")
                for i, alert in enumerate(alerts[:3]):
                    print(f"  {i+1}. {alert.get('title', 'Unknown')} - {alert.get('type', 'info')}")
            else:
                print("No alerts found")
        else:
            print(f"❌ Failed! Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test dashboard overview endpoint
    print("\n📈 Testing: Dashboard Overview")
    try:
        response = requests.get("http://localhost:5000/api/dashboard/overview", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard overview retrieved successfully!")
            print(f"Overview sections: {list(data.keys())}")
        else:
            print(f"❌ Failed! Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    print("\n🏁 Dashboard endpoints test completed!")

if __name__ == "__main__":
    test_dashboard_endpoints()
