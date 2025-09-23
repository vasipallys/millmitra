"""
Simplified Production Setup Script
Sets up production environment without Unicode issues
"""

import os
import secrets
import string
from pathlib import Path
from datetime import datetime

def generate_secure_key(length=64):
    """Generate a secure random key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=128):
    """Generate a secure JWT secret"""
    return secrets.token_urlsafe(length)

def setup_production_environment():
    """Set up production environment configuration"""
    print("Setting up Production Environment...")
    
    project_root = Path(__file__).parent.parent
    backend_path = Path(__file__).parent
    
    # Generate secure keys
    secret_key = generate_secure_key()
    jwt_secret = generate_jwt_secret()
    
    # Create production environment content
    production_env_content = f"""# Production Environment Configuration
# Generated on: {datetime.now().isoformat()}
# SECURITY WARNING: Keep these values secure!

# Flask Configuration
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_APP=app.py

# Database Configuration
DATABASE_URL=postgresql://rice_mill_user:secure_password@localhost:5432/rice_mill_production

# AI Services Configuration
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# AI Service URLs
AI_SERVICE_URL=http://127.0.0.1:8000
AI_SERVICE_TIMEOUT=30

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@company.com
MAIL_PASSWORD=your_app_password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=52428800

# Security Configuration
FORCE_HTTPS=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/rice_mill_production.log
"""
    
    # Write production environment file
    prod_env_file = backend_path / ".env.production"
    with open(prod_env_file, 'w', encoding='utf-8') as f:
        f.write(production_env_content)
    
    print(f"Created production environment: {prod_env_file}")
    
    # Create development environment if missing
    dev_env_file = backend_path / ".env"
    if not dev_env_file.exists():
        dev_env_content = f"""# Development Environment Configuration
SECRET_KEY={generate_secure_key(32)}
JWT_SECRET_KEY={generate_jwt_secret(64)}
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_APP=app.py
DATABASE_URL=sqlite:///rice_mill_dev.db
AI_SERVICE_URL=http://127.0.0.1:8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=DEBUG
"""
        
        with open(dev_env_file, 'w', encoding='utf-8') as f:
            f.write(dev_env_content)
        
        print(f"Created development environment: {dev_env_file}")
    
    return {
        'secret_key': secret_key,
        'jwt_secret': jwt_secret,
        'production_file': str(prod_env_file)
    }

def create_startup_script():
    """Create startup script for AI services"""
    print("Creating AI Services Startup Script...")
    
    project_root = Path(__file__).parent.parent
    
    # Create startup script for Windows
    startup_script = """@echo off
echo Starting Rice Mill Management System...

echo Starting AI Services...
cd ai-services
start "AI Services" python main.py
cd ..

echo Waiting for AI services to start...
timeout /t 5

echo Starting Backend API...
cd backend
start "Backend API" python app.py
cd ..

echo Starting Frontend...
cd frontend
start "Frontend" npm run dev

echo All services started!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo AI Services: http://localhost:8000
pause
"""
    
    startup_file = project_root / "start_system.bat"
    with open(startup_file, 'w') as f:
        f.write(startup_script)
    
    print(f"Created startup script: {startup_file}")
    
    # Create Linux/Mac startup script
    startup_script_unix = """#!/bin/bash
echo "Starting Rice Mill Management System..."

echo "Starting AI Services..."
cd ai-services
python main.py &
AI_PID=$!
cd ..

echo "Waiting for AI services to start..."
sleep 5

echo "Starting Backend API..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo "All services started!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo "AI Services: http://localhost:8000"
echo ""
echo "To stop all services, run: kill $AI_PID $BACKEND_PID $FRONTEND_PID"
"""
    
    startup_file_unix = project_root / "start_system.sh"
    with open(startup_file_unix, 'w') as f:
        f.write(startup_script_unix)
    
    # Make executable
    os.chmod(startup_file_unix, 0o755)
    
    print(f"Created Unix startup script: {startup_file_unix}")

def main():
    """Main setup function"""
    print("=" * 50)
    print("Rice Mill Management System - Production Setup")
    print("=" * 50)
    
    try:
        # Setup environment
        env_result = setup_production_environment()
        
        # Create startup scripts
        create_startup_script()
        
        print("=" * 50)
        print("PRODUCTION SETUP COMPLETE")
        print("=" * 50)
        print("Next Steps:")
        print("1. Update .env.production with your actual values")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start AI services: cd ai-services && python main.py")
        print("4. Start backend: python app.py")
        print("5. Start frontend: cd frontend && npm run dev")
        print("")
        print("Or use the startup scripts:")
        print("Windows: start_system.bat")
        print("Linux/Mac: ./start_system.sh")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"Error during setup: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("Setup completed successfully!")
    else:
        print("Setup failed!")
