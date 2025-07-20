import requests
import json
from datetime import datetime, timedelta
from models.production import ProductionBatch, QualityTest
from models.inventory import PaddyStock
import numpy as np

class AIProductionService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def optimize_batch_parameters(self, batch_data: dict):
        """Use AI to optimize batch parameters"""
        try:
            response = requests.post(f"{self.ai_service_url}/production/optimize-batch", json=batch_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # Fallback optimization
        return self._fallback_batch_optimization(batch_data)
    
    def analyze_batch_performance(self, batch: ProductionBatch):
        """Analyze batch performance using AI"""
        batch_data = {
            'batch_id': batch.id,
            'variety': batch.paddy_variety,
            'input_quantity': batch.input_quantity,
            'output_quantity': batch.output_quantity,
            'efficiency_score': batch.efficiency_score,
            'duration': (batch.end_time - batch.start_time).total_seconds() / 3600 if batch.end_time else None,
            'quality_scores': [test.overall_score for test in batch.quality_tests]
        }
        
        try:
            response = requests.post(f"{self.ai_service_url}/production/analyze-batch", json=batch_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_batch_analysis(batch_data)
    
    def perform_pre_start_checks(self, batch: ProductionBatch):
        """AI-powered pre-start checks"""
        check_data = {
            'batch_id': batch.id,
            'variety': batch.paddy_variety,
            'input_quantity': batch.input_quantity,
            'machine_settings': batch.machine_settings,
            'planned_start_time': batch.planned_start_time.isoformat()
        }
        
        try:
            response = requests.post(f"{self.ai_service_url}/production/pre-start-checks", json=check_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_pre_start_checks(batch)
    
    def predict_final_quality(self, batch: ProductionBatch, completion_data: dict):
        """Predict final quality before batch completion"""
        prediction_data = {
            'batch_id': batch.id,
            'variety': batch.paddy_variety,
            'input_quantity': batch.input_quantity,
            'output_quantity': completion_data['output_quantity'],
            'machine_settings': batch.machine_settings,
            'intermediate_quality_tests': [test.to_dict() for test in batch.quality_tests]
        }
        
        try:
            response = requests.post(f"{self.ai_service_url}/production/predict-quality", json=prediction_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_quality_prediction(batch, completion_data)
    
    def optimize_step_parameters(self, batch: ProductionBatch, step_data: dict):
        """Optimize production step parameters"""
        optimization_data = {
            'batch_id': batch.id,
            'current_step': step_data['step_name'],
            'batch_progress': len(batch.steps),
            'current_quality': batch.current_quality_score,
            'variety': batch.paddy_variety
        }
        
        try:
            response = requests.post(f"{self.ai_service_url}/production/optimize-step", json=optimization_data)
            if response.status_code == 200:
                optimized = response.json()
                step_data.update(optimized.get('parameters', {}))
                return {**step_data, 'recommendations': optimized.get('recommendations', [])}
        except:
            pass
        
        return step_data
    
    def analyze_quality_parameters(self, test_data: dict):
        """AI analysis of quality test parameters"""
        try:
            response = requests.post(f"{self.ai_service_url}/production/analyze-quality", json=test_data)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_quality_analysis(test_data)
    
    def get_real_time_insights(self, production_status: dict):
        """Get real-time AI insights for current production"""
        try:
            response = requests.post(f"{self.ai_service_url}/production/real-time-insights", json=production_status)
            if response.status_code == 200:
                return response.json().get('insights', [])
        except:
            pass
        
        return self._fallback_real_time_insights(production_status)
    
    def optimize_production_schedule(self, schedule_data: dict, optimization_type: str):
        """AI-powered production schedule optimization"""
        try:
            response = requests.post(f"{self.ai_service_url}/production/optimize-schedule", json={
                'schedule_data': schedule_data,
                'optimization_type': optimization_type
            })
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_schedule_optimization(schedule_data, optimization_type)
    
    def enhance_analytics(self, analytics: dict):
        """Enhance production analytics with AI insights"""
        try:
            response = requests.post(f"{self.ai_service_url}/production/enhance-analytics", json=analytics)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        return self._fallback_analytics_enhancement(analytics)
    
    def get_production_recommendations(self, user):
        """Get AI-powered production recommendations"""
        context = {
            'user_role': user.role,
            'current_time': datetime.now().isoformat(),
            'active_batches': ProductionBatch.query.filter(
                ProductionBatch.status.in_(['planned', 'in_progress'])
            ).count()
        }
        
        try:
            response = requests.post(f"{self.ai_service_url}/production/recommendations", json=context)
            if response.status_code == 200:
                return response.json().get('recommendations', [])
        except:
            pass
        
        return self._fallback_recommendations(context)
    
    # Fallback methods for when AI service is unavailable
    def _fallback_batch_optimization(self, batch_data: dict):
        """Fallback batch optimization"""
        recommendations = []
        
        # Basic optimization based on variety
        if batch_data['paddy_variety'] == 'basmati':
            recommendations.append("Use lower temperature for basmati processing")
            batch_data['machine_settings'] = {
                'temperature': 65,
                'humidity': 12,
                'cleaning_cycles': 3
            }
        
        return {
            **batch_data,
            'recommendations': recommendations,
            'confidence': 0.7
        }
    
    def _fallback_batch_analysis(self, batch_data: dict):
        """Fallback batch analysis"""
        insights = []
        
        if batch_data.get('efficiency_score', 0) > 85:
            insights.append({
                'type': 'success',
                'message': 'Excellent batch efficiency achieved',
                'recommendation': 'Maintain current settings for similar batches'
            })
        elif batch_data.get('efficiency_score', 0) < 70:
            insights.append({
                'type': 'warning',
                'message': 'Below average efficiency',
                'recommendation': 'Review machine settings and operator procedures'
            })
        
        return {'insights': insights}
    
    def _fallback_pre_start_checks(self, batch: ProductionBatch):
        """Fallback pre-start checks"""
        issues = []
        
        # Basic checks
        if not batch.machine_settings:
            issues.append("Machine settings not configured")
        
        return {
            'can_start': len(issues) == 0,
            'issues': issues,
            'confidence': 0.8
        }
    
    def _fallback_quality_prediction(self, batch: ProductionBatch, completion_data: dict):
        """Fallback quality prediction"""
        # Simple prediction based on efficiency
        output_ratio = completion_data['output_quantity'] / batch.input_quantity
        predicted_quality = min(95, output_ratio * 100)
        
        return {
            'predicted_quality': predicted_quality,
            'confidence': 0.6,
            'factors': ['Output ratio indicates good processing']
        }
    
    def _fallback_quality_analysis(self, test_data: dict):
        """Fallback quality analysis"""
        # Calculate overall score based on parameters
        scores = []
        
        if 'moisture_content' in test_data:
            moisture = test_data['moisture_content']
            if 12 <= moisture <= 14:
                scores.append(95)
            elif 10 <= moisture <= 16:
                scores.append(80)
            else:
                scores.append(60)
        
        if 'broken_percentage' in test_data:
            broken = test_data['broken_percentage']
            scores.append(max(0, 100 - (broken * 5)))
        
        overall_score = sum(scores) / len(scores) if scores else 75
        
        return {
            'overall_score': overall_score,
            'analysis': 'Basic quality assessment completed',
            'recommendations': ['Monitor moisture content closely']
        }
    
    def _fallback_real_time_insights(self, production_status: dict):
        """Fallback real-time insights"""
        insights = []
        
        active_count = production_status.get('active_batches', 0)
        
        if active_count == 0:
            insights.append({
                'type': 'info',
                'message': 'No active production batches',
                'recommendation': 'Consider starting new batch if demand exists'
            })
        elif active_count > 2:
            insights.append({
                'type': 'warning',
                'message': 'High production load',
                'recommendation': 'Monitor quality closely with multiple active batches'
            })
        
        return insights
    
    def _fallback_schedule_optimization(self, schedule_data: dict, optimization_type: str):
        """Fallback schedule optimization"""
        return {
            'optimized_schedule': schedule_data,
            'improvements': ['Basic scheduling applied'],
            'confidence': 0.5
        }
    
    def _fallback_analytics_enhancement(self, analytics: dict):
        """Fallback analytics enhancement"""
        return {
            'trends': ['Production levels stable'],
            'predictions': ['Maintain current production rate'],
            'recommendations': ['Continue monitoring quality metrics']
        }
    
    def _fallback_recommendations(self, context: dict):
        """Fallback recommendations"""
        recommendations = []
        
        current_hour = datetime.now().hour
        
        if 6 <= current_hour <= 18:  # Working hours
            recommendations.append({
                'type': 'operational',
                'title': 'Optimal Production Time',
                'message': 'Current time is optimal for production operations',
                'priority': 'medium'
            })
        
        return recommendations