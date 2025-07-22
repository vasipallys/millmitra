"""
Comprehensive System Testing Script
Tests all major functionalities of the Rice Mill Management System
"""

import requests
import json
import time
from datetime import datetime, timedelta

class RiceMillSystemTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {message}")
        
    def test_health_check(self):
        """Test system health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
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
    
    def test_user_authentication(self):
        """Test user authentication system"""
        try:
            # Test user registration
            register_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123",
                "role": "admin"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/register", 
                                   json=register_data, timeout=10)
            
            if response.status_code in [200, 201, 409]:  # 409 for user already exists
                self.log_test("User Registration", True, "Registration endpoint working")
            else:
                self.log_test("User Registration", False, f"Registration failed - Status: {response.status_code}")
                return False
            
            # Test user login
            login_data = {
                "username": "testuser",
                "password": "testpass123"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login", 
                                   json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.token = data['access_token']
                    self.log_test("User Login", True, "Login successful, token received")
                    return True
                else:
                    self.log_test("User Login", False, "Login response missing token")
                    return False
            else:
                self.log_test("User Login", False, f"Login failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("User Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        if self.token:
            return {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
        return {'Content-Type': 'application/json'}
    
    def test_ai_services(self):
        """Test AI services functionality"""
        try:
            # Test voice recognition
            voice_data = {
                "audio_data": "mock_audio_data",
                "language": "en"
            }
            
            response = requests.post(f"{self.base_url}/api/ai/voice/recognize", 
                                   json=voice_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("Voice Recognition", True, "Voice recognition endpoint working")
            else:
                self.log_test("Voice Recognition", False, f"Voice recognition failed - Status: {response.status_code}")
            
            # Test quality assessment
            quality_data = {
                "image_data": "mock_image_data",
                "batch_id": "TEST001"
            }
            
            response = requests.post(f"{self.base_url}/api/ai/quality/assess", 
                                   json=quality_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("AI Quality Assessment", True, "Quality assessment endpoint working")
                return True
            else:
                self.log_test("AI Quality Assessment", False, f"Quality assessment failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Services", False, f"AI services error: {str(e)}")
            return False
    
    def test_quality_control(self):
        """Test quality control module"""
        try:
            # Test quality test creation
            quality_test_data = {
                "batch_id": "TEST001",
                "test_type": "visual_inspection",
                "test_parameters": {
                    "moisture_content": 12.5,
                    "broken_percentage": 3.2,
                    "foreign_matter": 0.5
                }
            }
            
            response = requests.post(f"{self.base_url}/api/quality/tests/create", 
                                   json=quality_test_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code in [200, 201]:
                self.log_test("Quality Test Creation", True, "Quality test creation working")
                return True
            else:
                self.log_test("Quality Test Creation", False, f"Quality test creation failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Quality Control", False, f"Quality control error: {str(e)}")
            return False
    
    def test_financial_intelligence(self):
        """Test financial intelligence module"""
        try:
            # Test payment prediction
            payment_data = {
                "customer_id": 1,
                "amount": 50000,
                "due_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            response = requests.post(f"{self.base_url}/api/financial-intelligence/payments/predict", 
                                   json=payment_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("Payment Prediction", True, "Payment prediction working")
            else:
                self.log_test("Payment Prediction", False, f"Payment prediction failed - Status: {response.status_code}")
            
            # Test financial insights
            response = requests.get(f"{self.base_url}/api/financial-intelligence/insights/generate", 
                                  headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("Financial Insights", True, "Financial insights working")
                return True
            else:
                self.log_test("Financial Insights", False, f"Financial insights failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Financial Intelligence", False, f"Financial intelligence error: {str(e)}")
            return False
    
    def test_compliance_gst(self):
        """Test compliance and GST module"""
        try:
            # Test GST calculation
            gst_data = {
                "amount": 10000,
                "product_category": "processed_rice",
                "transaction_type": "sale"
            }
            
            response = requests.post(f"{self.base_url}/api/compliance/gst/calculate", 
                                   json=gst_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("GST Calculation", True, "GST calculation working")
            else:
                self.log_test("GST Calculation", False, f"GST calculation failed - Status: {response.status_code}")
            
            # Test compliance status
            response = requests.get(f"{self.base_url}/api/compliance/compliance/status", 
                                  headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("Compliance Status", True, "Compliance status working")
                return True
            else:
                self.log_test("Compliance Status", False, f"Compliance status failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Compliance GST", False, f"Compliance GST error: {str(e)}")
            return False
    
    def test_analytics_reporting(self):
        """Test analytics and reporting module"""
        try:
            # Test KPI calculation
            kpi_data = {
                "kpi_types": ["production", "quality", "financial"],
                "period": {
                    "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now().isoformat()
                }
            }
            
            response = requests.post(f"{self.base_url}/api/analytics/kpi/calculate", 
                                   json=kpi_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("KPI Calculation", True, "KPI calculation working")
            else:
                self.log_test("KPI Calculation", False, f"KPI calculation failed - Status: {response.status_code}")
            
            # Test dashboard overview
            response = requests.get(f"{self.base_url}/api/analytics/dashboard/overview", 
                                  headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("Analytics Dashboard", True, "Analytics dashboard working")
                return True
            else:
                self.log_test("Analytics Dashboard", False, f"Analytics dashboard failed - Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Analytics Reporting", False, f"Analytics reporting error: {str(e)}")
            return False
    
    def test_database_operations(self):
        """Test basic database operations"""
        try:
            # Test database connectivity through a simple query
            # This would typically involve checking if we can create/read records
            
            # For now, we'll test through API endpoints that interact with the database
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('services', {}).get('database') == 'connected':
                    self.log_test("Database Connectivity", True, "Database connection verified")
                    return True
                else:
                    self.log_test("Database Connectivity", False, "Database not connected")
                    return False
            else:
                self.log_test("Database Connectivity", False, "Cannot verify database status")
                return False
                
        except Exception as e:
            self.log_test("Database Operations", False, f"Database error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all system tests"""
        print("🚀 Starting Rice Mill Management System Tests...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Core system tests
        tests = [
            ("System Health", self.test_health_check),
            ("User Authentication", self.test_user_authentication),
            ("Database Operations", self.test_database_operations),
            ("AI Services", self.test_ai_services),
            ("Quality Control", self.test_quality_control),
            ("Financial Intelligence", self.test_financial_intelligence),
            ("Compliance & GST", self.test_compliance_gst),
            ("Analytics & Reporting", self.test_analytics_reporting)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_function in tests:
            print(f"\n🔍 Testing {test_name}...")
            try:
                if test_function():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed. Review issues before production deployment.")
        
        return self.test_results
    
    def generate_test_report(self):
        """Generate detailed test report"""
        report = {
            'test_summary': {
                'total_tests': len(self.test_results),
                'passed_tests': len([t for t in self.test_results if t['success']]),
                'failed_tests': len([t for t in self.test_results if not t['success']]),
                'test_date': datetime.now().isoformat()
            },
            'test_results': self.test_results
        }
        
        # Save report to file
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed test report saved to: test_report.json")
        return report

if __name__ == "__main__":
    tester = RiceMillSystemTester()
    results = tester.run_all_tests()
    tester.generate_test_report()
