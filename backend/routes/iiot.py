"""IIoT devices, ingest, manual entry, and discrepancy resolution."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from models.iiot import Discrepancy
from services import iiot_service
from services.access_control import has_permission
from services.tenant_scope import t_get
from utils import current_user

iiot_bp = Blueprint('iiot', __name__)


def _user_with(permission):
    user = current_user()
    if not user or not has_permission(user, permission):
        return None
    return user


@iiot_bp.route('/devices', methods=['GET'])
@jwt_required()
def list_devices():
    if not _user_with('iiot'):
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    return jsonify({
        'success': True,
        'devices': [row.to_dict(include_token=False) for row in iiot_service.list_devices()],
    })


@iiot_bp.route('/devices', methods=['POST'])
@jwt_required()
def create_device():
    if not _user_with('iiot'):
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    row, error = iiot_service.create_device(request.get_json() or {})
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'device': row.to_dict(include_token=True)}), 201


@iiot_bp.route('/readings', methods=['GET'])
@jwt_required()
def list_readings():
    if not _user_with('iiot'):
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    device_id = request.args.get('device_id')
    rows = iiot_service.latest_readings(device_id=device_id)
    return jsonify({'success': True, 'readings': [row.to_dict() for row in rows]})


@iiot_bp.route('/ingest', methods=['POST'])
def ingest():
    payload = request.get_json(silent=True) or {}
    token = (
        request.headers.get('X-Device-Token')
        or request.headers.get('X-Iot-Token')
        or payload.get('token')
        or payload.get('device_token')
    )
    device = iiot_service.device_by_token(token)
    if device is None:
        return jsonify({'success': False, 'message': 'Invalid device token'}), 401
    row, error = iiot_service.ingest(
        device,
        payload.get('metric'),
        payload.get('value'),
        source='sensor',
        reason=None,
        tags=payload.get('tags') if isinstance(payload.get('tags'), dict) else {},
    )
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'reading': row.to_dict()}), 201


@iiot_bp.route('/manual', methods=['POST'])
@jwt_required()
def manual():
    user = _user_with('iiot')
    if not user:
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    payload = request.get_json() or {}
    reason = (payload.get('reason') or '').strip()
    if not reason:
        return jsonify({'success': False, 'message': 'reason is required'}), 400
    device_id = (payload.get('device_id') or '').strip()
    device = next((row for row in iiot_service.list_devices() if row.device_id == device_id), None)
    if device is None:
        return jsonify({'success': False, 'message': 'Device not found'}), 404
    row, error = iiot_service.ingest(
        device,
        payload.get('metric'),
        payload.get('value'),
        source='manual',
        reason=reason,
        actor_id=user.id,
    )
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'reading': row.to_dict()}), 201


@iiot_bp.route('/discrepancies', methods=['GET'])
@jwt_required()
def list_discrepancies():
    if not _user_with('iiot'):
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    status = request.args.get('status')
    rows = iiot_service.list_discrepancies(status=status)
    return jsonify({'success': True, 'discrepancies': [row.to_dict() for row in rows]})


@iiot_bp.route('/discrepancies/<int:item_id>/resolve', methods=['POST'])
@jwt_required()
def resolve(item_id):
    user = _user_with('reconciliation')
    if not user:
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    row = t_get(Discrepancy, item_id)
    if row is None:
        return jsonify({'success': False, 'message': 'Discrepancy not found'}), 404
    payload = request.get_json() or {}
    updated = iiot_service.resolve_discrepancy(row, user, payload.get('resolution') or '')
    return jsonify({'success': True, 'discrepancy': updated.to_dict()})
