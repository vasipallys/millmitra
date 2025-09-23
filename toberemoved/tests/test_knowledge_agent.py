"""
Test suite for Knowledge Management Agent
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.knowledge_agent import KnowledgeManagementAgent


class TestKnowledgeManagementAgent(unittest.TestCase):
    """Test cases for the Knowledge Management Agent"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Redis client
        with patch('ai.knowledge_agent.redis.Redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            
            self.agent = KnowledgeManagementAgent()
            self.agent.redis_client = mock_redis_instance
    
    def test_initialization(self):
        """Test that the Knowledge Management agent initializes correctly"""
        self.assertIsInstance(self.agent, KnowledgeManagementAgent)
        self.assertIsNotNone(self.agent.redis_client)
        self.assertEqual(self.agent.queue_name, 'knowledge_queue')
        self.assertFalse(self.agent.running)
        self.assertIsNotNone(self.agent.index)
        self.assertIsInstance(self.agent.knowledge_base, dict)
        self.assertEqual(self.agent.id_counter, 0)
    
    def test_start_agent(self):
        """Test starting the Knowledge Management agent"""
        # Start the agent
        thread = self.agent.start()
        
        # Verify agent is running
        self.assertTrue(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:knowledge', 'online')
        
        # Verify thread was created
        self.assertIsNotNone(thread)
    
    def test_stop_agent(self):
        """Test stopping the Knowledge Management agent"""
        # Start the agent first
        self.agent.start()
        
        # Stop the agent
        self.agent.stop()
        
        # Verify agent is not running
        self.assertFalse(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:knowledge', 'offline')
    
    def test_handle_add_knowledge(self):
        """Test handling add knowledge task"""
        # Test data
        data = {
            'content': 'Test knowledge content',
            'embedding': [0.1] * 128,  # 128-dimensional embedding
            'metadata': {'source': 'test'}
        }
        
        # Handle the task
        result = self.agent._handle_add_knowledge(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['knowledge_id'], 0)
        
        # Verify knowledge was added
        self.assertEqual(len(self.agent.knowledge_base), 1)
        self.assertEqual(self.agent.id_counter, 1)
    
    def test_handle_retrieve_knowledge(self):
        """Test handling retrieve knowledge task"""
        # First add some knowledge
        add_data = {
            'content': 'Test knowledge content',
            'embedding': [0.1] * 128,
            'metadata': {'source': 'test'}
        }
        self.agent._handle_add_knowledge(add_data)
        
        # Test data
        data = {'knowledge_id': 0}
        
        # Handle the task
        result = self.agent._handle_retrieve_knowledge(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['content'], 'Test knowledge content')
        self.assertEqual(result['metadata'], {'source': 'test'})
    
    def test_handle_search_similar(self):
        """Test handling search similar task"""
        # First add some knowledge
        add_data = {
            'content': 'Test knowledge content',
            'embedding': [0.1] * 128,
            'metadata': {'source': 'test'}
        }
        self.agent._handle_add_knowledge(add_data)
        
        # Test data
        data = {
            'embedding': [0.1] * 128,
            'top_k': 5
        }
        
        # Handle the task
        result = self.agent._handle_search_similar(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['content'], 'Test knowledge content')
    
    def test_handle_update_knowledge(self):
        """Test handling update knowledge task"""
        # First add some knowledge
        add_data = {
            'content': 'Original content',
            'embedding': [0.1] * 128,
            'metadata': {'source': 'test'}
        }
        self.agent._handle_add_knowledge(add_data)
        
        # Test data
        data = {
            'knowledge_id': 0,
            'content': 'Updated content',
            'embedding': [0.2] * 128,
            'metadata': {'source': 'updated_test'}
        }
        
        # Handle the task
        result = self.agent._handle_update_knowledge(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['knowledge_id'], 0)
        
        # Verify knowledge was updated
        knowledge = self.agent.knowledge_base[0]
        self.assertEqual(knowledge['content'], 'Updated content')
        self.assertEqual(knowledge['metadata'], {'source': 'updated_test'})
    
    def test_handle_delete_knowledge(self):
        """Test handling delete knowledge task"""
        # First add some knowledge
        add_data = {
            'content': 'Test knowledge content',
            'embedding': [0.1] * 128,
            'metadata': {'source': 'test'}
        }
        self.agent._handle_add_knowledge(add_data)
        
        # Test data
        data = {'knowledge_id': 0}
        
        # Handle the task
        result = self.agent._handle_delete_knowledge(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['knowledge_id'], 0)
        
        # Verify knowledge was deleted
        self.assertEqual(len(self.agent.knowledge_base), 0)
    
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
