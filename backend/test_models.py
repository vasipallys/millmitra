#!/usr/bin/env python3
"""
Test model imports and basic functionality
"""

import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def test_model_imports():
    """Test that all models can be imported"""
    with app.app_context():
        try:
            # Test core model imports
            from models import User, Farmer, Customer, Payment
            print("Core models imported successfully")
            
            # Test new model imports
            from models import Equipment, UserPreference
            print("New models imported successfully")
            
            # Test relationship models
            from models import MaintenanceSchedule, QualityStandard
            print("Relationship models imported successfully")
            
            # Test all major models
            from models import (
                User, AuthLog, UserSession, UserPreference,
                Farmer, FarmerContract, PaddyProcurement,
                Customer, SalesOrder, Payment,
                Equipment, MaintenanceSchedule,
                Vehicle, Driver, QualityStandard
            )
            print("All major models imported successfully")
            
            print("Model import test PASSED!")
            return True
            
        except ImportError as e:
            print(f"Model import FAILED: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

def test_database_connection():
    """Test database connection"""
    with app.app_context():
        try:
            from extensions import db
            from sqlalchemy import text
            
            # Test basic connection
            result = db.session.execute(text("SELECT 1"))
            print("Database connection successful")
            
            # Test table count
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            table_count = result.fetchone()[0]
            print(f"Found {table_count} tables in database")
            
            print("Database connection test PASSED!")
            return True
            
        except Exception as e:
            print(f"Database connection FAILED: {e}")
            return False

def main():
    """Run all tests"""
    print("Model and Database Testing")
    print("=" * 50)
    
    success = True
    
    # Test model imports
    if not test_model_imports():
        success = False
    print()
    
    # Test database connection
    if not test_database_connection():
        success = False
    print()
    
    print("=" * 50)
    if success:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)