"""
Notifications API Routes
Handles notification-related endpoints for the Smart Rice Mill ERP
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
import uuid

notifications_bp = Blueprint('notifications', __name__)

# Mock notifications data for development
mock_notifications = [
    {
        'id': 1,
        'type': 'farmer_registration',
        'title': 'New Farmer Registration',
        'message': 'Siva Kumar reddy Vasipally has registered and is pending approval',
        'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
        'read': False,
        'priority': 'medium',
        'category': 'farmer_management',
        'action_url': '/farmers',
        'icon': 'person_add'
    },
    {
        'id': 2,
        'type': 'production_complete',
        'title': 'Production Batch Completed',
        'message': 'Production batch #PB001 has been completed successfully',
        'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
        'read': False,
        'priority': 'low',
        'category': 'production',
        'action_url': '/production',
        'icon': 'check_circle'
    },
    {
        'id': 3,
        'type': 'inventory_alert',
        'title': 'Low Stock Alert',
        'message': 'Basmati Rice stock is running low (Current: 50 kg, Minimum: 100 kg)',
        'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
        'read': False,
        'priority': 'high',
        'category': 'inventory',
        'action_url': '/inventory',
        'icon': 'warning'
    },
    {
        'id': 4,
        'type': 'quality_alert',
        'title': 'Quality Check Required',
        'message': 'Batch #QC001 requires immediate quality inspection',
        'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
        'read': True,
        'priority': 'high',
        'category': 'quality',
        'action_url': '/quality-control',
        'icon': 'science'
    },
    {
        'id': 5,
        'type': 'payment_received',
        'title': 'Payment Received',
        'message': 'Payment of ₹25,000 received from ABC Distributors',
        'timestamp': (datetime.now() - timedelta(hours=3)).isoformat(),
        'read': True,
        'priority': 'low',
        'category': 'finance',
        'action_url': '/finance',
        'icon': 'payment'
    },
    {
        'id': 6,
        'type': 'system_update',
        'title': 'System Update Available',
        'message': 'A new system update (v2.1.0) is available with enhanced AI features',
        'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
        'read': False,
        'priority': 'medium',
        'category': 'system',
        'action_url': '/settings',
        'icon': 'system_update'
    }
]

@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get all notifications"""
    try:
        # Calculate unread count
        unread_count = len([n for n in mock_notifications if not n['read']])
        
        return jsonify({
            'success': True,
            'notifications': mock_notifications,
            'unread_count': unread_count,
            'total': len(mock_notifications)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notifications_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        # Find the notification
        notification = next((n for n in mock_notifications if n['id'] == notification_id), None)
        
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Mark as read
        notification['read'] = True
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notifications_bp.route('/notifications/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        # Mark all as read
        for notification in mock_notifications:
            notification['read'] = True
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notifications_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        # Find and remove the notification
        global mock_notifications
        mock_notifications = [n for n in mock_notifications if n['id'] != notification_id]
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notifications_bp.route('/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    """Create a new notification"""
    try:
        data = request.get_json()
        
        # Generate new notification
        new_notification = {
            'id': max([n['id'] for n in mock_notifications]) + 1 if mock_notifications else 1,
            'type': data.get('type', 'general'),
            'title': data.get('title', 'New Notification'),
            'message': data.get('message', ''),
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'priority': data.get('priority', 'medium'),
            'category': data.get('category', 'system'),
            'action_url': data.get('action_url', ''),
            'icon': data.get('icon', 'info')
        }
        
        # Add to notifications
        mock_notifications.insert(0, new_notification)
        
        return jsonify({
            'success': True,
            'notification': new_notification,
            'message': 'Notification created'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notifications_bp.route('/notifications/categories', methods=['GET'])
@jwt_required()
def get_notification_categories():
    """Get notification categories"""
    try:
        categories = [
            {'id': 'farmer_management', 'name': 'Farmer Management', 'icon': 'person_add'},
            {'id': 'production', 'name': 'Production', 'icon': 'factory'},
            {'id': 'inventory', 'name': 'Inventory', 'icon': 'inventory'},
            {'id': 'quality', 'name': 'Quality Control', 'icon': 'science'},
            {'id': 'finance', 'name': 'Finance', 'icon': 'payment'},
            {'id': 'system', 'name': 'System', 'icon': 'settings'}
        ]
        
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notifications_bp.route('/notifications/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    """Get notification statistics"""
    try:
        total = len(mock_notifications)
        unread = len([n for n in mock_notifications if not n['read']])
        
        # Count by priority
        high_priority = len([n for n in mock_notifications if n['priority'] == 'high'])
        medium_priority = len([n for n in mock_notifications if n['priority'] == 'medium'])
        low_priority = len([n for n in mock_notifications if n['priority'] == 'low'])
        
        # Count by category
        categories = {}
        for notification in mock_notifications:
            category = notification['category']
            categories[category] = categories.get(category, 0) + 1
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'unread': unread,
                'read': total - unread,
                'priority': {
                    'high': high_priority,
                    'medium': medium_priority,
                    'low': low_priority
                },
                'categories': categories
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
