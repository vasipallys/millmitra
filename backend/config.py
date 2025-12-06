import os
from datetime import timedelta
import secrets

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # Database configuration - PostgreSQL preferred, SQLite fallback
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///rice_mill_erp.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 10
    }

    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or secrets.token_hex(32)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL') or None
    
    # Celery configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # File upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # AI service configuration
    GOOGLE_AI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')
    AI_SERVICES_URL = os.environ.get('AI_SERVICES_URL') or 'http://localhost:8000'
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    
    # Security configuration
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # Cache configuration
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Session configuration
    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'redis')
    SESSION_REDIS_URL = os.environ.get('SESSION_REDIS_URL', 'redis://localhost:6379/1')
    SESSION_PERMANENT = os.environ.get('SESSION_PERMANENT', 'False').lower() == 'true'
    SESSION_USE_SIGNER = os.environ.get('SESSION_USE_SIGNER', 'True').lower() == 'true'
    SESSION_KEY_PREFIX = os.environ.get('SESSION_KEY_PREFIX', 'rice_mill_session:')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_NAME = 'rice_mill_session'
    SESSION_COOKIE_DOMAIN = None  # Set to your domain in production

    # Session timeout settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 24)))
    SESSION_REFRESH_EACH_REQUEST = True
    
    # Business configuration
    COMPANY_NAME = "Rice Mill ERP"
    COMPANY_ADDRESS = "Your Company Address"
    COMPANY_PHONE = "+91-XXXXXXXXXX"
    COMPANY_EMAIL = "info@ricemill.com"
    
    # Currency and locale
    DEFAULT_CURRENCY = "INR"
    DEFAULT_LOCALE = "en_IN"
    TIMEZONE = "Asia/Kolkata"
    
    # Quality standards
    QUALITY_STANDARDS = {
        'moisture_content': {'min': 12.0, 'max': 14.5},
        'foreign_matter': {'max': 1.0},
        'broken_grains': {'max': 5.0},
        'chalky_grains': {'max': 6.0}
    }
    
    # Production defaults
    DEFAULT_BATCH_SIZE = 1000  # kg
    DEFAULT_PROCESSING_TIME = 8  # hours
    
    # Inventory thresholds
    LOW_STOCK_THRESHOLD = 100  # kg
    REORDER_POINT_DAYS = 7
    
    # Financial settings
    TAX_RATE = 0.18  # 18% GST
    PAYMENT_TERMS_DAYS = 30
    
    # Compliance settings
    AUDIT_RETENTION_DAYS = 2555  # 7 years
    DOCUMENT_RETENTION_DAYS = 1825  # 5 years

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging
    LOG_LEVEL = 'WARNING'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

