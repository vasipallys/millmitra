from extensions import db
from datetime import datetime
import json

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Basic information
    business_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(50))
    
    # Contact details
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    website = db.Column(db.String(200))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    country = db.Column(db.String(50), default='India')
    
    # Business details
    business_type = db.Column(db.String(50))  # retailer, distributor, restaurant, etc.
    industry = db.Column(db.String(50))
    annual_revenue = db.Column(db.Float)
    years_in_business = db.Column(db.Integer)
    employee_count = db.Column(db.Integer)
    
    # Financial information
    credit_limit = db.Column(db.Float, default=0)
    payment_terms = db.Column(db.Integer, default=30)  # days
    outstanding_balance = db.Column(db.Float, default=0)
    
    # Status and classification
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    customer_segment = db.Column(db.String(30))
    priority_level = db.Column(db.String(20), default='medium')  # high, medium, low
    
    # AI-enhanced fields
    ai_segment = db.Column(db.String(30))
    ai_segment_confidence = db.Column(db.Float)
    loyalty_score = db.Column(db.Float)
    churn_risk_score = db.Column(db.Float)
    lifetime_value = db.Column(db.Float)
    engagement_score = db.Column(db.Float)
    satisfaction_score = db.Column(db.Float)
    
    # Preferences
    preferred_communication = db.Column(db.String(20))  # email, phone, whatsapp
    preferred_delivery_time = db.Column(db.String(50))
    special_requirements = db.Column(db.Text)
    
    # Timestamps
    first_order_date = db.Column(db.Date)
    last_order_date = db.Column(db.Date)
    last_interaction_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    account_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationship to interactions
    interactions = db.relationship('CustomerInteraction', backref='customer', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_code': self.customer_code,
            'business_name': self.business_name,
            'contact_person': self.contact_person,
            'designation': self.designation,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'country': self.country,
            'business_type': self.business_type,
            'industry': self.industry,
            'annual_revenue': self.annual_revenue,
            'years_in_business': self.years_in_business,
            'employee_count': self.employee_count,
            'credit_limit': self.credit_limit,
            'payment_terms': self.payment_terms,
            'outstanding_balance': self.outstanding_balance,
            'status': self.status,
            'customer_segment': self.customer_segment,
            'priority_level': self.priority_level,
            'ai_segment': self.ai_segment,
            'ai_segment_confidence': self.ai_segment_confidence,
            'loyalty_score': self.loyalty_score,
            'churn_risk_score': self.churn_risk_score,
            'lifetime_value': self.lifetime_value,
            'engagement_score': self.engagement_score,
            'satisfaction_score': self.satisfaction_score,
            'preferred_communication': self.preferred_communication,
            'preferred_delivery_time': self.preferred_delivery_time,
            'special_requirements': self.special_requirements,
            'first_order_date': self.first_order_date.isoformat() if self.first_order_date else None,
            'last_order_date': self.last_order_date.isoformat() if self.last_order_date else None,
            'last_interaction_date': self.last_interaction_date.isoformat() if self.last_interaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CustomerInteraction(db.Model):
    __tablename__ = 'customer_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Interaction details
    interaction_type = db.Column(db.String(30))  # call, email, meeting, complaint, inquiry
    channel = db.Column(db.String(20))  # phone, email, whatsapp, in_person, website
    subject = db.Column(db.String(200))
    content = db.Column(db.Text)
    
    # Status and priority
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='medium')  # high, medium, low
    
    # AI-enhanced fields
    ai_category = db.Column(db.String(50))
    ai_subcategory = db.Column(db.String(50))
    ai_confidence = db.Column(db.Float)
    sentiment = db.Column(db.String(20))  # positive, negative, neutral
    sentiment_confidence = db.Column(db.Float)
    urgency_score = db.Column(db.Float)
    
    # Follow-up
    requires_follow_up = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    follow_up_notes = db.Column(db.Text)
    
    # Resolution
    resolution = db.Column(db.Text)
    resolution_time_hours = db.Column(db.Float)
    customer_satisfaction = db.Column(db.Integer)  # 1-5 rating
    
    # Timestamps
    interaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'interaction_type': self.interaction_type,
            'channel': self.channel,
            'subject': self.subject,
            'content': self.content,
            'status': self.status,
            'priority': self.priority,
            'ai_category': self.ai_category,
            'ai_subcategory': self.ai_subcategory,
            'ai_confidence': self.ai_confidence,
            'sentiment': self.sentiment,
            'sentiment_confidence': self.sentiment_confidence,
            'urgency_score': self.urgency_score,
            'requires_follow_up': self.requires_follow_up,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'follow_up_notes': self.follow_up_notes,
            'resolution': self.resolution,
            'resolution_time_hours': self.resolution_time_hours,
            'customer_satisfaction': self.customer_satisfaction,
            'interaction_date': self.interaction_date.isoformat() if self.interaction_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CustomerSegment(db.Model):
    __tablename__ = 'customer_segments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Segment criteria
    criteria = db.Column(db.Text)  # JSON
    
    # Segment characteristics
    min_annual_revenue = db.Column(db.Float)
    max_annual_revenue = db.Column(db.Float)
    min_order_frequency = db.Column(db.Integer)
    business_types = db.Column(db.Text)  # JSON array
    
    # AI-enhanced fields
    ai_defined = db.Column(db.Boolean, default=False)
    segment_score_threshold = db.Column(db.Float)
    
    # Marketing preferences
    preferred_communication_channels = db.Column(db.Text)  # JSON
    marketing_messages = db.Column(db.Text)  # JSON
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'criteria': json.loads(self.criteria) if self.criteria else {},
            'min_annual_revenue': self.min_annual_revenue,
            'max_annual_revenue': self.max_annual_revenue,
            'min_order_frequency': self.min_order_frequency,
            'business_types': json.loads(self.business_types) if self.business_types else [],
            'ai_defined': self.ai_defined,
            'segment_score_threshold': self.segment_score_threshold,
            'preferred_communication_channels': json.loads(self.preferred_communication_channels) if self.preferred_communication_channels else [],
            'marketing_messages': json.loads(self.marketing_messages) if self.marketing_messages else [],
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }