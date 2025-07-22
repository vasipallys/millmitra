from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Farmer, FarmerContract
from extensions import db
from datetime import datetime
import json

farmer_bp = Blueprint('farmer', __name__)

# Import services with fallback
try:
    from services.farmer_service import FarmerService
    from services.ai_farmer_service import AIFarmerService
    farmer_service = FarmerService()
    ai_farmer = AIFarmerService()
except ImportError:
    farmer_service = None
    ai_farmer = None

@farmer_bp.route('/register', methods=['POST'])
@jwt_required()
def register_farmer():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'phone', 'village', 'district', 'state']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Check for duplicate phone number
        existing_farmer = Farmer.query.filter_by(phone=data['phone']).first()
        if existing_farmer:
            return jsonify({
                'success': False,
                'message': 'Farmer with this phone number already exists'
            }), 400

        # Generate farmer code
        district_code = data['district'][:3].upper()
        farmer_count = Farmer.query.filter_by(district=data['district']).count()
        farmer_code = f"{district_code}{farmer_count + 1:04d}"

        # Create farmer
        farmer = Farmer(
            farmer_code=farmer_code,
            name=data['name'],
            phone=data['phone'],
            email=data.get('email'),
            aadhar_number=data.get('aadhar_number'),
            pan_number=data.get('pan_number'),
            bank_account=data.get('bank_account_number'),
            ifsc_code=data.get('bank_ifsc'),
            bank_name=data.get('bank_name'),
            branch_name=data.get('branch_name'),
            village=data['village'],
            district=data['district'],
            state=data['state'],
            pincode=data.get('pincode'),
            land_area=data.get('total_land_area', 0.0),
            farming_experience=data.get('farming_experience', 0),
            farming_type=data.get('farming_type', 'conventional'),
            irrigation_type=data.get('irrigation_type', 'bore_well'),
            created_by=user.id,
            created_at=datetime.utcnow()
        )

        db.session.add(farmer)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Farmer registered successfully',
            'farmer': {
                'id': farmer.id,
                'farmer_code': farmer.farmer_code,
                'name': farmer.name,
                'phone': farmer.phone,
                'village': farmer.village,
                'district': farmer.district,
                'state': farmer.state
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error registering farmer: {str(e)}'
        }), 500

@farmer_bp.route('/list', methods=['GET'])
@jwt_required()
def get_farmers():
    # Simplified implementation - return mock data for now
    farmers = Farmer.query.all()

    return jsonify({
        'farmers': [farmer.to_dict() for farmer in farmers],
        'insights': {
            'total_farmers': len(farmers),
            'active_farmers': len([f for f in farmers if f.is_active]),
            'message': 'Farmer data loaded successfully'
        }
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
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        data = request.get_json()

        # Validate required fields
        required_fields = ['farmer_id', 'crop_type', 'quantity_committed', 'base_price', 'contract_start_date', 'contract_end_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Verify farmer exists
        farmer = Farmer.query.get(data['farmer_id'])
        if not farmer:
            return jsonify({
                'success': False,
                'message': 'Farmer not found'
            }), 404

        # Generate contract number
        contract_count = FarmerContract.query.count()
        contract_number = f"CON{contract_count + 1:06d}"

        # Create contract
        contract = FarmerContract(
            contract_number=contract_number,
            farmer_id=data['farmer_id'],
            contract_type=data.get('contract_type', 'seasonal'),
            variety=data.get('variety', data['crop_type']),
            quantity_committed=float(data['quantity_committed']),
            price_per_kg=float(data['base_price']),
            start_date=datetime.strptime(data['contract_start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(data['contract_end_date'], '%Y-%m-%d'),
            quality_specifications=json.dumps(data.get('quality_specifications', {})),
            created_by=user.id,
            created_at=datetime.utcnow()
        )

        db.session.add(contract)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Contract created successfully',
            'contract': {
                'id': contract.id,
                'contract_number': contract.contract_number,
                'farmer_name': farmer.name,
                'variety': contract.variety,
                'quantity_committed': contract.quantity_committed,
                'price_per_kg': contract.price_per_kg,
                'start_date': contract.start_date.isoformat(),
                'end_date': contract.end_date.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error creating contract: {str(e)}'
        }), 500

@farmer_bp.route('/procurements', methods=['POST'])
@jwt_required()
def record_procurement():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        data = request.get_json()

        # Validate required fields
        required_fields = ['farmer_id', 'crop_type', 'quantity', 'price_per_unit', 'procurement_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400

        # Verify farmer exists
        farmer = Farmer.query.get(data['farmer_id'])
        if not farmer:
            return jsonify({
                'success': False,
                'message': 'Farmer not found'
            }), 404

        # Import PaddyStock model
        from models.inventory import PaddyStock

        # Generate stock ID
        stock_count = PaddyStock.query.count()
        stock_id = f"STOCK{stock_count + 1:06d}"

        # Calculate total amount
        quantity = float(data['quantity'])
        price_per_unit = float(data['price_per_unit'])
        total_amount = quantity * price_per_unit

        # Create procurement record
        procurement = PaddyStock(
            stock_id=stock_id,
            farmer_id=data['farmer_id'],
            variety=data['crop_type'],
            quantity=quantity,
            purchase_price=price_per_unit,
            total_amount=total_amount,
            moisture_content=float(data.get('moisture_content', 0)),
            purchase_date=datetime.strptime(data['procurement_date'], '%Y-%m-%d'),
            warehouse_id=data.get('storage_location', 'WH001'),
            quality_grade=data.get('quality_grade', 'A'),
            remaining_quantity=quantity,
            created_by=user.id,
            created_at=datetime.utcnow()
        )

        db.session.add(procurement)

        # Update farmer's total procurement
        farmer.total_quantity_supplied = (farmer.total_quantity_supplied or 0) + quantity
        farmer.total_transactions = (farmer.total_transactions or 0) + 1
        farmer.last_transaction_date = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Procurement recorded successfully',
            'procurement': {
                'id': procurement.id,
                'stock_id': procurement.stock_id,
                'farmer_name': farmer.name,
                'variety': procurement.variety,
                'quantity': procurement.quantity,
                'purchase_price': procurement.purchase_price,
                'total_amount': procurement.total_amount,
                'moisture_content': procurement.moisture_content,
                'purchase_date': procurement.purchase_date.isoformat()
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error recording procurement: {str(e)}'
        }), 500

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
    # Simplified implementation - return mock analytics data
    period = request.args.get('period', 'monthly')
    district = request.args.get('district')

    farmers = Farmer.query.all()

    return jsonify({
        'analytics': {
            'total_farmers': len(farmers),
            'period': period,
            'district': district or 'All Districts',
            'summary': 'Analytics data loaded successfully'
        },
        'ai_analytics': {
            'insights': ['Farmer engagement is stable', 'Quality metrics improving'],
            'recommendations': ['Focus on training programs', 'Expand procurement network']
        },
        'trend_analysis': {
            'direction': 'positive',
            'growth_rate': '5.2%'
        },
        'predictions': {
            'next_month_farmers': len(farmers) + 5,
            'confidence': 0.85
        }
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