from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from models.user import User
from models.auth_log import AuthLog
from services.ai_auth_service import AIAuthService
from extensions import db
import re
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
ai_auth = AIAuthService()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    login_method = data.get('method', 'password')  # password, voice, biometric
    device_info = data.get('device_info', {})
    
    # AI-powered input validation and correction
    username = ai_auth.normalize_username(username)
    
    # Find user by username, email, or phone
    user = User.query.filter(
        (User.username == username) | 
        (User.email == username) | 
        (User.phone == username)
    ).first()
    
    if not user or not user.is_active:
        ai_auth.log_failed_attempt(username, 'user_not_found', device_info)
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # AI risk assessment
    risk_score = ai_auth.assess_login_risk(user, device_info)
    
    # Authenticate based on method
    if login_method == 'password':
        if not user.check_password(password):
            ai_auth.log_failed_attempt(username, 'wrong_password', device_info)
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
    requires_2fa = risk_score > 0.7 or user.force_2fa
    
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
    user.login_count = (user.login_count or 0) + 1
    
    # Log successful login
    ai_auth.log_successful_login(user, device_info, risk_score)
    
    db.session.commit()
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'preferences': user.preferences
        },
        'risk_score': risk_score
    })

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