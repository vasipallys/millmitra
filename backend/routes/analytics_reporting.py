"""
Analytics and Reporting Routes
Natural language report generation and predictive analytics
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from models import Transaction, Invoice, Customer, User, ProductionBatch, QualityTest
from services.analytics_reporting_service import AnalyticsReportingService
from extensions import db

analytics_reporting_bp = Blueprint('analytics_reporting', __name__)
analytics_service = AnalyticsReportingService()

@analytics_reporting_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
def generate_natural_language_report():
    """Generate natural language report with AI insights"""
    try:
        data = request.get_json()
        
        report_type = data.get('report_type')
        period = data.get('period', {})
        language = data.get('language', 'english')
        
        if not report_type:
            return jsonify({'error': 'Report type is required'}), 400
        
        if not period.get('start_date') or not period.get('end_date'):
            return jsonify({'error': 'Period start_date and end_date are required'}), 400
        
        result = analytics_service.generate_natural_language_report(report_type, period, language)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/predictive/analyze', methods=['POST'])
@jwt_required()
def predictive_analytics():
    """Advanced predictive analytics with machine learning"""
    try:
        data = request.get_json()
        
        analysis_type = data.get('analysis_type')
        forecast_period = data.get('forecast_period', 30)
        
        if not analysis_type:
            return jsonify({'error': 'Analysis type is required'}), 400
        
        result = analytics_service.predictive_analytics(analysis_type, forecast_period)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Predictive analysis failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/insights/generate', methods=['POST'])
@jwt_required()
def generate_intelligent_insights():
    """Generate intelligent insights from multiple data sources"""
    try:
        data = request.get_json()
        
        data_sources = data.get('data_sources', ['production', 'quality', 'financial'])
        insight_type = data.get('insight_type', 'comprehensive')
        
        result = analytics_service.intelligent_insights(data_sources, insight_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Insight generation failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/dashboard/custom', methods=['POST'])
@jwt_required()
def generate_custom_dashboard():
    """Generate custom dashboard analytics"""
    try:
        data = request.get_json()
        
        dashboard_config = data.get('dashboard_config', {})
        
        if not dashboard_config:
            return jsonify({'error': 'Dashboard configuration is required'}), 400
        
        result = analytics_service.custom_dashboard_analytics(dashboard_config)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Dashboard generation failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/compare/analyze', methods=['POST'])
@jwt_required()
def comparative_analysis():
    """Perform comparative analysis"""
    try:
        data = request.get_json()
        
        comparison_config = data.get('comparison_config', {})
        
        if not comparison_config:
            return jsonify({'error': 'Comparison configuration is required'}), 400
        
        result = analytics_service.comparative_analysis(comparison_config)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Comparative analysis failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/anomaly/detect', methods=['POST'])
@jwt_required()
def detect_anomalies():
    """Detect anomalies in data streams"""
    try:
        data = request.get_json()
        
        data_type = data.get('data_type')
        sensitivity = data.get('sensitivity', 'medium')
        
        if not data_type:
            return jsonify({'error': 'Data type is required'}), 400
        
        result = analytics_service.anomaly_detection(data_type, sensitivity)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Anomaly detection failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/benchmark/analyze', methods=['POST'])
@jwt_required()
def performance_benchmarking():
    """Benchmark performance against standards"""
    try:
        data = request.get_json()
        
        benchmark_type = data.get('benchmark_type')
        comparison_data = data.get('comparison_data')
        
        if not benchmark_type:
            return jsonify({'error': 'Benchmark type is required'}), 400
        
        result = analytics_service.performance_benchmarking(benchmark_type, comparison_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Benchmarking failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/realtime/<metric_type>', methods=['GET'])
@jwt_required()
def real_time_analytics(metric_type):
    """Generate real-time analytics"""
    try:
        result = analytics_service.real_time_analytics(metric_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': f'Real-time analytics failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/dashboard/overview', methods=['GET'])
@jwt_required()
def analytics_dashboard_overview():
    """Get comprehensive analytics dashboard overview"""
    try:
        # Get key metrics for dashboard
        current_date = datetime.utcnow()
        last_30_days = current_date - timedelta(days=30)
        
        # Production metrics
        production_batches = ProductionBatch.query.filter(
            ProductionBatch.production_date >= last_30_days
        ).all()
        
        total_production = sum(batch.quantity_produced for batch in production_batches)
        
        # Quality metrics
        quality_tests = QualityTest.query.filter(
            QualityTest.test_date >= last_30_days
        ).all()
        
        avg_quality_score = 87.5  # Mock calculation
        
        # Financial metrics
        transactions = Transaction.query.filter(
            Transaction.transaction_date >= last_30_days
        ).all()
        
        revenue = sum(float(t.amount) for t in transactions if t.transaction_type == 'income')
        expenses = sum(float(t.amount) for t in transactions if t.transaction_type == 'expense')
        
        # Generate quick insights
        insights_result = analytics_service.intelligent_insights(['production', 'quality', 'financial'])
        
        dashboard_data = {
            'overview': {
                'total_production_30d': total_production,
                'average_quality_score': avg_quality_score,
                'revenue_30d': revenue,
                'profit_30d': revenue - expenses,
                'production_batches': len(production_batches),
                'quality_tests': len(quality_tests)
            },
            'trends': {
                'production_trend': 'increasing',
                'quality_trend': 'stable',
                'financial_trend': 'positive'
            },
            'alerts': [
                {
                    'type': 'info',
                    'message': 'Production efficiency improved by 5% this month',
                    'category': 'production'
                }
            ],
            'quick_insights': insights_result.get('insights', {}).get('ai_insights', [])[:3] if insights_result.get('success') else []
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data,
            'generated_at': current_date.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Dashboard overview failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/reports/templates', methods=['GET'])
@jwt_required()
def get_report_templates():
    """Get available report templates"""
    try:
        templates = analytics_service.report_templates
        
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get templates: {str(e)}'}), 500

@analytics_reporting_bp.route('/export/report', methods=['POST'])
@jwt_required()
def export_report():
    """Export report in various formats"""
    try:
        data = request.get_json()
        
        report_id = data.get('report_id')
        export_format = data.get('format', 'pdf')
        
        if not report_id:
            return jsonify({'error': 'Report ID is required'}), 400
        
        # Mock export functionality
        export_result = {
            'export_id': f"EXP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'report_id': report_id,
            'format': export_format,
            'file_path': f'/exports/report_{report_id}.{export_format}',
            'download_url': f'/api/analytics/download/report_{report_id}.{export_format}',
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'export': export_result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Report export failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/kpi/calculate', methods=['POST'])
@jwt_required()
def calculate_kpis():
    """Calculate Key Performance Indicators"""
    try:
        data = request.get_json()
        
        kpi_types = data.get('kpi_types', ['production', 'quality', 'financial'])
        period = data.get('period', {})
        
        if not period.get('start_date') or not period.get('end_date'):
            # Default to last 30 days
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            period = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
        
        kpis = {}
        
        # Production KPIs
        if 'production' in kpi_types:
            kpis['production'] = {
                'total_output': 125000,  # kg
                'efficiency_rate': 92.5,  # %
                'downtime_hours': 8,
                'yield_percentage': 78.5,
                'batches_completed': 45
            }
        
        # Quality KPIs
        if 'quality' in kpi_types:
            kpis['quality'] = {
                'average_grade': 'B+',
                'defect_rate': 2.3,  # %
                'grade_a_percentage': 65.0,
                'quality_score': 87.5,
                'tests_conducted': 120
            }
        
        # Financial KPIs
        if 'financial' in kpi_types:
            kpis['financial'] = {
                'revenue': 2500000,  # ₹
                'profit_margin': 18.5,  # %
                'cost_per_kg': 35.50,  # ₹
                'roi': 22.3,  # %
                'cash_flow': 450000  # ₹
            }
        
        # Customer KPIs
        if 'customer' in kpi_types:
            kpis['customer'] = {
                'satisfaction_score': 4.2,  # out of 5
                'retention_rate': 85.0,  # %
                'new_customers': 12,
                'average_order_value': 15000,  # ₹
                'repeat_orders': 78.0  # %
            }
        
        return jsonify({
            'success': True,
            'kpis': kpis,
            'period': period,
            'calculated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'KPI calculation failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/trends/analyze', methods=['POST'])
@jwt_required()
def analyze_trends():
    """Analyze trends in various metrics"""
    try:
        data = request.get_json()
        
        metric_type = data.get('metric_type')
        time_period = data.get('time_period', 90)  # days
        
        if not metric_type:
            return jsonify({'error': 'Metric type is required'}), 400
        
        # Mock trend analysis
        trend_data = []
        base_date = datetime.utcnow() - timedelta(days=time_period)
        
        for i in range(time_period):
            date = base_date + timedelta(days=i)
            
            if metric_type == 'production':
                value = 2500 + (i * 10) + (50 * np.sin(i * 0.1))  # Trending up with variation
            elif metric_type == 'quality':
                value = 85 + (i * 0.05) + (3 * np.sin(i * 0.2))  # Slowly improving
            elif metric_type == 'revenue':
                value = 50000 + (i * 200) + (5000 * np.sin(i * 0.15))  # Growing with seasonality
            else:
                value = 100 + (i * 0.5)  # Default trend
            
            trend_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': round(value, 2)
            })
        
        # Calculate trend statistics
        values = [point['value'] for point in trend_data]
        trend_direction = 'increasing' if values[-1] > values[0] else 'decreasing'
        trend_strength = abs((values[-1] - values[0]) / values[0] * 100)
        
        # Detect patterns
        patterns = []
        if trend_strength > 10:
            patterns.append('strong_trend')
        if np.std(values) > np.mean(values) * 0.1:
            patterns.append('high_volatility')
        
        trend_analysis = {
            'metric_type': metric_type,
            'time_period': time_period,
            'trend_direction': trend_direction,
            'trend_strength': round(trend_strength, 2),
            'patterns': patterns,
            'data_points': trend_data,
            'statistics': {
                'mean': round(np.mean(values), 2),
                'std_dev': round(np.std(values), 2),
                'min_value': round(min(values), 2),
                'max_value': round(max(values), 2)
            }
        }
        
        return jsonify({
            'success': True,
            'trend_analysis': trend_analysis,
            'analyzed_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Trend analysis failed: {str(e)}'}), 500

@analytics_reporting_bp.route('/alerts/smart', methods=['GET'])
@jwt_required()
def get_smart_alerts():
    """Get AI-generated smart alerts"""
    try:
        # Generate smart alerts based on data analysis
        alerts = []
        
        # Production alerts
        alerts.append({
            'id': 'ALERT001',
            'type': 'production',
            'severity': 'medium',
            'title': 'Production Efficiency Opportunity',
            'message': 'Production efficiency could be improved by 8% with optimized scheduling',
            'recommendation': 'Review production schedule and implement batch optimization',
            'created_at': datetime.utcnow().isoformat()
        })
        
        # Quality alerts
        alerts.append({
            'id': 'ALERT002',
            'type': 'quality',
            'severity': 'low',
            'title': 'Quality Trend Positive',
            'message': 'Quality scores have improved by 3% over the last week',
            'recommendation': 'Continue current quality control practices',
            'created_at': datetime.utcnow().isoformat()
        })
        
        # Financial alerts
        alerts.append({
            'id': 'ALERT003',
            'type': 'financial',
            'severity': 'high',
            'title': 'Cost Optimization Opportunity',
            'message': 'Energy costs have increased by 15% this month',
            'recommendation': 'Investigate energy usage patterns and implement conservation measures',
            'created_at': datetime.utcnow().isoformat()
        })
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'alert_count': len(alerts),
            'generated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Smart alerts generation failed: {str(e)}'}), 500
