#!/usr/bin/env python3

import requests
import json

def test_farmer_management():
    """Test farmer management endpoints"""
    
    print("👨‍🌾 Testing Farmer Management Endpoints")
    print("=" * 50)
    
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
    
    # Test 1: Register Farmer
    print("\n📝 Testing: Register Farmer")
    farmer_data = {
        "name": "Test Farmer 2",
        "phone": "9876543213",
        "email": "testfarmer@example.com",
        "village": "Test Village",
        "district": "Test District",
        "state": "Test State",
        "pincode": "123456",
        "total_land_area": 5.0,
        "farming_experience": 10
    }
    
    try:
        response = requests.post("http://localhost:5000/api/farmer/register", 
                               json=farmer_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Farmer registered successfully!")
            print(f"Farmer Code: {data['farmer']['farmer_code']}")
            farmer_id = data['farmer']['id']
        else:
            print(f"❌ Failed! Error: {response.text[:200]}")
            return
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return
    
    # Test 2: Create Contract
    print("\n📋 Testing: Create Contract")
    contract_data = {
        "farmer_id": farmer_id,
        "crop_type": "Basmati Rice",
        "quantity_committed": 1000.0,
        "base_price": 2500.0,
        "contract_start_date": "2024-01-01",
        "contract_end_date": "2024-12-31"
    }
    
    try:
        response = requests.post("http://localhost:5000/api/farmer/contracts", 
                               json=contract_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Contract created successfully!")
            print(f"Contract Number: {data['contract']['contract_number']}")
        else:
            print(f"❌ Failed! Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Record Procurement
    print("\n📦 Testing: Record Procurement")
    procurement_data = {
        "farmer_id": farmer_id,
        "crop_type": "Basmati Rice",
        "quantity": 500.0,
        "price_per_unit": 2600.0,
        "procurement_date": "2024-01-15"
    }
    
    try:
        response = requests.post("http://localhost:5000/api/farmer/procurements", 
                               json=procurement_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Procurement recorded successfully!")
            print(f"Stock ID: {data['procurement']['stock_id']}")
            print(f"Total Amount: ₹{data['procurement']['total_amount']}")
        else:
            print(f"❌ Failed! Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    print("\n🏁 Farmer management endpoints test completed!")

if __name__ == "__main__":
    test_farmer_management()
