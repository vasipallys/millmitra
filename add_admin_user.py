#!/usr/bin/env python3

"""
Quick script to add admin user to the database
"""

import os
import sys
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def add_admin_user():
    """Add admin user directly to SQLite database"""
    
    print("👤 Adding Admin User to Database")
    print("=" * 40)
    
    try:
        # Connect to SQLite database
        db_paths = [
            os.path.join('backend', 'instance', 'rice_mill_erp.db'),
            os.path.join('backend', 'instance', 'rice_mill.db'),
            os.path.join('backend', 'rice_mill.db')
        ]

        db_path = None
        for path in db_paths:
            if os.path.exists(path):
                db_path = path
                break

        if not db_path:
            print(f"❌ Database file not found in any of these locations:")
            for path in db_paths:
                print(f"   - {path}")
            return False

        print(f"✅ Found database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", ('admin@ricemill.com',))
        existing = cursor.fetchone()
        
        if existing:
            print("ℹ️ Admin user already exists, updating password...")
            password_hash = generate_password_hash('admin123')
            cursor.execute("""
                UPDATE users SET 
                    password_hash = ?,
                    is_active = 1,
                    is_verified = 1
                WHERE email = ?
            """, (password_hash, 'admin@ricemill.com'))
        else:
            print("✅ Creating new admin user...")
            password_hash = generate_password_hash('admin123')
            current_time = datetime.utcnow().isoformat()
            
            cursor.execute("""
                INSERT INTO users (
                    username, email, password_hash, first_name, last_name, 
                    role, is_active, is_verified, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
            """, ('admin', 'admin@ricemill.com', password_hash,
                 'System', 'Administrator', 'admin',
                 current_time, current_time))
        
        conn.commit()
        
        # Verify user was created/updated
        cursor.execute("SELECT username, email, role, is_active FROM users WHERE email = ?", 
                      ('admin@ricemill.com',))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ Admin user ready!")
            print(f"   Username: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Role: {user[2]}")
            print(f"   Active: {'Yes' if user[3] else 'No'}")
            print(f"\n🔑 Login Credentials:")
            print(f"   Email: admin@ricemill.com")
            print(f"   Password: admin123")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = add_admin_user()
    if success:
        print("\n🎉 Admin user is ready!")
        print("🌐 You can now login at: http://localhost:3000")
    else:
        print("\n❌ Failed to add admin user")
    sys.exit(0 if success else 1)
