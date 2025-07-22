"""
Biometric Authentication Routes
Handles voice, face, and fingerprint authentication
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
from io import BytesIO

from models import User
from services.biometric_service import BiometricService
from services.ai_auth_service import AIAuthService
from extensions import db

biometric_bp = Blueprint('biometric', __name__)
biometric_service = BiometricService()
ai_auth = AIAuthService()

@biometric_bp.route('/register/face', methods=['POST'])
@jwt_required()
def register_face():
    """Register user's face for biometric authentication"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'Image data required'}), 400
        
        result = biometric_service.register_face(user_id, data['image'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Face registration failed: {str(e)}'}), 500

@biometric_bp.route('/verify/face', methods=['POST'])
def verify_face():
    """Verify user's face for authentication"""
    try:
        data = request.get_json()
        
        if 'image' not in data or 'username' not in data:
            return jsonify({'error': 'Image and username required'}), 400
        
        # Find user
        user = User.query.filter(
            (User.username == data['username']) | 
            (User.email == data['username'])
        ).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        result = biometric_service.verify_face(user.id, data['image'])
        
        if result['success']:
            # Generate JWT token for successful authentication
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'token': token,
                'user': user.to_dict(),
                'confidence': result['confidence']
            }), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'error': f'Face verification failed: {str(e)}'}), 500

@biometric_bp.route('/register/fingerprint', methods=['POST'])
@jwt_required()
def register_fingerprint():
    """Register user's fingerprint"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'fingerprint_data' not in data:
            return jsonify({'error': 'Fingerprint data required'}), 400
        
        result = biometric_service.register_fingerprint(user_id, data['fingerprint_data'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Fingerprint registration failed: {str(e)}'}), 500

@biometric_bp.route('/verify/fingerprint', methods=['POST'])
def verify_fingerprint():
    """Verify user's fingerprint"""
    try:
        data = request.get_json()
        
        if 'fingerprint_data' not in data or 'username' not in data:
            return jsonify({'error': 'Fingerprint data and username required'}), 400
        
        # Find user
        user = User.query.filter(
            (User.username == data['username']) | 
            (User.email == data['username'])
        ).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        result = biometric_service.verify_fingerprint(user.id, data['fingerprint_data'])
        
        if result['success']:
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'token': token,
                'user': user.to_dict(),
                'confidence': result['confidence']
            }), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'error': f'Fingerprint verification failed: {str(e)}'}), 500

@biometric_bp.route('/login/voice', methods=['POST'])
def voice_login():
    """Voice-based login with speech recognition and voice verification"""
    try:
        # Handle file upload
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file required'}), 400
        
        audio_file = request.files['audio']
        device_info = request.form.get('device_info', '{}')
        
        result = ai_auth.process_voice_login(audio_file, device_info)
        
        if result['success']:
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=result['user_id'])
            
            return jsonify({
                'success': True,
                'token': token,
                'user_id': result['user_id'],
                'username': result['username'],
                'requires_2fa': result.get('requires_2fa', False),
                'risk_score': result.get('risk_score', 0)
            }), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'error': f'Voice login failed: {str(e)}'}), 500

@biometric_bp.route('/capture/voice', methods=['POST'])
def capture_voice():
    """Capture voice sample for registration"""
    try:
        data = request.get_json()
        duration = data.get('duration', 3)
        
        # Capture voice using AI auth service
        voice_data = ai_auth.capture_live_voice(duration)
        
        if voice_data:
            # Convert to base64 for transmission
            voice_b64 = base64.b64encode(voice_data).decode()
            return jsonify({
                'success': True,
                'voice_data': voice_b64
            }), 200
        else:
            return jsonify({'error': 'Failed to capture voice'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Voice capture failed: {str(e)}'}), 500

@biometric_bp.route('/status/<int:user_id>', methods=['GET'])
@jwt_required()
def get_biometric_status(user_id):
    """Get user's biometric registration status"""
    try:
        current_user_id = get_jwt_identity()
        
        # Users can only check their own status unless they're admin
        if current_user_id != user_id:
            current_user = User.query.get(current_user_id)
            if not current_user or current_user.role != 'admin':
                return jsonify({'error': 'Unauthorized'}), 403
        
        status = biometric_service.get_biometric_status(user_id)
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get biometric status: {str(e)}'}), 500

@biometric_bp.route('/register/voice', methods=['POST'])
@jwt_required()
def register_voice():
    """Register user's voice biometric"""
    try:
        user_id = get_jwt_identity()
        
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file required'}), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        # Extract voice features
        import numpy as np
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        features = ai_auth._extract_voice_features(audio_array)
        
        # Store voice biometric
        user = User.query.get(user_id)
        if user:
            preferences = user.get_preferences()
            biometric_data = preferences.get('biometric_data', {})
            
            biometric_data['voice_features'] = features.tolist()
            biometric_data['voice_registered_at'] = datetime.utcnow().isoformat()
            
            preferences['biometric_data'] = biometric_data
            user.set_preferences(preferences)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Voice biometric registered successfully'
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Voice registration failed: {str(e)}'}), 500

@biometric_bp.route('/verify/voice', methods=['POST'])
def verify_voice():
    """Verify user's voice biometric"""
    try:
        data = request.get_json()
        
        if 'voice_data' not in data or 'username' not in data:
            return jsonify({'error': 'Voice data and username required'}), 400
        
        # Find user
        user = User.query.filter(
            (User.username == data['username']) | 
            (User.email == data['username'])
        ).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Decode voice data
        voice_bytes = base64.b64decode(data['voice_data'])
        
        result = ai_auth.verify_voice_print(user.id, voice_bytes)
        
        if result:
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'token': token,
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Voice verification failed'
            }), 401
            
    except Exception as e:
        return jsonify({'error': f'Voice verification failed: {str(e)}'}), 500

@biometric_bp.route('/ai/process', methods=['POST'])
@jwt_required()
def process_ai_command():
    """Process AI voice commands"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        command_type = data.get('type', 'text')
        context = data.get('context', 'general')
        
        # Process the command using AI
        response = ai_auth.process_ai_command(query, command_type, context)
        
        return jsonify({
            'success': True,
            'response': response,
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'AI processing failed: {str(e)}'}), 500
