from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Customer, SalesOrder
# Temporarily disabled until services are fixed
# from services.sales_service import SalesService
from extensions import db

sales_bp = Blueprint('sales', __name__)
# Temporarily disabled until services are fixed
# sales_service = SalesService()
# ai_sales = SalesAI()

# Dashboard
@sales_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_sales_dashboard():
    days = request.args.get('days', 30, type=int)
    
    dashboard_data = sales_service.get_sales_dashboard_data(days)
    
    # AI insights for dashboard
    ai_insights = ai_sales.generate_dashboard_insights(dashboard_data)
    
    return jsonify({
        'success': True,
        'dashboard': dashboard_data,
        'ai_insights': ai_insights
    })

# Customer Management
@sales_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    customer_type = request.args.get('type', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(
            Customer.name.ilike(f'%{search}%') |
            Customer.company_name.ilike(f'%{search}%') |
            Customer.customer_code.ilike(f'%{search}%')
        )
    
    if customer_type:
        query = query.filter(Customer.customer_type == customer_type)
    
    customers = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'customers': [customer.to_dict() for customer in customers.items],
        'pagination': {
            'page': page,
            'pages': customers.pages,
            'per_page': per_page,
            'total': customers.total
        }
    })

@sales_bp.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI customer analysis
    ai_analysis = ai_sales.analyze_new_customer(data)
    
    customer = sales_service.create_customer(user, data, ai_analysis)
    
    return jsonify({
        'success': True,
        'customer': customer.to_dict(),
        'ai_analysis': ai_analysis
    }), 201

@sales_bp.route('/customers/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_details():
    customer_id = request.view_args['customer_id']
    
    analytics = sales_service.get_customer_analytics(customer_id)
    
    if not analytics:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404
    
    # AI customer insights
    ai_insights = ai_sales.generate_customer_insights(analytics)
    
    return jsonify({
        'success': True,
        'analytics': analytics,
        'ai_insights': ai_insights
    })

# Sales Orders
@sales_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_sales_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    customer_id = request.args.get('customer_id', type=int)
    
    query = SalesOrder.query
    
    if status:
        query = query.filter(SalesOrder.status == status)
    
    if customer_id:
        query = query.filter(SalesOrder.customer_id == customer_id)
    
    orders = query.order_by(SalesOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'orders': [order.to_dict() for order in orders.items],
        'pagination': {
            'page': page,
            'pages': orders.pages,
            'per_page': per_page,
            'total': orders.total
        }
    })

@sales_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_sales_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI order optimization
    ai_insights = ai_sales.optimize_sales_order(data)
    
    # AI fulfillment prediction
    fulfillment_prediction = ai_sales.predict_order_fulfillment(data)
    
    # AI risk assessment
    risk_assessment = ai_sales.assess_order_risk(data)
    
    combined_insights = {
        'fulfillment_prediction': fulfillment_prediction,
        'risk_assessment': risk_assessment,
        **ai_insights
    }
    
    order = sales_service.create_sales_order(user, data, combined_insights)
    
    return jsonify({
        'success': True,
        'order': order.to_dict(),
        'ai_insights': combined_insights
    }), 201

@sales_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    order_id = request.view_args['order_id']
    
    data = request.get_json()
    status = data.get('status')
    
    try:
        order = sales_service.update_order_status(order_id, status, user)
        
        if not order:
            return jsonify({'success': False, 'message': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# Quotations
@sales_bp.route('/quotations', methods=['GET'])
@jwt_required()
def get_quotations():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    
    query = Quotation.query
    
    if status:
        query = query.filter(Quotation.status == status)
    
    quotations = query.order_by(Quotation.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'quotations': [quotation.to_dict() for quotation in quotations.items],
        'pagination': {
            'page': page,
            'pages': quotations.pages,
            'per_page': per_page,
            'total': quotations.total
        }
    })

@sales_bp.route('/quotations', methods=['POST'])
@jwt_required()
def create_quotation():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI pricing optimization
    pricing_optimization = ai_sales.optimize_quotation_pricing(data)
    
    # AI conversion prediction
    conversion_prediction = ai_sales.predict_quotation_conversion(data)
    
    # AI competitive analysis
    competitive_analysis = ai_sales.analyze_competition(data)
    
    ai_insights = {
        'conversion_probability': conversion_prediction.get('probability'),
        'competitive_analysis': competitive_analysis,
        **pricing_optimization
    }
    
    quotation = sales_service.create_quotation(user, data, ai_insights)
    
    return jsonify({
        'success': True,
        'quotation': quotation.to_dict(),
        'ai_insights': ai_insights
    }), 201

@sales_bp.route('/quotations/<int:quotation_id>/convert', methods=['POST'])
@jwt_required()
def convert_quotation_to_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    quotation_id = request.view_args['quotation_id']
    
    data = request.get_json()
    modifications = data.get('modifications')
    
    try:
        order = sales_service.convert_quotation_to_order(quotation_id, user, modifications)
        
        if not order:
            return jsonify({'success': False, 'message': 'Quotation not found'}), 404
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        })
    
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# Sales Leads
@sales_bp.route('/leads', methods=['GET'])
@jwt_required()
def get_sales_leads():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    assigned_to = request.args.get('assigned_to', type=int)
    
    query = SalesLead.query
    
    if status:
        query = query.filter(SalesLead.status == status)
    
    if assigned_to:
        query = query.filter(SalesLead.assigned_to == assigned_to)
    
    leads = query.order_by(SalesLead.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'success': True,
        'leads': [lead.to_dict() for lead in leads.items],
        'pagination': {
            'page': page,
            'pages': leads.pages,
            'per_page': per_page,
            'total': leads.total
        }
    })

@sales_bp.route('/leads', methods=['POST'])
@jwt_required()
def create_sales_lead():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI lead scoring
    lead_scoring = ai_sales.calculate_lead_score(data)
    
    # AI lead qualification
    qualification_assessment = ai_sales.assess_lead_qualification(data)
    
    # AI next best action
    next_action = ai_sales.recommend_lead_action(lead_scoring, qualification_assessment)
    
    ai_scoring = {
        'lead_score': lead_scoring.get('score'),
        'qualification_status': qualification_assessment.get('status'),
        'next_action': next_action.get('action')
    }
    
    lead = sales_service.create_lead(user, data, ai_scoring)
    
    return jsonify({
        'success': True,
        'lead': lead.to_dict(),
        'ai_scoring': ai_scoring
    }), 201

@sales_bp.route('/leads/<int:lead_id>/status', methods=['PUT'])
@jwt_required()
def update_lead_status():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    lead_id = request.view_args['lead_id']
    
    data = request.get_json()
    status = data.get('status')
    
    lead = sales_service.update_lead_status(lead_id, status, user)
    
    if not lead:
        return jsonify({'success': False, 'message': 'Lead not found'}), 404
    
    return jsonify({
        'success': True,
        'lead': lead.to_dict()
    })

# Analytics
@sales_bp.route('/analytics/revenue', methods=['GET'])
@jwt_required()
def get_revenue_analytics():
    days = request.args.get('days', 30, type=int)
    
    # Get revenue analytics
    analytics = sales_service.get_sales_dashboard_data(days)
    
    # AI revenue insights
    ai_insights = ai_sales.analyze_revenue_trends(analytics)
    
    return jsonify({
        'success': True,
        'analytics': analytics,
        'ai_insights': ai_insights
    })

@sales_bp.route('/analytics/forecast', methods=['GET'])
@jwt_required()
def get_sales_forecast():
    months = request.args.get('months', 3, type=int)
    
    # AI sales forecasting
    forecast = ai_sales.forecast_sales(months)
    
    return jsonify({
        'success': True,
        'forecast': forecast
    })

@sales_bp.route('/lead-scoring', methods=['POST'])
@jwt_required()
def score_sales_lead():
    data = request.get_json()
    
    # AI lead scoring
    lead_score = ai_sales.calculate_lead_score(data)
    
    # AI lead qualification
    qualification_assessment = ai_sales.assess_lead_qualification(data)
    
    # AI next best action
    next_action = ai_sales.recommend_lead_action(lead_score, qualification_assessment)
    
    return jsonify({
        'lead_score': lead_score,
        'qualification_assessment': qualification_assessment,
        'next_action': next_action
    })

