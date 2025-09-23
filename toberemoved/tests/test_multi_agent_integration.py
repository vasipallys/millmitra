"""
Integration test suite for Multi-Agent AI Architecture
"""

import sys
import os
import unittest
import time
import json
import redis
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.ai_coordinator import AICoordinator


class TestMultiAgentIntegration(unittest.TestCase):
    """Integration test cases for the Multi-Agent AI Architecture"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Redis client
        with patch('ai.ai_coordinator.redis.Redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            
            self.coordinator = AICoordinator()
            self.coordinator.redis_client = mock_redis_instance
            
            # Mock agent status
            self.coordinator.agent_status = {
                'nlp': 'online',
                'vision': 'online',
                'voice': 'online',
                'analytics': 'online',
                'knowledge': 'online'
            }
    
    def test_nlp_task_processing(self):
        """Test processing an NLP task through the coordinator"""
        # Mock Redis methods
        self.coordinator.redis_client.lpush = MagicMock()
        self.coordinator.redis_client.get = MagicMock(return_value=json.dumps({
            'success': True,
            'response': 'Processed NLP task'
        }))
        
        # Test data
        task_data = {
            'text': 'What is the current production status?',
            'context': {}
        }
        
        # Process the task
        response = self.coordinator.process_nlp_task(task_data)
        
        # Verify result
        self.assertTrue(response['success'])
        self.assertEqual(response['response'], 'Processed NLP task')
        
        # Verify Redis interactions
        self.coordinator.redis_client.lpush.assert_called()
        self.coordinator.redis_client.get.assert_called()
    
    def test_vision_task_processing(self):
        """Test processing a vision task through the coordinator"""
        # Mock Redis methods
        self.coordinator.redis_client.lpush = MagicMock()
        self.coordinator.redis_client.get = MagicMock(return_value=json.dumps({
            'success': True,
            'quality_score': 85.5,
            'defects': [{'type': 'broken', 'count': 2}]
        }))
        
        # Test data
        task_data = {
            'image_data': 'base64imagestring',
            'task_type': 'quality_assessment'
        }
        
        # Process the task
        response = self.coordinator.process_vision_task(task_data)
        
        # Verify result
        self.assertTrue(response['success'])
        self.assertEqual(response['quality_score'], 85.5)
        self.assertEqual(response['defects'], [{'type': 'broken', 'count': 2}])
        
        # Verify Redis interactions
        self.coordinator.redis_client.lpush.assert_called()
        self.coordinator.redis_client.get.assert_called()
    
    def test_voice_task_processing(self):
        """Test processing a voice task through the coordinator"""
        # Mock Redis methods
        self.coordinator.redis_client.lpush = MagicMock()
        self.coordinator.redis_client.get = MagicMock(return_value=json.dumps({
            'success': True,
            'text': 'Production status command',
            'response': 'Current production status: 85% capacity'
        }))
        
        # Test data
        task_data = {
            'audio_data': 'base64audiodata',
            'task_type': 'voice_command'
        }
        
        # Process the task
        response = self.coordinator.process_voice_task(task_data)
        
        # Verify result
        self.assertTrue(response['success'])
        self.assertEqual(response['text'], 'Production status command')
        self.assertIn('Current production status', response['response'])
        
        # Verify Redis interactions
        self.coordinator.redis_client.lpush.assert_called()
        self.coordinator.redis_client.get.assert_called()
    
    def test_analytics_task_processing(self):
        """Test processing an analytics task through the coordinator"""
        # Mock Redis methods
        self.coordinator.redis_client.lpush = MagicMock()
        self.coordinator.redis_client.get = MagicMock(return_value=json.dumps({
            'success': True,
            'forecast': 115.5,
            'confidence_interval': [100.0, 130.0],
            'trend': 'increasing'
        }))
        
        # Test data
        task_data = {
            'historical_data': [
                {'date': '2023-01-01', 'production': 100},
                {'date': '2023-01-02', 'production': 110},
                {'date': '2023-01-03', 'production': 120}
            ],
            'task_type': 'production_forecast'
        }
        
        # Process the task
        response = self.coordinator.process_analytics_task(task_data)
        
        # Verify result
        self.assertTrue(response['success'])
        self.assertEqual(response['forecast'], 115.5)
        self.assertEqual(response['confidence_interval'], [100.0, 130.0])
        self.assertEqual(response['trend'], 'increasing')
        
        # Verify Redis interactions
        self.coordinator.redis_client.lpush.assert_called()
        self.coordinator.redis_client.get.assert_called()
    
    def test_knowledge_task_processing(self):
        """Test processing a knowledge task through the coordinator"""
        # Mock Redis methods
        self.coordinator.redis_client.lpush = MagicMock()
        self.coordinator.redis_client.get = MagicMock(return_value=json.dumps({
            'success': True,
            'results': [
                {
                    'knowledge_id': 0,
                    'content': 'Rice milling procedure',
                    'metadata': {'source': 'manual'},
                    'distance': 0.1
                }
            ]
        }))
        
        # Test data
        task_data = {
            'embedding': [0.1] * 128,
            'top_k': 5,
            'task_type': 'search_similar'
        }
        
        # Process the task
        response = self.coordinator.process_knowledge_task(task_data)
        
        # Verify result
        self.assertTrue(response['success'])
        self.assertEqual(len(response['results']), 1)
        self.assertEqual(response['results'][0]['content'], 'Rice milling procedure')
        
        # Verify Redis interactions
        self.coordinator.redis_client.lpush.assert_called()
        self.coordinator.redis_client.get.assert_called()
    
    def test_agent_status_check(self):
        """Test checking agent status through the coordinator"""
        # Mock Redis hgetall method
        self.coordinator.redis_client.hgetall = MagicMock(return_value={
            'nlp': 'online',
            'vision': 'online',
            'voice': 'online',
            'analytics': 'online',
            'knowledge': 'online'
        })
        
        # Check agent status
        status = self.coordinator.get_agent_status()
        
        # Verify result
        self.assertIsInstance(status, dict)
        self.assertEqual(len(status), 5)
        self.assertEqual(status['nlp'], 'online')
        self.assertEqual(status['vision'], 'online')
        self.assertEqual(status['voice'], 'online')
        self.assertEqual(status['analytics'], 'online')
        self.assertEqual(status['knowledge'], 'online')
    
    def test_coordinator_health_check(self):
        """Test coordinator health check"""
        # Mock Redis ping method
        self.coordinator.redis_client.ping = MagicMock(return_value=True)
        
        # Check health
        health = self.coordinator.health_check()
        
        # Verify result
        self.assertTrue(health)


if __name__ == '__main__':
    unittest.main()
