#!/usr/bin/env python3
"""
Database Migration Script
Recreates all database tables to match current models
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from extensions import db

# Import specific models to avoid import issues
from models.user import User, AuthLog, UserSession
from models.farmer import Farmer
from models.inventory import ProductStock, PaddyStock, StockMovement  # noqa: F401
from models.production import ProductionBatch, QualityTest
from models.sales import Customer, SalesOrder
from models.finance import Payment, Expense, Budget
from models.financial import Invoice  # noqa: F401

def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    return app

def migrate_database():
    """Migrate database to latest schema"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database migration...")
        
        # Backup existing database if it exists
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if os.path.exists(db_path):
            backup_path = f"{db_path}.backup"
            print(f"📦 Backing up existing database to {backup_path}")
            import shutil
            shutil.copy2(db_path, backup_path)
        
        # Drop all existing tables
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        # Create all tables with new schema
        print("🏗️  Creating tables with updated schema...")
        db.create_all()
        
        # Create default admin user
        print("👤 Creating default admin user...")
        create_default_users()
        
        print("✅ Database migration completed successfully!")
        print(f"📍 Database location: {db_path}")

def create_default_users():
    """Create default users for testing"""
    try:
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@ricemill.com',
                first_name='System',
                last_name='Administrator',
                role='admin',
                department='Management',
                is_active=True,
                is_verified=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
        
        # Create operator user
        operator_user = User.query.filter_by(username='operator').first()
        if not operator_user:
            operator_user = User(
                username='operator',
                email='operator@ricemill.com',
                first_name='Mill',
                last_name='Operator',
                role='operator',
                department='Production',
                is_active=True,
                is_verified=True
            )
            operator_user.set_password('operator123')
            db.session.add(operator_user)
        
        # Create manager user
        manager_user = User.query.filter_by(username='manager').first()
        if not manager_user:
            manager_user = User(
                username='manager',
                email='manager@ricemill.com',
                first_name='Production',
                last_name='Manager',
                role='manager',
                department='Production',
                is_active=True,
                is_verified=True
            )
            manager_user.set_password('manager123')
            db.session.add(manager_user)
        
        db.session.commit()
        print("✅ Default users created successfully!")
        print("   - admin@ricemill.com / admin123")
        print("   - operator@ricemill.com / operator123")
        print("   - manager@ricemill.com / manager123")
        
    except Exception as e:
        print(f"❌ Error creating default users: {e}")
        db.session.rollback()

if __name__ == '__main__':
    print("🚀 Rice Mill Management System - Database Migration")
    print("=" * 50)
    
    try:
        migrate_database()
        print("\n🎉 Migration completed successfully!")
        print("You can now start the application with: python app.py")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
