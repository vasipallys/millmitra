"""Active mill (tenant) for the current request. Never trust a raw header."""

from flask import g, has_request_context, jsonify, request
from flask_jwt_extended import get_jwt

from models.tenant import Tenant, TenantMembership

TENANT_HEADER = 'X-Tenant-ID'
SUSPENDED_ALLOWED_PREFIXES = (
    '/api/auth/me',
    '/api/auth/logout',
    '/api/tenants',
)


def current_tenant_id():
    if has_request_context():
        return getattr(g, 'tenant_id', None)
    return None


def current_tenant():
    if has_request_context():
        return getattr(g, 'tenant', None)
    return None


def current_membership():
    if has_request_context():
        return getattr(g, 'membership', None)
    return None


def current_tenant_role(user=None):
    membership = current_membership()
    if membership is not None:
        return membership.role
    if user is not None:
        return user.role
    return None


def memberships_for(user_id):
    return TenantMembership.query.filter_by(user_id=user_id).all()


def membership_for(user_id, tenant_id):
    if not user_id or not tenant_id:
        return None
    return TenantMembership.query.filter_by(user_id=user_id, tenant_id=str(tenant_id)).first()


def _claim_tenant_id():
    try:
        claims = get_jwt() or {}
    except Exception:
        return None
    value = claims.get('tenant_id')
    return str(value) if value else None


def _header_tenant_id():
    value = (request.headers.get(TENANT_HEADER) or '').strip()
    return value or None


def _is_suspended_allowed(path):
    return any(path == prefix or path.startswith(prefix + '/') for prefix in SUSPENDED_ALLOWED_PREFIXES)


def bind_tenant(user, path=''):
    """Set g.tenant_id from JWT / allowed header. Returns a Flask response on error."""
    if user is None:
        g.tenant_id = None
        g.tenant = None
        g.membership = None
        g.tenant_role = None
        return None

    rows = memberships_for(user.id)
    if not rows:
        if (path or request.path or '').startswith('/api/tenants'):
            g.tenant_id = None
            g.tenant = None
            g.membership = None
            g.tenant_role = None
            return None
        return jsonify({
            'success': False,
            'error': 'No mill membership',
            'message': 'This account is not assigned to a mill',
        }), 403

    header_id = _header_tenant_id()
    claim_id = _claim_tenant_id()
    chosen = header_id or claim_id or rows[0].tenant_id

    membership = next((row for row in rows if row.tenant_id == str(chosen)), None)
    if membership is None:
        return jsonify({
            'success': False,
            'error': 'You do not have access to that mill',
            'message': 'You do not have access to that mill',
        }), 403

    if claim_id and header_id is None and str(claim_id) != membership.tenant_id:
        return jsonify({
            'success': False,
            'error': 'You do not have access to that mill',
            'message': 'You do not have access to that mill',
        }), 403

    tenant = Tenant.query.get(membership.tenant_id)
    if tenant is None:
        return jsonify({
            'success': False,
            'error': 'Mill not found',
            'message': 'Mill not found',
        }), 403

    if tenant.is_suspended() and not _is_suspended_allowed(path or request.path or ''):
        return jsonify({
            'success': False,
            'error': 'This mill is suspended',
            'message': 'This mill is suspended',
        }), 403

    g.tenant_id = tenant.id
    g.tenant = tenant
    g.membership = membership
    g.tenant_role = membership.role
    return None


def issue_tenant_claims(user, tenant_id):
    membership = membership_for(user.id, tenant_id)
    if not membership:
        return None
    return {'tenant_id': membership.tenant_id}
