#!/usr/bin/env python3

"""
Test script for PostgreSQL migration
Tests the updated create_all_tables.py with PostgreSQL database
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    print("🔍 Testing PostgreSQL Connection")
    print("=" * 40)
    
    try:
        # Test connection to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="siva",
            database="postgres"  # Connect to default database first
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ PostgreSQL server connection successful")
        
        # Check if rice_mill_erp database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='rice_mill_erp'")
        db_exists = cursor.fetchone()
        
        if not db_exists:
            print("📦 Creating rice_mill_erp database...")
            cursor.execute("CREATE DATABASE rice_mill_erp")
            print("✅ Database created successfully")
        else:
            print("✅ Database rice_mill_erp already exists")
        
        cursor.close()
        conn.close()
        
        # Test connection to rice_mill_erp database
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="siva",
            database="rice_mill_erp"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Connected to rice_mill_erp database")
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def run_migration():
    """Run the migration script"""
    print("\n🔧 Running Database Migration")
    print("=" * 40)
    
    try:
        # Change to backend directory
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        
        # Run migration script
        result = subprocess.run([
            sys.executable, 
            'migrations/create_all_tables.py'
        ], 
        cwd=backend_dir,
        capture_output=True,
        text=True
        )
        
        print("Migration output:")
        print(result.stdout)
        
        if result.stderr:
            print("Migration errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully")
            return True
        else:
            print(f"❌ Migration failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False

def run_migration_with_sample_data():
    """Run migration with sample data"""
    print("\n📊 Running Migration with Sample Data")
    print("=" * 40)
    
    try:
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        
        result = subprocess.run([
            sys.executable, 
            'migrations/create_all_tables.py',
            '--with-sample-data'
        ], 
        cwd=backend_dir,
        capture_output=True,
        text=True
        )
        
        print("Migration with sample data output:")
        print(result.stdout)
        
        if result.stderr:
            print("Migration errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Migration with sample data completed successfully")
            return True
        else:
            print(f"❌ Migration with sample data failed")
            return False
            
    except Exception as e:
        print(f"❌ Error running migration with sample data: {e}")
        return False

def verify_tables():
    """Verify tables were created correctly"""
    print("\n🔍 Verifying Database Tables")
    print("=" * 40)
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="siva",
            database="rice_mill_erp"
        )
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables:")
        
        expected_tables = [
            'users', 'roles', 'farmers', 'farmer_contracts',
            'paddy_stock', 'product_stock', 'production_batches',
            'quality_tests', 'sales_orders', 'customers'
        ]
        
        table_names = [table[0] for table in tables]
        
        for table in table_names:
            print(f"  📋 {table}")
        
        # Check for expected tables
        missing_tables = []
        for expected in expected_tables:
            if expected not in table_names:
                missing_tables.append(expected)
        
        if missing_tables:
            print(f"⚠️ Missing expected tables: {missing_tables}")
        else:
            print("✅ All expected tables found")
        
        # Check admin user
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        admin_count = cursor.fetchone()[0]
        print(f"✅ Admin users found: {admin_count}")
        
        # Check roles
        cursor.execute("SELECT COUNT(*) FROM roles")
        role_count = cursor.fetchone()[0]
        print(f"✅ Roles found: {role_count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 PostgreSQL Migration Test")
    print("=" * 50)
    
    # Test PostgreSQL connection
    if not test_postgresql_connection():
        print("❌ PostgreSQL connection test failed. Please check your PostgreSQL setup.")
        return False
    
    # Run migration
    if not run_migration():
        print("❌ Migration failed. Please check the migration script.")
        return False
    
    # Verify tables
    if not verify_tables():
        print("❌ Table verification failed.")
        return False
    
    print("\n🎉 All tests passed! PostgreSQL migration is working correctly.")
    print("\n📝 Next steps:")
    print("1. Start the backend server: cd backend && python app.py")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Login with: admin@ricemill.com / admin123")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
