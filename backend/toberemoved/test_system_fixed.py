"""
Comprehensive System Testing Script (Fixed)
Tests all major functionalities of the Rice Mill Management System with correct endpoint URLs
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
        
        status = "PASS" if success else "FAIL"
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
            # Test user login with existing admin user
            login_data = {
                "username": "admin",
                "password": "admin123"
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
            # Test voice recognition (corrected endpoint)
            voice_data = {
                "audio_data": "mock_audio_data",
                "language": "en"
            }
            
            response = requests.post(f"{self.base_url}/api/ai-services/voice/recognize", 
                                   json=voice_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("Voice Recognition", True, "Voice recognition endpoint working")
            else:
                self.log_test("Voice Recognition", False, f"Voice recognition failed - Status: {response.status_code}")
            
            # Test quality assessment (corrected endpoint)
            quality_data = {
                "image_data": "mock_image_data",
                "batch_id": "TEST001"
            }
            
            response = requests.post(f"{self.base_url}/api/ai-services/quality/assess", 
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
            # Test quality test creation (corrected endpoint)
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
            # Test payment prediction (corrected endpoint)
            payment_data = {
                "customer_id": 1,
                "amount": 50000,
                "due_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            # Using a valid endpoint from financial intelligence
            response = requests.post(f"{self.base_url}/api/financial-intelligence/cash-flow/analyze", 
                                   json={'period_days': 30}, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("Cash Flow Analysis", True, "Cash flow analysis working")
            else:
                self.log_test("Cash Flow Analysis", False, f"Cash flow analysis failed - Status: {response.status_code}")
            
            # Test financial insights (corrected endpoint)
            response = requests.get(f"{self.base_url}/api/financial-intelligence/insights", 
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
            # Test GST calculation (corrected endpoint)
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
            
            # Test compliance status (corrected endpoint)
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
            # Test KPI calculation (using a valid endpoint)
            kpi_data = {
                "report_type": "production",
                "period": {
                    "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                    "end_date": datetime.now().isoformat()
                }
            }
            
            response = requests.post(f"{self.base_url}/api/analytics/reports/generate", 
                                   json=kpi_data, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                self.log_test("Report Generation", True, "Report generation working")
            else:
                self.log_test("Report Generation", False, f"Report generation failed - Status: {response.status_code}")
            
            # Test dashboard overview (corrected endpoint)
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
        print("Starting Rice Mill Management System Tests...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Core system tests
        tests = [
            self.test_health_check,
            self.test_user_authentication,
            self.test_database_operations,
            self.test_ai_services,
            self.test_quality_control,
            self.test_financial_intelligence,
            self.test_compliance_gst,
            self.test_analytics_reporting
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Small delay between tests
        
        # Summary
        end_time = time.time()
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "Success Rate: 0%")
        print(f"Execution Time: {end_time - start_time:.2f} seconds")
        
        # Show failed tests
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = RiceMillSystemTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
