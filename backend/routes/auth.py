from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models import User, AuthLog
from services.ai_auth_service import AIAuthService
from extensions import db
import re
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
ai_auth = AIAuthService()

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

        print(f"🔍 Login attempt: {username}")

        # AI-powered input validation and correction
        username = ai_auth.normalize_username(username)
        print(f"🔄 Normalized username: {username}")

        # Find user by username, email, or phone
        user = User.query.filter(
            (User.username == username) |
            (User.email == username) |
            (User.phone == username)
        ).first()

        print(f"👤 User found: {user.username if user else 'None'}")

        if not user or not user.is_active:
            print(f"❌ User not found or inactive")
            try:
                ai_auth.log_failed_attempt(username, 'user_not_found', device_info)
            except Exception as e:
                print(f"⚠️ Error logging failed attempt: {e}")
            return jsonify({'error': 'Invalid credentials'}), 401

        # AI risk assessment
        try:
            risk_score = ai_auth.assess_login_risk(user, device_info)
            print(f"🎯 Risk score: {risk_score}")
        except Exception as e:
            print(f"⚠️ Error assessing risk: {e}")
            risk_score = 0.0

        # Authenticate based on method
        if login_method == 'password':
            password_valid = user.check_password(password)
            print(f"🔑 Password valid: {password_valid}")
            if not password_valid:
                print(f"❌ Wrong password")
                try:
                    ai_auth.log_failed_attempt(username, 'wrong_password', device_info)
                except Exception as e:
                    print(f"⚠️ Error logging failed attempt: {e}")
                return jsonify({'error': 'Invalid credentials'}), 401
        elif login_method == 'voice':
            voice_data = data.get('voice_data')
            if not ai_auth.verify_voice_print(user.id, voice_data):
                return jsonify({'error': 'Voice authentication failed'}), 401
        elif login_method == 'biometric':
            biometric_data = data.get('biometric_data')
            if not ai_auth.verify_biometric(user.id, biometric_data):
                return jsonify({'error': 'Biometric authentication failed'}), 401

        # Check if 2FA is required based on risk score
        requires_2fa = risk_score > 0.7 or getattr(user, 'force_2fa', False)

        if requires_2fa and not data.get('otp_verified'):
            # Send OTP and require verification
            otp_method = ai_auth.select_optimal_2fa_method(user, device_info)
            ai_auth.send_otp(user, otp_method)
            return jsonify({
                'requires_2fa': True,
                'method': otp_method,
                'message': f'OTP sent via {otp_method}'
            }), 200

        # Create access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=8)
        )

        # Update user login info
        user.last_login = datetime.utcnow()
        user.login_count = getattr(user, 'login_count', 0) + 1

        # Log successful login
        try:
            ai_auth.log_successful_login(user, device_info, risk_score)
        except Exception as e:
            print(f"⚠️ Error logging successful login: {e}")

        db.session.commit()

        print(f"✅ Login successful for {username}")

        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'preferences': user.get_preferences() if hasattr(user, 'get_preferences') else {}
            },
            'risk_score': risk_score
        })

    except Exception as e:
        print(f"💥 Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Login failed due to server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'preferences': user.get_preferences() if hasattr(user, 'get_preferences') else {}
            }
        })

    except Exception as e:
        print(f"💥 Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    username = data.get('username')
    otp = data.get('otp')
    
    if ai_auth.verify_otp(username, otp):
        return jsonify({'verified': True})
    
    return jsonify({'error': 'Invalid OTP'}), 401

@auth_bp.route('/voice-login', methods=['POST'])
def voice_login():
    audio_data = request.files.get('audio')
    device_info = request.form.get('device_info', '{}')
    
    # Process voice for both speech-to-text and voice print
    result = ai_auth.process_voice_login(audio_data, device_info)
    
    if result['success']:
        return jsonify(result)
    
    return jsonify({'error': result['error']}), 401