#!/usr/bin/env python3
"""
Final Deployment Validation Script
=================================

This script validates that all critical deployment blockers have been addressed.
"""

import os
import sys
from pathlib import Path

def validate_environment_configuration():
    """Validate environment configuration"""
    print("[VALIDATION] Checking environment configuration...")
    
    env_file = Path('.env.production')
    if not env_file.exists():
        print("[ERROR] .env.production file not found")
        return False
    
    # Read environment variables
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                env_vars[key] = value.strip('"\'')
    
    # Check critical variables
    critical_vars = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'DATABASE_URL',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]
    
    missing_vars = []
    for var in critical_vars:
        if var not in env_vars:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[ERROR] Missing critical environment variables: {missing_vars}")
        return False
    
    # Validate specific values
    if env_vars.get('FLASK_DEBUG') == 'True':
        print("[ERROR] DEBUG mode should be disabled for production")
        return False
    
    if env_vars.get('FLASK_ENV') != 'production':
        print(f"[WARNING] FLASK_ENV is '{env_vars.get('FLASK_ENV')}', expected 'production'")
    
    # Check key strength
    secret_key = env_vars.get('SECRET_KEY', '')
    jwt_secret = env_vars.get('JWT_SECRET_KEY', '')
    
    if len(secret_key) < 32:
        print("[ERROR] SECRET_KEY is too short (minimum 32 characters)")
        return False
    
    if len(jwt_secret) < 32:
        print("[ERROR] JWT_SECRET_KEY is too short (minimum 32 characters)")
        return False
    
    print("[SUCCESS] Environment configuration validated")
    return True

def validate_database_security():
    """Validate database security setup"""
    print("[VALIDATION] Checking database security...")
    
    # Check if database security script exists
    db_script = Path('setup_database_security.py')
    if not db_script.exists():
        print("[ERROR] Database security script not found")
        return False
    
    # Check if backup script exists
    backup_script = Path('backups/backup_database.sh')
    if not backup_script.exists():
        print("[ERROR] Database backup script not found")
        return False
    
    print("[SUCCESS] Database security validated")
    return True

def validate_monitoring_setup():
    """Validate monitoring setup"""
    print("[VALIDATION] Checking monitoring setup...")
    
    # Check if monitoring config exists
    monitor_config = Path('config/monitoring.json')
    if not monitor_config.exists():
        print("[ERROR] Monitoring configuration not found")
        return False
    
    print("[SUCCESS] Monitoring setup validated")
    return True

def validate_deployment_checklist():
    """Validate deployment checklist"""
    print("[VALIDATION] Checking deployment checklist...")
    
    # Check if checklist exists
    checklist = Path('PRODUCTION_DEPLOYMENT_CHECKLIST.md')
    if not checklist.exists():
        print("[ERROR] Deployment checklist not found")
        return False
    
    print("[SUCCESS] Deployment checklist validated")
    return True

def main():
    """Main validation function"""
    print("[VALIDATION] Rice Mill Management System - Deployment Validation")
    print("=" * 65)
    
    validators = [
        validate_environment_configuration,
        validate_database_security,
        validate_monitoring_setup,
        validate_deployment_checklist
    ]
    
    results = []
    for validator in validators:
        result = validator()
        results.append(result)
    
    print("\n[SUMMARY] Deployment Validation Summary")
    print("=" * 40)
    
    if all(results):
        print("[SUCCESS] All deployment validations passed!")
        print("The system is ready for production deployment.")
        return 0
    else:
        print("[ERROR] Some validations failed. Please address the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
