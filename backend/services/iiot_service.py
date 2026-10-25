"""Device registry, telemetry ingest, and manual-vs-sensor reconciliation."""

import hmac
import json
import logging
from datetime import datetime, timedelta

from flask import current_app

from extensions import db
from kernel.events import BUS
from models.iiot import Device, Discrepancy, IiotAudit, MachineTelemetry
from models.tenant import Tenant
from services.tenant_scope import stamp_tenant, tq

logger = logging.getLogger(__name__)

DEMO_DEVICE_ID = 'mill-dryer-1'
MAX_METRIC_LEN = 80
MAX_REASON_LEN = 240
MAX_TAGS_JSON = 2048
VALUE_MIN = -1e9
VALUE_MAX = 1e9
TOKEN_PAD = 80


def _tolerance():
    try:
        return float(current_app.config.get('IOT_RECONCILE_TOLERANCE') or 0.5)
    except Exception:
        return 0.5


def _window_minutes():
    try:
        return int(current_app.config.get('IOT_RECONCILE_WINDOW_MINUTES') or 60)
    except Exception:
        return 60


def ensure_demo_device(tenant=None):
    tenant = tenant or Tenant.query.filter_by(slug='default').first()
    if tenant is None:
        return None
    token = current_app.config.get('IOT_DEMO_TOKEN') or 'demo-device-token'
    row = Device.query.filter_by(tenant_id=tenant.id, device_id=DEMO_DEVICE_ID).first()
    if row:
        if not row.token:
            row.token = token
            db.session.commit()
        return row
    row = Device(
        tenant_id=tenant.id,
        device_id=DEMO_DEVICE_ID,
        name='Mill dryer 1',
        location='Dryer hall',
        token=token,
        is_active=True,
    )
    db.session.add(row)
    db.session.commit()
    return row


def _padded(value):
    text = (value or '')[:TOKEN_PAD]
    return text.ljust(TOKEN_PAD, '\0')


def device_by_token(token):
    """Constant-time compare against active device tokens. Never logs the secret."""
    if not token or not isinstance(token, str):
        return None
    provided = token.strip()
    if not provided or len(provided) > TOKEN_PAD:
        return None
    matched = None
    for row in Device.query.filter_by(is_active=True).all():
        if hmac.compare_digest(_padded(row.token), _padded(provided)):
            if matched is None:
                matched = row
    return matched


def list_devices():
    return tq(Device).order_by(Device.id).all()


def create_device(payload):
    device_id = (payload.get('device_id') or '').strip()[:80]
    name = (payload.get('name') or device_id).strip()[:160]
    if not device_id:
        return None, 'device_id is required'
    existing = tq(Device).filter_by(device_id=device_id).first()
    if existing:
        return None, 'device already exists'
    supplied = payload.get('token')
    if supplied:
        return None, 'client-supplied tokens are not allowed'
    row = stamp_tenant(Device(
        device_id=device_id,
        name=name,
        location=(payload.get('location') or '')[:160],
        token=Device.new_token(),
        is_active=True,
    ))
    db.session.add(row)
    db.session.commit()
    return row, None


def latest_readings(device_id=None, limit=40):
    query = tq(MachineTelemetry).order_by(MachineTelemetry.time.desc())
    if device_id:
        query = query.filter_by(device_id=str(device_id)[:80])
    return query.limit(min(int(limit or 40), 200)).all()


def _peer_source(source):
    return 'manual' if source == 'sensor' else 'sensor'


def _find_peer(tenant_id, device_id, metric, when, source):
    start = when - timedelta(minutes=_window_minutes())
    return MachineTelemetry.query.filter(
        MachineTelemetry.tenant_id == tenant_id,
        MachineTelemetry.device_id == device_id,
        MachineTelemetry.metric == metric,
        MachineTelemetry.source == _peer_source(source),
        MachineTelemetry.time >= start,
        MachineTelemetry.time <= when,
    ).order_by(MachineTelemetry.time.desc()).first()


def _maybe_discrepancy(row, actor_id=None):
    peer = _find_peer(row.tenant_id, row.device_id, row.metric, row.time, row.source)
    if peer is None:
        return None
    delta = abs(float(row.value) - float(peer.value))
    if delta <= _tolerance():
        return None
    sensor = row if row.source == 'sensor' else peer
    manual = row if row.source == 'manual' else peer
    existing = Discrepancy.query.filter_by(
        tenant_id=row.tenant_id,
        device_id=row.device_id,
        metric=row.metric,
        status='open',
    ).first()
    if existing:
        existing.sensor_value = sensor.value
        existing.manual_value = manual.value
        existing.reason = row.reason or existing.reason
        return existing
    discrepancy = Discrepancy(
        tenant_id=row.tenant_id,
        device_id=row.device_id,
        metric=row.metric,
        sensor_value=sensor.value,
        manual_value=manual.value,
        tolerance=_tolerance(),
        reason=row.reason or 'manual vs sensor outside tolerance',
        status='open',
    )
    db.session.add(discrepancy)
    audit(row.tenant_id, 'discrepancy_opened', '%s %s' % (row.device_id, row.metric), actor_id)
    return discrepancy


def ingest(device, metric, value, source='sensor', reason=None, tags=None, when=None, actor_id=None):
    if device is None:
        return None, 'device and metric are required'
    metric = str(metric or '').strip()[:MAX_METRIC_LEN]
    if not metric:
        return None, 'device and metric are required'
    if source not in ('sensor', 'manual'):
        source = 'sensor'
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None, 'value must be numeric'
    if numeric != numeric or numeric < VALUE_MIN or numeric > VALUE_MAX:
        return None, 'value out of range'
    tags_raw = json.dumps(tags or {}, default=str)
    if len(tags_raw) > MAX_TAGS_JSON:
        return None, 'tags too large'
    when = when or datetime.utcnow()
    row = MachineTelemetry(
        tenant_id=device.tenant_id,
        time=when,
        device_id=device.device_id,
        metric=metric,
        value=numeric,
        source=source,
        tags_json=tags_raw,
        reason=(reason or '')[:MAX_REASON_LEN] or None,
    )
    db.session.add(row)
    _maybe_discrepancy(row, actor_id=actor_id)
    db.session.commit()
    BUS.publish('iiot.reading', row.to_dict())
    return row, None


def resolve_discrepancy(row, user, resolution):
    row.status = 'resolved'
    row.resolved_by = user.id if user else None
    row.resolution = (resolution or '')[:2000]
    row.resolved_at = datetime.utcnow()
    audit(row.tenant_id, 'discrepancy_resolved', str(row.id), row.resolved_by)
    db.session.commit()
    return row


def audit(tenant_id, action, detail, actor_id=None):
    db.session.add(IiotAudit(
        tenant_id=tenant_id,
        action=action,
        detail=(detail or '')[:500],
        actor_id=actor_id,
    ))


def list_discrepancies(status=None):
    query = tq(Discrepancy).order_by(Discrepancy.created_at.desc())
    if status in ('open', 'resolved'):
        query = query.filter_by(status=status)
    return query.limit(100).all()
