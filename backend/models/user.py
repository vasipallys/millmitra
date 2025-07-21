"""
User Management Models
"""

from datetime import datetime
import json
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50), default='operator')
    department = db.Column(db.String(50))

    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)

    # AI and biometric data
    voice_print_data = db.Column(db.Text)  # Encrypted voice biometric data
    face_encoding = db.Column(db.Text)     # Encrypted facial recognition data
    fingerprint_data = db.Column(db.Text)  # Encrypted fingerprint data
    
    # Preferences and settings
    preferences = db.Column(db.Text)  # JSON string
    dashboard_layout = db.Column(db.Text)  # Custom dashboard configuration
    notification_settings = db.Column(db.Text)  # Notification preferences

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_preferences(self):
        if self.preferences:
            try:
                return json.loads(self.preferences)
            except:
                return {}
        return {}

    def set_preferences(self, prefs):
        self.preferences = json.dumps(prefs)

    def get_dashboard_layout(self):
        if self.dashboard_layout:
            try:
                return json.loads(self.dashboard_layout)
            except:
                return {}
        return {}

    def set_dashboard_layout(self, layout):
        self.dashboard_layout = json.dumps(layout)

    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        role_permissions = {
            'super_admin': ['*'],  # All permissions
            'admin': ['manage_users', 'manage_inventory', 'manage_production', 'manage_sales', 'manage_finance', 'view_reports'],
            'manager': ['manage_inventory', 'manage_production', 'manage_sales', 'view_reports'],
            'supervisor': ['manage_production', 'manage_inventory', 'view_reports'],
            'operator': ['view_production', 'update_production', 'view_inventory'],
            'sales': ['manage_sales', 'view_customers', 'view_reports'],
            'quality_control': ['manage_quality', 'view_production', 'view_reports'],
            'finance': ['manage_finance', 'view_sales', 'view_reports'],
            'viewer': ['view_reports']
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return '*' in user_permissions or permission in user_permissions

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'phone': self.phone,
            'role': self.role,
            'department': self.department,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'preferences': self.get_preferences(),
            'dashboard_layout': self.get_dashboard_layout(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_biometric_data': bool(self.voice_print_data or self.face_encoding or self.fingerprint_data)
        }

class AuthLog(db.Model):
    __tablename__ = 'auth_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username_attempted = db.Column(db.String(120))
    action = db.Column(db.String(50))  # login, logout, failed_login, password_reset
    method = db.Column(db.String(50))  # password, voice, biometric, otp
    success = db.Column(db.Boolean)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    device_fingerprint = db.Column(db.String(255))
    location = db.Column(db.String(100))
    failure_reason = db.Column(db.String(100))
    risk_score = db.Column(db.Float)  # AI-calculated risk score
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username_attempted': self.username_attempted,
            'action': self.action,
            'method': self.method,
            'success': self.success,
            'ip_address': self.ip_address,
            'location': self.location,
            'failure_reason': self.failure_reason,
            'risk_score': self.risk_score,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    device_info = db.Column(db.Text)  # JSON string with device information
    ip_address = db.Column(db.String(45))
    is_active = db.Column(db.Boolean, default=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_info': json.loads(self.device_info) if self.device_info else {},
            'ip_address': self.ip_address,
            'is_active': self.is_active,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
