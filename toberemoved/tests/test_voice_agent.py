"""
Test suite for Voice Processing Agent
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.voice_agent import VoiceProcessingAgent


class TestVoiceProcessingAgent(unittest.TestCase):
    """Test cases for the Voice Processing Agent"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Redis client and speech recognizer
        with patch('ai.voice_agent.redis.Redis') as mock_redis, \
             patch('ai.voice_agent.sr.Recognizer') as mock_recognizer, \
             patch('ai.voice_agent.sr.Microphone') as mock_microphone:
            
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            
            mock_recognizer_instance = MagicMock()
            mock_recognizer.return_value = mock_recognizer_instance
            
            mock_microphone_instance = MagicMock()
            mock_microphone.return_value = mock_microphone_instance
            
            self.agent = VoiceProcessingAgent()
            self.agent.redis_client = mock_redis_instance
            self.agent.recognizer = mock_recognizer_instance
            self.agent.microphone = mock_microphone_instance
    
    def test_initialization(self):
        """Test that the Voice agent initializes correctly"""
        self.assertIsInstance(self.agent, VoiceProcessingAgent)
        self.assertIsNotNone(self.agent.redis_client)
        self.assertIsNotNone(self.agent.recognizer)
        self.assertIsNotNone(self.agent.microphone)
        self.assertEqual(self.agent.queue_name, 'voice_queue')
        self.assertFalse(self.agent.running)
    
    def test_start_agent(self):
        """Test starting the Voice agent"""
        # Start the agent
        thread = self.agent.start()
        
        # Verify agent is running
        self.assertTrue(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:voice', 'online')
        
        # Verify thread was created
        self.assertIsNotNone(thread)
    
    def test_stop_agent(self):
        """Test stopping the Voice agent"""
        # Start the agent first
        self.agent.start()
        
        # Stop the agent
        self.agent.stop()
        
        # Verify agent is not running
        self.assertFalse(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:voice', 'offline')
    
    def test_handle_voice_recognition_with_audio_data(self):
        """Test handling voice recognition task with provided audio data"""
        # Test data
        data = {'audio_data': 'base64audiodata'}
        
        # Handle the task
        result = self.agent._handle_voice_recognition(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['text'], 'Mock recognized text from provided audio')
        self.assertEqual(result['confidence'], 0.95)
    
    def test_handle_voice_command(self):
        """Test handling voice command task"""
        # Mock the voice recognition method
        self.agent._handle_voice_recognition = MagicMock(return_value={
            'success': True,
            'text': 'Production status'
        })
        
        # Test data
        data = {}
        
        # Handle the task
        result = self.agent._handle_voice_command(data)
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertEqual(result['command'], 'Production status')
        self.assertIn('Current production status', result['response'])
    
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
