"""
Test suite for Redis integration with AI Coordinator Agent
"""

import sys
import os
import unittest
import redis
import json
import time

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestRedisIntegration(unittest.TestCase):
    """Test cases for Redis integration"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            # Test connection
            self.redis_client.ping()
        except redis.ConnectionError:
            self.skipTest("Redis server not available")
    
    def test_redis_connection(self):
        """Test that we can connect to Redis"""
        self.assertTrue(self.redis_client.ping())
    
    def test_redis_set_get(self):
        """Test setting and getting values in Redis"""
        test_key = "test_key"
        test_value = "test_value"
        
        # Set value
        self.redis_client.set(test_key, test_value)
        
        # Get value
        retrieved_value = self.redis_client.get(test_key)
        
        self.assertEqual(retrieved_value, test_value)
        
        # Clean up
        self.redis_client.delete(test_key)
    
    def test_redis_queue_operations(self):
        """Test queue operations in Redis"""
        test_queue = "test_queue"
        test_message = {"id": "test-123", "data": "test data"}
        
        # Push message to queue
        self.redis_client.lpush(test_queue, json.dumps(test_message))
        
        # Pop message from queue
        retrieved_message = self.redis_client.rpop(test_queue)
        
        self.assertIsNotNone(retrieved_message)
        
        # Parse and verify message
        parsed_message = json.loads(retrieved_message)
        self.assertEqual(parsed_message["id"], test_message["id"])
        self.assertEqual(parsed_message["data"], test_message["data"])
    
    def test_redis_response_storage(self):
        """Test storing and retrieving responses in Redis"""
        test_request_id = "test-request-456"
        test_response = {
            "success": True,
            "data": "test response data",
            "request_id": test_request_id
        }
        
        # Store response
        response_key = f"response:{test_request_id}"
        self.redis_client.set(response_key, json.dumps(test_response))
        
        # Retrieve response
        retrieved_response = self.redis_client.get(response_key)
        
        self.assertIsNotNone(retrieved_response)
        
        # Parse and verify response
        parsed_response = json.loads(retrieved_response)
        self.assertEqual(parsed_response["success"], test_response["success"])
        self.assertEqual(parsed_response["data"], test_response["data"])
        self.assertEqual(parsed_response["request_id"], test_response["request_id"])
        
        # Clean up
        self.redis_client.delete(response_key)


if __name__ == '__main__':
    unittest.main()
