"""Create and switch organizations. Lookups and access matrix are per tenant."""

import re

from flask_jwt_extended import create_access_token
from datetime import timedelta

from extensions import db
from models.tenant import STATUS_ACTIVE, Tenant, TenantMembership, new_tenant_id
from models.user import User
from services.access_control import ensure_role_permissions
from services.lookup_service import ensure_lookup_options
from services.tenant_context import membership_for, memberships_for
from services.tenant_migration import DEFAULT_SLUG

SLUG_OK = re.compile(r'^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$')


def normalize_slug(value):
    slug = re.sub(r'[^a-z0-9]+', '-', str(value or '').strip().lower()).strip('-')
    return slug[:80]


def seed_tenant_defaults(tenant_id):
    ensure_role_permissions(tenant_id=tenant_id)
    ensure_lookup_options(tenant_id=tenant_id)


def create_tenant(name, slug=None, owner=None, owner_payload=None, status=STATUS_ACTIVE):
    slug = normalize_slug(slug or name)
    if not SLUG_OK.match(slug) and slug != DEFAULT_SLUG:
        if not slug:
            return None, 'A mill slug is required'
    existing = Tenant.query.filter_by(slug=slug).first()
    if existing:
        return existing, None
    tenant = Tenant(
        id=new_tenant_id(),
        name=(name or slug).strip() or slug,
        slug=slug,
        status=status or STATUS_ACTIVE,
        timezone='Asia/Kolkata',
        locale='en',
        currency='INR',
    )
    db.session.add(tenant)
    db.session.flush()

    user = owner
    if user is None and owner_payload:
        username = str(owner_payload.get('username') or '').strip()
        password = owner_payload.get('password') or ''
        if not username or not password:
            db.session.rollback()
            return None, 'Owner username and password are required'
        clash = User.query.filter((User.username == username) | (User.email == username)).first()
        if clash:
            db.session.rollback()
            return None, 'Username already exists'
        user = User(
            username=username,
            email=owner_payload.get('email') or f'{username}@ricemill.com',
            first_name=owner_payload.get('first_name') or username,
            last_name=owner_payload.get('last_name') or '',
            role='admin',
            is_active=True,
            is_verified=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

    if user is not None and not membership_for(user.id, tenant.id):
        db.session.add(TenantMembership(user_id=user.id, tenant_id=tenant.id, role='admin'))
    db.session.commit()
    seed_tenant_defaults(tenant.id)
    return tenant, None


def tenants_for_user(user):
    rows = memberships_for(user.id)
    tenants = []
    for row in rows:
        tenant = Tenant.query.get(row.tenant_id)
        if tenant:
            payload = tenant.to_public()
            payload['role'] = row.role
            tenants.append(payload)
    return tenants


def switch_token(user, tenant_id):
    membership = membership_for(user.id, tenant_id)
    if not membership:
        return None, 'You do not have access to that mill'
    tenant = Tenant.query.get(membership.tenant_id)
    if tenant is None:
        return None, 'Mill not found'
    token = create_access_token(
        identity=str(user.id),
        additional_claims={'tenant_id': tenant.id},
        expires_delta=timedelta(hours=8),
    )
    return {
        'access_token': token,
        'tenant': tenant.to_public(),
        'role': membership.role,
    }, None
