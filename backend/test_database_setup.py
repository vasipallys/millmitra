#!/usr/bin/env python3
"""
Test database setup and basic functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_setup():
    """Test database setup and basic operations"""
    try:
        print("🔍 Testing database setup...")
        
        # Import app and extensions
        from app import create_app
        from extensions import db
        from models import User, Farmer, Customer, ProductionBatch
        
        # Create app
        app = create_app()
        print("✅ App created successfully")
        
        # Test database operations within app context
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test basic queries
            user_count = User.query.count()
            farmer_count = Farmer.query.count()
            customer_count = Customer.query.count()
            batch_count = ProductionBatch.query.count()
            
            print(f"✅ Database queries successful:")
            print(f"   - Users: {user_count}")
            print(f"   - Farmers: {farmer_count}")
            print(f"   - Customers: {customer_count}")
            print(f"   - Production Batches: {batch_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database setup error: {str(e)}")
        return False

def test_basic_app_functionality():
    """Test basic app functionality"""
    try:
        print("\n🔍 Testing basic app functionality...")
        
        from app import create_app
        
        app = create_app()
        client = app.test_client()
        
        # Test a basic endpoint
        with app.app_context():
            # Test if we can make a request
            response = client.get('/')
            print(f"✅ Basic request test: Status {response.status_code}")
            
            # Test auth endpoint structure
            response = client.post('/api/auth/login', json={})
            print(f"✅ Auth endpoint test: Status {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ App functionality error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Rice Mill Management System - Database & App Test")
    print("=" * 60)
    
    # Test database setup
    db_success = test_database_setup()
    
    # Test basic app functionality
    app_success = test_basic_app_functionality()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if db_success and app_success:
        print("🎉 ALL TESTS PASSED - System is ready!")
        return 0
    elif db_success:
        print("⚠️  Database OK, but app functionality needs attention")
        return 1
    else:
        print("❌ Critical issues found - needs immediate attention")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
