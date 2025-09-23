"""
System Validation Script for Rice Mill Management System
Performs comprehensive validation of all system components
"""

import os
import sys
import requests
import json
import time
from pathlib import Path
from datetime import datetime

class SystemValidator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_url = "http://127.0.0.1:5000"
        self.ai_service_url = "http://127.0.0.1:8000"
        self.frontend_url = "http://127.0.0.1:3000"
        
        self.validation_results = {
            'environment': [],
            'backend': [],
            'ai_services': [],
            'database': [],
            'security': [],
            'overall_status': 'unknown'
        }
    
    def log_validation(self, category, test_name, status, message, details=None):
        """Log validation result"""
        result = {
            'test_name': test_name,
            'status': status,  # 'pass', 'fail', 'warning'
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.validation_results[category].append(result)
        
        status_icon = "[PASS]" if status == 'pass' else "[FAIL]" if status == 'fail' else "[WARN]"
        print(f"{status_icon} {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def validate_environment(self):
        """Validate environment configuration"""
        print("[CHECK] Validating Environment Variables...")
        
        # Check environment files
        env_files = [
            ('.env', 'Development environment'),
            ('.env.production', 'Production environment')
        ]
        
        for env_file, description in env_files:
            env_path = self.project_root / "backend" / env_file
            if env_path.exists():
                self.log_validation(
                    'environment', 
                    f"Environment File ({env_file})",
                    'pass',
                    f"{description} file exists"
                )
                
                # Check for critical variables
                with open(env_path, 'r') as f:
                    env_content = f.read()
                
                critical_vars = ['SECRET_KEY', 'JWT_SECRET_KEY', 'DATABASE_URL']
                missing_vars = []
                
                for var in critical_vars:
                    if f"{var}=" not in env_content:
                        missing_vars.append(var)
                
                if missing_vars:
                    self.log_validation(
                        'environment',
                        f"Critical Variables ({env_file})",
                        'warning',
                        f"Missing variables: {', '.join(missing_vars)}"
                    )
                else:
                    self.log_validation(
                        'environment',
                        f"Critical Variables ({env_file})",
                        'pass',
                        "All critical environment variables present"
                    )
            else:
                self.log_validation(
                    'environment',
                    f"Environment File ({env_file})",
                    'fail' if env_file == '.env' else 'warning',
                    f"{description} file missing"
                )
    
    def validate_backend(self):
        """Validate backend API"""
        print("[CHECK] Validating Backend API...")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log_validation(
                    'backend',
                    'Health Endpoint',
                    'pass',
                    'Backend health endpoint responding',
                    health_data
                )
                
                # Check service status
                services = health_data.get('services', {})
                for service, status in services.items():
                    service_status = 'pass' if status in ['connected', 'active'] else 'warning'
                    self.log_validation(
                        'backend',
                        f'Service: {service}',
                        service_status,
                        f'Status: {status}'
                    )
            else:
                self.log_validation(
                    'backend',
                    'Health Endpoint',
                    'fail',
                    f'Backend returned status {response.status_code}'
                )
        
        except requests.exceptions.ConnectionError:
            self.log_validation(
                'backend',
                'Backend Connection',
                'fail',
                'Cannot connect to backend - ensure backend is running'
            )
        except Exception as e:
            self.log_validation(
                'backend',
                'Backend Validation',
                'fail',
                f'Backend validation error: {str(e)}'
            )
    
    def validate_ai_services(self):
        """Validate AI services"""
        print("[CHECK] Validating AI Services...")
        
        try:
            # Test AI services health
            response = requests.get(f"{self.ai_service_url}/health", timeout=10)
            
            if response.status_code == 200:
                self.log_validation(
                    'ai_services',
                    'AI Services Health',
                    'pass',
                    'AI services responding correctly'
                )
                
                # Test query processing
                try:
                    query_response = requests.post(
                        f"{self.ai_service_url}/process-query",
                        params={"query": "test query"},
                        timeout=10
                    )
                    
                    if query_response.status_code == 200:
                        self.log_validation(
                            'ai_services',
                            'Query Processing',
                            'pass',
                            'AI query processing functional'
                        )
                    else:
                        self.log_validation(
                            'ai_services',
                            'Query Processing',
                            'warning',
                            f'Query processing returned status {query_response.status_code}'
                        )
                except Exception as e:
                    self.log_validation(
                        'ai_services',
                        'Query Processing',
                        'warning',
                        f'Query processing test failed: {str(e)}'
                    )
            else:
                self.log_validation(
                    'ai_services',
                    'AI Services Health',
                    'fail',
                    f'AI services returned status {response.status_code}'
                )
        
        except requests.exceptions.ConnectionError:
            self.log_validation(
                'ai_services',
                'AI Services Connection',
                'fail',
                'Cannot connect to AI services - ensure AI services are running'
            )
        except Exception as e:
            self.log_validation(
                'ai_services',
                'AI Services Validation',
                'fail',
                f'AI services validation error: {str(e)}'
            )
    
    def validate_database(self):
        """Validate database configuration"""
        print("[CHECK] Validating Database...")
        
        try:
            # Try to import and test database
            sys.path.append(str(self.project_root / "backend"))
            
            from app import create_app
            from sqlalchemy import text
            
            # Create app and test database connection within app context
            app = create_app()
            with app.app_context():
                from extensions import db
                from models import User
                
                # Test database connection
                try:
                    # Simple query to test connection
                    result = db.session.execute(text('SELECT 1')).scalar()
                    if result == 1:
                        self.log_validation(
                            'database',
                            'Database Connection',
                            'pass',
                            'Database connection successful'
                        )
                    else:
                        self.log_validation(
                            'database',
                            'Database Connection',
                            'fail',
                            'Database connection test failed'
                        )
                except Exception as e:
                    self.log_validation(
                        'database',
                        'Database Connection',
                        'fail',
                        f'Database connection error: {str(e)}'
                    )
                
                # Test model imports
                try:
                    user_count = User.query.count()
                    self.log_validation(
                        'database',
                        'Model Validation',
                        'pass',
                        f'User model working - {user_count} users in database'
                    )
                except Exception as e:
                    self.log_validation(
                        'database',
                        'Model Validation',
                        'warning',
                        f'Model validation issue: {str(e)}'
                    )
        except ImportError as e:
            self.log_validation(
                'database',
                'Database Import',
                'fail',
                f'Cannot import database modules: {str(e)}'
            )
                
        except ImportError as e:
            self.log_validation(
                'database',
                'Database Import',
                'fail',
                f'Cannot import database modules: {str(e)}'
            )
        except Exception as e:
            self.log_validation(
                'database',
                'Database Validation',
                'fail',
                f'Database validation error: {str(e)}'
            )
    
    def validate_security(self):
        """Validate security configuration"""
        print("[CHECK] Validating Security Configuration...")
        
        # Check environment file security
        env_file = self.project_root / "backend" / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            # Check for debug mode
            if "FLASK_DEBUG=True" in env_content:
                self.log_validation(
                    'security',
                    'Debug Mode',
                    'warning',
                    'Debug mode is enabled - disable for production'
                )
            else:
                self.log_validation(
                    'security',
                    'Debug Mode',
                    'pass',
                    'Debug mode properly configured'
                )
            
            # Check for default secret keys
            if "SECRET_KEY=dev" in env_content or "SECRET_KEY=your_" in env_content:
                self.log_validation(
                    'security',
                    'Secret Key',
                    'fail',
                    'Using default or placeholder secret key'
                )
            else:
                self.log_validation(
                    'security',
                    'Secret Key',
                    'pass',
                    'Secret key appears to be properly configured'
                )
        
        # Check HTTPS configuration in production
        prod_env_file = self.project_root / "backend" / ".env.production"
        if prod_env_file.exists():
            with open(prod_env_file, 'r') as f:
                prod_content = f.read()
            
            if "FORCE_HTTPS=True" in prod_content:
                self.log_validation(
                    'security',
                    'HTTPS Configuration',
                    'pass',
                    'HTTPS enforcement configured for production'
                )
            else:
                self.log_validation(
                    'security',
                    'HTTPS Configuration',
                    'warning',
                    'HTTPS enforcement not configured'
                )
    
    def calculate_overall_status(self):
        """Calculate overall system status"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warning_tests = 0
        
        for category, results in self.validation_results.items():
            if category == 'overall_status':
                continue
            
            for result in results:
                total_tests += 1
                if result['status'] == 'pass':
                    passed_tests += 1
                elif result['status'] == 'fail':
                    failed_tests += 1
                elif result['status'] == 'warning':
                    warning_tests += 1
        
        if failed_tests == 0 and warning_tests == 0:
            overall_status = 'excellent'
        elif failed_tests == 0:
            overall_status = 'good'
        elif failed_tests <= 2:
            overall_status = 'fair'
        else:
            overall_status = 'poor'
        
        self.validation_results['overall_status'] = {
            'status': overall_status,
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return overall_status
    
    def generate_validation_report(self):
        """Generate validation report"""
        print("[REPORT] Generating Validation Report...")
        
        # Calculate overall status
        overall_status = self.calculate_overall_status()
        
        # Save detailed report
        report_file = self.project_root / "system_validation_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"Detailed report saved: {report_file}")
        
        return overall_status
    
    def run_full_validation(self):
        """Run complete system validation"""
        print("[START] Starting System Validation...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all validation categories
        validation_categories = [
            ("Environment Configuration", self.validate_environment),
            ("Backend API", self.validate_backend),
            ("AI Services", self.validate_ai_services),
            ("Database", self.validate_database),
            ("Security", self.validate_security)
        ]
        
        for category_name, validation_function in validation_categories:
            try:
                validation_function()
            except Exception as e:
                self.log_validation(
                    'environment',  # Default category for errors
                    category_name,
                    'fail',
                    f"Validation error: {str(e)}"
                )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate report
        overall_status = self.generate_validation_report()
        status_info = self.validation_results['overall_status']
        
        # Print summary
        print("=" * 60)
        print(" SYSTEM VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {overall_status.upper()}")
        print(f"Total Tests: {status_info['total_tests']}")
        print(f" Passed: {status_info['passed']}")
        print(f" Failed: {status_info['failed']}")
        print(f"  Warnings: {status_info['warnings']}")
        print(f" Pass Rate: {status_info['pass_rate']:.1f}%")
        print(f"  Duration: {duration:.2f} seconds")
        print(f" Warnings: {status_info['warnings']}")
        print(f" Pass Rate: {status_info['pass_rate']:.1f}%")
        print(f" Duration: {duration:.2f} seconds")
        
        if overall_status in ['excellent', 'good']:
            print("\n SYSTEM VALIDATION SUCCESSFUL!")
            print(" System is ready for operation")
        elif overall_status == 'fair':
            print("\n SYSTEM NEEDS ATTENTION")
            print(" Address failed tests before production deployment")
        else:
            print("\n SYSTEM VALIDATION FAILED")
            print(" Critical issues must be resolved")
        
        print("=" * 60)
        
        return {
            'overall_status': overall_status,
            'status_info': status_info,
            'duration': duration
        }

if __name__ == "__main__":
    validator = SystemValidator()
    result = validator.run_full_validation()
    
    # Exit with appropriate code
    if result['overall_status'] in ['excellent', 'good']:
        sys.exit(0)
    else:
        sys.exit(1)
