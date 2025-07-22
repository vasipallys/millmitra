#!/usr/bin/env python3
"""
Test Login Functionality
"""

from app import create_app
from models.user import User
from extensions import db

def test_login():
    """Test login functionality"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Testing Login Functionality")
        print("=" * 40)
        
        # Check if users exist
        users = User.query.all()
        print(f"📊 Total users in database: {len(users)}")
        
        for user in users:
            print(f"👤 User: {user.username} / {user.email}")
            print(f"   Active: {user.is_active}")
            print(f"   Verified: {user.is_verified}")
            
            # Test password
            password_result = user.check_password('admin123')
            print(f"   Password 'admin123' check: {password_result}")
            
            if user.username == 'admin':
                # Test different password variations
                test_passwords = ['admin123', 'Admin123', 'ADMIN123', 'admin', '123']
                print(f"   Testing different passwords for admin:")
                for pwd in test_passwords:
                    result = user.check_password(pwd)
                    print(f"     '{pwd}': {result}")
            
            print()
        
        # Test the specific admin user
        admin = User.query.filter_by(email='admin@ricemill.com').first()
        if admin:
            print("🔐 Testing admin@ricemill.com specifically:")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Active: {admin.is_active}")
            print(f"   Verified: {admin.is_verified}")
            print(f"   Password hash exists: {bool(admin.password_hash)}")
            print(f"   Password hash length: {len(admin.password_hash) if admin.password_hash else 0}")
            
            # Test login with email
            email_login = User.query.filter(
                (User.username == 'admin@ricemill.com') | 
                (User.email == 'admin@ricemill.com') | 
                (User.phone == 'admin@ricemill.com')
            ).first()
            print(f"   Email login query result: {email_login.username if email_login else None}")
            
        else:
            print("❌ Admin user not found!")

if __name__ == '__main__':
    test_login()
