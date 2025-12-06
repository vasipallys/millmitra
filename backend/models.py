"""
Consolidated Models File
All database models for the Rice Mill Management System
"""

from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

# Import all models from the models directory
from models.user import User, AuthLog, UserSession
from models.farmer import Farmer
from models.inventory import ProductStock, PaddyStock
from models.production import ProductionBatch, QualityTest
from models.sales import Customer
from models.finance import Transaction, Payment, Expense
from models.financial import Invoice

# Re-export all models for easy importing
__all__ = [
    'User',
    'AuthLog',
    'UserSession',
    'Farmer',
    'ProductStock',
    'PaddyStock',
    'ProductionBatch',
    'QualityTest',
    'Customer',
    'Invoice',
    'Transaction',
    'Payment',
    'Expense'
]

# Additional utility functions for models
def init_db():
    """Initialize database with all tables"""
    db.create_all()

def drop_all():
    """Drop all tables"""
    db.drop_all()

def reset_db():
    """Reset database - drop and recreate all tables"""
    db.drop_all()
    db.create_all()

# Model validation functions
def validate_phone(phone):
    """Validate phone number format"""
    if not phone:
        return False
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    return len(digits) == 10

def validate_email(email):
    """Validate email format"""
    if not email:
        return False
    return '@' in email and '.' in email.split('@')[1]

def validate_gstin(gstin):
    """Validate GSTIN format"""
    if not gstin:
        return False
    return len(gstin) == 15 and gstin[:2].isdigit()

# Database utility functions
def get_or_create(session, model, **kwargs):
    """Get existing record or create new one"""
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance, True

def safe_commit(session):
    """Safely commit database changes"""
    try:
        session.commit()
        return True, None
    except Exception as e:
        session.rollback()
        return False, str(e)

# Model mixins for common functionality
class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime)
    
    def soft_delete(self):
        """Mark record as deleted"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft deleted record"""
        self.is_deleted = False
        self.deleted_at = None

# Query helpers
class BaseQuery:
    """Base query helpers for models"""
    
    @classmethod
    def get_active(cls):
        """Get only active (non-deleted) records"""
        if hasattr(cls, 'is_deleted'):
            return cls.query.filter(cls.is_deleted == False)
        return cls.query
    
    @classmethod
    def get_by_id(cls, id):
        """Get record by ID"""
        return cls.query.get(id)
    
    @classmethod
    def get_recent(cls, limit=10):
        """Get recent records"""
        if hasattr(cls, 'created_at'):
            return cls.query.order_by(cls.created_at.desc()).limit(limit)
        return cls.query.limit(limit)

# Data export helpers
def export_model_data(model_class, format='json'):
    """Export model data in specified format"""
    try:
        records = model_class.query.all()
        data = []
        
        for record in records:
            if hasattr(record, 'to_dict'):
                data.append(record.to_dict())
            else:
                # Fallback to basic serialization
                record_dict = {}
                for column in record.__table__.columns:
                    value = getattr(record, column.name)
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    record_dict[column.name] = value
                data.append(record_dict)
        
        if format == 'json':
            return json.dumps(data, indent=2)
        elif format == 'csv':
            # Basic CSV export
            if data:
                import csv
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
                return output.getvalue()
        
        return data
        
    except Exception as e:
        return f"Export error: {str(e)}"

# Database statistics
def get_database_stats():
    """Get database statistics"""
    stats = {}
    
    models = [User, Farmer, Customer, Transaction, Invoice, ProductionBatch, QualityTest]
    
    for model in models:
        try:
            count = model.query.count()
            stats[model.__tablename__] = count
        except Exception as e:
            stats[model.__tablename__] = f"Error: {str(e)}"
    
    return stats

# Data integrity checks
def check_data_integrity():
    """Check data integrity across models"""
    issues = []
    
    try:
        # Check for orphaned records
        # Transactions without users
        orphaned_transactions = Transaction.query.filter(
            Transaction.created_by.is_(None)
        ).count()
        
        if orphaned_transactions > 0:
            issues.append(f"{orphaned_transactions} transactions without user reference")
        
        # Invoices without customers
        orphaned_invoices = Invoice.query.filter(
            Invoice.customer_id.is_(None)
        ).count()
        
        if orphaned_invoices > 0:
            issues.append(f"{orphaned_invoices} invoices without customer reference")
        
        # Production batches without dates
        invalid_batches = ProductionBatch.query.filter(
            ProductionBatch.production_date.is_(None)
        ).count()
        
        if invalid_batches > 0:
            issues.append(f"{invalid_batches} production batches without dates")
        
    except Exception as e:
        issues.append(f"Integrity check error: {str(e)}")
    
    return issues

# Model relationship helpers
def get_model_relationships():
    """Get information about model relationships"""
    relationships = {}
    
    models = [User, Farmer, Customer, Transaction, Invoice, ProductionBatch, QualityTest]
    
    for model in models:
        model_relationships = []
        
        # Get foreign keys
        for column in model.__table__.columns:
            if column.foreign_keys:
                for fk in column.foreign_keys:
                    model_relationships.append({
                        'column': column.name,
                        'references': str(fk.column)
                    })
        
        relationships[model.__tablename__] = model_relationships
    
    return relationships

# Backup and restore functions
def create_backup():
    """Create database backup"""
    try:
        backup_data = {}
        models = [User, Farmer, Customer, Transaction, Invoice, ProductionBatch, QualityTest]
        
        for model in models:
            backup_data[model.__tablename__] = export_model_data(model, format='dict')
        
        backup_data['backup_timestamp'] = datetime.utcnow().isoformat()
        backup_data['backup_version'] = '1.0'
        
        return backup_data
        
    except Exception as e:
        return {'error': f"Backup failed: {str(e)}"}

def restore_backup(backup_data):
    """Restore database from backup"""
    try:
        if 'error' in backup_data:
            return False, backup_data['error']
        
        # This would implement backup restoration logic
        # For safety, this is a placeholder
        return True, "Backup restoration would be implemented here"
        
    except Exception as e:
        return False, f"Restore failed: {str(e)}"

# Performance optimization helpers
def optimize_database():
    """Optimize database performance"""
    optimizations = []
    
    try:
        # Add indexes for frequently queried columns
        index_commands = [
            "CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions(transaction_date);",
            "CREATE INDEX IF NOT EXISTS idx_invoice_date ON invoices(invoice_date);",
            "CREATE INDEX IF NOT EXISTS idx_production_date ON production_batches(production_date);",
            "CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers(phone);",
            "CREATE INDEX IF NOT EXISTS idx_farmer_phone ON farmers(phone);"
        ]
        
        for command in index_commands:
            try:
                db.session.execute(command)
                optimizations.append(f"Executed: {command}")
            except Exception as e:
                optimizations.append(f"Failed: {command} - {str(e)}")
        
        db.session.commit()
        
    except Exception as e:
        optimizations.append(f"Optimization error: {str(e)}")
        db.session.rollback()
    
    return optimizations

# Health check for models
def health_check():
    """Perform health check on all models"""
    health_status = {
        'status': 'healthy',
        'checks': [],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    models = [User, Farmer, Customer, Transaction, Invoice, ProductionBatch, QualityTest]
    
    for model in models:
        try:
            count = model.query.count()
            health_status['checks'].append({
                'model': model.__tablename__,
                'status': 'ok',
                'record_count': count
            })
        except Exception as e:
            health_status['checks'].append({
                'model': model.__tablename__,
                'status': 'error',
                'error': str(e)
            })
            health_status['status'] = 'unhealthy'
    
    return health_status
