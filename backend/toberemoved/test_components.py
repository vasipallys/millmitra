"""
Component Testing Script
Tests individual components without requiring a running server
"""

import sys
import traceback
from datetime import datetime, timedelta

class ComponentTester:
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
    
    def test_imports(self):
        """Test all critical imports"""
        print("🔍 Testing Critical Imports...")
        
        imports_to_test = [
            ("Flask", "from flask import Flask"),
            ("SQLAlchemy", "from flask_sqlalchemy import SQLAlchemy"),
            ("JWT", "from flask_jwt_extended import JWTManager"),
            ("Models", "from models import User, Transaction, Invoice"),
            ("Extensions", "from extensions import db, jwt"),
            ("AI Services", "from services.ai_services import AIService"),
            ("Quality Control", "from services.quality_control_service import QualityControlService"),
            ("Financial Intelligence", "from services.financial_intelligence_service import FinancialIntelligenceService"),
            ("Compliance GST", "from services.compliance_gst_service import ComplianceGSTService"),
            ("Analytics Reporting", "from services.analytics_reporting_service import AnalyticsReportingService"),
        ]
        
        for import_name, import_statement in imports_to_test:
            try:
                exec(import_statement)
                self.log_test(f"Import {import_name}", True, "Import successful")
            except Exception as e:
                self.log_test(f"Import {import_name}", False, f"Import failed: {str(e)}")
    
    def test_app_creation(self):
        """Test Flask app creation"""
        print("🔍 Testing App Creation...")
        
        try:
            from app import create_app
            app = create_app()
            
            if app:
                self.log_test("App Creation", True, "Flask app created successfully")
                
                # Test app configuration
                if hasattr(app, 'config'):
                    self.log_test("App Configuration", True, "App configuration accessible")
                else:
                    self.log_test("App Configuration", False, "App configuration not accessible")
                
                return app
            else:
                self.log_test("App Creation", False, "App creation returned None")
                return None
                
        except Exception as e:
            self.log_test("App Creation", False, f"App creation failed: {str(e)}")
            return None
    
    def test_database_models(self):
        """Test database model definitions"""
        print("🔍 Testing Database Models...")
        
        try:
            from models import User, Transaction, Invoice, Customer, Farmer, ProductionBatch, QualityTest
            
            models_to_test = [
                ("User", User),
                ("Transaction", Transaction),
                ("Invoice", Invoice),
                ("Customer", Customer),
                ("Farmer", Farmer),
                ("ProductionBatch", ProductionBatch),
                ("QualityTest", QualityTest)
            ]
            
            for model_name, model_class in models_to_test:
                try:
                    # Test model instantiation
                    if hasattr(model_class, '__tablename__'):
                        self.log_test(f"Model {model_name}", True, f"Model {model_name} defined correctly")
                    else:
                        self.log_test(f"Model {model_name}", False, f"Model {model_name} missing __tablename__")
                        
                    # Test to_dict method
                    if hasattr(model_class, 'to_dict'):
                        self.log_test(f"Model {model_name} to_dict", True, f"{model_name} has to_dict method")
                    else:
                        self.log_test(f"Model {model_name} to_dict", False, f"{model_name} missing to_dict method")
                        
                except Exception as e:
                    self.log_test(f"Model {model_name}", False, f"Model {model_name} error: {str(e)}")
                    
        except Exception as e:
            self.log_test("Database Models", False, f"Model import failed: {str(e)}")
    
    def test_service_classes(self):
        """Test service class instantiation"""
        print("🔍 Testing Service Classes...")
        
        services_to_test = [
            ("AI Services", "services.ai_services", "AIService"),
            ("Quality Control", "services.quality_control_service", "QualityControlService"),
            ("Financial Intelligence", "services.financial_intelligence_service", "FinancialIntelligenceService"),
            ("Compliance GST", "services.compliance_gst_service", "ComplianceGSTService"),
            ("Analytics Reporting", "services.analytics_reporting_service", "AnalyticsReportingService")
        ]
        
        for service_name, module_name, class_name in services_to_test:
            try:
                module = __import__(module_name, fromlist=[class_name])
                service_class = getattr(module, class_name)
                service_instance = service_class()
                
                if service_instance:
                    self.log_test(f"Service {service_name}", True, f"{service_name} instantiated successfully")
                else:
                    self.log_test(f"Service {service_name}", False, f"{service_name} instantiation returned None")
                    
            except Exception as e:
                self.log_test(f"Service {service_name}", False, f"{service_name} error: {str(e)}")
    
    def test_route_blueprints(self):
        """Test route blueprint imports"""
        print("🔍 Testing Route Blueprints...")
        
        blueprints_to_test = [
            ("Auth Routes", "routes.auth", "auth_bp"),
            ("AI Services Routes", "routes.ai_services", "ai_services_bp"),
            ("Quality Control Routes", "routes.quality_control", "quality_control_bp"),
            ("Financial Intelligence Routes", "routes.financial_intelligence", "financial_intelligence_bp"),
            ("Compliance GST Routes", "routes.compliance_gst", "compliance_gst_bp"),
            ("Analytics Reporting Routes", "routes.analytics_reporting", "analytics_reporting_bp")
        ]
        
        for blueprint_name, module_name, blueprint_var in blueprints_to_test:
            try:
                module = __import__(module_name, fromlist=[blueprint_var])
                blueprint = getattr(module, blueprint_var)
                
                if blueprint:
                    self.log_test(f"Blueprint {blueprint_name}", True, f"{blueprint_name} imported successfully")
                else:
                    self.log_test(f"Blueprint {blueprint_name}", False, f"{blueprint_name} import returned None")
                    
            except Exception as e:
                self.log_test(f"Blueprint {blueprint_name}", False, f"{blueprint_name} error: {str(e)}")
    
    def test_configuration(self):
        """Test application configuration"""
        print("🔍 Testing Configuration...")
        
        try:
            from app import create_app
            app = create_app()
            
            if app:
                # Test critical configuration values
                config_tests = [
                    ("SECRET_KEY", app.config.get('SECRET_KEY')),
                    ("SQLALCHEMY_DATABASE_URI", app.config.get('SQLALCHEMY_DATABASE_URI')),
                    ("JWT_SECRET_KEY", app.config.get('JWT_SECRET_KEY'))
                ]
                
                for config_name, config_value in config_tests:
                    if config_value:
                        self.log_test(f"Config {config_name}", True, f"{config_name} is configured")
                    else:
                        self.log_test(f"Config {config_name}", False, f"{config_name} is not configured")
            else:
                self.log_test("Configuration", False, "Cannot test configuration - app creation failed")
                
        except Exception as e:
            self.log_test("Configuration", False, f"Configuration test failed: {str(e)}")
    
    def test_database_connection(self):
        """Test database connection"""
        print("🔍 Testing Database Connection...")
        
        try:
            from app import create_app
            from extensions import db
            
            app = create_app()
            
            if app:
                with app.app_context():
                    try:
                        # Try to create tables
                        db.create_all()
                        self.log_test("Database Connection", True, "Database connection and table creation successful")
                    except Exception as e:
                        self.log_test("Database Connection", False, f"Database operation failed: {str(e)}")
            else:
                self.log_test("Database Connection", False, "Cannot test database - app creation failed")
                
        except Exception as e:
            self.log_test("Database Connection", False, f"Database connection test failed: {str(e)}")
    
    def test_ai_service_methods(self):
        """Test AI service methods"""
        print("🔍 Testing AI Service Methods...")
        
        try:
            from services.ai_services import AIService
            ai_service = AIService()
            
            # Test method existence
            methods_to_test = [
                "process_voice_command",
                "analyze_quality_image",
                "generate_insights",
                "predict_demand",
                "optimize_production"
            ]
            
            for method_name in methods_to_test:
                if hasattr(ai_service, method_name):
                    self.log_test(f"AI Method {method_name}", True, f"Method {method_name} exists")
                else:
                    self.log_test(f"AI Method {method_name}", False, f"Method {method_name} missing")
                    
        except Exception as e:
            self.log_test("AI Service Methods", False, f"AI service method test failed: {str(e)}")
    
    def test_file_structure(self):
        """Test file structure"""
        print("🔍 Testing File Structure...")
        
        import os
        
        required_files = [
            "app.py",
            "models.py",
            "extensions.py",
            "services/ai_services.py",
            "services/quality_control_service.py",
            "services/financial_intelligence_service.py",
            "services/compliance_gst_service.py",
            "services/analytics_reporting_service.py",
            "routes/auth.py",
            "routes/ai_services.py",
            "routes/quality_control.py",
            "routes/financial_intelligence.py",
            "routes/compliance_gst.py",
            "routes/analytics_reporting.py"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log_test(f"File {file_path}", True, f"File {file_path} exists")
            else:
                self.log_test(f"File {file_path}", False, f"File {file_path} missing")
    
    def run_all_tests(self):
        """Run all component tests"""
        print("🚀 Starting Component Tests...")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # Run all test categories
        test_categories = [
            ("File Structure", self.test_file_structure),
            ("Critical Imports", self.test_imports),
            ("App Creation", self.test_app_creation),
            ("Database Models", self.test_database_models),
            ("Service Classes", self.test_service_classes),
            ("Route Blueprints", self.test_route_blueprints),
            ("Configuration", self.test_configuration),
            ("Database Connection", self.test_database_connection),
            ("AI Service Methods", self.test_ai_service_methods)
        ]
        
        passed_tests = 0
        total_tests = 0
        
        for category_name, test_function in test_categories:
            print(f"\n🔍 Testing {category_name}...")
            try:
                test_function()
                # Count passed tests in this category
                category_tests = [t for t in self.test_results if category_name.lower() in t['test_name'].lower()]
                category_passed = len([t for t in category_tests if t['success']])
                passed_tests += category_passed
                total_tests += len(category_tests)
            except Exception as e:
                print(f"❌ Category {category_name} failed: {str(e)}")
                total_tests += 1
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 COMPONENT TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len([t for t in self.test_results if t['success']])}")
        print(f"Failed: {len([t for t in self.test_results if not t['success']])}")
        print(f"Success Rate: {(len([t for t in self.test_results if t['success']])/len(self.test_results)*100):.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if all(t['success'] for t in self.test_results):
            print("\n🎉 ALL COMPONENT TESTS PASSED!")
        else:
            failed_tests = [t for t in self.test_results if not t['success']]
            print(f"\n⚠️  {len(failed_tests)} component tests failed:")
            for test in failed_tests[:5]:  # Show first 5 failures
                print(f"   - {test['test_name']}: {test['message']}")
        
        print("=" * 60)
        
        return self.test_results

if __name__ == "__main__":
    tester = ComponentTester()
    results = tester.run_all_tests()
    
    # Save results
    import json
    with open('component_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("📄 Component test results saved to: component_test_results.json")
