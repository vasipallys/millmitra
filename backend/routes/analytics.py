from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from services.analytics_service import AnalyticsService
from services.ai_analytics_service import AIAnalyticsService

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()
ai_analytics = AIAnalyticsService()

@analytics_bp.route('/dashboards', methods=['POST'])
@jwt_required()
def create_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    dashboard = analytics_service.create_dashboard(user, data)
    
    return jsonify({
        'success': True,
        'dashboard': {
            'id': dashboard.id,
            'name': dashboard.dashboard_name,
            'type': dashboard.dashboard_type
        }
    }), 201

@analytics_bp.route('/dashboards/executive')
@jwt_required()
def get_executive_dashboard():
    dashboard_data = analytics_service.get_executive_dashboard_data()
    
    # AI insights
    ai_insights = ai_analytics.generate_executive_insights(dashboard_data)
    
    return jsonify({
        'dashboard_data': dashboard_data,
        'ai_insights': ai_insights
    })

@analytics_bp.route('/dashboards/operational')
@jwt_required()
def get_operational_dashboard():
    dashboard_data = analytics_service.get_operational_dashboard_data()
    
    # AI recommendations
    ai_recommendations = ai_analytics.generate_operational_recommendations(dashboard_data)
    
    return jsonify({
        'dashboard_data': dashboard_data,
        'ai_recommendations': ai_recommendations
    })

@analytics_bp.route('/kpis', methods=['POST'])
@jwt_required()
def create_kpi():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    kpi = analytics_service.create_kpi(user, data)
    
    return jsonify({
        'success': True,
        'kpi': {
            'id': kpi.id,
            'name': kpi.kpi_name,
            'code': kpi.kpi_code
        }
    }), 201

@analytics_bp.route('/kpis/dashboard')
@jwt_required()
def get_kpi_dashboard():
    category = request.args.get('category')
    kpi_data = analytics_service.get_kpi_dashboard(category)
    
    return jsonify({
        'kpis': kpi_data
    })

@analytics_bp.route('/reports/financial')
@jwt_required()
def generate_financial_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    report = analytics_service.generate_financial_report(start_date, end_date)
    
    # AI analysis
    ai_analysis = ai_analytics.analyze_financial_performance(report)
    
    return jsonify({
        'report': report,
        'ai_analysis': ai_analysis
    })

@analytics_bp.route('/reports/production')
@jwt_required()
def generate_production_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    report = analytics_service.generate_production_report(start_date, end_date)
    
    # AI insights
    ai_insights = ai_analytics.analyze_production_performance(report)
    
    return jsonify({
        'report': report,
        'ai_insights': ai_insights
    })

@analytics_bp.route('/trends/revenue')
@jwt_required()
def get_revenue_trends():
    period = request.args.get('period', '6m')  # 6m, 1y, 2y
    
    trends = analytics_service.get_revenue_trends(period)
    
    # AI forecasting
    forecast = ai_analytics.forecast_revenue(trends)
    
    return jsonify({
        'trends': trends,
        'forecast': forecast
    })

@analytics_bp.route('/insights/business')
@jwt_required()
def get_business_insights():
    # Get comprehensive business data
    business_data = analytics_service.get_comprehensive_business_data()
    
    # AI-powered insights
    insights = ai_analytics.generate_business_insights(business_data)
    
    return jsonify({
        'insights': insights
    })

@analytics_bp.route('/alerts/data', methods=['POST'])
@jwt_required()
def create_data_alert():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    alert = analytics_service.create_data_alert(user, data)
    
    return jsonify({
        'success': True,
        'alert': {
            'id': alert.id,
            'name': alert.alert_name,
            'type': alert.alert_type
        }
    }), 201

@analytics_bp.route('/performance/summary')
@jwt_required()
def get_performance_summary():
    period = request.args.get('period', '30d')
    
    summary = analytics_service.get_performance_summary(period)
    
    # AI performance analysis
    ai_analysis = ai_analytics.analyze_overall_performance(summary)
    
    return jsonify({
        'summary': summary,
        'ai_analysis': ai_analysis
    })