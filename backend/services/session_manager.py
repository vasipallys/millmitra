"""
Session Management Service
Handles user sessions, authentication state, and security
"""

import redis
import json
import uuid
from datetime import datetime, timedelta
from flask import session, request, current_app
from flask_jwt_extended import get_jwt_identity, get_jwt
from extensions import db
from models.user import User, UserSession
import hashlib
import secrets


class SessionManager:
    def __init__(self, app=None):
        self.redis_client = None
        self.use_redis = False
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize session manager with Flask app"""
        redis_url = app.config.get('SESSION_REDIS_URL')
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                print(f"Redis connected successfully at {redis_url}")
            except Exception as e:
                print(f"Warning: Redis connection failed: {e}. Falling back to database-only sessions.")
                self.redis_client = None
                self.use_redis = False
        else:
            print("Redis URL not configured. Using database-only sessions.")
            self.use_redis = False

        self.session_prefix = app.config.get('SESSION_KEY_PREFIX', 'rice_mill_session:')
        self.session_timeout = app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=24))
    
    def create_session(self, user_id, device_info=None, ip_address=None):
        """Create a new user session"""
        try:
            # Generate unique session token
            session_token = self._generate_session_token()
            
            # Get device fingerprint
            device_fingerprint = self._get_device_fingerprint(device_info)
            
            # Session data
            session_data = {
                'user_id': user_id,
                'session_token': session_token,
                'device_fingerprint': device_fingerprint,
                'ip_address': ip_address or self._get_client_ip(),
                'created_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat(),
                'is_active': True,
                'login_method': 'standard',
                'security_level': 'normal'
            }
            
            # Store in Redis with expiration (if available)
            if self.use_redis and self.redis_client:
                try:
                    redis_key = f"{self.session_prefix}{session_token}"
                    self.redis_client.setex(
                        redis_key,
                        int(self.session_timeout.total_seconds()),
                        json.dumps(session_data)
                    )
                except Exception as e:
                    print(f"Warning: Redis set failed: {e}. Session will be database-only.")
            
            # Store in database for persistence and audit
            db_session = UserSession(
                user_id=user_id,
                session_token=session_token,
                device_info=json.dumps(device_info) if device_info else None,
                ip_address=ip_address or self._get_client_ip(),
                expires_at=datetime.utcnow() + self.session_timeout,
                is_active=True
            )
            db.session.add(db_session)
            db.session.commit()
            
            return session_token
            
        except Exception as e:
            current_app.logger.error(f"Error creating session: {str(e)}")
            return None
    
    def get_session(self, session_token):
        """Get session data by token"""
        try:
            # Try Redis first (if available)
            if self.use_redis and self.redis_client:
                try:
                    redis_key = f"{self.session_prefix}{session_token}"
                    session_data = self.redis_client.get(redis_key)

                    if session_data:
                        return json.loads(session_data)
                except Exception as e:
                    print(f"Warning: Redis get failed: {e}. Falling back to database.")

            # Fallback to database if not in Redis
            db_session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()

            if db_session and not db_session.is_expired():
                # Restore to Redis (if available)
                session_data = {
                    'user_id': db_session.user_id,
                    'session_token': session_token,
                    'ip_address': db_session.ip_address,
                    'created_at': db_session.created_at.isoformat(),
                    'last_activity': db_session.last_activity.isoformat(),
                    'is_active': True
                }

                # Restore to Redis if available
                if self.use_redis and self.redis_client:
                    try:
                        redis_key = f"{self.session_prefix}{session_token}"
                        self.redis_client.setex(
                            redis_key,
                            int(self.session_timeout.total_seconds()),
                            json.dumps(session_data)
                        )
                    except Exception as e:
                        print(f"Warning: Redis restore failed: {e}.")

                return session_data
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting session: {str(e)}")
            return None
    
    def update_session_activity(self, session_token):
        """Update session last activity timestamp"""
        try:
            session_data = self.get_session(session_token)
            if session_data:
                session_data['last_activity'] = datetime.utcnow().isoformat()
                
                redis_key = f"{self.session_prefix}{session_token}"
                self.redis_client.setex(
                    redis_key,
                    int(self.session_timeout.total_seconds()),
                    json.dumps(session_data)
                )
                
                # Update database
                UserSession.query.filter_by(session_token=session_token).update({
                    'last_activity': datetime.utcnow()
                })
                db.session.commit()
                
                return True
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error updating session activity: {str(e)}")
            return False
    
    def invalidate_session(self, session_token):
        """Invalidate a specific session"""
        try:
            # Remove from Redis
            redis_key = f"{self.session_prefix}{session_token}"
            self.redis_client.delete(redis_key)
            
            # Mark as inactive in database
            UserSession.query.filter_by(session_token=session_token).update({
                'is_active': False
            })
            db.session.commit()
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error invalidating session: {str(e)}")
            return False
    
    def invalidate_user_sessions(self, user_id, except_token=None):
        """Invalidate all sessions for a user except specified token"""
        try:
            # Get all user sessions
            user_sessions = UserSession.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            for session in user_sessions:
                if except_token and session.session_token == except_token:
                    continue
                
                # Remove from Redis
                redis_key = f"{self.session_prefix}{session.session_token}"
                self.redis_client.delete(redis_key)
                
                # Mark as inactive
                session.is_active = False
            
            db.session.commit()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error invalidating user sessions: {str(e)}")
            return False
    
    def get_active_sessions(self, user_id):
        """Get all active sessions for a user"""
        try:
            sessions = UserSession.query.filter_by(
                user_id=user_id,
                is_active=True
            ).filter(
                UserSession.expires_at > datetime.utcnow()
            ).all()
            
            return [{
                'id': session.id,
                'device_info': json.loads(session.device_info) if session.device_info else {},
                'ip_address': session.ip_address,
                'last_activity': session.last_activity.isoformat(),
                'created_at': session.created_at.isoformat(),
                'is_current': False  # Will be set by caller
            } for session in sessions]
            
        except Exception as e:
            current_app.logger.error(f"Error getting active sessions: {str(e)}")
            return []
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions from database"""
        try:
            expired_sessions = UserSession.query.filter(
                UserSession.expires_at < datetime.utcnow()
            ).all()
            
            for session in expired_sessions:
                # Remove from Redis
                redis_key = f"{self.session_prefix}{session.session_token}"
                self.redis_client.delete(redis_key)
                
                # Mark as inactive
                session.is_active = False
            
            db.session.commit()
            return len(expired_sessions)
            
        except Exception as e:
            current_app.logger.error(f"Error cleaning up expired sessions: {str(e)}")
            return 0
    
    def _generate_session_token(self):
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def _get_device_fingerprint(self, device_info):
        """Generate device fingerprint from device info"""
        if not device_info:
            return None
        
        # Create fingerprint from device characteristics
        fingerprint_data = {
            'user_agent': device_info.get('user_agent', ''),
            'screen_resolution': device_info.get('screen_resolution', ''),
            'timezone': device_info.get('timezone', ''),
            'language': device_info.get('language', ''),
            'platform': device_info.get('platform', '')
        }
        
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    def _get_client_ip(self):
        """Get client IP address"""
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        elif request.environ.get('HTTP_X_REAL_IP'):
            return request.environ['HTTP_X_REAL_IP']
        else:
            return request.environ.get('REMOTE_ADDR', 'unknown')


# Global session manager instance
session_manager = SessionManager()
