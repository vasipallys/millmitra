"""
Test suite for Analytics Agent
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.analytics_agent import AnalyticsAgent


class TestAnalyticsAgent(unittest.TestCase):
    """Test cases for the Analytics Agent"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Redis client
        with patch('ai.analytics_agent.redis.Redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            
            self.agent = AnalyticsAgent()
            self.agent.redis_client = mock_redis_instance
    
    def test_initialization(self):
        """Test that the Analytics agent initializes correctly"""
        self.assertIsInstance(self.agent, AnalyticsAgent)
        self.assertIsNotNone(self.agent.redis_client)
        self.assertEqual(self.agent.queue_name, 'analytics_queue')
        self.assertFalse(self.agent.running)
        self.assertIsInstance(self.agent.models, dict)
    
    def test_start_agent(self):
        """Test starting the Analytics agent"""
        # Start the agent
        thread = self.agent.start()
        
        # Verify agent is running
        self.assertTrue(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:analytics', 'online')
        
        # Verify thread was created
        self.assertIsNotNone(thread)
    
    def test_stop_agent(self):
        """Test stopping the Analytics agent"""
        # Start the agent first
        self.agent.start()
        
        # Stop the agent
        self.agent.stop()
        
        # Verify agent is not running
        self.assertFalse(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:analytics', 'offline')
    
    def test_handle_predictive_maintenance(self):
        """Test handling predictive maintenance task"""
        # Test data
        data = {
            'equipment_data': [
                {'equipment_id': 'EQ001', 'hours_of_operation': 1200},
                {'equipment_id': 'EQ002', 'hours_of_operation': 800}
            ]
        }
        
        # Handle the task
        result = self.agent._handle_predictive_maintenance(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(len(result['predictions']), 2)
        
        # Verify first equipment prediction
        first_prediction = result['predictions'][0]
        self.assertEqual(first_prediction['equipment_id'], 'EQ001')
        self.assertGreaterEqual(first_prediction['risk_score'], 0)
        self.assertLessEqual(first_prediction['risk_score'], 100)
    
    def test_handle_production_forecast(self):
        """Test handling production forecast task"""
        # Test data
        data = {
            'historical_data': [
                {'date': '2023-01-01', 'production': 100},
                {'date': '2023-01-02', 'production': 110},
                {'date': '2023-01-03', 'production': 120}
            ]
        }
        
        # Handle the task
        result = self.agent._handle_production_forecast(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['forecast'], 0)
        self.assertEqual(len(result['confidence_interval']), 2)
        self.assertIn(result['trend'], ['increasing', 'decreasing', 'stable'])
    
    def test_handle_quality_analysis(self):
        """Test handling quality analysis task"""
        # Test data
        data = {
            'quality_data': [
                {'batch_id': 'B001', 'quality_score': 85},
                {'batch_id': 'B002', 'quality_score': 90},
                {'batch_id': 'B003', 'quality_score': 75}
            ]
        }
        
        # Handle the task
        result = self.agent._handle_quality_analysis(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['average_quality'], 0)
        self.assertGreaterEqual(result['quality_std'], 0)
        self.assertGreaterEqual(result['outliers_count'], 0)
    
    def test_handle_anomaly_detection(self):
        """Test handling anomaly detection task"""
        # Test data
        data = {
            'sensor_data': [
                {'timestamp': '2023-01-01T10:00:00', 'temperature': 25, 'humidity': 60},
                {'timestamp': '2023-01-01T11:00:00', 'temperature': 26, 'humidity': 62},
                {'timestamp': '2023-01-01T12:00:00', 'temperature': 100, 'humidity': 61}  # Anomaly
            ]
        }
        
        # Handle the task
        result = self.agent._handle_anomaly_detection(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertGreaterEqual(result['anomalies_count'], 0)
    
    def test_process_task_unknown_type(self):
        """Test processing task with unknown type"""
        # Mock Redis set method
        self.agent.redis_client.set = MagicMock()
        
        # Test task with unknown type
        task_json = '{"request_id": "test-123", "task_type": "unknown_task", "data": {}}'
        
        # Process the task
        self.agent._process_task(task_json)
        
        # Verify Redis set was called to store error response
        self.agent.redis_client.set.assert_called()


if __name__ == '__main__':
    unittest.main()
