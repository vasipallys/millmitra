#!/usr/bin/env python3

"""
Fix Users Script - SQLite Compatible
Creates default users using SQLite database
"""

import os
import sys
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def create_users_sqlite():
    """Create users directly in SQLite database"""
    
    print("👥 Creating Default Users (SQLite)")
    print("=" * 50)
    
    try:
        # Connect to SQLite database
        db_path = os.path.join('backend', 'rice_mill.db')
        
        if not os.path.exists(db_path):
            print(f"❌ Database file not found: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table not found in database")
            return False
        
        print("✅ Connected to SQLite database")
        
        # Check existing users
        cursor.execute("SELECT username, email, role FROM users")
        existing_users = cursor.fetchall()
        
        print(f"📊 Current users in database: {len(existing_users)}")
        if existing_users:
            print("👥 Existing users:")
            for user in existing_users:
                print(f"  - {user[0]} ({user[1]}) - Role: {user[2]}")
        
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
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for user_data in default_users:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", 
                         (user_data['username'], user_data['email']))
            existing = cursor.fetchone()
            
            # Hash password
            password_hash = generate_password_hash(user_data['password'])
            current_time = datetime.utcnow().isoformat()
            
            if existing:
                print(f"ℹ️ Updating user: {user_data['username']}")
                cursor.execute("""
                    UPDATE users SET 
                        password_hash = ?,
                        first_name = ?,
                        last_name = ?,
                        role = ?,
                        is_active = 1,
                        is_verified = 1,
                        updated_at = ?
                    WHERE id = ?
                """, (password_hash, user_data['first_name'], user_data['last_name'], 
                     user_data['role'], current_time, existing[0]))
                updated_count += 1
            else:
                print(f"✅ Creating user: {user_data['username']} ({user_data['email']})")
                cursor.execute("""
                    INSERT INTO users (
                        username, email, password_hash, first_name, last_name, 
                        role, is_active, is_verified, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
                """, (user_data['username'], user_data['email'], password_hash,
                     user_data['first_name'], user_data['last_name'], user_data['role'],
                     current_time, current_time))
                created_count += 1
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ User creation completed!")
        print(f"📊 Created: {created_count} new users")
        print(f"📊 Updated: {updated_count} existing users")
        
        # Verify users
        cursor.execute("SELECT username, email, role, is_active FROM users")
        all_users = cursor.fetchall()
        
        print(f"\n👥 All users in database ({len(all_users)}):")
        for user in all_users:
            status = "✅ Active" if user[3] else "❌ Inactive"
            print(f"  - {user[0]} ({user[1]}) - Role: {user[2]} - {status}")
        
        print(f"\n🔑 Login Credentials:")
        print("=" * 30)
        for user_data in default_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Role: {user_data['role']}")
            print("-" * 30)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        import traceback
        traceback.print_exc()
        return False

def install_postgresql_driver():
    """Install PostgreSQL driver for future use"""
    
    print("\n🐘 Installing PostgreSQL Driver")
    print("=" * 40)
    
    try:
        import subprocess
        
        print("📦 Installing psycopg2-binary...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL driver installed successfully")
            return True
        else:
            print(f"⚠️ Failed to install PostgreSQL driver: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error installing PostgreSQL driver: {e}")
        return False

def main():
    """Main function"""
    
    print("🔧 Rice Mill ERP - User Setup Fix")
    print("=" * 50)
    
    # Create users in SQLite
    success = create_users_sqlite()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("=" * 50)
        print("✅ Default users created successfully")
        print("🚀 You can now login to the application!")
        print("\n🌐 Try logging in at: http://localhost:3000")
        print("📧 Email: admin@ricemill.com")
        print("🔑 Password: admin123")
        
        # Try to install PostgreSQL driver for future use
        print("\n🔧 Installing PostgreSQL driver for future use...")
        install_postgresql_driver()
        
    else:
        print("\n❌ Failed to create default users")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
