#!/usr/bin/env python3

"""
Create Default Users Script
Adds default users to the Rice Mill ERP database
"""

import os
import sys
from datetime import datetime

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def create_default_users():
    """Create default users for the system"""
    
    print("👥 Creating Default Users for Rice Mill ERP")
    print("=" * 50)
    
    try:
        # Import Flask app and database
        from app import app
        from extensions import db
        from models.user import User
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            print("🔍 Checking existing users...")
            
            # Check current user count
            existing_users = User.query.all()
            print(f"📊 Current users in database: {len(existing_users)}")
            
            if existing_users:
                print("👥 Existing users:")
                for user in existing_users:
                    print(f"  - {user.username} ({user.email}) - Role: {user.role}")
            
            # Define default users
            default_users = [
                {
                    'username': 'admin',
                    'email': 'admin@ricemill.com',
                    'password': 'admin123',
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'role': 'admin'
                },
                {
                    'username': 'manager',
                    'email': 'manager@ricemill.com',
                    'password': 'manager123',
                    'first_name': 'Mill',
                    'last_name': 'Manager',
                    'role': 'manager'
                },
                {
                    'username': 'operator',
                    'email': 'operator@ricemill.com',
                    'password': 'operator123',
                    'first_name': 'Mill',
                    'last_name': 'Operator',
                    'role': 'operator'
                },
                {
                    'username': 'quality',
                    'email': 'quality@ricemill.com',
                    'password': 'quality123',
                    'first_name': 'Quality',
                    'last_name': 'Controller',
                    'role': 'quality_controller'
                },
                {
                    'username': 'sales',
                    'email': 'sales@ricemill.com',
                    'password': 'sales123',
                    'first_name': 'Sales',
                    'last_name': 'Representative',
                    'role': 'sales'
                }
            ]
            
            print(f"\n🔧 Creating {len(default_users)} default users...")
            
            created_count = 0
            updated_count = 0
            
            for user_data in default_users:
                # Check if user already exists by username or email
                existing_user = User.query.filter(
                    (User.username == user_data['username']) | 
                    (User.email == user_data['email'])
                ).first()
                
                if existing_user:
                    print(f"ℹ️ User {user_data['username']} already exists, updating...")
                    
                    # Update existing user
                    existing_user.password_hash = generate_password_hash(user_data['password'])
                    existing_user.first_name = user_data['first_name']
                    existing_user.last_name = user_data['last_name']
                    existing_user.role = user_data['role']
                    existing_user.is_active = True
                    existing_user.is_verified = True
                    existing_user.updated_at = datetime.utcnow()
                    
                    updated_count += 1
                else:
                    print(f"✅ Creating user: {user_data['username']} ({user_data['email']})")
                    
                    # Create new user
                    new_user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=generate_password_hash(user_data['password']),
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role=user_data['role'],
                        is_active=True,
                        is_verified=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.session.add(new_user)
                    created_count += 1
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✅ User creation completed!")
            print(f"📊 Created: {created_count} new users")
            print(f"📊 Updated: {updated_count} existing users")
            
            # Verify users were created
            print(f"\n🔍 Verifying users...")
            all_users = User.query.all()
            print(f"📊 Total users in database: {len(all_users)}")
            
            print("\n👥 All users:")
            for user in all_users:
                status = "✅ Active" if user.is_active else "❌ Inactive"
                print(f"  - {user.username} ({user.email}) - Role: {user.role} - {status}")
            
            print(f"\n🔑 Login Credentials:")
            print("=" * 30)
            for user_data in default_users:
                print(f"Username: {user_data['email']}")
                print(f"Password: {user_data['password']}")
                print(f"Role: {user_data['role']}")
                print("-" * 30)
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating default users: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login():
    """Test login with default admin user"""
    
    print("\n🧪 Testing Admin Login")
    print("=" * 30)
    
    try:
        from app import app
        from extensions import db
        from models.user import User
        from werkzeug.security import check_password_hash
        
        with app.app_context():
            # Find admin user
            admin_user = User.query.filter_by(email='admin@ricemill.com').first()
            
            if not admin_user:
                print("❌ Admin user not found!")
                return False
            
            print(f"✅ Admin user found: {admin_user.username}")
            print(f"📧 Email: {admin_user.email}")
            print(f"👤 Name: {admin_user.first_name} {admin_user.last_name}")
            print(f"🔑 Role: {admin_user.role}")
            print(f"✅ Active: {admin_user.is_active}")
            print(f"✅ Verified: {admin_user.is_verified}")
            
            # Test password
            password_correct = check_password_hash(admin_user.password_hash, 'admin123')
            print(f"🔐 Password test: {'✅ Correct' if password_correct else '❌ Incorrect'}")
            
            return password_correct
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return False

def main():
    """Main function"""
    
    # Create default users
    success = create_default_users()
    
    if success:
        # Test admin login
        login_success = test_login()
        
        if login_success:
            print("\n🎉 SUCCESS!")
            print("=" * 50)
            print("✅ Default users created successfully")
            print("✅ Admin login test passed")
            print("🚀 You can now login to the application!")
            print("\n🌐 Try logging in at: http://localhost:3000")
            print("📧 Email: admin@ricemill.com")
            print("🔑 Password: admin123")
        else:
            print("\n⚠️ Users created but login test failed")
    else:
        print("\n❌ Failed to create default users")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
