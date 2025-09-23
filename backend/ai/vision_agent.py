"""
Vision Analysis Agent for Rice Mill Management System
Handles computer vision tasks in the multi-agent AI architecture.
"""

import json
import logging
import redis
import threading
import time
import cv2
import numpy as np
from typing import Dict, Any
from PIL import Image
import io
import base64


class VisionAnalysisAgent:
    """Vision Analysis Agent that handles vision tasks from the AI Coordinator"""
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        """Initialize the Vision Analysis Agent"""
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.queue_name = 'vision_queue'
        self.running = False
        self.logger.info("Vision Analysis Agent initialized")
    
    def start(self):
        """Start the Vision Analysis Agent"""
        self.running = True
        self.logger.info("Vision Analysis Agent started")
        
        # Start processing loop in a separate thread
        processing_thread = threading.Thread(target=self._processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
        
        # Notify coordinator that agent is online
        self.redis_client.set('agent_status:vision', 'online')
        
        return processing_thread
    
    def stop(self):
        """Stop the Vision Analysis Agent"""
        self.running = False
        self.logger.info("Vision Analysis Agent stopped")
        
        # Notify coordinator that agent is offline
        self.redis_client.set('agent_status:vision', 'offline')
    
    def _processing_loop(self):
        """Main processing loop for handling vision tasks"""
        self.logger.info("Vision Analysis Agent listening for tasks")
        
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
        """Process a single vision task"""
        try:
            # Parse the task
            task = json.loads(task_json)
            request_id = task.get('request_id')
            task_type = task.get('task_type')
            data = task.get('data', {})
            
            self.logger.info(f"Processing vision task {task_type} with request ID {request_id}")
            
            # Update agent status to busy
            self.redis_client.set('agent_status:vision', 'busy')
            
            # Process based on task type
            if task_type == 'quality_assessment':
                result = self._handle_quality_assessment(data)
            elif task_type == 'object_detection':
                result = self._handle_object_detection(data)
            elif task_type == 'image_analysis':
                result = self._handle_image_analysis(data)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown vision task type: {task_type}'
                }
            
            # Add request ID to result
            result['request_id'] = request_id
            
            # Store result in Redis
            response_key = f"response:{request_id}"
            self.redis_client.set(response_key, json.dumps(result))
            
            self.logger.info(f"Vision task {request_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error processing vision task: {str(e)}")
            
            # Store error result
            if 'request_id' in locals():
                error_result = {
                    'success': False,
                    'error': f'Vision processing error: {str(e)}',
                    'request_id': request_id
                }
                response_key = f"response:{request_id}"
                self.redis_client.set(response_key, json.dumps(error_result))
        
        finally:
            # Update agent status back to online
            self.redis_client.set('agent_status:vision', 'online')
    
    def _handle_quality_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle rice quality assessment task"""
        try:
            # Get image data
            image_data = data.get('image_data')
            if not image_data:
                return {
                    'success': False,
                    'error': 'No image data provided'
                }
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Perform quality assessment (mock implementation)
            # In a real implementation, this would use a trained model
            quality_score = self._calculate_quality_score(opencv_image)
            defects = self._detect_defects(opencv_image)
            
            return {
                'success': True,
                'quality_score': quality_score,
                'defects': defects
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Quality assessment error: {str(e)}'
            }
    
    def _handle_object_detection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle object detection task"""
        try:
            # Get image data
            image_data = data.get('image_data')
            if not image_data:
                return {
                    'success': False,
                    'error': 'No image data provided'
                }
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Perform object detection (mock implementation)
            # In a real implementation, this would use a trained model
            objects = self._detect_objects(opencv_image)
            
            return {
                'success': True,
                'objects': objects
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Object detection error: {str(e)}'
            }
    
    def _handle_image_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general image analysis task"""
        try:
            # Get image data
            image_data = data.get('image_data')
            if not image_data:
                return {
                    'success': False,
                    'error': 'No image data provided'
                }
            
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Perform general image analysis
            brightness = self._calculate_brightness(opencv_image)
            contrast = self._calculate_contrast(opencv_image)
            color_balance = self._calculate_color_balance(opencv_image)
            
            return {
                'success': True,
                'brightness': brightness,
                'contrast': contrast,
                'color_balance': color_balance
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Image analysis error: {str(e)}'
            }
    
    def _calculate_quality_score(self, image) -> float:
        """Calculate rice quality score based on image properties"""
        # Mock implementation - in a real system, this would use a trained model
        # For now, we'll calculate based on image properties
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize quality score between 0 and 100
        quality_score = min(100, max(0, blur / 10))
        return round(quality_score, 2)
    
    def _detect_defects(self, image) -> list:
        """Detect defects in rice grains"""
        # Mock implementation - in a real system, this would use a trained model
        # For now, we'll return a mock list of defects
        return [
            {'type': 'broken', 'count': 2},
            {'type': 'discolored', 'count': 1}
        ]
    
    def _detect_objects(self, image) -> list:
        """Detect objects in the image"""
        # Mock implementation - in a real system, this would use a trained model
        # For now, we'll return a mock list of objects
        return [
            {'label': 'rice_grain', 'confidence': 0.95, 'bbox': [10, 20, 50, 60]},
            {'label': 'rice_grain', 'confidence': 0.87, 'bbox': [70, 80, 110, 120]}
        ]
    
    def _calculate_brightness(self, image) -> float:
        """Calculate average brightness of the image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        return round(brightness, 2)
    
    def _calculate_contrast(self, image) -> float:
        """Calculate contrast of the image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray)
        return round(contrast, 2)
    
    def _calculate_color_balance(self, image) -> Dict[str, float]:
        """Calculate color balance of the image"""
        # Calculate mean values for each channel
        b, g, r = cv2.split(image)
        return {
            'red': round(np.mean(r), 2),
            'green': round(np.mean(g), 2),
            'blue': round(np.mean(b), 2)
        }


def main():
    """Main function to run the Vision Analysis Agent"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the agent
    agent = VisionAnalysisAgent()
    agent.start()
    
    try:
        # Keep the agent running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Vision Analysis Agent...")
        agent.stop()


if __name__ == "__main__":
    main()
