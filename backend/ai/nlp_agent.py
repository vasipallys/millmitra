"""
NLP Processing Agent for Rice Mill Management System
Handles natural language processing tasks in the multi-agent AI architecture.
"""

import json
import logging
import redis
import threading
import time
from typing import Dict, Any

# Import the enhanced NLP processor
from backend.ai.enhanced_nlp import EnhancedNLPProcessor


class NLPProcessingAgent:
    """NLP Processing Agent that handles NLP tasks from the AI Coordinator"""
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        """Initialize the NLP Processing Agent"""
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.nlp_processor = EnhancedNLPProcessor()
        self.queue_name = 'nlp_queue'
        self.running = False
        self.logger.info("NLP Processing Agent initialized")
    
    def start(self):
        """Start the NLP Processing Agent"""
        self.running = True
        self.logger.info("NLP Processing Agent started")
        
        # Start processing loop in a separate thread
        processing_thread = threading.Thread(target=self._processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
        
        # Notify coordinator that agent is online
        self.redis_client.set('agent_status:nlp', 'online')
        
        return processing_thread
    
    def stop(self):
        """Stop the NLP Processing Agent"""
        self.running = False
        self.logger.info("NLP Processing Agent stopped")
        
        # Notify coordinator that agent is offline
        self.redis_client.set('agent_status:nlp', 'offline')
    
    def _processing_loop(self):
        """Main processing loop for handling NLP tasks"""
        self.logger.info("NLP Processing Agent listening for tasks")
        
        while self.running:
            try:
                # Block until a task is available
                task_data = self.redis_client.brpop(self.queue_name, timeout=1)
                
                if task_data:
                    # Process the task
                    self._process_task(task_data[1])
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {str(e)}")
                time.sleep(1)  # Wait before retrying
    
    def _process_task(self, task_json: str):
        """Process a single NLP task"""
        try:
            # Parse the task
            task = json.loads(task_json)
            request_id = task.get('request_id')
            task_type = task.get('task_type')
            data = task.get('data', {})
            
            self.logger.info(f"Processing NLP task {task_type} with request ID {request_id}")
            
            # Update agent status to busy
            self.redis_client.set('agent_status:nlp', 'busy')
            
            # Process based on task type
            if task_type == 'query_processing':
                result = self._handle_query_processing(data)
            elif task_type == 'intent_classification':
                result = self._handle_intent_classification(data)
            elif task_type == 'entity_extraction':
                result = self._handle_entity_extraction(data)
            elif task_type == 'sentiment_analysis':
                result = self._handle_sentiment_analysis(data)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown NLP task type: {task_type}'
                }
            
            # Add request ID to result
            result['request_id'] = request_id
            
            # Store result in Redis
            response_key = f"response:{request_id}"
            self.redis_client.set(response_key, json.dumps(result))
            
            self.logger.info(f"NLP task {request_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error processing NLP task: {str(e)}")
            
            # Store error result
            if 'request_id' in locals():
                error_result = {
                    'success': False,
                    'error': f'NLP processing error: {str(e)}',
                    'request_id': request_id
                }
                response_key = f"response:{request_id}"
                self.redis_client.set(response_key, json.dumps(error_result))
        
        finally:
            # Update agent status back to online
            self.redis_client.set('agent_status:nlp', 'online')
    
    def _handle_query_processing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query processing task"""
        query = data.get('query', '')
        user_context = data.get('user_context', {})
        
        # Process the query using the enhanced NLP processor
        result = self.nlp_processor.process_query(query, user_context)
        
        return result
    
    def _handle_intent_classification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle intent classification task"""
        query = data.get('query', '')
        
        # Classify intent using the enhanced NLP processor
        intent = self.nlp_processor._classify_intent(query)
        
        return {
            'success': True,
            'intent': intent
        }
    
    def _handle_entity_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle entity extraction task"""
        query = data.get('query', '')
        
        # Extract entities using the enhanced NLP processor
        entities = self.nlp_processor._extract_entities(query)
        
        return {
            'success': True,
            'entities': entities
        }
    
    def _handle_sentiment_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sentiment analysis task"""
        query = data.get('query', '')
        
        # Analyze sentiment using the enhanced NLP processor
        sentiment = self.nlp_processor._analyze_sentiment(query)
        
        return {
            'success': True,
            'sentiment': sentiment
        }


def main():
    """Main function to run the NLP Processing Agent"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the agent
    agent = NLPProcessingAgent()
    agent.start()
    
    try:
        # Keep the agent running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down NLP Processing Agent...")
        agent.stop()


if __name__ == "__main__":
    main()
