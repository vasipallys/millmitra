"""
Test suite for NLP Processing Agent
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.nlp_agent import NLPProcessingAgent


class TestNLPProcessingAgent(unittest.TestCase):
    """Test cases for the NLP Processing Agent"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Redis client
        with patch('ai.nlp_agent.redis.Redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            
            # Mock EnhancedNLPProcessor
            with patch('ai.nlp_agent.EnhancedNLPProcessor') as mock_nlp:
                mock_nlp_instance = MagicMock()
                mock_nlp.return_value = mock_nlp_instance
                
                self.agent = NLPProcessingAgent()
                self.agent.redis_client = mock_redis_instance
                self.agent.nlp_processor = mock_nlp_instance
    
    def test_initialization(self):
        """Test that the NLP agent initializes correctly"""
        self.assertIsInstance(self.agent, NLPProcessingAgent)
        self.assertIsNotNone(self.agent.redis_client)
        self.assertIsNotNone(self.agent.nlp_processor)
        self.assertEqual(self.agent.queue_name, 'nlp_queue')
        self.assertFalse(self.agent.running)
    
    def test_start_agent(self):
        """Test starting the NLP agent"""
        # Start the agent
        thread = self.agent.start()
        
        # Verify agent is running
        self.assertTrue(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:nlp', 'online')
        
        # Verify thread was created
        self.assertIsNotNone(thread)
    
    def test_stop_agent(self):
        """Test stopping the NLP agent"""
        # Start the agent first
        self.agent.start()
        
        # Stop the agent
        self.agent.stop()
        
        # Verify agent is not running
        self.assertFalse(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:nlp', 'offline')
    
    def test_handle_query_processing(self):
        """Test handling query processing task"""
        # Mock NLP processor response
        mock_result = {'success': True, 'response': 'Test response'}
        self.agent.nlp_processor.process_query.return_value = mock_result
        
        # Test data
        data = {'query': 'test query', 'user_context': {}}
        
        # Handle the task
        result = self.agent._handle_query_processing(data)
        
        # Verify result
        self.assertEqual(result, mock_result)
        
        # Verify NLP processor was called
        self.agent.nlp_processor.process_query.assert_called_with('test query', {})
    
    def test_handle_intent_classification(self):
        """Test handling intent classification task"""
        # Mock NLP processor response
        mock_intent = 'information_request'
        self.agent.nlp_processor._classify_intent.return_value = mock_intent
        
        # Test data
        data = {'query': 'test query'}
        
        # Handle the task
        result = self.agent._handle_intent_classification(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['intent'], mock_intent)
        
        # Verify NLP processor was called
        self.agent.nlp_processor._classify_intent.assert_called_with('test query')
    
    def test_handle_entity_extraction(self):
        """Test handling entity extraction task"""
        # Mock NLP processor response
        mock_entities = ['entity1', 'entity2']
        self.agent.nlp_processor._extract_entities.return_value = mock_entities
        
        # Test data
        data = {'query': 'test query'}
        
        # Handle the task
        result = self.agent._handle_entity_extraction(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['entities'], mock_entities)
        
        # Verify NLP processor was called
        self.agent.nlp_processor._extract_entities.assert_called_with('test query')
    
    def test_handle_sentiment_analysis(self):
        """Test handling sentiment analysis task"""
        # Mock NLP processor response
        mock_sentiment = {'polarity': 0.5, 'subjectivity': 0.3}
        self.agent.nlp_processor._analyze_sentiment.return_value = mock_sentiment
        
        # Test data
        data = {'query': 'test query'}
        
        # Handle the task
        result = self.agent._handle_sentiment_analysis(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['sentiment'], mock_sentiment)
        
        # Verify NLP processor was called
        self.agent.nlp_processor._analyze_sentiment.assert_called_with('test query')
    
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
