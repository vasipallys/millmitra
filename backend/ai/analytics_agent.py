"""
Analytics Agent for Rice Mill Management System
Handles data analytics and predictive modeling tasks in the multi-agent AI architecture.
"""

import json
import logging
import redis
import threading
import time
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64


class AnalyticsAgent:
    """Analytics Agent that handles analytics tasks from the AI Coordinator"""
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        """Initialize the Analytics Agent"""
        self.logger = logging.getLogger(__name__)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.queue_name = 'analytics_queue'
        self.running = False
        self.models = {}  # Store trained models
        self.logger.info("Analytics Agent initialized")
    
    def start(self):
        """Start the Analytics Agent"""
        self.running = True
        self.logger.info("Analytics Agent started")
        
        # Start processing loop in a separate thread
        processing_thread = threading.Thread(target=self._processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
        
        # Notify coordinator that agent is online
        self.redis_client.set('agent_status:analytics', 'online')
        
        return processing_thread
    
    def stop(self):
        """Stop the Analytics Agent"""
        self.running = False
        self.logger.info("Analytics Agent stopped")
        
        # Notify coordinator that agent is offline
        self.redis_client.set('agent_status:analytics', 'offline')
    
    def _processing_loop(self):
        """Main processing loop for handling analytics tasks"""
        self.logger.info("Analytics Agent listening for tasks")
        
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
        """Process a single analytics task"""
        try:
            # Parse the task
            task = json.loads(task_json)
            request_id = task.get('request_id')
            task_type = task.get('task_type')
            data = task.get('data', {})
            
            self.logger.info(f"Processing analytics task {task_type} with request ID {request_id}")
            
            # Update agent status to busy
            self.redis_client.set('agent_status:analytics', 'busy')
            
            # Process based on task type
            if task_type == 'predictive_maintenance':
                result = self._handle_predictive_maintenance(data)
            elif task_type == 'production_forecast':
                result = self._handle_production_forecast(data)
            elif task_type == 'quality_analysis':
                result = self._handle_quality_analysis(data)
            elif task_type == 'anomaly_detection':
                result = self._handle_anomaly_detection(data)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown analytics task type: {task_type}'
                }
            
            # Add request ID to result
            result['request_id'] = request_id
            
            # Store result in Redis
            response_key = f"response:{request_id}"
            self.redis_client.set(response_key, json.dumps(result))
            
            self.logger.info(f"Analytics task {request_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error processing analytics task: {str(e)}")
            
            # Store error result
            if 'request_id' in locals():
                error_result = {
                    'success': False,
                    'error': f'Analytics processing error: {str(e)}',
                    'request_id': request_id
                }
                response_key = f"response:{request_id}"
                self.redis_client.set(response_key, json.dumps(error_result))
        
        finally:
            # Update agent status back to online
            self.redis_client.set('agent_status:analytics', 'online')
    
    def _handle_predictive_maintenance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle predictive maintenance task"""
        try:
            # Get equipment data
            equipment_data = data.get('equipment_data', [])
            
            if not equipment_data:
                return {
                    'success': False,
                    'error': 'No equipment data provided'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(equipment_data)
            
            # Mock predictive maintenance logic
            # In a real implementation, this would use a trained model
            predictions = []
            for _, row in df.iterrows():
                # Simple mock prediction based on hours of operation
                hours = row.get('hours_of_operation', 0)
                risk_score = min(100, max(0, hours / 100 * 10))  # Normalize to 0-100
                
                predictions.append({
                    'equipment_id': row.get('equipment_id'),
                    'risk_score': round(risk_score, 2),
                    'maintenance_needed': risk_score > 70
                })
            
            return {
                'success': True,
                'predictions': predictions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Predictive maintenance error: {str(e)}'
            }
    
    def _handle_production_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle production forecast task"""
        try:
            # Get historical data
            historical_data = data.get('historical_data', [])
            
            if not historical_data:
                return {
                    'success': False,
                    'error': 'No historical data provided'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            
            # Mock production forecast logic
            # In a real implementation, this would use a trained model
            if len(df) > 0:
                # Simple mock forecast: average of last 3 days + trend
                last_values = df['production'].tail(3).values
                avg_production = np.mean(last_values)
                trend = (last_values[-1] - last_values[0]) / len(last_values)
                forecast = avg_production + trend
                
                # Confidence interval (mock)
                std_dev = np.std(last_values)
                confidence_interval = [max(0, forecast - std_dev), forecast + std_dev]
                
                return {
                    'success': True,
                    'forecast': round(forecast, 2),
                    'confidence_interval': [round(x, 2) for x in confidence_interval],
                    'trend': 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
                }
            else:
                return {
                    'success': True,
                    'forecast': 0,
                    'confidence_interval': [0, 0],
                    'trend': 'unknown'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Production forecast error: {str(e)}'
            }
    
    def _handle_quality_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle quality analysis task"""
        try:
            # Get quality data
            quality_data = data.get('quality_data', [])
            
            if not quality_data:
                return {
                    'success': False,
                    'error': 'No quality data provided'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(quality_data)
            
            # Mock quality analysis logic
            if len(df) > 0:
                avg_quality = df['quality_score'].mean()
                std_quality = df['quality_score'].std()
                
                # Identify outliers (mock)
                outliers = df[df['quality_score'] < (avg_quality - 2 * std_quality)]
                
                return {
                    'success': True,
                    'average_quality': round(avg_quality, 2),
                    'quality_std': round(std_quality, 2),
                    'outliers_count': len(outliers),
                    'outliers': outliers[['batch_id', 'quality_score']].to_dict('records')
                }
            else:
                return {
                    'success': True,
                    'average_quality': 0,
                    'quality_std': 0,
                    'outliers_count': 0,
                    'outliers': []
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Quality analysis error: {str(e)}'
            }
    
    def _handle_anomaly_detection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle anomaly detection task"""
        try:
            # Get sensor data
            sensor_data = data.get('sensor_data', [])
            
            if not sensor_data:
                return {
                    'success': False,
                    'error': 'No sensor data provided'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(sensor_data)
            
            # Mock anomaly detection logic
            # In a real implementation, this would use statistical methods or ML models
            anomalies = []
            if len(df) > 0:
                # Simple mock anomaly detection based on z-score
                for column in df.select_dtypes(include=[np.number]).columns:
                    mean = df[column].mean()
                    std = df[column].std()
                    
                    # Identify values more than 2 standard deviations from mean
                    z_scores = np.abs((df[column] - mean) / std)
                    anomaly_indices = df[z_scores > 2].index
                    
                    for idx in anomaly_indices:
                        anomalies.append({
                            'timestamp': df.loc[idx, 'timestamp'] if 'timestamp' in df.columns else None,
                            'sensor': column,
                            'value': df.loc[idx, column],
                            'z_score': round(z_scores[idx], 2)
                        })
            
            return {
                'success': True,
                'anomalies_count': len(anomalies),
                'anomalies': anomalies
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Anomaly detection error: {str(e)}'
            }


def main():
    """Main function to run the Analytics Agent"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start the agent
    agent = AnalyticsAgent()
    agent.start()
    
    try:
        # Keep the agent running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Analytics Agent...")
        agent.stop()


if __name__ == "__main__":
    main()
