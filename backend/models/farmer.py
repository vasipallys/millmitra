"""
Farmer Management Models
"""

from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class Farmer(db.Model):
    __tablename__ = 'farmers'
    
    id = db.Column(db.Integer, primary_key=True)
    farmer_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    
    # Address information
    address = db.Column(db.Text)
    village = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    
    # Banking information
    bank_account = db.Column(db.String(50))
    ifsc_code = db.Column(db.String(15))
    bank_name = db.Column(db.String(100))
    branch_name = db.Column(db.String(100))
    
    # Identity information
    pan_number = db.Column(db.String(15))
    aadhar_number = db.Column(db.String(15))
    
    # Farming information
    land_area = db.Column(db.Float)  # in acres
    farming_experience = db.Column(db.Integer)  # in years
    preferred_varieties = db.Column(db.Text)  # JSON string
    farming_type = db.Column(db.String(50))  # organic, conventional, mixed
    irrigation_type = db.Column(db.String(50))  # bore_well, canal, rain_fed
    
    # Business metrics
    quality_rating = db.Column(db.Float, default=0.0)
    reliability_score = db.Column(db.Float, default=0.0)
    total_transactions = db.Column(db.Integer, default=0)
    total_quantity_supplied = db.Column(db.Float, default=0.0)  # in kg
    average_quality_grade = db.Column(db.String(10))
    
    # Payment and terms
    payment_terms = db.Column(db.String(50), default='immediate')
    credit_limit = db.Column(db.Float, default=0.0)
    outstanding_amount = db.Column(db.Float, default=0.0)
    
    # Status and tracking
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime)
    last_transaction_date = db.Column(db.DateTime)
    
    # AI insights
    risk_category = db.Column(db.String(20))  # low, medium, high
    seasonal_pattern = db.Column(db.Text)  # JSON string with seasonal data
    price_sensitivity = db.Column(db.Float)  # AI-calculated price sensitivity
    loyalty_score = db.Column(db.Float)  # AI-calculated loyalty score
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User")

    def get_preferred_varieties(self):
        if self.preferred_varieties:
            try:
                return json.loads(self.preferred_varieties)
            except:
                return []
        return []

    def set_preferred_varieties(self, varieties):
        self.preferred_varieties = json.dumps(varieties)

    def get_seasonal_pattern(self):
        if self.seasonal_pattern:
            try:
                return json.loads(self.seasonal_pattern)
            except:
                return {}
        return {}

    def set_seasonal_pattern(self, pattern):
        self.seasonal_pattern = json.dumps(pattern)

    def calculate_quality_rating(self):
        """Calculate quality rating based on recent transactions"""
        # This would be implemented with actual transaction data
        # For now, return current rating
        return self.quality_rating or 0.0

    def update_business_metrics(self, new_transaction_data):
        """Update business metrics after a new transaction"""
        self.total_transactions = (self.total_transactions or 0) + 1
        self.total_quantity_supplied = (self.total_quantity_supplied or 0) + new_transaction_data.get('quantity', 0)
        self.last_transaction_date = datetime.utcnow()
        
        # Update quality rating (simplified logic)
        current_grade = new_transaction_data.get('quality_grade', 'C')
        grade_scores = {'A': 5, 'B': 4, 'C': 3, 'D': 2, 'E': 1}
        new_score = grade_scores.get(current_grade, 3)
        
        if self.quality_rating:
            # Weighted average with more weight to recent transactions
            self.quality_rating = (self.quality_rating * 0.8) + (new_score * 0.2)
        else:
            self.quality_rating = new_score

    def get_risk_assessment(self):
        """Get AI-powered risk assessment"""
        factors = {
            'payment_history': 0.3,
            'quality_consistency': 0.25,
            'quantity_reliability': 0.2,
            'seasonal_availability': 0.15,
            'market_reputation': 0.1
        }
        
        # Simplified risk calculation
        risk_score = 0.0
        if self.reliability_score:
            risk_score += self.reliability_score * factors['payment_history']
        if self.quality_rating:
            risk_score += (self.quality_rating / 5.0) * factors['quality_consistency']
        
        if risk_score >= 0.8:
            return 'low'
        elif risk_score >= 0.6:
            return 'medium'
        else:
            return 'high'

    def to_dict(self):
        return {
            'id': self.id,
            'farmer_code': self.farmer_code,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'village': self.village,
            'district': self.district,
            'state': self.state,
            'pincode': self.pincode,
            'bank_account': self.bank_account,
            'ifsc_code': self.ifsc_code,
            'bank_name': self.bank_name,
            'branch_name': self.branch_name,
            'pan_number': self.pan_number,
            'aadhar_number': self.aadhar_number,
            'land_area': self.land_area,
            'farming_experience': self.farming_experience,
            'preferred_varieties': self.get_preferred_varieties(),
            'farming_type': self.farming_type,
            'irrigation_type': self.irrigation_type,
            'quality_rating': self.quality_rating,
            'reliability_score': self.reliability_score,
            'total_transactions': self.total_transactions,
            'total_quantity_supplied': self.total_quantity_supplied,
            'average_quality_grade': self.average_quality_grade,
            'payment_terms': self.payment_terms,
            'credit_limit': self.credit_limit,
            'outstanding_amount': self.outstanding_amount,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'last_transaction_date': self.last_transaction_date.isoformat() if self.last_transaction_date else None,
            'risk_category': self.risk_category or self.get_risk_assessment(),
            'seasonal_pattern': self.get_seasonal_pattern(),
            'price_sensitivity': self.price_sensitivity,
            'loyalty_score': self.loyalty_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PaddyProcurement(db.Model):
    __tablename__ = 'paddy_procurements'
    
    id = db.Column(db.Integer, primary_key=True)
    procurement_number = db.Column(db.String(50), unique=True, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    
    # Procurement details
    variety = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # in kg
    moisture_content = db.Column(db.Float)
    quality_grade = db.Column(db.String(10))
    price_per_kg = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Quality parameters
    broken_percentage = db.Column(db.Float)
    foreign_matter = db.Column(db.Float)
    chalky_grains = db.Column(db.Float)
    
    # Dates
    procurement_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, completed, rejected
    payment_status = db.Column(db.String(20), default='pending')  # pending, partial, completed
    
    # Notes
    notes = db.Column(db.Text)
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farmer = relationship("Farmer")
    created_by_user = relationship("User")

    def to_dict(self):
        return {
            'id': self.id,
            'procurement_number': self.procurement_number,
            'farmer_id': self.farmer_id,
            'variety': self.variety,
            'quantity': self.quantity,
            'moisture_content': self.moisture_content,
            'quality_grade': self.quality_grade,
            'price_per_kg': self.price_per_kg,
            'total_amount': self.total_amount,
            'broken_percentage': self.broken_percentage,
            'foreign_matter': self.foreign_matter,
            'chalky_grains': self.chalky_grains,
            'procurement_date': self.procurement_date.isoformat() if self.procurement_date else None,
            'status': self.status,
            'payment_status': self.payment_status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FarmerContract(db.Model):
    __tablename__ = 'farmer_contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    
    # Contract details
    contract_type = db.Column(db.String(50))  # seasonal, annual, spot
    variety = db.Column(db.String(50))
    quantity_committed = db.Column(db.Float)  # in kg
    price_per_kg = db.Column(db.Float)
    quality_specifications = db.Column(db.Text)  # JSON string
    
    # Timeline
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    delivery_schedule = db.Column(db.Text)  # JSON string
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    completion_percentage = db.Column(db.Float, default=0.0)
    
    # Terms and conditions
    payment_terms = db.Column(db.String(100))
    penalty_clauses = db.Column(db.Text)
    bonus_clauses = db.Column(db.Text)
    advance_amount = db.Column(db.Float, default=0.0)
    contract_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farmer = relationship("Farmer")
    created_by_user = relationship("User")

    def to_dict(self):
        return {
            'id': self.id,
            'contract_number': self.contract_number,
            'farmer_id': self.farmer_id,
            'contract_type': self.contract_type or 'seasonal',
            'variety': self.variety or 'Rice',
            'quantity_committed': self.quantity_committed or 0,
            'price_per_kg': self.price_per_kg or 0,
            'quality_specifications': json.loads(self.quality_specifications) if self.quality_specifications else {},
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'delivery_schedule': json.loads(self.delivery_schedule) if self.delivery_schedule else {},
            'status': self.status or 'active',
            'completion_percentage': self.completion_percentage or 0.0,
            'payment_terms': self.payment_terms or 'immediate',
            'penalty_clauses': self.penalty_clauses,
            'bonus_clauses': self.bonus_clauses,
            'advance_amount': self.advance_amount or 0.0,
            'contract_date': self.contract_date.isoformat() if self.contract_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
