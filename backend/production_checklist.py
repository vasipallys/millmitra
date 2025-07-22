"""
Production Deployment Checklist
Comprehensive checklist for production deployment readiness
"""

import os
import json
from datetime import datetime

class ProductionChecker:
    def __init__(self):
        self.checklist_items = []
        self.critical_issues = []
        self.warnings = []
        
    def log_check(self, item_name, status, description, is_critical=False):
        """Log checklist item"""
        item = {
            'item': item_name,
            'status': status,  # 'pass', 'fail', 'warning'
            'description': description,
            'is_critical': is_critical,
            'checked_at': datetime.now().isoformat()
        }
        
        self.checklist_items.append(item)
        
        if status == 'fail' and is_critical:
            self.critical_issues.append(item)
        elif status == 'warning':
            self.warnings.append(item)
        
        status_icon = "✅" if status == 'pass' else "❌" if status == 'fail' else "⚠️"
        critical_marker = " [CRITICAL]" if is_critical else ""
        print(f"{status_icon} {item_name}: {description}{critical_marker}")
    
    def check_environment_variables(self):
        """Check required environment variables"""
        print("🔍 Checking Environment Variables...")
        
        required_vars = [
            ('SECRET_KEY', True, 'Flask secret key for session security'),
            ('DATABASE_URL', True, 'Database connection string'),
            ('JWT_SECRET_KEY', True, 'JWT token signing key'),
            ('FLASK_ENV', False, 'Flask environment setting'),
            ('MAIL_SERVER', False, 'Email server configuration'),
            ('REDIS_URL', False, 'Redis cache server URL')
        ]
        
        for var_name, is_critical, description in required_vars:
            value = os.environ.get(var_name)
            
            if value:
                if var_name == 'SECRET_KEY' and value == 'dev':
                    self.log_check(f"ENV {var_name}", 'fail', 
                                 f"{description} - Using default value", is_critical)
                elif var_name == 'FLASK_ENV' and value == 'development':
                    self.log_check(f"ENV {var_name}", 'warning', 
                                 f"{description} - Set to development mode")
                else:
                    self.log_check(f"ENV {var_name}", 'pass', 
                                 f"{description} - Configured")
            else:
                status = 'fail' if is_critical else 'warning'
                self.log_check(f"ENV {var_name}", status, 
                             f"{description} - Not set", is_critical)
    
    def check_security_configuration(self):
        """Check security configuration"""
        print("\n🔍 Checking Security Configuration...")
        
        # Check debug mode
        debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        if debug_mode:
            self.log_check("Debug Mode", 'fail', 
                         "Debug mode is enabled - disable for production", True)
        else:
            self.log_check("Debug Mode", 'pass', "Debug mode is disabled")
        
        # Check secret keys
        secret_key = os.environ.get('SECRET_KEY', 'dev')
        if secret_key == 'dev' or len(secret_key) < 32:
            self.log_check("Secret Key Strength", 'fail', 
                         "Weak or default secret key", True)
        else:
            self.log_check("Secret Key Strength", 'pass', 
                         "Strong secret key configured")
        
        # Check HTTPS configuration
        force_https = os.environ.get('FORCE_HTTPS', 'False').lower() == 'true'
        if not force_https:
            self.log_check("HTTPS Enforcement", 'warning', 
                         "HTTPS not enforced - recommended for production")
        else:
            self.log_check("HTTPS Enforcement", 'pass', "HTTPS enforcement enabled")
    
    def check_database_configuration(self):
        """Check database configuration"""
        print("\n🔍 Checking Database Configuration...")
        
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            self.log_check("Database URL", 'fail', 
                         "Database URL not configured", True)
        elif 'sqlite' in db_url.lower():
            self.log_check("Database Type", 'warning', 
                         "Using SQLite - consider PostgreSQL for production")
        else:
            self.log_check("Database Configuration", 'pass', 
                         "Production database configured")
        
        # Check database backup strategy
        backup_enabled = os.environ.get('DB_BACKUP_ENABLED', 'False').lower() == 'true'
        if not backup_enabled:
            self.log_check("Database Backup", 'warning', 
                         "Database backup not configured")
        else:
            self.log_check("Database Backup", 'pass', "Database backup enabled")
    
    def check_file_structure(self):
        """Check critical file structure"""
        print("\n🔍 Checking File Structure...")
        
        critical_files = [
            'app.py',
            'models.py',
            'extensions.py',
            'requirements.txt'
        ]
        
        critical_directories = [
            'services',
            'routes',
            'uploads',
            'exports',
            'logs'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                self.log_check(f"File {file_path}", 'pass', f"Critical file exists")
            else:
                self.log_check(f"File {file_path}", 'fail', 
                             f"Critical file missing", True)
        
        for dir_path in critical_directories:
            if os.path.exists(dir_path):
                self.log_check(f"Directory {dir_path}", 'pass', f"Required directory exists")
            else:
                self.log_check(f"Directory {dir_path}", 'warning', 
                             f"Directory missing - will be created")
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    self.log_check(f"Create {dir_path}", 'pass', f"Directory created")
                except Exception as e:
                    self.log_check(f"Create {dir_path}", 'fail', 
                                 f"Failed to create directory: {str(e)}")
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print("\n🔍 Checking Dependencies...")
        
        critical_packages = [
            'flask',
            'flask-sqlalchemy',
            'flask-jwt-extended',
            'werkzeug',
            'numpy'
        ]
        
        for package in critical_packages:
            try:
                __import__(package.replace('-', '_'))
                self.log_check(f"Package {package}", 'pass', f"Package available")
            except ImportError:
                self.log_check(f"Package {package}", 'fail', 
                             f"Critical package missing", True)
    
    def check_performance_settings(self):
        """Check performance-related settings"""
        print("\n🔍 Checking Performance Settings...")
        
        # Check worker processes
        workers = os.environ.get('WEB_CONCURRENCY', '1')
        try:
            worker_count = int(workers)
            if worker_count < 2:
                self.log_check("Worker Processes", 'warning', 
                             "Single worker - consider multiple workers for production")
            else:
                self.log_check("Worker Processes", 'pass', 
                             f"{worker_count} workers configured")
        except ValueError:
            self.log_check("Worker Processes", 'warning', 
                         "Invalid worker configuration")
        
        # Check caching
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            self.log_check("Caching", 'warning', 
                         "Redis cache not configured - performance may be impacted")
        else:
            self.log_check("Caching", 'pass', "Redis cache configured")
    
    def check_monitoring_logging(self):
        """Check monitoring and logging setup"""
        print("\n🔍 Checking Monitoring & Logging...")
        
        # Check logging configuration
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
        if log_level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            self.log_check("Log Level", 'pass', f"Log level set to {log_level}")
        else:
            self.log_check("Log Level", 'warning', "Invalid log level")
        
        # Check log directory
        if os.path.exists('logs'):
            self.log_check("Log Directory", 'pass', "Log directory exists")
        else:
            self.log_check("Log Directory", 'warning', "Log directory missing")
        
        # Check error tracking
        sentry_dsn = os.environ.get('SENTRY_DSN')
        if not sentry_dsn:
            self.log_check("Error Tracking", 'warning', 
                         "Sentry error tracking not configured")
        else:
            self.log_check("Error Tracking", 'pass', "Sentry error tracking enabled")
    
    def check_api_documentation(self):
        """Check API documentation"""
        print("\n🔍 Checking API Documentation...")
        
        # Check if API documentation exists
        doc_files = ['api_docs.md', 'README.md', 'docs/api.md']
        doc_found = any(os.path.exists(doc) for doc in doc_files)
        
        if doc_found:
            self.log_check("API Documentation", 'pass', "API documentation found")
        else:
            self.log_check("API Documentation", 'warning', 
                         "API documentation not found")
    
    def check_backup_recovery(self):
        """Check backup and recovery procedures"""
        print("\n🔍 Checking Backup & Recovery...")
        
        # Check backup configuration
        backup_strategy = os.environ.get('BACKUP_STRATEGY')
        if not backup_strategy:
            self.log_check("Backup Strategy", 'warning', 
                         "Backup strategy not defined")
        else:
            self.log_check("Backup Strategy", 'pass', "Backup strategy configured")
        
        # Check recovery procedures
        recovery_docs = os.path.exists('recovery_procedures.md')
        if not recovery_docs:
            self.log_check("Recovery Procedures", 'warning', 
                         "Recovery procedures not documented")
        else:
            self.log_check("Recovery Procedures", 'pass', 
                         "Recovery procedures documented")
    
    def generate_deployment_report(self):
        """Generate deployment readiness report"""
        print("\n📄 Generating Deployment Report...")
        
        total_items = len(self.checklist_items)
        passed_items = len([item for item in self.checklist_items if item['status'] == 'pass'])
        failed_items = len([item for item in self.checklist_items if item['status'] == 'fail'])
        warning_items = len([item for item in self.checklist_items if item['status'] == 'warning'])
        
        report = {
            'deployment_readiness': {
                'total_checks': total_items,
                'passed': passed_items,
                'failed': failed_items,
                'warnings': warning_items,
                'critical_issues': len(self.critical_issues),
                'readiness_score': (passed_items / total_items * 100) if total_items > 0 else 0,
                'deployment_ready': len(self.critical_issues) == 0,
                'checked_at': datetime.now().isoformat()
            },
            'checklist_items': self.checklist_items,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'recommendations': self._generate_recommendations()
        }
        
        # Save report
        with open('deployment_readiness_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("✅ Deployment report saved to: deployment_readiness_report.json")
        return report
    
    def _generate_recommendations(self):
        """Generate deployment recommendations"""
        recommendations = []
        
        if self.critical_issues:
            recommendations.append("🚨 CRITICAL: Fix all critical issues before deployment")
        
        if len(self.warnings) > 5:
            recommendations.append("⚠️ Address warning items to improve production readiness")
        
        recommendations.extend([
            "🔒 Ensure all environment variables are set with production values",
            "🗄️ Set up database backups and test recovery procedures",
            "📊 Configure monitoring and alerting systems",
            "🔍 Set up log aggregation and analysis",
            "🧪 Perform load testing before production deployment",
            "📚 Document deployment and rollback procedures",
            "🔄 Set up CI/CD pipeline for automated deployments",
            "🛡️ Conduct security audit and penetration testing"
        ])
        
        return recommendations
    
    def run_full_check(self):
        """Run complete production readiness check"""
        print("🚀 Starting Production Deployment Readiness Check...")
        print("=" * 70)
        
        start_time = datetime.now()
        
        # Run all checks
        check_categories = [
            ("Environment Variables", self.check_environment_variables),
            ("Security Configuration", self.check_security_configuration),
            ("Database Configuration", self.check_database_configuration),
            ("File Structure", self.check_file_structure),
            ("Dependencies", self.check_dependencies),
            ("Performance Settings", self.check_performance_settings),
            ("Monitoring & Logging", self.check_monitoring_logging),
            ("API Documentation", self.check_api_documentation),
            ("Backup & Recovery", self.check_backup_recovery)
        ]
        
        for category_name, check_function in check_categories:
            try:
                check_function()
            except Exception as e:
                self.log_check(category_name, 'fail', 
                             f"Check failed: {str(e)}", True)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate report
        report = self.generate_deployment_report()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 PRODUCTION READINESS SUMMARY")
        print("=" * 70)
        print(f"Total Checks: {report['deployment_readiness']['total_checks']}")
        print(f"✅ Passed: {report['deployment_readiness']['passed']}")
        print(f"❌ Failed: {report['deployment_readiness']['failed']}")
        print(f"⚠️  Warnings: {report['deployment_readiness']['warnings']}")
        print(f"🚨 Critical Issues: {report['deployment_readiness']['critical_issues']}")
        print(f"📊 Readiness Score: {report['deployment_readiness']['readiness_score']:.1f}%")
        print(f"⏱️  Check Duration: {duration:.2f} seconds")
        
        if report['deployment_readiness']['deployment_ready']:
            print("\n🎉 SYSTEM IS READY FOR PRODUCTION DEPLOYMENT!")
            print("✅ All critical checks passed")
        else:
            print(f"\n⚠️  SYSTEM NOT READY FOR PRODUCTION")
            print(f"🚨 {len(self.critical_issues)} critical issues must be resolved")
            print("\nCritical Issues:")
            for issue in self.critical_issues:
                print(f"   - {issue['item']}: {issue['description']}")
        
        if self.warnings:
            print(f"\n💡 Recommendations ({len(self.warnings)} warnings to address):")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"   - {warning['item']}: {warning['description']}")
        
        print("=" * 70)
        
        return report

if __name__ == "__main__":
    checker = ProductionChecker()
    checker.run_full_check()
