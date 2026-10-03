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
        from services.demo_users import ensure_demo_users
        created = ensure_demo_users()
        print("✅ Default users ensured (admin, manager, operator, quality).")
        if created:
            print(f"   Created {created} missing demo account(s).")
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
