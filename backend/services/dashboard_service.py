from models import User, ProductionBatch, QualityTest, PaddyStock, ProductStock, SalesOrder, Customer, Farmer
from extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import requests
import json

class SmartDashboardService:
    def __init__(self):
        self.ai_service_url = "http://ai-services:8000"
    
    def get_smart_overview(self, user: User, start_date: datetime, end_date: datetime):
        """Generate AI-powered dashboard overview based on user role and context"""
        
        base_metrics = self._get_base_metrics(start_date, end_date)
        role_specific_data = self._get_role_specific_data(user, start_date, end_date)
        ai_insights = self._get_ai_overview_insights(user, base_metrics)
        
        return {
            'summary': {
                'total_production': base_metrics['total_production'],
                'quality_score': base_metrics['avg_quality'],
                'inventory_value': base_metrics['inventory_value'],
                'pending_orders': base_metrics['pending_orders'],
                'active_farmers': base_metrics['active_farmers']
            },
            'trends': self._calculate_trends(start_date, end_date),
            'role_data': role_specific_data,
            'ai_insights': ai_insights,
            'quick_actions': self._get_quick_actions(user),
            'performance_indicators': self._get_kpis(user, start_date, end_date)
        }
    
    def get_priority_widgets(self, user: User):
        """AI determines widget priority based on user role, time, and current context"""
        
        current_hour = datetime.now().hour
        user_preferences = user.get_preferences()
        
        # Base widgets for all roles
        widgets = []
        
        if user.role == 'manager' or user.role == 'admin':
            widgets.extend([
                self._create_production_overview_widget(),
                self._create_quality_trends_widget(),
                self._create_financial_summary_widget(),
                self._create_alerts_widget(user)
            ])
        
        if user.role == 'operator' or user.role == 'supervisor':
            widgets.extend([
                self._create_current_batch_widget(),
                self._create_quality_control_widget(),
                self._create_machine_status_widget(),
                self._create_safety_widget()
            ])
        
        if user.role == 'sales' or user.role == 'manager':
            widgets.extend([
                self._create_sales_pipeline_widget(),
                self._create_customer_insights_widget(),
                self._create_inventory_alerts_widget()
            ])
        
        # AI prioritization based on context
        prioritized_widgets = self._ai_prioritize_widgets(widgets, user, current_hour)
        
        return prioritized_widgets
    
    def get_smart_alerts(self, user: User):
        """Generate AI-powered alerts and recommendations"""
        
        alerts = []
        
        # Production alerts
        production_alerts = self._check_production_alerts()
        alerts.extend(production_alerts)
        
        # Quality alerts
        quality_alerts = self._check_quality_alerts()
        alerts.extend(quality_alerts)
        
        # Inventory alerts
        inventory_alerts = self._check_inventory_alerts()
        alerts.extend(inventory_alerts)
        
        # Predictive alerts from AI
        ai_alerts = self._get_ai_predictive_alerts(user)
        alerts.extend(ai_alerts)
        
        # Filter and prioritize based on user role
        filtered_alerts = self._filter_alerts_by_role(alerts, user.role)
        
        return sorted(filtered_alerts, key=lambda x: x['priority'], reverse=True)
    
    def get_production_metrics(self, days: int):
        """Get production metrics with AI analysis"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Raw metrics
        batches = ProductionBatch.query.filter(
            ProductionBatch.start_time >= start_date
        ).all()
        
        daily_production = db.session.query(
            func.date(ProductionBatch.start_time).label('date'),
            func.sum(ProductionBatch.output_quantity).label('total_output'),
            func.avg(ProductionBatch.efficiency_score).label('avg_efficiency')
        ).filter(
            ProductionBatch.start_time >= start_date
        ).group_by(func.date(ProductionBatch.start_time)).all()
        
        # AI analysis
        ai_analysis = self._get_ai_production_analysis(batches, daily_production)
        
        return {
            'daily_production': [
                {
                    'date': item.date.isoformat(),
                    'output': float(item.total_output or 0),
                    'efficiency': float(item.avg_efficiency or 0)
                } for item in daily_production
            ],
            'total_batches': len(batches),
            'avg_efficiency': sum(b.efficiency_score or 0 for b in batches) / len(batches) if batches else 0,
            'ai_insights': ai_analysis
        }
    
    def get_quality_metrics(self, days: int):
        """Get quality metrics with AI insights"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        quality_tests = QualityTest.query.filter(
            QualityTest.test_date >= start_date
        ).all()
        
        # Quality trends
        quality_trends = db.session.query(
            func.date(QualityTest.test_date).label('date'),
            func.avg(QualityTest.overall_score).label('avg_score'),
            func.count(QualityTest.id).label('test_count')
        ).filter(
            QualityTest.test_date >= start_date
        ).group_by(func.date(QualityTest.test_date)).all()
        
        # AI quality analysis
        ai_quality_insights = self._get_ai_quality_analysis(quality_tests)
        
        return {
            'quality_trends': [
                {
                    'date': item.date.isoformat(),
                    'score': float(item.avg_score or 0),
                    'tests': item.test_count
                } for item in quality_trends
            ],
            'avg_quality_score': sum(q.overall_score or 0 for q in quality_tests) / len(quality_tests) if quality_tests else 0,
            'total_tests': len(quality_tests),
            'ai_insights': ai_quality_insights
        }
    
    def get_inventory_metrics(self):
        """Get inventory metrics with AI optimization suggestions"""
        
        paddy_stock = PaddyStock.query.all()
        product_stock = ProductStock.query.all()
        
        # Calculate inventory values
        total_paddy_value = sum(stock.quantity * stock.price_per_kg for stock in paddy_stock)
        total_product_value = sum(stock.quantity * stock.price_per_kg for stock in product_stock)
        
        # AI inventory optimization
        ai_optimization = self._get_ai_inventory_optimization(paddy_stock, product_stock)
        
        return {
            'paddy_inventory': {
                'total_quantity': sum(stock.quantity for stock in paddy_stock),
                'total_value': total_paddy_value,
                'varieties': len(set(stock.variety for stock in paddy_stock))
            },
            'product_inventory': {
                'total_quantity': sum(stock.quantity for stock in product_stock),
                'total_value': total_product_value,
                'products': len(set(stock.product_type for stock in product_stock))
            },
            'ai_optimization': ai_optimization
        }
    
    def save_user_preferences(self, user: User, preferences: dict):
        """Save user dashboard preferences"""
        current_prefs = user.get_preferences()
        current_prefs.update({
            'dashboard': preferences
        })
        user.set_preferences(current_prefs)
        db.session.commit()
    
    # Helper methods
    def _get_base_metrics(self, start_date: datetime, end_date: datetime):
        """Get base metrics for the dashboard"""
        
        total_production = db.session.query(
            func.sum(ProductionBatch.output_quantity)
        ).filter(
            ProductionBatch.start_time >= start_date,
            ProductionBatch.start_time <= end_date
        ).scalar() or 0
        
        avg_quality = db.session.query(
            func.avg(QualityTest.overall_score)
        ).filter(
            QualityTest.test_date >= start_date,
            QualityTest.test_date <= end_date
        ).scalar() or 0
        
        inventory_value = (
            db.session.query(func.sum(PaddyStock.quantity * PaddyStock.price_per_kg)).scalar() or 0
        ) + (
            db.session.query(func.sum(ProductStock.quantity * ProductStock.price_per_kg)).scalar() or 0
        )
        
        pending_orders = SalesOrder.query.filter(
            SalesOrder.status.in_(['pending', 'processing'])
        ).count()
        
        active_farmers = Farmer.query.filter(
            Farmer.last_delivery >= start_date
        ).count()
        
        return {
            'total_production': float(total_production),
            'avg_quality': float(avg_quality),
            'inventory_value': float(inventory_value),
            'pending_orders': pending_orders,
            'active_farmers': active_farmers
        }
    
    def _get_role_specific_data(self, user: User, start_date: datetime, end_date: datetime):
        """Get data specific to user role"""
        
        if user.role == 'manager':
            return {
                'profit_margin': self._calculate_profit_margin(start_date, end_date),
                'efficiency_trends': self._get_efficiency_trends(start_date, end_date),
                'cost_analysis': self._get_cost_analysis(start_date, end_date)
            }
        elif user.role == 'operator':
            return {
                'current_batch': self._get_current_batch_info(),
                'machine_status': self._get_machine_status(),
                'next_maintenance': self._get_next_maintenance()
            }
        elif user.role == 'sales':
            return {
                'sales_pipeline': self._get_sales_pipeline(),
                'customer_insights': self._get_customer_insights(),
                'revenue_forecast': self._get_revenue_forecast()
            }
        
        return {}
    
    def _get_ai_overview_insights(self, user: User, metrics: dict):
        """Get AI-generated insights for overview"""
        try:
            response = requests.post(f"{self.ai_service_url}/dashboard/insights", json={
                'user_role': user.role,
                'metrics': metrics,
                'context': 'overview'
            })
            if response.status_code == 200:
                return response.json().get('insights', [])
        except:
            pass
        
        return [
            {
                'type': 'info',
                'title': 'Production Status',
                'message': f'Total production: {metrics["total_production"]:.1f} kg',
                'action': None
            }
        ]
    
    def _create_production_overview_widget(self):
        """Create production overview widget"""
        recent_batches = ProductionBatch.query.filter(
            ProductionBatch.start_time >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            'id': 'production_overview',
            'title': 'Production Overview',
            'type': 'chart',
            'priority': 9,
            'data': {
                'recent_batches': recent_batches,
                'chart_type': 'line',
                'endpoint': '/api/dashboard/metrics/production'
            }
        }
    
    def _create_quality_trends_widget(self):
        """Create quality trends widget"""
        return {
            'id': 'quality_trends',
            'title': 'Quality Trends',
            'type': 'chart',
            'priority': 8,
            'data': {
                'chart_type': 'area',
                'endpoint': '/api/dashboard/metrics/quality'
            }
        }
    
    def _create_alerts_widget(self, user: User):
        """Create alerts widget"""
        alert_count = len(self.get_smart_alerts(user))
        
        return {
            'id': 'alerts',
            'title': 'Smart Alerts',
            'type': 'list',
            'priority': 10 if alert_count > 0 else 5,
            'data': {
                'count': alert_count,
                'endpoint': '/api/dashboard/alerts'
            }
        }
    
    def _ai_prioritize_widgets(self, widgets: list, user: User, current_hour: int):
        """Use AI to prioritize widgets based on context"""
        try:
            response = requests.post(f"{self.ai_service_url}/dashboard/prioritize", json={
                'widgets': widgets,
                'user_role': user.role,
                'current_hour': current_hour,
                'user_preferences': user.get_preferences()
            })
            if response.status_code == 200:
                return response.json().get('prioritized_widgets', widgets)
        except:
            pass
        
        # Fallback: sort by priority
        return sorted(widgets, key=lambda x: x['priority'], reverse=True)
    
    def _check_production_alerts(self):
        """Check for production-related alerts"""
        alerts = []
        
        # Check for low efficiency
        recent_batches = ProductionBatch.query.filter(
            ProductionBatch.start_time >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        if recent_batches:
            avg_efficiency = sum(b.efficiency_score or 0 for b in recent_batches) / len(recent_batches)
            if avg_efficiency < 70:
                alerts.append({
                    'id': 'low_efficiency',
                    'type': 'warning',
                    'title': 'Low Production Efficiency',
                    'message': f'Average efficiency in last 24h: {avg_efficiency:.1f}%',
                    'priority': 8,
                    'action': 'Check machine maintenance schedule'
                })
        
        return alerts
    
    def _check_quality_alerts(self):
        """Check for quality-related alerts"""
        alerts = []
        
        # Check recent quality scores
        recent_tests = QualityTest.query.filter(
            QualityTest.test_date >= datetime.utcnow() - timedelta(hours=12)
        ).all()
        
        if recent_tests:
            avg_quality = sum(t.overall_score or 0 for t in recent_tests) / len(recent_tests)
            if avg_quality < 80:
                alerts.append({
                    'id': 'quality_decline',
                    'type': 'error',
                    'title': 'Quality Score Declining',
                    'message': f'Average quality in last 12h: {avg_quality:.1f}%',
                    'priority': 9,
                    'action': 'Review quality control procedures'
                })
        
        return alerts
    
    def _check_inventory_alerts(self):
        """Check for inventory-related alerts"""
        alerts = []
        
        # Check low stock
        low_stock_items = ProductStock.query.filter(
            ProductStock.quantity < ProductStock.min_threshold
        ).all()
        
        if low_stock_items:
            alerts.append({
                'id': 'low_inventory',
                'type': 'warning',
                'title': 'Low Inventory Alert',
                'message': f'{len(low_stock_items)} items below minimum threshold',
                'priority': 7,
                'action': 'Review inventory levels'
            })
        
        return alerts
    
    def _get_ai_predictive_alerts(self, user: User):
        """Get AI-generated predictive alerts"""
        try:
            response = requests.post(f"{self.ai_service_url}/dashboard/predictive-alerts", json={
                'user_role': user.role,
                'context': 'dashboard'
            })
            if response.status_code == 200:
                return response.json().get('alerts', [])
        except:
            pass
        
        return []
    
    def _filter_alerts_by_role(self, alerts: list, role: str):
        """Filter alerts based on user role"""
        role_filters = {
            'operator': ['production', 'quality', 'safety'],
            'supervisor': ['production', 'quality', 'safety', 'efficiency'],
            'manager': ['all'],
            'sales': ['inventory', 'orders', 'customers'],
            'admin': ['all']
        }
        
        if role in ['manager', 'admin']:
            return alerts
        
        allowed_types = role_filters.get(role, [])
        return [alert for alert in alerts if any(t in alert.get('type', '') for t in allowed_types)]