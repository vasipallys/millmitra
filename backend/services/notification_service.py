"""
Notification Service
Handles notification creation, management, and delivery
"""

from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models.notification import Notification, NotificationTemplate
from models.user import User
from extensions import db
import json

class NotificationService:
    
    @staticmethod
    def create_farmer_registration_notification(farmer):
        """Create notification for new farmer registration"""
        return Notification.create_notification(
            type='farmer_registration',
            title='New Farmer Registration',
            message=f'{farmer.name} has registered and is pending verification',
            priority='medium',
            category='farmer_management',
            action_url='/farmers',
            action_type='navigate',
            role_target='admin',
            icon='person_add',
            farmer_id=farmer.id
        )
    
    @staticmethod
    def create_farmer_verification_notification(farmer, verified_by):
        """Create notification when farmer is verified"""
        return Notification.create_notification(
            type='farmer_verified',
            title='Farmer Verified',
            message=f'{farmer.name} has been verified and approved',
            priority='low',
            category='farmer_management',
            action_url=f'/farmers/{farmer.id}',
            action_type='navigate',
            role_target='manager',
            icon='verified_user',
            farmer_id=farmer.id,
            created_by=verified_by
        )
    
    @staticmethod
    def create_production_batch_notification(batch_data):
        """Create notification for production batch completion"""
        return Notification.create_notification(
            type='production_complete',
            title='Production Batch Completed',
            message=f'Production batch #{batch_data.get("batch_number")} has been completed successfully',
            priority='medium',
            category='production',
            action_url='/production',
            action_type='navigate',
            role_target='operator',
            icon='manufacturing',
            batch_id=batch_data.get('id')
        )
    
    @staticmethod
    def create_inventory_low_stock_notification(item):
        """Create notification for low stock items"""
        return Notification.create_notification(
            type='inventory_low',
            title='Low Stock Alert',
            message=f'{item.get("name", "Unknown item")} stock is running low ({item.get("quantity", 0)} remaining)',
            priority='high',
            category='inventory',
            action_url='/inventory',
            action_type='navigate',
            role_target='manager',
            icon='warning',
            inventory_id=item.get('id')
        )
    
    @staticmethod
    def create_contract_expiring_notification(contract):
        """Create notification for expiring contracts"""
        return Notification.create_notification(
            type='contract_expiring',
            title='Contract Expiring Soon',
            message=f'Contract with {contract.get("farmer_name", "Unknown farmer")} expires in 7 days',
            priority='high',
            category='contracts',
            action_url='/contracts',
            action_type='navigate',
            role_target='admin',
            icon='schedule',
            contract_id=contract.get('id'),
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
    
    @staticmethod
    def create_quality_issue_notification(quality_data):
        """Create notification for quality issues"""
        return Notification.create_notification(
            type='quality_issue',
            title='Quality Issue Detected',
            message=f'Quality issue detected in batch #{quality_data.get("batch_number")}',
            priority='urgent',
            category='quality',
            action_url='/quality',
            action_type='navigate',
            role_target='admin',
            icon='report_problem',
            batch_id=quality_data.get('batch_id')
        )
    
    @staticmethod
    def get_notifications(user_id=None, role=None, limit=50, offset=0, unread_only=False):
        """Get notifications for user or role"""
        query = Notification.query.filter(Notification.archived == False)
        
        # Filter by user or role
        if user_id:
            query = query.filter(
                or_(
                    Notification.user_id == user_id,
                    Notification.user_id.is_(None)  # Global notifications
                )
            )
        
        if role:
            query = query.filter(
                or_(
                    Notification.role_target == role,
                    Notification.role_target.is_(None)  # Global notifications
                )
            )
        
        # Filter by read status
        if unread_only:
            query = query.filter(Notification.read == False)
        
        # Filter expired notifications
        query = query.filter(
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
        
        # Order by priority and creation time
        priority_order = {
            'urgent': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        notifications = query.order_by(
            Notification.read.asc(),  # Unread first
            Notification.created_at.desc()  # Newest first
        ).limit(limit).offset(offset).all()
        
        return notifications
    
    @staticmethod
    def mark_as_read(notification_id, user_id=None):
        """Mark notification as read"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.read = True
            notification.updated_at = datetime.utcnow()
            db.session.commit()
            return notification
        return None
    
    @staticmethod
    def mark_all_as_read(user_id=None, role=None):
        """Mark all notifications as read for user/role"""
        query = Notification.query.filter(Notification.read == False)
        
        if user_id:
            query = query.filter(
                or_(
                    Notification.user_id == user_id,
                    Notification.user_id.is_(None)
                )
            )
        
        if role:
            query = query.filter(
                or_(
                    Notification.role_target == role,
                    Notification.role_target.is_(None)
                )
            )
        
        updated_count = query.update({'read': True, 'updated_at': datetime.utcnow()})
        db.session.commit()
        return updated_count
    
    @staticmethod
    def archive_notification(notification_id):
        """Archive a notification"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.archived = True
            notification.updated_at = datetime.utcnow()
            db.session.commit()
            return notification
        return None
    
    @staticmethod
    def get_notification_stats(user_id=None, role=None):
        """Get notification statistics"""
        base_query = Notification.query.filter(Notification.archived == False)
        
        if user_id:
            base_query = base_query.filter(
                or_(
                    Notification.user_id == user_id,
                    Notification.user_id.is_(None)
                )
            )
        
        if role:
            base_query = base_query.filter(
                or_(
                    Notification.role_target == role,
                    Notification.role_target.is_(None)
                )
            )
        
        total = base_query.count()
        unread = base_query.filter(Notification.read == False).count()
        urgent = base_query.filter(Notification.priority == 'urgent').count()
        high = base_query.filter(Notification.priority == 'high').count()
        
        return {
            'total': total,
            'unread': unread,
            'urgent': urgent,
            'high': high,
            'read': total - unread
        }
    
    @staticmethod
    def cleanup_expired_notifications():
        """Remove expired notifications"""
        expired_count = Notification.query.filter(
            and_(
                Notification.expires_at.isnot(None),
                Notification.expires_at < datetime.utcnow()
            )
        ).delete()
        
        db.session.commit()
        return expired_count
    
    @staticmethod
    def create_template_based_notification(template_type, context_data, **override_params):
        """Create notification using template"""
        template = NotificationTemplate.query.filter_by(type=template_type, is_active=True).first()
        
        if not template:
            raise ValueError(f"No active template found for type: {template_type}")
        
        # Format title and message using context data
        title = template.title_template.format(**context_data)
        message = template.message_template.format(**context_data)
        
        # Set default values from template
        params = {
            'type': template_type,
            'title': title,
            'message': message,
            'priority': template.default_priority,
            'category': template.default_category,
            'icon': template.default_icon
        }
        
        # Add auto-expiry if configured
        if template.auto_expire_hours:
            params['expires_at'] = datetime.utcnow() + timedelta(hours=template.auto_expire_hours)
        
        # Override with provided parameters
        params.update(override_params)
        
        return Notification.create_notification(**params)