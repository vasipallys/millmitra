"""
Rice Mill Management System - Database Models

This module contains all the database models for the rice mill management system.
Models are organized by functional areas for better maintainability.
"""

# Standard library imports
from datetime import datetime
import json

# Third-party imports
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

# Local imports
from extensions import db

# =============================================================================
# AI INTERACTION MODELS
# =============================================================================

class AIInteraction(db.Model):
    __tablename__ = 'ai_interactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    query = db.Column(db.String(500))
    response = db.Column(db.Text)
    context = db.Column(db.JSON)
    interaction_type = db.Column(db.String(50))  # voice, text, dashboard
    confidence_score = db.Column(db.Float)
    processing_time = db.Column(db.Float)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =============================================================================
# IMPORTS FROM OTHER MODEL FILES
# =============================================================================

# Import models from separate files
try:
    from .user import User, AuthLog, UserSession, UserPreference
except ImportError:
    pass

try:
    from .farmer import Farmer, FarmerContract, PaddyProcurement
except ImportError:
    pass

try:
    from .inventory import PaddyStock, ProductStock
except ImportError:
    pass

try:
    from .production import ProductionBatch, QualityTest
except ImportError:
    pass

try:
    from .sales import Customer, SalesOrder
except ImportError:
    pass

try:
    from .finance import Payment, Expense, Budget
except ImportError:
    pass

try:
    from .financial import Transaction, Invoice, FinancialAlert, CashFlowForecast, FinancialHealthScore, PaymentSchedule
except ImportError:
    pass

try:
    from .maintenance import Equipment, MaintenanceSchedule, MaintenanceTask, EquipmentReading, SparePart
except ImportError:
    pass

try:
    from .logistics import Vehicle, Driver, Route, Shipment, ShipmentItem, ShipmentTracking, VehicleMaintenance
except ImportError:
    pass

try:
    from .quality import QualityStandard, QualityTestTemplate, QualityInspection, QualityAlert, QualityTrend
except ImportError:
    pass

try:
    from .compliance import ComplianceFramework, ComplianceAssessment, ComplianceActionItem, RegulatoryDocument, ComplianceAlert, AuditTrail
except ImportError:
    pass

try:
    from .analytics import Dashboard, DashboardWidget, Report, ReportExecution, KPI, KPIValue, DataAlert, AlertTrigger
except ImportError:
    pass

# Export all models
__all__ = [
    'User', 'AuthLog', 'AIInteraction', 'UserSession', 'UserPreference',
    'Farmer', 'FarmerContract', 'PaddyProcurement', 'PaddyStock', 'ProductStock',
    'ProductionBatch', 'QualityTest', 'Customer', 'SalesOrder',
    'Payment', 'Expense', 'Budget', 'Transaction', 'Invoice',
    'FinancialAlert', 'CashFlowForecast', 'FinancialHealthScore', 'PaymentSchedule',
    'Equipment', 'MaintenanceSchedule', 'MaintenanceTask', 'EquipmentReading', 'SparePart',
    'Vehicle', 'Driver', 'Route', 'Shipment', 'ShipmentItem', 'ShipmentTracking', 'VehicleMaintenance',
    'QualityStandard', 'QualityTestTemplate', 'QualityInspection', 'QualityAlert', 'QualityTrend',
    'ComplianceFramework', 'ComplianceAssessment', 'ComplianceActionItem', 'RegulatoryDocument', 'ComplianceAlert', 'AuditTrail',
    'Dashboard', 'DashboardWidget', 'Report', 'ReportExecution', 'KPI', 'KPIValue', 'DataAlert', 'AlertTrigger'
]
