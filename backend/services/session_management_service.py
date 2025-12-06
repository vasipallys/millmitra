"""
Session Management Service
Enhanced session handling using existing UserSession model
"""

import uuid
import hashlib
import json
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from models.user import User, UserSession, AuthLog
from extensions import db
import secrets
import user_agents

class SessionManagementService:
    
    # Session configuration
    SESSION_TIMEOUT_HOURS = 8
    MAX_SESSIONS_PER_USER = 5
    INACTIVITY_TIMEOUT_MINUTES = 30
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    @staticmethod
    def create_session(user, request_data=None):
        """Create new user session with security checks"""
        try:
            # Extract request information
            ip_address = SessionManagementService._get_client_ip(request_data)
            user_agent = request_data.headers.get('User-Agent', '') if request_data else ''
            
            # Parse user agent for device info
            device_info = SessionManagementService._parse_user_agent(user_agent)
            
            # Generate session token
            session_token = secrets.token_hex(64)
            
            # Create session using existing model structure
            expires_at = datetime.utcnow() + timedelta(hours=SessionManagementService.SESSION_TIMEOUT_HOURS)
            
            session = UserSession(
                user_id=user.id,
                session_token=session_token,
                device_info=json.dumps(device_info),
                ip_address=ip_address,
                expires_at=expires_at,
                is_active=True,
                last_activity=datetime.utcnow()
            )
            
            db.session.add(session)
            
            # Log successful login
            auth_log = AuthLog(
                user_id=user.id,
                username_attempted=user.username,
                action='login',
                method='password',
                success=True,
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=SessionManagementService._create_device_fingerprint(ip_address, user_agent, device_info),
                risk_score=SessionManagementService._calculate_login_risk(user, ip_address)
            )
            
            db.session.add(auth_log)
            
            # Clean up old sessions
            SessionManagementService._cleanup_old_sessions(user.id)
            
            # Update user last login
            user.last_login = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'session_token': session_token,
                'expires_at': expires_at.isoformat(),
                'user_id': user.id,
                'username': user.username
            }
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def validate_session(session_token):
        """Validate session token and return user"""
        try:
            session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if not session:
                return None
            
            # Check if session expired
            if datetime.utcnow() > session.expires_at:
                SessionManagementService.terminate_session(session.id, 'expired')
                return None
            
            # Check for inactivity timeout
            if session.last_activity:
                inactivity_threshold = datetime.utcnow() - timedelta(
                    minutes=SessionManagementService.INACTIVITY_TIMEOUT_MINUTES
                )
                
                if session.last_activity < inactivity_threshold:
                    SessionManagementService.terminate_session(session.id, 'inactivity')
                    return None
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            db.session.commit()
            
            return session.user
            
        except Exception as e:
            print(f"Session validation error: {str(e)}")
            return None
    
    @staticmethod
    def terminate_session(session_id, reason='user_logout'):
        """Terminate a specific session"""
        try:
            session = UserSession.query.get(session_id)
            
            if session:
                session.is_active = False
                
                # Log logout
                auth_log = AuthLog(
                    user_id=session.user_id,
                    action='logout',
                    success=True,
                    ip_address=session.ip_address,
                    timestamp=datetime.utcnow()
                )
                
                db.session.add(auth_log)
                db.session.commit()
                
            return True
            
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def terminate_all_user_sessions(user_id, except_session_id=None):
        """Terminate all sessions for a user"""
        try:
            query = UserSession.query.filter_by(user_id=user_id, is_active=True)
            
            if except_session_id:
                query = query.filter(UserSession.id != except_session_id)
            
            sessions = query.all()
            
            for session in sessions:
                session.is_active = False
            
            db.session.commit()
            return len(sessions)
            
        except Exception as e:
            db.session.rollback()
            return 0
    
    @staticmethod
    def get_user_sessions(user_id, active_only=True):
        """Get all sessions for a user"""
        query = UserSession.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        sessions = query.order_by(UserSession.last_activity.desc()).all()
        
        return [{
            'id': s.id,
            'user_id': s.user_id,
            'device_info': json.loads(s.device_info) if s.device_info else {},
            'ip_address': s.ip_address,
            'is_active': s.is_active,
            'last_activity': s.last_activity.isoformat() if s.last_activity else None,
            'expires_at': s.expires_at.isoformat() if s.expires_at else None,
            'created_at': s.created_at.isoformat() if s.created_at else None
        } for s in sessions]
    
    @staticmethod
    def check_brute_force_protection(username, ip_address):
        """Check if login should be blocked due to brute force attempts"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=SessionManagementService.LOCKOUT_DURATION_MINUTES)
        
        # Count recent failed attempts
        failed_attempts = AuthLog.query.filter(
            and_(
                AuthLog.username_attempted == username,
                AuthLog.success == False,
                AuthLog.timestamp > cutoff_time
            )
        ).count()
        
        # Also check IP-based attempts
        ip_failed_attempts = AuthLog.query.filter(
            and_(
                AuthLog.ip_address == ip_address,
                AuthLog.success == False,
                AuthLog.timestamp > cutoff_time
            )
        ).count()
        
        return {
            'blocked': failed_attempts >= SessionManagementService.MAX_LOGIN_ATTEMPTS or ip_failed_attempts >= SessionManagementService.MAX_LOGIN_ATTEMPTS * 2,
            'attempts_remaining': max(0, SessionManagementService.MAX_LOGIN_ATTEMPTS - failed_attempts),
            'lockout_expires': cutoff_time + timedelta(minutes=SessionManagementService.LOCKOUT_DURATION_MINUTES)
        }
    
    @staticmethod
    def log_failed_login(username, ip_address, user_agent, reason, user_id=None):
        """Log failed login attempt"""
        try:
            device_info = SessionManagementService._parse_user_agent(user_agent)
            device_fingerprint = SessionManagementService._create_device_fingerprint(
                ip_address, user_agent, device_info
            )
            
            # Calculate risk score for failed attempt
            risk_score = 0.5  # Base risk for failed attempt
            
            auth_log = AuthLog(
                user_id=user_id,
                username_attempted=username,
                action='failed_login',
                method='password',
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                failure_reason=reason,
                risk_score=risk_score,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(auth_log)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Failed to log login attempt: {str(e)}")
    
    @staticmethod
    def _cleanup_old_sessions(user_id):
        """Remove old sessions if user exceeds limit"""
        sessions = UserSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(UserSession.last_activity.desc()).all()
        
        if len(sessions) >= SessionManagementService.MAX_SESSIONS_PER_USER:
            # Terminate oldest sessions
            sessions_to_terminate = sessions[SessionManagementService.MAX_SESSIONS_PER_USER-1:]
            
            for session in sessions_to_terminate:
                session.is_active = False
    
    @staticmethod
    def _get_client_ip(request_data):
        """Extract client IP from request"""
        if not request_data:
            return 'unknown'
        
        # Check for forwarded IP (common in load balancers)
        forwarded = request_data.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        
        # Check other common headers
        real_ip = request_data.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request_data.remote_addr or 'unknown'
    
    @staticmethod
    def _parse_user_agent(user_agent):
        """Parse user agent for device information"""
        try:
            ua = user_agents.parse(user_agent)
            
            return {
                'browser': f"{ua.browser.family} {ua.browser.version_string}",
                'os': f"{ua.os.family} {ua.os.version_string}",
                'device_type': 'mobile' if ua.is_mobile else 'tablet' if ua.is_tablet else 'desktop'
            }
        except:
            return {
                'browser': 'unknown',
                'os': 'unknown',
                'device_type': 'unknown'
            }
    
    @staticmethod
    def _create_device_fingerprint(ip_address, user_agent, device_info):
        """Create device fingerprint for session tracking"""
        fingerprint_data = f"{ip_address}:{user_agent}:{device_info.get('browser', '')}:{device_info.get('os', '')}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    @staticmethod
    def _calculate_login_risk(user, ip_address):
        """Calculate basic risk score for login attempt"""
        risk_score = 0.0
        
        # Check if this is a new IP
        recent_ip_sessions = UserSession.query.filter(
            and_(
                UserSession.user_id == user.id,
                UserSession.ip_address == ip_address,
                UserSession.created_at > datetime.utcnow() - timedelta(days=7)
            )
        ).count()
        
        if recent_ip_sessions == 0:
            risk_score += 0.2  # New IP
        
        # Check recent failed attempts from this IP
        recent_failures = AuthLog.query.filter(
            and_(
                AuthLog.ip_address == ip_address,
                AuthLog.success == False,
                AuthLog.timestamp > datetime.utcnow() - timedelta(hours=1)
            )
        ).count()
        
        risk_score += min(0.4, recent_failures * 0.1)
        
        # Check time-based patterns (unusual login hours)
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 23:
            risk_score += 0.1  # Unusual hours
        
        return min(1.0, risk_score)