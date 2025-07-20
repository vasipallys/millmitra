from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='operator')
    is_active = db.Column(db.Boolean, default=True)
    force_2fa = db.Column(db.Boolean, default=False)
    
    # AI-enhanced fields
    voice_print_hash = db.Column(db.Text)  # Encrypted voice biometric
    face_encoding = db.Column(db.Text)     # Encrypted face encoding
    typing_pattern = db.Column(db.Text)    # Keystroke dynamics
    preferences = db.Column(db.Text)       # JSON preferences
    
    # Login tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_preferences(self):
        return json.loads(self.preferences) if self.preferences else {}
    
    def set_preferences(self, prefs):
        self.preferences = json.dumps(prefs)
    
    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()

class AuthLog(db.Model):
    __tablename__ = 'auth_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    username_attempted = db.Column(db.String(120))
    success = db.Column(db.Boolean, nullable=False)
    method = db.Column(db.String(50))  # password, voice, biometric
    risk_score = db.Column(db.Float)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    device_fingerprint = db.Column(db.String(255))
    location = db.Column(db.String(100))
    failure_reason = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

