"""
Notification Management Models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # farmer_registration, production_complete, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Priority and categorization
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50))  # farmer_management, production, inventory, etc.
    
    # Status tracking
    read = db.Column(db.Boolean, default=False)
    archived = db.Column(db.Boolean, default=False)
    
    # Navigation and actions
    action_url = db.Column(db.String(200))
    action_type = db.Column(db.String(50))  # navigate, approve, reject, etc.
    action_data = db.Column(db.Text)  # JSON string for additional data
    
    # User targeting
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # specific user, null for all users
    role_target = db.Column(db.String(50))  # admin, manager, operator - for role-based notifications
    
    # Metadata
    icon = db.Column(db.String(50))
    expires_at = db.Column(db.DateTime)  # for time-sensitive notifications
    
    # Related entities
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=True)
    batch_id = db.Column(db.Integer, nullable=True)  # production batch reference
    contract_id = db.Column(db.Integer, nullable=True)  # contract reference
    inventory_id = db.Column(db.Integer, nullable=True)  # inventory item reference
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    farmer = relationship("Farmer", foreign_keys=[farmer_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'priority': self.priority,
            'category': self.category,
            'read': self.read,
            'archived': self.archived,
            'action_url': self.action_url,
            'action_type': self.action_type,
            'action_data': self.action_data,
            'user_id': self.user_id,
            'role_target': self.role_target,
            'icon': self.icon,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'farmer_id': self.farmer_id,
            'batch_id': self.batch_id,
            'contract_id': self.contract_id,
            'inventory_id': self.inventory_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by,
            # Related data
            'farmer_name': self.farmer.name if self.farmer else None,
            'creator_name': self.creator.username if self.creator else None
        }
    
    @staticmethod
    def create_notification(
        type, title, message,
        priority='medium', category=None,
        action_url=None, action_type=None, action_data=None,
        user_id=None, role_target=None,
        icon=None, expires_at=None,
        farmer_id=None, batch_id=None, contract_id=None, inventory_id=None,
        created_by=None
    ):
        """Helper method to create notifications"""
        notification = Notification(
            type=type,
            title=title,
            message=message,
            priority=priority,
            category=category,
            action_url=action_url,
            action_type=action_type,
            action_data=action_data,
            user_id=user_id,
            role_target=role_target,
            icon=icon,
            expires_at=expires_at,
            farmer_id=farmer_id,
            batch_id=batch_id,
            contract_id=contract_id,
            inventory_id=inventory_id,
            created_by=created_by
        )
        
        db.session.add(notification)
        db.session.commit()
        return notification

class NotificationTemplate(db.Model):
    __tablename__ = 'notification_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), unique=True, nullable=False)
    title_template = db.Column(db.String(200), nullable=False)
    message_template = db.Column(db.Text, nullable=False)
    
    # Default settings
    default_priority = db.Column(db.String(20), default='medium')
    default_category = db.Column(db.String(50))
    default_icon = db.Column(db.String(50))
    
    # Behavior settings
    is_active = db.Column(db.Boolean, default=True)
    auto_expire_hours = db.Column(db.Integer)  # auto-expire after X hours
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title_template': self.title_template,
            'message_template': self.message_template,
            'default_priority': self.default_priority,
            'default_category': self.default_category,
            'default_icon': self.default_icon,
            'is_active': self.is_active,
            'auto_expire_hours': self.auto_expire_hours,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }