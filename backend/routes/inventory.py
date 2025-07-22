from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import PaddyStock, ProductStock, User
# Temporarily disabled until services are fixed
# from services.inventory_service import InventoryService
# from services.ai_inventory_service import AIInventoryService
from extensions import db
from datetime import datetime
import json

inventory_bp = Blueprint('inventory', __name__)
# Temporarily disabled until services are fixed
# inventory_service = InventoryService()
# ai_inventory = AIInventoryService()

# Simple endpoints for frontend compatibility
@inventory_bp.route('/paddy', methods=['GET'])
@jwt_required()
def get_paddy():
    """Simple paddy stock endpoint for frontend compatibility"""
    paddy_stocks = PaddyStock.query.all()
    return jsonify({
        'stocks': [stock.to_dict() for stock in paddy_stocks],
        'total_quantity': sum(stock.quantity for stock in paddy_stocks),
        'total_value': sum(stock.quantity * stock.purchase_price for stock in paddy_stocks),
        'message': 'Paddy stock data loaded successfully'
    })

@inventory_bp.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    """Simple product stock endpoint for frontend compatibility"""
    product_stocks = ProductStock.query.all()
    return jsonify({
        'stocks': [stock.to_dict() for stock in product_stocks],
        'total_quantity': sum(stock.quantity for stock in product_stocks),
        'total_value': sum(stock.quantity * stock.market_price for stock in product_stocks),
        'message': 'Product stock data loaded successfully'
    })

# Paddy Stock Management
@inventory_bp.route('/paddy-stock', methods=['GET'])
@jwt_required()
def get_paddy_stock():
    variety = request.args.get('variety', '')
    location = request.args.get('location', '')
    
    stocks = inventory_service.get_paddy_stock(variety, location)
    
    # AI stock analysis
    stock_analysis = ai_inventory.analyze_paddy_stock_levels([s.to_dict() for s in stocks])
    
    # AI demand prediction
    demand_forecast = ai_inventory.predict_paddy_demand(variety)
    
    return jsonify({
        'stocks': [s.to_dict() for s in stocks],
        'analysis': stock_analysis,
        'demand_forecast': demand_forecast
    })

@inventory_bp.route('/paddy-stock', methods=['POST'])
@jwt_required()
def add_paddy_stock():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI quality assessment
    quality_assessment = ai_inventory.assess_paddy_quality(data)
    
    # AI storage optimization
    storage_optimization = ai_inventory.optimize_storage_location(data)
    
    # AI pricing recommendation
    pricing_recommendation = ai_inventory.recommend_purchase_price(data)
    
    stock = inventory_service.add_paddy_stock(user, data, quality_assessment, storage_optimization)
    
    # AI post-addition recommendations
    recommendations = ai_inventory.get_stock_management_recommendations(stock.id)
    
    return jsonify({
        'success': True,
        'stock': stock.to_dict(),
        'quality_assessment': quality_assessment,
        'storage_optimization': storage_optimization,
        'pricing_recommendation': pricing_recommendation,
        'recommendations': recommendations
    }), 201

@inventory_bp.route('/paddy-stock/<int:stock_id>', methods=['PUT'])
@jwt_required()
def update_paddy_stock(stock_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    stock = inventory_service.update_paddy_stock(stock_id, user, data)
    
    return jsonify({
        'success': True,
        'stock': stock.to_dict()
    })

# Product Stock Management
@inventory_bp.route('/product-stock', methods=['GET'])
@jwt_required()
def get_product_stock():
    product_type = request.args.get('product_type', '')
    grade = request.args.get('grade', '')
    
    stocks = inventory_service.get_product_stock(product_type, grade)
    
    # AI stock analysis
    stock_analysis = ai_inventory.analyze_product_stock_levels([s.to_dict() for s in stocks])
    
    # AI sales velocity analysis
    velocity_analysis = ai_inventory.analyze_sales_velocity(product_type, grade)
    
    return jsonify({
        'stocks': [s.to_dict() for s in stocks],
        'analysis': stock_analysis,
        'velocity_analysis': velocity_analysis
    })

@inventory_bp.route('/product-stock', methods=['POST'])
@jwt_required()
def add_product_stock():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI pricing suggestions
    pricing_suggestion = ai_inventory.suggest_product_pricing(data)
    
    stock = inventory_service.add_product_stock(user, data, pricing_suggestion)
    
    return jsonify({
        'success': True,
        'stock': stock.to_dict(),
        'pricing_suggestion': pricing_suggestion
    }), 201

# Stock Movements
@inventory_bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    transaction_type = request.args.get('type', '')
    
    transactions = inventory_service.get_transactions(page, per_page, transaction_type)
    
    # AI transaction pattern analysis
    pattern_analysis = ai_inventory.analyze_transaction_patterns([t.to_dict() for t in transactions['items']])
    
    return jsonify({
        'transactions': [t.to_dict() for t in transactions['items']],
        'pagination': transactions['pagination'],
        'pattern_analysis': pattern_analysis
    })

@inventory_bp.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI transaction validation
    validation_result = ai_inventory.validate_transaction(data)
    
    if not validation_result['valid']:
        return jsonify({
            'success': False,
            'errors': validation_result['errors']
        }), 400
    
    # AI impact analysis
    impact_analysis = ai_inventory.analyze_transaction_impact(data)
    
    # AI fraud detection
    fraud_check = ai_inventory.detect_transaction_fraud(data)
    
    if fraud_check['is_suspicious']:
        return jsonify({
            'success': False,
            'message': 'Transaction flagged for review',
            'fraud_indicators': fraud_check['indicators']
        }), 400
    
    transaction = inventory_service.create_transaction(user, data)
    
    # AI post-transaction recommendations
    recommendations = ai_inventory.get_post_transaction_recommendations(transaction.id)
    
    return jsonify({
        'success': True,
        'transaction': transaction.to_dict(),
        'impact_analysis': impact_analysis,
        'recommendations': recommendations
    }), 201

# Inventory Analytics
@inventory_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
def get_inventory_overview():
    overview = inventory_service.get_inventory_overview()
    
    # AI-enhanced analytics
    ai_analytics = ai_inventory.enhance_inventory_analytics(overview)
    
    return jsonify({
        'overview': overview,
        'ai_analytics': ai_analytics
    })

@inventory_bp.route('/analytics/turnover', methods=['GET'])
@jwt_required()
def get_inventory_turnover():
    days = request.args.get('days', 30, type=int)
    turnover = inventory_service.calculate_inventory_turnover(days)
    
    return jsonify(turnover)

@inventory_bp.route('/analytics/valuation', methods=['GET'])
@jwt_required()
def get_inventory_valuation():
    method = request.args.get('method', 'fifo')
    
    valuation = inventory_service.calculate_inventory_valuation(method)
    
    # AI valuation optimization
    optimization = ai_inventory.optimize_inventory_valuation(valuation)
    
    # AI market price analysis
    market_analysis = ai_inventory.analyze_market_prices()
    
    return jsonify({
        'valuation': valuation,
        'optimization': optimization,
        'market_analysis': market_analysis
    })

# Reorder Management
@inventory_bp.route('/reorder-rules', methods=['GET'])
@jwt_required()
def get_reorder_rules():
    rules = inventory_service.get_reorder_rules()
    
    # AI rule effectiveness analysis
    effectiveness_analysis = ai_inventory.analyze_rule_effectiveness([rule.to_dict() for rule in rules])
    
    return jsonify({
        'rules': [rule.to_dict() for rule in rules],
        'effectiveness_analysis': effectiveness_analysis
    })

@inventory_bp.route('/reorder-rules', methods=['POST'])
@jwt_required()
def create_reorder_rule():
    user_id = get_jwt_identity()
    
    data = request.get_json()
    
    # AI optimization of reorder parameters
    optimized_rule = ai_inventory.optimize_reorder_rule(data)
    
    rule = inventory_service.create_reorder_rule(optimized_rule)
    
    return jsonify({
        'success': True,
        'rule': rule.to_dict(),
        'optimization_notes': optimized_rule.get('optimization_notes', [])
    }), 201

@inventory_bp.route('/reorder-alerts', methods=['GET'])
@jwt_required()
def get_reorder_alerts():
    alerts = inventory_service.check_reorder_alerts()
    
    # AI prioritization of alerts
    prioritized_alerts = ai_inventory.prioritize_reorder_alerts(alerts)
    
    return jsonify({
        'alerts': prioritized_alerts
    })

# Supplier Management
@inventory_bp.route('/suppliers', methods=['GET'])
@jwt_required()
def get_suppliers():
    suppliers = inventory_service.get_suppliers()
    
    # AI supplier performance analysis
    performance_analysis = ai_inventory.analyze_supplier_performance(suppliers)
    
    return jsonify({
        'suppliers': suppliers,
        'performance_analysis': performance_analysis
    })

@inventory_bp.route('/suppliers', methods=['POST'])
@jwt_required()
def create_supplier():
    data = request.get_json()
    supplier = inventory_service.create_supplier(data)
    
    return jsonify({
        'success': True,
        'supplier': supplier.to_dict()
    }), 201

# AI-Powered Features
@inventory_bp.route('/ai/demand-forecast', methods=['POST'])
@jwt_required()
def get_ai_demand_forecast():
    data = request.get_json()
    forecast = ai_inventory.generate_demand_forecast(data)
    
    return jsonify(forecast)

@inventory_bp.route('/ai/optimize-stock-levels', methods=['POST'])
@jwt_required()
def optimize_stock_levels():
    data = request.get_json()
    optimization = ai_inventory.optimize_stock_levels(data)
    
    return jsonify(optimization)

@inventory_bp.route('/ai/price-recommendations', methods=['POST'])
@jwt_required()
def get_price_recommendations():
    data = request.get_json()
    recommendations = ai_inventory.get_pricing_recommendations(data)
    
    return jsonify(recommendations)

# Inventory Reports
@inventory_bp.route('/reports/stock-aging', methods=['GET'])
@jwt_required()
def get_stock_aging_report():
    report = inventory_service.generate_stock_aging_report()
    
    return jsonify(report)

@inventory_bp.route('/reports/movement-summary', methods=['GET'])
@jwt_required()
def get_movement_summary():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    summary = inventory_service.generate_movement_summary(start_date, end_date)
    
    return jsonify(summary)

@inventory_bp.route('/reports/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_report():
    report = inventory_service.generate_low_stock_report()
    
    # AI recommendations for low stock items
    ai_recommendations = ai_inventory.get_low_stock_recommendations(report)
    
    return jsonify({
        'report': report,
        'ai_recommendations': ai_recommendations
    })

@inventory_bp.route('/waste-tracking', methods=['GET'])
@jwt_required()
def get_waste_tracking():
    period = request.args.get('period', 'monthly')
    
    waste_data = inventory_service.get_waste_tracking(period)
    
    # AI waste analysis
    waste_analysis = ai_inventory.analyze_waste_patterns(waste_data)
    
    # AI waste reduction recommendations
    reduction_recommendations = ai_inventory.recommend_waste_reduction(waste_data)
    
    return jsonify({
        'waste_data': waste_data,
        'analysis': waste_analysis,
        'reduction_recommendations': reduction_recommendations
    })

@inventory_bp.route('/optimization', methods=['POST'])
@jwt_required()
def optimize_inventory():
    data = request.get_json()
    optimization_type = data.get('type', 'cost')
    
    # AI inventory optimization
    optimization_result = ai_inventory.optimize_inventory_levels(data, optimization_type)
    
    return jsonify(optimization_result)

@inventory_bp.route('/aging-analysis', methods=['GET'])
@jwt_required()
def get_aging_analysis():
    stock_type = request.args.get('stock_type', 'all')
    
    aging_data = inventory_service.get_aging_analysis(stock_type)
    
    # AI aging insights
    aging_insights = ai_inventory.analyze_stock_aging(aging_data)
    
    # AI disposal recommendations
    disposal_recommendations = ai_inventory.recommend_stock_disposal(aging_data)
    
    return jsonify({
        'aging_data': aging_data,
        'insights': aging_insights,
        'disposal_recommendations': disposal_recommendations
    })

@inventory_bp.route('/turnover-analysis', methods=['GET'])
@jwt_required()
def get_turnover_analysis():
    period_days = request.args.get('days', 90, type=int)
    
    turnover_data = inventory_service.calculate_turnover_rates(period_days)
    
    # AI turnover optimization
    turnover_optimization = ai_inventory.optimize_turnover_rates(turnover_data)
    
    return jsonify({
        'turnover_data': turnover_data,
        'optimization': turnover_optimization
    })

@inventory_bp.route('/quality-tracking', methods=['GET'])
@jwt_required()
def get_quality_tracking():
    stock_type = request.args.get('type', 'all')  # paddy, product, all
    
    quality_data = inventory_service.get_quality_tracking(stock_type)
    
    # AI quality trend analysis
    quality_analysis = ai_inventory.analyze_quality_trends(quality_data)
    
    return jsonify({
        'quality_data': quality_data,
        'ai_analysis': quality_analysis
    })

@inventory_bp.route('/storage-optimization', methods=['GET'])
@jwt_required()
def get_storage_optimization():
    # AI storage space optimization
    optimization = ai_inventory.optimize_storage_utilization()
    
    return jsonify(optimization)

@inventory_bp.route('/predictive-maintenance', methods=['GET'])
@jwt_required()
def get_predictive_maintenance():
    # AI predictive maintenance for storage equipment
    maintenance_predictions = ai_inventory.predict_equipment_maintenance()
    
    return jsonify({'maintenance_predictions': maintenance_predictions})

@inventory_bp.route('/cost-analysis', methods=['GET'])
@jwt_required()
def get_cost_analysis():
    period_days = request.args.get('days', 30, type=int)
    
    cost_data = inventory_service.get_inventory_costs(period_days)
    
    # AI cost optimization
    cost_optimization = ai_inventory.optimize_inventory_costs(cost_data)
    
    return jsonify({
        'cost_data': cost_data,
        'optimization': cost_optimization
    })

@inventory_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_inventory_dashboard():
    user_id = get_jwt_identity()
    
    dashboard_data = inventory_service.get_dashboard_data()
    
    # AI-enhanced dashboard insights
    ai_insights = ai_inventory.generate_dashboard_insights(dashboard_data)
    
    # AI stock level optimization
    optimization_suggestions = ai_inventory.get_stock_optimization_suggestions()
    
    return jsonify({
        'dashboard': dashboard_data,
        'ai_insights': ai_insights,
        'optimization_suggestions': optimization_suggestions
    })

@inventory_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_stock_alerts():
    alert_type = request.args.get('type', '')
    priority = request.args.get('priority', '')
    
    alerts = inventory_service.get_stock_alerts(alert_type, priority)
    
    # AI alert prioritization
    prioritized_alerts = ai_inventory.prioritize_alerts([a.to_dict() for a in alerts])
    
    # AI resolution suggestions
    resolution_suggestions = ai_inventory.suggest_alert_resolutions(prioritized_alerts)
    
    return jsonify({
        'alerts': prioritized_alerts,
        'resolution_suggestions': resolution_suggestions
    })

@inventory_bp.route('/reorder-points', methods=['GET'])
@jwt_required()
def get_reorder_points():
    # AI-calculated reorder points
    reorder_points = ai_inventory.calculate_optimal_reorder_points()
    
    return jsonify({'reorder_points': reorder_points})

@inventory_bp.route('/reorder-points', methods=['POST'])
@jwt_required()
def update_reorder_points():
    data = request.get_json()
    
    # AI validation of reorder points
    validation = ai_inventory.validate_reorder_points(data)
    
    if validation['valid']:
        result = inventory_service.update_reorder_points(data['reorder_points'])
        return jsonify({'success': True, 'updated': result})
    else:
        return jsonify({
            'success': False,
            'errors': validation['errors']
        }), 400

@inventory_bp.route('/demand-forecast', methods=['GET'])
@jwt_required()
def get_demand_forecast():
    product_type = request.args.get('product_type', '')
    days = request.args.get('days', 30, type=int)
    
    # AI demand forecasting
    forecast = ai_inventory.forecast_demand(product_type, days)
    
    # AI seasonal analysis
    seasonal_analysis = ai_inventory.analyze_seasonal_patterns(product_type)
    
    return jsonify({
        'forecast': forecast,
        'seasonal_analysis': seasonal_analysis
    })

@inventory_bp.route('/cycle-count', methods=['POST'])
@jwt_required()
def initiate_cycle_count():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI cycle count optimization
    optimized_plan = ai_inventory.optimize_cycle_count_plan(data)
    
    cycle_count = inventory_service.initiate_cycle_count(user, optimized_plan)
    
    return jsonify({
        'success': True,
        'cycle_count': cycle_count.to_dict(),
        'optimized_plan': optimized_plan
    }), 201

@inventory_bp.route('/supplier-performance', methods=['GET'])
@jwt_required()
def get_supplier_performance():
    supplier_id = request.args.get('supplier_id', type=int)
    
    performance_data = inventory_service.get_supplier_performance(supplier_id)
    
    # AI supplier analysis
    supplier_analysis = ai_inventory.analyze_supplier_performance(performance_data)
    
    # AI supplier recommendations
    supplier_recommendations = ai_inventory.recommend_supplier_actions(performance_data)
    
    return jsonify({
        'performance_data': performance_data,
        'analysis': supplier_analysis,
        'recommendations': supplier_recommendations
    })

@inventory_bp.route('/quality-trends', methods=['GET'])
@jwt_required()
def get_quality_trends():
    product_type = request.args.get('product_type', '')
    period = request.args.get('period', 'quarterly')
    
    quality_data = inventory_service.get_quality_trends(product_type, period)
    
    # AI quality analysis
    quality_analysis = ai_inventory.analyze_quality_trends(quality_data)
    
    # AI quality improvement recommendations
    improvement_recommendations = ai_inventory.recommend_quality_improvements(quality_data)
    
    return jsonify({
        'quality_data': quality_data,
        'analysis': quality_analysis,
        'improvement_recommendations': improvement_recommendations
    })

@inventory_bp.route('/smart-alerts', methods=['GET'])
@jwt_required()
def get_smart_alerts():
    # AI-generated smart alerts
    smart_alerts = ai_inventory.generate_smart_alerts()
    
    return jsonify({'smart_alerts': smart_alerts})

@inventory_bp.route('/batch-tracking', methods=['GET'])
@jwt_required()
def get_batch_tracking():
    batch_id = request.args.get('batch_id', '')
    
    tracking_data = inventory_service.get_batch_tracking(batch_id)
    
    # AI batch analysis
    batch_analysis = ai_inventory.analyze_batch_performance(tracking_data)
    
    return jsonify({
        'tracking_data': tracking_data,
        'analysis': batch_analysis
    })

