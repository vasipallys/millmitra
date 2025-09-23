import redis
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from config import Config

print("Testing Redis connection with session manager configuration...")

# Use the same Redis URL as the session manager
redis_url = Config.SESSION_REDIS_URL
print(f"Redis URL: {redis_url}")

try:
    # Try to connect to Redis
    redis_client = redis.from_url(redis_url, decode_responses=True)
    
    # Test connection
    redis_client.ping()
    print("Successfully connected to Redis!")
    
    # Test setting and getting a value
    test_key = "rice_mill_test"
    test_value = "test_value"
    
    redis_client.set(test_key, test_value)
    retrieved_value = redis_client.get(test_key)
    
    if retrieved_value == test_value:
        print("Successfully set and retrieved test value from Redis!")
    else:
        print(f"Error: Expected '{test_value}', got '{retrieved_value}'")
    
    # Clean up
    redis_client.delete(test_key)
    
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
    import traceback
    traceback.print_exc()
