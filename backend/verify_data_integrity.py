#!/usr/bin/env python3
"""
Verify data integrity and fix any remaining issues
"""

import os
import sys

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def check_missing_foreign_keys():
    """Check for missing foreign key constraints"""
    with app.app_context():
        try:
            print("Checking foreign key constraints...")
            
            # Check some key relationships
            checks = [
                ("farmers", "created_by", "users", "id"),
                ("farmer_contracts", "farmer_id", "farmers", "id"),
                ("paddy_procurements", "farmer_id", "farmers", "id"),
                ("payments", "farmer_id", "farmers", "id"),
                ("payments", "customer_id", "customers", "id"),
                ("user_preferences", "user_id", "users", "id")
            ]
            
            for table, fk_col, ref_table, ref_col in checks:
                # Check if FK constraint exists
                result = db.session.execute(text("""
                    SELECT constraint_name
                    FROM information_schema.table_constraints
                    WHERE table_name = :table
                    AND constraint_type = 'FOREIGN KEY'
                    AND constraint_name LIKE '%' || :fk_col || '%'
                """), {"table": table, "fk_col": fk_col})
                
                if result.fetchone():
                    print(f"  [OK] {table}.{fk_col} -> {ref_table}.{ref_col}")
                else:
                    print(f"  [MISSING] {table}.{fk_col} -> {ref_table}.{ref_col}")
            
            print("Foreign key check completed")
            
        except Exception as e:
            print(f"Error checking foreign keys: {e}")

def check_data_consistency():
    """Check for data consistency issues"""
    with app.app_context():
        try:
            print("Checking data consistency...")
            
            # Check for orphaned records
            orphan_checks = [
                ("farmer_contracts", "farmer_id", "farmers", "id"),
                ("paddy_procurements", "farmer_id", "farmers", "id"),
                ("payments", "farmer_id", "farmers", "id"),
                ("payments", "customer_id", "customers", "id")
            ]
            
            for table, fk_col, ref_table, ref_col in orphan_checks:
                result = db.session.execute(text(f"""
                    SELECT COUNT(*) 
                    FROM {table} t
                    WHERE t.{fk_col} IS NOT NULL 
                    AND NOT EXISTS (
                        SELECT 1 FROM {ref_table} r 
                        WHERE r.{ref_col} = t.{fk_col}
                    )
                """))
                
                orphan_count = result.fetchone()[0]
                if orphan_count > 0:
                    print(f"  [WARNING] {orphan_count} orphaned records in {table}.{fk_col}")
                else:
                    print(f"  [OK] No orphaned records in {table}.{fk_col}")
            
            print("Data consistency check completed")
            
        except Exception as e:
            print(f"Error checking data consistency: {e}")

def check_table_completeness():
    """Check if all expected tables exist"""
    with app.app_context():
        try:
            print("Checking table completeness...")
            
            # Get existing tables
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            existing_tables = [row[0] for row in result.fetchall()]
            
            # Expected core tables
            expected_tables = [
                'users', 'farmers', 'farmer_contracts', 'paddy_procurements',
                'customers', 'sales_orders', 'payments', 'expenses', 'budgets',
                'paddy_stock', 'product_stock', 'production_batches', 'quality_tests',
                'transactions', 'invoices', 'financial_alerts', 'user_preferences',
                'equipment', 'maintenance_schedules', 'maintenance_records',
                'deliveries', 'delivery_items', 'quality_parameters', 'quality_assessments',
                'regulations', 'compliance_records', 'performance_metrics', 'kpi_targets'
            ]
            
            missing_tables = []
            for table in expected_tables:
                if table in existing_tables:
                    print(f"  [OK] {table}")
                else:
                    print(f"  [MISSING] {table}")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"Missing {len(missing_tables)} expected tables")
            else:
                print("All expected tables exist!")
            
        except Exception as e:
            print(f"Error checking tables: {e}")

def verify_critical_columns():
    """Verify critical columns exist in key tables"""
    with app.app_context():
        try:
            print("Checking critical columns...")
            
            critical_columns = [
                ("farmers", ["farmer_code", "name", "phone", "is_active"]),
                ("farmer_contracts", ["contract_number", "farmer_id", "advance_amount", "contract_date"]),
                ("customers", ["customer_code", "name", "phone", "is_active"]),
                ("payments", ["payment_id", "payment_type", "payment_category", "amount"]),
                ("users", ["username", "email", "password_hash", "is_active"])
            ]
            
            for table, columns in critical_columns:
                print(f"  Checking {table}:")
                
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = :table_name
                """), {"table_name": table})
                
                existing_columns = [row[0] for row in result.fetchall()]
                
                for column in columns:
                    if column in existing_columns:
                        print(f"    [OK] {column}")
                    else:
                        print(f"    [MISSING] {column}")
            
            print("Critical columns check completed")
            
        except Exception as e:
            print(f"Error checking columns: {e}")

def main():
    """Run all verification checks"""
    print("Data Integrity Verification")
    print("=" * 60)
    
    check_table_completeness()
    print()
    
    verify_critical_columns()
    print()
    
    check_missing_foreign_keys()
    print()
    
    check_data_consistency()
    print()
    
    print("=" * 60)
    print("Data integrity verification completed!")

if __name__ == "__main__":
    main()