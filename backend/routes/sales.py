from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Customer, SalesOrder
from extensions import db
from datetime import datetime, timedelta
import json

# Temporarily disabled until services are fixed
# from services.sales_service import SalesService

sales_bp = Blueprint('sales', __name__)

# Mock AI Sales Service
class MockAISalesService:
    def generate_dashboard_insights(self, dashboard_data):
        return {
            'trends': ['Sales increasing', 'Customer satisfaction high'],
            'predictions': ['Next month sales: +20%', 'New customers: +15%'],
            'recommendations': ['Focus on high-value customers', 'Expand product range'],
            'alerts': []
        }

    def analyze_new_customer(self, data):
        return {
            'risk_score': 25,
            'credit_rating': 'A',
            'potential_value': 50000,
            'recommendations': ['Standard credit terms', 'Regular follow-up']
        }

    def generate_customer_insights(self, analytics):
        return {
            'loyalty_score': 85,
            'churn_risk': 'low',
            'upsell_opportunities': ['Premium products', 'Bulk orders'],
            'next_best_action': 'Schedule quarterly review'
        }

    def optimize_sales_order(self, data):
        return {
            'optimized_pricing': True,
            'margin_improvement': '5%',
            'delivery_optimization': 'Standard shipping recommended'
        }

    def predict_order_fulfillment(self, data):
        return {
            'probability': 95,
            'estimated_delivery': '5 days',
            'potential_delays': []
        }

    def assess_order_risk(self, data):
        return {
            'risk_level': 'low',
            'payment_risk': 15,
            'delivery_risk': 10
        }

    def optimize_quotation_pricing(self, data):
        return {
            'recommended_price': float(data.get('amount', 0)) * 1.05,
            'margin_analysis': 'Good',
            'competitive_position': 'Competitive'
        }

    def predict_quotation_conversion(self, data):
        return {
            'probability': 75,
            'factors': ['Good pricing', 'Strong relationship'],
            'recommendations': ['Follow up in 3 days']
        }

    def analyze_competition(self, data):
        return {
            'competitive_advantage': 'Quality and service',
            'price_position': 'Competitive',
            'market_share': '15%'
        }

    def calculate_lead_score(self, data):
        return {
            'score': 85,
            'factors': ['Company size', 'Industry match', 'Budget confirmed'],
            'confidence': 'high'
        }

    def assess_lead_qualification(self, data):
        return {
            'status': 'qualified',
            'criteria_met': ['Budget', 'Authority', 'Need', 'Timeline'],
            'next_steps': ['Schedule demo', 'Prepare proposal']
        }

    def recommend_lead_action(self, lead_scoring, qualification_assessment):
        return {
            'action': 'Schedule meeting',
            'priority': 'high',
            'timeline': '2 days'
        }

    def analyze_revenue_trends(self, analytics):
        return {
            'growth_rate': '15%',
            'trend': 'positive',
            'key_drivers': ['New customers', 'Increased order size'],
            'forecast': 'Continued growth expected'
        }

    def forecast_sales(self, months):
        return {
            'forecast_period': f'{months} months',
            'projected_revenue': 750000,
            'confidence_interval': '±10%',
            'key_assumptions': ['Market stability', 'Current growth rate']
        }

# Mock Sales Service
class MockSalesService:
    def get_sales_dashboard_data(self, days):
        return {
            'total_revenue': 500000,
            'total_orders': 150,
            'average_order_value': 3333,
            'new_customers': 25,
            'customer_retention': 85,
            'top_products': ['Basmati Rice', 'Sona Masuri', 'IR64']
        }

    def create_customer(self, user, data, ai_analysis):
        customer = Customer(
            name=data.get('name', 'New Customer'),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            created_by=user.id
        )

        db.session.add(customer)
        db.session.commit()
        return customer

    def get_customer_analytics(self, customer_id):
        customer = Customer.query.get(customer_id)
        if not customer:
            return None

        return {
            'customer': customer.to_dict(),
            'total_orders': 15,
            'total_revenue': 75000,
            'average_order_value': 5000,
            'last_order_date': '2025-07-20'
        }

    def create_sales_order(self, user, data, ai_insights):
        order = SalesOrder(
            customer_id=data.get('customer_id'),
            order_number=f"SO{datetime.now().strftime('%Y%m%d%H%M%S')}",
            total_amount=float(data.get('total_amount', 0)),
            status='pending',
            order_date=datetime.now(),
            created_by=user.id
        )

        db.session.add(order)
        db.session.commit()
        return order

    def update_order_status(self, order_id, status, user):
        order = SalesOrder.query.get(order_id)
        if order:
            order.status = status
            db.session.commit()
        return order

    def create_quotation(self, user, data, ai_insights):
        # Mock quotation object
        class MockQuotation:
            def __init__(self):
                self.id = 1
                self.quotation_number = f"QT{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.customer_id = data.get('customer_id')
                self.amount = float(data.get('amount', 0))
                self.status = 'pending'
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'quotation_number': self.quotation_number,
                    'customer_id': self.customer_id,
                    'amount': self.amount,
                    'status': self.status,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockQuotation()

    def convert_quotation_to_order(self, quotation_id, user, modifications):
        # Mock conversion
        order = SalesOrder(
            customer_id=1,
            order_number=f"SO{datetime.now().strftime('%Y%m%d%H%M%S')}",
            total_amount=float(modifications.get('amount', 5000)),
            status='confirmed',
            order_date=datetime.now(),
            created_by=user.id
        )

        db.session.add(order)
        db.session.commit()
        return order

    def create_lead(self, user, data, ai_scoring):
        # Mock lead object
        class MockLead:
            def __init__(self):
                self.id = 1
                self.company_name = data.get('company_name', 'New Lead')
                self.contact_name = data.get('contact_name', '')
                self.email = data.get('email', '')
                self.phone = data.get('phone', '')
                self.status = 'new'
                self.score = ai_scoring.get('lead_score', 50)
                self.created_by = user.id
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'company_name': self.company_name,
                    'contact_name': self.contact_name,
                    'email': self.email,
                    'phone': self.phone,
                    'status': self.status,
                    'score': self.score,
                    'created_by': self.created_by,
                    'created_at': self.created_at.isoformat()
                }

        return MockLead()

    def update_lead_status(self, lead_id, status, user):
        # Mock lead update
        class MockLead:
            def __init__(self):
                self.id = lead_id
                self.status = status
                self.updated_by = user.id
                self.updated_at = datetime.now()

            def to_dict(self):
                return {
                    'id': self.id,
                    'status': self.status,
                    'updated_by': self.updated_by,
                    'updated_at': self.updated_at.isoformat()
                }

        return MockLead()

# Initialize services
sales_service = MockSalesService()
ai_sales = MockAISalesService()

# Simple analytics endpoint for frontend compatibility
@sales_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_sales_analytics():
    """General sales analytics endpoint for frontend compatibility"""

    # Get basic sales data
    orders = SalesOrder.query.all()
    total_orders = len(orders)
    total_revenue = sum(order.total_amount or 0 for order in orders)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    # Recent orders (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_orders = [order for order in orders if order.created_at and order.created_at >= thirty_days_ago]

    analytics = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_order_value': avg_order_value,
        'recent_orders_count': len(recent_orders),
        'recent_revenue': sum(order.total_amount or 0 for order in recent_orders),
        'growth_rate': 5.2,  # Mock growth rate
        'top_products': ['Premium Rice', 'Standard Rice', 'Organic Rice']
    }

    return jsonify({
        'analytics': analytics,
        'message': 'Sales analytics loaded successfully'
    })

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

