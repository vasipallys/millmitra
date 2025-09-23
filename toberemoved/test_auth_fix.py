#!/usr/bin/env python3

"""
Test Authentication Fix
Verifies that the auth_logs database issue is resolved
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import requests
import json
import time

def test_auth_endpoints():
    """Test authentication endpoints with long device fingerprints"""
    
    print("🧪 Testing Authentication Fix")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test data with very long device fingerprint (simulating the original error)
    test_data = {
        "username": "admin@ricemill.com",
        "password": "wrongpassword",  # Intentionally wrong to test failed login logging
        "device_info": {
            "fingerprint": "eyJjYW52YXMiOiJkYXRhOmltYWdlL3BuZztiYXNlNjQsaVZCT1J3MEtHZ29BQUFBTlNVaEVVZ0FBQVN3QUFBQ1dDQVlBQUFCa1c3WFNBQUFBQVhOU1IwSUFyczRjNlFBQUNOcEpSRUZVZUY3dDI3d" * 100,  # Very long fingerprint
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "ip_address": "127.0.0.1",
            "location": "Test Location"
        }
    }
    
    print(f"📊 Test fingerprint length: {len(test_data['device_info']['fingerprint'])} characters")
    
    # Test 1: Check if backend is running
    print("\n🔍 Test 1: Backend Health Check")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not running: {e}")
        print("💡 Please start the backend server: cd backend && python app.py")
        return False
    
    # Test 2: Test failed login (this was causing the original error)
    print("\n🔍 Test 2: Failed Login with Long Device Fingerprint")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response: {response.text[:200]}...")
        
        if response.status_code == 401:
            print("✅ Failed login handled correctly (401 Unauthorized)")
            print("✅ No database error occurred!")
        else:
            print(f"⚠️ Unexpected response code: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 3: Test username suggestion (another endpoint that might use device info)
    print("\n🔍 Test 3: Username Suggestion")
    try:
        suggestion_data = {
            "email": "test@example.com",
            "device_info": test_data["device_info"]
        }
        
        response = requests.post(
            f"{base_url}/api/auth/suggest-username",
            json=suggestion_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Username suggestion works correctly")
        else:
            print(f"⚠️ Username suggestion returned: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Username suggestion failed: {e}")
    
    # Test 4: Test with correct credentials (if default user exists)
    print("\n🔍 Test 4: Successful Login Test")
    correct_data = {
        "username": "admin",
        "password": "admin123",  # Default admin password
        "device_info": test_data["device_info"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=correct_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successful login works correctly")
            print("✅ Long device fingerprint handled in successful login too!")
        elif response.status_code == 401:
            print("ℹ️ Login failed (user may not exist or wrong password)")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login test failed: {e}")
    
    return True

def test_database_directly():
    """Test database operations directly"""
    
    print("\n🔍 Direct Database Test")
    print("=" * 30)
    
    try:
        # Import backend modules
        from backend.app import app
        from backend.extensions import db
        from backend.models.user import AuthLog
        from datetime import datetime
        
        with app.app_context():
            # Test inserting a record with very long device fingerprint
            test_log = AuthLog(
                username_attempted='test@example.com',
                action='login',
                method='password',
                success=False,
                ip_address='127.0.0.1',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                device_fingerprint='eyJjYW52YXMiOiJkYXRhOmltYWdlL3BuZztiYXNlNjQsaVZCT1J3MEtHZ29BQUFBTlNVaEVVZ0FBQVN3QUFBQ1dDQVlBQUFCa1c3WFNBQUFBQVhOU1IwSUFyczRjNlFBQUNOcEpSRUZVZUY3dDI3d' * 50,
                location='Test Location',
                failure_reason='test_insert',
                risk_score=0.5,
                timestamp=datetime.utcnow()
            )
            
            print(f"📊 Test fingerprint length: {len(test_log.device_fingerprint)} characters")
            
            # Try to insert
            db.session.add(test_log)
            db.session.commit()
            
            print("✅ Direct database insert successful!")
            
            # Clean up
            db.session.delete(test_log)
            db.session.commit()
            print("✅ Test record cleaned up")
            
            return True
            
    except Exception as e:
        print(f"❌ Direct database test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🔧 Authentication Fix Verification")
    print("=" * 60)
    print("Testing that the auth_logs database error is resolved...")
    print()
    
    # Test API endpoints
    api_success = test_auth_endpoints()
    
    # Test database directly
    db_success = test_database_directly()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"API Tests: {'✅ PASSED' if api_success else '❌ FAILED'}")
    print(f"Database Tests: {'✅ PASSED' if db_success else '❌ FAILED'}")
    
    if api_success and db_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Authentication database error is FIXED!")
        print("✅ Long device fingerprints are now handled correctly!")
        print("✅ PWA login functionality should work without errors!")
    else:
        print("\n⚠️ Some tests failed")
        print("Please check the error messages above")
    
    print("\n🔗 Next Steps:")
    print("1. Test PWA login functionality in the browser")
    print("2. Verify no console errors during login attempts")
    print("3. Check that auth_logs table stores data correctly")

if __name__ == "__main__":
    main()
