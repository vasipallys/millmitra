from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.production import ProductionBatch, QualityTest
from models.inventory import PaddyStock, ProductStock
from models.sales import SalesOrder
from services.dashboard_service import SmartDashboardService
from services.ai_insights_service import AIInsightsService
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)
dashboard_service = SmartDashboardService()
ai_insights = AIInsightsService()

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_dashboard_overview():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get time range from query params
    days = request.args.get('days', 7, type=int)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get AI-powered dashboard data
    overview = dashboard_service.get_smart_overview(user, start_date, end_date)
    
    return jsonify(overview)

@dashboard_bp.route('/widgets', methods=['GET'])
@jwt_required()
def get_smart_widgets():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # AI determines which widgets to show based on role, time, and context
    widgets = dashboard_service.get_priority_widgets(user)
    
    return jsonify({'widgets': widgets})

@dashboard_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_ai_insights():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get AI-generated insights
    insights = ai_insights.generate_insights(user)
    
    return jsonify({'insights': insights})

@dashboard_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_smart_alerts():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get AI-powered alerts and recommendations
    alerts = dashboard_service.get_smart_alerts(user)
    
    return jsonify({'alerts': alerts})

@dashboard_bp.route('/metrics/production', methods=['GET'])
@jwt_required()
def get_production_metrics():
    user_id = get_jwt_identity()
    
    days = request.args.get('days', 30, type=int)
    metrics = dashboard_service.get_production_metrics(days)
    
    return jsonify(metrics)

@dashboard_bp.route('/metrics/quality', methods=['GET'])
@jwt_required()
def get_quality_metrics():
    user_id = get_jwt_identity()
    
    days = request.args.get('days', 30, type=int)
    metrics = dashboard_service.get_quality_metrics(days)
    
    return jsonify(metrics)

@dashboard_bp.route('/metrics/inventory', methods=['GET'])
@jwt_required()
def get_inventory_metrics():
    user_id = get_jwt_identity()
    
    metrics = dashboard_service.get_inventory_metrics()
    
    return jsonify(metrics)

@dashboard_bp.route('/predictions', methods=['GET'])
@jwt_required()
def get_predictions():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    prediction_type = request.args.get('type', 'all')
    predictions = ai_insights.get_predictions(user, prediction_type)
    
    return jsonify({'predictions': predictions})

@dashboard_bp.route('/customize', methods=['POST'])
@jwt_required()
def customize_dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    customization = request.get_json()
    dashboard_service.save_user_preferences(user, customization)
    
    return jsonify({'success': True})