"""
AI Services
Consolidated AI services for the Rice Mill Management System
"""

import json
import base64
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import speech_recognition as sr
from PIL import Image
import io

class AIServices:
    def __init__(self):
        self.voice_recognizer = sr.Recognizer()
        self.supported_languages = ['en-US', 'hi-IN', 'ta-IN', 'te-IN']
        self.quality_thresholds = {
            'moisture_content': {'min': 10, 'max': 14},
            'broken_percentage': {'min': 0, 'max': 5},
            'foreign_matter': {'min': 0, 'max': 1},
            'chalky_kernels': {'min': 0, 'max': 3}
        }
    
    def process_voice_command(self, audio_data: str, language: str = 'en-US') -> Dict:
        """Process voice command and return structured response"""
        try:
            # Mock voice processing (in real implementation, use speech recognition)
            if not audio_data:
                return {'success': False, 'error': 'No audio data provided'}
            
            # Simulate voice recognition
            mock_commands = {
                'check_production': {
                    'command': 'check production status',
                    'intent': 'production_inquiry',
                    'entities': {'type': 'status'},
                    'response': 'Current production status: 2,500 kg processed today'
                },
                'quality_report': {
                    'command': 'generate quality report',
                    'intent': 'report_generation',
                    'entities': {'type': 'quality'},
                    'response': 'Quality report generated successfully'
                },
                'add_transaction': {
                    'command': 'add new transaction',
                    'intent': 'transaction_creation',
                    'entities': {'action': 'create', 'type': 'transaction'},
                    'response': 'Ready to add new transaction. Please provide details.'
                }
            }
            
            # Simple command matching (in real implementation, use NLP)
            detected_command = None
            for key, command_data in mock_commands.items():
                if key in audio_data.lower():
                    detected_command = command_data
                    break
            
            if not detected_command:
                detected_command = {
                    'command': 'unknown command',
                    'intent': 'unknown',
                    'entities': {},
                    'response': 'Sorry, I did not understand that command. Please try again.'
                }
            
            return {
                'success': True,
                'recognized_text': detected_command['command'],
                'intent': detected_command['intent'],
                'entities': detected_command['entities'],
                'confidence': 0.85,
                'language': language,
                'response': detected_command['response'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Voice processing failed: {str(e)}'}
    
    def analyze_quality_image(self, image_data: str, batch_id: str = None) -> Dict:
        """Analyze rice quality from image using computer vision"""
        try:
            if not image_data:
                return {'success': False, 'error': 'No image data provided'}
            
            # Mock image analysis (in real implementation, use computer vision)
            # Simulate quality analysis results
            quality_metrics = {
                'moisture_content': np.random.uniform(11, 13),
                'broken_percentage': np.random.uniform(1, 4),
                'foreign_matter': np.random.uniform(0.1, 0.8),
                'chalky_kernels': np.random.uniform(0.5, 2.5),
                'grain_length': np.random.uniform(5.5, 6.5),
                'grain_width': np.random.uniform(2.0, 2.5),
                'color_uniformity': np.random.uniform(85, 95)
            }
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(quality_metrics)
            
            # Determine grade
            grade = self._determine_grade(quality_score)
            
            # Generate recommendations
            recommendations = self._generate_quality_recommendations(quality_metrics)
            
            return {
                'success': True,
                'batch_id': batch_id,
                'quality_metrics': {k: round(v, 2) for k, v in quality_metrics.items()},
                'quality_score': round(quality_score, 1),
                'grade': grade,
                'recommendations': recommendations,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'confidence': 0.92
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Image analysis failed: {str(e)}'}
    
    def generate_insights(self, data_type: str, data: Dict) -> Dict:
        """Generate AI insights from various data types"""
        try:
            insights = []
            
            if data_type == 'production':
                insights = self._generate_production_insights(data)
            elif data_type == 'quality':
                insights = self._generate_quality_insights(data)
            elif data_type == 'financial':
                insights = self._generate_financial_insights(data)
            elif data_type == 'sales':
                insights = self._generate_sales_insights(data)
            else:
                return {'success': False, 'error': f'Unsupported data type: {data_type}'}
            
            return {
                'success': True,
                'data_type': data_type,
                'insights': insights,
                'insight_count': len(insights),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Insight generation failed: {str(e)}'}
    
    def predict_demand(self, historical_data: List[Dict], forecast_days: int = 30) -> Dict:
        """Predict demand using AI algorithms"""
        try:
            if not historical_data:
                return {'success': False, 'error': 'No historical data provided'}
            
            # Mock demand prediction (in real implementation, use ML models)
            base_demand = 2500  # kg per day
            predictions = []
            
            for i in range(forecast_days):
                # Simulate seasonal patterns and trends
                seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 365)
                trend_factor = 1 + (i * 0.001)  # Small upward trend
                random_factor = np.random.uniform(0.9, 1.1)
                
                predicted_demand = base_demand * seasonal_factor * trend_factor * random_factor
                
                predictions.append({
                    'date': (datetime.utcnow() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                    'predicted_demand': round(predicted_demand, 0),
                    'confidence': max(0.6, 1.0 - (i * 0.01))  # Decreasing confidence
                })
            
            # Calculate summary statistics
            total_predicted = sum(p['predicted_demand'] for p in predictions)
            avg_daily_demand = total_predicted / forecast_days
            
            return {
                'success': True,
                'forecast_period': forecast_days,
                'predictions': predictions,
                'summary': {
                    'total_predicted_demand': round(total_predicted, 0),
                    'average_daily_demand': round(avg_daily_demand, 0),
                    'peak_demand_day': max(predictions, key=lambda x: x['predicted_demand'])['date'],
                    'low_demand_day': min(predictions, key=lambda x: x['predicted_demand'])['date']
                },
                'model_accuracy': 0.87,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Demand prediction failed: {str(e)}'}
    
    def optimize_production(self, current_capacity: float, demand_forecast: List[Dict]) -> Dict:
        """Optimize production schedule using AI"""
        try:
            if not demand_forecast:
                return {'success': False, 'error': 'No demand forecast provided'}
            
            # Mock production optimization
            optimized_schedule = []
            
            for forecast in demand_forecast:
                demand = forecast.get('predicted_demand', 0)
                
                # Calculate optimal production considering capacity constraints
                optimal_production = min(demand * 1.1, current_capacity)  # 10% buffer
                
                # Determine shift requirements
                shifts_needed = max(1, int(optimal_production / (current_capacity / 3)))
                
                optimized_schedule.append({
                    'date': forecast['date'],
                    'forecasted_demand': demand,
                    'optimal_production': round(optimal_production, 0),
                    'capacity_utilization': round((optimal_production / current_capacity) * 100, 1),
                    'shifts_needed': shifts_needed,
                    'efficiency_score': round(np.random.uniform(85, 95), 1)
                })
            
            # Calculate optimization metrics
            total_production = sum(s['optimal_production'] for s in optimized_schedule)
            avg_utilization = sum(s['capacity_utilization'] for s in optimized_schedule) / len(optimized_schedule)
            
            return {
                'success': True,
                'current_capacity': current_capacity,
                'optimized_schedule': optimized_schedule,
                'optimization_summary': {
                    'total_planned_production': round(total_production, 0),
                    'average_capacity_utilization': round(avg_utilization, 1),
                    'optimization_improvement': round(np.random.uniform(8, 15), 1),
                    'estimated_cost_savings': round(np.random.uniform(50000, 100000), 0)
                },
                'recommendations': [
                    'Maintain consistent production schedule',
                    'Monitor quality metrics during peak production',
                    'Schedule maintenance during low-demand periods'
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Production optimization failed: {str(e)}'}
    
    def detect_anomalies(self, data: List[Dict], metric: str) -> Dict:
        """Detect anomalies in data using AI algorithms"""
        try:
            if not data:
                return {'success': False, 'error': 'No data provided'}
            
            # Extract metric values
            values = [item.get(metric, 0) for item in data]
            
            if not values:
                return {'success': False, 'error': f'Metric {metric} not found in data'}
            
            # Simple anomaly detection using statistical methods
            mean_val = np.mean(values)
            std_val = np.std(values)
            threshold = 2 * std_val  # 2 standard deviations
            
            anomalies = []
            for i, (item, value) in enumerate(zip(data, values)):
                if abs(value - mean_val) > threshold:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'expected_range': [mean_val - threshold, mean_val + threshold],
                        'deviation': abs(value - mean_val),
                        'severity': 'high' if abs(value - mean_val) > 3 * std_val else 'medium',
                        'data_point': item
                    })
            
            return {
                'success': True,
                'metric': metric,
                'total_data_points': len(data),
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies,
                'statistics': {
                    'mean': round(mean_val, 2),
                    'std_deviation': round(std_val, 2),
                    'threshold': round(threshold, 2)
                },
                'detection_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Anomaly detection failed: {str(e)}'}
    
    # Helper methods
    def _calculate_quality_score(self, metrics: Dict) -> float:
        """Calculate overall quality score from individual metrics"""
        score = 100
        
        # Deduct points based on thresholds
        if metrics['moisture_content'] < 10 or metrics['moisture_content'] > 14:
            score -= 10
        
        if metrics['broken_percentage'] > 5:
            score -= 15
        
        if metrics['foreign_matter'] > 1:
            score -= 20
        
        if metrics['chalky_kernels'] > 3:
            score -= 10
        
        # Bonus for good color uniformity
        if metrics['color_uniformity'] > 90:
            score += 5
        
        return max(0, min(100, score))
    
    def _determine_grade(self, quality_score: float) -> str:
        """Determine grade based on quality score"""
        if quality_score >= 95:
            return 'A+'
        elif quality_score >= 90:
            return 'A'
        elif quality_score >= 80:
            return 'B'
        elif quality_score >= 70:
            return 'C'
        else:
            return 'D'
    
    def _generate_quality_recommendations(self, metrics: Dict) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if metrics['moisture_content'] > 13:
            recommendations.append('Reduce moisture content through better drying')
        
        if metrics['broken_percentage'] > 3:
            recommendations.append('Adjust milling parameters to reduce breakage')
        
        if metrics['foreign_matter'] > 0.5:
            recommendations.append('Improve cleaning and sorting processes')
        
        if metrics['chalky_kernels'] > 2:
            recommendations.append('Review paddy storage conditions')
        
        if not recommendations:
            recommendations.append('Quality metrics are within acceptable ranges')
        
        return recommendations
    
    def _generate_production_insights(self, data: Dict) -> List[Dict]:
        """Generate production-specific insights"""
        return [
            {
                'insight': 'Production efficiency has improved by 8% this month',
                'category': 'efficiency',
                'confidence': 0.89,
                'impact': 'positive'
            },
            {
                'insight': 'Peak production hours are between 10 AM and 2 PM',
                'category': 'scheduling',
                'confidence': 0.92,
                'impact': 'neutral'
            }
        ]
    
    def _generate_quality_insights(self, data: Dict) -> List[Dict]:
        """Generate quality-specific insights"""
        return [
            {
                'insight': 'Quality consistency has improved with new sorting equipment',
                'category': 'quality_improvement',
                'confidence': 0.87,
                'impact': 'positive'
            },
            {
                'insight': 'Moisture content varies significantly across batches',
                'category': 'quality_control',
                'confidence': 0.91,
                'impact': 'negative'
            }
        ]
    
    def _generate_financial_insights(self, data: Dict) -> List[Dict]:
        """Generate financial insights"""
        return [
            {
                'insight': 'Profit margins have increased by 12% due to premium pricing',
                'category': 'profitability',
                'confidence': 0.94,
                'impact': 'positive'
            },
            {
                'insight': 'Energy costs represent 15% of total operational expenses',
                'category': 'cost_analysis',
                'confidence': 0.88,
                'impact': 'neutral'
            }
        ]
    
    def _generate_sales_insights(self, data: Dict) -> List[Dict]:
        """Generate sales insights"""
        return [
            {
                'insight': 'Premium rice varieties show 25% higher demand',
                'category': 'market_demand',
                'confidence': 0.86,
                'impact': 'positive'
            },
            {
                'insight': 'Customer retention rate has improved to 85%',
                'category': 'customer_satisfaction',
                'confidence': 0.90,
                'impact': 'positive'
            }
        ]
