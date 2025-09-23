"""
Production Configuration Generator
Generates secure production environment variables and configurations
"""

import os
import secrets
import string
from pathlib import Path
from datetime import datetime

class ProductionConfigGenerator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_path = self.project_root / "backend"
        
    def generate_secure_key(self, length=64):
        """Generate a secure random key"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_jwt_secret(self, length=128):
        """Generate a secure JWT secret"""
        return secrets.token_urlsafe(length)
    
    def create_production_env(self):
        """Create production environment file with secure defaults"""
        print("🔐 Generating Production Environment Configuration...")
        
        # Generate secure keys
        secret_key = self.generate_secure_key()
        jwt_secret = self.generate_jwt_secret()
        
        # Create production environment content
        production_env_content = f"""# Production Environment Configuration
# Generated on: {datetime.now().isoformat()}
# SECURITY WARNING: Keep these values secure and never commit to version control!

# Flask Configuration
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_APP=app.py

# Database Configuration
# Update with your production database credentials
DATABASE_URL=postgresql://rice_mill_user:secure_password@localhost:5432/rice_mill_production
# Alternative MySQL: mysql+pymysql://user:password@localhost:3306/rice_mill_production

# AI Services Configuration
# Get these from your respective AI service providers
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# AI Service URLs
AI_SERVICE_URL=http://127.0.0.1:8000
AI_SERVICE_TIMEOUT=30

# Email Configuration (for notifications and 2FA)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your_email@company.com
MAIL_PASSWORD=your_app_specific_password
MAIL_DEFAULT_SENDER=noreply@company.com

# Redis Configuration (for caching and sessions)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_redis_password

# File Upload Configuration
UPLOAD_FOLDER=uploads
TEMP_FOLDER=temp
MAX_CONTENT_LENGTH=52428800  # 50MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf,csv,xlsx

# Security Configuration
FORCE_HTTPS=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=28800  # 8 hours

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CORS_SUPPORTS_CREDENTIALS=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/rice_mill_production.log
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Performance Configuration
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_POOL_TIMEOUT=30
SQLALCHEMY_POOL_RECYCLE=3600
SQLALCHEMY_MAX_OVERFLOW=30

# Monitoring Configuration
SENTRY_DSN=your_sentry_dsn_here
MONITORING_ENABLED=True

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_DEFAULT=1000 per hour
RATE_LIMIT_STORAGE_URL=redis://localhost:6379/1

# SSL/TLS Configuration
SSL_CERT_PATH=/path/to/ssl/cert.pem
SSL_KEY_PATH=/path/to/ssl/private.key
SSL_CA_BUNDLE=/path/to/ssl/ca-bundle.crt
"""
        
        # Write to production environment file
        prod_env_file = self.backend_path / ".env.production"
        with open(prod_env_file, 'w') as f:
            f.write(production_env_content)
        
        print(f"✅ Production environment created: {prod_env_file}")
        
        # Create development environment if it doesn't exist
        dev_env_file = self.backend_path / ".env"
        if not dev_env_file.exists():
            dev_env_content = f"""# Development Environment Configuration
# Generated on: {datetime.now().isoformat()}

# Flask Configuration
SECRET_KEY={self.generate_secure_key(32)}
JWT_SECRET_KEY={self.generate_jwt_secret(64)}
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_APP=app.py

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///rice_mill_dev.db

# AI Services Configuration (use test keys)
OPENAI_API_KEY=test_key
GOOGLE_API_KEY=test_key
GEMINI_API_KEY=test_key

# AI Service URLs
AI_SERVICE_URL=http://127.0.0.1:8000
AI_SERVICE_TIMEOUT=30

# Email Configuration (disabled for development)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USERNAME=test@localhost
MAIL_PASSWORD=test

# File Upload Configuration
UPLOAD_FOLDER=uploads
TEMP_FOLDER=temp
MAX_CONTENT_LENGTH=52428800

# Security Configuration (relaxed for development)
FORCE_HTTPS=False
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True

# CORS Configuration (allow all for development)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FILE=logs/rice_mill_dev.log
"""
            
            with open(dev_env_file, 'w') as f:
                f.write(dev_env_content)
            
            print(f"✅ Development environment created: {dev_env_file}")
        
        return {
            'secret_key': secret_key,
            'jwt_secret': jwt_secret,
            'production_file': str(prod_env_file),
            'development_file': str(dev_env_file)
        }
    
    def create_docker_configs(self):
        """Create Docker configuration files for production deployment"""
        print("🐳 Creating Docker Configuration...")
        
        # Docker Compose for production
        docker_compose_content = """version: '3.8'

services:
  # Rice Mill Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://rice_mill_user:${DB_PASSWORD}@db:5432/rice_mill_production
    depends_on:
      - db
      - redis
      - ai-services
    volumes:
      - ./backend/uploads:/app/uploads
      - ./backend/logs:/app/logs
    restart: unless-stopped
    networks:
      - rice_mill_network

  # AI Services
  ai-services:
    build:
      context: ./ai-services
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./ai-services/models:/app/models
    restart: unless-stopped
    networks:
      - rice_mill_network

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    volumes:
      - ./ssl:/etc/ssl/certs
    restart: unless-stopped
    networks:
      - rice_mill_network

  # PostgreSQL Database
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=rice_mill_production
      - POSTGRES_USER=rice_mill_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - rice_mill_network

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - rice_mill_network

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - rice_mill_network

volumes:
  postgres_data:
  redis_data:

networks:
  rice_mill_network:
    driver: bridge
"""
        
        docker_compose_file = self.project_root / "docker-compose.production.yml"
        with open(docker_compose_file, 'w') as f:
            f.write(docker_compose_content)
        
        print(f"✅ Docker Compose created: {docker_compose_file}")
        
        # Create environment file for Docker
        docker_env_content = """# Docker Environment Variables
# Copy this to .env and update with your values

# Database
DB_PASSWORD=your_secure_database_password

# Redis
REDIS_PASSWORD=your_secure_redis_password

# AI API Keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key

# Domain Configuration
DOMAIN=yourdomain.com
EMAIL=admin@yourdomain.com
"""
        
        docker_env_file = self.project_root / ".env.docker"
        with open(docker_env_file, 'w') as f:
            f.write(docker_env_content)
        
        print(f"✅ Docker environment template created: {docker_env_file}")
    
    def create_nginx_config(self):
        """Create Nginx configuration for production"""
        print("🌐 Creating Nginx Configuration...")
        
        nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }

    upstream ai_services {
        server ai-services:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/certs/private.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Frontend (React App)
        location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers
            add_header Access-Control-Allow-Origin "https://yourdomain.com";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With";
        }

        # AI Services
        location /ai/ {
            limit_req zone=api burst=10 nodelay;
            
            proxy_pass http://ai_services/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Authentication endpoints (stricter rate limiting)
        location /api/auth/login {
            limit_req zone=login burst=5 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files with caching
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            proxy_pass http://frontend;
        }

        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://backend/api/health;
        }
    }
}
"""
        
        nginx_file = self.project_root / "nginx.conf"
        with open(nginx_file, 'w') as f:
            f.write(nginx_config)
        
        print(f"✅ Nginx configuration created: {nginx_file}")
    
    def create_ssl_setup_script(self):
        """Create SSL certificate setup script"""
        print("🔒 Creating SSL Setup Script...")
        
        ssl_script = """#!/bin/bash
# SSL Certificate Setup Script for Rice Mill Management System

echo "🔒 Setting up SSL certificates..."

# Create SSL directory
mkdir -p ssl

# Option 1: Let's Encrypt (Recommended for production)
echo "Setting up Let's Encrypt certificates..."
echo "Run the following commands on your server:"
echo ""
echo "# Install certbot"
echo "sudo apt-get update"
echo "sudo apt-get install certbot python3-certbot-nginx"
echo ""
echo "# Get SSL certificate"
echo "sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com"
echo ""
echo "# Auto-renewal setup"
echo "sudo crontab -e"
echo "# Add this line: 0 12 * * * /usr/bin/certbot renew --quiet"

# Option 2: Self-signed certificates (for testing)
echo ""
echo "For testing with self-signed certificates:"
echo "openssl req -x509 -newkey rsa:4096 -keyout ssl/private.key -out ssl/cert.pem -days 365 -nodes"

echo ""
echo "✅ SSL setup instructions created!"
echo "Update nginx.conf with your actual domain name before deployment."
"""
        
        ssl_script_file = self.project_root / "setup_ssl.sh"
        with open(ssl_script_file, 'w') as f:
            f.write(ssl_script)
        
        # Make script executable
        os.chmod(ssl_script_file, 0o755)
        
        print(f"✅ SSL setup script created: {ssl_script_file}")
    
    def run_all_configurations(self):
        """Run all production configuration tasks"""
        print("🚀 Starting Production Configuration Setup...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Generate environment configurations
            env_result = self.create_production_env()
            
            # Create Docker configurations
            self.create_docker_configs()
            
            # Create Nginx configuration
            self.create_nginx_config()
            
            # Create SSL setup script
            self.create_ssl_setup_script()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("=" * 60)
            print("✅ PRODUCTION CONFIGURATION COMPLETE")
            print("=" * 60)
            print(f"⏱️  Setup Duration: {duration:.2f} seconds")
            print()
            print("📋 Next Steps:")
            print("1. Update .env.production with your actual values")
            print("2. Configure your domain in nginx.conf")
            print("3. Set up SSL certificates using setup_ssl.sh")
            print("4. Update .env.docker for Docker deployment")
            print("5. Start services: docker-compose -f docker-compose.production.yml up -d")
            print()
            print("🔐 Security Notes:")
            print("- Generated secure secret keys")
            print("- HTTPS enforced in production")
            print("- Rate limiting configured")
            print("- Security headers added")
            print("=" * 60)
            
            return {
                'success': True,
                'env_config': env_result,
                'duration': duration
            }
            
        except Exception as e:
            print(f"❌ Error during configuration: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

if __name__ == "__main__":
    generator = ProductionConfigGenerator()
    result = generator.run_all_configurations()
    
    if result['success']:
        print("\n🎉 Production configuration setup completed successfully!")
    else:
        print(f"\n❌ Configuration failed: {result['error']}")
