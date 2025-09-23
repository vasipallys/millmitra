#!/usr/bin/env python3
"""
Production Database Setup Script for Rice Mill ERP
Creates secure database configuration and initializes tables
"""

import os
import sys
import secrets
from datetime import datetime

def generate_secure_database_config():
    """Generate secure database configuration"""
    
    print("🔧 Setting up Production Database Configuration...")
    
    # Generate secure database credentials
    db_password = secrets.token_urlsafe(16)
    
    # Create production database URL (using environment or default)
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'rice_mill_erp_prod')
    db_user = os.getenv('DB_USER', 'rice_mill_user')
    
    production_db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print(f"✅ Generated secure database configuration:")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    print(f"   Host: {db_host}:{db_port}")
    print(f"   Password: {db_password}")
    
    return production_db_url, db_password

def create_production_env():
    """Create production environment file"""
    
    print("\n🔐 Creating production environment configuration...")
    
    # Generate secure keys
    secret_key = secrets.token_urlsafe(32)
    jwt_secret = secrets.token_urlsafe(32)
    
    # Get database config
    db_url, db_password = generate_secure_database_config()
    
    production_env = f"""# =============================================================================
# Rice Mill ERP - Production Environment Configuration
# Generated on: {datetime.now().isoformat()}
# =============================================================================

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=False

# Application URLs
BACKEND_URL=http://localhost:5000
FRONTEND_URL=http://localhost:3000
AI_SERVICES_URL=http://localhost:8000

# =============================================================================
# SECURITY CONFIGURATION (PRODUCTION)
# =============================================================================
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}

# JWT Token Expiration
JWT_ACCESS_TOKEN_EXPIRES_HOURS=8
JWT_REFRESH_TOKEN_EXPIRES_DAYS=7

# Password Security
BCRYPT_LOG_ROUNDS=14

# =============================================================================
# DATABASE CONFIGURATION (PRODUCTION)
# =============================================================================
DATABASE_URL={db_url}

# Database Connection Pool Settings (Production Optimized)
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_POOL_TIMEOUT=30
SQLALCHEMY_POOL_RECYCLE=3600
SQLALCHEMY_MAX_OVERFLOW=10
SQLALCHEMY_POOL_PRE_PING=True

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_DB=0
REDIS_SESSION_DB=1
REDIS_CELERY_DB=2

# =============================================================================
# PRODUCTION SECURITY SETTINGS
# =============================================================================
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict
WTF_CSRF_ENABLED=True

# =============================================================================
# LOGGING CONFIGURATION (PRODUCTION)
# =============================================================================
LOG_LEVEL=WARNING
LOG_FILE=logs/app.log
LOG_MAX_BYTES=52428800  # 50MB
LOG_BACKUP_COUNT=10

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================
CACHE_TYPE=redis
CACHE_DEFAULT_TIMEOUT=600  # 10 minutes
RATELIMIT_DEFAULT=500 per hour
RATELIMIT_LOGIN_ATTEMPTS=3 per minute

# =============================================================================
# MONITORING & ALERTING
# =============================================================================
HEALTH_CHECK_ENABLED=True
PERFORMANCE_MONITORING_ENABLED=True
SENTRY_ENVIRONMENT=production

# =============================================================================
# BACKUP CONFIGURATION
# =============================================================================
AUTO_BACKUP_ENABLED=True
BACKUP_FREQUENCY=daily
BACKUP_RETENTION_DAYS=90
"""
    
    # Write production environment file
    with open('backend/.env.production', 'w') as f:
        f.write(production_env)
    
    print("✅ Created backend/.env.production")
    
    # Create database setup instructions
    db_setup_sql = f"""-- Rice Mill ERP Production Database Setup
-- Run these commands as PostgreSQL superuser

-- Create database user
CREATE USER {os.getenv('DB_USER', 'rice_mill_user')} WITH PASSWORD '{db_password}';

-- Create database
CREATE DATABASE {os.getenv('DB_NAME', 'rice_mill_erp_prod')} OWNER {os.getenv('DB_USER', 'rice_mill_user')};

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE {os.getenv('DB_NAME', 'rice_mill_erp_prod')} TO {os.getenv('DB_USER', 'rice_mill_user')};

-- Connect to the database and grant schema permissions
\\c {os.getenv('DB_NAME', 'rice_mill_erp_prod')};
GRANT ALL ON SCHEMA public TO {os.getenv('DB_USER', 'rice_mill_user')};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {os.getenv('DB_USER', 'rice_mill_user')};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {os.getenv('DB_USER', 'rice_mill_user')};

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {os.getenv('DB_USER', 'rice_mill_user')};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {os.getenv('DB_USER', 'rice_mill_user')};
"""
    
    with open('setup_production_database.sql', 'w') as f:
        f.write(db_setup_sql)
    
    print("✅ Created setup_production_database.sql")
    
    return secret_key, jwt_secret, db_password

def initialize_database():
    """Initialize database tables"""
    
    print("\n🗄️ Initializing database tables...")
    
    try:
        # Import Flask app
        sys.path.append('backend')
        from app import create_app
        from extensions import db
        
        # Create app with production config
        app = create_app()
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create default admin user
            from models.user import User
            from werkzeug.security import generate_password_hash
            
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@ricemill.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin',
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Default admin user created (username: admin, password: admin123)")
            else:
                print("ℹ️ Admin user already exists")
                
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    return True

def create_startup_script():
    """Create production startup script"""
    
    startup_script = """#!/bin/bash
# Rice Mill ERP Production Startup Script

echo "🚀 Starting Rice Mill ERP Production Server..."

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️ Redis not running. Starting Redis..."
    redis-server --daemonize yes
fi

# Check if PostgreSQL is running
if ! pgrep -x "postgres" > /dev/null; then
    echo "⚠️ PostgreSQL not running. Please start PostgreSQL service."
    exit 1
fi

# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Start backend server
cd backend
echo "🔧 Starting backend server..."
gunicorn -w 4 -b 0.0.0.0:5000 app:app --timeout 120 --keep-alive 2 --max-requests 1000 &

# Start AI services
cd ../ai-services
echo "🤖 Starting AI services..."
python main.py &

# Start frontend (for development - use nginx in production)
cd ../frontend
echo "🎨 Starting frontend..."
npm run build
npm run preview &

echo "✅ All services started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:5000"
echo "🤖 AI Services: http://localhost:8000"

# Keep script running
wait
"""
    
    with open('start_production.sh', 'w') as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod('start_production.sh', 0o755)
    print("✅ Created start_production.sh")

def main():
    """Main setup function"""
    
    print("🎯 Rice Mill ERP - Production Setup")
    print("=" * 50)
    
    # Create production configuration
    secret_key, jwt_secret, db_password = create_production_env()
    
    # Initialize database
    if initialize_database():
        print("\n✅ Database initialization completed")
    else:
        print("\n❌ Database initialization failed")
        return False
    
    # Create startup script
    create_startup_script()
    
    print("\n🎉 Production Setup Complete!")
    print("=" * 50)
    print("📋 Next Steps:")
    print("1. Run setup_production_database.sql in PostgreSQL")
    print("2. Copy backend/.env.production to backend/.env")
    print("3. Install production dependencies: pip install gunicorn")
    print("4. Run: ./start_production.sh")
    print("\n🔐 Important Security Notes:")
    print(f"- Database password: {db_password}")
    print("- Change default admin password after first login")
    print("- Set up SSL/HTTPS for production deployment")
    print("- Configure firewall and security groups")
    
    return True

if __name__ == "__main__":
    main()