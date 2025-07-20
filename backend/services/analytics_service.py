from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy import func, and_, or_, text
from models.analytics import Dashboard, DashboardWidget, Report, KPI, KPIValue, DataAlert
from models.production import ProductionBatch, QualityTest
from models.sales import SalesOrder
from models.finance import Invoice, Payment
from models.inventory import PaddyStock, ProductStock
from models.user import User
from database import db
import json

class AnalyticsService:
    def __init__(self):
        pass
    
    def create_dashboard(self, user: User, dashboard_data: Dict):
        """Create new dashboard"""
        dashboard = Dashboard(
            dashboard_name=dashboard_data['dashboard_name'],
            dashboard_type=dashboard_data['dashboard_type'],
            description=dashboard_data.get('description'),
            layout_config=dashboard_data.get('layout_config', {}),
            refresh_interval=dashboard_data.get('refresh_interval', 300),
            is_public=dashboard_data.get('is_public', False),
            department=dashboard_data.get('department'),
            access_roles=dashboard_data.get('access_roles', []),
            created_by=user.id
        )
        
        db.session.add(dashboard)
        db.session.flush()
        
        # Add widgets
        for widget_data in dashboard_data.get('widgets', []):
            widget = DashboardWidget(
                dashboard_id=dashboard.id,
                widget_name=widget_data['widget_name'],
                widget_type=widget_data['widget_type'],
                data_source=widget_data.get('data_source'),
                query_config=widget_data.get('query_config', {}),
                chart_config=widget_data.get('chart_config', {}),
                position_x=widget_data.get('position_x', 0),
                position_y=widget_data.get('position_y', 0),
                width=widget_data.get('width', 4),
                height=widget_data.get('height', 3)
            )
            db.session.add(widget)
        
        db.session.commit()
        return dashboard
    
    def get_executive_dashboard_data(self):
        """Get data for executive dashboard"""
        today = datetime.now()
        month_start = today.replace(day=1)
        
        # Revenue metrics
        monthly_revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.invoice_type == 'sales',
                Invoice.invoice_date >= month_start
            )
        ).scalar() or 0
        
        # Production metrics
        monthly_production = db.session.query(func.sum(ProductionBatch.output_quantity)).filter(
            and_(
                ProductionBatch.status == 'completed',
                ProductionBatch.end_time >= month_start
            )
        ).scalar() or 0
        
        # Quality metrics
        avg_quality = db.session.query(func.avg(QualityTest.quality_score)).filter(
            QualityTest.test_date >= month_start
        ).scalar() or 0
        
        # Inventory value
        inventory_value = self._calculate_inventory_value()
        
        # Outstanding receivables
        receivables = db.session.query(func.sum(Invoice.total_amount - Invoice.paid_amount)).filter(
            and_(
                Invoice.invoice_type == 'sales',
                Invoice.status != 'paid'
            )
        ).scalar() or 0
        
        return {
            'revenue': {
                'monthly': monthly_revenue,
                'trend': self._calculate_revenue_trend()
            },
            'production': {
                'monthly': monthly_production,
                'efficiency': self._calculate_production_efficiency()
            },
            'quality': {
                'average_score': avg_quality,
                'trend': self._calculate_quality_trend()
            },
            'inventory': {
                'total_value': inventory_value,
                'turnover_ratio': self._calculate_inventory_turnover()
            },
            'financials': {
                'receivables': receivables,
                'cash_flow': self._calculate_cash_flow()
            }
        }
    
    def get_operational_dashboard_data(self):
        """Get data for operational dashboard"""
        today = datetime.now()
        week_start = today - timedelta(days=7)
        
        # Active production batches
        active_batches = ProductionBatch.query.filter(
            ProductionBatch.status == 'in_progress'
        ).count()
        
        # Daily production trend
        daily_production = self._get_daily_production_trend(7)
        
        # Machine utilization
        machine_utilization = self._calculate_machine_utilization()
        
        # Quality alerts
        quality_alerts = self._get_recent_quality_alerts()
        
        # Inventory levels
        inventory_status = self._get_inventory_status()
        
        return {
            'production': {
                'active_batches': active_batches,
                'daily_trend': daily_production,
                'machine_utilization': machine_utilization
            },
            'quality': {
                'alerts': quality_alerts,
                'pass_rate': self._calculate_quality_pass_rate()
            },
            'inventory': inventory_status,
            'alerts': self._get_operational_alerts()
        }
    
    def create_kpi(self, user: User, kpi_data: Dict):
        """Create new KPI"""
        kpi = KPI(
            kpi_name=kpi_data['kpi_name'],
            kpi_code=kpi_data['kpi_code'],
            description=kpi_data.get('description'),
            category=kpi_data['category'],
            calculation_method=kpi_data['calculation_method'],
            calculation_config=kpi_data.get('calculation_config', {}),
            unit_of_measure=kpi_data.get('unit_of_measure'),
            target_value=kpi_data.get('target_value'),
            warning_threshold=kpi_data.get('warning_threshold'),
            critical_threshold=kpi_data.get('critical_threshold'),
            display_format=kpi_data.get('display_format', 'number'),
            update_frequency=kpi_data.get('update_frequency', 'daily'),
            created_by=user.id
        )
        
        db.session.add(kpi)
        db.session.commit()
        return kpi
    
    def calculate_kpi_value(self, kpi_id: int, measurement_date: datetime = None):
        """Calculate KPI value"""
        if measurement_date is None:
            measurement_date = datetime.now()
        
        kpi = KPI.query.get_or_404(kpi_id)
        
        # Calculate value based on method
        if kpi.calculation_method == 'sql':
            value = self._execute_sql_calculation(kpi.calculation_config, measurement_date)
        elif kpi.calculation_method == 'formula':
            value = self._execute_formula_calculation(kpi.calculation_config, measurement_date)
        else:
            value = 0
        
        # Store the value
        kpi_value = KPIValue(
            kpi_id=kpi_id,
            measurement_date=measurement_date,
            value=value,
            period_type='daily',
            period_start=measurement_date.replace(hour=0, minute=0, second=0),
            period_end=measurement_date.replace(hour=23, minute=59, second=59)
        )
        
        db.session.add(kpi_value)
        kpi.last_calculated = measurement_date
        db.session.commit()
        
        return kpi_value
    
    def get_kpi_dashboard(self, category: str = None):
        """Get KPI dashboard data"""
        query = KPI.query.filter(KPI.is_active == True)
        if category:
            query = query.filter(KPI.category == category)
        
        kpis = query.all()
        
        kpi_data = []
        for kpi in kpis:
            # Get latest value
            latest_value = KPIValue.query.filter(
                KPIValue.kpi_id == kpi.id
            ).order_by(KPIValue.measurement_date.desc()).first()
            
            # Get trend (last 7 values)
            trend_values = KPIValue.query.filter(
                KPIValue.kpi_id == kpi.id
            ).order_by(KPIValue.measurement_date.desc()).limit(7).all()
            
            status = 'normal'
            if latest_value:
                if kpi.critical_threshold and latest_value.value <= kpi.critical_threshold:
                    status = 'critical'
                elif kpi.warning_threshold and latest_value.value <= kpi.warning_threshold:
                    status = 'warning'
            
            kpi_data.append({
                'kpi': {
                    'id': kpi.id,
                    'name': kpi.kpi_name,
                    'code': kpi.kpi_code,
                    'category': kpi.category,
                    'unit': kpi.unit_of_measure,
                    'target': kpi.target_value
                },
                'current_value': latest_value.value if latest_value else None,
                'status': status,
                'trend': [v.value for v in reversed(trend_values)],
                'last_updated': latest_value.measurement_date if latest_value else None
            })
        
        return kpi_data
    
    def generate_financial_report(self, start_date: str, end_date: str):
        """Generate comprehensive financial report"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Revenue analysis
        revenue_data = self._analyze_revenue(start, end)
        
        # Expense analysis
        expense_data = self._analyze_expenses(start, end)
        
        # Profitability analysis
        profitability_data = self._analyze_profitability(start, end)
        
        # Cash flow analysis
        cash_flow_data = self._analyze_cash_flow(start, end)
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'revenue': revenue_data,
            'expenses': expense_data,
            'profitability': profitability_data,
            'cash_flow': cash_flow_data,
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_production_report(self, start_date: str, end_date: str):
        """Generate production performance report"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Production volume
        batches = ProductionBatch.query.filter(
            and_(
                ProductionBatch.start_time >= start,
                ProductionBatch.end_time <= end,
                ProductionBatch.status == 'completed'
            )
        ).all()
        
        total_output = sum(batch.output_quantity or 0 for batch in batches)
        total_input = sum(batch.input_quantity or 0 for batch in batches)
        avg_efficiency = sum(batch.efficiency_score or 0 for batch in batches) / len(batches) if batches else 0
        
        # Quality metrics
        quality_tests = QualityTest.query.filter(
            and_(
                QualityTest.test_date >= start,
                QualityTest.test_date <= end
            )
        ).all()
        
        avg_quality = sum(test.quality_score or 0 for test in quality_tests) / len(quality_tests) if quality_tests else 0
        pass_rate = sum(1 for test in quality_tests if test.pass_fail) / len(quality_tests) * 100 if quality_tests else 0
        
        return {
            'period': {'start': start_date, 'end': end_date},
            'production': {
                'total_batches': len(batches),
                'total_output': total_output,
                'total_input': total_input,
                'yield_percentage': (total_output / total_input * 100) if total_input > 0 else 0,
                'average_efficiency': avg_efficiency
            },
            'quality': {
                'total_tests': len(quality_tests),
                'average_score': avg_quality,
                'pass_rate': pass_rate
            },
            'generated_at': datetime.now().isoformat()
        }
    
    # Helper methods
    def _calculate_inventory_value(self):
        """Calculate total inventory value"""
        paddy_value = db.session.query(func.sum(PaddyStock.quantity * PaddyStock.purchase_price)).scalar() or 0
        product_value = db.session.query(func.sum(ProductStock.quantity * ProductStock.unit_cost)).scalar() or 0
        return paddy_value + product_value
    
    def _calculate_revenue_trend(self):
        """Calculate revenue trend for last 6 months"""
        trends = []
        for i in range(6):
            month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
                and_(
                    Invoice.invoice_type == 'sales',
                    Invoice.invoice_date >= month_start,
                    Invoice.invoice_date < month_end
                )
            ).scalar() or 0
            
            trends.append({
                'month': month_start.strftime('%Y-%m'),
                'revenue': revenue
            })
        
        return list(reversed(trends))
    
    def _get_daily_production_trend(self, days: int):
        """Get daily production trend"""
        trends = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            
            production = db.session.query(func.sum(ProductionBatch.output_quantity)).filter(
                and_(
                    func.date(ProductionBatch.end_time) == date,
                    ProductionBatch.status == 'completed'
                )
            ).scalar() or 0
            
            trends.append({
                'date': date.isoformat(),
                'production': production
            })
        
        return list(reversed(trends))
    
    def _execute_sql_calculation(self, config: Dict, measurement_date: datetime):
        """Execute SQL-based KPI calculation"""
        query = config.get('query', '')
        if not query:
            return 0
        
        # Replace date placeholders
        query = query.replace('{{measurement_date}}', f"'{measurement_date.isoformat()}'")
        
        try:
            result = db.session.execute(text(query)).scalar()
            return float(result) if result else 0
        except:
            return 0
    
    def _execute_formula_calculation(self, config: Dict, measurement_date: datetime):
        """Execute formula-based KPI calculation"""
        # This would implement formula parsing and calculation
        # For now, return a placeholder
        return 0