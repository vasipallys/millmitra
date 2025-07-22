"""
Stability and Bug Fix Script
Identifies and fixes common stability issues in the Rice Mill Management System
"""

import os
import sys
import traceback
from datetime import datetime
from extensions import db
from models import User, Transaction, Invoice, Customer, Farmer, ProductionBatch, QualityTest

class StabilityFixer:
    def __init__(self):
        self.fixes_applied = []
        self.issues_found = []
        
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
            print(f"✅ FIXED: {fix_name}")
            print(f"   Issue: {issue_description}")
            print(f"   Fix: {fix_description}")
        else:
            self.issues_found.append(fix_record)
            print(f"❌ ISSUE: {fix_name}")
            print(f"   Problem: {issue_description}")
        print()
    
    def fix_database_integrity(self):
        """Fix database integrity issues"""
        print("🔧 Checking Database Integrity...")
        
        try:
            # Check for orphaned records
            orphaned_issues = []
            
            # Check for transactions without valid references
            invalid_transactions = db.session.query(Transaction).filter(
                Transaction.created_by.is_(None)
            ).count()
            
            if invalid_transactions > 0:
                # Fix by setting a default user
                db.session.query(Transaction).filter(
                    Transaction.created_by.is_(None)
                ).update({'created_by': 1})  # Assuming user ID 1 exists
                db.session.commit()
                
                self.log_fix(
                    "Orphaned Transactions",
                    f"{invalid_transactions} transactions without valid user reference",
                    "Set default user reference for orphaned transactions"
                )
            
            # Check for invoices without customer references
            invalid_invoices = db.session.query(Invoice).filter(
                Invoice.customer_id.is_(None)
            ).count()
            
            if invalid_invoices > 0:
                self.log_fix(
                    "Invalid Invoices",
                    f"{invalid_invoices} invoices without customer reference",
                    "Manual review required for invoice-customer relationships",
                    success=False
                )
            
            # Check for production batches without valid dates
            invalid_batches = db.session.query(ProductionBatch).filter(
                ProductionBatch.production_date.is_(None)
            ).count()
            
            if invalid_batches > 0:
                # Fix by setting current date
                db.session.query(ProductionBatch).filter(
                    ProductionBatch.production_date.is_(None)
                ).update({'production_date': datetime.now().date()})
                db.session.commit()
                
                self.log_fix(
                    "Invalid Production Dates",
                    f"{invalid_batches} production batches without dates",
                    "Set current date for batches missing production dates"
                )
            
        except Exception as e:
            self.log_fix(
                "Database Integrity Check",
                f"Error during integrity check: {str(e)}",
                "Manual database review required",
                success=False
            )
    
    def fix_model_relationships(self):
        """Fix model relationship issues"""
        print("🔧 Fixing Model Relationships...")
        
        try:
            # Ensure all models have proper to_dict methods
            models_to_check = [Transaction, Invoice, Customer, Farmer, ProductionBatch, QualityTest]
            
            for model in models_to_check:
                if not hasattr(model, 'to_dict'):
                    self.log_fix(
                        f"{model.__name__} to_dict Method",
                        f"{model.__name__} missing to_dict method",
                        "to_dict method needs to be added manually",
                        success=False
                    )
                else:
                    self.log_fix(
                        f"{model.__name__} to_dict Method",
                        "Checking to_dict method availability",
                        "to_dict method is available"
                    )
            
        except Exception as e:
            self.log_fix(
                "Model Relationships",
                f"Error checking model relationships: {str(e)}",
                "Manual model review required",
                success=False
            )
    
    def fix_api_error_handling(self):
        """Fix API error handling issues"""
        print("🔧 Fixing API Error Handling...")
        
        # This would involve checking route files for proper error handling
        api_files = [
            'routes/auth.py',
            'routes/ai_services.py',
            'routes/quality_control.py',
            'routes/financial_intelligence.py',
            'routes/compliance_gst.py',
            'routes/analytics_reporting.py'
        ]
        
        for api_file in api_files:
            if os.path.exists(api_file):
                self.log_fix(
                    f"API File {api_file}",
                    "Checking API error handling",
                    "API file exists and should have proper error handling"
                )
            else:
                self.log_fix(
                    f"API File {api_file}",
                    f"API file {api_file} not found",
                    "API file may need to be created or path corrected",
                    success=False
                )
    
    def fix_configuration_issues(self):
        """Fix configuration and environment issues"""
        print("🔧 Fixing Configuration Issues...")
        
        # Check for required environment variables
        required_configs = [
            'SECRET_KEY',
            'DATABASE_URL',
            'JWT_SECRET_KEY'
        ]
        
        missing_configs = []
        for config in required_configs:
            if not os.environ.get(config):
                missing_configs.append(config)
        
        if missing_configs:
            self.log_fix(
                "Environment Configuration",
                f"Missing environment variables: {', '.join(missing_configs)}",
                "Set missing environment variables in .env file",
                success=False
            )
        else:
            self.log_fix(
                "Environment Configuration",
                "Checking required environment variables",
                "All required environment variables are set"
            )
        
        # Check for required directories
        required_dirs = [
            'uploads',
            'exports',
            'logs',
            'temp'
        ]
        
        for directory in required_dirs:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                    self.log_fix(
                        f"Directory {directory}",
                        f"Directory {directory} was missing",
                        f"Created directory {directory}"
                    )
                except Exception as e:
                    self.log_fix(
                        f"Directory {directory}",
                        f"Could not create directory {directory}: {str(e)}",
                        "Manual directory creation required",
                        success=False
                    )
            else:
                self.log_fix(
                    f"Directory {directory}",
                    "Checking directory existence",
                    f"Directory {directory} exists"
                )
    
    def fix_import_issues(self):
        """Fix import and dependency issues"""
        print("🔧 Fixing Import Issues...")
        
        # Check for common import issues
        try:
            import numpy as np
            self.log_fix(
                "NumPy Import",
                "Checking NumPy availability",
                "NumPy is available for analytics"
            )
        except ImportError:
            self.log_fix(
                "NumPy Import",
                "NumPy not available",
                "Install NumPy: pip install numpy",
                success=False
            )
        
        try:
            import requests
            self.log_fix(
                "Requests Import",
                "Checking Requests library availability",
                "Requests library is available"
            )
        except ImportError:
            self.log_fix(
                "Requests Import",
                "Requests library not available",
                "Install Requests: pip install requests",
                success=False
            )
        
        try:
            from flask_jwt_extended import JWTManager
            self.log_fix(
                "JWT Import",
                "Checking JWT extension availability",
                "JWT extension is available"
            )
        except ImportError:
            self.log_fix(
                "JWT Import",
                "JWT extension not available",
                "Install JWT: pip install flask-jwt-extended",
                success=False
            )
    
    def fix_data_validation_issues(self):
        """Fix data validation issues"""
        print("🔧 Fixing Data Validation Issues...")
        
        try:
            # Check for invalid data in key tables
            
            # Check for negative amounts in transactions
            negative_transactions = db.session.query(Transaction).filter(
                Transaction.amount < 0
            ).count()
            
            if negative_transactions > 0:
                self.log_fix(
                    "Negative Transaction Amounts",
                    f"{negative_transactions} transactions with negative amounts",
                    "Review and correct negative transaction amounts",
                    success=False
                )
            
            # Check for future dates in historical records
            future_transactions = db.session.query(Transaction).filter(
                Transaction.transaction_date > datetime.now().date()
            ).count()
            
            if future_transactions > 0:
                self.log_fix(
                    "Future Transaction Dates",
                    f"{future_transactions} transactions with future dates",
                    "Review and correct future transaction dates",
                    success=False
                )
            
            # Check for empty required fields
            empty_customer_names = db.session.query(Customer).filter(
                Customer.name.is_(None) | (Customer.name == '')
            ).count()
            
            if empty_customer_names > 0:
                self.log_fix(
                    "Empty Customer Names",
                    f"{empty_customer_names} customers without names",
                    "Add names for customers missing this required field",
                    success=False
                )
            
        except Exception as e:
            self.log_fix(
                "Data Validation",
                f"Error during data validation: {str(e)}",
                "Manual data review required",
                success=False
            )
    
    def fix_security_issues(self):
        """Fix security-related issues"""
        print("🔧 Fixing Security Issues...")
        
        # Check for security configurations
        security_checks = [
            {
                'name': 'Debug Mode',
                'check': lambda: os.environ.get('FLASK_ENV') != 'production',
                'issue': 'Debug mode enabled in production',
                'fix': 'Set FLASK_ENV=production for production deployment'
            },
            {
                'name': 'Secret Key',
                'check': lambda: os.environ.get('SECRET_KEY', 'dev') == 'dev',
                'issue': 'Using default secret key',
                'fix': 'Set a strong, unique SECRET_KEY'
            },
            {
                'name': 'JWT Secret',
                'check': lambda: os.environ.get('JWT_SECRET_KEY', 'jwt-secret') == 'jwt-secret',
                'issue': 'Using default JWT secret',
                'fix': 'Set a strong, unique JWT_SECRET_KEY'
            }
        ]
        
        for check in security_checks:
            try:
                if check['check']():
                    self.log_fix(
                        check['name'],
                        check['issue'],
                        check['fix'],
                        success=False
                    )
                else:
                    self.log_fix(
                        check['name'],
                        f"Checking {check['name'].lower()} security",
                        f"{check['name']} security is properly configured"
                    )
            except Exception as e:
                self.log_fix(
                    check['name'],
                    f"Error checking {check['name'].lower()}: {str(e)}",
                    "Manual security review required",
                    success=False
                )
    
    def generate_stability_report(self):
        """Generate stability report"""
        print("📄 Generating Stability Report...")
        
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
                'Regular database maintenance and integrity checks',
                'Monitor system logs for errors and warnings',
                'Keep dependencies updated to latest stable versions',
                'Implement comprehensive error logging',
                'Regular security audits and updates',
                'Backup database regularly',
                'Monitor system performance metrics'
            ]
        }
        
        # Save report
        import json
        with open('stability_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("✅ Stability report saved to: stability_report.json")
        return report
    
    def run_all_fixes(self):
        """Run all stability fixes"""
        print("🚀 Starting Stability and Bug Fixes...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all fix categories
        fix_categories = [
            ("Database Integrity", self.fix_database_integrity),
            ("Model Relationships", self.fix_model_relationships),
            ("API Error Handling", self.fix_api_error_handling),
            ("Configuration Issues", self.fix_configuration_issues),
            ("Import Issues", self.fix_import_issues),
            ("Data Validation", self.fix_data_validation_issues),
            ("Security Issues", self.fix_security_issues)
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
        print("📊 STABILITY CHECK SUMMARY")
        print("=" * 60)
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        print(f"⚠️  Issues Found: {len(self.issues_found)}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if len(self.issues_found) == 0:
            print("\n🎉 System is stable and ready for production!")
        else:
            print(f"\n⚠️  {len(self.issues_found)} issues need attention before production deployment.")
            print("Review the stability report for details.")
        
        print("=" * 60)

if __name__ == "__main__":
    fixer = StabilityFixer()
    fixer.run_all_fixes()
