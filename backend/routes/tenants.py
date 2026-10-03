"""Organization create / list / switch."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from services.access_control import permissions_for
from services.tenant_context import current_tenant
from services.tenant_service import create_tenant, switch_token, tenants_for_user
from utils import current_user

tenants_bp = Blueprint('tenants', __name__)


def _user_payload(user, tenant=None, role=None):
    payload = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': role or user.role,
        'permissions': permissions_for(user),
        'is_platform_admin': bool(getattr(user, 'is_platform_admin', False)),
        'preferences': user.get_preferences() if hasattr(user, 'get_preferences') else {},
    }
    if tenant is not None:
        payload['tenant'] = tenant.to_public() if hasattr(tenant, 'to_public') else tenant
    return payload


@tenants_bp.route('/tenants/mine', methods=['GET'])
@jwt_required()
def mine():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    rows = tenants_for_user(user)
    active = current_tenant()
    return jsonify({
        'success': True,
        'tenants': rows,
        'current': active.to_public() if active else (rows[0] if rows else None),
    })


@tenants_bp.route('/tenants/<tenant_id>/switch', methods=['POST'])
@jwt_required()
def switch(tenant_id):
    user = current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    result, error = switch_token(user, tenant_id)
    if error:
        return jsonify({'success': False, 'message': error}), 403
    from models.tenant import Tenant
    tenant = Tenant.query.get(result['tenant']['id'])
    return jsonify({
        'success': True,
        **result,
        'user': _user_payload(user, tenant, result.get('role')),
    })


@tenants_bp.route('/tenants', methods=['POST'])
def create():
    data = request.get_json() or {}
    user = None
    try:
        from flask_jwt_extended import verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user = current_user()
    except Exception:
        user = None

    name = str(data.get('name') or '').strip()
    slug = data.get('slug')
    if not name:
        return jsonify({'success': False, 'message': 'name is required'}), 400

    owner = None
    owner_payload = None
    if user and (getattr(user, 'is_platform_admin', False) or data.get('as_owner')):
        owner = user
    elif user and getattr(user, 'is_platform_admin', False) and data.get('owner'):
        owner_payload = data.get('owner')
    elif not user:
        owner_payload = data.get('owner') or {
            'username': data.get('username'),
            'password': data.get('password'),
            'email': data.get('email'),
            'first_name': data.get('first_name'),
        }
    else:
        owner = user

    tenant, error = create_tenant(name, slug=slug, owner=owner, owner_payload=owner_payload)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'tenant': tenant.to_public()}), 201
