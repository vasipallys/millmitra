"""
User Profile API Routes
Handles user profile and authentication related endpoints
"""

from flask import Blueprint, request, jsonify, send_file, session
from flask_jwt_extended import jwt_required
from utils import current_user
from models.user import AuthLog, UserSession
from extensions import db
from services.mill_settings_service import (
    backup_status,
    can_manage_mill,
    cleanup_old_backups,
    create_backup_file,
    get_mill_config,
    mail_configured,
    save_mill_config,
    sqlite_file_path,
)
import json
import tempfile
from pathlib import Path

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

def _merged_settings(user):
    mill = get_mill_config()
    prefs = user.get_preferences() or {}
    legacy = prefs.get('mill_settings') if isinstance(prefs.get('mill_settings'), dict) else {}
    user_notes = user.get_notification_settings()
    notifications = dict(mill.get('notifications') or {})
    notifications.update(user_notes or {})
    if 'inApp' not in notifications and 'pushNotifications' in notifications:
        notifications['inApp'] = bool(notifications.get('pushNotifications'))
    business = dict(mill.get('business') or {})
    legacy_business = (legacy.get('business') or {}) if isinstance(legacy, dict) else {}
    if not any(business.values()) and legacy_business:
        business = {**business, **legacy_business}
    security = dict(mill.get('security') or {})
    user_security = prefs.get('security') if isinstance(prefs.get('security'), dict) else {}
    if user_security.get('sessionTimeout'):
        security['sessionTimeout'] = user_security.get('sessionTimeout')
    return {
        'business': business,
        'notifications': notifications,
        'ai': mill.get('ai') or {},
        'security': security,
        'backup': mill.get('backup') or {},
    }


def _settings_meta(user):
    return {
        'mail_configured': mail_configured(),
        'can_edit_business': can_manage_mill(user),
        'can_manage_backup': can_manage_mill(user),
        'notification_scope': 'per_user',
        'backup': backup_status(),
    }


@user_bp.route('/api/user/mill-settings', methods=['GET'])
@jwt_required()
def get_mill_settings():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    return jsonify({
        'success': True,
        'settings': _merged_settings(user),
        **_settings_meta(user),
    })

@user_bp.route('/api/user/mill-settings', methods=['PUT'])
@jwt_required()
def save_mill_settings():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    data = request.get_json() or {}
    incoming = data.get('settings') if isinstance(data.get('settings'), dict) else data
    if not isinstance(incoming, dict):
        incoming = {}
    tab = (data.get('tab') or incoming.get('tab') or '').strip().lower()
    manager = can_manage_mill(user)

    if tab == 'business' and not manager:
        return jsonify({
            'success': False,
            'error': 'Only admin or manager can change mill business info',
            'message': 'Only admin or manager can change mill business info',
        }), 403
    if tab == 'backup' and not manager:
        return jsonify({
            'success': False,
            'error': 'Only admin or manager can change backup settings',
            'message': 'Only admin or manager can change backup settings',
        }), 403

    if isinstance(incoming.get('notifications'), dict):
        notes = user.get_notification_settings()
        notes.update(incoming['notifications'])
        if 'inApp' in incoming['notifications']:
            notes['pushNotifications'] = bool(incoming['notifications']['inApp'])
        user.set_notification_settings(notes)
        prefs = user.get_preferences() or {}
        prefs['notifications'] = notes
        user.set_preferences(prefs)
        if manager:
            save_mill_config({'notifications': notes})

    mill_updates = {}
    if manager and isinstance(incoming.get('business'), dict):
        mill_updates['business'] = incoming['business']
    if isinstance(incoming.get('ai'), dict):
        mill_updates['ai'] = incoming['ai']
    if manager and isinstance(incoming.get('backup'), dict):
        mill_updates['backup'] = incoming['backup']
    if isinstance(incoming.get('security'), dict):
        timeout = incoming['security'].get('sessionTimeout')
        prefs = user.get_preferences() or {}
        prefs['security'] = {**(prefs.get('security') or {}), 'sessionTimeout': timeout}
        user.set_preferences(prefs)
        if manager:
            mill_updates['security'] = {'sessionTimeout': timeout}
    if mill_updates:
        save_mill_config(mill_updates)
    db.session.commit()
    return jsonify({
        'success': True,
        'settings': _merged_settings(user),
        'message': 'Settings saved',
        **_settings_meta(user),
    })


def _send_db_copy(path):
    return send_file(
        str(path),
        as_attachment=True,
        download_name=path.name,
        mimetype='application/octet-stream',
    )


@user_bp.route('/api/user/backup/status', methods=['GET'])
@jwt_required()
def get_backup_status():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    return jsonify({'success': True, **_settings_meta(user)})


@user_bp.route('/api/user/backup', methods=['POST'])
@jwt_required()
def create_mill_backup():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    if not can_manage_mill(user):
        return jsonify({
            'success': False,
            'error': 'Only admin or manager can back up the mill database onto the server',
            'message': 'Only admin or manager can back up the mill database onto the server',
        }), 403
    dest, error = create_backup_file()
    if error:
        return jsonify({'success': False, 'error': error, 'message': error}), 404
    return _send_db_copy(dest)


@user_bp.route('/api/user/backup/download', methods=['GET'])
@jwt_required()
def download_mill_copy():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    src = sqlite_file_path()
    if not src.exists():
        return jsonify({
            'success': False,
            'error': 'SQLite database file was not found',
            'message': 'SQLite database file was not found',
        }), 404
    stamp = Path(tempfile.gettempdir()) / f'rice_mill_erp_copy_{user.id}.db'
    from services.mill_settings_service import _copy_sqlite
    _copy_sqlite(src, stamp)
    return send_file(
        str(stamp),
        as_attachment=True,
        download_name=f'rice_mill_erp_copy.db',
        mimetype='application/octet-stream',
    )


@user_bp.route('/api/user/backup/cleanup', methods=['POST'])
@jwt_required()
def run_backup_cleanup():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 401
    if not can_manage_mill(user):
        return jsonify({
            'success': False,
            'error': 'Only admin or manager can delete old backup files',
            'message': 'Only admin or manager can delete old backup files',
        }), 403
    data = request.get_json(silent=True) or {}
    result = cleanup_old_backups(days=data.get('retentionDays'))
    return jsonify({'success': True, **result, 'backup': backup_status()})

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
