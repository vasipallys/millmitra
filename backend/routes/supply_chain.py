from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from services.supply_chain_service import SupplyChainService
from services.ai_supply_chain_service import AISupplyChainService

supply_chain_bp = Blueprint('supply_chain', __name__)
supply_chain_service = SupplyChainService()
ai_supply_chain = AISupplyChainService()

@supply_chain_bp.route('/suppliers', methods=['POST'])
@jwt_required()
def create_supplier():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    supplier = supply_chain_service.create_supplier(user, data)
    
    return jsonify({
        'success': True,
        'supplier': {
            'id': supplier.id,
            'supplier_code': supplier.supplier_code,
            'company_name': supplier.company_name
        }
    }), 201

@supply_chain_bp.route('/purchase-orders', methods=['POST'])
@jwt_required()
def create_purchase_order():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI optimization
    ai_optimization = ai_supply_chain.optimize_purchase_order(data)
    
    # AI risk assessment
    risk_assessment = ai_supply_chain.assess_supply_risk(data['supplier_id'], data)
    
    ai_insights = {
        'recommendations': ai_optimization.get('recommendations', []),
        'risk_assessment': risk_assessment,
        'cost_savings': ai_optimization.get('cost_savings_potential', 0)
    }
    
    po = supply_chain_service.create_purchase_order(user, data, ai_insights)
    
    return jsonify({
        'success': True,
        'purchase_order': {
            'id': po.id,
            'po_number': po.po_number,
            'total_amount': po.total_amount
        },
        'ai_insights': ai_insights
    }), 201

@supply_chain_bp.route('/purchase-orders/<int:po_id>/receive', methods=['POST'])
@jwt_required()
def receive_purchase_order(po_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    po = supply_chain_service.receive_purchase_order(po_id, user, data)
    
    return jsonify({
        'success': True,
        'purchase_order': {
            'id': po.id,
            'status': po.status,
            'delivery_status': po.delivery_status
        }
    })

@supply_chain_bp.route('/procurement-requests', methods=['POST'])
@jwt_required()
def create_procurement_request():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI supplier recommendations
    supplier_recommendations = ai_supply_chain.recommend_suppliers(data)
    
    request_obj = supply_chain_service.create_procurement_request(user, data)
    
    return jsonify({
        'success': True,
        'request': {
            'id': request_obj.id,
            'request_number': request_obj.request_number
        },
        'supplier_recommendations': supplier_recommendations
    }), 201

@supply_chain_bp.route('/suppliers/<int:supplier_id>/performance')
@jwt_required()
def get_supplier_performance(supplier_id):
    period_days = request.args.get('period', 90, type=int)
    
    performance = supply_chain_service.evaluate_supplier_performance(supplier_id, period_days)
    
    # AI performance prediction
    ai_prediction = ai_supply_chain.predict_supplier_performance(
        {'supplier_id': supplier_id}, 
        {'period_days': period_days}
    )
    
    return jsonify({
        'performance': performance,
        'ai_prediction': ai_prediction
    })

@supply_chain_bp.route('/optimize-inventory', methods=['POST'])
@jwt_required()
def optimize_inventory():
    data = request.get_json()
    
    optimization = ai_supply_chain.optimize_inventory_levels(data)
    
    return jsonify({
        'success': True,
        'optimization': optimization
    })

@supply_chain_bp.route('/predict-delivery', methods=['POST'])
@jwt_required()
def predict_delivery():
    data = request.get_json()
    
    prediction = ai_supply_chain.predict_delivery_date(
        data['supplier_id'], 
        data['order_details']
    )
    
    return jsonify({
        'success': True,
        'prediction': prediction
    })