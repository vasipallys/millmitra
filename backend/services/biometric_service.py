"""
Biometric Authentication Service
Handles fingerprint, face recognition, and voice biometrics
"""

import numpy as np
import base64
from typing import Dict, Optional, Tuple
from io import BytesIO
from PIL import Image
import hashlib
import json
from datetime import datetime, timedelta

from extensions import db
from models import User

# Handle OpenCV compatibility issues
try:
    import cv2
    CV2_AVAILABLE = True
    try:
        # Check if cv2.face is available (requires opencv-contrib-python)
        cv2.face.LBPHFaceRecognizer_create()
        CV2_FACE_AVAILABLE = True
    except AttributeError:
        CV2_FACE_AVAILABLE = False
except ImportError:
    CV2_AVAILABLE = False
    CV2_FACE_AVAILABLE = False
    cv2 = None

class BiometricService:
    def __init__(self):
        # Initialize OpenCV components if available
        if CV2_AVAILABLE:
            try:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            except:
                self.face_cascade = None
        else:
            self.face_cascade = None

        if CV2_FACE_AVAILABLE:
            try:
                self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
            except:
                self.face_recognizer = None
        else:
            self.face_recognizer = None
        
    def register_face(self, user_id: int, image_data: str) -> Dict:
        """Register user's face for biometric authentication"""
        if not CV2_AVAILABLE or not self.face_cascade:
            return {
                'success': False,
                'error': 'Face recognition not available - OpenCV not installed or configured'
            }

        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(BytesIO(image_bytes))
            image_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return {'success': False, 'error': 'No face detected'}
            
            if len(faces) > 1:
                return {'success': False, 'error': 'Multiple faces detected. Please ensure only one face is visible'}
            
            # Extract face region
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            
            # Resize to standard size
            face_roi = cv2.resize(face_roi, (200, 200))
            
            # Extract features
            features = self._extract_face_features(face_roi)
            
            # Store biometric data
            user = User.query.get(user_id)
            if user:
                biometric_data = {
                    'face_features': features.tolist(),
                    'face_encoding': base64.b64encode(face_roi.tobytes()).decode(),
                    'registered_at': datetime.utcnow().isoformat()
                }
                
                # Update user preferences with biometric data
                preferences = user.get_preferences()
                preferences['biometric_data'] = biometric_data
                user.set_preferences(preferences)
                db.session.commit()
                
                return {'success': True, 'message': 'Face registered successfully'}
            
            return {'success': False, 'error': 'User not found'}
            
        except Exception as e:
            return {'success': False, 'error': f'Face registration failed: {str(e)}'}
    
    def verify_face(self, user_id: int, image_data: str) -> Dict:
        """Verify user's face against registered biometric"""
        if not CV2_AVAILABLE or not self.face_cascade:
            return {
                'success': False,
                'error': 'Face verification not available - OpenCV not installed or configured'
            }

        try:
            # Decode image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(BytesIO(image_bytes))
            image_array = np.array(image)
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) == 0:
                return {'success': False, 'error': 'No face detected'}
            
            # Extract face region
            (x, y, w, h) = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))
            
            # Extract features
            current_features = self._extract_face_features(face_roi)
            
            # Get stored biometric data
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            preferences = user.get_preferences()
            biometric_data = preferences.get('biometric_data', {})
            
            if 'face_features' not in biometric_data:
                return {'success': False, 'error': 'No face biometric registered'}
            
            stored_features = np.array(biometric_data['face_features'])
            
            # Calculate similarity
            similarity = self._calculate_face_similarity(current_features, stored_features)
            
            # Threshold for face verification (adjust based on testing)
            threshold = 0.8
            
            if similarity > threshold:
                return {
                    'success': True, 
                    'confidence': float(similarity),
                    'message': 'Face verified successfully'
                }
            else:
                return {
                    'success': False, 
                    'confidence': float(similarity),
                    'error': 'Face verification failed'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Face verification failed: {str(e)}'}
    
    def register_fingerprint(self, user_id: int, fingerprint_data: str) -> Dict:
        """Register user's fingerprint (simulated)"""
        try:
            # In a real implementation, this would process actual fingerprint data
            # For now, we'll simulate by storing a hash of the fingerprint data
            
            fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            # Extract simulated minutiae points
            minutiae = self._extract_fingerprint_minutiae(fingerprint_data)
            
            user = User.query.get(user_id)
            if user:
                preferences = user.get_preferences()
                biometric_data = preferences.get('biometric_data', {})
                
                biometric_data['fingerprint'] = {
                    'hash': fingerprint_hash,
                    'minutiae': minutiae,
                    'registered_at': datetime.utcnow().isoformat()
                }
                
                preferences['biometric_data'] = biometric_data
                user.set_preferences(preferences)
                db.session.commit()
                
                return {'success': True, 'message': 'Fingerprint registered successfully'}
            
            return {'success': False, 'error': 'User not found'}
            
        except Exception as e:
            return {'success': False, 'error': f'Fingerprint registration failed: {str(e)}'}
    
    def verify_fingerprint(self, user_id: int, fingerprint_data: str) -> Dict:
        """Verify user's fingerprint"""
        try:
            fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            current_minutiae = self._extract_fingerprint_minutiae(fingerprint_data)
            
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            preferences = user.get_preferences()
            biometric_data = preferences.get('biometric_data', {})
            
            if 'fingerprint' not in biometric_data:
                return {'success': False, 'error': 'No fingerprint registered'}
            
            stored_data = biometric_data['fingerprint']
            stored_minutiae = stored_data['minutiae']
            
            # Calculate similarity
            similarity = self._calculate_fingerprint_similarity(current_minutiae, stored_minutiae)
            
            threshold = 0.85
            
            if similarity > threshold:
                return {
                    'success': True,
                    'confidence': float(similarity),
                    'message': 'Fingerprint verified successfully'
                }
            else:
                return {
                    'success': False,
                    'confidence': float(similarity),
                    'error': 'Fingerprint verification failed'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Fingerprint verification failed: {str(e)}'}
    
    def get_biometric_status(self, user_id: int) -> Dict:
        """Get user's biometric registration status"""
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}
        
        preferences = user.get_preferences()
        biometric_data = preferences.get('biometric_data', {})
        
        return {
            'face_registered': 'face_features' in biometric_data,
            'fingerprint_registered': 'fingerprint' in biometric_data,
            'voice_registered': 'voice_features' in biometric_data,
            'registration_date': biometric_data.get('registered_at')
        }
    
    def _extract_face_features(self, face_image: np.ndarray) -> np.ndarray:
        """Extract facial features for comparison"""
        if not CV2_AVAILABLE:
            return np.zeros(259)  # Return default features if OpenCV not available

        try:
            # Simple feature extraction using histogram
            hist = cv2.calcHist([face_image], [0], None, [256], [0, 256])
            
            # Normalize histogram
            hist = hist.flatten()
            hist = hist / np.sum(hist)
            
            # Add geometric features
            height, width = face_image.shape
            geometric_features = np.array([height, width, height/width])
            
            # Combine features
            features = np.concatenate([hist, geometric_features])
            
            return features
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return np.zeros(259)  # 256 histogram + 3 geometric features
    
    def _calculate_face_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate similarity between two face feature vectors"""
        try:
            # Ensure same length
            min_len = min(len(features1), len(features2))
            features1 = features1[:min_len]
            features2 = features2[:min_len]
            
            # Calculate cosine similarity
            dot_product = np.dot(features1, features2)
            norm1 = np.linalg.norm(features1)
            norm2 = np.linalg.norm(features2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, similarity)  # Ensure non-negative
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def _extract_fingerprint_minutiae(self, fingerprint_data: str) -> list:
        """Extract minutiae points from fingerprint (simulated)"""
        # In a real implementation, this would use actual fingerprint processing
        # For simulation, we'll create pseudo-minutiae based on the data
        
        hash_bytes = hashlib.md5(fingerprint_data.encode()).digest()
        minutiae = []
        
        for i in range(0, len(hash_bytes), 3):
            if i + 2 < len(hash_bytes):
                x = hash_bytes[i] % 100
                y = hash_bytes[i + 1] % 100
                angle = hash_bytes[i + 2] % 360
                minutiae.append({'x': x, 'y': y, 'angle': angle})
        
        return minutiae[:20]  # Limit to 20 minutiae points
    
    def _calculate_fingerprint_similarity(self, minutiae1: list, minutiae2: list) -> float:
        """Calculate similarity between fingerprint minutiae"""
        if not minutiae1 or not minutiae2:
            return 0.0
        
        matches = 0
        tolerance = 10  # Pixel tolerance for matching
        
        for m1 in minutiae1:
            for m2 in minutiae2:
                distance = np.sqrt((m1['x'] - m2['x'])**2 + (m1['y'] - m2['y'])**2)
                angle_diff = abs(m1['angle'] - m2['angle'])
                
                if distance < tolerance and angle_diff < 30:
                    matches += 1
                    break
        
        # Calculate similarity as ratio of matches
        max_possible_matches = min(len(minutiae1), len(minutiae2))
        return matches / max_possible_matches if max_possible_matches > 0 else 0.0
