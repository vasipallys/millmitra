from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash
from models import User, AuthLog
from services.ai_auth_service import AIAuthService
from extensions import db
from utils import current_user_id
from services.access_control import permissions_for
import re
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
ai_auth = AIAuthService()


def _tenant_for_login(user):
    from models.tenant import Tenant
    from services.tenant_context import memberships_for
    from services.tenant_migration import ensure_default_tenant, ensure_user_memberships

    rows = memberships_for(user.id)
    if not rows:
        tenant = ensure_default_tenant()
        ensure_user_memberships(tenant)
        rows = memberships_for(user.id)
    if not rows:
        raise RuntimeError('No mill membership after default-tenant heal')
    membership = rows[0]
    tenant = Tenant.query.get(membership.tenant_id)
    if tenant is None:
        raise RuntimeError('Membership tenant is missing')
    return tenant, membership


def _issue_login_response(user, device_info, risk_score=0.0):
    tenant, membership = _tenant_for_login(user)
    if tenant is not None:
        from flask import g
        g.tenant_id = tenant.id
        g.tenant = tenant
        g.membership = membership
        g.tenant_role = membership.role if membership else user.role
    claims = {'tenant_id': tenant.id} if tenant else {}
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=claims,
        expires_delta=timedelta(hours=8)
    )
    session_token = None
    try:
        from services.session_manager import session_manager
        session_token = session_manager.create_session(
            user_id=user.id,
            device_info=device_info,
            ip_address=request.remote_addr
        )
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass

    user.last_login = datetime.utcnow()
    try:
        ai_auth.log_successful_login(user, device_info, risk_score)
    except Exception:
        pass
    db.session.commit()

    return jsonify({
        'access_token': access_token,
        'session_token': session_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': (membership.role if membership else user.role),
            'permissions': permissions_for(user),
            'tenant': tenant.to_public() if tenant else None,
            'is_platform_admin': bool(getattr(user, 'is_platform_admin', False)),
            'preferences': user.get_preferences() if hasattr(user, 'get_preferences') else {}
        },
        'risk_score': risk_score
    })

@auth_bp.route('/suggest-username', methods=['POST'])
def suggest_username():
    """AI-powered username suggestions"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()

        if not name:
            return jsonify({'error': 'Name is required'}), 400

        # Generate username suggestions
        suggestions = ai_auth.generate_username_suggestions(name)

        return jsonify({
            'success': True,
            'suggestions': suggestions
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        login_method = data.get('method', 'password')  # password, voice, biometric
        device_info = data.get('device_info', {})

        username = ai_auth.normalize_username(username)

        user = User.query.filter(
            (User.username == username) |
            (User.email == username) |
            (User.phone == username)
        ).first()

        if not user or not user.is_active:
            try:
                ai_auth.log_failed_attempt(username, 'user_not_found', device_info)
            except Exception:
                pass
            return jsonify({
                'success': False,
                'error': 'Username or password is not recognized',
                'message': 'Username or password is not recognized',
            }), 401

        try:
            risk_score = ai_auth.assess_login_risk(user, device_info)
        except Exception:
            risk_score = 0.0

        if login_method == 'password':
            if not user.check_password(password):
                try:
                    ai_auth.log_failed_attempt(username, 'wrong_password', device_info)
                except Exception:
                    pass
                return jsonify({
                'success': False,
                'error': 'Username or password is not recognized',
                'message': 'Username or password is not recognized',
            }), 401
        elif login_method == 'voice':
            return jsonify({'error': 'Voice login is experimental. Use the Password tab.'}), 501
        elif login_method == 'biometric':
            return jsonify({'error': 'Biometric login is experimental. Use the Password tab.'}), 501

        requires_2fa = risk_score > 0.7 or getattr(user, 'force_2fa', False)

        if requires_2fa and not data.get('otp_verified'):
            otp_method = ai_auth.select_optimal_2fa_method(user, device_info)
            sent = False
            try:
                sent = bool(ai_auth.send_otp(user, otp_method))
            except Exception:
                sent = False
            if sent:
                return jsonify({
                    'requires_2fa': True,
                    'method': otp_method,
                    'message': f'OTP sent via {otp_method}'
                }), 200

        return _issue_login_response(user, device_info, risk_score)

    except Exception:
        current_app.logger.exception('login_failed path=/api/auth/login')
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': 'Login failed due to server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        from utils import current_user as load_user
        user = load_user()

        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404

        from services.tenant_context import current_membership, current_tenant
        tenant = current_tenant()
        membership = current_membership()
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': (membership.role if membership else user.role),
                'permissions': permissions_for(user),
                'tenant': tenant.to_public() if tenant else None,
                'is_platform_admin': bool(getattr(user, 'is_platform_admin', False)),
                'preferences': user.get_preferences() if hasattr(user, 'get_preferences') else {}
            }
        })

    except Exception:
        return jsonify({'error': 'Failed to get user information'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    username = data.get('username')
    otp = data.get('otp')
    device_info = data.get('device_info', {})

    if not username or not otp:
        return jsonify({'error': 'Username and OTP are required'}), 400

    if not ai_auth.verify_otp(username, otp):
        return jsonify({'error': 'Invalid OTP'}), 401

    user = User.query.filter(
        (User.username == username) |
        (User.email == username) |
        (User.phone == username)
    ).first()
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 404
    return _issue_login_response(user, device_info, 0.0)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and invalidate session"""
    try:
        from services.session_manager import session_manager

        # Get session token from headers
        session_token = request.headers.get('X-Session-Token')

        if session_token:
            session_manager.invalidate_session(session_token)
        else:
            session_manager.invalidate_user_sessions(current_user_id())

        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })

    except Exception as e:
        print(f"[ERROR] Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Logout failed'
        }), 500

@auth_bp.route('/voice-login', methods=['POST'])
def voice_login():
    audio_data = request.files.get('audio')
    device_info = request.form.get('device_info', '{}')

    # Process voice for both speech-to-text and voice print
    result = ai_auth.process_voice_login(audio_data, device_info)

    if result['success']:
        return jsonify(result)

    return jsonify({'error': result['error']}), 401