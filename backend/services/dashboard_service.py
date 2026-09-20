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
        widgets = []
        role = (user.role or '').lower()

        factories = []
        if role in ('manager', 'admin', 'administrator', 'super_admin'):
            factories.extend([
                self._create_production_overview_widget,
                self._create_quality_trends_widget,
                self._create_financial_summary_widget,
                lambda: self._create_alerts_widget(user),
            ])

        if role in ('operator', 'supervisor', 'manager', 'admin', 'administrator'):
            factories.extend([
                self._create_current_batch_widget,
                self._create_quality_control_widget,
                self._create_machine_status_widget,
                self._create_safety_widget,
            ])

        if role in ('sales', 'manager', 'admin', 'administrator'):
            factories.extend([
                self._create_sales_pipeline_widget,
                self._create_customer_insights_widget,
                self._create_inventory_alerts_widget,
            ])

        for factory in factories:
            try:
                widget = factory()
                if widget:
                    widgets.append(widget)
            except Exception:
                db.session.rollback()

        return self._ai_prioritize_widgets(widgets, user, current_hour)
    
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
            func.sum(ProductionBatch.total_output).label('total_output'),
            func.avg(ProductionBatch.efficiency_percentage).label('avg_efficiency')
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
            'avg_efficiency': sum((b.efficiency_percentage or 0) for b in batches) / len(batches) if batches else 0,
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
            func.avg(QualityTest.grade_confidence).label('avg_score'),
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
            'avg_quality_score': sum(q.grade_confidence or 0 for q in quality_tests) / len(quality_tests) if quality_tests else 0,
            'total_tests': len(quality_tests),
            'ai_insights': ai_quality_insights
        }
    
    def get_inventory_metrics(self):
        """Get inventory metrics with AI optimization suggestions"""
        
        paddy_stock = PaddyStock.query.all()
        product_stock = ProductStock.query.all()
        
        # Calculate inventory values
        total_paddy_value = sum((stock.quantity or 0) * (stock.purchase_price or 0) for stock in paddy_stock)
        total_product_value = sum((stock.quantity or 0) * (stock.market_price or stock.unit_cost or 0) for stock in product_stock)
        
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

    def get_financial_metrics(self, days: int):
        """Get financial metrics with AI insights"""

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get sales data
        sales_orders = SalesOrder.query.filter(
            SalesOrder.order_date >= start_date,
            SalesOrder.order_date <= end_date
        ).all()

        # Calculate financial metrics
        total_revenue = sum(order.total_amount for order in sales_orders if order.status == 'completed')
        total_orders = len(sales_orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Get pending payments
        pending_payments = sum(order.total_amount for order in sales_orders if order.status == 'pending')

        # Calculate profit margins (simplified)
        estimated_costs = total_revenue * 0.7  # Assume 70% cost ratio
        estimated_profit = total_revenue - estimated_costs
        profit_margin = (estimated_profit / total_revenue * 100) if total_revenue > 0 else 0

        # AI financial insights
        ai_financial_insights = [
            f"Revenue trend: {'Increasing' if total_revenue > 0 else 'Stable'}",
            f"Average order value: ₹{avg_order_value:,.2f}",
            f"Profit margin: {profit_margin:.1f}%"
        ]

        if pending_payments > total_revenue * 0.1:
            ai_financial_insights.append("High pending payments detected - consider follow-up")

        return {
            'period_days': days,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'pending_payments': pending_payments,
            'estimated_profit': estimated_profit,
            'profit_margin': profit_margin,
            'ai_insights': ai_financial_insights
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
            func.sum(ProductionBatch.total_output)
        ).filter(
            ProductionBatch.start_time >= start_date,
            ProductionBatch.start_time <= end_date
        ).scalar() or 0
        
        avg_quality = db.session.query(
            func.avg(QualityTest.grade_confidence)
        ).filter(
            QualityTest.test_date >= start_date,
            QualityTest.test_date <= end_date
        ).scalar() or 0
        
        inventory_value = (
            db.session.query(func.sum(PaddyStock.quantity * PaddyStock.purchase_price)).scalar() or 0
        ) + (
            db.session.query(func.sum(ProductStock.quantity * ProductStock.market_price)).scalar() or 0
        )
        
        pending_orders = SalesOrder.query.filter(
            SalesOrder.status.in_(['pending', 'processing'])
        ).count()
        
        active_farmers = Farmer.query.filter(
            Farmer.last_transaction_date >= start_date
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
            }, timeout=2)
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
                'endpoint': '/dashboard/metrics/production'
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
                'endpoint': '/dashboard/metrics/quality'
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
                'endpoint': '/dashboard/alerts'
            }
        }

    def _create_financial_summary_widget(self):
        """Create financial summary widget"""
        return {
            'id': 'financial_summary',
            'title': 'Financial Summary',
            'type': 'metric',
            'priority': 9,
            'data': {
                'revenue': 0,
                'expenses': 0,
                'profit': 0,
                'chart_type': 'bar',
                'endpoint': '/dashboard/metrics/financial'
            }
        }

    def _create_current_batch_widget(self):
        """Create current batch widget"""
        return {
            'id': 'current_batch',
            'title': 'Current Batch',
            'type': 'status',
            'priority': 10,
            'data': {
                'batch_id': 'N/A',
                'status': 'No active batch',
                'progress': 0,
                'endpoint': '/production/current-status'
            }
        }

    def _create_quality_control_widget(self):
        """Create quality control widget"""
        return {
            'id': 'quality_control',
            'title': 'Quality Control',
            'type': 'metric',
            'priority': 7,
            'data': {
                'tests_today': 0,
                'pass_rate': 100,
                'endpoint': '/dashboard/metrics/quality'
            }
        }

    def _create_machine_status_widget(self):
        """Create machine status widget"""
        return {
            'id': 'machine_status',
            'title': 'Machine Status',
            'type': 'status',
            'priority': 6,
            'data': {
                'online': 0,
                'offline': 0,
                'maintenance': 0,
                'endpoint': '/dashboard/machine-status'
            }
        }

    def _create_safety_widget(self):
        """Create safety widget"""
        return {
            'id': 'safety',
            'title': 'Safety Status',
            'type': 'status',
            'priority': 8,
            'data': {
                'incidents': 0,
                'days_safe': 30,
                'endpoint': '/dashboard/safety'
            }
        }

    def _create_sales_pipeline_widget(self):
        """Open sales orders grouped by status, with empty fallbacks."""
        stages = {
            'pending': 0,
            'confirmed': 0,
            'processing': 0,
            'shipped': 0,
            'delivered': 0,
        }
        open_orders = 0
        pipeline_value = 0.0
        try:
            rows = db.session.query(
                SalesOrder.status, func.count(SalesOrder.id)
            ).group_by(SalesOrder.status).all()
            for status, count in rows:
                key = (status or 'pending').lower()
                if key in stages:
                    stages[key] = int(count or 0)
            open_filter = SalesOrder.status.in_(
                ['pending', 'confirmed', 'processing', 'shipped']
            )
            open_orders = SalesOrder.query.filter(open_filter).count()
            pipeline_value = db.session.query(
                func.coalesce(func.sum(SalesOrder.total_amount), 0)
            ).filter(open_filter).scalar() or 0
        except Exception:
            db.session.rollback()

        items = [
            {'title': label, 'description': f'{stages[key]} orders'}
            for key, label in (
                ('pending', 'Pending'),
                ('confirmed', 'Confirmed'),
                ('processing', 'Processing'),
                ('shipped', 'Shipped'),
                ('delivered', 'Delivered'),
            )
        ]
        return {
            'id': 'sales_pipeline',
            'title': 'Sales Pipeline',
            'type': 'list',
            'priority': 8,
            'data': {
                'value': open_orders,
                'subtitle': f'₹{float(pipeline_value):,.0f} open value',
                'items': items,
                'stages': stages,
                'open_orders': open_orders,
                'pipeline_value': float(pipeline_value),
            }
        }

    def _create_customer_insights_widget(self):
        """Customer counts for the dashboard, with empty fallbacks."""
        total = 0
        active = 0
        try:
            total = Customer.query.count()
            try:
                active = Customer.query.filter_by(is_active=True).count()
            except Exception:
                db.session.rollback()
                active = total
        except Exception:
            db.session.rollback()

        return {
            'id': 'customer_insights',
            'title': 'Customer Insights',
            'type': 'metric',
            'priority': 7,
            'data': {
                'value': total,
                'subtitle': f'{active} active customers',
                'total_customers': total,
                'active_customers': active,
            }
        }

    def _create_inventory_alerts_widget(self):
        """Low product (and empty paddy) stock alerts for the dashboard."""
        items = []
        try:
            for stock in ProductStock.query.all():
                qty = stock.quantity or 0
                min_level = stock.minimum_stock_level or stock.reorder_point or 0
                if min_level and qty < min_level:
                    name = stock.variety or stock.product_type or f'Product {stock.id}'
                    items.append({
                        'title': name,
                        'description': f'{qty:.0f} kg remaining (min {min_level:.0f} kg)'
                    })
            if not items:
                for stock in PaddyStock.query.all():
                    remaining = (
                        stock.remaining_quantity
                        if stock.remaining_quantity is not None
                        else stock.quantity
                    ) or 0
                    if remaining <= 0:
                        items.append({
                            'title': stock.variety or f'Paddy {stock.id}',
                            'description': 'No remaining paddy'
                        })
        except Exception:
            db.session.rollback()

        return {
            'id': 'inventory_alerts',
            'title': 'Inventory Alerts',
            'type': 'list',
            'priority': 9 if items else 4,
            'data': {
                'count': len(items),
                'value': len(items),
                'subtitle': f'{len(items)} low-stock items' if items else 'Stock levels OK',
                'items': items[:8],
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
            }, timeout=2)
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
            avg_efficiency = sum((b.efficiency_percentage or 0) for b in recent_batches) / len(recent_batches)
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
            avg_quality = sum(t.calculate_quality_score() or 0 for t in recent_tests) / len(recent_tests)
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
            ProductStock.quantity < ProductStock.minimum_stock_level
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
            }, timeout=2)
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

    def _calculate_trends(self, start_date: datetime, end_date: datetime):
        """Calculate trends for dashboard overview"""
        try:
            # Production trends
            production_trend = db.session.query(
                func.date(ProductionBatch.start_time).label('date'),
                func.sum(ProductionBatch.total_output).label('output')
            ).filter(
                ProductionBatch.start_time >= start_date
            ).group_by(func.date(ProductionBatch.start_time)).all()

            # Quality trends
            quality_trend = db.session.query(
                func.date(QualityTest.test_date).label('date'),
                func.avg(QualityTest.grade_confidence).label('quality')
            ).filter(
                QualityTest.test_date >= start_date
            ).group_by(func.date(QualityTest.test_date)).all()

            return {
                'production': [{'date': str(item.date), 'value': float(item.output or 0)} for item in production_trend],
                'quality': [{'date': str(item.date), 'value': float(item.quality or 0)} for item in quality_trend],
                'direction': 'up' if len(production_trend) > 0 else 'stable'
            }
        except Exception as e:
            return {
                'production': [],
                'quality': [],
                'direction': 'stable',
                'error': str(e)
            }

    def _get_quick_actions(self, user: User):
        """Get quick actions based on user role"""
        actions = []

        if user.role in ['admin', 'manager']:
            actions.extend([
                {'id': 'view_reports', 'title': 'View Reports', 'icon': 'chart', 'url': '/reports'},
                {'id': 'manage_inventory', 'title': 'Manage Inventory', 'icon': 'warehouse', 'url': '/inventory'},
                {'id': 'farmer_payments', 'title': 'Farmer Payments', 'icon': 'money', 'url': '/payments'}
            ])

        if user.role in ['operator', 'supervisor']:
            actions.extend([
                {'id': 'start_batch', 'title': 'Start New Batch', 'icon': 'play', 'url': '/production/new'},
                {'id': 'quality_test', 'title': 'Quality Test', 'icon': 'test', 'url': '/quality/test'},
                {'id': 'machine_status', 'title': 'Machine Status', 'icon': 'settings', 'url': '/machines'}
            ])

        if user.role == 'sales':
            actions.extend([
                {'id': 'new_order', 'title': 'New Order', 'icon': 'plus', 'url': '/orders/new'},
                {'id': 'customer_list', 'title': 'Customers', 'icon': 'users', 'url': '/customers'},
                {'id': 'price_update', 'title': 'Update Prices', 'icon': 'tag', 'url': '/pricing'}
            ])

        return actions

    def _get_kpis(self, user: User, start_date: datetime, end_date: datetime):
        """Get key performance indicators based on user role"""
        kpis = []

        try:
            if user.role in ['admin', 'manager']:
                # Financial KPIs
                total_revenue = db.session.query(func.sum(SalesOrder.total_amount)).filter(
                    SalesOrder.order_date >= start_date,
                    SalesOrder.status == 'completed'
                ).scalar() or 0

                kpis.extend([
                    {'name': 'Revenue', 'value': f'₹{total_revenue:,.0f}', 'trend': 'up', 'change': '+5.2%'},
                    {'name': 'Profit Margin', 'value': '12.5%', 'trend': 'up', 'change': '+0.8%'},
                    {'name': 'ROI', 'value': '18.3%', 'trend': 'stable', 'change': '0%'}
                ])

            if user.role in ['operator', 'supervisor']:
                # Production KPIs
                total_production = db.session.query(func.sum(ProductionBatch.total_output)).filter(
                    ProductionBatch.start_time >= start_date
                ).scalar() or 0

                kpis.extend([
                    {'name': 'Production', 'value': f'{total_production:,.0f} kg', 'trend': 'up', 'change': '+3.1%'},
                    {'name': 'Efficiency', 'value': '87.2%', 'trend': 'up', 'change': '+2.1%'},
                    {'name': 'Quality Score', 'value': '92.5%', 'trend': 'stable', 'change': '0%'}
                ])

            if user.role == 'sales':
                # Sales KPIs
                order_count = SalesOrder.query.filter(
                    SalesOrder.order_date >= start_date
                ).count()

                kpis.extend([
                    {'name': 'Orders', 'value': str(order_count), 'trend': 'up', 'change': '+12%'},
                    {'name': 'Conversion', 'value': '68.4%', 'trend': 'up', 'change': '+4.2%'},
                    {'name': 'Avg Order', 'value': '₹45,230', 'trend': 'stable', 'change': '0%'}
                ])

        except Exception as e:
            kpis.append({'name': 'Error', 'value': 'N/A', 'trend': 'stable', 'change': '0%'})

        return kpis

    def _get_ai_production_analysis(self, batches, daily_production):
        """AI analysis of production data"""
        try:
            if not batches:
                return ["No production data available for analysis"]

            total_output = sum(batch.total_output or 0 for batch in batches)
            avg_efficiency = sum((batch.efficiency_percentage or 0) for batch in batches) / len(batches)

            insights = []

            if avg_efficiency > 85:
                insights.append("Excellent production efficiency maintained")
            elif avg_efficiency > 70:
                insights.append("Good production efficiency, room for improvement")
            else:
                insights.append("Production efficiency needs attention")

            if len(daily_production) > 1:
                recent_trend = daily_production[-1].output - daily_production[-2].output if len(daily_production) > 1 else 0
                if recent_trend > 0:
                    insights.append("Production trending upward")
                elif recent_trend < 0:
                    insights.append("Production declining - investigate causes")
                else:
                    insights.append("Production stable")

            insights.append(f"Total output: {total_output:,.0f} kg")

            return insights

        except Exception as e:
            return [f"Analysis error: {str(e)}"]

    def _get_ai_quality_analysis(self, quality_tests):
        """AI analysis of quality data"""
        try:
            if not quality_tests:
                return ["No quality data available for analysis"]

            avg_grade = sum(test.grade_confidence or 0 for test in quality_tests) / len(quality_tests)

            insights = []

            if avg_grade > 90:
                insights.append("Excellent quality standards maintained")
            elif avg_grade > 80:
                insights.append("Good quality, minor improvements possible")
            elif avg_grade > 70:
                insights.append("Quality acceptable, focus on consistency")
            else:
                insights.append("Quality issues detected - immediate attention required")

            # Check for quality trends
            if len(quality_tests) > 5:
                recent_tests = quality_tests[-5:]
                recent_avg = sum(test.grade_confidence or 0 for test in recent_tests) / len(recent_tests)

                if recent_avg > avg_grade:
                    insights.append("Quality improving in recent tests")
                elif recent_avg < avg_grade:
                    insights.append("Quality declining in recent tests")
                else:
                    insights.append("Quality stable")

            insights.append(f"Average quality score: {avg_grade:.1f}%")
            insights.append(f"Total tests conducted: {len(quality_tests)}")

            return insights

        except Exception as e:
            return [f"Quality analysis error: {str(e)}"]

    def _get_ai_inventory_optimization(self, paddy_stock, product_stock):
        """AI optimization suggestions for inventory"""
        try:
            suggestions = []

            # Analyze paddy stock
            if paddy_stock:
                total_paddy = sum(stock.quantity for stock in paddy_stock)
                if total_paddy < 1000:  # kg
                    suggestions.append("Low paddy stock - consider procurement")
                elif total_paddy > 10000:  # kg
                    suggestions.append("High paddy stock - optimize storage costs")
                else:
                    suggestions.append("Paddy stock levels optimal")
            else:
                suggestions.append("No paddy stock data available")

            # Analyze product stock
            if product_stock:
                total_products = sum(stock.quantity for stock in product_stock)
                if total_products < 500:  # kg
                    suggestions.append("Low product stock - increase production")
                elif total_products > 5000:  # kg
                    suggestions.append("High product stock - focus on sales")
                else:
                    suggestions.append("Product stock levels balanced")
            else:
                suggestions.append("No product stock data available")

            # General optimization tips
            suggestions.append("Monitor stock rotation to minimize waste")
            suggestions.append("Implement just-in-time inventory for efficiency")

            return suggestions

        except Exception as e:
            return [f"Inventory optimization error: {str(e)}"]