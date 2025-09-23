#!/usr/bin/env python3
"""
Rice Mill Management System - Security & Deployment Hardening Script
====================================================================

This script addresses critical deployment blockers identified in the stability analysis:
1. Generate strong SECRET_KEY and JWT_SECRET_KEY
2. Configure production environment settings
3. Set up secure database configuration
4. Disable debug mode for production
5. Configure HTTPS enforcement
6. Set up proper logging and monitoring

Usage:
    python fix_security_deployment.py [--environment production|development]
"""

import os
import secrets
import string
import sys
from pathlib import Path
from datetime import datetime
import json
import hashlib

class SecurityHardening:
    def __init__(self, environment='production'):
        self.environment = environment
        self.backend_dir = Path(__file__).parent
        self.env_file = self.backend_dir / '.env'
        self.env_example = self.backend_dir / '.env.example'
        self.fixes_applied = []
        self.issues_found = []
        
    def generate_strong_key(self, length=64):
        """Generate a cryptographically strong secret key"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def generate_jwt_secret(self, length=128):
        """Generate a strong JWT secret key"""
        return secrets.token_urlsafe(length)
    
    def create_production_env(self):
        """Create a production-ready .env file"""
        try:
            print("[INFO] Creating production-ready environment configuration...")
            
            # Read the example file as template
            if not self.env_example.exists():
                raise FileNotFoundError(f"Template file {self.env_example} not found")
            
            with open(self.env_example, 'r') as f:
                template_content = f.read()
            
            # Generate strong keys
            secret_key = self.generate_strong_key()
            jwt_secret = self.generate_jwt_secret()
            
            # Production configuration replacements
            replacements = {
                'FLASK_ENV=development': 'FLASK_ENV=production',
                'FLASK_DEBUG=True': 'FLASK_DEBUG=False',
                'SECRET_KEY=your-super-secret-key-change-in-production': f'SECRET_KEY={secret_key}',
                'JWT_SECRET_KEY=your-jwt-secret-key-change-in-production': f'JWT_SECRET_KEY={jwt_secret}',
                'LOG_LEVEL=INFO': 'LOG_LEVEL=WARNING',
                'CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000': 'CORS_ORIGINS=https://yourdomain.com',
                'DATABASE_URL=postgresql://rice_mill_user:secure_password@localhost:5432/rice_mill_erp': 
                    'DATABASE_URL=postgresql://rice_mill_user:CHANGE_THIS_PASSWORD@localhost:5432/rice_mill_erp',
                'GOOGLE_AI_API_KEY=your-google-ai-api-key-here': 'GOOGLE_AI_API_KEY=',
                'MAIL_USERNAME=your-email@gmail.com': 'MAIL_USERNAME=',
                'MAIL_PASSWORD=your-app-password': 'MAIL_PASSWORD=',
                'SENTRY_DSN=your-sentry-dsn-here': 'SENTRY_DSN=',
            }
            
            # Apply replacements
            production_content = template_content
            for old, new in replacements.items():
                production_content = production_content.replace(old, new)
            
            # Add production-specific settings
            production_additions = f"""

# =============================================================================
# PRODUCTION SECURITY SETTINGS (Auto-generated {datetime.now().isoformat()})
# =============================================================================
# Session Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# CSRF Protection
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600

# Rate Limiting
RATELIMIT_DEFAULT=500 per hour
RATELIMIT_STORAGE_URL=redis://localhost:6379/3

# Security Headers
FORCE_HTTPS=True
HSTS_MAX_AGE=31536000
CONTENT_SECURITY_POLICY=default-src 'self'

# Database Security
SQLALCHEMY_ECHO=False
SQLALCHEMY_RECORD_QUERIES=False

# Monitoring
HEALTH_CHECK_TOKEN={self.generate_strong_key(32)}
ADMIN_API_TOKEN={self.generate_strong_key(48)}

# =============================================================================
# CRITICAL: CHANGE THESE VALUES BEFORE DEPLOYMENT
# =============================================================================
# 1. Update DATABASE_URL with actual production database credentials
# 2. Set GOOGLE_AI_API_KEY with your actual API key
# 3. Configure MAIL_USERNAME and MAIL_PASSWORD for email notifications
# 4. Set SENTRY_DSN for error tracking
# 5. Update CORS_ORIGINS with your actual domain
# 6. Review all other configuration values
"""
            
            production_content += production_additions
            
            # Write the production .env file
            with open(self.env_file, 'w') as f:
                f.write(production_content)
            
            self.fixes_applied.append({
                'fix_name': 'Production Environment Configuration',
                'description': 'Created secure .env file with strong keys and production settings',
                'details': {
                    'secret_key_length': len(secret_key),
                    'jwt_secret_length': len(jwt_secret),
                    'environment': self.environment,
                    'security_features': [
                        'Strong SECRET_KEY generated',
                        'Strong JWT_SECRET_KEY generated',
                        'Debug mode disabled',
                        'HTTPS enforcement enabled',
                        'Secure session cookies',
                        'CSRF protection enabled',
                        'Rate limiting configured'
                    ]
                }
            })
            
            print(f"[SUCCESS] Production environment file created: {self.env_file}")
            print(f"[KEY] Generated {len(secret_key)}-character SECRET_KEY")
            print(f"[KEY] Generated {len(jwt_secret)}-character JWT_SECRET_KEY")
            
        except Exception as e:
            self.issues_found.append({
                'issue': 'Environment Configuration Creation Failed',
                'error': str(e),
                'fix_required': 'Manual environment setup needed'
            })
            print(f"[ERROR] Error creating environment configuration: {e}")
    
    def create_database_security_script(self):
        """Create database security and backup configuration"""
        try:
            db_security_script = self.backend_dir / 'setup_database_security.py'
            
            script_content = '''#!/usr/bin/env python3
"""
Database Security and Backup Setup Script
=========================================
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def setup_postgresql_security():
    """Configure PostgreSQL security settings"""
    print("[INFO] Setting up PostgreSQL security...")
    
    # Create database user with limited privileges
    commands = [
        "CREATE USER rice_mill_user WITH ENCRYPTED PASSWORD 'CHANGE_THIS_PASSWORD';",
        "CREATE DATABASE rice_mill_erp OWNER rice_mill_user;",
        "GRANT CONNECT ON DATABASE rice_mill_erp TO rice_mill_user;",
        "GRANT USAGE ON SCHEMA public TO rice_mill_user;",
        "GRANT CREATE ON SCHEMA public TO rice_mill_user;",
        "ALTER USER rice_mill_user SET default_transaction_isolation TO 'read committed';",
        "ALTER USER rice_mill_user SET timezone TO 'UTC';"
    ]
    
    print("Execute these commands in PostgreSQL as superuser:")
    for cmd in commands:
        print(f"  {cmd}")
    
    return commands

def setup_backup_strategy():
    """Set up automated database backup"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    backup_script = backup_dir / "backup_database.sh"
    
    backup_content = f"""#!/bin/bash
# Automated Database Backup Script
# Generated on {datetime.now().isoformat()}

BACKUP_DIR="$(dirname "$0")"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="rice_mill_erp"
DB_USER="rice_mill_user"
BACKUP_FILE="$BACKUP_DIR/rice_mill_backup_$TIMESTAMP.sql"

echo "Starting database backup at $(date)"

# Create backup
pg_dump -U $DB_USER -h localhost -d $DB_NAME > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
    
    # Compress backup
    gzip "$BACKUP_FILE"
    echo "Backup compressed: $BACKUP_FILE.gz"
    
    # Remove backups older than 30 days
    find "$BACKUP_DIR" -name "rice_mill_backup_*.sql.gz" -mtime +30 -delete
    echo "Old backups cleaned up"
else
    echo "Backup failed!"
    exit 1
fi

echo "Backup process completed at $(date)"
"""
    
    with open(backup_script, 'w') as f:
        f.write(backup_content)
    
    # Make script executable
    os.chmod(backup_script, 0o755)
    
    print(f"[SUCCESS] Backup script created: {backup_script}")
    print("[INFO] Set up cron job for daily backups:")
    print(f"   0 2 * * * {backup_script.absolute()}")
    
    return backup_script

if __name__ == "__main__":
    print("[INFO] Database Security Setup")
    print("=" * 50)
    
    setup_postgresql_security()
    setup_backup_strategy()
    
    print("\\n[INFO] Next Steps:")
    print("1. Execute the PostgreSQL commands as superuser")
    print("2. Update DATABASE_URL in .env with the actual password")
    print("3. Set up the cron job for automated backups")
    print("4. Test database connection and backup script")
'''
            
            with open(db_security_script, 'w') as f:
                f.write(script_content)
            
            os.chmod(db_security_script, 0o755)
            
            self.fixes_applied.append({
                'fix_name': 'Database Security Script',
                'description': 'Created database security and backup setup script',
                'file': str(db_security_script)
            })
            
            print(f"[SUCCESS] Database security script created: {db_security_script}")
            
        except Exception as e:
            self.issues_found.append({
                'issue': 'Database Security Script Creation Failed',
                'error': str(e)
            })
            print(f"[ERROR] Error creating database security script: {e}")
    
    def create_monitoring_config(self):
        """Create monitoring and health check configuration"""
        try:
            monitoring_script = self.backend_dir / 'setup_monitoring.py'
            
            script_content = '''#!/usr/bin/env python3
"""
Production Monitoring Setup
===========================
"""

import os
import json
from pathlib import Path
from datetime import datetime

def create_health_check_endpoint():
    """Create enhanced health check configuration"""
    
    health_config = {
        "health_checks": {
            "database": {
                "enabled": True,
                "timeout": 5,
                "query": "SELECT 1"
            },
            "redis": {
                "enabled": True,
                "timeout": 3
            },
            "disk_space": {
                "enabled": True,
                "threshold_percent": 85
            },
            "memory": {
                "enabled": True,
                "threshold_percent": 90
            }
        },
        "monitoring": {
            "response_time_threshold": 2000,
            "error_rate_threshold": 0.05,
            "alert_email": "admin@ricemill.com"
        }
    }
    
    config_file = Path("config/monitoring.json")
    config_file.parent.mkdir(exist_ok=True)
    
    with open(config_file, 'w') as f:
        json.dump(health_config, f, indent=2)
    
    print(f"[SUCCESS] Monitoring configuration created: {config_file}")
    return config_file

def setup_log_rotation():
    """Set up log rotation configuration"""
    
    logrotate_config = """# Rice Mill Application Log Rotation
/path/to/rice_mill/backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload rice-mill-backend
    endscript
}
"""
    
    print("[INFO] Log rotation configuration:")
    print(logrotate_config)
    print("Save this to /etc/logrotate.d/rice-mill")
    
    return logrotate_config

if __name__ == "__main__":
    print("[INFO] Setting up Production Monitoring")
    print("=" * 50)
    
    create_health_check_endpoint()
    setup_log_rotation()
    
    print("\\n[INFO] Additional Monitoring Setup:")
    print("1. Configure Sentry for error tracking")
    print("2. Set up Prometheus/Grafana for metrics")
    print("3. Configure email alerts")
    print("4. Set up uptime monitoring")
'''
            
            with open(monitoring_script, 'w') as f:
                f.write(script_content)
            
            os.chmod(monitoring_script, 0o755)
            
            self.fixes_applied.append({
                'fix_name': 'Monitoring Configuration',
                'description': 'Created production monitoring and health check setup',
                'file': str(monitoring_script)
            })
            
            print(f"[SUCCESS] Monitoring setup script created: {monitoring_script}")
            
        except Exception as e:
            self.issues_found.append({
                'issue': 'Monitoring Configuration Failed',
                'error': str(e)
            })
            print(f"[ERROR] Error creating monitoring configuration: {e}")
    
    def create_deployment_checklist(self):
        """Create production deployment checklist"""
        try:
            checklist_file = self.backend_dir / 'PRODUCTION_DEPLOYMENT_CHECKLIST.md'
            
            checklist_content = f'''# Production Deployment Checklist

Generated on: {datetime.now().isoformat()}

## Security Configuration

### Critical Security Items
- [ ] **SECRET_KEY**: Strong secret key generated [SUCCESS]
- [ ] **JWT_SECRET_KEY**: Strong JWT secret generated [SUCCESS]
- [ ] **Database Password**: Change default database password
- [ ] **Debug Mode**: Disabled for production [SUCCESS]
- [ ] **HTTPS**: SSL certificate installed and configured
- [ ] **CORS Origins**: Updated with production domain
- [ ] **Rate Limiting**: Configured and tested

### Environment Variables
- [ ] **DATABASE_URL**: Production database connection string
- [ ] **GOOGLE_AI_API_KEY**: Valid API key for AI services
- [ ] **MAIL_USERNAME/PASSWORD**: Email service credentials
- [ ] **SENTRY_DSN**: Error tracking service configured
- [ ] **REDIS_URL**: Redis server connection

## Database Setup

- [ ] **PostgreSQL**: Production database server installed
- [ ] **Database User**: Limited privilege user created
- [ ] **Database**: Rice mill database created
- [ ] **Migrations**: All database migrations applied
- [ ] **Backup Strategy**: Automated backups configured
- [ ] **Connection Pool**: Database connection pool optimized

## Infrastructure

- [ ] **Web Server**: Nginx/Apache configured
- [ ] **WSGI Server**: Gunicorn/uWSGI configured
- [ ] **Process Manager**: Systemd/Supervisor setup
- [ ] **Firewall**: Only necessary ports open
- [ ] **SSL Certificate**: Valid SSL certificate installed
- [ ] **Log Rotation**: Log rotation configured

## Monitoring & Alerting

- [ ] **Health Checks**: Application health monitoring
- [ ] **Error Tracking**: Sentry error tracking active
- [ ] **Performance Monitoring**: Response time monitoring
- [ ] **Uptime Monitoring**: External uptime checks
- [ ] **Log Aggregation**: Centralized logging setup
- [ ] **Alerts**: Email/SMS alerts configured

## Testing

- [ ] **Unit Tests**: All tests passing
- [ ] **Integration Tests**: API endpoints tested
- [ ] **Load Testing**: Performance under load verified
- [ ] **Security Testing**: Security vulnerabilities scanned
- [ ] **Backup Testing**: Backup and restore tested

## Documentation

- [ ] **API Documentation**: Complete API documentation
- [ ] **User Manual**: User guide completed
- [ ] **Admin Guide**: System administration guide
- [ ] **Troubleshooting**: Common issues documented
- [ ] **Deployment Guide**: Step-by-step deployment instructions

## Deployment Process

- [ ] **CI/CD Pipeline**: Automated deployment pipeline
- [ ] **Blue-Green Deployment**: Zero-downtime deployment strategy
- [ ] **Rollback Plan**: Rollback procedures documented
- [ ] **Database Migrations**: Migration strategy planned
- [ ] **Asset Optimization**: Static assets optimized

## Post-Deployment Verification

- [ ] **Application Start**: Application starts without errors
- [ ] **Database Connection**: Database connectivity verified
- [ ] **API Endpoints**: All endpoints responding correctly
- [ ] **Authentication**: Login/logout functionality working
- [ ] **File Uploads**: File upload functionality tested
- [ ] **Email Notifications**: Email system working
- [ ] **AI Services**: AI features functioning
- [ ] **Performance**: Response times acceptable

## Emergency Procedures

- [ ] **Emergency Contacts**: Contact list prepared
- [ ] **Rollback Procedure**: Quick rollback process documented
- [ ] **Incident Response**: Incident response plan ready
- [ ] **Data Recovery**: Data recovery procedures tested

---

## Support Information

**Technical Support**: [Your Support Email]
**Emergency Contact**: [Emergency Phone Number]
**Documentation**: [Documentation URL]

## Quick Commands

```bash
# Start application
sudo systemctl start rice-mill-backend

# Check status
sudo systemctl status rice-mill-backend

# View logs
sudo journalctl -u rice-mill-backend -f

# Database backup
./backups/backup_database.sh

# Health check
curl https://yourdomain.com/health
```

---
**Note**: This checklist was auto-generated by the security hardening script.
Update it according to your specific deployment requirements.
'''
            
            with open(checklist_file, 'w') as f:
                f.write(checklist_content)
            
            self.fixes_applied.append({
                'fix_name': 'Production Deployment Checklist',
                'description': 'Created comprehensive deployment checklist',
                'file': str(checklist_file)
            })
            
            print(f"[SUCCESS] Deployment checklist created: {checklist_file}")
            
        except Exception as e:
            self.issues_found.append({
                'issue': 'Deployment Checklist Creation Failed',
                'error': str(e)
            })
            print(f"[ERROR] Error creating deployment checklist: {e}")
    
    def run_security_hardening(self):
        """Execute all security hardening steps"""
        print("[SECURITY] Rice Mill Management System - Security Hardening")
        print("=" * 60)
        print(f"Environment: {self.environment}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Execute hardening steps
        self.create_production_env()
        self.create_database_security_script()
        self.create_monitoring_config()
        self.create_deployment_checklist()
        
        # Generate summary report
        self.generate_security_report()
    
    def generate_security_report(self):
        """Generate security hardening report"""
        report = {
            'security_hardening_summary': {
                'timestamp': datetime.now().isoformat(),
                'environment': self.environment,
                'fixes_applied': len(self.fixes_applied),
                'issues_found': len(self.issues_found),
                'status': 'completed' if len(self.issues_found) == 0 else 'completed_with_warnings'
            },
            'fixes_applied': self.fixes_applied,
            'issues_found': self.issues_found,
            'next_steps': [
                'Review and update .env file with production values',
                'Execute database security setup script',
                'Configure monitoring and alerting',
                'Complete production deployment checklist',
                'Test all security configurations'
            ]
        }
        
        report_file = self.backend_dir / 'security_hardening_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n[SUMMARY] Security Hardening Summary")
        print("=" * 40)
        print(f"[OK] Fixes Applied: {len(self.fixes_applied)}")
        print(f"[WARNING] Issues Found: {len(self.issues_found)}")
        print(f"[FILE] Report: {report_file}")
        
        if self.issues_found:
            print("\n[ATTENTION] Issues Requiring Attention:")
            for issue in self.issues_found:
                print(f"  - {issue['issue']}")
        
        print("\n[NEXT] Next Steps:")
        for step in report['next_steps']:
            print(f"  1. {step}")
        
        print(f"\n[COMPLETE] Security hardening completed for {self.environment} environment!")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rice Mill Security Hardening')
    parser.add_argument('--environment', choices=['production', 'development'], 
                       default='production', help='Target environment')
    
    args = parser.parse_args()
    
    hardening = SecurityHardening(args.environment)
    hardening.run_security_hardening()

if __name__ == "__main__":
    main()
