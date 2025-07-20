from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.logistics import Vehicle, Driver, Shipment
from services.logistics_service import LogisticsService

logistics_bp = Blueprint('logistics', __name__)
logistics_service = LogisticsService()

@logistics_bp.route('/shipments', methods=['POST'])
@jwt_required()
def create_shipment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    shipment = logistics_service.create_shipment(user, data)
    
    return jsonify({
        'success': True,
        'shipment': {
            'id': shipment.id,
            'shipment_number': shipment.shipment_number,
            'status': shipment.status
        }
    }), 201

@logistics_bp.route('/shipments/<int:shipment_id>/assign', methods=['POST'])
@jwt_required()
def assign_shipment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    shipment = logistics_service.assign_vehicle_and_driver(
        shipment_id=data['shipment_id'],
        vehicle_id=data['vehicle_id'],
        driver_id=data['driver_id'],
        user=user
    )
    
    return jsonify({
        'success': True,
        'shipment': {
            'id': shipment.id,
            'status': shipment.status
        }
    })

@logistics_bp.route('/shipments/<int:shipment_id>/start', methods=['POST'])
@jwt_required()
def start_shipment():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    shipment = logistics_service.start_shipment(shipment_id, user)
    
    return jsonify({
        'success': True,
        'shipment': {
            'id': shipment.id,
            'status': shipment.status,
            'actual_pickup': shipment.actual_pickup.isoformat()
        }
    })

@logistics_bp.route('/shipments/<int:shipment_id>/complete', methods=['POST'])
@jwt_required()
def complete_delivery():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    data = request.get_json()
    shipment = logistics_service.complete_delivery(shipment_id, data, user)
    
    return jsonify({
        'success': True,
        'shipment': {
            'id': shipment.id,
            'status': shipment.status,
            'actual_delivery': shipment.actual_delivery.isoformat()
        }
    })

@logistics_bp.route('/track/<shipment_number>')
def track_shipment(shipment_number):
    tracking_info = logistics_service.track_shipment(shipment_number)
    return jsonify(tracking_info)

@logistics_bp.route('/fleet/status')
@jwt_required()
def get_fleet_status():
    status = logistics_service.get_fleet_status()
    return jsonify(status)

@logistics_bp.route('/vehicles', methods=['GET'])
@jwt_required()
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify({
        'vehicles': [
            {
                'id': v.id,
                'vehicle_number': v.vehicle_number,
                'vehicle_type': v.vehicle_type,
                'status': v.status,
                'load_capacity': v.load_capacity
            }
            for v in vehicles
        ]
    })

@logistics_bp.route('/drivers', methods=['GET'])
@jwt_required()
def get_drivers():
    drivers = Driver.query.all()
    return jsonify({
        'drivers': [
            {
                'id': d.id,
                'driver_name': d.driver_name,
                'license_number': d.license_number,
                'status': d.status,
                'rating': d.rating
            }
            for d in drivers
        ]
    })