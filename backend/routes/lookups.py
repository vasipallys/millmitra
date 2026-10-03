"""Lookup option APIs. Active list is readable by any logged-in user."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from models.lookup import LookupOption
from services.access_control import has_permission
from services import lookup_service
from services.tenant_scope import t_get
from utils import current_user

lookups_bp = Blueprint('lookups', __name__)


def _require_lookups_admin():
    user = current_user()
    if not user or not has_permission(user, 'lookups'):
        return None
    return user


@lookups_bp.route('/lookups', methods=['GET'])
@jwt_required()
def list_active():
    group = (request.args.get('group') or '').strip() or None
    rows = lookup_service.list_active(group)
    return jsonify({
        'success': True,
        'group': group,
        'options': [row.to_public() for row in rows],
    })


@lookups_bp.route('/lookups/admin', methods=['GET'])
@jwt_required()
def list_admin():
    if not _require_lookups_admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    group = (request.args.get('group') or '').strip() or None
    rows = lookup_service.list_admin(group)
    groups = []
    for key in lookup_service.GROUP_KEYS:
        groups.append({
            'key': key,
            'locked': lookup_service.group_is_locked(key),
        })
    return jsonify({
        'success': True,
        'groups': groups,
        'options': [row.to_admin() for row in rows],
    })


@lookups_bp.route('/lookups', methods=['POST'])
@jwt_required()
def create_lookup():
    if not _require_lookups_admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    row, error = lookup_service.create_option(request.get_json() or {})
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'option': row.to_admin()}), 201


@lookups_bp.route('/lookups/<int:option_id>', methods=['PUT'])
@jwt_required()
def update_lookup(option_id):
    if not _require_lookups_admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    row = t_get(LookupOption, option_id)
    if not row:
        return jsonify({'success': False, 'message': 'Option not found'}), 404
    updated, error = lookup_service.update_option(row, request.get_json() or {})
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'option': updated.to_admin()})


@lookups_bp.route('/lookups/<int:option_id>/activate', methods=['POST'])
@jwt_required()
def activate_lookup(option_id):
    if not _require_lookups_admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    row = t_get(LookupOption, option_id)
    if not row:
        return jsonify({'success': False, 'message': 'Option not found'}), 404
    updated, error = lookup_service.set_active(row, True)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'option': updated.to_admin()})


@lookups_bp.route('/lookups/<int:option_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_lookup(option_id):
    if not _require_lookups_admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    row = t_get(LookupOption, option_id)
    if not row:
        return jsonify({'success': False, 'message': 'Option not found'}), 404
    updated, error = lookup_service.set_active(row, False)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    return jsonify({'success': True, 'option': updated.to_admin()})
