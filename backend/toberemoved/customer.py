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
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    alternate_phone = db.Column(db.String(20))
    
    # Address
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    country = db.Column(db.String(50), default='India')
    
    # Business details
    business_type = db.Column(db.String(50))  # wholesale, retail, distributor
    business_age_years = db.Column(db.Integer)
    annual_revenue = db.Column(db.Float)
    employee_count = db.Column(db.Integer)
    
    # Customer classification
    customer_segment_id = db.Column(db.Integer, db.ForeignKey('customer_segments.id'))
    customer_tier = db.Column(db.String(20), default='standard')  # premium, gold, standard
    
    # AI-powered insights
    ai_predicted_segment = db.Column(db.String(50))
    ai_customer_score = db.Column(db.Float)
    ai_growth_potential = db.Column(db.String(20))  # high, medium, low
    ai_churn_risk = db.Column(db.String(20))  # high, medium, low
    ai_lifetime_value = db.Column(db.Float)
    
    # Credit and payment
    credit_limit = db.Column(db.Float, default=0)
    credit_grade = db.Column(db.String(10))  # A, B, C
    payment_terms = db.Column(db.String(20), default='advance')  # advance, 15_days, 30_days
    outstanding_amount = db.Column(db.Float, default=0)
    
    # Preferences
    preferred_products = db.Column(db.Text)  # JSON
    preferred_delivery_time = db.Column(db.String(50))
    communication_preferences = db.Column(db.Text)  # JSON
    
    # Status and tracking
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    acquisition_source = db.Column(db.String(50))  # referral, marketing, direct
    acquisition_date = db.Column(db.Date, default=datetime.utcnow)
    last_order_date = db.Column(db.Date)
    total_orders = db.Column(db.Integer, default=0)
    total_order_value = db.Column(db.Float, default=0)
    
    # AI interaction tracking
    last_interaction_date = db.Column(db.Date)
    interaction_frequency = db.Column(db.String(20))  # high, medium, low
    satisfaction_score = db.Column(db.Float)
    nps_score = db.Column(db.Integer)  # Net Promoter Score
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    account_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_code': self.customer_code,
            'business_name': self.business_name,
            'contact_person': self.contact_person,
            'designation': self.designation,
            'phone': self.phone,
            'email': self.email,
            'alternate_phone': self.alternate_phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'country': self.country,
            'business_type': self.business_type,
            'business_age_years': self.business_age_years,
            'annual_revenue': self.annual_revenue,
            'employee_count': self.employee_count,
            'customer_segment_id': self.customer_segment_id,
            'customer_tier': self.customer_tier,
            'ai_predicted_segment': self.ai_predicted_segment,
            'ai_customer_score': self.ai_customer_score,
            'ai_growth_potential': self.ai_growth_potential,
            'ai_churn_risk': self.ai_churn_risk,
            'ai_lifetime_value': self.ai_lifetime_value,
            'credit_limit': self.credit_limit,
            'credit_grade': self.credit_grade,
            'payment_terms': self.payment_terms,
            'outstanding_amount': self.outstanding_amount,
            'preferred_products': json.loads(self.preferred_products) if self.preferred_products else [],
            'preferred_delivery_time': self.preferred_delivery_time,
            'communication_preferences': json.loads(self.communication_preferences) if self.communication_preferences else [],
            'status': self.status,
            'acquisition_source': self.acquisition_source,
            'acquisition_date': self.acquisition_date.isoformat() if self.acquisition_date else None,
            'last_order_date': self.last_order_date.isoformat() if self.last_order_date else None,
            'total_orders': self.total_orders,
            'total_order_value': self.total_order_value,
            'last_interaction_date': self.last_interaction_date.isoformat() if self.last_interaction_date else None,
            'interaction_frequency': self.interaction_frequency,
            'satisfaction_score': self.satisfaction_score,
            'nps_score': self.nps_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CustomerInteraction(db.Model):
    __tablename__ = 'customer_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Customer reference
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Interaction details
    interaction_type = db.Column(db.String(30), nullable=False)  # call, email, meeting, complaint
    interaction_channel = db.Column(db.String(20))  # phone, email, in_person, chat
    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # AI analysis
    ai_sentiment_score = db.Column(db.Float)  # -1 to 1
    ai_sentiment_label = db.Column(db.String(20))  # positive, neutral, negative
    ai_interaction_category = db.Column(db.String(50))
    ai_priority_score = db.Column(db.Float)
    ai_follow_up_required = db.Column(db.Boolean, default=False)
    
    # Status and resolution
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    resolution = db.Column(db.Text)
    satisfaction_rating = db.Column(db.Integer)  # 1-5 scale
    
    # Follow-up
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    follow_up_notes = db.Column(db.Text)
    
    # Timestamps
    interaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'interaction_type': self.interaction_type,
            'interaction_channel': self.interaction_channel,
            'subject': self.subject,
            'description': self.description,
            'ai_sentiment_score': self.ai_sentiment_score,
            'ai_sentiment_label': self.ai_sentiment_label,
            'ai_interaction_category': self.ai_interaction_category,
            'ai_priority_score': self.ai_priority_score,
            'ai_follow_up_required': self.ai_follow_up_required,
            'status': self.status,
            'resolution': self.resolution,
            'satisfaction_rating': self.satisfaction_rating,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'follow_up_notes': self.follow_up_notes,
            'interaction_date': self.interaction_date.isoformat() if self.interaction_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CustomerSegment(db.Model):
    __tablename__ = 'customer_segments'
    
    id = db.Column(db.Integer, primary_key=True)
    segment_name = db.Column(db.String(100), nullable=False)
    segment_code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    
    # Segment criteria
    criteria = db.Column(db.Text)  # JSON
    min_annual_revenue = db.Column(db.Float)
    max_annual_revenue = db.Column(db.Float)
    business_types = db.Column(db.Text)  # JSON
    
    # AI insights
    ai_segment_score = db.Column(db.Float)
    ai_growth_rate = db.Column(db.Float)
    ai_profitability_score = db.Column(db.Float)
    
    # Segment metrics
    customer_count = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0)
    avg_order_value = db.Column(db.Float, default=0)
    churn_rate = db.Column(db.Float, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'segment_name': self.segment_name,
            'segment_code': self.segment_code,
            'description': self.description,
            'criteria': json.loads(self.criteria) if self.criteria else {},
            'min_annual_revenue': self.min_annual_revenue,
            'max_annual_revenue': self.max_annual_revenue,
            'business_types': json.loads(self.business_types) if self.business_types else [],
            'ai_segment_score': self.ai_segment_score,
            'ai_growth_rate': self.ai_growth_rate,
            'ai_profitability_score': self.ai_profitability_score,
            'customer_count': self.customer_count,
            'total_revenue': self.total_revenue,
            'avg_order_value': self.avg_order_value,
            'churn_rate': self.churn_rate,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CustomerContract(db.Model):
    __tablename__ = 'customer_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    
    # Customer reference
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Contract details
    contract_type = db.Column(db.String(30))  # annual, quarterly, spot
    contract_value = db.Column(db.Float)
    contract_quantity = db.Column(db.Float)  # in tons
    
    # Terms
    price_per_unit = db.Column(db.Float)
    payment_terms = db.Column(db.String(50))
    delivery_terms = db.Column(db.String(100))
    quality_specifications = db.Column(db.Text)  # JSON
    
    # AI analysis
    ai_risk_assessment = db.Column(db.String(20))  # low, medium, high
    ai_profitability_score = db.Column(db.Float)
    ai_renewal_probability = db.Column(db.Float)
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    renewal_date = db.Column(db.Date)
    
    # Status
    status = db.Column(db.String(20), default='active')  # draft, active, completed, cancelled
    
    # Performance tracking
    delivered_quantity = db.Column(db.Float, default=0)
    delivered_value = db.Column(db.Float, default=0)
    completion_percentage = db.Column(db.Float, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_number': self.contract_number,
            'customer_id': self.customer_id,
            'contract_type': self.contract_type,
            'contract_value': self.contract_value,
            'contract_quantity': self.contract_quantity,
            'price_per_unit': self.price_per_unit,
            'payment_terms': self.payment_terms,
            'delivery_terms': self.delivery_terms,
            'quality_specifications': json.loads(self.quality_specifications) if self.quality_specifications else {},
            'ai_risk_assessment': self.ai_risk_assessment,
            'ai_profitability_score': self.ai_profitability_score,
            'ai_renewal_probability': self.ai_renewal_probability,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
            'status': self.status,
            'delivered_quantity': self.delivered_quantity,
            'delivered_value': self.delivered_value,
            'completion_percentage': self.completion_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CustomerFeedback(db.Model):
    __tablename__ = 'customer_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    feedback_text = db.Column(db.Text)
    rating = db.Column(db.Integer)  # 1-10 scale
    category = db.Column(db.String(50))  # product, service, delivery, etc.
    
    # AI-enhanced fields
    sentiment_score = db.Column(db.Float)
    sentiment_label = db.Column(db.String(20))
    themes = db.Column(db.Text)  # JSON string of extracted themes
    ai_analysis = db.Column(db.Text)  # Full AI analysis JSON
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'feedback_text': self.feedback_text,
            'rating': self.rating,
            'category': self.category,
            'sentiment_score': self.sentiment_score,
            'sentiment_label': self.sentiment_label,
            'themes': json.loads(self.themes) if self.themes else [],
            'ai_analysis': json.loads(self.ai_analysis) if self.ai_analysis else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


