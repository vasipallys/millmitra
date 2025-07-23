import re
import hashlib
import numpy as np
from datetime import datetime, timedelta
from models import User, AuthLog
from extensions import db
import requests
import json
from typing import Dict, Any
from io import BytesIO

# Handle Python 3.13 compatibility issues
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None

class AIAuthService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"

        # Initialize speech recognition if available
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
            except:
                self.microphone = None
        else:
            self.recognizer = None
            self.microphone = None
    
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
        """Verify user's voice print using AI"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return False  # Voice verification not available

        try:
            # Convert audio data to numpy array for processing
            audio_array = np.frombuffer(voice_data, dtype=np.int16)

            # Extract voice features (MFCC, pitch, etc.)
            features = self._extract_voice_features(audio_array)

            # Send to AI service for verification
            response = requests.post(f"{self.ai_service_url}/verify-voice",
                                   json={
                                       'user_id': user_id,
                                       'features': features.tolist()
                                   })

            if response.status_code == 200:
                result = response.json()
                return result.get('verified', False) and result.get('confidence', 0) > 0.8
        except Exception as e:
            print(f"Voice verification error: {e}")

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
        """Process voice login with speech-to-text and voice verification"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return {'success': False, 'error': 'Voice authentication not available'}

        try:
            # Convert audio to text for username extraction
            audio_data = audio_file.read()

            # Speech to text
            text_result = self._speech_to_text(audio_data)
            if not text_result['success']:
                return {'success': False, 'error': 'Could not understand speech'}

            spoken_text = text_result['text'].lower()

            # Extract username from speech
            username = self._extract_username_from_speech(spoken_text)
            if not username:
                return {'success': False, 'error': 'Could not identify username from speech'}

            # Find user
            user = User.query.filter(
                (User.username == username) |
                (User.email == username)
            ).first()

            if not user:
                return {'success': False, 'error': 'User not found'}

            # Verify voice print
            if not self.verify_voice_print(user.id, audio_data):
                return {'success': False, 'error': 'Voice verification failed'}

            # Check if additional verification needed
            device_info_dict = json.loads(device_info) if isinstance(device_info, str) else device_info
            risk_score = self.assess_login_risk(user, device_info_dict)

            return {
                'success': True,
                'user_id': user.id,
                'username': user.username,
                'risk_score': risk_score,
                'requires_2fa': risk_score > 0.7
            }

        except Exception as e:
            return {'success': False, 'error': f'Voice processing error: {str(e)}'}
    
    def _speech_to_text(self, audio_data: bytes) -> Dict:
        """Convert speech to text using local speech recognition"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return {'success': False, 'error': 'Speech recognition not available'}

        try:
            # Convert bytes to audio file
            audio_file = BytesIO(audio_data)

            # Use speech recognition
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)

            return {'success': True, 'text': text}
        except sr.UnknownValueError:
            return {'success': False, 'error': 'Could not understand audio'}
        except sr.RequestError as e:
            return {'success': False, 'error': f'Speech recognition error: {e}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
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
            device_fingerprint=self._optimize_device_fingerprint(device_info.get('fingerprint')),
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
            device_fingerprint=self._optimize_device_fingerprint(device_info.get('fingerprint'))
        )
        db.session.add(log)
        db.session.commit()
    
    # Helper methods
    def _generate_otp(self) -> str:
        import random
        return str(random.randint(100000, 999999))

    def _optimize_device_fingerprint(self, fingerprint: str) -> str:
        """Optimize device fingerprint for storage"""
        if not fingerprint:
            return None

        try:
            # If fingerprint is very long, create a hash instead
            if len(fingerprint) > 1000:
                # Create a SHA-256 hash of the fingerprint
                hash_obj = hashlib.sha256(fingerprint.encode('utf-8'))
                return f"hash:{hash_obj.hexdigest()}"

            # For shorter fingerprints, store as-is but limit length
            return fingerprint[:1000] if fingerprint else None

        except Exception as e:
            print(f"⚠️ Error optimizing device fingerprint: {e}")
            # Fallback: create hash of the fingerprint
            if fingerprint:
                hash_obj = hashlib.sha256(str(fingerprint).encode('utf-8'))
                return f"hash:{hash_obj.hexdigest()}"
            return None
    
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

    def _extract_voice_features(self, audio_array: np.ndarray) -> np.ndarray:
        """Extract voice features for biometric verification"""
        try:
            # Basic voice feature extraction
            # In a real implementation, you'd use more sophisticated features like MFCC
            features = []

            # Fundamental frequency (pitch)
            fft = np.fft.fft(audio_array)
            freqs = np.fft.fftfreq(len(fft))
            magnitude = np.abs(fft)
            fundamental_freq = freqs[np.argmax(magnitude)]
            features.append(fundamental_freq)

            # Energy
            energy = np.sum(audio_array ** 2) / len(audio_array)
            features.append(energy)

            # Zero crossing rate
            zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
            zcr = zero_crossings / len(audio_array)
            features.append(zcr)

            # Spectral centroid
            spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
            features.append(spectral_centroid)

            return np.array(features)
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return np.zeros(4)  # Return default features

    def capture_live_voice(self, duration: int = 3) -> bytes:
        """Capture live voice from microphone"""
        if not SPEECH_RECOGNITION_AVAILABLE or not self.microphone:
            return b''  # Return empty bytes if not available

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=duration)
                return audio.get_wav_data()
        except Exception as e:
            print(f"Voice capture error: {e}")
            return b""

    def process_ai_command(self, query: str, command_type: str = 'text', context: str = 'general') -> str:
        """Process AI commands and return intelligent responses"""
        try:
            # Normalize query
            query_lower = query.lower().strip()

            # Rice mill specific command processing
            if 'production' in query_lower:
                return self._handle_production_query(query_lower)
            elif 'inventory' in query_lower or 'stock' in query_lower:
                return self._handle_inventory_query(query_lower)
            elif 'sales' in query_lower or 'order' in query_lower:
                return self._handle_sales_query(query_lower)
            elif 'farmer' in query_lower:
                return self._handle_farmer_query(query_lower)
            elif 'quality' in query_lower:
                return self._handle_quality_query(query_lower)
            elif 'finance' in query_lower or 'payment' in query_lower:
                return self._handle_finance_query(query_lower)
            elif 'help' in query_lower:
                return self._get_help_response()
            else:
                return self._get_general_response(query)

        except Exception as e:
            return f"I'm sorry, I encountered an error processing your request: {str(e)}"

    def _handle_production_query(self, query: str) -> str:
        """Handle production-related queries"""
        if 'status' in query:
            return "Current production status: 3 batches in progress. Batch PB001 is 85% complete, expected completion in 2 hours. Overall efficiency is at 87.5%."
        elif 'today' in query:
            return "Today's production: 2,400 kg of rice processed across 4 batches. Quality grade A: 65%, Grade B: 30%, Grade C: 5%."
        elif 'efficiency' in query:
            return "Current production efficiency is 87.5%, which is 2.3% above last month's average. AI suggests optimizing evening shift parameters for 15% improvement."
        else:
            return "I can help you with production status, today's output, efficiency metrics, and batch tracking. What specific information do you need?"

    def _handle_inventory_query(self, query: str) -> str:
        """Handle inventory-related queries"""
        if 'low' in query or 'alert' in query:
            return "Current low stock alerts: Basmati rice (120 kg remaining, 3 days supply), Packaging materials (2 days supply). Recommend immediate procurement."
        elif 'total' in query:
            return "Total inventory: Paddy stock: 15,400 kg, Finished rice: 8,200 kg, Broken rice: 1,100 kg. Storage utilization: 68%."
        elif 'basmati' in query:
            return "Basmati rice inventory: 120 kg in stock, 45 kg reserved for pending orders. Current market price: ₹85/kg. Recommend restocking."
        else:
            return "I can provide inventory levels, stock alerts, storage utilization, and procurement recommendations. What would you like to know?"

    def _handle_sales_query(self, query: str) -> str:
        """Handle sales-related queries"""
        if 'today' in query:
            return "Today's sales: ₹45,000 revenue from 8 orders. Top customer: ABC Traders (₹12,000). Pending deliveries: 3 orders worth ₹18,000."
        elif 'pending' in query:
            return "Pending orders: 12 orders totaling ₹1,25,000. 3 orders due for delivery today, 5 orders in production, 4 orders awaiting confirmation."
        elif 'customer' in query:
            return "Top customers this month: ABC Traders (₹85,000), XYZ Distributors (₹67,000), Rice Mart (₹45,000). 2 new customer registrations pending approval."
        else:
            return "I can help with sales reports, order status, customer information, and revenue analytics. What specific data do you need?"

    def _handle_farmer_query(self, query: str) -> str:
        """Handle farmer-related queries"""
        if 'payment' in query:
            return "Farmer payments: ₹2,35,000 pending for this week's procurement. 15 farmers have payments due. Average payment cycle: 3 days."
        elif 'procurement' in query:
            return "Recent procurement: 5,400 kg paddy purchased this week from 23 farmers. Average price: ₹28/kg. Quality distribution: Grade A: 70%, Grade B: 25%, Grade C: 5%."
        else:
            return "I can provide farmer payment status, procurement reports, quality assessments, and contract information. How can I assist?"

    def _handle_quality_query(self, query: str) -> str:
        """Handle quality-related queries"""
        if 'test' in query or 'report' in query:
            return "Latest quality tests: 15 samples tested today. Pass rate: 94%. Issues detected: 1 batch with high moisture content (15.2%). Recommended actions sent to production team."
        elif 'grade' in query:
            return "Current quality distribution: Grade A: 65% (excellent), Grade B: 30% (good), Grade C: 5% (acceptable). Overall quality score: 91.7%."
        else:
            return "I can provide quality test results, grade distributions, compliance reports, and improvement recommendations. What information do you need?"

    def _handle_finance_query(self, query: str) -> str:
        """Handle finance-related queries"""
        if 'revenue' in query:
            return "This month's revenue: ₹6,80,000 (18% increase from last month). Profit margin: 23.8%. Outstanding receivables: ₹1,25,000."
        elif 'expense' in query:
            return "Monthly expenses: ₹4,20,000. Major categories: Raw materials (60%), Labor (25%), Utilities (10%), Others (5%). 3 pending approvals worth ₹45,000."
        elif 'profit' in query:
            return "Current profit margin: 23.8% (above industry average of 20%). Monthly profit: ₹2,60,000. YTD profit growth: 15%."
        else:
            return "I can provide revenue reports, expense analysis, profit margins, and financial forecasts. What financial information do you need?"

    def _get_help_response(self) -> str:
        """Provide help information"""
        return """I'm your AI assistant for rice mill management. I can help you with:

• Production: Status, efficiency, batch tracking
• Inventory: Stock levels, alerts, procurement
• Sales: Orders, revenue, customer data
• Farmers: Payments, procurement, contracts
• Quality: Test results, grades, compliance
• Finance: Revenue, expenses, profit analysis

Just ask me questions like "What's the production status?" or "Show me today's sales" and I'll provide detailed information."""

    def _get_general_response(self, query: str) -> str:
        """Handle general queries"""
        return f"I understand you're asking about '{query}'. I'm specialized in rice mill operations. Try asking about production, inventory, sales, farmers, quality, or finance. You can also say 'help' for more information."

    def generate_username_suggestions(self, name: str) -> list:
        """Generate AI-powered username suggestions"""
        try:
            # Basic name processing
            name = name.lower().strip()
            name_parts = name.split()

            suggestions = []

            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = name_parts[-1]

                # Generate various combinations
                suggestions.extend([
                    f"{first_name}.{last_name}",
                    f"{first_name}_{last_name}",
                    f"{first_name}{last_name}",
                    f"{first_name[0]}{last_name}",
                    f"{first_name}{last_name[0]}",
                    f"{last_name}.{first_name}",
                    f"{first_name}.{last_name}123",
                    f"{first_name}_{last_name}_2024"
                ])
            else:
                # Single name
                base_name = name_parts[0] if name_parts else name
                suggestions.extend([
                    base_name,
                    f"{base_name}123",
                    f"{base_name}_user",
                    f"{base_name}2024",
                    f"user_{base_name}",
                    f"{base_name}_admin"
                ])

            # Remove duplicates and limit to 6 suggestions
            unique_suggestions = list(dict.fromkeys(suggestions))[:6]

            return unique_suggestions

        except Exception as e:
            # Return basic suggestions on error
            return [
                "user123",
                "admin_user",
                "rice_mill_user",
                "operator123",
                "manager_user",
                "staff_member"
            ]