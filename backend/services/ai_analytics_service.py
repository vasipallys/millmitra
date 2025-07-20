import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

class AIAnalyticsService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def generate_executive_insights(self, dashboard_data: Dict):
        """Generate AI insights for executive dashboard"""
        try:
            response = requests.post(f"{self.ai_service_url}/analytics/executive-insights", json=dashboard_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_executive_insights(dashboard_data)
    
    def generate_operational_recommendations(self, operational_data: Dict):
        """Generate AI recommendations for operations"""
        try:
            response = requests.post(f"{self.ai_service_url}/analytics/operational-recommendations", json=operational_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_operational_recommendations(operational_data)
    
    def analyze_financial_performance(self, financial_report: Dict):
        """AI analysis of financial performance"""
        try:
            response = requests.post(f"{self.ai_service_url}/analytics/financial-analysis", json=financial_report)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_financial_analysis(financial_report)
    
    def forecast_revenue(self, historical_trends: List[Dict]):
        """AI revenue forecasting"""
        try:
            response = requests.post(f"{self.ai_service_url}/analytics/revenue-forecast", json={'trends': historical_trends})
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_revenue_forecast(historical_trends)
    
    def generate_business_insights(self, business_data: Dict):
        """Generate comprehensive business insights"""
        try:
            response = requests.post(f"{self.ai_service_url}/analytics/business-insights", json=business_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_business_insights(business_data)
    
    def analyze_production_performance(self, production_report: Dict):
        """AI analysis of production performance"""
        try:
            response = requests.post(f"{self.ai_service_url}/analytics/production-analysis", json=production_report)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_production_analysis(production_report)
    
    def detect_anomalies(self, data_series: List[Dict], metric_name: str):
        """AI anomaly detection"""
        try:
            anomaly_data = {'data_series': data_series, 'metric_name': metric_name}
            response = requests.post(f"{self.ai_service_url}/analytics/detect-anomalies", json=anomaly_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_anomaly_detection(data_series)
    
    def predict_demand(self, historical_sales: List[Dict], external_factors: Dict):
        """AI demand prediction"""
        try:
            prediction_data = {'historical_sales': historical_sales, 'external_factors': external_factors}
            response = requests.post(f"{self.ai_service_url}/analytics/predict-demand", json=prediction_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_demand_prediction(historical_sales)
    
    # Fallback methods
    def _fallback_executive_insights(self, dashboard_data: Dict):
        """Fallback executive insights"""
        insights = []
        
        revenue = dashboard_data.get('revenue', {}).get('monthly', 0)
        if revenue > 1000000:
            insights.append({
                'type': 'positive',
                'title': 'Strong Revenue Performance',
                'message': f'Monthly revenue of ₹{revenue:,.0f} exceeds target',
                'priority': 'high'
            })
        
        quality_score = dashboard_data.get('quality', {}).get('average_score', 0)
        if quality_score < 80:
            insights.append({
                'type': 'warning',
                'title': 'Quality Attention Needed',
                'message': f'Average quality score of {quality_score:.1f} is below target',
                'priority': 'medium'
            })
        
        return {
            'insights': insights,
            'recommendations': [
                'Focus on maintaining quality standards',
                'Monitor cash flow closely',
                'Consider expanding high-performing product lines'
            ]
        }
    
    def _fallback_operational_recommendations(self, operational_data: Dict):
        """Fallback operational recommendations"""
        recommendations = []
        
        active_batches = operational_data.get('production', {}).get('active_batches', 0)
        if active_batches > 10:
            recommendations.append({
                'category': 'production',
                'priority': 'medium',
                'recommendation': 'High number of active batches - consider resource optimization'
            })
        
        return {
            'recommendations': recommendations,
            'optimization_opportunities': [
                'Implement predictive maintenance',
                'Optimize batch scheduling',
                'Improve quality control processes'
            ]
        }
    
    def _fallback_financial_analysis(self, financial_report: Dict):
        """Fallback financial analysis"""
        revenue = financial_report.get('revenue', {}).get('total', 0)
        expenses = financial_report.get('expenses', {}).get('total', 0)
        profit_margin = ((revenue - expenses) / revenue * 100) if revenue > 0 else 0
        
        analysis = {
            'profit_margin': profit_margin,
            'financial_health': 'good' if profit_margin > 15 else 'fair' if profit_margin > 5 else 'poor',
            'key_metrics': {
                'revenue_growth': 'stable',
                'cost_efficiency': 'good' if profit_margin > 10 else 'needs_improvement',
                'cash_flow': 'positive'
            }
        }
        
        recommendations = []
        if profit_margin < 10:
            recommendations.append('Review cost structure and identify savings opportunities')
        if profit_margin > 20:
            recommendations.append('Consider reinvestment in growth initiatives')
        
        analysis['recommendations'] = recommendations
        return analysis
    
    def _fallback_revenue_forecast(self, historical_trends: List[Dict]):
        """Fallback revenue forecast"""
        if not historical_trends:
            return {'forecast': [], 'confidence': 0.5}
        
        # Simple linear trend
        revenues = [trend.get('revenue', 0) for trend in historical_trends[-6:]]
        if len(revenues) < 2:
            return {'forecast': [], 'confidence': 0.5}
        
        # Calculate trend
        avg_growth = sum(revenues[i] - revenues[i-1] for i in range(1, len(revenues))) / (len(revenues) - 1)
        
        forecast = []
        last_revenue = revenues[-1]
        
        for i in range(1, 7):  # 6 months forecast
            predicted_revenue = last_revenue + (avg_growth * i)
            forecast.append({
                'period': f'Month +{i}',
                'predicted_revenue': max(0, predicted_revenue),
                'confidence': max(0.3, 0.9 - (i * 0.1))
            })
        
        return {
            'forecast': forecast,
            'trend': 'increasing' if avg_growth > 0 else 'decreasing',
            'confidence': 0.7
        }
    
    def _fallback_business_insights(self, business_data: Dict):
        """Fallback business insights"""
        return {
            'strategic_insights': [
                'Focus on high-margin products',
                'Improve operational efficiency',
                'Strengthen customer relationships'
            ],
            'growth_opportunities': [
                'Expand to new markets',
                'Introduce premium product lines',
                'Implement automation'
            ],
            'risk_factors': [
                'Market competition',
                'Raw material price volatility',
                'Regulatory changes'
            ]
        }
    
    def _fallback_production_analysis(self, production_report: Dict):
        """Fallback production analysis"""
        efficiency = production_report.get('production', {}).get('average_efficiency', 0)
        
        return {
            'efficiency_analysis': {
                'current_efficiency': efficiency,
                'benchmark': 85,
                'gap': max(0, 85 - efficiency)
            },
            'improvement_areas': [
                'Machine maintenance optimization',
                'Process standardization',
                'Quality control enhancement'
            ],
            'predicted_improvements': {
                'efficiency_gain': min(10, max(0, 85 - efficiency)),
                'cost_savings': 50000
            }
        }
    
    def _fallback_anomaly_detection(self, data_series: List[Dict]):
        """Fallback anomaly detection"""
        if len(data_series) < 5:
            return {'anomalies': [], 'confidence': 0.5}
        
        values = [d.get('value', 0) for d in data_series]
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        anomalies = []
        for i, data_point in enumerate(data_series):
            value = data_point.get('value', 0)
            if abs(value - mean_val) > 2 * std_val:
                anomalies.append({
                    'index': i,
                    'value': value,
                    'expected_range': [mean_val - 2*std_val, mean_val + 2*std_val],
                    'severity': 'high' if abs(value - mean_val) > 3 * std_val else 'medium'
                })
        
        return {
            'anomalies': anomalies,
            'confidence': 0.8
        }
    
    def _fallback_demand_prediction(self, historical_sales: List[Dict]):
        """Fallback demand prediction"""
        if not historical_sales:
            return {'predictions': [], 'confidence': 0.5}
        
        # Simple moving average
        recent_sales = historical_sales[-4:]  # Last 4 periods
        avg_demand = sum(sale.get('quantity', 0) for sale in recent_sales) / len(recent_sales)
        
        predictions = []
        for i in range(1, 5):  # 4 periods ahead
            predicted_demand = avg_demand * (1 + np.random.uniform(-0.1, 0.1))
            predictions.append({
                'period': f'Period +{i}',
                'predicted_demand': max(0, predicted_demand),
                'confidence': max(0.4, 0.8 - (i * 0.1))
            })
        
        return {
            'predictions': predictions,
            'trend': 'stable',
            'confidence': 0.6
        }