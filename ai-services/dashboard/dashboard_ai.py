from fastapi import APIRouter
from typing import Dict, List, Any
import numpy as np
from datetime import datetime, timedelta
import json

router = APIRouter()

class DashboardAI:
    def __init__(self):
        self.insight_templates = {
            'production': [
                "Production efficiency has {trend} by {percentage}% compared to last week",
                "Peak production hours are between {start_hour}:00 and {end_hour}:00",
                "Machine {machine_id} shows {status} performance patterns"
            ],
            'quality': [
                "Quality scores show {trend} trend with {correlation} correlation to {factor}",
                "Moisture content variations affect quality by {impact}%",
                "Best quality achieved during {time_period} shifts"
            ],
            'inventory': [
                "Inventory turnover rate is {rate}x, {comparison} than industry average",
                "Optimal reorder point for {product} is {quantity} kg",
                "Seasonal demand pattern suggests {action} for {product}"
            ]
        }
    
    async def generate_insights(self, user_data: Dict) -> List[Dict]:
        """Generate AI-powered insights based on user role and data"""
        insights = []
        
        role = user_data.get('role', 'operator')
        metrics = user_data.get('metrics', {})
        
        if role in ['manager', 'admin']:
            insights.extend(self._generate_management_insights(metrics))
        
        if role in ['operator', 'supervisor']:
            insights.extend(self._generate_operational_insights(metrics))
        
        if role == 'sales':
            insights.extend(self._generate_sales_insights(metrics))
        
        return insights
    
    async def prioritize_widgets(self, widget_data: Dict) -> Dict:
        """AI-powered widget prioritization"""
        widgets = widget_data.get('widgets', [])
        user_role = widget_data.get('user_role', 'operator')
        current_hour = widget_data.get('current_hour', 12)
        preferences = widget_data.get('user_preferences', {})
        
        # AI scoring based on multiple factors
        for widget in widgets:
            score = self._calculate_widget_score(widget, user_role, current_hour, preferences)
            widget['ai_score'] = score
        
        # Sort by AI score
        prioritized = sorted(widgets, key=lambda x: x.get('ai_score', 0), reverse=True)
        
        return {'prioritized_widgets': prioritized}
    
    async def generate_predictive_alerts(self, context_data: Dict) -> Dict:
        """Generate AI-powered predictive alerts"""
        alerts = []
        
        # Simulate predictive analytics
        current_time = datetime.now()
        
        # Predict maintenance needs
        maintenance_alert = self._predict_maintenance_needs(context_data)
        if maintenance_alert:
            alerts.append(maintenance_alert)
        
        # Predict quality issues
        quality_alert = self._predict_quality_issues(context_data)
        if quality_alert:
            alerts.append(quality_alert)
        
        # Predict inventory shortages
        inventory_alert = self._predict_inventory_shortages(context_data)
        if inventory_alert:
            alerts.append(inventory_alert)
        
        return {'alerts': alerts}
    
    async def analyze_production_patterns(self, production_data: Dict) -> Dict:
        """Analyze production patterns using AI"""
        batches = production_data.get('batches', [])
        daily_data = production_data.get('daily_production', [])
        
        analysis = {
            'efficiency_trend': self._analyze_efficiency_trend(batches),
            'optimal_hours': self._find_optimal_production_hours(daily_data),
            'bottlenecks': self._identify_bottlenecks(batches),
            'recommendations': self._generate_production_recommendations(batches)
        }
        
        return analysis
    
    async def analyze_quality_patterns(self, quality_data: Dict) -> Dict:
        """Analyze quality patterns using AI"""
        tests = quality_data.get('quality_tests', [])
        
        analysis = {
            'quality_factors': self._identify_quality_factors(tests),
            'correlation_analysis': self._analyze_quality_correlations(tests),
            'improvement_suggestions': self._suggest_quality_improvements(tests),
            'risk_assessment': self._assess_quality_risks(tests)
        }
        
        return analysis
    
    def _generate_management_insights(self, metrics: Dict) -> List[Dict]:
        """Generate insights for management roles"""
        insights = []
        
        # Production efficiency insight
        if 'total_production' in metrics:
            production = metrics['total_production']
            if production > 1000:
                insights.append({
                    'type': 'success',
                    'category': 'production',
                    'title': 'Strong Production Performance',
                    'message': f'Production of {production:.0f}kg exceeds targets',
                    'confidence': 0.9,
                    'action': 'Consider expanding capacity'
                })
        
        # Quality insight
        if 'avg_quality' in metrics:
            quality = metrics['avg_quality']
            if quality < 80:
                insights.append({
                    'type': 'warning',
                    'category': 'quality',
                    'title': 'Quality Attention Needed',
                    'message': f'Average quality score of {quality:.1f}% below standard',
                    'confidence': 0.85,
                    'action': 'Review quality control processes'
                })
        
        return insights
    
    def _generate_operational_insights(self, metrics: Dict) -> List[Dict]:
        """Generate insights for operational roles"""
        insights = []
        
        # Current shift performance
        insights.append({
            'type': 'info',
            'category': 'operations',
            'title': 'Shift Performance',
            'message': 'Current shift running at optimal efficiency',
            'confidence': 0.8,
            'action': 'Maintain current settings'
        })
        
        return insights
    
    def _generate_sales_insights(self, metrics: Dict) -> List[Dict]:
        """Generate insights for sales roles"""
        insights = []
        
        # Inventory insights for sales
        if 'inventory_value' in metrics:
            value = metrics['inventory_value']
            insights.append({
                'type': 'info',
                'category': 'sales',
                'title': 'Inventory Status',
                'message': f'Current inventory value: ₹{value:,.0f}',
                'confidence': 0.95,
                'action': 'Review pricing strategy'
            })
        
        return insights
    
    def _calculate_widget_score(self, widget: Dict, role: str, hour: int, preferences: Dict) -> float:
        """Calculate AI score for widget prioritization"""
        base_score = widget.get('priority', 5)
        
        # Role-based scoring
        role_multipliers = {
            'manager': {'financial_summary': 1.5, 'alerts': 1.3},
            'operator': {'current_batch': 1.5, 'machine_status': 1.4},
            'sales': {'sales_pipeline': 1.5, 'customer_insights': 1.3}
        }
        
        widget_id = widget.get('id', '')
        role_multiplier = role_multipliers.get(role, {}).get(widget_id, 1.0)
        
        # Time-based scoring
        time_multiplier = 1.0
        if 'production' in widget_id and 6 <= hour <= 18:  # Working hours
            time_multiplier = 1.2
        elif 'alerts' in widget_id:
            time_multiplier = 1.3  # Always important
        
        # User preference scoring
        pref_multiplier = 1.0
        dashboard_prefs = preferences.get('dashboard', {})
        if widget_id in dashboard_prefs.get('favorites', []):
            pref_multiplier = 1.4
        
        return base_score * role_multiplier * time_multiplier * pref_multiplier
    
    def _predict_maintenance_needs(self, context: Dict) -> Dict:
        """Predict maintenance needs using AI"""
        # Simulate AI prediction
        risk_score = np.random.random()
        
        if risk_score > 0.7:
            return {
                'id': 'maintenance_prediction',
                'type': 'warning',
                'title': 'Maintenance Required Soon',
                'message': 'Machine efficiency declining, maintenance recommended within 48 hours',
                'priority': 8,
                'confidence': risk_score,
                'action': 'Schedule maintenance'
            }
        return None
    
    def _predict_quality_issues(self, context: Dict) -> Dict:
        """Predict quality issues using AI"""
        # Simulate AI prediction
        risk_score = np.random.random()
        
        if risk_score > 0.8:
            return {
                'id': 'quality_prediction',
                'type': 'error',
                'title': 'Quality Risk Detected',
                'message': 'Pattern suggests potential quality decline in next batch',
                'priority': 9,
                'confidence': risk_score,
                'action': 'Increase quality monitoring'
            }
        return None
    
    def _predict_inventory_shortages(self, context: Dict) -> Dict:
        """Predict inventory shortages using AI"""
        # Simulate AI prediction
        risk_score = np.random.random()
        
        if risk_score > 0.6:
            return {
                'id': 'inventory_prediction',
                'type': 'warning',
                'title': 'Inventory Shortage Predicted',
                'message': 'Premium rice stock may run out in 5 days at current rate',
                'priority': 7,
                'confidence': risk_score,
                'action': 'Reorder premium rice'
            }
        return None
    
    def _analyze_efficiency_trend(self, batches: List) -> Dict:
        """Analyze production efficiency trends"""
        if not batches:
            return {'trend': 'stable', 'change': 0}
        
        # Simulate trend analysis
        recent_efficiency = np.mean([b.get('efficiency_score', 80) for b in batches[-5:]])
        older_efficiency = np.mean([b.get('efficiency_score', 80) for b in batches[-10:-5]]) if len(batches) >= 10 else recent_efficiency
        
        change = ((recent_efficiency - older_efficiency) / older_efficiency) * 100
        
        if change > 5:
            trend = 'improving'
        elif change < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {'trend': trend, 'change': change}
    
    def _find_optimal_production_hours(self, daily_data: List) -> Dict:
        """Find optimal production hours"""
        # Simulate analysis
        return {
            'peak_hours': [8, 9, 10, 14, 15, 16],
            'efficiency_by_hour': {str(h): 80 + np.random.randint(-10, 20) for h in range(6, 22)}
        }
    
    def _identify_bottlenecks(self, batches: List) -> List[Dict]:
        """Identify production bottlenecks"""
        # Simulate bottleneck detection
        bottlenecks = []
        
        if np.random.random() > 0.7:
            bottlenecks.append({
                'type': 'cleaning',
                'description': 'Cleaning process taking longer than optimal',
                'impact': 'medium',
                'suggestion': 'Review cleaning procedures'
            })
        
        return bottlenecks

dashboard_ai = DashboardAI()

@router.post("/insights")
async def generate_insights(data: Dict):
    insights = await dashboard_ai.generate_insights(data)
    return {'insights': insights}

@router.post("/prioritize")
async def prioritize_widgets(data: Dict):
    result = await dashboard_ai.prioritize_widgets(data)
    return result

@router.post("/predictive-alerts")
async def generate_predictive_alerts(data: Dict):
    result = await dashboard_ai.generate_predictive_alerts(data)
    return result

@router.post("/analyze-production")
async def analyze_production(data: Dict):
    result = await dashboard_ai.analyze_production_patterns(data)
    return result

@router.post("/analyze-quality")
async def analyze_quality(data: Dict):
    result = await dashboard_ai.analyze_quality_patterns(data)
    return result