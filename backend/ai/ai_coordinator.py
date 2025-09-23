"""
AI Coordinator Agent for Rice Mill Management System

This module implements the central coordinator for the multi-agent AI architecture,
responsible for routing requests to appropriate specialized agents and aggregating responses.
"""

import json
import logging
import redis
import uuid
import time
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify

import logging
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)

class AICoordinator:
    """AI Coordinator that manages and routes requests to specialized AI agents"""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        """Initialize the AI Coordinator"""
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.agent_registry = {
            'nlp': 'nlp_processing_queue',
            'vision': 'vision_analysis_queue',
            'voice': 'voice_processing_queue',
            'analytics': 'analytics_queue',
            'knowledge': 'knowledge_management_queue'
        }
        
        # Initialize agent status tracking
        self.agent_status = {agent: 'offline' for agent in self.agent_registry.keys()}
        
        self.logger.info("AI Coordinator initialized")
    
    def route_request(self, task_type: str, data: Dict, context: Dict = None) -> Dict:
        """Route request to appropriate agent based on task type"""
        try:
            # Validate agent availability
            agent_type = self._determine_target_agent(task_type)
            if not agent_type or self.agent_status.get(agent_type) != 'online':
                return {
                    'success': False,
                    'error': f'Agent {agent_type} is not available'
                }
            
            # Generate unique request ID
            request_id = str(uuid.uuid4())
            
            # Create task message
            task_message = {
                'request_id': request_id,
                'task_type': task_type,
                'data': data,
                'context': context or {}
            }
            
            # Send to appropriate agent queue
            queue_name = self.agent_registry[agent_type]
            self.redis_client.lpush(queue_name, json.dumps(task_message))
            
            # Wait for response with timeout
            timeout = 30  # seconds
            start_time = time.time()
            response_key = f"response:{request_id}"
            
            while time.time() - start_time < timeout:
                response = self.redis_client.get(response_key)
                if response:
                    self.redis_client.delete(response_key)
                    return json.loads(response)
                time.sleep(0.1)
            
            return {
                'success': False,
                'error': 'Request timeout'
            }
            
        except Exception as e:
            self.logger.error(f"Error routing request: {str(e)}")
            return {
                'success': False,
                'error': f'Routing error: {str(e)}'
            }
    
    def _determine_target_agent(self, task_type: str) -> Optional[str]:
        """Determine which agent should handle the task based on task type"""
        agent_mapping = {
            # NLP Processing Agent tasks
            'query_processing': 'nlp',
            'intent_classification': 'nlp',
            'entity_extraction': 'nlp',
            'sentiment_analysis': 'nlp',
            'response_generation': 'nlp',
            
            # Vision Analysis Agent tasks
            'image_analysis': 'vision',
            'quality_assessment': 'vision',
            'defect_detection': 'vision',
            'grade_determination': 'vision',
            
            # Voice Processing Agent tasks
            'voice_recognition': 'voice',
            'voice_command_processing': 'voice',
            
            # Analytics Agent tasks
            'demand_prediction': 'analytics',
            'production_optimization': 'analytics',
            'anomaly_detection': 'analytics',
            'insight_generation': 'analytics',
            'financial_analysis': 'analytics',
            
            # Knowledge Management Agent tasks
            'knowledge_retrieval': 'knowledge',
            'faq_lookup': 'knowledge',
            'policy_lookup': 'knowledge',
            'best_practices_lookup': 'knowledge'
        }
        
        return agent_mapping.get(task_type)
    
    def get_response(self, request_id: str, timeout: int = 30) -> Dict:
        """Retrieve response for a specific request ID"""
        try:
            # Check if response is available in Redis
            response_key = f"response:{request_id}"
            response_data = self.redis_client.get(response_key)
            
            if response_data:
                # Delete the response from Redis after retrieval
                self.redis_client.delete(response_key)
                return json.loads(response_data)
            
            return {
                'success': False,
                'error': 'Response not available yet',
                'request_id': request_id
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving response: {str(e)}")
            return {
                'success': False,
                'error': f'Response retrieval failed: {str(e)}',
                'request_id': request_id
            }
    
    def register_agent(self, agent_name: str, queue_name: str):
        """Register a new agent with the coordinator"""
        self.agent_registry[agent_name] = queue_name
        self.agent_status[agent_name] = 'online'
        self.logger.info(f"Agent {agent_name} registered with queue {queue_name}")
    
    def update_agent_status(self, agent_name: str, status: str):
        """Update the status of an agent"""
        if agent_name in self.agent_status:
            self.agent_status[agent_name] = status
            self.logger.info(f"Agent {agent_name} status updated to {status}")
        
    def get_agent_status(self) -> Dict:
        """Get the status of all registered agents"""
        return self.agent_status
    
    def health_check(self) -> bool:
        """Check if the coordinator and Redis connection are healthy"""
        try:
            # Test Redis connection
            self.redis_client.ping()
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
    
    def process_nlp_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an NLP task by sending it to the NLP agent"""
        try:
            # Generate a unique request ID
            request_id = str(uuid.uuid4())
            
            # Create task message
            task = {
                'request_id': request_id,
                'task_type': 'process_text',
                'data': task_data
            }
            
            # Send task to NLP agent queue
            task_json = json.dumps(task)
            self.redis_client.lpush(self.agent_registry['nlp'], task_json)
            
            # Set a timeout for response
            timeout = 30  # seconds
            start_time = time.time()
            
            # Wait for response
            response_key = f"response:{request_id}"
            while time.time() - start_time < timeout:
                response = self.redis_client.get(response_key)
                if response:
                    # Remove response from Redis
                    self.redis_client.delete(response_key)
                    return json.loads(response)
                time.sleep(0.1)
            
            # Timeout
            return {
                'success': False,
                'error': 'NLP task timeout'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing NLP task: {str(e)}")
            return {
                'success': False,
                'error': f'NLP processing error: {str(e)}'
            }
    
    def process_vision_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a vision task by sending it to the vision agent"""
        try:
            # Generate a unique request ID
            request_id = str(uuid.uuid4())
            
            # Create task message
            task = {
                'request_id': request_id,
                'task_type': task_data.get('task_type', 'analyze_image'),
                'data': task_data
            }
            
            # Send task to vision agent queue
            task_json = json.dumps(task)
            self.redis_client.lpush(self.agent_registry['vision'], task_json)
            
            # Set a timeout for response
            timeout = 30  # seconds
            start_time = time.time()
            
            # Wait for response
            response_key = f"response:{request_id}"
            while time.time() - start_time < timeout:
                response = self.redis_client.get(response_key)
                if response:
                    # Remove response from Redis
                    self.redis_client.delete(response_key)
                    return json.loads(response)
                time.sleep(0.1)
            
            # Timeout
            return {
                'success': False,
                'error': 'Vision task timeout'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing vision task: {str(e)}")
            return {
                'success': False,
                'error': f'Vision processing error: {str(e)}'
            }
    
    def process_voice_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a voice task by sending it to the voice agent"""
        try:
            # Generate a unique request ID
            request_id = str(uuid.uuid4())
            
            # Create task message
            task = {
                'request_id': request_id,
                'task_type': task_data.get('task_type', 'process_audio'),
                'data': task_data
            }
            
            # Send task to voice agent queue
            task_json = json.dumps(task)
            self.redis_client.lpush(self.agent_registry['voice'], task_json)
            
            # Set a timeout for response
            timeout = 30  # seconds
            start_time = time.time()
            
            # Wait for response
            response_key = f"response:{request_id}"
            while time.time() - start_time < timeout:
                response = self.redis_client.get(response_key)
                if response:
                    # Remove response from Redis
                    self.redis_client.delete(response_key)
                    return json.loads(response)
                time.sleep(0.1)
            
            # Timeout
            return {
                'success': False,
                'error': 'Voice task timeout'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing voice task: {str(e)}")
            return {
                'success': False,
                'error': f'Voice processing error: {str(e)}'
            }
    
    def process_analytics_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process an analytics task by sending it to the analytics agent"""
        try:
            # Generate a unique request ID
            request_id = str(uuid.uuid4())
            
            # Create task message
            task = {
                'request_id': request_id,
                'task_type': task_data.get('task_type', 'analyze_data'),
                'data': task_data
            }
            
            # Send task to analytics agent queue
            task_json = json.dumps(task)
            self.redis_client.lpush(self.agent_registry['analytics'], task_json)
            
            # Set a timeout for response
            timeout = 30  # seconds
            start_time = time.time()
            
            # Wait for response
            response_key = f"response:{request_id}"
            while time.time() - start_time < timeout:
                response = self.redis_client.get(response_key)
                if response:
                    # Remove response from Redis
                    self.redis_client.delete(response_key)
                    return json.loads(response)
                time.sleep(0.1)
            
            # Timeout
            return {
                'success': False,
                'error': 'Analytics task timeout'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing analytics task: {str(e)}")
            return {
                'success': False,
                'error': f'Analytics processing error: {str(e)}'
            }
    
    def process_knowledge_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a knowledge task by sending it to the knowledge agent"""
        try:
            # Generate a unique request ID
            request_id = str(uuid.uuid4())
            
            # Create task message
            task = {
                'request_id': request_id,
                'task_type': task_data.get('task_type', 'search_similar'),
                'data': task_data
            }
            
            # Send task to knowledge agent queue
            task_json = json.dumps(task)
            self.redis_client.lpush(self.agent_registry['knowledge'], task_json)
            
            # Set a timeout for response
            timeout = 30  # seconds
            start_time = time.time()
            
            # Wait for response
            response_key = f"response:{request_id}"
            while time.time() - start_time < timeout:
                response = self.redis_client.get(response_key)
                if response:
                    # Remove response from Redis
                    self.redis_client.delete(response_key)
                    return json.loads(response)
                time.sleep(0.1)
            
            # Timeout
            return {
                'success': False,
                'error': 'Knowledge task timeout'
            }
            
        except Exception as e:
            self.logger.error(f"Error processing knowledge task: {str(e)}")
            return {
                'success': False,
                'error': f'Knowledge processing error: {str(e)}'
            }


# Flask app for RESTful API endpoints
app = Flask(__name__)
coordinator = AICoordinator()


@app.route('/api/ai-coordinator/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'agent_status': coordinator.get_agent_status()
    })


@app.route('/api/ai-coordinator/process', methods=['POST'])
def process_request():
    """Process AI request by routing to appropriate agent"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        task_type = data.get('task_type')
        task_data = data.get('data', {})
        context = data.get('context', {})
        
        if not task_type:
            return jsonify({
                'success': False,
                'error': 'Task type is required'
            }), 400
        
        # Route request to appropriate agent
        result = coordinator.route_request(task_type, task_data, context)
        
        if result['success']:
            return jsonify(result), 202  # Accepted for processing
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Processing failed: {str(e)}'
        }), 500


@app.route('/api/ai-coordinator/response/<request_id>', methods=['GET'])
def get_response(request_id: str):
    """Get response for a specific request ID"""
    try:
        response = coordinator.get_response(request_id)
        
        if response['success']:
            return jsonify(response), 200
        else:
            return jsonify(response), 404
            
    except Exception as e:
        logger.error(f"Error retrieving response: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Response retrieval failed: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
