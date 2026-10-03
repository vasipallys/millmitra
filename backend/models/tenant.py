"""Shared-schema tenants. Users stay global; membership is per mill."""

from datetime import datetime
import uuid

from extensions import db

STATUS_ACTIVE = 'ACTIVE'
STATUS_TRIAL = 'TRIAL'
STATUS_SUSPENDED = 'SUSPENDED'
TENANT_STATUSES = (STATUS_ACTIVE, STATUS_TRIAL, STATUS_SUSPENDED)


def new_tenant_id():
    return str(uuid.uuid4())


class Tenant(db.Model):
    __tablename__ = 'tenants'

    id = db.Column(db.String(36), primary_key=True, default=new_tenant_id)
    name = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default=STATUS_ACTIVE, nullable=False)
    timezone = db.Column(db.String(60), default='Asia/Kolkata')
    locale = db.Column(db.String(12), default='en')
    currency = db.Column(db.String(8), default='INR')
    logo_url = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_suspended(self):
        return (self.status or '').upper() == STATUS_SUSPENDED

    def to_public(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'status': self.status,
            'timezone': self.timezone,
            'locale': self.locale,
            'currency': self.currency,
            'logo_url': self.logo_url,
        }


class TenantMembership(db.Model):
    __tablename__ = 'tenant_memberships'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'tenant_id', name='uq_membership_user_tenant'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    tenant_id = db.Column(db.String(36), db.ForeignKey('tenants.id'), nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False, default='operator')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, tenant=None):
        payload = {
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'role': self.role,
        }
        if tenant is not None:
            payload['tenant'] = tenant.to_public()
        return payload
