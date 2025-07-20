from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_code = db.Column(db.String(20), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    country = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    
    # Business details
    tax_id = db.Column(db.String(50))
    payment_terms = db.Column(db.String(50))  # net_30, net_60, etc.
    credit_limit = db.Column(db.Float, default=0.0)
    supplier_type = db.Column(db.String(50))  # raw_material, equipment, service
    
    # Performance metrics
    quality_rating = db.Column(db.Float, default=0.0)  # 0-5 scale
    delivery_rating = db.Column(db.Float, default=0.0)
    price_competitiveness = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, inactive, blacklisted
    is_preferred = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    supplier_contracts = relationship("SupplierContract", back_populates="supplier")

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    po_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    expected_delivery_date = db.Column(db.DateTime)
    actual_delivery_date = db.Column(db.DateTime)
    
    # Financial details
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    shipping_cost = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Status tracking
    status = db.Column(db.String(20), default='draft')  # draft, sent, confirmed, delivered, cancelled
    priority = db.Column(db.String(10), default='normal')  # low, normal, high, urgent
    
    # Delivery and quality
    delivery_status = db.Column(db.String(20), default='pending')  # pending, partial, complete, delayed
    quality_check_status = db.Column(db.String(20), default='pending')  # pending, passed, failed
    
    # Notes and references
    notes = db.Column(db.Text)
    reference_number = db.Column(db.String(100))
    
    # AI insights
    ai_recommendations = db.Column(JSON)
    risk_assessment = db.Column(JSON)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    po_items = relationship("PurchaseOrderItem", back_populates="purchase_order")
    created_by_user = relationship("User")

class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    po_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    item_code = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # Quantities
    ordered_quantity = db.Column(db.Float, nullable=False)
    received_quantity = db.Column(db.Float, default=0.0)
    unit_of_measure = db.Column(db.String(20))
    
    # Pricing
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Quality specifications
    quality_specs = db.Column(JSON)
    received_quality = db.Column(JSON)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, received, rejected
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="po_items")

class SupplierContract(db.Model):
    __tablename__ = 'supplier_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # Contract details
    contract_type = db.Column(db.String(50))  # supply_agreement, service_contract, etc.
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    auto_renewal = db.Column(db.Boolean, default=False)
    
    # Terms and conditions
    payment_terms = db.Column(db.String(100))
    delivery_terms = db.Column(db.String(100))
    quality_requirements = db.Column(JSON)
    pricing_structure = db.Column(JSON)
    
    # Performance metrics
    minimum_quality_score = db.Column(db.Float, default=4.0)
    maximum_delivery_days = db.Column(db.Integer, default=7)
    penalty_clauses = db.Column(JSON)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, expired, terminated
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="supplier_contracts")

class ProcurementRequest(db.Model):
    __tablename__ = 'procurement_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    department = db.Column(db.String(50))
    
    # Request details
    item_category = db.Column(db.String(50))
    urgency = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    required_date = db.Column(db.DateTime)
    justification = db.Column(db.Text)
    
    # Budget and approval
    estimated_cost = db.Column(db.Float)
    approved_budget = db.Column(db.Float)
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.DateTime)
    
    # Processing
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='submitted')  # submitted, in_progress, completed, cancelled
    
    # AI recommendations
    supplier_recommendations = db.Column(JSON)
    cost_optimization = db.Column(JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    requested_by_user = relationship("User", foreign_keys=[requested_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    assigned_to_user = relationship("User", foreign_keys=[assigned_to])
    request_items = relationship("ProcurementRequestItem", back_populates="request")

class ProcurementRequestItem(db.Model):
    __tablename__ = 'procurement_request_items'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('procurement_requests.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, nullable=False)
    unit_of_measure = db.Column(db.String(20))
    estimated_unit_price = db.Column(db.Float)
    specifications = db.Column(JSON)
    
    # Relationships
    request = relationship("ProcurementRequest", back_populates="request_items")