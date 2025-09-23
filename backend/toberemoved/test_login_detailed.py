#!/usr/bin/env python3
"""
Detailed Login Test
"""

import json
from app import create_app
from models.user import User
from services.ai_auth_service import AIAuthService

def test_login_process():
    """Test the complete login process"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Detailed Login Process Test")
        print("=" * 50)
        
        # Initialize AI auth service
        ai_auth = AIAuthService()
        
        # Test data
        test_username = "admin@ricemill.com"
        test_password = "admin123"
        
        print(f"📧 Testing login with: {test_username}")
        print(f"🔑 Password: {test_password}")
        print()
        
        # Step 1: Normalize username
        normalized_username = ai_auth.normalize_username(test_username)
        print(f"1️⃣ Username normalization:")
        print(f"   Original: {test_username}")
        print(f"   Normalized: {normalized_username}")
        print(f"   Changed: {test_username != normalized_username}")
        print()
        
        # Step 2: Find user
        print(f"2️⃣ User lookup:")
        user = User.query.filter(
            (User.username == normalized_username) | 
            (User.email == normalized_username) | 
            (User.phone == normalized_username)
        ).first()
        
        if user:
            print(f"   ✅ User found: {user.username}")
            print(f"   📧 Email: {user.email}")
            print(f"   🟢 Active: {user.is_active}")
            print(f"   ✅ Verified: {user.is_verified}")
        else:
            print(f"   ❌ User not found!")
            
            # Debug: Check what users exist
            all_users = User.query.all()
            print(f"   Available users:")
            for u in all_users:
                print(f"     - {u.username} / {u.email}")
        print()
        
        # Step 3: Check password
        if user:
            print(f"3️⃣ Password verification:")
            password_valid = user.check_password(test_password)
            print(f"   Password valid: {password_valid}")
            
            if not password_valid:
                print(f"   🔍 Testing other passwords:")
                for pwd in ['admin', 'Admin123', 'password', '123']:
                    result = user.check_password(pwd)
                    print(f"     '{pwd}': {result}")
        print()
        
        # Step 4: Test the complete login flow
        print(f"4️⃣ Complete login simulation:")
        
        # Simulate the request data
        request_data = {
            'username': test_username,
            'password': test_password,
            'method': 'password',
            'device_info': {}
        }
        
        print(f"   Request data: {json.dumps(request_data, indent=2)}")
        
        # Test each step
        username = request_data.get('username', '').strip()
        password = request_data.get('password', '')
        
        print(f"   Extracted username: '{username}'")
        print(f"   Extracted password: '{password}'")
        
        normalized = ai_auth.normalize_username(username)
        print(f"   Normalized username: '{normalized}'")
        
        user_lookup = User.query.filter(
            (User.username == normalized) | 
            (User.email == normalized) | 
            (User.phone == normalized)
        ).first()
        
        if user_lookup:
            print(f"   ✅ User lookup successful: {user_lookup.username}")
            if user_lookup.is_active:
                print(f"   ✅ User is active")
                password_check = user_lookup.check_password(password)
                print(f"   Password check: {password_check}")
                
                if password_check:
                    print(f"   🎉 LOGIN SHOULD SUCCEED!")
                else:
                    print(f"   ❌ LOGIN FAILS: Wrong password")
            else:
                print(f"   ❌ LOGIN FAILS: User not active")
        else:
            print(f"   ❌ LOGIN FAILS: User not found")

if __name__ == '__main__':
    test_login_process()
