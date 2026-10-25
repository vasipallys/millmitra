"""IIoT devices, telemetry rows, and supervisor discrepancies."""

from datetime import datetime
import secrets
import uuid

from extensions import db


class Device(db.Model):
    __tablename__ = 'iiot_devices'
    __table_args__ = (db.UniqueConstraint('tenant_id', 'device_id', name='uq_iiot_tenant_device'),)

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    device_id = db.Column(db.String(80), nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False)
    location = db.Column(db.String(160))
    token = db.Column(db.String(80), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def new_token():
        return secrets.token_hex(16)

    def to_dict(self, include_token=False):
        payload = {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'location': self.location or '',
            'is_active': bool(self.is_active),
        }
        if include_token:
            payload['token'] = self.token
        return payload


class MachineTelemetry(db.Model):
    """Designed as a Timescale hypertable (time, tenant_id, device_id, metric)."""

    __tablename__ = 'machine_telemetry'
    __table_args__ = (
        db.Index('ix_telemetry_tenant_device_time', 'tenant_id', 'device_id', 'time'),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = db.Column(db.String(36), index=True)
    time = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)
    device_id = db.Column(db.String(80), nullable=False, index=True)
    metric = db.Column(db.String(80), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(20), default='sensor')
    tags_json = db.Column(db.Text, default='{}')
    reason = db.Column(db.String(240))

    def to_dict(self):
        return {
            'id': self.id,
            'time': self.time.isoformat() if self.time else None,
            'device_id': self.device_id,
            'metric': self.metric,
            'value': self.value,
            'source': self.source,
            'reason': self.reason or '',
        }


class Discrepancy(db.Model):
    __tablename__ = 'iiot_discrepancies'
    __table_args__ = (
        db.Index('ix_discrepancy_tenant_device', 'tenant_id', 'device_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    device_id = db.Column(db.String(80), nullable=False)
    metric = db.Column(db.String(80), nullable=False)
    sensor_value = db.Column(db.Float)
    manual_value = db.Column(db.Float)
    tolerance = db.Column(db.Float, default=0)
    reason = db.Column(db.String(240))
    status = db.Column(db.String(20), default='open')
    resolved_by = db.Column(db.Integer)
    resolution = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'metric': self.metric,
            'sensor_value': self.sensor_value,
            'manual_value': self.manual_value,
            'tolerance': self.tolerance,
            'reason': self.reason or '',
            'status': self.status,
            'resolved_by': self.resolved_by,
            'resolution': self.resolution or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
        }


class IiotAudit(db.Model):
    __tablename__ = 'iiot_audit'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    action = db.Column(db.String(80), nullable=False)
    detail = db.Column(db.Text, default='')
    actor_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'detail': self.detail,
            'actor_id': self.actor_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
