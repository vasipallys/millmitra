#!/usr/bin/env python3

"""
Simple Migration Script for Rice Mill ERP
Works with both PostgreSQL and SQLite
"""

import os
import sys

def run_migration():
    """Run the database migration"""
    print("🔧 Rice Mill ERP - Database Migration")
    print("=" * 50)
    
    try:
        # Change to backend directory
        original_dir = os.getcwd()
        os.chdir('backend')
        
        # Add backend to Python path
        sys.path.insert(0, os.getcwd())
        
        # Import and run migration
        print("📦 Importing migration module...")
        from migrations.create_all_tables import create_tables
        
        print("🚀 Running database migration...")
        create_tables()
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def main():
    """Main function"""
    success = run_migration()
    
    if success:
        print("\n✅ Database is ready!")
        print("🚀 You can now start the servers:")
        print("   Backend:  cd backend && python app.py")
        print("   Frontend: cd frontend && npm run dev")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
