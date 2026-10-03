from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Farmer, FarmerContract, Payment
from models.farmer_edit_request import FarmerEditRequest
from extensions import db
from services.tenant_scope import tq, t_get, t_get_or_404
from datetime import datetime, timedelta
from utils import current_user
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

@farmer_bp.route('/extract-id', methods=['POST'])
@jwt_required()
def extract_farmer_id():
    """Fill farmer form fields from an ID photo. Does not create a farmer or store the image."""
    user = current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    upload = request.files.get('image') or request.files.get('file')
    if upload is None:
        return jsonify({
            'success': False,
            'fields': {},
            'extracted': {},
            'notes': 'Choose a JPG, PNG, or WebP image.',
            'message': 'Choose a JPG, PNG, or WebP image.',
        }), 400
    from services.id_extract_service import (
        MAX_IMAGE_BYTES,
        extract_id_document,
        filename_allowed,
    )
    if not filename_allowed(upload.filename, upload.mimetype):
        return jsonify({
            'success': False,
            'fields': {},
            'extracted': {},
            'notes': 'Use a JPG, PNG, or WebP image.',
            'message': 'Use a JPG, PNG, or WebP image.',
        }), 400
    payload = upload.read(MAX_IMAGE_BYTES + 1)
    result = extract_id_document(payload, filename=upload.filename or '')
    status = 200 if result.get('success', True) else 400
    return jsonify(result), status


@farmer_bp.route('/register', methods=['POST'])
@jwt_required()
def register_farmer():
    try:
        user = current_user()
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 401
        user_id = user.id

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
        existing_farmer = tq(Farmer).filter_by(phone=data['phone']).first()
        if existing_farmer:
            return jsonify({
                'success': False,
                'message': 'Farmer with this phone number already exists'
            }), 400

        # Generate farmer code
        district_code = data['district'][:3].upper()
        farmer_count = tq(Farmer).filter_by(district=data['district']).count()
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
        from services.notification_service import farmer_registered
        farmer_registered(farmer)

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
    farmers = tq(Farmer).all()

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
    farmer = t_get_or_404(Farmer, farmer_id)
    contracts = []
    procurements = []
    payments = []
    try:
        contracts = tq(FarmerContract).filter_by(farmer_id=farmer_id).all()
    except Exception:
        db.session.rollback()
    try:
        from models.inventory import PaddyStock
        procurements = tq(PaddyStock).filter_by(farmer_id=farmer_id).order_by(
            PaddyStock.purchase_date.desc()
        ).limit(10).all()
    except Exception:
        db.session.rollback()
    try:
        payments = tq(Payment).filter_by(farmer_id=farmer_id).all()
    except Exception:
        db.session.rollback()

    return jsonify({
        'farmer': farmer.to_dict(),
        'active_contracts': [c.to_dict() for c in contracts if getattr(c, 'status', None) == 'active'],
        'recent_procurements': [
            {
                'id': p.id,
                'variety': p.variety,
                'quantity': p.quantity,
                'total_amount': p.total_amount,
                'purchase_date': p.purchase_date.isoformat() if p.purchase_date else None
            } for p in procurements
        ],
        'payment_summary': {
            'total_payments': sum(getattr(p, 'amount', 0) or 0 for p in payments),
            'pending_payments': farmer.outstanding_amount or 0
        },
        'performance_analysis': None,
        'recommendations': None
    })

@farmer_bp.route('/<int:farmer_id>', methods=['PUT'])
@jwt_required()
def update_farmer(farmer_id):
    """Submit farmer information update for verification"""
    try:
        user = current_user()
        user_id = user.id if user else None

        data = request.get_json()
        reason = data.pop('edit_reason', 'Information update')

        # Get farmer
        farmer = t_get_or_404(Farmer, farmer_id)

        # Get current farmer data
        original_data = farmer.to_dict()

        # Prepare proposed changes (only include fields that are being changed)
        proposed_changes = {}
        for key, value in data.items():
            if key in ['name', 'phone', 'email', 'village', 'district', 'state', 'pincode', 'address',
                      'aadhar_number', 'pan_number', 'land_area', 'farming_experience', 'farming_type',
                      'irrigation_type', 'bank_account', 'ifsc_code', 'bank_name', 'branch_name',
                      'payment_terms', 'credit_limit', 'is_verified', 'verification_date']:
                # Only include if value is different from current
                current_value = getattr(farmer, key, None)
                if str(current_value) != str(value):
                    proposed_changes[key] = value

        if not proposed_changes:
            return jsonify({
                'success': False,
                'message': 'No changes detected'
            }), 400

        # Create edit request
        edit_request = FarmerEditRequest.create_edit_request(
            farmer_id=farmer_id,
            requested_by=user_id,
            original_data=original_data,
            proposed_changes=proposed_changes,
            reason=reason
        )

        db.session.add(edit_request)
        db.session.commit()

        # If auto-approved, apply changes immediately
        if edit_request.auto_approved:
            apply_farmer_changes(farmer, proposed_changes)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Changes applied successfully (auto-approved)',
                'farmer': farmer.to_dict(),
                'edit_request': edit_request.to_dict(),
                'auto_approved': True
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Edit request submitted for approval',
                'edit_request': edit_request.to_dict(),
                'requires_approval': True,
                'pending_approval': True
            })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error submitting edit request: {str(e)}'
        }), 500

def apply_farmer_changes(farmer, changes):
    """Apply approved changes to farmer"""
    for key, value in changes.items():
        if hasattr(farmer, key):
            # Handle numeric fields that should be None if empty
            if key in ['land_area', 'credit_limit']:
                setattr(farmer, key, float(value) if value and str(value).strip() else None)
            elif key in ['farming_experience']:
                setattr(farmer, key, int(value) if value and str(value).strip() else None)
            else:
                # For string fields, set to None if empty string
                setattr(farmer, key, value if value and str(value).strip() else None)
    farmer.updated_at = datetime.utcnow()

@farmer_bp.route('/edit-requests', methods=['GET'])
@jwt_required()
def get_edit_requests():
    """Get farmer edit requests"""
    try:
        status = request.args.get('status', 'pending')
        farmer_id = request.args.get('farmer_id', type=int)

        if farmer_id:
            requests = FarmerEditRequest.get_requests_by_farmer(farmer_id)
        elif status == 'all':
            requests = tq(FarmerEditRequest).order_by(FarmerEditRequest.created_at.desc()).all()
        else:
            requests = FarmerEditRequest.get_requests_by_status(status)

        return jsonify({
            'success': True,
            'edit_requests': [req.to_dict() for req in requests],
            'total': len(requests)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching edit requests: {str(e)}'
        }), 500

@farmer_bp.route('/edit-requests/<int:request_id>/approve', methods=['POST'])
@jwt_required()
def approve_edit_request(request_id):
    """Approve farmer edit request"""
    try:
        # Get authenticated user from JWT
        user = current_user()
        user_id = user.id if user else None if user_id else None

        data = request.get_json()
        comments = data.get('comments', '')

        edit_request = t_get_or_404(FarmerEditRequest, request_id)

        if edit_request.status != 'pending':
            return jsonify({
                'success': False,
                'message': 'Edit request is not pending'
            }), 400

        # Get farmer and apply changes
        farmer = t_get(Farmer, edit_request.farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'message': 'Farmer not found'
            }), 404

        # Apply the approved changes
        proposed_changes = json.loads(edit_request.proposed_changes)
        apply_farmer_changes(farmer, proposed_changes)

        # Update edit request status
        edit_request.approve(user_id, comments)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Edit request approved and changes applied',
            'edit_request': edit_request.to_dict(),
            'farmer': farmer.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error approving edit request {request_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error approving edit request: {str(e)}',
            'error_details': str(e)
        }), 500

@farmer_bp.route('/edit-requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_edit_request(request_id):
    """Reject farmer edit request"""
    try:
        # Get authenticated user from JWT
        user = current_user()
        user_id = user.id if user else None if user_id else None

        data = request.get_json()
        comments = data.get('comments', '')

        if not comments:
            return jsonify({
                'success': False,
                'message': 'Rejection reason is required'
            }), 400

        edit_request = t_get_or_404(FarmerEditRequest, request_id)

        if edit_request.status != 'pending':
            return jsonify({
                'success': False,
                'message': 'Edit request is not pending'
            }), 400

        # Update edit request status
        edit_request.reject(user_id, comments)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Edit request rejected',
            'edit_request': edit_request.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error rejecting edit request {request_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error rejecting edit request: {str(e)}',
            'error_details': str(e)
        }), 500

@farmer_bp.route('/edit-requests/create-sample', methods=['POST'])
@jwt_required()
def create_sample_edit_requests():
    return jsonify({
        'success': False,
        'message': 'Sample edit-request seed is disabled. Create a real edit from Farmers.',
    }), 410

@farmer_bp.route('/contracts', methods=['GET'])
@jwt_required()
def get_contracts():
    """Get farmer contracts with optional filtering"""
    try:
        farmer_id = request.args.get('farmer_id')
        status = request.args.get('status', 'active')

        query = tq(FarmerContract)

        if farmer_id:
            query = query.filter_by(farmer_id=farmer_id)

        # Only filter by status if it's not 'all'
        if status and status != 'all':
            query = query.filter_by(status=status)

        contracts = query.all()

        # Format contract data with farmer names and field mapping
        contract_list = []
        for contract in contracts:
            contract_dict = contract.to_dict()

            # Get farmer name
            farmer = t_get(Farmer, contract.farmer_id)
            contract_dict['farmer_name'] = farmer.name if farmer else 'Unknown'

            # Map fields for frontend compatibility
            contract_dict['crop_type'] = contract_dict.get('variety', 'Rice')  # Map variety to crop_type
            contract_dict['season'] = contract_dict.get('contract_type', 'Kharif')  # Map contract_type to season
            contract_dict['base_price'] = contract_dict.get('price_per_kg', 0)  # Map price_per_kg to base_price
            contract_dict['contract_start_date'] = contract_dict.get('start_date')  # Map start_date
            contract_dict['contract_end_date'] = contract_dict.get('end_date')  # Map end_date

            # Add season mapping based on contract dates if available
            if contract_dict.get('start_date'):
                try:
                    start_date = datetime.fromisoformat(contract_dict['start_date'].replace('Z', '+00:00'))
                    month = start_date.month
                    if month in [6, 7, 8, 9, 10]:  # June to October
                        contract_dict['season'] = 'Kharif'
                    elif month in [11, 12, 1, 2, 3]:  # November to March
                        contract_dict['season'] = 'Rabi'
                    else:  # April to May
                        contract_dict['season'] = 'Summer'
                except:
                    contract_dict['season'] = contract_dict.get('contract_type', 'Kharif')

            contract_list.append(contract_dict)

        return jsonify({
            'success': True,
            'contracts': contract_list,
            'total': len(contract_list)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching contracts: {str(e)}'
        }), 500

@farmer_bp.route('/contracts/<int:contract_id>', methods=['PUT'])
@jwt_required()
def update_contract(contract_id):
    """Update contract information"""
    try:
        user = current_user()
        user_id = user.id if user else None

        data = request.get_json()

        # Get contract
        contract = t_get_or_404(FarmerContract, contract_id)

        # Update fields if provided
        if 'quantity_committed' in data:
            contract.quantity_committed = float(data['quantity_committed']) if data['quantity_committed'] else None
        if 'base_price' in data or 'price_per_kg' in data:
            contract.price_per_kg = float(data.get('price_per_kg', data.get('base_price'))) if data.get('price_per_kg', data.get('base_price')) else None
        if 'advance_amount' in data:
            contract.advance_amount = float(data['advance_amount']) if data['advance_amount'] else None
        if 'status' in data:
            contract.status = data['status']
        if 'payment_terms' in data:
            contract.payment_terms = data['payment_terms']
        if 'variety' in data or 'crop_type' in data:
            contract.variety = data.get('variety') or data.get('crop_type')

        contract.updated_at = datetime.utcnow()

        db.session.commit()

        # Get farmer name for response
        farmer = t_get(Farmer, contract.farmer_id)
        contract_dict = contract.to_dict()
        contract_dict['farmer_name'] = farmer.name if farmer else 'Unknown'

        return jsonify({
            'success': True,
            'message': 'Contract updated successfully',
            'contract': contract_dict
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating contract: {str(e)}'
        }), 500

@farmer_bp.route('/contracts', methods=['POST'])
@jwt_required()
def create_contract():
    try:
        user = current_user()
        user_id = user.id if user else None

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
        farmer = t_get(Farmer, data['farmer_id'])
        if not farmer:
            return jsonify({
                'success': False,
                'message': 'Farmer not found'
            }), 404

        # Generate contract number
        contract_count = tq(FarmerContract).count()
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

@farmer_bp.route('/procurements', methods=['GET'])
@jwt_required()
def get_procurements():
    """Get procurement records with optional filtering"""
    try:
        farmer_id = request.args.get('farmer_id')
        limit = request.args.get('limit', 50, type=int)
        sort = request.args.get('sort', 'recent')

        # Import PaddyStock model
        from models.inventory import PaddyStock

        query = tq(PaddyStock)

        if farmer_id:
            query = query.filter_by(farmer_id=farmer_id)

        # Sort by date
        if sort == 'recent':
            query = query.order_by(PaddyStock.purchase_date.desc())
        else:
            query = query.order_by(PaddyStock.purchase_date.asc())

        # Apply limit
        procurements = query.limit(limit).all()

        # Format procurement data
        procurement_list = []
        for procurement in procurements:
            # Get farmer name
            farmer = t_get(Farmer, procurement.farmer_id)
            farmer_name = farmer.name if farmer else 'Unknown'

            procurement_list.append({
                'id': procurement.id,
                'farmer_id': procurement.farmer_id,
                'farmer_name': farmer_name,
                'variety': procurement.variety,
                'quantity': procurement.quantity,
                'price_per_unit': procurement.purchase_price,
                'total_amount': procurement.total_amount,
                'procurement_date': procurement.purchase_date.isoformat() if procurement.purchase_date else None,
                'quality_grade': procurement.quality_grade,
                'moisture_content': procurement.moisture_content,
                'status': 'Completed'  # Default status
            })

        return jsonify({
            'success': True,
            'procurements': procurement_list,
            'total': len(procurement_list)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching procurements: {str(e)}'
        }), 500

@farmer_bp.route('/procurements', methods=['POST'])
@jwt_required()
def record_procurement():
    try:
        user = current_user()
        user_id = user.id if user else None

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
        farmer = t_get(Farmer, data['farmer_id'])
        if not farmer:
            return jsonify({
                'success': False,
                'message': 'Farmer not found'
            }), 404

        # Import PaddyStock model
        from models.inventory import PaddyStock

        # Generate stock ID
        stock_count = tq(PaddyStock).count()
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
    from utils import current_user as _current_user
    user = _current_user()
    data = request.get_json() or {}
    amount = float(data.get('amount', 0) or 0)
    if amount <= 0 or not data.get('farmer_id'):
        return jsonify({'success': False, 'message': 'farmer_id and amount are required'}), 400

    payment = Payment(
        payment_id=f'FPAY{datetime.utcnow().strftime("%Y%m%d")}{datetime.utcnow().strftime("%H%M%S")}',
        payment_type='paid',
        payment_category='farmer_payment',
        farmer_id=data['farmer_id'],
        amount=amount,
        payment_method=data.get('payment_method', 'cash'),
        reference_number=data.get('reference_number'),
        payment_date=datetime.utcnow(),
        status='cleared',
        description=data.get('notes'),
        created_by=user.id if user else None
    )
    db.session.add(payment)
    farmer = t_get(Farmer, data['farmer_id'])
    if farmer:
        farmer.outstanding_amount = max(0, (farmer.outstanding_amount or 0) - amount)
    db.session.commit()
    return jsonify({
        'success': True,
        'payment': payment.to_dict()
    }), 201

@farmer_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
def get_farmer_analytics():
    """Get comprehensive farmer analytics overview"""
    try:
        # Validate and sanitize parameters
        period = request.args.get('period', 'monthly')
        district = request.args.get('district')

        # Handle case where period might be an object string
        if period and ('[object' in str(period).lower() or 'object' in str(period).lower()):
            period = 'monthly'

        # Validate period parameter
        valid_periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        if period not in valid_periods:
            period = 'monthly'

        print(f"[DEBUG] Analytics request - Period: {period}, District: {district}")

        # Get basic counts with error handling
        try:
            total_farmers = tq(Farmer).count()
            active_farmers = tq(Farmer).filter_by(is_active=True).count()
        except Exception as e:
            print(f"[WARN] Error getting farmer counts: {e}")
            total_farmers = 0
            active_farmers = 0

        # Get contract analytics with error handling
        try:
            active_contracts = tq(FarmerContract).filter_by(status='active').count()
            total_contracts = tq(FarmerContract).count()
        except Exception as e:
            print(f"[WARN] Error getting contract counts: {e}")
            active_contracts = 0
            total_contracts = 0

        # Get procurement analytics with error handling
        total_procurement_qty = 0
        total_procurement_records = 0
        total_procurement_value = 0
        try:
            # Try to import PaddyStock model
            from models.inventory import PaddyStock
            total_procurement_qty = tq(PaddyStock).with_entities(db.func.sum(PaddyStock.quantity)).scalar() or 0
            total_procurement_records = tq(PaddyStock).count()
            total_procurement_value = tq(PaddyStock).with_entities(
                db.func.sum(PaddyStock.quantity * PaddyStock.purchase_price)
            ).scalar() or 0
        except ImportError:
            print("[WARN] PaddyStock model not found, using default values")
        except Exception as e:
            print(f"[WARN] Error getting procurement data: {e}")

        # Get payment analytics with error handling
        total_payments = 0
        payment_records = 0
        try:
            total_payments = db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.payment_category == 'farmer_payment',
                Payment.status == 'cleared'
            ).scalar() or 0
            payment_records = tq(Payment).filter(Payment.payment_category == 'farmer_payment').count()
        except Exception as e:
            print(f"[WARN] Error getting payment data: {e}")

        # Calculate average metrics with error handling
        avg_land_area = 0
        try:
            avg_land_area = db.session.query(db.func.avg(Farmer.land_area)).scalar() or 0
        except Exception as e:
            print(f"[WARN] Error calculating average land area: {e}")

        avg_quality_rating = 0
        try:
            avg_quality_rating = db.session.query(db.func.avg(Farmer.quality_rating)).scalar() or 0
        except Exception as e:
            print(f"[WARN] Error calculating average quality rating: {e}")

        # Get recent activity (last 30 days) with error handling
        recent_farmers = 0
        recent_contracts = 0
        recent_procurements = 0
        try:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_farmers = tq(Farmer).filter(Farmer.created_at >= thirty_days_ago).count()
            recent_contracts = tq(FarmerContract).filter(FarmerContract.created_at >= thirty_days_ago).count()

            # Only try to get recent procurements if PaddyStock is available
            try:
                from models.inventory import PaddyStock
                recent_procurements = tq(PaddyStock).filter(PaddyStock.purchase_date >= thirty_days_ago).count()
            except ImportError:
                recent_procurements = 0
        except Exception as e:
            print(f"[WARN] Error calculating recent activity: {e}")

        print(f"[SUCCESS] Analytics calculated successfully - Farmers: {total_farmers}, Contracts: {active_contracts}")

        return jsonify({
            'success': True,
            'analytics': {
                'total_farmers': total_farmers,
                'active_farmers': active_farmers,
                'active_contracts': active_contracts,
                'total_contracts': total_contracts,
                'total_procurement': total_procurement_qty,
                'total_procurement_records': total_procurement_records,
                'total_procurement_value': total_procurement_value,
                'total_payments': total_payments,
                'payment_records': payment_records,
                'avg_land_area': round(avg_land_area, 2),
                'avg_quality_rating': round(avg_quality_rating, 2),
                'period': period,
                'district': district or 'All Districts'
            },
            'recent_activity': {
                'new_farmers': recent_farmers,
                'new_contracts': recent_contracts,
                'new_procurements': recent_procurements,
                'period': '30 days'
            },
            'ai_analytics': {
                'insights': [
                    f'Total of {total_farmers} farmers registered',
                    f'{active_contracts} active contracts in progress',
                    f'{total_procurement_qty:.0f} kg total procurement recorded',
                    'Quality metrics showing positive trends'
                ],
                'recommendations': [
                    'Focus on farmer training programs',
                    'Expand procurement network',
                    'Improve contract completion rates',
                    'Enhance quality assessment processes'
                ]
            },
            'trend_analysis': {
                'direction': 'positive' if recent_farmers > 0 else 'stable',
                'growth_rate': f'{(recent_farmers / max(total_farmers, 1) * 100):.1f}%',
                'procurement_trend': 'increasing' if recent_procurements > 0 else 'stable'
            },
            'predictions': {
                'next_month_farmers': total_farmers + max(recent_farmers, 2),
                'next_month_procurement': total_procurement_qty * 1.1,
                'confidence': 0.85
            }
        })

    except Exception as e:
        print(f"[ERROR] Analytics endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error fetching analytics: {str(e)}',
            'analytics': {
                'total_farmers': 0,
                'active_farmers': 0,
                'active_contracts': 0,
                'total_procurement': 0,
                'total_payments': 0
            }
        }), 500

@farmer_bp.route('/analytics/test', methods=['GET'])
@jwt_required()
def test_analytics():
    """Simple test endpoint for analytics"""
    return jsonify({
        'success': True,
        'message': 'Analytics endpoint is working',
        'timestamp': datetime.utcnow().isoformat()
    })

@farmer_bp.route('/seasonal-planning', methods=['POST'])
@jwt_required()
def create_seasonal_plan():
    user = current_user()
    user_id = user.id if user else None
    
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
    if not farmer_service:
        return jsonify({
            'error': 'Farmer service not available'
        }), 503

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

@farmer_bp.route('/<int:farmer_id>/verify', methods=['PUT'])
@jwt_required()
def verify_farmer(farmer_id):
    """Verify farmer status (admin action)"""
    try:
        user = current_user()
        user_id = user.id if user else None
        
        # Check if user has permission to verify farmers
        if not user or user.role not in ['admin', 'manager']:
            return jsonify({
                'success': False,
                'message': 'Insufficient permissions to verify farmers'
            }), 403
        
        data = request.get_json()
        farmer = t_get_or_404(Farmer, farmer_id)
        
        # Update verification status
        farmer.is_verified = data.get('is_verified', True)
        if data.get('verification_date'):
            farmer.verification_date = datetime.fromisoformat(data['verification_date'].replace('Z', '+00:00'))
        else:
            farmer.verification_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Farmer verification status updated successfully',
            'farmer': farmer.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating farmer verification: {str(e)}'
        }), 500