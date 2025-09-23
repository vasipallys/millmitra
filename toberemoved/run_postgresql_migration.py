#!/usr/bin/env python3

"""
PostgreSQL Migration Runner
Runs the database migration for Rice Mill ERP with PostgreSQL optimizations
"""

import os
import sys
import subprocess
import time

def check_postgresql():
    """Check if PostgreSQL is running and accessible"""
    print("🔍 Checking PostgreSQL status...")
    
    try:
        # Try to connect to PostgreSQL using psql
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                ['powershell', '-Command', 
                 "try { $env:PGPASSWORD='siva'; psql -h localhost -U postgres -d postgres -c '\\conninfo' } catch { Write-Host 'PostgreSQL connection failed' }"],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:  # Linux/Mac
            result = subprocess.run(
                ['psql', '-h', 'localhost', '-U', 'postgres', '-d', 'postgres', '-c', '\\conninfo'],
                capture_output=True,
                text=True,
                env={**os.environ, 'PGPASSWORD': 'siva'},
                timeout=5
            )
        
        if "You are connected to database" in result.stdout:
            print("✅ PostgreSQL is running and accessible")
            return True
        else:
            print("❌ PostgreSQL connection failed")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ PostgreSQL connection timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking PostgreSQL: {e}")
        return False

def create_database():
    """Create the rice_mill_erp database if it doesn't exist"""
    print("🔧 Creating database if it doesn't exist...")
    
    try:
        # Check if database exists
        if os.name == 'nt':  # Windows
            result = subprocess.run(
                ['powershell', '-Command', 
                 "try { $env:PGPASSWORD='siva'; psql -h localhost -U postgres -d postgres -c \"SELECT 1 FROM pg_database WHERE datname='rice_mill_erp'\" } catch { Write-Host 'PostgreSQL query failed' }"],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:  # Linux/Mac
            result = subprocess.run(
                ['psql', '-h', 'localhost', '-U', 'postgres', '-d', 'postgres', '-c', "SELECT 1 FROM pg_database WHERE datname='rice_mill_erp'"],
                capture_output=True,
                text=True,
                env={**os.environ, 'PGPASSWORD': 'siva'},
                timeout=5
            )
        
        # If database doesn't exist (no rows returned)
        if "(0 rows)" in result.stdout or "0 rows" in result.stdout:
            print("🔧 Database 'rice_mill_erp' doesn't exist, creating...")
            
            if os.name == 'nt':  # Windows
                create_result = subprocess.run(
                    ['powershell', '-Command', 
                     "try { $env:PGPASSWORD='siva'; psql -h localhost -U postgres -d postgres -c \"CREATE DATABASE rice_mill_erp\" } catch { Write-Host 'Database creation failed' }"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:  # Linux/Mac
                create_result = subprocess.run(
                    ['psql', '-h', 'localhost', '-U', 'postgres', '-d', 'postgres', '-c', "CREATE DATABASE rice_mill_erp"],
                    capture_output=True,
                    text=True,
                    env={**os.environ, 'PGPASSWORD': 'siva'},
                    timeout=10
                )
            
            if "ERROR" in create_result.stdout or "ERROR" in create_result.stderr:
                print("❌ Failed to create database")
                print(f"Output: {create_result.stdout}")
                print(f"Error: {create_result.stderr}")
                return False
            else:
                print("✅ Database 'rice_mill_erp' created successfully")
                return True
        else:
            print("✅ Database 'rice_mill_erp' already exists")
            return True
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def run_migration():
    """Run the database migration script"""
    print("\n🚀 Running database migration...")
    
    try:
        # Change to backend directory
        os.chdir('backend')
        
        # Run the migration script
        result = subprocess.run(
            [sys.executable, 'migrations/create_all_tables.py', '--with-sample-data'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print("❌ Migration failed")
            print(f"Error: {result.stderr}")
            return False
        else:
            print("✅ Migration completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        return False
    finally:
        # Change back to original directory
        os.chdir('..')

def main():
    """Main function"""
    print("🐘 PostgreSQL Migration Runner")
    print("=" * 50)
    
    # Check if PostgreSQL is running
    if not check_postgresql():
        print("❌ Please make sure PostgreSQL is running and accessible")
        return False
    
    # Create database if it doesn't exist
    if not create_database():
        print("❌ Failed to create database")
        return False
    
    # Run migration
    if not run_migration():
        print("❌ Migration failed")
        return False
    
    print("\n🎉 PostgreSQL migration completed successfully!")
    print("=" * 50)
    print("✅ Database is now ready for use")
    print("✅ You can start the backend server with: python backend/app.py")
    print("✅ You can start the frontend server with: cd frontend && npm run dev")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
