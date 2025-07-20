from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import db

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100))
    customer_type = db.Column(db.String(20), default='retail')  # retail, wholesale, distributor, export
    
    # Contact Information
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    country = db.Column(db.String(50), default='India')
    
    # Business Information
    gst_number = db.Column(db.String(15))
    pan_number = db.Column(db.String(10))
    credit_limit = db.Column(db.Float, default=0)
    payment_terms = db.Column(db.String(50), default='cash')  # cash, credit_30, credit_60, etc.
    
    # Customer Metrics
    total_orders = db.Column(db.Integer, default=0)
    total_value = db.Column(db.Float, default=0)
    average_order_value = db.Column(db.Float, default=0)
    last_order_date = db.Column(db.DateTime)
    
    # AI Insights
    customer_score = db.Column(db.Float)  # AI calculated customer value score
    risk_rating = db.Column(db.String(10))  # low, medium, high
    preferred_products = db.Column(JSON)
    buying_patterns = db.Column(JSON)
    
    # Status and tracking
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('SalesOrder', backref='customer', lazy='dynamic')
    quotations = db.relationship('Quotation', backref='customer', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_code': self.customer_code,
            'name': self.name,
            'company_name': self.company_name,
            'customer_type': self.customer_type,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'gst_number': self.gst_number,
            'credit_limit': self.credit_limit,
            'payment_terms': self.payment_terms,
            'total_orders': self.total_orders,
            'total_value': self.total_value,
            'average_order_value': self.average_order_value,
            'last_order_date': self.last_order_date.isoformat() if self.last_order_date else None,
            'customer_score': self.customer_score,
            'risk_rating': self.risk_rating,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Customer and reference
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'))
    
    # Order details
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime)
    order_type = db.Column(db.String(20), default='standard')  # standard, urgent, export
    
    # Financial details
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    
    # Payment and delivery
    payment_terms = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid
    delivery_address = db.Column(db.Text)
    delivery_status = db.Column(db.String(20), default='pending')  # pending, dispatched, delivered
    
    # AI insights
    fulfillment_prediction = db.Column(JSON)
    risk_assessment = db.Column(JSON)
    
    # Status and tracking
    status = db.Column(db.String(20), default='draft')  # draft, confirmed, processing, completed, cancelled
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('SalesOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'order_date': self.order_date.isoformat(),
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'order_type': self.order_type,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount,
            'payment_terms': self.payment_terms,
            'payment_status': self.payment_status,
            'delivery_status': self.delivery_status,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat()
        }

class SalesOrderItem(db.Model):
    __tablename__ = 'sales_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    
    # Product details
    product_name = db.Column(db.String(100), nullable=False)
    product_variety = db.Column(db.String(50))
    product_grade = db.Column(db.String(10))
    
    # Quantity and pricing
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='quintal')
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Fulfillment
    allocated_quantity = db.Column(db.Float, default=0)
    delivered_quantity = db.Column(db.Float, default=0)
    
    # Source tracking
    source_type = db.Column(db.String(20))  # production, inventory
    source_reference_id = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_variety': self.product_variety,
            'product_grade': self.product_grade,
            'quantity': self.quantity,
            'unit': self.unit,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'allocated_quantity': self.allocated_quantity,
            'delivered_quantity': self.delivered_quantity
        }

class Quotation(db.Model):
    __tablename__ = 'quotations'
    
    id = db.Column(db.Integer, primary_key=True)
    quotation_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Customer and reference
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Quotation details
    quotation_date = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    
    # Financial details
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, default=0)
    
    # Terms and conditions
    payment_terms = db.Column(db.String(50))
    delivery_terms = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # AI insights
    conversion_probability = db.Column(db.Float)  # AI predicted conversion rate
    competitive_analysis = db.Column(JSON)
    
    # Status and tracking
    status = db.Column(db.String(20), default='draft')  # draft, sent, accepted, rejected, expired
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('QuotationItem', backref='quotation', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'quotation_number': self.quotation_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'quotation_date': self.quotation_date.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'payment_terms': self.payment_terms,
            'conversion_probability': self.conversion_probability,
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat()
        }

class QuotationItem(db.Model):
    __tablename__ = 'quotation_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    
    # Product details
    product_name = db.Column(db.String(100), nullable=False)
    product_variety = db.Column(db.String(50))
    product_grade = db.Column(db.String(10))
    
    # Quantity and pricing
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='quintal')
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    
    # Additional details
    specifications = db.Column(db.Text)
    delivery_timeline = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'product_variety': self.product_variety,
            'product_grade': self.product_grade,
            'quantity': self.quantity,
            'unit': self.unit,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'specifications': self.specifications,
            'delivery_timeline': self.delivery_timeline
        }

class SalesLead(db.Model):
    __tablename__ = 'sales_leads'
    
    id = db.Column(db.Integer, primary_key=True)
    lead_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Lead information
    name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # Lead details
    source = db.Column(db.String(50))  # website, referral, cold_call, exhibition
    product_interest = db.Column(db.String(100))
    estimated_value = db.Column(db.Float)
    expected_closure_date = db.Column(db.DateTime)
    
    # AI scoring
    lead_score = db.Column(db.Float)  # AI calculated lead score
    qualification_status = db.Column(db.String(20))  # unqualified, qualified, hot, cold
    next_action = db.Column(db.String(100))  # AI recommended next action
    
    # Status and tracking
    status = db.Column(db.String(20), default='new')  # new, contacted, qualified, proposal, negotiation, won, lost
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'lead_number': self.lead_number,
            'name': self.name,
            'company_name': self.company_name,
            'email': self.email,
            'phone': self.phone,
            'source': self.source,
            'product_interest': self.product_interest,
            'estimated_value': self.estimated_value,
            'expected_closure_date': self.expected_closure_date.isoformat() if self.expected_closure_date else None,
            'lead_score': self.lead_score,
            'qualification_status': self.qualification_status,
            'next_action': self.next_action,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
