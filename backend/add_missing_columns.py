#!/usr/bin/env python3
"""
Add missing columns and tables to the database
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def add_missing_columns():
    """Add missing columns to existing tables"""
    with app.app_context():
        try:
            # Add missing columns to farmer_contracts table
            print("Adding missing columns to farmer_contracts table...")
            
            # Check if columns exist first
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'farmer_contracts' 
                AND table_schema = 'public'
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'advance_amount' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE farmer_contracts 
                    ADD COLUMN advance_amount FLOAT DEFAULT 0.0
                """))
                print("Success: Added advance_amount column to farmer_contracts")
            else:
                print("Info: advance_amount column already exists")
            
            if 'contract_date' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE farmer_contracts 
                    ADD COLUMN contract_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """))
                print("Success: Added contract_date column to farmer_contracts")
            else:
                print("Info: contract_date column already exists")
            
            db.session.commit()
            print("Success: Successfully added missing columns to farmer_contracts")
            
        except Exception as e:
            print(f"Error: Error adding columns: {e}")
            db.session.rollback()

def create_paddy_procurement_table():
    """Create the paddy_procurements table if it doesn't exist"""
    with app.app_context():
        try:
            # Check if table exists
            result = db.session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'paddy_procurements'
                )
            """))
            table_exists = result.fetchone()[0]
            
            if not table_exists:
                print("Creating paddy_procurements table...")
                db.session.execute(text("""
                    CREATE TABLE paddy_procurements (
                        id SERIAL PRIMARY KEY,
                        procurement_number VARCHAR(50) UNIQUE NOT NULL,
                        farmer_id INTEGER NOT NULL REFERENCES farmers(id),
                        variety VARCHAR(50) NOT NULL,
                        quantity FLOAT NOT NULL,
                        moisture_content FLOAT,
                        quality_grade VARCHAR(10),
                        price_per_kg FLOAT NOT NULL,
                        total_amount FLOAT NOT NULL,
                        broken_percentage FLOAT,
                        foreign_matter FLOAT,
                        chalky_grains FLOAT,
                        procurement_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'pending',
                        payment_status VARCHAR(20) DEFAULT 'pending',
                        notes TEXT,
                        created_by INTEGER REFERENCES users(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create index on farmer_id for performance
                db.session.execute(text("""
                    CREATE INDEX idx_paddy_procurements_farmer_id ON paddy_procurements(farmer_id)
                """))
                
                # Create index on procurement_date for performance
                db.session.execute(text("""
                    CREATE INDEX idx_paddy_procurements_date ON paddy_procurements(procurement_date)
                """))
                
                db.session.commit()
                print("Success: Successfully created paddy_procurements table")
            else:
                print("Info: paddy_procurements table already exists")
                
        except Exception as e:
            print(f"Error: Error creating paddy_procurements table: {e}")
            db.session.rollback()

def main():
    """Run all migrations"""
    print("Starting database migration...")
    print("=" * 50)
    
    # Add missing columns
    add_missing_columns()
    print()
    
    # Create missing tables
    create_paddy_procurement_table()
    print()
    
    print("=" * 50)
    print("Database migration completed!")

if __name__ == "__main__":
    main()