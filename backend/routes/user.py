"""
User Profile API Routes
Handles user profile and authentication related endpoints
"""

from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required
from utils import current_user
from models.user import AuthLog, UserSession
from extensions import db
import json

user_bp = Blueprint('user', __name__)


def _require_user():
    user = current_user()
    if not user:
        return None
    return user


def _profile_payload(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'department': user.department,
        'role': user.role,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'preferences': user.get_preferences() or {},
    }


@user_bp.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user profile"""
    user = _require_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    return jsonify({'success': True, 'user': _profile_payload(user)})


@user_bp.route('/api/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    """Update user profile"""
    user = _require_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    data = request.get_json() or {}
    for field in ('first_name', 'last_name', 'phone', 'department'):
        if field in data:
            setattr(user, field, data[field])
    if 'email' in data and data['email']:
        user.email = data['email']
    db.session.commit()
    return jsonify({
        'success': True,
        'user': _profile_payload(user),
        'message': 'Profile updated successfully'
    })


@user_bp.route('/api/user/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    user = _require_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    data = request.get_json() or {}
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    if not current_password or not new_password:
        return jsonify({
            'success': False,
            'error': 'Current password and new password are required'
        }), 400
    if len(str(new_password)) < 6:
        return jsonify({'success': False, 'error': 'New password must be at least 6 characters'}), 400
    if not user.check_password(current_password):
        return jsonify({'success': False, 'error': 'Current password is incorrect'}), 400
    user.set_password(new_password)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Password changed successfully'})


@user_bp.route('/api/user/preferences', methods=['PUT'])
@jwt_required()
def update_user_preferences():
    """Update user preferences"""
    user = _require_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    data = request.get_json() or {}
    incoming = data.get('preferences') if isinstance(data.get('preferences'), dict) else data
    prefs = user.get_preferences() or {}
    if isinstance(incoming, dict):
        prefs.update(incoming)
        user.set_preferences(prefs)
        db.session.commit()
    return jsonify({
        'success': True,
        'preferences': user.get_preferences(),
        'message': 'Preferences updated successfully'
    })

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
@jwt_required()
def get_user_activity():
    """Get user activity log"""
    user = _require_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    logs = AuthLog.query.filter_by(user_id=user.id).order_by(AuthLog.timestamp.desc()).limit(50).all()
    activities = [
        {
            'id': log.id,
            'action': log.action,
            'description': log.failure_reason or log.action,
            'timestamp': log.timestamp.isoformat() if log.timestamp else None,
            'ip_address': log.ip_address,
            'user_agent': log.user_agent,
        }
        for log in logs
    ]
    return jsonify({
        'success': True,
        'activities': activities,
        'total': len(activities)
    })

@user_bp.route('/api/user/sessions', methods=['GET'])
@jwt_required()
def get_user_sessions():
    """Get active user sessions"""
    user = _require_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    rows = UserSession.query.filter_by(user_id=user.id, is_active=True).order_by(
        UserSession.last_activity.desc()
    ).all()
    sessions = []
    for row in rows:
        info = {}
        try:
            info = json.loads(row.device_info) if row.device_info else {}
        except Exception:
            info = {}
        sessions.append({
            'id': row.id,
            'device': info.get('platform') or info.get('user_agent') or 'Unknown device',
            'browser': info.get('user_agent'),
            'ip_address': row.ip_address,
            'last_active': row.last_activity.isoformat() if row.last_activity else None,
            'expires_at': row.expires_at.isoformat() if row.expires_at else None,
            'current': False
        })
    return jsonify({
        'success': True,
        'sessions': sessions,
        'total': len(sessions)
    })

@user_bp.route('/api/user/enable-2fa', methods=['POST'])
@jwt_required()
def enable_two_factor():
    """Enable two-factor authentication"""
    if not _require_user():
        return jsonify({'success': False, 'error': 'User not found'}), 401
    return jsonify({
        'success': False,
        'error': 'Two-factor setup is not available in this deployment'
    }), 501

@user_bp.route('/api/user/disable-2fa', methods=['POST'])
@jwt_required()
def disable_two_factor():
    """Disable two-factor authentication"""
    if not _require_user():
        return jsonify({'success': False, 'error': 'User not found'}), 401
    return jsonify({
        'success': False,
        'error': 'Two-factor setup is not available in this deployment'
    }), 501

@user_bp.route('/api/user/logout', methods=['POST'])
@jwt_required()
def logout_user():
    """Logout user"""
    try:
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
@jwt_required()
def delete_session(session_id):
    """Delete a specific user session"""
    user = _require_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    row = UserSession.query.filter_by(id=session_id, user_id=user.id).first()
    if not row:
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    row.is_active = False
    db.session.commit()
    return jsonify({
        'success': True,
        'message': f'Session {session_id} deleted successfully'
    })
