"""
Voice Processing Agent for Rice Mill Management System
Handles voice recognition tasks in the multi-agent AI architecture.
"""

import json
import logging
import redis
import threading
import time
import speech_recognition as sr
from typing import Dict, Any


class VoiceProcessingAgent:
    """Voice Processing Agent that handles voice tasks from the AI Coordinator"""
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        """Initialize the Voice Processing Agent"""
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.queue_name = 'voice_queue'
        self.running = False
        self.logger.info("Voice Processing Agent initialized")
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def start(self):
        """Start the Voice Processing Agent"""
        self.running = True
        self.logger.info("Voice Processing Agent started")
        
        # Start processing loop in a separate thread
        processing_thread = threading.Thread(target=self._processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
        
        # Notify coordinator that agent is online
        self.redis_client.set('agent_status:voice', 'online')
        
        return processing_thread
    
    def stop(self):
        """Stop the Voice Processing Agent"""
        self.running = False
        self.logger.info("Voice Processing Agent stopped")
        
        # Notify coordinator that agent is offline
        self.redis_client.set('agent_status:voice', 'offline')
    
    def _processing_loop(self):
        """Main processing loop for handling voice tasks"""
        self.logger.info("Voice Processing Agent listening for tasks")
        
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
        """Process a single voice task"""
        try:
            # Parse the task
            task = json.loads(task_json)
            request_id = task.get('request_id')
            task_type = task.get('task_type')
            data = task.get('data', {})
            
            self.logger.info(f"Processing voice task {task_type} with request ID {request_id}")
            
            # Update agent status to busy
            self.redis_client.set('agent_status:voice', 'busy')
            
            # Process based on task type
            if task_type == 'voice_recognition':
                result = self._handle_voice_recognition(data)
            elif task_type == 'voice_command':
                result = self._handle_voice_command(data)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown voice task type: {task_type}'
                }
            
            # Add request ID to result
            result['request_id'] = request_id
            
            # Store result in Redis
            response_key = f"response:{request_id}"
            self.redis_client.set(response_key, json.dumps(result))
            
            self.logger.info(f"Voice task {request_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error processing voice task: {str(e)}")
            
            # Store error result
            if 'request_id' in locals():
                error_result = {
                    'success': False,
                    'error': f'Voice processing error: {str(e)}',
                    'request_id': request_id
                }
                response_key = f"response:{request_id}"
                self.redis_client.set(response_key, json.dumps(error_result))
        
        finally:
            # Update agent status back to online
            self.redis_client.set('agent_status:voice', 'online')
    
    def _handle_voice_recognition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voice recognition task"""
        try:
            # Get audio data if provided
            audio_data = data.get('audio_data')
            
            if audio_data:
                # Process provided audio data
                # This would typically be a base64 encoded audio file
                # For now, we'll return a mock result
                return {
                    'success': True,
                    'text': 'Mock recognized text from provided audio',
                    'confidence': 0.95
                }
            else:
                # Listen for live audio input
                with self.microphone as source:
                    self.logger.info("Listening for voice input...")
                    audio = self.recognizer.listen(source, timeout=5)
                
                # Recognize speech
                text = self.recognizer.recognize_google(audio)
                
                return {
                    'success': True,
                    'text': text,
                    'confidence': 0.90  # Mock confidence
                }
                
        except sr.WaitTimeoutError:
            return {
                'success': False,
                'error': 'No speech detected within timeout period'
            }
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Could not understand audio'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'Could not request results from speech recognition service: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Voice recognition error: {str(e)}'
            }
    
    def _handle_voice_command(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voice command task"""
        try:
            # First, recognize the voice input
            recognition_result = self._handle_voice_recognition(data)
            
            if not recognition_result['success']:
                return recognition_result
            
            # Process the recognized text as a command
            command_text = recognition_result['text'].lower()
            
            # Simple command processing
            if 'production status' in command_text:
                response = 'Current production status: 85% capacity'
            elif 'inventory' in command_text:
                response = 'Current inventory: 500 kg rice, 200 kg husk'
            elif 'weather' in command_text:
                response = 'Current weather: Sunny, 32°C'
            else:
                response = f'I understood: "{recognition_result["text"]}" but I am not sure how to respond to that command.'
            
            return {
                'success': True,
                'command': recognition_result['text'],
                'response': response
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Voice command error: {str(e)}'
            }


def main():
    """Main function to run the Voice Processing Agent"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the agent
    agent = VoiceProcessingAgent()
    agent.start()
    
    try:
        # Keep the agent running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Voice Processing Agent...")
        agent.stop()


if __name__ == "__main__":
    main()
