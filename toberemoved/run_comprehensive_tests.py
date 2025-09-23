#!/usr/bin/env python3
"""
Comprehensive Test Suite for Rice Mill ERP
Tests all components, APIs, and system integration
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class RiceMillTestSuite:
    def __init__(self):
        self.backend_url = "http://localhost:5000"
        self.ai_services_url = "http://localhost:8000"
        self.test_results = []
        self.auth_token = None
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test result"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_health_check(self):
        """Test system health"""
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"System healthy - {data.get('status')}", data)
                return True
            else:
                self.log_test("Health Check", False, f"Health check failed - Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Health check error: {str(e)}")
            return False
    
    def test_authentication(self):
        """Test user authentication"""
        try:
            # Test registration
            register_data = {
                "username": "testuser",
                "email": "test@ricemill.com",
                "password": "testpass123",
                "role": "user"
            }
            
            response = requests.post(f"{self.backend_url}/api/auth/register", 
                                   json=register_data, timeout=10)
            
            if response.status_code in [200, 201, 409]:  # 409 if user exists
                # Test login
                login_data = {
                    "username": "admin",
                    "password": "admin123"
                }
                
                response = requests.post(f"{self.backend_url}/api/auth/login", 
                                       json=login_data, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get('access_token')
                    self.log_test("Authentication", True, "Login successful", data)
                    return True
                else:
                    self.log_test("Authentication", False, f"Login failed - Status: {response.status_code}")
                    return False
            else:
                self.log_test("Authentication", False, f"Registration failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        endpoints = [
            ("GET", "/api/dashboard/metrics", "Dashboard Metrics"),
            ("GET", "/api/farmer/list", "Farmer List"),
            ("GET", "/api/inventory/stock", "Inventory Stock"),
            ("GET", "/api/production/batches", "Production Batches"),
            ("GET", "/api/sales/orders", "Sales Orders"),
            ("GET", "/api/finance/transactions", "Finance Transactions"),
            ("GET", "/api/customers/list", "Customer List"),
            ("GET", "/api/notifications", "Notifications"),
            ("GET", "/api/analytics/kpi", "Analytics KPI"),
            ("GET", "/api/quality/tests", "Quality Tests"),
            ("GET", "/api/compliance/status", "Compliance Status"),
            ("GET", "/api/supply-chain/status", "Supply Chain Status"),
            ("GET", "/api/logistics/deliveries", "Logistics Deliveries"),
        ]
        
        success_count = 0
        
        for method, endpoint, name in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", 
                                          headers=headers, timeout=10)
                elif method == "POST":
                    response = requests.post(f"{self.backend_url}{endpoint}", 
                                           headers=headers, json={}, timeout=10)
                
                if response.status_code in [200, 201]:
                    self.log_test(f"API - {name}", True, f"Endpoint working - Status: {response.status_code}")
                    success_count += 1
                else:
                    self.log_test(f"API - {name}", False, f"Endpoint failed - Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"API - {name}", False, f"Endpoint error: {str(e)}")
        
        return success_count == len(endpoints)
    
    def test_ai_services(self):
        """Test AI services"""
        try:
            # Test AI health
            response = requests.get(f"{self.ai_services_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test("AI Services Health", True, "AI services healthy")
                
                # Test voice recognition
                voice_data = {"text": "Add new farmer John Doe"}
                response = requests.post(f"{self.ai_services_url}/voice/process", 
                                       json=voice_data, timeout=15)
                
                if response.status_code == 200:
                    self.log_test("AI Voice Processing", True, "Voice processing working")
                    return True
                else:
                    self.log_test("AI Voice Processing", False, f"Voice processing failed - Status: {response.status_code}")
                    return False
            else:
                self.log_test("AI Services Health", False, f"AI services unhealthy - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Services", False, f"AI services error: {str(e)}")
            return False
    
    def test_database_operations(self):
        """Test database operations"""
        headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
        try:
            # Test farmer creation
            farmer_data = {
                "name": "Test Farmer",
                "phone": "9876543210",
                "address": "Test Address",
                "email": "farmer@test.com"
            }
            
            response = requests.post(f"{self.backend_url}/api/farmer/create", 
                                   json=farmer_data, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                self.log_test("Database Operations", True, "Farmer creation successful")
                return True
            else:
                self.log_test("Database Operations", False, f"Farmer creation failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Operations", False, f"Database error: {str(e)}")
            return False
    
    def test_performance(self):
        """Test system performance"""
        try:
            start_time = time.time()
            
            # Test concurrent requests
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for i in range(10):
                    future = executor.submit(requests.get, f"{self.backend_url}/api/health", timeout=5)
                    futures.append(future)
                
                success_count = 0
                for future in as_completed(futures):
                    try:
                        response = future.result()
                        if response.status_code == 200:
                            success_count += 1
                    except:
                        pass
            
            end_time = time.time()
            duration = end_time - start_time
            
            if success_count >= 8 and duration < 10:  # 80% success rate, under 10 seconds
                self.log_test("Performance Test", True, f"Performance good - {success_count}/10 requests in {duration:.2f}s")
                return True
            else:
                self.log_test("Performance Test", False, f"Performance issues - {success_count}/10 requests in {duration:.2f}s")
                return False
                
        except Exception as e:
            self.log_test("Performance Test", False, f"Performance test error: {str(e)}")
            return False
    
    def test_security(self):
        """Test security features"""
        try:
            # Test unauthorized access
            response = requests.get(f"{self.backend_url}/api/farmer/list", timeout=10)
            
            if response.status_code in [401, 403]:
                self.log_test("Security - Unauthorized Access", True, "Unauthorized access properly blocked")
            else:
                self.log_test("Security - Unauthorized Access", False, f"Security issue - Status: {response.status_code}")
            
            # Test SQL injection protection
            malicious_data = {"username": "admin'; DROP TABLE users; --", "password": "test"}
            response = requests.post(f"{self.backend_url}/api/auth/login", 
                                   json=malicious_data, timeout=10)
            
            if response.status_code in [400, 401, 422]:
                self.log_test("Security - SQL Injection", True, "SQL injection attempt blocked")
                return True
            else:
                self.log_test("Security - SQL Injection", False, "Potential SQL injection vulnerability")
                return False
                
        except Exception as e:
            self.log_test("Security Test", False, f"Security test error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        test_functions = [
            self.test_health_check,
            self.test_authentication,
            self.test_api_endpoints,
            self.test_ai_services,
            self.test_database_operations,
            self.test_performance,
            self.test_security
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test function {test_func.__name__} failed: {e}")
        
        # Generate report
        self.generate_report(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def generate_report(self, passed_tests, total_tests):
        """Generate test report"""
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": success_rate,
                "test_date": datetime.now().isoformat()
            },
            "test_results": self.test_results
        }
        
        # Save report
        with open('backend/comprehensive_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 System is ready for production!")
        elif success_rate >= 60:
            print("⚠️ System needs some fixes before production")
        else:
            print("❌ System has critical issues - not ready for production")
        
        print(f"\n📄 Detailed report saved to: backend/comprehensive_test_report.json")

def main():
    """Main test function"""
    
    print("🎯 Rice Mill ERP - Comprehensive Test Suite")
    print("Testing all system components...")
    
    # Check if services are running
    print("\n🔍 Checking service availability...")
    
    test_suite = RiceMillTestSuite()
    
    # Run tests
    success = test_suite.run_all_tests()
    
    if success:
        print("\n✅ All tests passed! System is production ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()