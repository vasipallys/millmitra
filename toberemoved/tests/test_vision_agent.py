"""
Test suite for Vision Analysis Agent
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai.vision_agent import VisionAnalysisAgent


class TestVisionAnalysisAgent(unittest.TestCase):
    """Test cases for the Vision Analysis Agent"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock Redis client
        with patch('ai.vision_agent.redis.Redis') as mock_redis:
            mock_redis_instance = MagicMock()
            mock_redis.return_value = mock_redis_instance
            
            self.agent = VisionAnalysisAgent()
            self.agent.redis_client = mock_redis_instance
    
    def test_initialization(self):
        """Test that the Vision agent initializes correctly"""
        self.assertIsInstance(self.agent, VisionAnalysisAgent)
        self.assertIsNotNone(self.agent.redis_client)
        self.assertEqual(self.agent.queue_name, 'vision_queue')
        self.assertFalse(self.agent.running)
    
    def test_start_agent(self):
        """Test starting the Vision agent"""
        # Start the agent
        thread = self.agent.start()
        
        # Verify agent is running
        self.assertTrue(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:vision', 'online')
        
        # Verify thread was created
        self.assertIsNotNone(thread)
    
    def test_stop_agent(self):
        """Test stopping the Vision agent"""
        # Start the agent first
        self.agent.start()
        
        # Stop the agent
        self.agent.stop()
        
        # Verify agent is not running
        self.assertFalse(self.agent.running)
        
        # Verify Redis status update
        self.agent.redis_client.set.assert_called_with('agent_status:vision', 'offline')
    
    def test_handle_quality_assessment(self):
        """Test handling quality assessment task"""
        # Mock the helper methods
        self.agent._calculate_quality_score = MagicMock(return_value=85.5)
        self.agent._detect_defects = MagicMock(return_value=[{'type': 'broken', 'count': 2}])
        
        # Mock base64 decoding and image processing
        with patch('ai.vision_agent.base64.b64decode') as mock_decode, \
             patch('ai.vision_agent.Image.open') as mock_image, \
             patch('ai.vision_agent.cv2.cvtColor') as mock_cvt_color:
            
            mock_decode.return_value = b'test'
            mock_image.return_value = MagicMock()
            mock_cvt_color.return_value = MagicMock()
            
            # Test data
            data = {'image_data': 'base64imagestring'}
            
            # Handle the task
            result = self.agent._handle_quality_assessment(data)
            
            # Verify result
            self.assertTrue(result['success'])
            self.assertEqual(result['quality_score'], 85.5)
            self.assertEqual(result['defects'], [{'type': 'broken', 'count': 2}])
    
    def test_handle_object_detection(self):
        """Test handling object detection task"""
        # Mock the helper method
        self.agent._detect_objects = MagicMock(return_value=[{'label': 'rice_grain', 'confidence': 0.95}])
        
        # Mock base64 decoding and image processing
        with patch('ai.vision_agent.base64.b64decode') as mock_decode, \
             patch('ai.vision_agent.Image.open') as mock_image, \
             patch('ai.vision_agent.cv2.cvtColor') as mock_cvt_color:
            
            mock_decode.return_value = b'test'
            mock_image.return_value = MagicMock()
            mock_cvt_color.return_value = MagicMock()
            
            # Test data
            data = {'image_data': 'base64imagestring'}
            
            # Handle the task
            result = self.agent._handle_object_detection(data)
            
            # Verify result
            self.assertTrue(result['success'])
            self.assertEqual(result['objects'], [{'label': 'rice_grain', 'confidence': 0.95}])
    
    def test_handle_image_analysis(self):
        """Test handling image analysis task"""
        # Mock the helper methods
        self.agent._calculate_brightness = MagicMock(return_value=120.5)
        self.agent._calculate_contrast = MagicMock(return_value=45.3)
        self.agent._calculate_color_balance = MagicMock(return_value={'red': 100.2, 'green': 95.7, 'blue': 88.9})
        
        # Mock base64 decoding and image processing
        with patch('ai.vision_agent.base64.b64decode') as mock_decode, \
             patch('ai.vision_agent.Image.open') as mock_image, \
             patch('ai.vision_agent.cv2.cvtColor') as mock_cvt_color:
            
            mock_decode.return_value = b'test'
            mock_image.return_value = MagicMock()
            mock_cvt_color.return_value = MagicMock()
            
            # Test data
            data = {'image_data': 'base64imagestring'}
            
            # Handle the task
            result = self.agent._handle_image_analysis(data)
            
            # Verify result
            self.assertTrue(result['success'])
            self.assertEqual(result['brightness'], 120.5)
            self.assertEqual(result['contrast'], 45.3)
            self.assertEqual(result['color_balance'], {'red': 100.2, 'green': 95.7, 'blue': 88.9})
    
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
