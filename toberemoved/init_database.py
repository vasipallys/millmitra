#!/usr/bin/env python3
"""
Simple Database Initialization Script
"""

import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

try:
    from app import create_app
    from extensions import db
    
    print("🗄️ Initializing Rice Mill ERP Database...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Try to create default admin user
        try:
            from models.user import User
            from werkzeug.security import generate_password_hash
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@ricemill.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created!")
                print("   Username: admin")
                print("   Password: admin123")
            else:
                print("ℹ️ Admin user already exists")
                
        except Exception as e:
            print(f"⚠️ Could not create admin user: {e}")
            print("   You can create users manually later")
        
        print("\n🎉 Database initialization complete!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try installing missing dependencies:")
    print("   pip install opencv-python")
    print("   pip install -r backend/requirements.txt")
    
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    print("💡 Make sure PostgreSQL is running and configured correctly")