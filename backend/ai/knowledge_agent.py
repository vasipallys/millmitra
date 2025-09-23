"""
Knowledge Management Agent for Rice Mill Management System
Handles knowledge management and retrieval tasks in the multi-agent AI architecture.
"""

import json
import logging
import redis
import threading
import time
import numpy as np
import faiss
from typing import Dict, Any, List


class KnowledgeManagementAgent:
    """Knowledge Management Agent that handles knowledge tasks from the AI Coordinator"""
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        """Initialize the Knowledge Management Agent"""
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.queue_name = 'knowledge_queue'
        self.running = False
        
        # Initialize FAISS index for similarity search
        self.dimension = 128  # Default dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.knowledge_base = {}  # Store knowledge with IDs
        self.id_counter = 0
        
        self.logger.info("Knowledge Management Agent initialized")
    
    def start(self):
        """Start the Knowledge Management Agent"""
        self.running = True
        self.logger.info("Knowledge Management Agent started")
        
        # Start processing loop in a separate thread
        processing_thread = threading.Thread(target=self._processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
        
        # Notify coordinator that agent is online
        self.redis_client.set('agent_status:knowledge', 'online')
        
        return processing_thread
    
    def stop(self):
        """Stop the Knowledge Management Agent"""
        self.running = False
        self.logger.info("Knowledge Management Agent stopped")
        
        # Notify coordinator that agent is offline
        self.redis_client.set('agent_status:knowledge', 'offline')
    
    def _processing_loop(self):
        """Main processing loop for handling knowledge tasks"""
        self.logger.info("Knowledge Management Agent listening for tasks")
        
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
        """Process a single knowledge task"""
        try:
            # Parse the task
            task = json.loads(task_json)
            request_id = task.get('request_id')
            task_type = task.get('task_type')
            data = task.get('data', {})
            
            self.logger.info(f"Processing knowledge task {task_type} with request ID {request_id}")
            
            # Update agent status to busy
            self.redis_client.set('agent_status:knowledge', 'busy')
            
            # Process based on task type
            if task_type == 'add_knowledge':
                result = self._handle_add_knowledge(data)
            elif task_type == 'retrieve_knowledge':
                result = self._handle_retrieve_knowledge(data)
            elif task_type == 'search_similar':
                result = self._handle_search_similar(data)
            elif task_type == 'update_knowledge':
                result = self._handle_update_knowledge(data)
            elif task_type == 'delete_knowledge':
                result = self._handle_delete_knowledge(data)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown knowledge task type: {task_type}'
                }
            
            # Add request ID to result
            result['request_id'] = request_id
            
            # Store result in Redis
            response_key = f"response:{request_id}"
            self.redis_client.set(response_key, json.dumps(result))
            
            self.logger.info(f"Knowledge task {request_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error processing knowledge task: {str(e)}")
            
            # Store error result
            if 'request_id' in locals():
                error_result = {
                    'success': False,
                    'error': f'Knowledge processing error: {str(e)}',
                    'request_id': request_id
                }
                response_key = f"response:{request_id}"
                self.redis_client.set(response_key, json.dumps(error_result))
        
        finally:
            # Update agent status back to online
            self.redis_client.set('agent_status:knowledge', 'online')
    
    def _handle_add_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle adding knowledge to the knowledge base"""
        try:
            # Get knowledge data
            content = data.get('content')
            embedding = data.get('embedding')
            metadata = data.get('metadata', {})
            
            if not content or not embedding:
                return {
                    'success': False,
                    'error': 'Content and embedding are required'
                }
            
            # Ensure embedding is the correct dimension
            if len(embedding) != self.dimension:
                # Resize embedding if necessary
                if len(embedding) > self.dimension:
                    embedding = embedding[:self.dimension]
                else:
                    embedding = embedding + [0] * (self.dimension - len(embedding))
            
            # Add to knowledge base
            knowledge_id = self.id_counter
            self.knowledge_base[knowledge_id] = {
                'content': content,
                'embedding': embedding,
                'metadata': metadata
            }
            self.id_counter += 1
            
            # Add to FAISS index
            embedding_array = np.array([embedding], dtype=np.float32)
            self.index.add(embedding_array)
            
            return {
                'success': True,
                'knowledge_id': knowledge_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Add knowledge error: {str(e)}'
            }
    
    def _handle_retrieve_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle retrieving knowledge from the knowledge base"""
        try:
            # Get knowledge ID
            knowledge_id = data.get('knowledge_id')
            
            if knowledge_id is None:
                return {
                    'success': False,
                    'error': 'Knowledge ID is required'
                }
            
            # Retrieve from knowledge base
            if knowledge_id in self.knowledge_base:
                knowledge = self.knowledge_base[knowledge_id]
                return {
                    'success': True,
                    'content': knowledge['content'],
                    'metadata': knowledge['metadata']
                }
            else:
                return {
                    'success': False,
                    'error': f'Knowledge with ID {knowledge_id} not found'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Retrieve knowledge error: {str(e)}'
            }
    
    def _handle_search_similar(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle searching for similar knowledge"""
        try:
            # Get query embedding
            query_embedding = data.get('embedding')
            top_k = data.get('top_k', 5)
            
            if not query_embedding:
                return {
                    'success': False,
                    'error': 'Query embedding is required'
                }
            
            # Ensure embedding is the correct dimension
            if len(query_embedding) != self.dimension:
                # Resize embedding if necessary
                if len(query_embedding) > self.dimension:
                    query_embedding = query_embedding[:self.dimension]
                else:
                    query_embedding = query_embedding + [0] * (self.dimension - len(query_embedding))
            
            # Search using FAISS
            query_array = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
            
            # Format results
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx < len(self.knowledge_base):
                    knowledge_id = list(self.knowledge_base.keys())[idx]
                    knowledge = self.knowledge_base[knowledge_id]
                    results.append({
                        'knowledge_id': knowledge_id,
                        'content': knowledge['content'],
                        'metadata': knowledge['metadata'],
                        'distance': float(distances[0][i])
                    })
            
            return {
                'success': True,
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Search similar error: {str(e)}'
            }
    
    def _handle_update_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle updating knowledge in the knowledge base"""
        try:
            # Get knowledge data
            knowledge_id = data.get('knowledge_id')
            content = data.get('content')
            embedding = data.get('embedding')
            metadata = data.get('metadata')
            
            if knowledge_id is None:
                return {
                    'success': False,
                    'error': 'Knowledge ID is required'
                }
            
            # Check if knowledge exists
            if knowledge_id not in self.knowledge_base:
                return {
                    'success': False,
                    'error': f'Knowledge with ID {knowledge_id} not found'
                }
            
            # Update knowledge
            if content is not None:
                self.knowledge_base[knowledge_id]['content'] = content
            
            if embedding is not None:
                # Ensure embedding is the correct dimension
                if len(embedding) != self.dimension:
                    # Resize embedding if necessary
                    if len(embedding) > self.dimension:
                        embedding = embedding[:self.dimension]
                    else:
                        embedding = embedding + [0] * (self.dimension - len(embedding))
                
                self.knowledge_base[knowledge_id]['embedding'] = embedding
                
                # Update in FAISS index
                embedding_array = np.array([embedding], dtype=np.float32)
                self.index.remove_ids(np.array([knowledge_id]))
                self.index.add(embedding_array)
            
            if metadata is not None:
                self.knowledge_base[knowledge_id]['metadata'] = metadata
            
            return {
                'success': True,
                'knowledge_id': knowledge_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Update knowledge error: {str(e)}'
            }
    
    def _handle_delete_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deleting knowledge from the knowledge base"""
        try:
            # Get knowledge ID
            knowledge_id = data.get('knowledge_id')
            
            if knowledge_id is None:
                return {
                    'success': False,
                    'error': 'Knowledge ID is required'
                }
            
            # Check if knowledge exists
            if knowledge_id not in self.knowledge_base:
                return {
                    'success': False,
                    'error': f'Knowledge with ID {knowledge_id} not found'
                }
            
            # Delete from knowledge base
            del self.knowledge_base[knowledge_id]
            
            # Remove from FAISS index
            self.index.remove_ids(np.array([knowledge_id]))
            
            return {
                'success': True,
                'knowledge_id': knowledge_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Delete knowledge error: {str(e)}'
            }


def main():
    """Main function to run the Knowledge Management Agent"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the agent
    agent = KnowledgeManagementAgent()
    agent.start()
    
    try:
        # Keep the agent running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Knowledge Management Agent...")
        agent.stop()


if __name__ == "__main__":
    main()
