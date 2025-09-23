#!/usr/bin/env python3
"""
Production Deployment Script for Rice Mill ERP
Handles complete production deployment with health checks
"""

import os
import sys
import subprocess
import time
import requests
import json
from datetime import datetime

class ProductionDeployer:
    def __init__(self):
        self.services = {
            'redis': {'port': 6379, 'process': 'redis-server'},
            'postgresql': {'port': 5432, 'process': 'postgres'},
            'backend': {'port': 5000, 'url': 'http://localhost:5000/api/health'},
            'ai_services': {'port': 8000, 'url': 'http://localhost:8000/health'},
            'frontend': {'port': 3000, 'url': 'http://localhost:3000'}
        }
        self.deployment_log = []
    
    def log_step(self, step, success, message):
        """Log deployment step"""
        entry = {
            'step': step,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.deployment_log.append(entry)
        
        status = "✅" if success else "❌"
        print(f"{status} {step}: {message}")
    
    def check_prerequisites(self):
        """Check system prerequisites"""
        print("🔍 Checking Prerequisites...")
        
        prerequisites = [
            ('Python', 'python --version'),
            ('Node.js', 'node --version'),
            ('npm', 'npm --version'),
            ('Redis', 'redis-cli --version'),
            ('PostgreSQL', 'psql --version')
        ]
        
        all_good = True
        
        for name, command in prerequisites:
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.log_step(f"Check {name}", True, f"Found: {version}")
                else:
                    self.log_step(f"Check {name}", False, f"Not found or error")
                    all_good = False
            except Exception as e:
                self.log_step(f"Check {name}", False, f"Error: {str(e)}")
                all_good = False
        
        return all_good
    
    def setup_environment(self):
        """Set up production environment"""
        print("\n🔧 Setting up Production Environment...")
        
        try:
            # Create production directories
            directories = [
                'backend/logs',
                'backend/uploads',
                'backend/exports',
                'backend/temp',
                'docs',
                'backups'
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                self.log_step(f"Create Directory", True, f"Created {directory}")
            
            # Install backend dependencies
            os.chdir('backend')
            result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step("Backend Dependencies", True, "Installed successfully")
            else:
                self.log_step("Backend Dependencies", False, f"Error: {result.stderr}")
                return False
            
            # Install production server
            result = subprocess.run(['pip', 'install', 'gunicorn'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step("Production Server", True, "Gunicorn installed")
            else:
                self.log_step("Production Server", False, f"Error: {result.stderr}")
            
            os.chdir('..')
            
            # Install frontend dependencies
            os.chdir('frontend')
            result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step("Frontend Dependencies", True, "Installed successfully")
            else:
                self.log_step("Frontend Dependencies", False, f"Error: {result.stderr}")
                return False
            
            # Build frontend for production
            result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step("Frontend Build", True, "Built successfully")
            else:
                self.log_step("Frontend Build", False, f"Error: {result.stderr}")
                return False
            
            os.chdir('..')
            
            return True
            
        except Exception as e:
            self.log_step("Environment Setup", False, f"Error: {str(e)}")
            return False
    
    def start_infrastructure_services(self):
        """Start Redis and PostgreSQL"""
        print("\n🗄️ Starting Infrastructure Services...")
        
        try:
            # Start Redis
            if not self.is_service_running('redis'):
                if os.name == 'nt':  # Windows
                    subprocess.Popen(['redis-server'], shell=True)
                else:  # Linux/Mac
                    subprocess.Popen(['redis-server', '--daemonize', 'yes'])
                
                time.sleep(2)
                
                if self.is_service_running('redis'):
                    self.log_step("Redis Server", True, "Started successfully")
                else:
                    self.log_step("Redis Server", False, "Failed to start")
                    return False
            else:
                self.log_step("Redis Server", True, "Already running")
            
            # Check PostgreSQL
            if self.is_service_running('postgresql'):
                self.log_step("PostgreSQL", True, "Running")
            else:
                self.log_step("PostgreSQL", False, "Not running - please start PostgreSQL service")
                return False
            
            return True
            
        except Exception as e:
            self.log_step("Infrastructure Services", False, f"Error: {str(e)}")
            return False
    
    def initialize_database(self):
        """Initialize production database"""
        print("\n🗄️ Initializing Database...")
        
        try:
            os.chdir('backend')
            
            # Run database initialization
            result = subprocess.run([sys.executable, '-c', '''
import sys
sys.path.append(".")
from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables created successfully")
'''], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_step("Database Tables", True, "Created successfully")
            else:
                self.log_step("Database Tables", False, f"Error: {result.stderr}")
                os.chdir('..')
                return False
            
            os.chdir('..')
            return True
            
        except Exception as e:
            self.log_step("Database Initialization", False, f"Error: {str(e)}")
            return False
    
    def start_application_services(self):
        """Start backend, AI services, and frontend"""
        print("\n🚀 Starting Application Services...")
        
        try:
            # Start backend with Gunicorn
            os.chdir('backend')
            backend_cmd = [
                'gunicorn',
                '-w', '4',
                '-b', '0.0.0.0:5000',
                '--timeout', '120',
                '--keep-alive', '2',
                '--max-requests', '1000',
                '--access-logfile', 'logs/access.log',
                '--error-logfile', 'logs/error.log',
                'app:app'
            ]
            
            subprocess.Popen(backend_cmd)
            os.chdir('..')
            
            # Wait for backend to start
            time.sleep(5)
            
            if self.check_service_health('backend'):
                self.log_step("Backend Server", True, "Started successfully")
            else:
                self.log_step("Backend Server", False, "Failed to start or unhealthy")
                return False
            
            # Start AI services
            os.chdir('ai-services')
            subprocess.Popen([sys.executable, 'main.py'])
            os.chdir('..')
            
            # Wait for AI services to start
            time.sleep(3)
            
            if self.check_service_health('ai_services'):
                self.log_step("AI Services", True, "Started successfully")
            else:
                self.log_step("AI Services", False, "Failed to start or unhealthy")
            
            # Start frontend
            os.chdir('frontend')
            subprocess.Popen(['npm', 'run', 'preview'])
            os.chdir('..')
            
            # Wait for frontend to start
            time.sleep(3)
            
            if self.check_service_health('frontend'):
                self.log_step("Frontend Server", True, "Started successfully")
            else:
                self.log_step("Frontend Server", False, "Failed to start")
            
            return True
            
        except Exception as e:
            self.log_step("Application Services", False, f"Error: {str(e)}")
            return False
    
    def is_service_running(self, service_name):
        """Check if a service is running"""
        try:
            if service_name == 'redis':
                result = subprocess.run(['redis-cli', 'ping'], 
                                      capture_output=True, text=True)
                return result.returncode == 0 and 'PONG' in result.stdout
            
            elif service_name == 'postgresql':
                result = subprocess.run(['pg_isready'], capture_output=True, text=True)
                return result.returncode == 0
            
            return False
            
        except:
            return False
    
    def check_service_health(self, service_name):
        """Check service health via HTTP"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        if 'url' not in service:
            return False
        
        try:
            response = requests.get(service['url'], timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def run_health_checks(self):
        """Run comprehensive health checks"""
        print("\n🏥 Running Health Checks...")
        
        all_healthy = True
        
        for service_name, service in self.services.items():
            if 'url' in service:
                if self.check_service_health(service_name):
                    self.log_step(f"Health Check - {service_name}", True, "Healthy")
                else:
                    self.log_step(f"Health Check - {service_name}", False, "Unhealthy")
                    all_healthy = False
        
        return all_healthy
    
    def generate_deployment_report(self):
        """Generate deployment report"""
        
        success_count = sum(1 for entry in self.deployment_log if entry['success'])
        total_count = len(self.deployment_log)
        success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
        
        report = {
            'deployment_summary': {
                'total_steps': total_count,
                'successful_steps': success_count,
                'failed_steps': total_count - success_count,
                'success_rate': success_rate,
                'deployment_date': datetime.now().isoformat(),
                'status': 'success' if success_rate >= 90 else 'partial' if success_rate >= 70 else 'failed'
            },
            'deployment_log': self.deployment_log,
            'service_urls': {
                'Frontend': 'http://localhost:3000',
                'Backend API': 'http://localhost:5000',
                'AI Services': 'http://localhost:8000',
                'API Documentation': 'docs/api_documentation.html'
            }
        }
        
        with open('deployment_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def deploy(self):
        """Run complete deployment"""
        print("🚀 Rice Mill ERP - Production Deployment")
        print("=" * 60)
        
        steps = [
            ("Prerequisites", self.check_prerequisites),
            ("Environment Setup", self.setup_environment),
            ("Infrastructure Services", self.start_infrastructure_services),
            ("Database Initialization", self.initialize_database),
            ("Application Services", self.start_application_services),
            ("Health Checks", self.run_health_checks)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"\n❌ Deployment failed at: {step_name}")
                self.generate_deployment_report()
                return False
        
        # Generate final report
        report = self.generate_deployment_report()
        
        print("\n" + "=" * 60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 60)
        
        if report['deployment_summary']['success_rate'] >= 90:
            print("✅ Deployment successful!")
            print("\n🌐 Service URLs:")
            for service, url in report['service_urls'].items():
                print(f"  {service}: {url}")
            
            print("\n📊 Quick Test:")
            print("  curl http://localhost:5000/api/health")
            print("\n📄 Deployment report: deployment_report.json")
            
        else:
            print("⚠️ Deployment completed with issues")
            print("📄 Check deployment_report.json for details")
        
        return True

def main():
    """Main deployment function"""
    
    deployer = ProductionDeployer()
    success = deployer.deploy()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Test the application at http://localhost:3000")
        print("2. Check API health at http://localhost:5000/api/health")
        print("3. Review logs in backend/logs/")
        print("4. Set up monitoring and backups")
        sys.exit(0)
    else:
        print("\n❌ Deployment failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()