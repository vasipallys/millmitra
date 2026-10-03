"""
Sales and Customer Management Models
"""

from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    customer_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    customer_type = db.Column(db.String(50))  # retailer, wholesaler, distributor, export
    
    # Contact information
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    contact_person = db.Column(db.String(100))
    
    # Address information
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    country = db.Column(db.String(50), default='India')
    
    # Business information
    business_name = db.Column(db.String(150))
    gst_number = db.Column(db.String(20))
    pan_number = db.Column(db.String(15))
    trade_license = db.Column(db.String(50))
    
    # Banking information
    bank_account = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(15))
    bank_name = db.Column(db.String(100))
    
    # Business metrics
    credit_limit = db.Column(db.Float, default=0.0)
    outstanding_amount = db.Column(db.Float, default=0.0)
    total_orders = db.Column(db.Integer, default=0)
    total_order_value = db.Column(db.Float, default=0.0)
    average_order_value = db.Column(db.Float, default=0.0)
    
    # Customer behavior
    payment_terms = db.Column(db.String(50), default='immediate')  # immediate, 15_days, 30_days, 45_days
    preferred_products = db.Column(db.Text)  # JSON string
    seasonal_pattern = db.Column(db.Text)  # JSON string
    price_sensitivity = db.Column(db.Float)  # AI-calculated
    loyalty_score = db.Column(db.Float)  # AI-calculated
    
    # Risk assessment
    credit_rating = db.Column(db.String(10))  # AAA, AA, A, BBB, BB, B, CCC, CC, C, D
    risk_category = db.Column(db.String(20))  # low, medium, high
    payment_behavior_score = db.Column(db.Float)  # AI-calculated
    
    # Status and tracking
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime)
    last_order_date = db.Column(db.DateTime)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI insights
    churn_probability = db.Column(db.Float)  # AI-predicted churn probability
    lifetime_value = db.Column(db.Float)  # AI-calculated customer lifetime value
    next_order_prediction = db.Column(db.DateTime)  # AI-predicted next order date
    recommended_products = db.Column(db.Text)  # JSON string with AI recommendations
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User")

    def get_preferred_products(self):
        if self.preferred_products:
            try:
                return json.loads(self.preferred_products)
            except:
                return []
        return []

    def set_preferred_products(self, products):
        self.preferred_products = json.dumps(products)

    def get_seasonal_pattern(self):
        if self.seasonal_pattern:
            try:
                return json.loads(self.seasonal_pattern)
            except:
                return {}
        return {}

    def set_seasonal_pattern(self, pattern):
        self.seasonal_pattern = json.dumps(pattern)

    def get_recommended_products(self):
        if self.recommended_products:
            try:
                return json.loads(self.recommended_products)
            except:
                return []
        return []

    def set_recommended_products(self, products):
        self.recommended_products = json.dumps(products)

    def calculate_average_order_value(self):
        """Calculate average order value"""
        if self.total_orders and self.total_orders > 0:
            return self.total_order_value / self.total_orders
        return 0.0

    def update_business_metrics(self, new_order_value):
        """Update business metrics after a new order"""
        self.total_orders = (self.total_orders or 0) + 1
        self.total_order_value = (self.total_order_value or 0) + new_order_value
        self.average_order_value = self.calculate_average_order_value()
        self.last_order_date = datetime.utcnow()

    def get_credit_status(self):
        """Get current credit status"""
        available_credit = self.credit_limit - (self.outstanding_amount or 0)
        utilization = 0
        if self.credit_limit > 0:
            utilization = ((self.outstanding_amount or 0) / self.credit_limit) * 100
        
        return {
            'credit_limit': self.credit_limit,
            'outstanding_amount': self.outstanding_amount or 0,
            'available_credit': available_credit,
            'utilization_percentage': utilization,
            'status': 'good' if utilization < 80 else 'warning' if utilization < 95 else 'critical'
        }

    @property
    def status(self):
        """Alias for is_active field for backward compatibility"""
        return 'active' if self.is_active else 'inactive'
    
    @property
    def segment(self):
        """Alias for customer_type field for backward compatibility"""
        return self.customer_type

    def get_customer_insights(self):
        """Get AI-powered customer insights"""
        insights = []
        
        # Churn risk analysis
        if self.churn_probability and self.churn_probability > 0.7:
            insights.append({
                'type': 'churn_risk',
                'message': f'High churn risk ({self.churn_probability*100:.1f}%)',
                'priority': 'high',
                'recommendation': 'Consider retention strategies'
            })
        
        # Credit utilization
        credit_status = self.get_credit_status()
        if credit_status['utilization_percentage'] > 90:
            insights.append({
                'type': 'credit_risk',
                'message': f'High credit utilization ({credit_status["utilization_percentage"]:.1f}%)',
                'priority': 'high',
                'recommendation': 'Review credit terms'
            })
        
        # Order frequency
        if self.last_order_date:
            days_since_last_order = (datetime.utcnow() - self.last_order_date).days
            if days_since_last_order > 60:
                insights.append({
                    'type': 'inactive_customer',
                    'message': f'No orders for {days_since_last_order} days',
                    'priority': 'medium',
                    'recommendation': 'Reach out to customer'
                })
        
        return insights

    def to_dict(self):
        return {
            'id': self.id,
            'customer_code': self.customer_code,
            'name': self.name,
            'customer_type': self.customer_type,
            'phone': self.phone,
            'email': self.email,
            'contact_person': self.contact_person,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'country': self.country,
            'business_name': self.business_name,
            'gst_number': self.gst_number,
            'pan_number': self.pan_number,
            'trade_license': self.trade_license,
            'bank_account': self.bank_account,
            'ifsc_code': self.ifsc_code,
            'bank_name': self.bank_name,
            'credit_limit': self.credit_limit,
            'outstanding_amount': self.outstanding_amount,
            'total_orders': self.total_orders,
            'total_order_value': self.total_order_value,
            'average_order_value': self.average_order_value,
            'payment_terms': self.payment_terms,
            'preferred_products': self.get_preferred_products(),
            'seasonal_pattern': self.get_seasonal_pattern(),
            'price_sensitivity': self.price_sensitivity,
            'loyalty_score': self.loyalty_score,
            'credit_rating': self.credit_rating,
            'risk_category': self.risk_category,
            'payment_behavior_score': self.payment_behavior_score,
            'is_active': self.is_active,
            'status': self.status,
            'segment': self.segment,
            'is_verified': self.is_verified,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'last_order_date': self.last_order_date.isoformat() if self.last_order_date else None,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'churn_probability': self.churn_probability,
            'lifetime_value': self.lifetime_value,
            'next_order_prediction': self.next_order_prediction.isoformat() if self.next_order_prediction else None,
            'recommended_products': self.get_recommended_products(),
            'credit_status': self.get_credit_status(),
            'customer_insights': self.get_customer_insights(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Order details
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    delivery_date = db.Column(db.DateTime)
    expected_delivery_date = db.Column(db.DateTime)
    
    # Products and quantities
    order_items = db.Column(db.Text)  # JSON string with product details
    total_quantity = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Pricing and discounts
    base_amount = db.Column(db.Float)
    discount_percentage = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    
    # Payment terms
    payment_terms = db.Column(db.String(50))
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, paid, overdue
    advance_amount = db.Column(db.Float, default=0.0)
    balance_amount = db.Column(db.Float)
    
    # Delivery information
    delivery_address = db.Column(db.Text)
    delivery_method = db.Column(db.String(50))  # pickup, delivery, courier
    transport_cost = db.Column(db.Float, default=0.0)
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, processing, shipped, delivered, cancelled
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # AI insights
    profit_margin = db.Column(db.Float)
    delivery_risk_score = db.Column(db.Float)  # AI-calculated delivery risk
    customer_satisfaction_prediction = db.Column(db.Float)
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    confirmed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer")
    created_by_user = relationship("User", foreign_keys=[created_by])
    confirmed_by_user = relationship("User", foreign_keys=[confirmed_by])

    def get_order_items(self):
        if self.order_items:
            try:
                return json.loads(self.order_items)
            except:
                return []
        return []

    def set_order_items(self, items):
        self.order_items = json.dumps(items)

    def calculate_totals(self):
        """Calculate order totals"""
        items = self.get_order_items()
        
        self.total_quantity = sum(item.get('quantity', 0) for item in items)
        self.base_amount = sum(item.get('quantity', 0) * item.get('unit_price', 0) for item in items)
        
        self.discount_amount = (self.base_amount * (self.discount_percentage or 0)) / 100
        subtotal = self.base_amount - self.discount_amount
        
        # Calculate tax (assuming 5% GST for rice)
        self.tax_amount = subtotal * 0.05
        
        self.total_amount = subtotal + self.tax_amount + (self.transport_cost or 0)
        self.balance_amount = self.total_amount - (self.advance_amount or 0)

    def get_delivery_timeline(self):
        """Get delivery timeline analysis"""
        if not self.expected_delivery_date:
            return None
        
        days_to_delivery = (self.expected_delivery_date - datetime.utcnow()).days
        
        timeline = {
            'days_remaining': days_to_delivery,
            'status': 'on_time'
        }
        
        if days_to_delivery < 0:
            timeline['status'] = 'overdue'
        elif days_to_delivery <= 1:
            timeline['status'] = 'urgent'
        elif days_to_delivery <= 3:
            timeline['status'] = 'due_soon'
        
        return timeline

    def get_order_insights(self):
        """Get AI-powered order insights"""
        insights = []
        
        # Delivery timeline
        timeline = self.get_delivery_timeline()
        if timeline and timeline['status'] == 'overdue':
            insights.append({
                'type': 'delivery_overdue',
                'message': f'Order is {abs(timeline["days_remaining"])} days overdue',
                'priority': 'critical'
            })
        elif timeline and timeline['status'] == 'urgent':
            insights.append({
                'type': 'delivery_urgent',
                'message': 'Order delivery is due within 24 hours',
                'priority': 'high'
            })
        
        # Payment status
        if self.payment_status == 'overdue':
            insights.append({
                'type': 'payment_overdue',
                'message': f'Payment overdue: ₹{self.balance_amount:,.0f}',
                'priority': 'high'
            })
        
        # Profit margin analysis
        if self.profit_margin and self.profit_margin < 10:
            insights.append({
                'type': 'low_margin',
                'message': f'Low profit margin ({self.profit_margin:.1f}%)',
                'priority': 'medium'
            })
        
        return insights

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'expected_delivery_date': self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            'order_items': self.get_order_items(),
            'total_quantity': self.total_quantity,
            'total_amount': self.total_amount,
            'base_amount': self.base_amount,
            'discount_percentage': self.discount_percentage,
            'discount_amount': self.discount_amount,
            'tax_amount': self.tax_amount,
            'payment_terms': self.payment_terms,
            'payment_status': self.payment_status,
            'advance_amount': self.advance_amount,
            'balance_amount': self.balance_amount,
            'delivery_address': self.delivery_address,
            'delivery_method': self.delivery_method,
            'transport_cost': self.transport_cost,
            'status': self.status,
            'priority': self.priority,
            'profit_margin': self.profit_margin,
            'delivery_risk_score': self.delivery_risk_score,
            'customer_satisfaction_prediction': self.customer_satisfaction_prediction,
            'delivery_timeline': self.get_delivery_timeline(),
            'order_insights': self.get_order_insights(),
            'customer_name': self.customer.name if self.customer else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
