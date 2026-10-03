"""Admin user list and access-matrix APIs."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from extensions import db
from models.tenant import TenantMembership
from models.user import User
from services.access_control import (
    ROLES,
    has_permission,
    matrix_payload,
    permissions_for,
    set_permission,
)
from services.tenant_context import current_tenant_id
from utils import current_user

users_admin_bp = Blueprint('users_admin', __name__)


def _admin_user():
    user = current_user()
    if not user or not has_permission(user, 'users'):
        return None
    return user


def _tenant_users():
    tid = current_tenant_id()
    if not tid:
        return []
    member_ids = [
        row.user_id for row in TenantMembership.query.filter_by(tenant_id=tid).all()
    ]
    if not member_ids:
        return []
    return User.query.filter(User.id.in_(member_ids)).order_by(User.username.asc()).all()


def _membership_role(user):
    tid = current_tenant_id()
    if not tid:
        return user.role
    row = TenantMembership.query.filter_by(user_id=user.id, tenant_id=tid).first()
    return row.role if row else user.role


def _user_row(user):
    role = _membership_role(user)
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': role,
        'is_active': bool(user.is_active),
        'permissions': permissions_for(user),
    }


@users_admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    if not _admin_user():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    users = _tenant_users()
    return jsonify({'success': True, 'users': [_user_row(item) for item in users]})


@users_admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    if not _admin_user():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    data = request.get_json() or {}
    username = str(data.get('username') or '').strip()
    password = data.get('password') or ''
    role = str(data.get('role') or 'operator').strip().lower()
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'}), 400
    if role not in ROLES:
        return jsonify({'success': False, 'message': 'Unknown role'}), 400
    if User.query.filter((User.username == username) | (User.email == username)).first():
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    user = User(
        username=username,
        email=data.get('email') or f'{username}@ricemill.com',
        first_name=data.get('first_name') or username,
        last_name=data.get('last_name') or '',
        role=role,
        is_active=True,
        is_verified=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    tid = current_tenant_id()
    if tid:
        db.session.add(TenantMembership(user_id=user.id, tenant_id=tid, role=role))
    db.session.commit()
    return jsonify({'success': True, 'user': _user_row(user)}), 201


@users_admin_bp.route('/users/<int:user_id>', methods=['PATCH'])
@jwt_required()
def update_user(user_id):
    actor = _admin_user()
    if not actor:
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    tid = current_tenant_id()
    membership = TenantMembership.query.filter_by(user_id=user_id, tenant_id=tid).first() if tid else None
    user = User.query.get(user_id) if membership else None
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    data = request.get_json() or {}
    if 'role' in data:
        role = str(data.get('role') or '').strip().lower()
        if role not in ROLES:
            return jsonify({'success': False, 'message': 'Unknown role'}), 400
        user.role = role
        membership.role = role
    if 'is_active' in data:
        active = bool(data.get('is_active'))
        if not active and user.id == actor.id:
            return jsonify({'success': False, 'message': 'You cannot deactivate your own account'}), 400
        user.is_active = active
    db.session.commit()
    return jsonify({'success': True, 'user': _user_row(user)})


@users_admin_bp.route('/access', methods=['GET'])
@jwt_required()
def get_access_matrix():
    if not _admin_user():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    return jsonify({'success': True, **matrix_payload()})


@users_admin_bp.route('/access', methods=['PUT'])
@jwt_required()
def save_access_matrix():
    if not _admin_user():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    data = request.get_json() or {}
    role = data.get('role')
    permission = data.get('permission')
    allowed = data.get('allowed')
    if role is None or permission is None or allowed is None:
        return jsonify({'success': False, 'message': 'role, permission, and allowed are required'}), 400
    row = set_permission(role, permission, allowed)
    if not row:
        return jsonify({'success': False, 'message': 'Unknown role or permission'}), 400
    return jsonify({'success': True, **matrix_payload()})
