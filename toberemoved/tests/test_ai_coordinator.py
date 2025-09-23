"""
Test suite for AI Coordinator Agent
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.ai_coordinator import AICoordinator


class TestAICoordinator(unittest.TestCase):
    """Test cases for the AI Coordinator Agent"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.coordinator = AICoordinator()
        # Mock Redis client
        self.coordinator.redis_client = MagicMock()
    
    def test_initialization(self):
        """Test that the coordinator initializes correctly"""
        self.assertIsInstance(self.coordinator, AICoordinator)
        self.assertIsNotNone(self.coordinator.redis_client)
        self.assertIn('nlp', self.coordinator.agent_registry)
        self.assertIn('vision', self.coordinator.agent_registry)
        self.assertIn('voice', self.coordinator.agent_registry)
        self.assertIn('analytics', self.coordinator.agent_registry)
        self.assertIn('knowledge', self.coordinator.agent_registry)
    
    def test_agent_registration(self):
        """Test agent registration functionality"""
        initial_agent_count = len(self.coordinator.agent_registry)
        self.coordinator.register_agent('test_agent', 'test_queue')
        self.assertEqual(len(self.coordinator.agent_registry), initial_agent_count + 1)
        self.assertIn('test_agent', self.coordinator.agent_registry)
        self.assertEqual(self.coordinator.agent_registry['test_agent'], 'test_queue')
    
    def test_agent_status_updates(self):
        """Test agent status update functionality"""
        # Register a test agent
        self.coordinator.register_agent('test_agent', 'test_queue')
        
        # Update status
        self.coordinator.update_agent_status('test_agent', 'online')
        status = self.coordinator.get_agent_status()
        self.assertEqual(status['test_agent'], 'online')
        
        # Update to different status
        self.coordinator.update_agent_status('test_agent', 'busy')
        status = self.coordinator.get_agent_status()
        self.assertEqual(status['test_agent'], 'busy')
    
    def test_determine_target_agent(self):
        """Test agent determination logic"""
        # Test NLP tasks
        self.assertEqual(self.coordinator._determine_target_agent('query_processing'), 'nlp')
        self.assertEqual(self.coordinator._determine_target_agent('intent_classification'), 'nlp')
        
        # Test Vision tasks
        self.assertEqual(self.coordinator._determine_target_agent('image_analysis'), 'vision')
        self.assertEqual(self.coordinator._determine_target_agent('quality_assessment'), 'vision')
        
        # Test Voice tasks
        self.assertEqual(self.coordinator._determine_target_agent('voice_recognition'), 'voice')
        
        # Test Analytics tasks
        self.assertEqual(self.coordinator._determine_target_agent('demand_prediction'), 'analytics')
        
        # Test Knowledge tasks
        self.assertEqual(self.coordinator._determine_target_agent('knowledge_retrieval'), 'knowledge')
        
        # Test unknown task
        self.assertIsNone(self.coordinator._determine_target_agent('unknown_task'))
    
    @patch('ai.ai_coordinator.uuid.uuid4')
    def test_route_request_success(self, mock_uuid):
        """Test successful request routing"""
        # Mock UUID generation
        mock_uuid.return_value = 'test-request-id'
        
        # Mock Redis lpush
        self.coordinator.redis_client.lpush = MagicMock()
        
        # Test routing to NLP agent
        result = self.coordinator.route_request('query_processing', {'query': 'test query'})
        
        self.assertTrue(result['success'])
        self.assertEqual(result['request_id'], 'test-request-id')
        self.assertEqual(result['target_agent'], 'nlp')
        
        # Verify Redis lpush was called
        self.coordinator.redis_client.lpush.assert_called_once()
    
    def test_route_request_unknown_task(self):
        """Test routing failure for unknown task type"""
        result = self.coordinator.route_request('unknown_task', {})
        
        self.assertFalse(result['success'])
        self.assertIn('No agent found', result['error'])
    
    def test_get_response_success(self):
        """Test successful response retrieval"""
        # Mock Redis response
        mock_response = '{"success": true, "data": "test response"}'
        self.coordinator.redis_client.get.return_value = mock_response
        self.coordinator.redis_client.delete = MagicMock()
        
        result = self.coordinator.get_response('test-request-id')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data'], 'test response')
        
        # Verify Redis get and delete were called
        self.coordinator.redis_client.get.assert_called_with('response:test-request-id')
        self.coordinator.redis_client.delete.assert_called_with('response:test-request-id')
    
    def test_get_response_not_available(self):
        """Test response retrieval when response is not available"""
        # Mock Redis response as None
        self.coordinator.redis_client.get.return_value = None
        
        result = self.coordinator.get_response('test-request-id')
        
        self.assertFalse(result['success'])
        self.assertIn('Response not available', result['error'])


if __name__ == '__main__':
    unittest.main()
