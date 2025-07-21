"""
Finance Management Models
"""

from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Payment details
    payment_type = db.Column(db.String(20), nullable=False)  # received, paid
    payment_category = db.Column(db.String(50))  # customer_payment, farmer_payment, expense_payment, salary
    
    # Related entities
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'))
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'))
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'))
    
    # Amount details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    
    # Payment method
    payment_method = db.Column(db.String(50))  # cash, bank_transfer, cheque, upi, card
    reference_number = db.Column(db.String(100))  # transaction/cheque number
    bank_details = db.Column(db.Text)  # JSON string with bank information
    
    # Dates
    payment_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime)
    cleared_date = db.Column(db.DateTime)  # when payment was cleared/realized
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, cleared, failed, cancelled
    
    # Tax information
    tds_amount = db.Column(db.Float, default=0.0)
    tds_percentage = db.Column(db.Float, default=0.0)
    gst_amount = db.Column(db.Float, default=0.0)
    
    # Additional information
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # AI insights
    fraud_risk_score = db.Column(db.Float)  # AI-calculated fraud risk
    payment_behavior_impact = db.Column(db.Float)  # Impact on customer/farmer behavior score
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer")
    farmer = relationship("Farmer")
    sales_order = relationship("SalesOrder")
    created_by_user = relationship("User", foreign_keys=[created_by])
    approved_by_user = relationship("User", foreign_keys=[approved_by])

    def get_bank_details(self):
        if self.bank_details:
            try:
                return json.loads(self.bank_details)
            except:
                return {}
        return {}

    def set_bank_details(self, details):
        self.bank_details = json.dumps(details)

    def is_overdue(self):
        """Check if payment is overdue"""
        if self.due_date and self.status == 'pending':
            return datetime.utcnow() > self.due_date
        return False

    def get_days_overdue(self):
        """Get number of days overdue"""
        if self.is_overdue():
            return (datetime.utcnow() - self.due_date).days
        return 0

    def calculate_net_amount(self):
        """Calculate net amount after deductions"""
        return self.amount - (self.tds_amount or 0)

    def get_payment_insights(self):
        """Get AI-powered payment insights"""
        insights = []
        
        # Overdue analysis
        if self.is_overdue():
            days_overdue = self.get_days_overdue()
            insights.append({
                'type': 'overdue',
                'message': f'Payment is {days_overdue} days overdue',
                'priority': 'high' if days_overdue > 30 else 'medium'
            })
        
        # Fraud risk
        if self.fraud_risk_score and self.fraud_risk_score > 0.7:
            insights.append({
                'type': 'fraud_risk',
                'message': f'High fraud risk score ({self.fraud_risk_score*100:.1f}%)',
                'priority': 'critical'
            })
        
        # Large amount alert
        if self.amount > 100000:  # 1 lakh
            insights.append({
                'type': 'large_amount',
                'message': f'Large payment amount: ₹{self.amount:,.0f}',
                'priority': 'medium'
            })
        
        return insights

    def to_dict(self):
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'payment_type': self.payment_type,
            'payment_category': self.payment_category,
            'customer_id': self.customer_id,
            'farmer_id': self.farmer_id,
            'sales_order_id': self.sales_order_id,
            'expense_id': self.expense_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'bank_details': self.get_bank_details(),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'cleared_date': self.cleared_date.isoformat() if self.cleared_date else None,
            'status': self.status,
            'tds_amount': self.tds_amount,
            'tds_percentage': self.tds_percentage,
            'gst_amount': self.gst_amount,
            'description': self.description,
            'notes': self.notes,
            'fraud_risk_score': self.fraud_risk_score,
            'payment_behavior_impact': self.payment_behavior_impact,
            'net_amount': self.calculate_net_amount(),
            'is_overdue': self.is_overdue(),
            'days_overdue': self.get_days_overdue(),
            'payment_insights': self.get_payment_insights(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Expense details
    expense_category = db.Column(db.String(50), nullable=False)  # operational, maintenance, salary, utilities, transport
    expense_type = db.Column(db.String(50))  # electricity, fuel, repairs, wages, etc.
    description = db.Column(db.String(200), nullable=False)
    
    # Amount details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    
    # Vendor/Payee information
    vendor_name = db.Column(db.String(100))
    vendor_contact = db.Column(db.String(50))
    vendor_gst = db.Column(db.String(20))
    
    # Dates
    expense_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime)
    paid_date = db.Column(db.DateTime)
    
    # Payment details
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    
    # Tax information
    gst_amount = db.Column(db.Float, default=0.0)
    gst_percentage = db.Column(db.Float, default=0.0)
    tds_amount = db.Column(db.Float, default=0.0)
    tds_percentage = db.Column(db.Float, default=0.0)
    
    # Approval workflow
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.DateTime)
    approval_notes = db.Column(db.Text)
    
    # Budget tracking
    budget_category = db.Column(db.String(50))
    budget_allocated = db.Column(db.Float)
    budget_utilized = db.Column(db.Float)
    
    # AI insights
    anomaly_score = db.Column(db.Float)  # AI-detected anomaly score
    budget_impact = db.Column(db.Float)  # Impact on budget
    cost_optimization_suggestions = db.Column(db.Text)  # JSON string
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    approved_by_user = relationship("User", foreign_keys=[approved_by])
    created_by_user = relationship("User", foreign_keys=[created_by])

    def get_cost_optimization_suggestions(self):
        if self.cost_optimization_suggestions:
            try:
                return json.loads(self.cost_optimization_suggestions)
            except:
                return []
        return []

    def set_cost_optimization_suggestions(self, suggestions):
        self.cost_optimization_suggestions = json.dumps(suggestions)

    def is_overdue(self):
        """Check if expense payment is overdue"""
        if self.due_date and self.payment_status == 'pending':
            return datetime.utcnow() > self.due_date
        return False

    def get_total_amount(self):
        """Get total amount including taxes"""
        return self.amount + (self.gst_amount or 0)

    def get_net_payable(self):
        """Get net payable amount after TDS"""
        return self.get_total_amount() - (self.tds_amount or 0)

    def analyze_expense_pattern(self):
        """AI-powered expense pattern analysis"""
        analysis = {
            'category_trend': 'normal',
            'amount_variance': 'normal',
            'frequency_pattern': 'normal',
            'recommendations': []
        }
        
        # Amount variance analysis
        if self.anomaly_score and self.anomaly_score > 0.8:
            analysis['amount_variance'] = 'high'
            analysis['recommendations'].append({
                'type': 'amount_review',
                'message': 'Expense amount significantly higher than usual',
                'priority': 'medium'
            })
        
        # Budget impact
        if self.budget_allocated and self.amount > self.budget_allocated * 0.8:
            analysis['recommendations'].append({
                'type': 'budget_alert',
                'message': f'Expense uses {(self.amount/self.budget_allocated)*100:.1f}% of allocated budget',
                'priority': 'high'
            })
        
        return analysis

    def get_expense_insights(self):
        """Get AI-powered expense insights"""
        insights = []
        
        # Overdue payment
        if self.is_overdue():
            days_overdue = (datetime.utcnow() - self.due_date).days
            insights.append({
                'type': 'payment_overdue',
                'message': f'Payment is {days_overdue} days overdue',
                'priority': 'high'
            })
        
        # High amount alert
        if self.amount > 50000:  # 50k threshold
            insights.append({
                'type': 'high_amount',
                'message': f'High expense amount: ₹{self.amount:,.0f}',
                'priority': 'medium'
            })
        
        # Approval pending
        if self.approval_status == 'pending' and self.amount > 10000:
            insights.append({
                'type': 'approval_pending',
                'message': 'High-value expense pending approval',
                'priority': 'medium'
            })
        
        return insights

    def to_dict(self):
        return {
            'id': self.id,
            'expense_id': self.expense_id,
            'expense_category': self.expense_category,
            'expense_type': self.expense_type,
            'description': self.description,
            'amount': self.amount,
            'currency': self.currency,
            'vendor_name': self.vendor_name,
            'vendor_contact': self.vendor_contact,
            'vendor_gst': self.vendor_gst,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'payment_status': self.payment_status,
            'gst_amount': self.gst_amount,
            'gst_percentage': self.gst_percentage,
            'tds_amount': self.tds_amount,
            'tds_percentage': self.tds_percentage,
            'approval_status': self.approval_status,
            'approved_by': self.approved_by,
            'approval_date': self.approval_date.isoformat() if self.approval_date else None,
            'approval_notes': self.approval_notes,
            'budget_category': self.budget_category,
            'budget_allocated': self.budget_allocated,
            'budget_utilized': self.budget_utilized,
            'anomaly_score': self.anomaly_score,
            'budget_impact': self.budget_impact,
            'cost_optimization_suggestions': self.get_cost_optimization_suggestions(),
            'total_amount': self.get_total_amount(),
            'net_payable': self.get_net_payable(),
            'is_overdue': self.is_overdue(),
            'expense_pattern_analysis': self.analyze_expense_pattern(),
            'expense_insights': self.get_expense_insights(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Budget details
    budget_name = db.Column(db.String(100), nullable=False)
    budget_category = db.Column(db.String(50), nullable=False)
    budget_period = db.Column(db.String(20))  # monthly, quarterly, yearly
    
    # Amount details
    allocated_amount = db.Column(db.Float, nullable=False)
    utilized_amount = db.Column(db.Float, default=0.0)
    remaining_amount = db.Column(db.Float)
    
    # Period
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, completed, exceeded, cancelled
    
    # AI insights
    utilization_forecast = db.Column(db.Float)  # AI-predicted utilization
    overspend_risk = db.Column(db.Float)  # AI-calculated overspend risk
    
    # Audit fields
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.remaining_amount:
            self.remaining_amount = self.allocated_amount

    def get_utilization_percentage(self):
        """Get budget utilization percentage"""
        if self.allocated_amount > 0:
            return (self.utilized_amount / self.allocated_amount) * 100
        return 0.0

    def update_utilization(self, expense_amount):
        """Update budget utilization"""
        self.utilized_amount = (self.utilized_amount or 0) + expense_amount
        self.remaining_amount = self.allocated_amount - self.utilized_amount
        
        # Update status based on utilization
        utilization_pct = self.get_utilization_percentage()
        if utilization_pct >= 100:
            self.status = 'exceeded'
        elif utilization_pct >= 90:
            self.status = 'critical'

    def get_budget_alerts(self):
        """Get budget-related alerts"""
        alerts = []
        utilization_pct = self.get_utilization_percentage()
        
        if utilization_pct >= 100:
            alerts.append({
                'type': 'budget_exceeded',
                'message': f'Budget exceeded by {utilization_pct-100:.1f}%',
                'priority': 'critical'
            })
        elif utilization_pct >= 90:
            alerts.append({
                'type': 'budget_critical',
                'message': f'Budget {utilization_pct:.1f}% utilized',
                'priority': 'high'
            })
        elif utilization_pct >= 75:
            alerts.append({
                'type': 'budget_warning',
                'message': f'Budget {utilization_pct:.1f}% utilized',
                'priority': 'medium'
            })
        
        return alerts

    def to_dict(self):
        return {
            'id': self.id,
            'budget_id': self.budget_id,
            'budget_name': self.budget_name,
            'budget_category': self.budget_category,
            'budget_period': self.budget_period,
            'allocated_amount': self.allocated_amount,
            'utilized_amount': self.utilized_amount,
            'remaining_amount': self.remaining_amount,
            'utilization_percentage': self.get_utilization_percentage(),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'utilization_forecast': self.utilization_forecast,
            'overspend_risk': self.overspend_risk,
            'budget_alerts': self.get_budget_alerts(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
