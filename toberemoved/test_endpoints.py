#!/usr/bin/env python3
"""
Quick Endpoint Tester for Rice Mill ERP
Tests actual available endpoints
"""

import requests
import json

def test_endpoint(url, method='GET', data=None, headers=None):
    """Test a single endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=5)
        
        return {
            'url': url,
            'status': response.status_code,
            'success': response.status_code < 400,
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
        }
    except Exception as e:
        return {
            'url': url,
            'status': 'error',
            'success': False,
            'response': str(e)
        }

def main():
    """Test key endpoints"""
    
    base_url = "http://localhost:5001"
    
    # Test endpoints without authentication first
    public_endpoints = [
        f"{base_url}/api/health",
        f"{base_url}/api/auth/login",
    ]
    
    print("🧪 Testing Public Endpoints")
    print("=" * 50)
    
    for endpoint in public_endpoints:
        result = test_endpoint(endpoint)
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['url']} - Status: {result['status']}")
        if not result['success']:
            print(f"   Response: {result['response']}")
    
    # Try to login and get token
    print("\n🔐 Testing Authentication")
    print("=" * 50)
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    login_result = test_endpoint(f"{base_url}/api/auth/login", 'POST', login_data)
    print(f"Login attempt: Status {login_result['status']}")
    
    token = None
    if login_result['success'] and isinstance(login_result['response'], dict):
        token = login_result['response'].get('access_token')
        print(f"✅ Got token: {token[:20]}..." if token else "❌ No token received")
    
    # Test protected endpoints
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    protected_endpoints = [
        f"{base_url}/api/dashboard/overview",
        f"{base_url}/api/dashboard/widgets",
        f"{base_url}/api/farmer/list",
        f"{base_url}/api/inventory/stock",
        f"{base_url}/api/production/batches",
        f"{base_url}/api/customers/list",
    ]
    
    print("\n🔒 Testing Protected Endpoints")
    print("=" * 50)
    
    for endpoint in protected_endpoints:
        result = test_endpoint(endpoint, headers=headers)
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['url']} - Status: {result['status']}")
        if not result['success']:
            print(f"   Response: {result['response']}")
    
    # Test some POST endpoints
    print("\n📝 Testing POST Endpoints")
    print("=" * 50)
    
    # Try creating a farmer
    farmer_data = {
        "name": "Test Farmer",
        "phone": "9876543210",
        "address": "Test Address",
        "email": "test@farmer.com"
    }
    
    create_farmer_result = test_endpoint(f"{base_url}/api/farmer/create", 'POST', farmer_data, headers)
    status = "✅" if create_farmer_result['success'] else "❌"
    print(f"{status} Create Farmer - Status: {create_farmer_result['status']}")
    if not create_farmer_result['success']:
        print(f"   Response: {create_farmer_result['response']}")

if __name__ == "__main__":
    main()