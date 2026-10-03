"""Role permission matrix. Stored rows override defaults."""
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request
from extensions import db
from models.user import RolePermission
from utils import current_user

PERMISSIONS = (
    'dashboard',
    'mill_flow',
    'farmers',
    'inventory',
    'production',
    'quality',
    'sales',
    'customers',
    'finance',
    'settings',
    'users',
    'preview',
)

ROLES = (
    'admin',
    'manager',
    'operator',
    'quality_control',
    'sales',
    'accountant',
)

DEFAULT_MATRIX = {
    'admin': list(PERMISSIONS),
    'manager': [p for p in PERMISSIONS if p != 'users'],
    'operator': ['dashboard', 'mill_flow', 'farmers', 'inventory', 'production', 'settings'],
    'quality_control': ['dashboard', 'production', 'quality', 'settings'],
    'quality_controller': ['dashboard', 'production', 'quality', 'settings'],
    'sales': ['dashboard', 'customers', 'sales', 'finance', 'settings'],
    'accountant': ['dashboard', 'finance', 'customers', 'settings'],
}

PUBLIC_PREFIXES = (
    '/api/health',
    '/api/ready',
    '/api/auth/login',
    '/api/auth/suggest-username',
    '/api/auth/verify-otp',
    '/api/auth/voice-login',
    '/api/auth/biometric-login',
)

SENSITIVE_READ = {
    'finance',
    'users',
}

QUALITY_WRITE_MARKERS = ('quality-test', 'quality_test')


def normalize_role(role):
    value = (role or '').strip().lower()
    if value in ('quality_controller', 'quality'):
        return 'quality_control'
    if value in ('administrator', 'super_admin'):
        return 'admin'
    return value


def default_permissions(role):
    return list(DEFAULT_MATRIX.get(normalize_role(role), []))


def has_permission(user, permission):
    if not user or not user.is_active:
        return False
    role = normalize_role(user.role)
    row = RolePermission.query.filter_by(role=role, permission=permission).first()
    if row is not None:
        return bool(row.allowed)
    return permission in DEFAULT_MATRIX.get(role, [])


def permissions_for(user):
    return [perm for perm in PERMISSIONS if has_permission(user, perm)]


def ensure_role_permissions():
    created = 0
    for role, perms in DEFAULT_MATRIX.items():
        if role == 'quality_controller':
            continue
        for perm in PERMISSIONS:
            existing = RolePermission.query.filter_by(role=role, permission=perm).first()
            if existing:
                continue
            db.session.add(RolePermission(
                role=role,
                permission=perm,
                allowed=perm in perms,
            ))
            created += 1
    if created:
        db.session.commit()
    return created


def matrix_payload():
    rows = RolePermission.query.all()
    stored = {(row.role, row.permission): bool(row.allowed) for row in rows}
    matrix = {}
    for role in ROLES:
        matrix[role] = {}
        defaults = set(DEFAULT_MATRIX.get(role, []))
        for perm in PERMISSIONS:
            if (role, perm) in stored:
                matrix[role][perm] = stored[(role, perm)]
            else:
                matrix[role][perm] = perm in defaults
    return {
        'permissions': list(PERMISSIONS),
        'roles': list(ROLES),
        'matrix': matrix,
    }


def set_permission(role, permission, allowed):
    role = normalize_role(role)
    if role not in ROLES or permission not in PERMISSIONS:
        return None
    row = RolePermission.query.filter_by(role=role, permission=permission).first()
    if row:
        row.allowed = bool(allowed)
    else:
        row = RolePermission(role=role, permission=permission, allowed=bool(allowed))
        db.session.add(row)
    db.session.commit()
    return row


def _is_public(path):
    return any(path == prefix or path.startswith(prefix + '/') for prefix in PUBLIC_PREFIXES) or path in PUBLIC_PREFIXES


def _is_quality_write(path):
    lowered = path.lower()
    return any(marker in lowered for marker in QUALITY_WRITE_MARKERS)


def permission_for_path(path, method):
    write = method in ('POST', 'PUT', 'PATCH', 'DELETE')
    if path.startswith('/api/users') or path.startswith('/api/access'):
        return 'users'
    if path.startswith('/api/user'):
        return 'settings'
    if path.startswith('/api/finance') or path.startswith('/api/financial-intelligence'):
        return 'finance'
    if path.startswith('/api/farmer'):
        return 'farmers'
    if path.startswith('/api/inventory'):
        return 'inventory'
    if path.startswith('/api/production'):
        if write and _is_quality_write(path):
            return 'quality'
        return 'production'
    if path.startswith('/api/quality') or path.startswith('/api/quality-vision'):
        return 'quality'
    if path.startswith('/api/sales'):
        if '/customer' in path:
            return 'sales' if write else 'customers'
        return 'sales'
    if path.startswith('/api/customers'):
        return 'sales' if write else 'customers'
    if path.startswith('/api/dashboard'):
        return 'dashboard'
    if path.startswith('/api/analytics') or path.startswith('/api/compliance'):
        return 'preview'
    if path.startswith('/api/auth/me') or path.startswith('/api/auth/logout') or path.startswith('/api/notifications'):
        return None
    if write:
        return 'dashboard'
    return None


def user_may_access(user, permission, path, method):
    write = method in ('POST', 'PUT', 'PATCH', 'DELETE')
    role = normalize_role(user.role)
    if permission == 'production' and write and role == 'quality_control' and not _is_quality_write(path):
        return False
    if permission == 'customers' and write:
        return has_permission(user, 'sales')
    if not permission:
        return True
    if not write and permission not in SENSITIVE_READ and permission in (
        'dashboard', 'farmers', 'inventory', 'production', 'quality', 'sales',
        'customers', 'settings', 'mill_flow', 'preview',
    ):
        return has_permission(user, permission)
    return has_permission(user, permission)


def register_access_guard(app):
    @app.before_request
    def _enforce_role_access():
        if request.method == 'OPTIONS':
            return None
        path = request.path or ''
        if not path.startswith('/api/'):
            return None
        if _is_public(path):
            return None
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            return jsonify({'success': False, 'error': 'Unauthorized', 'message': 'Unauthorized'}), 401
        user = current_user()
        permission = permission_for_path(path, request.method)
        if permission is None:
            return None
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized', 'message': 'Unauthorized'}), 401
        if not user_may_access(user, permission, path, request.method):
            return jsonify({
                'success': False,
                'error': 'You do not have access',
                'message': 'You do not have access',
            }), 403
        return None
