"""
Database migration script to create all tables for Rice Mill ERP
"""

from flask import Flask
from database import db
from config import Config

# Import all models to ensure they're registered
from models.user import User, Role, Permission
from models.farmer import Farmer, Contract, Procurement
from models.inventory import InventoryItem, StockMovement, Warehouse
from models.production import ProductionBatch, ProductionStep, QualityTest
from models.sales import Customer, SalesOrder, SalesOrderItem
from models.finance import Transaction, Invoice, Payment
from models.supply_chain import Supplier, PurchaseOrder, PurchaseOrderItem
from models.logistics import Vehicle, Driver, Shipment, ShipmentItem
from models.compliance import ComplianceFramework, ComplianceAssessment, RegulatoryDocument

def create_tables():
    """Create all database tables"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        # Drop all tables (use with caution in production)
        # db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("All tables created successfully!")
        
        # Create default roles and permissions
        create_default_roles()
        
        print("Default roles and permissions created!")

def create_default_roles():
    """Create default roles and permissions"""
    # Create permissions
    permissions = [
        'user_management', 'farmer_management', 'inventory_management',
        'production_management', 'sales_management', 'finance_management',
        'supply_chain_management', 'logistics_management', 'compliance_management',
        'analytics_access', 'quality_management', 'system_admin'
    ]
    
    for perm_name in permissions:
        if not Permission.query.filter_by(name=perm_name).first():
            permission = Permission(name=perm_name, description=f"{perm_name.replace('_', ' ').title()}")
            db.session.add(permission)
    
    # Create roles
    roles_config = {
        'super_admin': {
            'description': 'Super Administrator with all permissions',
            'permissions': permissions
        },
        'admin': {
            'description': 'Administrator with most permissions',
            'permissions': [p for p in permissions if p != 'system_admin']
        },
        'manager': {
            'description': 'Manager with operational permissions',
            'permissions': [
                'farmer_management', 'inventory_management', 'production_management',
                'sales_management', 'supply_chain_management', 'logistics_management',
                'quality_management', 'analytics_access'
            ]
        },
        'operator': {
            'description': 'Operator with limited permissions',
            'permissions': [
                'inventory_management', 'production_management', 'quality_management'
            ]
        },
        'viewer': {
            'description': 'Read-only access',
            'permissions': ['analytics_access']
        }
    }
    
    for role_name, role_config in roles_config.items():
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=role_config['description'])
            
            # Add permissions to role
            for perm_name in role_config['permissions']:
                permission = Permission.query.filter_by(name=perm_name).first()
                if permission:
                    role.permissions.append(permission)
            
            db.session.add(role)
    
    # Create default admin user
    if not User.query.filter_by(username='admin').first():
        admin_role = Role.query.filter_by(name='super_admin').first()
        admin_user = User(
            username='admin',
            email='admin@ricemill.com',
            full_name='System Administrator',
            is_active=True
        )
        admin_user.set_password('admin123')  # Change this in production
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
    
    db.session.commit()

if __name__ == '__main__':
    create_tables()