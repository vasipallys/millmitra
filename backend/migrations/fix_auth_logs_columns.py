#!/usr/bin/env python3

"""
Fix auth_logs table column sizes
Fixes the device_fingerprint and user_agent columns to handle longer data
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def fix_auth_logs_columns():
    """Fix auth_logs table column sizes"""

    print("🔧 Fixing auth_logs table column sizes...")

    with app.app_context():
        try:
            # Detect database type
            db_url = str(db.engine.url)
            is_sqlite = 'sqlite' in db_url
            is_postgres = 'postgresql' in db_url
            is_mysql = 'mysql' in db_url

            print(f"📊 Database type detected: {db_url.split(':')[0]}")

            # Check if auth_logs table exists (universal query)
            if is_sqlite:
                result = db.session.execute(text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table' AND name='auth_logs';
                """))
                table_exists = result.scalar() is not None
            else:
                # PostgreSQL/MySQL
                result = db.session.execute(text("""
                    SELECT table_name FROM information_schema.tables
                    WHERE table_name = 'auth_logs';
                """))
                table_exists = result.scalar() is not None

            if not table_exists:
                print("❌ auth_logs table does not exist. Creating tables first...")
                db.create_all()
                print("✅ Tables created successfully")
                return
            
            print("📋 Checking current column types...")

            if is_sqlite:
                # SQLite: Recreate table with correct column types
                print("🔧 SQLite detected - recreating table with correct column types...")

                # Create new table with correct structure
                db.session.execute(text("""
                    CREATE TABLE auth_logs_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        username_attempted VARCHAR(320),
                        action VARCHAR(50),
                        method VARCHAR(50),
                        success BOOLEAN,
                        ip_address VARCHAR(45),
                        user_agent TEXT,
                        device_fingerprint TEXT,
                        location VARCHAR(500),
                        failure_reason VARCHAR(500),
                        risk_score FLOAT,
                        timestamp DATETIME,
                        FOREIGN KEY(user_id) REFERENCES users (id)
                    );
                """))

                # Copy data from old table
                db.session.execute(text("""
                    INSERT INTO auth_logs_new
                    SELECT * FROM auth_logs;
                """))

                # Drop old table and rename new one
                db.session.execute(text("DROP TABLE auth_logs;"))
                db.session.execute(text("ALTER TABLE auth_logs_new RENAME TO auth_logs;"))

            else:
                # PostgreSQL/MySQL: Use ALTER COLUMN
                print("🔧 PostgreSQL/MySQL detected - altering column types...")

                # Check current column types
                result = db.session.execute(text("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'auth_logs'
                    AND column_name IN ('device_fingerprint', 'user_agent')
                    ORDER BY column_name;
                """))

                columns = result.fetchall()
                print("Current column types:")
                for col in columns:
                    print(f"  {col[0]}: {col[1]} ({col[2]} chars)")

                # Fix device_fingerprint column
                print("🔧 Updating device_fingerprint column to TEXT...")
                if is_postgres:
                    db.session.execute(text("ALTER TABLE auth_logs ALTER COLUMN device_fingerprint TYPE TEXT;"))
                else:  # MySQL
                    db.session.execute(text("ALTER TABLE auth_logs MODIFY device_fingerprint TEXT;"))

                # Fix user_agent column
                print("🔧 Updating user_agent column to TEXT...")
                if is_postgres:
                    db.session.execute(text("ALTER TABLE auth_logs ALTER COLUMN user_agent TYPE TEXT;"))
                else:  # MySQL
                    db.session.execute(text("ALTER TABLE auth_logs MODIFY user_agent TEXT;"))

                # Update other columns
                print("🔧 Updating other varchar columns...")

                if is_postgres:
                    db.session.execute(text("ALTER TABLE auth_logs ALTER COLUMN username_attempted TYPE VARCHAR(320);"))
                    db.session.execute(text("ALTER TABLE auth_logs ALTER COLUMN location TYPE VARCHAR(500);"))
                    db.session.execute(text("ALTER TABLE auth_logs ALTER COLUMN failure_reason TYPE VARCHAR(500);"))
                else:  # MySQL
                    db.session.execute(text("ALTER TABLE auth_logs MODIFY username_attempted VARCHAR(320);"))
                    db.session.execute(text("ALTER TABLE auth_logs MODIFY location VARCHAR(500);"))
                    db.session.execute(text("ALTER TABLE auth_logs MODIFY failure_reason VARCHAR(500);"))
            
            # Commit changes
            db.session.commit()
            
            print("\n✅ Column updates completed successfully!")
            
            # Verify changes
            print("\n📋 Verifying updated column types...")

            if is_sqlite:
                # SQLite: Check table structure
                result = db.session.execute(text("PRAGMA table_info(auth_logs);"))
                columns = result.fetchall()
                print("Updated column types (SQLite):")
                for col in columns:
                    if col[1] in ['device_fingerprint', 'user_agent', 'username_attempted', 'location', 'failure_reason']:
                        print(f"  ✅ {col[1]}: {col[2]}")
            else:
                # PostgreSQL/MySQL: Check information_schema
                result = db.session.execute(text("""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'auth_logs'
                    AND column_name IN ('device_fingerprint', 'user_agent', 'username_attempted', 'location', 'failure_reason')
                    ORDER BY column_name;
                """))

                columns = result.fetchall()
                print("Updated column types:")
                for col in columns:
                    max_length = col[2] if col[2] else "unlimited"
                    print(f"  ✅ {col[0]}: {col[1]} ({max_length} chars)")
            
        except Exception as e:
            print(f"❌ Error fixing auth_logs columns: {e}")
            db.session.rollback()
            raise
        finally:
            db.session.close()

def test_auth_logs_insert():
    """Test inserting a record with long device fingerprint"""
    
    print("\n🧪 Testing auth_logs insert with long data...")
    
    with app.app_context():
        try:
            from models.user import AuthLog
            from datetime import datetime
            
            # Create a test record with long device fingerprint
            test_log = AuthLog(
                username_attempted='test@example.com',
                action='login',
                method='password',
                success=False,
                ip_address='127.0.0.1',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
                device_fingerprint='eyJjYW52YXMiOiJkYXRhOmltYWdlL3BuZztiYXNlNjQsaVZCT1J3MEtHZ29BQUFBTlNVaEVVZ0FBQVN3QUFBQ1dDQVlBQUFCa1c3WFNBQUFBQVhOU1IwSUFyczRjNlFBQUNOcEpSRUZVZUY3dDI3d' * 50,  # Very long fingerprint
                location='Test Location',
                failure_reason='test_insert',
                risk_score=0.5,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(test_log)
            db.session.commit()
            
            print("✅ Test insert successful - long data handled correctly!")
            
            # Clean up test record
            db.session.delete(test_log)
            db.session.commit()
            print("✅ Test record cleaned up")
            
        except Exception as e:
            print(f"❌ Test insert failed: {e}")
            db.session.rollback()
        finally:
            db.session.close()

if __name__ == "__main__":
    print("🔧 Auth Logs Column Fix Migration")
    print("=" * 50)
    
    fix_auth_logs_columns()
    test_auth_logs_insert()
    
    print("\n🎉 Migration completed successfully!")
    print("The auth_logs table can now handle long device fingerprints and user agents.")
