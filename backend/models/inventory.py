from extensions import db
from datetime import datetime
import json

class PaddyStock(db.Model):
    __tablename__ = 'paddy_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Paddy details
    variety = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(10), default='A')
    quantity = db.Column(db.Float, nullable=False)  # in kg
    unit_price = db.Column(db.Float)
    total_value = db.Column(db.Float)
    
    # Quality parameters
    moisture_content = db.Column(db.Float)
    foreign_matter_percentage = db.Column(db.Float)
    broken_percentage = db.Column(db.Float)
    chalky_percentage = db.Column(db.Float)
    
    # AI quality assessment
    ai_quality_score = db.Column(db.Float)
    ai_quality_grade = db.Column(db.String(10))
    quality_factors = db.Column(db.Text)  # JSON
    
    # Storage details
    storage_location = db.Column(db.String(50))
    storage_type = db.Column(db.String(20))  # bulk, bagged
    storage_conditions = db.Column(db.Text)  # JSON
    
    # Supplier information
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    purchase_date = db.Column(db.Date)
    lot_number = db.Column(db.String(30))
    
    # Status
    status = db.Column(db.String(20), default='available')  # available, reserved, processing
    reserved_quantity = db.Column(db.Float, default=0)
    available_quantity = db.Column(db.Float)
    
    # AI predictions
    predicted_processing_yield = db.Column(db.Float)
    predicted_quality_degradation = db.Column(db.Float)
    optimal_processing_date = db.Column(db.Date)
    
    # Timestamps
    received_date = db.Column(db.Date, default=datetime.utcnow)
    last_inspection_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'variety': self.variety,
            'grade': self.grade,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_value': self.total_value,
            'moisture_content': self.moisture_content,
            'foreign_matter_percentage': self.foreign_matter_percentage,
            'broken_percentage': self.broken_percentage,
            'chalky_percentage': self.chalky_percentage,
            'ai_quality_score': self.ai_quality_score,
            'ai_quality_grade': self.ai_quality_grade,
            'quality_factors': json.loads(self.quality_factors) if self.quality_factors else [],
            'storage_location': self.storage_location,
            'storage_type': self.storage_type,
            'storage_conditions': json.loads(self.storage_conditions) if self.storage_conditions else [],
            'supplier_id': self.supplier_id,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'lot_number': self.lot_number,
            'status': self.status,
            'reserved_quantity': self.reserved_quantity,
            'available_quantity': self.available_quantity,
            'predicted_processing_yield': self.predicted_processing_yield,
            'predicted_quality_degradation': self.predicted_quality_degradation,
            'optimal_processing_date': self.optimal_processing_date.isoformat() if self.optimal_processing_date else None,
            'received_date': self.received_date.isoformat() if self.received_date else None,
            'last_inspection_date': self.last_inspection_date.isoformat() if self.last_inspection_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'age_days': (datetime.now().date() - self.received_date).days if self.received_date else 0
        }

class ProductStock(db.Model):
    __tablename__ = 'product_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Product details
    product_type = db.Column(db.String(50), nullable=False)  # rice, bran, husk
    product_name = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.String(10), default='A')
    packaging = db.Column(db.String(30))  # 25kg, 50kg, bulk
    
    # Quantity and pricing
    quantity = db.Column(db.Float, nullable=False)  # in kg
    unit_price = db.Column(db.Float)
    total_value = db.Column(db.Float)
    
    # Production details
    production_batch_id = db.Column(db.Integer, db.ForeignKey('production_batches.id'))
    production_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    
    # Quality parameters
    broken_percentage = db.Column(db.Float)
    head_rice_percentage = db.Column(db.Float)
    moisture_content = db.Column(db.Float)
    
    # AI quality assessment
    ai_quality_score = db.Column(db.Float)
    predicted_shelf_life = db.Column(db.Integer)  # days
    quality_trend = db.Column(db.String(20))  # improving, stable, declining
    
    # Storage details
    storage_location = db.Column(db.String(50))
    storage_conditions = db.Column(db.Text)  # JSON
    
    # Inventory management
    reorder_point = db.Column(db.Float)
    max_stock_level = db.Column(db.Float)
    reserved_quantity = db.Column(db.Float, default=0)
    available_quantity = db.Column(db.Float)
    
    # AI predictions
    predicted_demand = db.Column(db.Float)
    sales_velocity = db.Column(db.Float)  # units per day
    stockout_risk = db.Column(db.String(20))  # low, medium, high
    
    # Status
    status = db.Column(db.String(20), default='available')  # available, reserved, sold, damaged
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'product_type': self.product_type,
            'product_name': self.product_name,
            'grade': self.grade,
            'packaging': self.packaging,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_value': self.total_value,
            'production_batch_id': self.production_batch_id,
            'production_date': self.production_date.isoformat() if self.production_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'broken_percentage': self.broken_percentage,
            'head_rice_percentage': self.head_rice_percentage,
            'moisture_content': self.moisture_content,
            'ai_quality_score': self.ai_quality_score,
            'predicted_shelf_life': self.predicted_shelf_life,
            'quality_trend': self.quality_trend,
            'storage_location': self.storage_location,
            'storage_conditions': json.loads(self.storage_conditions) if self.storage_conditions else [],
            'reorder_point': self.reorder_point,
            'max_stock_level': self.max_stock_level,
            'reserved_quantity': self.reserved_quantity,
            'available_quantity': self.available_quantity,
            'predicted_demand': self.predicted_demand,
            'sales_velocity': self.sales_velocity,
            'stockout_risk': self.stockout_risk,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'age_days': (datetime.now().date() - self.production_date).days if self.production_date else 0
        }

class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Transaction details
    transaction_type = db.Column(db.String(30), nullable=False)  # purchase, sale, transfer, adjustment
    transaction_subtype = db.Column(db.String(30))  # inbound, outbound, internal
    
    # Item details
    item_type = db.Column(db.String(20), nullable=False)  # paddy, product
    item_id = db.Column(db.Integer, nullable=False)  # paddy_stock_id or product_stock_id
    item_name = db.Column(db.String(100))
    
    # Quantity and pricing
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float)
    total_value = db.Column(db.Float)
    
    # Before/after quantities
    quantity_before = db.Column(db.Float)
    quantity_after = db.Column(db.Float)
    
    # Reference information
    reference_type = db.Column(db.String(30))  # sales_order, purchase_order, production_batch
    reference_id = db.Column(db.Integer)
    reference_number = db.Column(db.String(50))
    
    # Location details
    from_location = db.Column(db.String(50))
    to_location = db.Column(db.String(50))
    
    # AI analysis
    ai_validated = db.Column(db.Boolean, default=False)
    fraud_risk_score = db.Column(db.Float)
    anomaly_flags = db.Column(db.Text)  # JSON
    
    # Additional details
    notes = db.Column(db.Text)
    batch_number = db.Column(db.String(30))
    
    # Timestamps
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_code': self.transaction_code,
            'transaction_type': self.transaction_type,
            'transaction_subtype': self.transaction_subtype,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_value': self.total_value,
            'quantity_before': self.quantity_before,
            'quantity_after': self.quantity_after,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'reference_number': self.reference_number,
            'from_location': self.from_location,
            'to_location': self.to_location,
            'ai_validated': self.ai_validated,
            'fraud_risk_score': self.fraud_risk_score,
            'anomaly_flags': json.loads(self.anomaly_flags) if self.anomaly_flags else [],
            'notes': self.notes,
            'batch_number': self.batch_number,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StockAlert(db.Model):
    __tablename__ = 'stock_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Alert details
    alert_type = db.Column(db.String(30), nullable=False)  # low_stock, overstock, expiry, quality
    alert_level = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    
    # Item reference
    item_type = db.Column(db.String(20))  # paddy, product
    item_id = db.Column(db.Integer)
    item_name = db.Column(db.String(100))
    
    # Alert thresholds
    threshold_value = db.Column(db.Float)
    current_value = db.Column(db.Float)
    
    # AI enhancement
    ai_generated = db.Column(db.Boolean, default=False)
    ai_priority_score = db.Column(db.Float)
    predicted_impact = db.Column(db.Text)  # JSON
    
    # Status and resolution
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved, dismissed
    resolution_notes = db.Column(db.Text)
    
    # Timestamps
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'alert_level': self.alert_level,
            'title': self.title,
            'message': self.message,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'threshold_value': self.threshold_value,
            'current_value': self.current_value,
            'ai_generated': self.ai_generated,
            'ai_priority_score': self.ai_priority_score,
            'predicted_impact': json.loads(self.predicted_impact) if self.predicted_impact else {},
            'status': self.status,
            'resolution_notes': self.resolution_notes,
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }

