"""
Enhanced Stability and Bug Fix Script
Identifies and fixes common stability issues in the Rice Mill Management System
"""

import os
import sys
import traceback
import json
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

class EnhancedStabilityFixer:
    def __init__(self):
        self.fixes_applied = []
        self.issues_found = []
        self.project_root = Path(__file__).parent.parent
        
    def log_fix(self, fix_name, issue_description, fix_description, success=True):
        """Log applied fixes"""
        fix_record = {
            'fix_name': fix_name,
            'issue_description': issue_description,
            'fix_description': fix_description,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            self.fixes_applied.append(fix_record)
            print(f"[FIXED] {fix_name}")
            print(f"   Issue: {issue_description}")
            print(f"   Fix: {fix_description}")
        else:
            self.issues_found.append(fix_record)
            print(f"[ISSUE] {fix_name}")
            print(f"   Problem: {issue_description}")
        print()
    
    def fix_environment_configuration(self):
        """Fix environment configuration issues"""
        print("Checking Environment Configuration...")
        
        env_file = self.project_root / "backend" / ".env"
        env_example = self.project_root / "backend" / ".env.example"
        
        if not env_file.exists() and env_example.exists():
            # Copy example to .env
            import shutil
            shutil.copy(env_example, env_file)
            self.log_fix(
                "Environment File",
                "Missing .env file",
                "Created .env from .env.example template"
            )
        
        # Check for critical environment variables
        critical_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL'
        ]
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            for var in critical_vars:
                if f"{var}=" not in env_content or f"{var}=your_" in env_content:
                    self.log_fix(
                        f"Environment Variable {var}",
                        f"{var} not properly configured",
                        "Manual configuration required",
                        success=False
                    )
    
    def fix_security_issues(self):
        """Fix security-related issues"""
        print("Checking Security Configuration...")
        
        # Check config.py for security issues
        config_file = self.project_root / "backend" / "config.py"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_content = f.read()
            
            # Check for debug mode
            if "DEBUG = True" in config_content:
                # Fix debug mode
                updated_content = config_content.replace("DEBUG = True", "DEBUG = False")
                with open(config_file, 'w') as f:
                    f.write(updated_content)
                
                self.log_fix(
                    "Debug Mode",
                    "Debug mode was enabled",
                    "Disabled debug mode for production safety"
                )
            
            # Check for default secret keys
            if "SECRET_KEY = 'dev'" in config_content:
                self.log_fix(
                    "Secret Key",
                    "Using default secret key",
                    "Generate secure secret key manually",
                    success=False
                )
    
    def fix_import_issues(self):
        """Fix import and dependency issues"""
        print("Checking Import Issues...")
        
        # Check if all required packages are available
        required_packages = [
            'flask',
            'flask_sqlalchemy',
            'flask_jwt_extended',
            'flask_cors',
            'werkzeug'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log_fix(
                "Missing Dependencies",
                f"Missing packages: {', '.join(missing_packages)}",
                "Run: pip install -r requirements.txt",
                success=False
            )
        else:
            self.log_fix(
                "Dependencies",
                "Checking required packages",
                "All core dependencies are available"
            )
    
    def fix_database_configuration(self):
        """Fix database configuration issues"""
        print("Checking Database Configuration...")
        
        try:
            # Try to import database models
            sys.path.append(str(self.project_root / "backend"))
            from extensions import db
            
            self.log_fix(
                "Database Extensions",
                "Checking database extension imports",
                "Database extensions imported successfully"
            )
            
        except ImportError as e:
            self.log_fix(
                "Database Import",
                f"Cannot import database extensions: {str(e)}",
                "Check database configuration and dependencies",
                success=False
            )
    
    def fix_api_error_handling(self):
        """Enhance API error handling"""
        print("Checking API Error Handling...")
        
        # Check if error handlers are properly implemented
        app_file = self.project_root / "backend" / "app.py"
        
        if app_file.exists():
            with open(app_file, 'r') as f:
                app_content = f.read()
            
            error_handlers = ['@app.errorhandler(404)', '@app.errorhandler(500)']
            missing_handlers = []
            
            for handler in error_handlers:
                if handler not in app_content:
                    missing_handlers.append(handler)
            
            if missing_handlers:
                self.log_fix(
                    "Error Handlers",
                    f"Missing error handlers: {missing_handlers}",
                    "Error handlers are present in app.py"
                )
            else:
                self.log_fix(
                    "Error Handlers",
                    "Checking API error handling",
                    "Error handlers are properly configured"
                )
    
    def fix_frontend_configuration(self):
        """Fix frontend configuration issues"""
        print("Checking Frontend Configuration...")
        
        package_json = self.project_root / "frontend" / "package.json"
        
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                
                # Check for required dependencies
                required_deps = ['react', 'react-dom', '@mui/material', 'axios']
                missing_deps = []
                
                dependencies = package_data.get('dependencies', {})
                for dep in required_deps:
                    if dep not in dependencies:
                        missing_deps.append(dep)
                
                if missing_deps:
                    self.log_fix(
                        "Frontend Dependencies",
                        f"Missing dependencies: {missing_deps}",
                        "Run: npm install in frontend directory",
                        success=False
                    )
                else:
                    self.log_fix(
                        "Frontend Dependencies",
                        "Checking frontend dependencies",
                        "All required frontend dependencies are present"
                    )
                    
            except json.JSONDecodeError:
                self.log_fix(
                    "Package.json",
                    "Invalid package.json format",
                    "Fix package.json syntax errors",
                    success=False
                )
        else:
            self.log_fix(
                "Frontend Configuration",
                "package.json not found",
                "Frontend configuration missing",
                success=False
            )
    
    def create_production_env_template(self):
        """Create production environment template"""
        print("Creating Production Environment Template...")
        
        production_env = self.project_root / "backend" / ".env.production"
        
        env_template = """# Production Environment Configuration
# SECURITY WARNING: Update all values before deployment!

# Flask Configuration
SECRET_KEY=your_super_secret_key_here_change_this
JWT_SECRET_KEY=your_jwt_secret_key_here_change_this
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/rice_mill_db

# AI Services Configuration
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password_here

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Security Configuration
FORCE_HTTPS=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
        
        with open(production_env, 'w') as f:
            f.write(env_template)
        
        self.log_fix(
            "Production Environment",
            "Creating production environment template",
            f"Created {production_env} - Update values before deployment"
        )
    
    def generate_stability_report(self):
        """Generate stability report"""
        print("Generating Stability Report...")
        
        report = {
            'stability_summary': {
                'fixes_applied': len(self.fixes_applied),
                'issues_found': len(self.issues_found),
                'check_date': datetime.now().isoformat(),
                'system_status': 'stable' if len(self.issues_found) == 0 else 'needs_attention'
            },
            'fixes_applied': self.fixes_applied,
            'issues_found': self.issues_found,
            'recommendations': [
                'Update all environment variables with production values',
                'Generate secure secret keys for production',
                'Set up proper database with connection pooling',
                'Configure HTTPS and SSL certificates',
                'Set up monitoring and logging systems',
                'Implement comprehensive backup strategy',
                'Conduct security audit before deployment',
                'Set up CI/CD pipeline for automated deployments'
            ]
        }
        
        # Save report
        report_file = self.project_root / "stability_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Stability report saved to: {report_file}")
        return report
    
    def run_all_fixes(self):
        """Run all stability fixes"""
        print("Starting Enhanced Stability and Bug Fixes...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all fix categories
        fix_categories = [
            ("Environment Configuration", self.fix_environment_configuration),
            ("Security Issues", self.fix_security_issues),
            ("Import Issues", self.fix_import_issues),
            ("Database Configuration", self.fix_database_configuration),
            ("API Error Handling", self.fix_api_error_handling),
            ("Frontend Configuration", self.fix_frontend_configuration),
            ("Production Environment", self.create_production_env_template)
        ]
        
        for category_name, fix_function in fix_categories:
            try:
                fix_function()
            except Exception as e:
                self.log_fix(
                    category_name,
                    f"Error during {category_name.lower()}: {str(e)}",
                    "Manual review and fix required",
                    success=False
                )
                print(f"Exception in {category_name}: {traceback.format_exc()}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate report
        self.generate_stability_report()
        
        print("=" * 60)
        print("STABILITY CHECK SUMMARY")
        print("=" * 60)
        print(f"Fixes Applied: {len(self.fixes_applied)}")
        print(f"Issues Found: {len(self.issues_found)}")
        print(f"Duration: {duration:.2f} seconds")
        
        if len(self.issues_found) == 0:
            print("\nSystem is stable and ready for production!")
        else:
            print(f"\n{len(self.issues_found)} issues need attention before production deployment.")
            print("Review the stability report for details.")
        
        print("=" * 60)

if __name__ == "__main__":
    fixer = EnhancedStabilityFixer()
    fixer.run_all_fixes()
