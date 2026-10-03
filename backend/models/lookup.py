"""Configurable dropdown options maintained by admin."""

from datetime import datetime

from extensions import db


class LookupOption(db.Model):
    __tablename__ = 'lookup_options'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'group_key', 'value', name='uq_lookup_tenant_group_value'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    group_key = db.Column(db.String(80), nullable=False, index=True)
    value = db.Column(db.String(80), nullable=False)
    label_en = db.Column(db.String(200), nullable=False)
    label_hi = db.Column(db.String(200), default='')
    label_te = db.Column(db.String(200), default='')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_public(self):
        return {
            'id': self.id,
            'group_key': self.group_key,
            'value': self.value,
            'label': self.label_en,
            'labels': {
                'en': self.label_en or self.value,
                'hi': self.label_hi or self.label_en or self.value,
                'te': self.label_te or self.label_en or self.value,
            },
            'sort_order': self.sort_order,
            'is_active': bool(self.is_active),
            'is_locked': bool(self.is_locked),
        }

    def to_admin(self):
        payload = self.to_public()
        payload['label_en'] = self.label_en
        payload['label_hi'] = self.label_hi or ''
        payload['label_te'] = self.label_te or ''
        payload['created_at'] = self.created_at.isoformat() if self.created_at else None
        payload['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return payload
