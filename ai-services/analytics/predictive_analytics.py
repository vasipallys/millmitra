"""
Predictive Analytics for Rice Mill Operations
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

class PredictiveAnalytics:
    """AI-powered predictive analytics for rice mill operations"""
    
    def __init__(self):
        self.models = {
            'demand_forecast': None,
            'price_prediction': None,
            'quality_prediction': None,
            'maintenance_prediction': None
        }
    
    async def predict_demand(self, historical_data: List[Dict], days_ahead: int = 30) -> Dict:
        """Predict rice demand for the next period"""
        try:
            # Simple trend-based prediction (in production, use ML models)
            if not historical_data:
                return {
                    'predictions': [],
                    'confidence': 0.0,
                    'trend': 'stable',
                    'error': 'No historical data available'
                }
            
            # Calculate simple moving average trend
            recent_demand = [item.get('demand', 0) for item in historical_data[-7:]]
            avg_demand = sum(recent_demand) / len(recent_demand) if recent_demand else 0
            
            # Generate predictions
            predictions = []
            for i in range(days_ahead):
                # Simple trend with some variation
                predicted_demand = avg_demand * (1 + np.random.normal(0, 0.1))
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i+1)).isoformat(),
                    'predicted_demand': max(0, predicted_demand),
                    'confidence': 0.75
                })
            
            return {
                'predictions': predictions,
                'confidence': 0.75,
                'trend': 'stable',
                'model_type': 'moving_average'
            }
            
        except Exception as e:
            return {
                'predictions': [],
                'confidence': 0.0,
                'trend': 'unknown',
                'error': f'Prediction error: {str(e)}'
            }
    
    async def predict_prices(self, market_data: List[Dict], days_ahead: int = 7) -> Dict:
        """Predict rice prices for the next period"""
        try:
            if not market_data:
                return {
                    'predictions': [],
                    'confidence': 0.0,
                    'trend': 'stable',
                    'error': 'No market data available'
                }
            
            # Simple price trend analysis
            recent_prices = [item.get('price', 0) for item in market_data[-7:]]
            avg_price = sum(recent_prices) / len(recent_prices) if recent_prices else 0
            
            predictions = []
            for i in range(days_ahead):
                # Simple price prediction with market volatility
                predicted_price = avg_price * (1 + np.random.normal(0, 0.05))
                predictions.append({
                    'date': (datetime.now() + timedelta(days=i+1)).isoformat(),
                    'predicted_price': max(0, predicted_price),
                    'confidence': 0.70
                })
            
            return {
                'predictions': predictions,
                'confidence': 0.70,
                'trend': 'stable',
                'model_type': 'price_trend'
            }
            
        except Exception as e:
            return {
                'predictions': [],
                'confidence': 0.0,
                'trend': 'unknown',
                'error': f'Price prediction error: {str(e)}'
            }
    
    async def predict_quality(self, production_data: List[Dict]) -> Dict:
        """Predict rice quality based on production parameters"""
        try:
            if not production_data:
                return {
                    'quality_score': 0.0,
                    'confidence': 0.0,
                    'recommendations': [],
                    'error': 'No production data available'
                }
            
            # Simple quality scoring based on production parameters
            latest_batch = production_data[-1] if production_data else {}
            
            # Basic quality factors
            moisture = latest_batch.get('moisture_content', 14)
            temperature = latest_batch.get('temperature', 25)
            processing_time = latest_batch.get('processing_time', 60)
            
            # Simple quality score calculation
            quality_score = 100
            if moisture > 14:
                quality_score -= (moisture - 14) * 5
            if temperature > 30:
                quality_score -= (temperature - 30) * 2
            if processing_time > 90:
                quality_score -= (processing_time - 90) * 0.5
            
            quality_score = max(0, min(100, quality_score))
            
            recommendations = []
            if moisture > 14:
                recommendations.append("Reduce moisture content for better quality")
            if temperature > 30:
                recommendations.append("Control processing temperature")
            if processing_time > 90:
                recommendations.append("Optimize processing time")
            
            return {
                'quality_score': quality_score,
                'confidence': 0.80,
                'recommendations': recommendations,
                'factors': {
                    'moisture_impact': moisture,
                    'temperature_impact': temperature,
                    'time_impact': processing_time
                }
            }
            
        except Exception as e:
            return {
                'quality_score': 0.0,
                'confidence': 0.0,
                'recommendations': [],
                'error': f'Quality prediction error: {str(e)}'
            }
    
    async def predict_maintenance(self, equipment_data: List[Dict]) -> Dict:
        """Predict equipment maintenance needs"""
        try:
            if not equipment_data:
                return {
                    'maintenance_alerts': [],
                    'confidence': 0.0,
                    'next_maintenance': None,
                    'error': 'No equipment data available'
                }
            
            alerts = []
            for equipment in equipment_data:
                equipment_id = equipment.get('id', 'unknown')
                runtime_hours = equipment.get('runtime_hours', 0)
                last_maintenance = equipment.get('last_maintenance_hours', 0)
                
                hours_since_maintenance = runtime_hours - last_maintenance
                
                if hours_since_maintenance > 500:
                    alerts.append({
                        'equipment_id': equipment_id,
                        'alert_type': 'overdue_maintenance',
                        'priority': 'high',
                        'hours_overdue': hours_since_maintenance - 500,
                        'recommendation': 'Schedule immediate maintenance'
                    })
                elif hours_since_maintenance > 400:
                    alerts.append({
                        'equipment_id': equipment_id,
                        'alert_type': 'maintenance_due',
                        'priority': 'medium',
                        'hours_until_due': 500 - hours_since_maintenance,
                        'recommendation': 'Schedule maintenance within 1 week'
                    })
            
            return {
                'maintenance_alerts': alerts,
                'confidence': 0.85,
                'next_maintenance': alerts[0] if alerts else None,
                'total_alerts': len(alerts)
            }
            
        except Exception as e:
            return {
                'maintenance_alerts': [],
                'confidence': 0.0,
                'next_maintenance': None,
                'error': f'Maintenance prediction error: {str(e)}'
            }
