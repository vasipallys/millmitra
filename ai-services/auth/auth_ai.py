from fastapi import APIRouter, UploadFile, File, Form
import speech_recognition as sr
import numpy as np
from typing import Dict, List
import cv2
import face_recognition
from io import BytesIO
import librosa

router = APIRouter()

class AuthAI:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    async def correct_username(self, username: str) -> str:
        """AI-powered username typo correction"""
        # Implement fuzzy matching against known usernames
        # This would typically use a trained model or fuzzy string matching
        corrections = {
            'jhon': 'john',
            'admn': 'admin',
            'manger': 'manager'
        }
        return corrections.get(username.lower(), username)
    
    async def assess_login_risk(self, user_data: Dict) -> float:
        """AI-powered risk assessment"""
        risk_score = 0.0
        
        # Analyze login patterns
        login_history = user_data.get('login_history', {})
        current_time = user_data.get('current_time')
        device_info = user_data.get('device_info', {})
        
        # Time-based analysis
        usual_hours = login_history.get('login_times', [])
        if usual_hours:
            current_hour = int(current_time.split('T')[1].split(':')[0])
            if current_hour not in usual_hours:
                risk_score += 0.3
        
        # Device analysis
        known_devices = login_history.get('devices', [])
        current_device = device_info.get('fingerprint')
        if current_device not in known_devices:
            risk_score += 0.4
        
        # Location analysis (simplified)
        known_locations = login_history.get('locations', [])
        current_location = device_info.get('location')
        if current_location and current_location not in known_locations:
            risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    async def verify_voice_print(self, user_id: int, audio_data: bytes) -> Dict:
        """Verify voice biometric"""
        try:
            # Extract voice features
            audio_features = self._extract_voice_features(audio_data)
            
            # Compare with stored voice print
            # In production, this would use a trained speaker verification model
            stored_features = self._get_stored_voice_features(user_id)
            
            if stored_features is None:
                return {'verified': False, 'confidence': 0.0, 'error': 'No voice print on file'}
            
            # Calculate similarity
            similarity = self._calculate_voice_similarity(audio_features, stored_features)
            
            return {
                'verified': similarity > 0.8,
                'confidence': similarity,
                'features': audio_features.tolist()
            }
            
        except Exception as e:
            return {'verified': False, 'confidence': 0.0, 'error': str(e)}
    
    async def verify_face_biometric(self, user_id: int, image_data: bytes) -> Dict:
        """Verify face biometric"""
        try:
            # Load image
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Extract face encoding
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                return {'verified': False, 'confidence': 0.0, 'error': 'No face detected'}
            
            current_encoding = face_encodings[0]
            
            # Compare with stored encoding
            stored_encoding = self._get_stored_face_encoding(user_id)
            
            if stored_encoding is None:
                return {'verified': False, 'confidence': 0.0, 'error': 'No face encoding on file'}
            
            # Calculate similarity
            distance = face_recognition.face_distance([stored_encoding], current_encoding)[0]
            confidence = 1 - distance
            
            return {
                'verified': confidence > 0.85,
                'confidence': confidence,
                'encoding': current_encoding.tolist()
            }
            
        except Exception as e:
            return {'verified': False, 'confidence': 0.0, 'error': str(e)}
    
    def _extract_voice_features(self, audio_data: bytes) -> np.ndarray:
        """Extract voice features for comparison"""
        # Convert bytes to audio array
        audio_array = np.frombuffer(audio_data, dtype=np.float32)
        
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(y=audio_array, sr=22050, n_mfcc=13)
        
        # Return mean of features
        return np.mean(mfccs, axis=1)
    
    def _calculate_voice_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate similarity between voice features"""
        # Cosine similarity
        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _get_stored_voice_features(self, user_id: int) -> np.ndarray:
        """Get stored voice features for user"""
        # In production, this would query the database
        # For demo, return None
        return None
    
    def _get_stored_face_encoding(self, user_id: int) -> np.ndarray:
        """Get stored face encoding for user"""
        # In production, this would query the database
        # For demo, return None
        return None

auth_ai = AuthAI()

@router.post("/correct-username")
async def correct_username(data: Dict):
    corrected = await auth_ai.correct_username(data['username'])
    return {'corrected': corrected}

@router.post("/assess-login-risk")
async def assess_login_risk(data: Dict):
    risk_score = await auth_ai.assess_login_risk(data)
    return {'risk_score': risk_score}

@router.post("/verify-voice")
async def verify_voice(audio: UploadFile = File(...), user_id: int = Form(...)):
    audio_data = await audio.read()
    result = await auth_ai.verify_voice_print(user_id, audio_data)
    return result

@router.post("/verify-biometric")
async def verify_biometric(data: Dict):
    user_id = data['user_id']
    biometric_data = data['biometric_data']
    
    if 'image' in biometric_data:
        # Face verification
        image_data = bytes(biometric_data['image'])
        result = await auth_ai.verify_face_biometric(user_id, image_data)
    else:
        result = {'verified': False, 'error': 'Unsupported biometric type'}
    
    return result

@router.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    try:
        audio_data = await audio.read()
        
        # Convert to recognizable format
        recognizer = sr.Recognizer()
        audio_file = sr.AudioFile(BytesIO(audio_data))
        
        with audio_file as source:
            audio = recognizer.record(source)
        
        text = recognizer.recognize_google(audio)
        
        return {'success': True, 'text': text}
    except Exception as e:
        return {'success': False, 'error': str(e)}