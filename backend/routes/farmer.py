from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from services.farmer_service import FarmerService
from services.ai_farmer_service import AIFarmerService

farmer_bp = Blueprint('farmer', __name__)
farmer_service = FarmerService()
ai_farmer = AIFarmerService()

@farmer_bp.route('/register', methods=['POST'])
@jwt_required()
def register_farmer():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI verification and validation
    ai_verification = ai_farmer.verify_farmer_details(data)
    
    # AI duplicate detection
    duplicate_check = ai_farmer.check_duplicate_farmer(data)
    
    if duplicate_check['is_duplicate']:
        return jsonify({
            'success': False,
            'message': 'Potential duplicate farmer found',
            'duplicate_matches': duplicate_check['matches']
        }), 400
    
    farmer = farmer_service.register_farmer(user, data, ai_verification)
    
    # AI onboarding recommendations
    onboarding_recommendations = ai_farmer.get_onboarding_recommendations(farmer.to_dict())
    
    return jsonify({
        'success': True,
        'farmer': farmer.to_dict(),
        'verification': ai_verification,
        'onboarding_recommendations': onboarding_recommendations
    }), 201

@farmer_bp.route('/list', methods=['GET'])
@jwt_required()
def get_farmers():
    filters = {
        'district': request.args.get('district'),
        'status': request.args.get('status'),
        'verification_status': request.args.get('verification_status'),
        'search': request.args.get('search')
    }
    
    farmers = farmer_service.get_farmers_list(filters)
    
    # AI farmer insights
    farmer_insights = ai_farmer.analyze_farmer_portfolio([f.to_dict() for f in farmers])
    
    return jsonify({
        'farmers': [farmer.to_dict() for farmer in farmers],
        'insights': farmer_insights
    })

@farmer_bp.route('/<int:farmer_id>', methods=['GET'])
@jwt_required()
def get_farmer_details(farmer_id):
    dashboard_data = farmer_service.get_farmer_dashboard_data(farmer_id)
    
    # AI farmer performance analysis
    performance_analysis = ai_farmer.analyze_farmer_performance(dashboard_data)
    
    # AI recommendations for farmer
    recommendations = ai_farmer.get_farmer_recommendations(dashboard_data)
    
    return jsonify({
        **dashboard_data,
        'performance_analysis': performance_analysis,
        'recommendations': recommendations
    })

@farmer_bp.route('/contracts', methods=['POST'])
@jwt_required()
def create_contract():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI contract optimization
    contract_optimization = ai_farmer.optimize_contract_terms(data)
    
    # AI risk assessment
    risk_assessment = ai_farmer.assess_contract_risk(data)
    
    if risk_assessment['risk_level'] == 'high':
        return jsonify({
            'success': False,
            'message': 'High risk contract detected',
            'risk_factors': risk_assessment['risk_factors'],
            'recommendations': risk_assessment['recommendations']
        }), 400
    
    contract = farmer_service.create_contract(user, data, contract_optimization)
    
    return jsonify({
        'success': True,
        'contract': contract.to_dict(),
        'optimization': contract_optimization,
        'risk_assessment': risk_assessment
    }), 201

@farmer_bp.route('/procurements', methods=['POST'])
@jwt_required()
def record_procurement():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI quality assessment
    quality_assessment = ai_farmer.assess_paddy_quality(data)
    
    # AI pricing recommendation
    pricing_recommendation = ai_farmer.recommend_procurement_price(data, quality_assessment)
    
    # Apply AI recommendations to data
    if pricing_recommendation.get('recommended_price'):
        data['base_price'] = pricing_recommendation['recommended_price']
    
    procurement = farmer_service.record_procurement(user, data, quality_assessment)
    
    # AI post-procurement analysis
    post_analysis = ai_farmer.analyze_procurement_impact(procurement.to_dict())
    
    return jsonify({
        'success': True,
        'procurement': procurement.to_dict(),
        'quality_assessment': quality_assessment,
        'pricing_recommendation': pricing_recommendation,
        'post_analysis': post_analysis
    }), 201

@farmer_bp.route('/payments', methods=['POST'])
@jwt_required()
def process_payment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI payment validation
    payment_validation = ai_farmer.validate_farmer_payment(data)
    
    # AI fraud detection
    fraud_check = ai_farmer.detect_payment_fraud(data)
    
    if fraud_check['is_suspicious']:
        return jsonify({
            'success': False,
            'message': 'Payment flagged for review',
            'fraud_indicators': fraud_check['indicators']
        }), 400
    
    payment = farmer_service.process_payment(user, data, payment_validation)
    
    # AI payment impact analysis
    impact_analysis = ai_farmer.analyze_payment_impact(payment.to_dict())
    
    return jsonify({
        'success': True,
        'payment': payment.to_dict(),
        'impact_analysis': impact_analysis
    }), 201

@farmer_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
def get_farmer_analytics():
    period = request.args.get('period', 'monthly')
    district = request.args.get('district')
    
    analytics = farmer_service.get_farmer_analytics(period, district)
    
    # AI enhanced analytics
    ai_analytics = ai_farmer.enhance_farmer_analytics(analytics)
    
    # AI trend analysis
    trend_analysis = ai_farmer.analyze_farmer_trends(analytics)
    
    # AI predictions
    predictions = ai_farmer.predict_farmer_behavior(analytics)
    
    return jsonify({
        'analytics': analytics,
        'ai_analytics': ai_analytics,
        'trend_analysis': trend_analysis,
        'predictions': predictions
    })

@farmer_bp.route('/seasonal-planning', methods=['POST'])
@jwt_required()
def create_seasonal_plan():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    
    # AI seasonal planning
    seasonal_plan = ai_farmer.generate_seasonal_plan(data)
    
    # AI crop recommendations
    crop_recommendations = ai_farmer.recommend_crops(data)
    
    # AI yield predictions
    yield_predictions = ai_farmer.predict_seasonal_yield(data)
    
    return jsonify({
        'seasonal_plan': seasonal_plan,
        'crop_recommendations': crop_recommendations,
        'yield_predictions': yield_predictions
    })

@farmer_bp.route('/quality-trends', methods=['GET'])
@jwt_required()
def get_quality_trends():
    farmer_id = request.args.get('farmer_id', type=int)
    period = request.args.get('period', 'yearly')
    
    quality_trends = farmer_service.get_quality_trends(farmer_id, period)
    
    # AI quality analysis
    quality_analysis = ai_farmer.analyze_quality_trends(quality_trends)
    
    # AI improvement recommendations
    improvement_recommendations = ai_farmer.recommend_quality_improvements(quality_trends)
    
    return jsonify({
        'quality_trends': quality_trends,
        'analysis': quality_analysis,
        'recommendations': improvement_recommendations
    })