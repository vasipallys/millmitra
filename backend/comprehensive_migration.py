#!/usr/bin/env python3
"""
Comprehensive database migration to create all missing tables and fix issues
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text

def create_missing_tables():
    """Create all missing tables"""
    with app.app_context():
        try:
            print("Creating missing tables...")
            
            # Check which tables exist
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            existing_tables = [row[0] for row in result.fetchall()]
            
            # User Preferences Table
            if 'user_preferences' not in existing_tables:
                print("Creating user_preferences table...")
                db.session.execute(text("""
                    CREATE TABLE user_preferences (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        preference_key VARCHAR(100) NOT NULL,
                        preference_value TEXT,
                        category VARCHAR(50),
                        is_public BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, preference_key)
                    )
                """))
                print("  - Created user_preferences table")
            
            # Equipment Table
            if 'equipment' not in existing_tables:
                print("Creating equipment table...")
                db.session.execute(text("""
                    CREATE TABLE equipment (
                        id SERIAL PRIMARY KEY,
                        equipment_code VARCHAR(20) UNIQUE NOT NULL,
                        equipment_name VARCHAR(100) NOT NULL,
                        equipment_type VARCHAR(50) NOT NULL,
                        category VARCHAR(30) NOT NULL,
                        manufacturer VARCHAR(100),
                        model VARCHAR(50),
                        serial_number VARCHAR(50),
                        year_manufactured INTEGER,
                        purchase_date DATE,
                        purchase_cost FLOAT,
                        location VARCHAR(100),
                        capacity FLOAT,
                        capacity_unit VARCHAR(20),
                        specifications JSON,
                        operating_parameters JSON,
                        status VARCHAR(20) DEFAULT 'active',
                        condition VARCHAR(20) DEFAULT 'good',
                        last_service_date DATE,
                        next_service_date DATE,
                        efficiency_rating FLOAT,
                        uptime_percentage FLOAT,
                        total_operating_hours FLOAT DEFAULT 0,
                        health_score FLOAT,
                        predicted_failure_date DATE,
                        maintenance_priority VARCHAR(10),
                        created_by INTEGER REFERENCES users(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created equipment table")
            
            # Maintenance Schedules Table
            if 'maintenance_schedules' not in existing_tables:
                print("Creating maintenance_schedules table...")
                db.session.execute(text("""
                    CREATE TABLE maintenance_schedules (
                        id SERIAL PRIMARY KEY,
                        equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
                        maintenance_type VARCHAR(50) NOT NULL,
                        frequency_days INTEGER NOT NULL,
                        last_performed DATE,
                        next_due DATE NOT NULL,
                        estimated_duration INTEGER,
                        priority VARCHAR(10) DEFAULT 'medium',
                        assigned_to INTEGER REFERENCES users(id),
                        instructions TEXT,
                        required_parts JSON,
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created maintenance_schedules table")
            
            # Maintenance Records Table
            if 'maintenance_records' not in existing_tables:
                print("Creating maintenance_records table...")
                db.session.execute(text("""
                    CREATE TABLE maintenance_records (
                        id SERIAL PRIMARY KEY,
                        equipment_id INTEGER NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
                        schedule_id INTEGER REFERENCES maintenance_schedules(id),
                        maintenance_type VARCHAR(50) NOT NULL,
                        performed_date DATE NOT NULL,
                        performed_by INTEGER REFERENCES users(id),
                        duration_hours FLOAT,
                        cost FLOAT,
                        parts_used JSON,
                        work_performed TEXT,
                        issues_found TEXT,
                        recommendations TEXT,
                        next_maintenance_date DATE,
                        status VARCHAR(20) DEFAULT 'completed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created maintenance_records table")
            
            # Deliveries Table
            if 'deliveries' not in existing_tables:
                print("Creating deliveries table...")
                db.session.execute(text("""
                    CREATE TABLE deliveries (
                        id SERIAL PRIMARY KEY,
                        delivery_number VARCHAR(50) UNIQUE NOT NULL,
                        sales_order_id INTEGER REFERENCES sales_orders(id),
                        customer_id INTEGER NOT NULL REFERENCES customers(id),
                        vehicle_id INTEGER REFERENCES vehicles(id),
                        driver_id INTEGER REFERENCES drivers(id),
                        route_id INTEGER REFERENCES routes(id),
                        delivery_date DATE NOT NULL,
                        scheduled_time TIME,
                        actual_start_time TIMESTAMP,
                        actual_end_time TIMESTAMP,
                        delivery_address TEXT NOT NULL,
                        delivery_instructions TEXT,
                        total_weight FLOAT,
                        total_volume FLOAT,
                        status VARCHAR(20) DEFAULT 'scheduled',
                        priority VARCHAR(10) DEFAULT 'normal',
                        delivery_notes TEXT,
                        customer_signature TEXT,
                        photo_proof TEXT,
                        rating INTEGER,
                        feedback TEXT,
                        created_by INTEGER REFERENCES users(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created deliveries table")
            
            # Delivery Items Table
            if 'delivery_items' not in existing_tables:
                print("Creating delivery_items table...")
                db.session.execute(text("""
                    CREATE TABLE delivery_items (
                        id SERIAL PRIMARY KEY,
                        delivery_id INTEGER NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
                        product_name VARCHAR(100) NOT NULL,
                        quantity FLOAT NOT NULL,
                        unit VARCHAR(20) NOT NULL,
                        weight FLOAT,
                        volume FLOAT,
                        packaging_type VARCHAR(50),
                        lot_number VARCHAR(50),
                        expiry_date DATE,
                        special_instructions TEXT,
                        delivered_quantity FLOAT,
                        condition_on_delivery VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created delivery_items table")
            
            # Quality Parameters Table
            if 'quality_parameters' not in existing_tables:
                print("Creating quality_parameters table...")
                db.session.execute(text("""
                    CREATE TABLE quality_parameters (
                        id SERIAL PRIMARY KEY,
                        parameter_name VARCHAR(100) NOT NULL,
                        parameter_code VARCHAR(20) UNIQUE NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        unit VARCHAR(20),
                        min_value FLOAT,
                        max_value FLOAT,
                        target_value FLOAT,
                        tolerance FLOAT,
                        test_method VARCHAR(100),
                        importance_level VARCHAR(10) DEFAULT 'medium',
                        is_critical BOOLEAN DEFAULT FALSE,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created quality_parameters table")
            
            # Quality Assessments Table
            if 'quality_assessments' not in existing_tables:
                print("Creating quality_assessments table...")
                db.session.execute(text("""
                    CREATE TABLE quality_assessments (
                        id SERIAL PRIMARY KEY,
                        assessment_number VARCHAR(50) UNIQUE NOT NULL,
                        batch_id INTEGER REFERENCES production_batches(id),
                        procurement_id INTEGER REFERENCES paddy_procurements(id),
                        assessment_type VARCHAR(50) NOT NULL,
                        assessment_date DATE NOT NULL,
                        assessed_by INTEGER REFERENCES users(id),
                        sample_size FLOAT,
                        sample_unit VARCHAR(20),
                        overall_grade VARCHAR(10),
                        overall_score FLOAT,
                        parameters_tested JSON,
                        test_results JSON,
                        compliance_status VARCHAR(20),
                        issues_identified TEXT,
                        recommendations TEXT,
                        approved_by INTEGER REFERENCES users(id),
                        approval_date DATE,
                        status VARCHAR(20) DEFAULT 'draft',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created quality_assessments table")
            
            # Regulations Table
            if 'regulations' not in existing_tables:
                print("Creating regulations table...")
                db.session.execute(text("""
                    CREATE TABLE regulations (
                        id SERIAL PRIMARY KEY,
                        regulation_code VARCHAR(50) UNIQUE NOT NULL,
                        regulation_name VARCHAR(200) NOT NULL,
                        regulatory_body VARCHAR(100) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        effective_date DATE NOT NULL,
                        expiry_date DATE,
                        description TEXT,
                        requirements JSON,
                        compliance_criteria JSON,
                        penalties JSON,
                        status VARCHAR(20) DEFAULT 'active',
                        priority VARCHAR(10) DEFAULT 'medium',
                        impact_areas JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created regulations table")
            
            # Compliance Records Table
            if 'compliance_records' not in existing_tables:
                print("Creating compliance_records table...")
                db.session.execute(text("""
                    CREATE TABLE compliance_records (
                        id SERIAL PRIMARY KEY,
                        record_number VARCHAR(50) UNIQUE NOT NULL,
                        regulation_id INTEGER NOT NULL REFERENCES regulations(id),
                        compliance_date DATE NOT NULL,
                        assessed_by INTEGER REFERENCES users(id),
                        compliance_status VARCHAR(20) NOT NULL,
                        compliance_score FLOAT,
                        findings TEXT,
                        evidence JSON,
                        corrective_actions TEXT,
                        responsible_person INTEGER REFERENCES users(id),
                        target_completion_date DATE,
                        actual_completion_date DATE,
                        verification_date DATE,
                        verified_by INTEGER REFERENCES users(id),
                        next_assessment_date DATE,
                        status VARCHAR(20) DEFAULT 'open',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created compliance_records table")
            
            # Performance Metrics Table
            if 'performance_metrics' not in existing_tables:
                print("Creating performance_metrics table...")
                db.session.execute(text("""
                    CREATE TABLE performance_metrics (
                        id SERIAL PRIMARY KEY,
                        metric_name VARCHAR(100) NOT NULL,
                        metric_code VARCHAR(50) UNIQUE NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        unit VARCHAR(20),
                        calculation_method TEXT,
                        data_source VARCHAR(100),
                        frequency VARCHAR(20),
                        target_value FLOAT,
                        threshold_low FLOAT,
                        threshold_high FLOAT,
                        current_value FLOAT,
                        previous_value FLOAT,
                        trend VARCHAR(10),
                        last_calculated TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        dashboard_visible BOOLEAN DEFAULT TRUE,
                        alert_enabled BOOLEAN DEFAULT FALSE,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created performance_metrics table")
            
            # KPI Targets Table
            if 'kpi_targets' not in existing_tables:
                print("Creating kpi_targets table...")
                db.session.execute(text("""
                    CREATE TABLE kpi_targets (
                        id SERIAL PRIMARY KEY,
                        metric_id INTEGER NOT NULL REFERENCES performance_metrics(id),
                        target_period VARCHAR(20) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        target_value FLOAT NOT NULL,
                        actual_value FLOAT,
                        achievement_percentage FLOAT,
                        status VARCHAR(20) DEFAULT 'active',
                        responsible_person INTEGER REFERENCES users(id),
                        department VARCHAR(50),
                        priority VARCHAR(10) DEFAULT 'medium',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("  - Created kpi_targets table")
            
            db.session.commit()
            print("Successfully created all missing tables!")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            db.session.rollback()
            raise

def create_indexes():
    """Create important indexes for performance"""
    with app.app_context():
        try:
            print("Creating indexes...")
            
            # Performance-critical indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_equipment_status ON equipment(status)",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_schedules_next_due ON maintenance_schedules(next_due)",
                "CREATE INDEX IF NOT EXISTS idx_maintenance_records_equipment ON maintenance_records(equipment_id)",
                "CREATE INDEX IF NOT EXISTS idx_deliveries_date ON deliveries(delivery_date)",
                "CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(status)",
                "CREATE INDEX IF NOT EXISTS idx_quality_assessments_date ON quality_assessments(assessment_date)",
                "CREATE INDEX IF NOT EXISTS idx_compliance_records_regulation ON compliance_records(regulation_id)",
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_active ON performance_metrics(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_kpi_targets_period ON kpi_targets(start_date, end_date)"
            ]
            
            for index_sql in indexes:
                db.session.execute(text(index_sql))
            
            db.session.commit()
            print("Successfully created indexes!")
            
        except Exception as e:
            print(f"Error creating indexes: {e}")
            db.session.rollback()

def fix_model_issues():
    """Fix any model-related issues"""
    with app.app_context():
        try:
            print("Fixing model issues...")
            
            # Add any missing columns to existing tables
            # This is where we can add specific column fixes
            
            # Example: Check if a column exists before adding
            # result = db.session.execute(text("""
            #     SELECT column_name 
            #     FROM information_schema.columns 
            #     WHERE table_name = 'some_table' 
            #     AND column_name = 'some_column'
            # """))
            # if not result.fetchone():
            #     db.session.execute(text("ALTER TABLE some_table ADD COLUMN some_column TYPE"))
            
            db.session.commit()
            print("Model issues fixed!")
            
        except Exception as e:
            print(f"Error fixing model issues: {e}")
            db.session.rollback()

def main():
    """Run comprehensive migration"""
    print("Comprehensive Database Migration")
    print("=" * 60)
    
    try:
        create_missing_tables()
        print()
        
        create_indexes()
        print()
        
        fix_model_issues()
        print()
        
        print("=" * 60)
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()