#!/usr/bin/env python3
"""
Check database schema and compare with model definitions
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from sqlalchemy import text, inspect

def get_existing_tables():
    """Get list of existing tables in the database"""
    with app.app_context():
        try:
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            return tables
        except Exception as e:
            print(f"Error getting tables: {e}")
            return []

def get_table_columns(table_name):
    """Get columns for a specific table"""
    with app.app_context():
        try:
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = :table_name 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """), {"table_name": table_name})
            
            columns = []
            for row in result.fetchall():
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3]
                })
            return columns
        except Exception as e:
            print(f"Error getting columns for {table_name}: {e}")
            return []

def check_model_tables():
    """Check which model tables are defined"""
    model_tables = {
        # Core models
        'users': 'User model',
        'farmers': 'Farmer model',
        'farmer_contracts': 'FarmerContract model',
        'paddy_procurements': 'PaddyProcurement model',
        'customers': 'Customer model',
        'sales_orders': 'SalesOrder model',
        'payments': 'Payment model',
        'expenses': 'Expense model',
        'budgets': 'Budget model',
        
        # Inventory models
        'paddy_stock': 'PaddyStock model',
        'product_stock': 'ProductStock model',
        
        # Production models
        'production_batches': 'ProductionBatch model',
        'quality_tests': 'QualityTest model',
        
        # Financial models
        'transactions': 'Transaction model',
        'invoices': 'Invoice model',
        'financial_alerts': 'FinancialAlert model',
        'cash_flow_forecasts': 'CashFlowForecast model',
        'financial_health_scores': 'FinancialHealthScore model',
        'payment_schedules': 'PaymentSchedule model',
        
        # User management
        'auth_logs': 'AuthLog model',
        'user_sessions': 'UserSession model',
        'user_preferences': 'UserPreference model',
        
        # Edit requests
        'farmer_edit_requests': 'FarmerEditRequest model',
        
        # AI models
        'ai_interactions': 'AIInteraction model',
        
        # Supply chain models
        'suppliers': 'Supplier model',
        'supplier_contracts': 'SupplierContract model',
        'procurement_requests': 'ProcurementRequest model',
        'procurement_request_items': 'ProcurementRequestItem model',
        
        # Logistics models
        'vehicles': 'Vehicle model',
        'drivers': 'Driver model',
        'routes': 'Route model',
        'deliveries': 'Delivery model',
        'delivery_items': 'DeliveryItem model',
        
        # Maintenance models
        'equipment': 'Equipment model',
        'maintenance_schedules': 'MaintenanceSchedule model',
        'maintenance_records': 'MaintenanceRecord model',
        
        # Quality models
        'quality_parameters': 'QualityParameter model',
        'quality_standards': 'QualityStandard model',
        'quality_assessments': 'QualityAssessment model',
        
        # Compliance models
        'regulations': 'Regulation model',
        'compliance_records': 'ComplianceRecord model',
        'audit_trails': 'AuditTrail model',
        'compliance_alerts': 'ComplianceAlert model',
        
        # Analytics models
        'performance_metrics': 'PerformanceMetric model',
        'kpi_targets': 'KPITarget model',
        'dashboard_widgets': 'DashboardWidget model'
    }
    return model_tables

def main():
    """Main function to check database schema"""
    print("Database Schema Analysis")
    print("=" * 60)
    
    # Get existing tables
    existing_tables = get_existing_tables()
    print(f"Found {len(existing_tables)} existing tables:")
    for table in existing_tables:
        print(f"  - {table}")
    
    print("\n" + "=" * 60)
    
    # Get expected model tables
    model_tables = check_model_tables()
    print(f"Expected {len(model_tables)} model tables:")
    
    missing_tables = []
    for table_name, description in model_tables.items():
        if table_name in existing_tables:
            print(f"  [EXISTS] {table_name} - {description}")
        else:
            print(f"  [MISSING] {table_name} - {description}")
            missing_tables.append(table_name)
    
    print("\n" + "=" * 60)
    
    if missing_tables:
        print(f"Missing Tables ({len(missing_tables)}):")
        for table in missing_tables:
            print(f"  - {table}")
    else:
        print("All expected tables exist!")
    
    print("\n" + "=" * 60)
    
    # Check some key tables for column completeness
    key_tables = ['farmers', 'farmer_contracts', 'customers', 'payments', 'users']
    print("Checking key tables for column details:")
    
    for table in key_tables:
        if table in existing_tables:
            print(f"\n{table.upper()} TABLE:")
            columns = get_table_columns(table)
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col['default'] else ""
                print(f"  - {col['name']}: {col['type']} {nullable}{default}")
        else:
            print(f"\n{table.upper()} TABLE: MISSING")

if __name__ == "__main__":
    main()