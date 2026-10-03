"""
Financial Models
Additional financial models for the intelligence module
"""

from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from extensions import db

class Transaction(db.Model):
    """Financial transaction model"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    transaction_id = db.Column(db.String(50), unique=True, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # income, expense
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))
    reference_id = db.Column(db.String(50))  # Reference to other entities
    transaction_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount),
            'description': self.description,
            'category': self.category,
            'reference_id': self.reference_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

class Invoice(db.Model):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    invoice_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid, overdue, cancelled
    payment_terms = db.Column(db.String(20), default='net_30')
    notes = db.Column(db.Text)
    invoice_items = db.Column(db.JSON)  # Store invoice items as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_terms': self.payment_terms,
            'notes': self.notes,
            'invoice_items': self.invoice_items,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
    
    def set_invoice_items(self, items):
        """Set invoice items as JSON"""
        self.invoice_items = items
    
    def get_invoice_items(self):
        """Get invoice items from JSON"""
        return self.invoice_items or []

class FinancialAlert(db.Model):
    """Financial alerts and notifications"""
    __tablename__ = 'financial_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # cash_flow, payment, health_score
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON)  # Additional alert data
    is_read = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'is_read': self.is_read,
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_by': self.created_by
        }

class CashFlowForecast(db.Model):
    """Cash flow forecast data"""
    __tablename__ = 'cash_flow_forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    forecast_date = db.Column(db.DateTime, nullable=False)
    predicted_inflow = db.Column(db.Float, default=0)
    predicted_outflow = db.Column(db.Float, default=0)
    predicted_balance = db.Column(db.Float, default=0)
    confidence_score = db.Column(db.Float, default=0.5)
    forecast_type = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    model_version = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'forecast_date': self.forecast_date.isoformat() if self.forecast_date else None,
            'predicted_inflow': float(self.predicted_inflow),
            'predicted_outflow': float(self.predicted_outflow),
            'predicted_balance': float(self.predicted_balance),
            'confidence_score': float(self.confidence_score),
            'forecast_type': self.forecast_type,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

class FinancialHealthScore(db.Model):
    """Financial health score tracking"""
    __tablename__ = 'financial_health_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    score_date = db.Column(db.DateTime, nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    health_grade = db.Column(db.String(2), nullable=False)
    component_scores = db.Column(db.JSON)  # Individual component scores
    financial_ratios = db.Column(db.JSON)  # Financial ratios used
    recommendations = db.Column(db.JSON)  # Improvement recommendations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'score_date': self.score_date.isoformat() if self.score_date else None,
            'overall_score': float(self.overall_score),
            'health_grade': self.health_grade,
            'component_scores': self.component_scores,
            'financial_ratios': self.financial_ratios,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
    
    def set_component_scores(self, scores):
        """Set component scores as JSON"""
        self.component_scores = scores
    
    def get_component_scores(self):
        """Get component scores from JSON"""
        return self.component_scores or {}
    
    def set_financial_ratios(self, ratios):
        """Set financial ratios as JSON"""
        self.financial_ratios = ratios
    
    def get_financial_ratios(self):
        """Get financial ratios from JSON"""
        return self.financial_ratios or {}
    
    def set_recommendations(self, recommendations):
        """Set recommendations as JSON"""
        self.recommendations = recommendations
    
    def get_recommendations(self):
        """Get recommendations from JSON"""
        return self.recommendations or []

class PaymentSchedule(db.Model):
    """Smart payment scheduling"""
    __tablename__ = 'payment_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    schedule_id = db.Column(db.String(50), unique=True, nullable=False)
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    risk_score = db.Column(db.Float, default=0.5)
    recommended_terms = db.Column(db.String(20))
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, processed, cancelled
    ai_recommendations = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'farmer_id': self.farmer_id,
            'amount': float(self.amount),
            'payment_type': self.payment_type,
            'risk_score': float(self.risk_score),
            'recommended_terms': self.recommended_terms,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'status': self.status,
            'ai_recommendations': self.ai_recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }
    
    def set_ai_recommendations(self, recommendations):
        """Set AI recommendations as JSON"""
        self.ai_recommendations = recommendations
    
    def get_ai_recommendations(self):
        """Get AI recommendations from JSON"""
        return self.ai_recommendations or []
