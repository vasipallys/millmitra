import re
import hashlib
import numpy as np
from datetime import datetime, timedelta
from models import User, AuthLog
from extensions import db
import requests
import json
from typing import Dict, Any
# Temporarily disabled until dependencies are installed
# import speech_recognition as sr
from io import BytesIO

class AIAuthService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
        # self.recognizer = sr.Recognizer()  # Temporarily disabled
    
    def normalize_username(self, username: str) -> str:
        """AI-powered username normalization and typo correction"""
        username = username.strip().lower()
        
        # Check if it's a phone number
        if re.match(r'^\d{10}$', username):
            return username
        
        # Check if it's an email
        if '@' in username:
            return username
        
        # For regular usernames, check for common typos
        return self._correct_username_typos(username)
    
    def _correct_username_typos(self, username: str) -> str:
        """Use AI to suggest username corrections"""
        try:
            response = requests.post(f"{self.ai_service_url}/correct-username", 
                                   json={"username": username})
            if response.status_code == 200:
                return response.json().get('corrected', username)
        except:
            pass
        return username
    
    def assess_login_risk(self, user: User, device_info: Dict) -> float:
        """AI-powered risk assessment for login attempts"""
        risk_factors = []
        
        # Time-based risk
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Outside normal hours
            risk_factors.append(0.3)
        
        # Location-based risk
        ip_address = device_info.get('ip_address')
        if self._is_suspicious_location(user.id, ip_address):
            risk_factors.append(0.4)
        
        # Device-based risk
        device_fingerprint = device_info.get('fingerprint')
        if not self._is_known_device(user.id, device_fingerprint):
            risk_factors.append(0.3)
        
        # Behavioral risk
        user_agent = device_info.get('user_agent')
        if self._is_suspicious_user_agent(user_agent):
            risk_factors.append(0.2)
        
        # Recent failed attempts
        recent_failures = AuthLog.query.filter(
            AuthLog.username_attempted == user.username,
            AuthLog.success == False,
            AuthLog.timestamp > datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        if recent_failures > 3:
            risk_factors.append(0.5)
        
        # Calculate overall risk score
        base_risk = min(sum(risk_factors), 1.0)
        
        # Use AI model for advanced risk assessment
        try:
            ai_risk = self._get_ai_risk_score(user, device_info)
            return max(base_risk, ai_risk)
        except:
            return base_risk
    
    def _get_ai_risk_score(self, user: User, device_info: Dict) -> float:
        """Get AI-computed risk score"""
        payload = {
            "user_id": user.id,
            "login_history": self._get_user_login_patterns(user.id),
            "device_info": device_info,
            "current_time": datetime.now().isoformat()
        }
        
        response = requests.post(f"{self.ai_service_url}/assess-login-risk", 
                               json=payload)
        if response.status_code == 200:
            return response.json().get('risk_score', 0.5)
        return 0.5
    
    def verify_voice_print(self, user_id: int, voice_data: bytes) -> bool:
        """Verify user's voice print using AI - TEMPORARILY DISABLED"""
        # TODO: Re-enable after speech_recognition is installed
        return False
    
    def verify_biometric(self, user_id: int, biometric_data: Dict) -> bool:
        """Verify biometric data (face recognition)"""
        try:
            payload = {
                "user_id": user_id,
                "biometric_data": biometric_data
            }
            
            response = requests.post(f"{self.ai_service_url}/verify-biometric", 
                                   json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('verified', False) and result.get('confidence', 0) > 0.85
        except Exception as e:
            print(f"Biometric verification error: {e}")
        
        return False
    
    def process_voice_login(self, audio_file, device_info: str) -> Dict:
        """Process voice login with speech-to-text and voice verification - TEMPORARILY DISABLED"""
        # TODO: Re-enable after speech_recognition is installed
        return {'success': False, 'error': 'Voice login temporarily disabled'}
    
    def _speech_to_text(self, audio_data: bytes) -> Dict:
        """Convert speech to text - TEMPORARILY DISABLED"""
        return {'success': False, 'error': 'Speech recognition temporarily disabled'}
    
    def _extract_username_from_speech(self, text: str) -> str:
        """Extract username from spoken text using NLP"""
        # Common patterns: "login as john", "I am john", "john here"
        patterns = [
            r'login as (\w+)',
            r'i am (\w+)',
            r'(\w+) here',
            r'this is (\w+)',
            r'my name is (\w+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1)
        
        # If no pattern matches, try to extract the most likely username
        words = text.split()
        for word in words:
            if len(word) > 2 and word.isalpha():
                # Check if this word exists as a username
                user = User.query.filter(User.username == word.lower()).first()
                if user:
                    return word.lower()
        
        return None
    
    def select_optimal_2fa_method(self, user: User, device_info: Dict) -> str:
        """AI selects the best 2FA method based on context"""
        available_methods = []
        
        if user.phone:
            available_methods.append('sms')
        if user.email:
            available_methods.append('email')
        
        # Consider device capabilities
        if device_info.get('has_camera'):
            available_methods.append('qr')
        if device_info.get('has_microphone'):
            available_methods.append('voice')
        
        # AI decision based on user preferences and context
        preferences = user.get_preferences()
        preferred_method = preferences.get('preferred_2fa', 'sms')
        
        if preferred_method in available_methods:
            return preferred_method
        
        return available_methods[0] if available_methods else 'email'
    
    def send_otp(self, user: User, method: str) -> bool:
        """Send OTP via specified method"""
        otp_code = self._generate_otp()
        
        # Store OTP in database
        otp_record = OTP(
            user_id=user.id,
            code=otp_code,
            method=method,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        db.session.add(otp_record)
        db.session.commit()
        
        # Send OTP
        if method == 'sms':
            return self._send_sms_otp(user.phone, otp_code)
        elif method == 'email':
            return self._send_email_otp(user.email, otp_code)
        elif method == 'voice':
            return self._send_voice_otp(user.phone, otp_code)
        
        return False
    
    def verify_otp(self, username: str, otp_code: str) -> bool:
        """Verify OTP code"""
        user = User.query.filter(
            (User.username == username) | 
            (User.email == username) | 
            (User.phone == username)
        ).first()
        
        if not user:
            return False
        
        otp_record = OTP.query.filter(
            OTP.user_id == user.id,
            OTP.code == otp_code,
            OTP.used == False,
            OTP.expires_at > datetime.utcnow()
        ).first()
        
        if otp_record:
            otp_record.used = True
            db.session.commit()
            return True
        
        return False
    
    def log_successful_login(self, user: User, device_info: Dict, risk_score: float):
        """Log successful login for AI learning"""
        log = AuthLog(
            user_id=user.id,
            username_attempted=user.username,
            success=True,
            method='password',  # Will be updated based on actual method
            risk_score=risk_score,
            ip_address=device_info.get('ip_address'),
            user_agent=device_info.get('user_agent'),
            device_fingerprint=device_info.get('fingerprint'),
            location=device_info.get('location')
        )
        db.session.add(log)
    
    def log_failed_attempt(self, username: str, reason: str, device_info: Dict):
        """Log failed login attempt"""
        log = AuthLog(
            username_attempted=username,
            success=False,
            failure_reason=reason,
            ip_address=device_info.get('ip_address'),
            user_agent=device_info.get('user_agent'),
            device_fingerprint=device_info.get('fingerprint')
        )
        db.session.add(log)
        db.session.commit()
    
    # Helper methods
    def _generate_otp(self) -> str:
        import random
        return str(random.randint(100000, 999999))
    
    def _is_suspicious_location(self, user_id: int, ip_address: str) -> bool:
        # Check if IP is from a different country/region than usual
        return False  # Implement geolocation logic
    
    def _is_known_device(self, user_id: int, fingerprint: str) -> bool:
        # Check if device fingerprint is known
        return AuthLog.query.filter(
            AuthLog.user_id == user_id,
            AuthLog.device_fingerprint == fingerprint,
            AuthLog.success == True
        ).first() is not None
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        # Check for suspicious user agents
        suspicious_patterns = ['bot', 'crawler', 'spider']
        return any(pattern in user_agent.lower() for pattern in suspicious_patterns)
    
    def _get_user_login_patterns(self, user_id: int) -> Dict:
        # Get user's historical login patterns for AI analysis
        logs = AuthLog.query.filter(
            AuthLog.user_id == user_id,
            AuthLog.success == True
        ).order_by(AuthLog.timestamp.desc()).limit(50).all()
        
        return {
            'login_times': [log.timestamp.hour for log in logs],
            'devices': [log.device_fingerprint for log in logs if log.device_fingerprint],
            'locations': [log.location for log in logs if log.location]
        }
    
    def _send_sms_otp(self, phone: str, otp: str) -> bool:
        # Implement SMS sending logic
        return True
    
    def _send_email_otp(self, email: str, otp: str) -> bool:
        # Implement email sending logic
        return True
    
    def _send_voice_otp(self, phone: str, otp: str) -> bool:
        # Implement voice call OTP
        return True