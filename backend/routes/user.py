"""
User Profile API Routes
Handles user profile and authentication related endpoints
"""

from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required
from datetime import datetime
from utils import current_user
from extensions import db
import uuid

user_bp = Blueprint('user', __name__)

# Mock user data for development
mock_user_data = {
    'id': 1,
    'username': 'admin',
    'email': 'admin@smartricemill.com',
    'first_name': 'Admin',
    'last_name': 'User',
    'phone': '+91 9876543210',
    'department': 'Management',
    'role': 'Administrator',
    'last_login': datetime.now().isoformat(),
    'created_at': '2024-01-01T00:00:00',
    'preferences': {
        'theme': 'light',
        'language': 'en',
        'timezone': 'Asia/Kolkata',
        'notifications': {
            'email': True,
            'push': True,
            'sms': False
        }
    },
    'permissions': [
        'farmer_management',
        'production_management',
        'inventory_management',
        'quality_control',
        'financial_management',
        'system_administration'
    ]
}

@user_bp.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get current user profile"""
    try:
        # In a real application, you would get the user ID from the session/token
        # For now, return mock data
        return jsonify({
            'success': True,
            'user': mock_user_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/profile', methods=['PUT'])
def update_user_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Update mock user data
        if 'first_name' in data:
            mock_user_data['first_name'] = data['first_name']
        if 'last_name' in data:
            mock_user_data['last_name'] = data['last_name']
        if 'email' in data:
            mock_user_data['email'] = data['email']
        if 'phone' in data:
            mock_user_data['phone'] = data['phone']
        if 'department' in data:
            mock_user_data['department'] = data['department']
        
        return jsonify({
            'success': True,
            'user': mock_user_data,
            'message': 'Profile updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Current password and new password are required'
            }), 400
        
        # In a real application, you would verify the current password
        # and hash the new password before storing
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/preferences', methods=['PUT'])
def update_user_preferences():
    """Update user preferences"""
    try:
        data = request.get_json()
        
        # Update preferences
        if 'preferences' in data:
            mock_user_data['preferences'].update(data['preferences'])
        
        return jsonify({
            'success': True,
            'preferences': mock_user_data['preferences'],
            'message': 'Preferences updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/mill-settings', methods=['GET'])
@jwt_required()
def get_mill_settings():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    prefs = user.get_preferences() or {}
    settings = prefs.get('mill_settings') or {}
    return jsonify({'success': True, 'settings': settings})

@user_bp.route('/api/user/mill-settings', methods=['PUT'])
@jwt_required()
def save_mill_settings():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    data = request.get_json() or {}
    settings = data.get('settings') or data
    prefs = user.get_preferences() or {}
    prefs['mill_settings'] = settings
    user.set_preferences(prefs)
    db.session.commit()
    return jsonify({
        'success': True,
        'settings': settings,
        'message': 'Settings saved'
    })

@user_bp.route('/api/user/activity', methods=['GET'])
def get_user_activity():
    """Get user activity log"""
    try:
        # Mock activity data
        activities = [
            {
                'id': 1,
                'action': 'login',
                'description': 'User logged in',
                'timestamp': (datetime.now()).isoformat(),
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0...'
            },
            {
                'id': 2,
                'action': 'profile_update',
                'description': 'Profile information updated',
                'timestamp': (datetime.now()).isoformat(),
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0...'
            },
            {
                'id': 3,
                'action': 'farmer_created',
                'description': 'New farmer record created',
                'timestamp': (datetime.now()).isoformat(),
                'ip_address': '192.168.1.100',
                'user_agent': 'Mozilla/5.0...'
            }
        ]
        
        return jsonify({
            'success': True,
            'activities': activities,
            'total': len(activities)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/sessions', methods=['GET'])
def get_user_sessions():
    """Get active user sessions"""
    try:
        # Mock session data
        sessions = [
            {
                'id': 1,
                'device': 'Windows PC',
                'browser': 'Chrome 120.0',
                'ip_address': '192.168.1.100',
                'location': 'Hyderabad, India',
                'last_active': datetime.now().isoformat(),
                'current': True
            },
            {
                'id': 2,
                'device': 'Mobile Device',
                'browser': 'Chrome Mobile',
                'ip_address': '192.168.1.101',
                'location': 'Hyderabad, India',
                'last_active': (datetime.now()).isoformat(),
                'current': False
            }
        ]
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/enable-2fa', methods=['POST'])
def enable_two_factor():
    """Enable two-factor authentication"""
    try:
        # In a real application, you would generate QR code and secret
        return jsonify({
            'success': True,
            'message': 'Two-factor authentication enabled',
            'qr_code': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            'secret': 'JBSWY3DPEHPK3PXP'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/disable-2fa', methods=['POST'])
def disable_two_factor():
    """Disable two-factor authentication"""
    try:
        return jsonify({
            'success': True,
            'message': 'Two-factor authentication disabled'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/logout', methods=['POST'])
def logout_user():
    """Logout user"""
    try:
        # Clear session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/api/user/delete-session/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a specific user session"""
    try:
        return jsonify({
            'success': True,
            'message': f'Session {session_id} deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
