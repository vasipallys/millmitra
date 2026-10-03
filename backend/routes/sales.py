from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Customer, SalesOrder
from extensions import db
from datetime import datetime, timedelta
from utils import current_user
from sqlalchemy import or_
import uuid

sales_bp = Blueprint('sales', __name__)


class _ServiceStub:
    class _Result:
        def to_dict(self):
            return {}

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            if name.startswith('get_'):
                return {
                    'total_orders': 0,
                    'total_revenue': 0,
                    'average_order_value': 0,
                    'recent_orders': [],
                    'top_customers': []
                }
            return {}
        return _call


sales_service = _ServiceStub()
ai_sales = _ServiceStub()


def _customer_code():
    count = Customer.query.count() + 1
    return f'CUST{count:06d}'


def _order_number():
    today = datetime.utcnow().strftime('%y%m%d')
    count = SalesOrder.query.filter(
        SalesOrder.order_number.like(f'SO{today}%')
    ).count() + 1
    return f'SO{today}{count:03d}'

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
    start = datetime.utcnow() - timedelta(days=days)
    orders = SalesOrder.query.filter(SalesOrder.created_at >= start).all()
    total_revenue = sum(order.total_amount or 0 for order in orders)
    dashboard_data = {
        'total_orders': len(orders),
        'total_revenue': total_revenue,
        'average_order_value': total_revenue / len(orders) if orders else 0,
        'recent_orders': [order.to_dict() for order in orders[:10]],
        'growth': 0
    }
    return jsonify({
        'success': True,
        'dashboard': dashboard_data,
        'ai_insights': {'message': 'Sales dashboard loaded'}
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
            or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.business_name.ilike(f'%{search}%'),
                Customer.customer_code.ilike(f'%{search}%')
            )
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
    user = current_user()
    data = request.get_json() or {}
    if not data.get('name') or not data.get('phone'):
        return jsonify({'success': False, 'message': 'Name and phone are required'}), 400
    customer = Customer(
        customer_code=_customer_code(),
        name=data['name'],
        customer_type=data.get('customer_type', 'retailer'),
        phone=data['phone'],
        email=data.get('email'),
        contact_person=data.get('contact_person'),
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        pincode=data.get('pincode'),
        business_name=data.get('business_name') or data.get('company_name'),
        gst_number=data.get('gst_number'),
        pan_number=data.get('pan_number'),
        credit_limit=float(data.get('credit_limit', 0) or 0),
        payment_terms=data.get('payment_terms', 'immediate'),
        created_by=user.id if user else None
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({
        'success': True,
        'customer': customer.to_dict(),
        'ai_analysis': {}
    }), 201

@sales_bp.route('/customers/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_details(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    orders = SalesOrder.query.filter_by(customer_id=customer_id).all()
    analytics = {
        'customer': customer.to_dict(),
        'order_count': len(orders),
        'total_amount': sum(o.total_amount or 0 for o in orders)
    }
    return jsonify({
        'success': True,
        'analytics': analytics,
        'ai_insights': {}
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
    user = current_user()
    data = request.get_json() or {}
    if not data.get('customer_id'):
        return jsonify({'success': False, 'message': 'customer_id is required'}), 400

    customer = Customer.query.get(data['customer_id'])
    if not customer:
        return jsonify({'success': False, 'message': 'Customer not found'}), 404

    items = data.get('items', [])
    total_quantity = sum(float(item.get('quantity', 0) or 0) for item in items)
    base_amount = sum(float(item.get('quantity', 0) or 0) * float(item.get('unit_price', 0) or 0) for item in items)
    tax_amount = float(data.get('tax_amount', base_amount * 0.05) or 0)
    discount_amount = float(data.get('discount_amount', 0) or 0)
    total_amount = base_amount + tax_amount - discount_amount

    order_date = datetime.utcnow()
    if data.get('order_date'):
        try:
            order_date = datetime.fromisoformat(str(data['order_date']).replace('Z', ''))
        except ValueError:
            pass
    delivery_date = None
    if data.get('delivery_date'):
        try:
            delivery_date = datetime.fromisoformat(str(data['delivery_date']).replace('Z', ''))
        except ValueError:
            try:
                delivery_date = datetime.strptime(data['delivery_date'], '%Y-%m-%d')
            except ValueError:
                pass

    order = SalesOrder(
        order_number=_order_number(),
        customer_id=customer.id,
        order_date=order_date,
        delivery_date=delivery_date,
        total_quantity=total_quantity,
        total_amount=total_amount,
        base_amount=base_amount,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        payment_terms=data.get('payment_terms') or customer.payment_terms,
        delivery_address=data.get('delivery_address') or customer.address,
        status='pending',
        created_by=user.id if user else None
    )
    order.set_order_items(items)
    order.calculate_totals()
    db.session.add(order)
    customer.update_business_metrics(order.total_amount)
    db.session.commit()
    from services.notification_service import sales_order_created
    sales_order_created(order, customer)

    return jsonify({
        'success': True,
        'order': order.to_dict(),
        'ai_insights': {}
    }), 201

@sales_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    data = request.get_json() or {}
    status = data.get('status')
    if not status:
        return jsonify({'success': False, 'message': 'status is required'}), 400
    order.status = status
    db.session.commit()
    return jsonify({'success': True, 'order': order.to_dict()})

# Quotations / leads are not modeled in the current schema
@sales_bp.route('/quotations', methods=['GET'])
@jwt_required()
def get_quotations():
    return jsonify({
        'success': True,
        'quotations': [],
        'pagination': {'page': 1, 'pages': 0, 'per_page': 20, 'total': 0}
    })

@sales_bp.route('/quotations', methods=['POST'])
@jwt_required()
def create_quotation():
    return jsonify({
        'success': False,
        'message': 'Quotations are not enabled in this deployment'
    }), 501

@sales_bp.route('/quotations/<int:quotation_id>/convert', methods=['POST'])
@jwt_required()
def convert_quotation_to_order(quotation_id):
    return jsonify({'success': False, 'message': 'Quotations are not enabled'}), 501

@sales_bp.route('/leads', methods=['GET'])
@jwt_required()
def get_sales_leads():
    return jsonify({
        'success': True,
        'leads': [],
        'pagination': {'page': 1, 'pages': 0, 'per_page': 20, 'total': 0}
    })

@sales_bp.route('/leads', methods=['POST'])
@jwt_required()
def create_sales_lead():
    return jsonify({'success': False, 'message': 'Leads are not enabled in this deployment'}), 501

@sales_bp.route('/leads/<int:lead_id>/status', methods=['PUT'])
@jwt_required()
def update_lead_status(lead_id):
    return jsonify({'success': False, 'message': 'Leads are not enabled'}), 501

@sales_bp.route('/analytics/revenue', methods=['GET'])
@jwt_required()
def get_revenue_analytics():
    return get_sales_dashboard()

@sales_bp.route('/analytics/forecast', methods=['GET'])
@jwt_required()
def get_sales_forecast():
    return jsonify({'success': True, 'forecast': []})

@sales_bp.route('/lead-scoring', methods=['POST'])
@jwt_required()
def score_sales_lead():
    return jsonify({
        'lead_score': {'score': 0},
        'qualification_assessment': {'status': 'unknown'},
        'next_action': {'action': 'review'}
    })


