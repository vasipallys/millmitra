import requests
import json
from datetime import datetime, timedelta

# Test the analytics dashboard endpoint specifically
def test_analytics_dashboard():
    base_url = "http://localhost:5000"
    
    # First login to get token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            print(f"Token received: {token[:20]}...")
            
            # Test analytics dashboard
            headers = {'Authorization': f'Bearer {token}'}
            dashboard_response = requests.get(f"{base_url}/api/analytics/dashboard/overview", headers=headers)
            print(f"Dashboard status: {dashboard_response.status_code}")
            print(f"Dashboard response: {dashboard_response.text}")
        else:
            print(f"Login failed: {login_response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_analytics_dashboard()
