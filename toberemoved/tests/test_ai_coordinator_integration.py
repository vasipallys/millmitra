"""
Integration test suite for AI Coordinator Agent
"""

import sys
import os
import unittest
import requests
import json
import time

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestAICoordinatorIntegration(unittest.TestCase):
    """Integration test cases for the AI Coordinator Agent"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.base_url = "http://localhost:5005/api/ai-coordinator"
        
    def test_health_check(self):
        """Test that the AI Coordinator Agent health check endpoint works"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('status', data)
            self.assertIn('agent_status', data)
            self.assertEqual(data['status'], 'healthy')
            
        except requests.exceptions.ConnectionError:
            self.skipTest("AI Coordinator Agent not available")
        except requests.exceptions.Timeout:
            self.skipTest("AI Coordinator Agent health check timed out")
    
    def test_process_request_missing_data(self):
        """Test processing request with missing data"""
        try:
            response = requests.post(f"{self.base_url}/process", json={}, timeout=5)
            self.assertEqual(response.status_code, 400)
            
            data = response.json()
            self.assertFalse(data['success'])
            self.assertIn('No data provided', data['error'])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("AI Coordinator Agent not available")
        except requests.exceptions.Timeout:
            self.skipTest("AI Coordinator Agent request timed out")
    
    def test_process_request_missing_task_type(self):
        """Test processing request with missing task type"""
        try:
            response = requests.post(f"{self.base_url}/process", 
                                   json={'data': {'query': 'test query'}}, 
                                   timeout=5)
            self.assertEqual(response.status_code, 400)
            
            data = response.json()
            self.assertFalse(data['success'])
            self.assertIn('Task type is required', data['error'])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("AI Coordinator Agent not available")
        except requests.exceptions.Timeout:
            self.skipTest("AI Coordinator Agent request timed out")
    
    def test_process_request_unknown_task(self):
        """Test processing request with unknown task type"""
        try:
            response = requests.post(f"{self.base_url}/process", 
                                   json={'task_type': 'unknown_task', 'data': {}}, 
                                   timeout=5)
            self.assertEqual(response.status_code, 400)
            
            data = response.json()
            self.assertFalse(data['success'])
            self.assertIn('No agent found', data['error'])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("AI Coordinator Agent not available")
        except requests.exceptions.Timeout:
            self.skipTest("AI Coordinator Agent request timed out")
    
    def test_process_request_valid_nlp_task(self):
        """Test processing a valid NLP task request"""
        try:
            response = requests.post(f"{self.base_url}/process", 
                                   json={'task_type': 'query_processing', 
                                         'data': {'query': 'What is the production status?'}}, 
                                   timeout=5)
            # Should return 202 (Accepted) for valid requests
            self.assertEqual(response.status_code, 202)
            
            data = response.json()
            self.assertTrue(data['success'])
            self.assertIn('request_id', data)
            self.assertEqual(data['target_agent'], 'nlp')
            
        except requests.exceptions.ConnectionError:
            self.skipTest("AI Coordinator Agent not available")
        except requests.exceptions.Timeout:
            self.skipTest("AI Coordinator Agent request timed out")


if __name__ == '__main__':
    unittest.main()
