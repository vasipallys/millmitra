"""
Session Management Routes
Handles session-related API endpoints
"""

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from services.session_manager import session_manager
from middleware.session_middleware import require_session, log_user_activity
from models.user import User, UserSession
from extensions import db
import json

session_bp = Blueprint('session', __name__)


@session_bp.route('/active', methods=['GET'])
@jwt_required()
@require_session
def get_active_sessions():
    """Get all active sessions for current user"""
    try:
        user_id = g.current_user.id
        current_session_token = getattr(g, 'session_token', None)
        
        sessions = session_manager.get_active_sessions(user_id)
        
        # Mark current session
        for session in sessions:
            if current_session_token and session.get('session_token') == current_session_token:
                session['is_current'] = True
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching sessions: {str(e)}'
        }), 500


@session_bp.route('/invalidate/<session_id>', methods=['POST'])
@jwt_required()
@require_session
@log_user_activity('session_invalidated')
def invalidate_session(session_id):
    """Invalidate a specific session"""
    try:
        user_id = g.current_user.id
        
        # Get session and verify ownership
        session = UserSession.query.filter_by(
            id=session_id,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'message': 'Session not found or already inactive'
            }), 404
        
        # Invalidate session
        success = session_manager.invalidate_session(session.session_token)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session invalidated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to invalidate session'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error invalidating session: {str(e)}'
        }), 500


@session_bp.route('/invalidate-all', methods=['POST'])
@jwt_required()
@require_session
@log_user_activity('all_sessions_invalidated')
def invalidate_all_sessions():
    """Invalidate all sessions except current one"""
    try:
        user_id = g.current_user.id
        current_session_token = getattr(g, 'session_token', None)
        
        success = session_manager.invalidate_user_sessions(
            user_id, 
            except_token=current_session_token
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'All other sessions invalidated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to invalidate sessions'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error invalidating sessions: {str(e)}'
        }), 500


@session_bp.route('/extend', methods=['POST'])
@jwt_required()
@require_session
def extend_session():
    """Extend current session"""
    try:
        session_token = getattr(g, 'session_token', None)
        
        if not session_token:
            return jsonify({
                'success': False,
                'message': 'No active session found'
            }), 400
        
        # Update session activity (which extends it)
        success = session_manager.update_session_activity(session_token)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session extended successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to extend session'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error extending session: {str(e)}'
        }), 500


@session_bp.route('/info', methods=['GET'])
@jwt_required()
@require_session
def get_session_info():
    """Get current session information"""
    try:
        session_token = getattr(g, 'session_token', None)
        
        if not session_token:
            return jsonify({
                'success': False,
                'message': 'No active session found'
            }), 400
        
        session_data = session_manager.get_session(session_token)
        
        if session_data:
            # Remove sensitive information
            safe_session_data = {
                'created_at': session_data.get('created_at'),
                'last_activity': session_data.get('last_activity'),
                'ip_address': session_data.get('ip_address'),
                'security_level': session_data.get('security_level', 'normal'),
                'login_method': session_data.get('login_method', 'standard')
            }
            
            return jsonify({
                'success': True,
                'session': safe_session_data
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting session info: {str(e)}'
        }), 500


@session_bp.route('/security/update', methods=['POST'])
@jwt_required()
@require_session
@log_user_activity('session_security_updated')
def update_session_security():
    """Update session security level"""
    try:
        data = request.get_json()
        security_level = data.get('security_level', 'normal')
        
        if security_level not in ['low', 'normal', 'high', 'critical']:
            return jsonify({
                'success': False,
                'message': 'Invalid security level'
            }), 400
        
        session_token = getattr(g, 'session_token', None)
        
        if not session_token:
            return jsonify({
                'success': False,
                'message': 'No active session found'
            }), 400
        
        session_data = session_manager.get_session(session_token)
        
        if session_data:
            session_data['security_level'] = security_level
            
            # Update in Redis
            redis_key = f"{session_manager.session_prefix}{session_token}"
            session_manager.redis_client.setex(
                redis_key,
                int(session_manager.session_timeout.total_seconds()),
                json.dumps(session_data)
            )
            
            return jsonify({
                'success': True,
                'message': 'Session security level updated'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Session not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating session security: {str(e)}'
        }), 500


@session_bp.route('/cleanup', methods=['POST'])
@jwt_required()
@require_session
@log_user_activity('session_cleanup')
def cleanup_expired_sessions():
    """Clean up expired sessions (admin only)"""
    try:
        if g.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        cleaned_count = session_manager.cleanup_expired_sessions()
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleaned_count} expired sessions'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error cleaning up sessions: {str(e)}'
        }), 500


@session_bp.route('/stats', methods=['GET'])
@jwt_required()
@require_session
def get_session_stats():
    """Get session statistics (admin only)"""
    try:
        if g.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        # Get session statistics
        total_sessions = UserSession.query.filter_by(is_active=True).count()
        expired_sessions = UserSession.query.filter(
            UserSession.expires_at < db.func.now()
        ).count()
        
        # Get active sessions by user
        active_by_user = db.session.query(
            UserSession.user_id,
            db.func.count(UserSession.id).label('session_count')
        ).filter_by(is_active=True).group_by(UserSession.user_id).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_active_sessions': total_sessions,
                'expired_sessions': expired_sessions,
                'active_users': len(active_by_user),
                'sessions_by_user': [
                    {'user_id': user_id, 'session_count': count}
                    for user_id, count in active_by_user
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting session stats: {str(e)}'
        }), 500
