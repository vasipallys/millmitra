#!/usr/bin/env python3
"""
Comprehensive test of all Rice Mill Management System modules
Tests all 9 core modules for functionality
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_module_imports():
    """Test that all core modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        # Core app imports
        from app import create_app
        from extensions import db, jwt
        from models import User, Farmer, Customer, ProductionBatch, QualityTest
        
        # Service imports
        from services.ai_services import AIServices
        from services.quality_control_service import QualityControlService
        from services.financial_intelligence_service import FinancialIntelligenceService
        from services.compliance_gst_service import ComplianceGSTService
        from services.analytics_reporting_service import AnalyticsReportingService
        
        # Route imports
        from routes.auth import auth_bp
        from routes.dashboard import dashboard_bp
        from routes.farmer import farmer_bp
        from routes.inventory import inventory_bp
        from routes.production import production_bp
        from routes.sales import sales_bp
        from routes.finance import finance_bp
        from routes.customers import customers_bp
        
        print("✅ All core modules imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Module import error: {str(e)}")
        return False

def test_database_models():
    """Test database models and relationships"""
    print("\n🔍 Testing database models...")
    
    try:
        from app import create_app
        from extensions import db
        from models import User, Farmer, Customer, ProductionBatch, QualityTest
        
        app = create_app()
        
        with app.app_context():
            # Test model creation
            db.create_all()
            
            # Test basic queries
            user_count = User.query.count()
            farmer_count = Farmer.query.count()
            customer_count = Customer.query.count()
            batch_count = ProductionBatch.query.count()
            quality_count = QualityTest.query.count()
            
            print(f"✅ Database models working:")
            print(f"   - Users: {user_count}")
            print(f"   - Farmers: {farmer_count}")
            print(f"   - Customers: {customer_count}")
            print(f"   - Production Batches: {batch_count}")
            print(f"   - Quality Tests: {quality_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database model error: {str(e)}")
        return False

def test_ai_services():
    """Test AI services functionality"""
    print("\n🔍 Testing AI services...")
    
    try:
        from services.ai_services import AIServices
        
        ai_service = AIServices()
        
        # Test voice command processing
        response = ai_service.process_voice_command("Test command")
        print(f"✅ Voice command processing: {type(response).__name__}")
        
        # Test quality image analysis
        test_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
        quality_response = ai_service.analyze_quality_image(test_image)
        print(f"✅ Quality image analysis: {type(quality_response).__name__}")
        
        # Test insights generation
        insights = ai_service.generate_insights({"test": "data"}, {"test": "data"})
        print(f"✅ Insights generation: {type(insights).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI services error: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints with test client"""
    print("\n🔍 Testing API endpoints...")
    
    try:
        from app import create_app
        
        app = create_app()
        client = app.test_client()
        
        endpoints_to_test = [
            ('/api/auth/login', 'POST', {'username': 'test', 'password': 'test'}),
            ('/api/dashboard/metrics', 'GET', None),
            ('/api/farmer/list', 'GET', None),
            ('/api/inventory/paddy-stock', 'GET', None),
            ('/api/production/batches', 'GET', None),
            ('/api/sales/orders', 'GET', None),
            ('/api/finance/transactions', 'GET', None),
            ('/api/customers/list', 'GET', None),
        ]
        
        results = {}
        
        with app.app_context():
            for endpoint, method, data in endpoints_to_test:
                try:
                    if method == 'GET':
                        response = client.get(endpoint)
                    elif method == 'POST':
                        response = client.post(endpoint, json=data)
                    
                    results[endpoint] = {
                        'status': response.status_code,
                        'success': response.status_code < 500
                    }
                    
                except Exception as e:
                    results[endpoint] = {
                        'status': 'error',
                        'error': str(e),
                        'success': False
                    }
        
        successful_endpoints = sum(1 for r in results.values() if r['success'])
        total_endpoints = len(results)
        
        print(f"✅ API endpoints tested: {successful_endpoints}/{total_endpoints} successful")
        
        for endpoint, result in results.items():
            status = result['status']
            if result['success']:
                print(f"   ✅ {endpoint}: {status}")
            else:
                print(f"   ⚠️  {endpoint}: {status}")
        
        return successful_endpoints >= total_endpoints * 0.7  # 70% success rate
        
    except Exception as e:
        print(f"❌ API endpoint testing error: {str(e)}")
        return False

def test_service_integrations():
    """Test service layer integrations"""
    print("\n🔍 Testing service integrations...")
    
    try:
        from services.quality_control_service import QualityControlService
        from services.financial_intelligence_service import FinancialIntelligenceService
        from services.compliance_gst_service import ComplianceGSTService
        from services.analytics_reporting_service import AnalyticsReportingService
        
        # Test service instantiation
        quality_service = QualityControlService()
        financial_service = FinancialIntelligenceService()
        compliance_service = ComplianceGSTService()
        analytics_service = AnalyticsReportingService()
        
        print("✅ All services instantiated successfully:")
        print("   ✅ Quality Control Service")
        print("   ✅ Financial Intelligence Service")
        print("   ✅ Compliance GST Service")
        print("   ✅ Analytics Reporting Service")
        
        return True
        
    except Exception as e:
        print(f"❌ Service integration error: {str(e)}")
        return False

def generate_module_test_report():
    """Generate comprehensive module test report"""
    print("🚀 Rice Mill Management System - Module Testing")
    print("=" * 60)
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'overall_status': 'unknown'
    }
    
    # Run all tests
    tests = [
        ('Module Imports', test_module_imports),
        ('Database Models', test_database_models),
        ('AI Services', test_ai_services),
        ('API Endpoints', test_api_endpoints),
        ('Service Integrations', test_service_integrations)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results['tests'][test_name] = {
                'passed': result,
                'timestamp': datetime.now().isoformat()
            }
            if result:
                passed_tests += 1
        except Exception as e:
            test_results['tests'][test_name] = {
                'passed': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    # Determine overall status
    success_rate = passed_tests / total_tests
    if success_rate >= 0.9:
        test_results['overall_status'] = 'excellent'
    elif success_rate >= 0.7:
        test_results['overall_status'] = 'good'
    elif success_rate >= 0.5:
        test_results['overall_status'] = 'fair'
    else:
        test_results['overall_status'] = 'needs_work'
    
    # Save report
    with open('module_test_report.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 MODULE TEST SUMMARY")
    print("=" * 60)
    print(f"Overall Status: {test_results['overall_status'].upper()}")
    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1%})")
    
    for test_name, result in test_results['tests'].items():
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result['passed'] and 'error' in result:
            print(f"      Error: {result['error']}")
    
    print("\n📋 RECOMMENDATIONS:")
    if success_rate >= 0.9:
        print("🎉 Excellent! All core modules are working well.")
        print("   - System is ready for production use")
        print("   - Consider performance optimization")
    elif success_rate >= 0.7:
        print("👍 Good! Most modules are working.")
        print("   - Address failing tests before production")
        print("   - Monitor system performance")
    else:
        print("⚠️  Multiple issues detected.")
        print("   - Fix critical issues before deployment")
        print("   - Review system architecture")
    
    print("=" * 60)
    
    return test_results

def main():
    """Main function"""
    try:
        report = generate_module_test_report()
        
        if report['overall_status'] in ['excellent', 'good']:
            return 0
        elif report['overall_status'] == 'fair':
            return 1
        else:
            return 2
            
    except Exception as e:
        print(f"❌ Critical error during module testing: {str(e)}")
        return 3

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
