"""
Notifications API Routes
Handles notification-related endpoints for the Smart Rice Mill ERP
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from models.notification import Notification, NotificationTemplate
from models.user import User
from services.notification_service import NotificationService
from extensions import db
import json

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications for current user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        category = request.args.get('category')
        priority = request.args.get('priority')
        
        # Get notifications using service
        notifications = NotificationService.get_notifications(
            user_id=user_id,
            role=user.role if user else None,
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
        # Apply additional filters
        if category:
            notifications = [n for n in notifications if n.category == category]
        
        if priority:
            notifications = [n for n in notifications if n.priority == priority]
        
        # Get notification stats
        stats = NotificationService.get_notification_stats(
            user_id=user_id,
            role=user.role if user else None
        )
        
        return jsonify({
            'success': True,
            'notifications': [n.to_dict() for n in notifications],
            'stats': stats,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(notifications)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching notifications: {str(e)}'
        }), 500

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    try:
        user_id = get_jwt_identity()
        
        notification = NotificationService.mark_as_read(notification_id, user_id)
        
        if notification:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read',
                'notification': notification.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Notification not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error marking notification as read: {str(e)}'
        }), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read for current user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        updated_count = NotificationService.mark_all_as_read(
            user_id=user_id,
            role=user.role if user else None
        )
        
        return jsonify({
            'success': True,
            'message': f'Marked {updated_count} notifications as read',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error marking notifications as read: {str(e)}'
        }), 500

@notifications_bp.route('/<int:notification_id>/archive', methods=['POST'])
@jwt_required()
def archive_notification(notification_id):
    """Archive a notification"""
    try:
        notification = NotificationService.archive_notification(notification_id)
        
        if notification:
            return jsonify({
                'success': True,
                'message': 'Notification archived',
                'notification': notification.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Notification not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error archiving notification: {str(e)}'
        }), 500

@notifications_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    """Get notification statistics for current user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        stats = NotificationService.get_notification_stats(
            user_id=user_id,
            role=user.role if user else None
        )
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching notification stats: {str(e)}'
        }), 500

@notifications_bp.route('/create', methods=['POST'])
@jwt_required()
def create_notification():
    """Create a new notification (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user has permission to create notifications
        if not user or user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Insufficient permissions'
            }), 403
        
        data = request.get_json()
        
        notification = Notification.create_notification(
            type=data.get('type'),
            title=data.get('title'),
            message=data.get('message'),
            priority=data.get('priority', 'medium'),
            category=data.get('category'),
            action_url=data.get('action_url'),
            action_type=data.get('action_type'),
            user_id=data.get('user_id'),
            role_target=data.get('role_target'),
            icon=data.get('icon'),
            farmer_id=data.get('farmer_id'),
            batch_id=data.get('batch_id'),
            contract_id=data.get('contract_id'),
            inventory_id=data.get('inventory_id'),
            created_by=user_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Notification created successfully',
            'notification': notification.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating notification: {str(e)}'
        }), 500

@notifications_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_notification_templates():
    """Get notification templates (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Insufficient permissions'
            }), 403
        
        templates = NotificationTemplate.query.all()
        
        return jsonify({
            'success': True,
            'templates': [t.to_dict() for t in templates]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching templates: {str(e)}'
        }), 500

@notifications_bp.route('/cleanup', methods=['POST'])
@jwt_required()
def cleanup_expired_notifications():
    """Clean up expired notifications (admin only)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Insufficient permissions'
            }), 403
        
        expired_count = NotificationService.cleanup_expired_notifications()
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {expired_count} expired notifications',
            'expired_count': expired_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error cleaning up notifications: {str(e)}'
        }), 500

# Webhook endpoints for external systems to create notifications
@notifications_bp.route('/webhook/farmer-registered', methods=['POST'])
def webhook_farmer_registered():
    """Webhook for farmer registration notifications"""
    try:
        data = request.get_json()
        
        # Verify webhook authenticity here if needed
        
        farmer_data = data.get('farmer', {})
        
        notification = NotificationService.create_farmer_registration_notification(farmer_data)
        
        return jsonify({
            'success': True,
            'message': 'Notification created',
            'notification_id': notification.id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating notification: {str(e)}'
        }), 500

@notifications_bp.route('/webhook/low-stock', methods=['POST'])
def webhook_low_stock():
    """Webhook for low stock notifications"""
    try:
        data = request.get_json()
        
        item_data = data.get('item', {})
        
        notification = NotificationService.create_inventory_low_stock_notification(item_data)
        
        return jsonify({
            'success': True,
            'message': 'Low stock notification created',
            'notification_id': notification.id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating notification: {str(e)}'
        }), 500