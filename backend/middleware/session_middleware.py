"""
Session Middleware
Handles automatic session management for all requests
"""

from flask import request, g, current_app, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from functools import wraps
from services.session_manager import session_manager
from models.user import User
import json


class SessionMiddleware:
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize session middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Initialize session manager
        session_manager.init_app(app)
    
    def before_request(self):
        """Process request before handling"""
        # Skip session handling for certain endpoints
        if self._should_skip_session():
            return

        # Initialize defaults
        g.current_user = None
        g.user_id = None
        g.session_token = None

        # Skip JWT validation for OPTIONS requests
        if request.method == 'OPTIONS':
            return

        # Try to get session from JWT token
        try:
            # Use optional=True to avoid exceptions on missing tokens
            verify_jwt_in_request(optional=True)

            # Only proceed if we have a valid JWT context
            try:
                user_id = get_jwt_identity()

                if user_id:
                    try:
                        user_pk = int(user_id)
                    except (TypeError, ValueError):
                        user_pk = None
                    user = User.query.get(user_pk) if user_pk else None
                    if user and user.is_active:
                        g.current_user = user
                        g.user_id = user_id

                        # Update session activity if session token exists
                        session_token = request.headers.get('X-Session-Token')
                        if session_token:
                            session_manager.update_session_activity(session_token)
                            g.session_token = session_token

            except Exception as jwt_error:
                # JWT identity not available, which is fine for optional requests
                current_app.logger.debug(f"JWT identity not available: {str(jwt_error)}")
                pass

        except Exception as e:
            # Log only if it's not a common "no token" error
            if "Missing Authorization Header" not in str(e):
                current_app.logger.debug(f"Session validation error: {str(e)}")
            pass
    
    def after_request(self, response):
        """Process response after handling"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add session info to response headers if user is authenticated
        if hasattr(g, 'current_user') and g.current_user:
            response.headers['X-User-ID'] = str(g.current_user.id)
            response.headers['X-User-Role'] = g.current_user.role
            
            if hasattr(g, 'session_token'):
                response.headers['X-Session-Token'] = g.session_token
        
        return response
    
    def _should_skip_session(self):
        """Check if session handling should be skipped for this request"""
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return True

        # Skip for specific paths
        skip_paths = [
            '/api/health',
            '/api/ready',
            '/api/auth/login',
            '/api/auth/register',
            '/api/auth/voice-login',
            '/static/',
            '/favicon.ico',
            '/robots.txt'
        ]

        # Skip for static files and common non-authenticated endpoints
        skip_patterns = [
            '/static/',
            '/assets/',
            '/public/',
            '/.well-known/'
        ]

        # Check exact paths
        if any(request.path.startswith(path) for path in skip_paths):
            return True

        # Check patterns
        if any(pattern in request.path for pattern in skip_patterns):
            return True

        return False


def require_session(f):
    """Decorator to require valid session"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({'error': 'Valid session required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def require_role(role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if g.current_user.role != role and g.current_user.role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_role(*roles):
    """Decorator to require any of the specified roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if g.current_user.role not in roles and g.current_user.role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_user_activity(activity_type, details=None):
    """Log user activity"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # Log activity after successful execution
            if hasattr(g, 'current_user') and g.current_user:
                try:
                    from models.user import AuthLog
                    from extensions import db
                    
                    log_entry = AuthLog(
                        user_id=g.current_user.id,
                        action=activity_type,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', ''),
                        details=json.dumps(details) if details else None,
                        success=True
                    )
                    db.session.add(log_entry)
                    db.session.commit()
                    
                except Exception as e:
                    current_app.logger.error(f"Error logging user activity: {str(e)}")
            
            return result
        return decorated_function
    return decorator


# Global middleware instance
session_middleware = SessionMiddleware()
