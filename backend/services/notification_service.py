"""Create and deliver mill notifications from real database events."""

import json
import queue
import threading
from datetime import datetime

from sqlalchemy import or_

from extensions import db
from models.notification import Notification

_subscribers = []
_lock = threading.Lock()


def subscribe():
    waiter = queue.Queue(maxsize=100)
    with _lock:
        _subscribers.append(waiter)
    return waiter


def unsubscribe(waiter):
    with _lock:
        if waiter in _subscribers:
            _subscribers.remove(waiter)


def publish(payload, owner_id=None):
    event = {'notification': payload, 'user_id': owner_id}
    with _lock:
        waiters = list(_subscribers)
    for waiter in waiters:
        try:
            waiter.put_nowait(event)
        except queue.Full:
            pass


def visible_query(user_id):
    return Notification.query.filter(
        or_(Notification.user_id.is_(None), Notification.user_id == user_id)
    )


def create_notification(
    title,
    body,
    category=None,
    severity='medium',
    link=None,
    user_id=None,
):
    """Persist a mill-wide (user_id null) or user-targeted notification."""
    row = Notification(
        user_id=user_id,
        title=(title or 'Mill update')[:200],
        body=body or '',
        category=category,
        severity=severity or 'medium',
        link=link,
        created_at=datetime.utcnow(),
    )
    db.session.add(row)
    db.session.commit()
    publish(row.to_dict(), owner_id=row.user_id)
    return row


def safe_notify(*args, **kwargs):
    try:
        return create_notification(*args, **kwargs)
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


def list_notifications(user_id, limit=100):
    rows = (
        visible_query(user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return [row.to_dict() for row in rows]


def unread_count(user_id):
    return visible_query(user_id).filter(Notification.read_at.is_(None)).count()


def get_visible(user_id, notification_id):
    return visible_query(user_id).filter(Notification.id == notification_id).first()


def mark_read(user_id, notification_id):
    row = get_visible(user_id, notification_id)
    if not row:
        return None
    if row.read_at is None:
        row.read_at = datetime.utcnow()
        db.session.commit()
    return row


def mark_all_read(user_id):
    now = datetime.utcnow()
    updated = (
        visible_query(user_id)
        .filter(Notification.read_at.is_(None))
        .update({'read_at': now}, synchronize_session=False)
    )
    db.session.commit()
    return updated


def delete_notification(user_id, notification_id):
    row = get_visible(user_id, notification_id)
    if not row:
        return False
    db.session.delete(row)
    db.session.commit()
    return True


def _qty(value):
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return 0.0
    return number


def _label(value, fallback='item'):
    text = (value or '').strip() if isinstance(value, str) else ''
    return text or fallback


def farmer_registered(farmer):
    name = _label(getattr(farmer, 'name', None), 'Farmer')
    code = getattr(farmer, 'farmer_code', None) or ''
    suffix = f' ({code})' if code else ''
    return safe_notify(
        title='New farmer registered',
        body=f'{name}{suffix} was registered',
        category='farmer_management',
        severity='medium',
        link='/farmers',
    )


def paddy_stock_added(stock):
    variety = _label(getattr(stock, 'variety', None), 'Paddy')
    qty = _qty(getattr(stock, 'quantity', 0) or getattr(stock, 'remaining_quantity', 0))
    return safe_notify(
        title='Paddy stock added',
        body=f'{qty:g} kg {variety} received',
        category='inventory',
        severity='low',
        link='/inventory',
    )


def notify_low_product_stock(stock):
    if stock is None:
        return None
    try:
        from services.mill_settings_service import notification_writer_enabled
        if not notification_writer_enabled('lowStockAlerts', True):
            return None
    except Exception:
        pass
    threshold = (
        getattr(stock, 'minimum_stock_level', None)
        or getattr(stock, 'reorder_point', None)
        or 100
    )
    qty = _qty(getattr(stock, 'quantity', 0))
    try:
        limit = float(threshold)
    except (TypeError, ValueError):
        limit = 100.0
    if qty > limit:
        return None
    name = _label(
        getattr(stock, 'product_name', None) or getattr(stock, 'variety', None),
        'Product',
    )
    link = f'/inventory?stock={getattr(stock, "id", "")}'
    existing = Notification.query.filter(
        Notification.category == 'inventory',
        Notification.link == link,
        Notification.read_at.is_(None),
        Notification.title == 'Low stock',
    ).first()
    if existing:
        return existing
    return safe_notify(
        title='Low stock',
        body=f'{name} stock is running low ({qty:g} kg)',
        category='inventory',
        severity='high',
        link=link,
    )


def batch_started(batch):
    number = _label(getattr(batch, 'batch_number', None), f'#{getattr(batch, "id", "")}')
    return safe_notify(
        title='Production batch started',
        body=f'Batch {number} is in progress',
        category='production',
        severity='medium',
        link='/production',
    )


def batch_completed(batch):
    try:
        from services.mill_settings_service import notification_writer_enabled
        if not notification_writer_enabled('productionAlerts', True):
            return None
    except Exception:
        pass
    number = _label(getattr(batch, 'batch_number', None), f'#{getattr(batch, "id", "")}')
    output = _qty(
        getattr(batch, 'rice_output', None)
        or getattr(batch, 'output_quantity', None)
    )
    detail = f' ({output:g} kg rice)' if output else ''
    return safe_notify(
        title='Production batch completed',
        body=f'Batch {number} finished{detail}',
        category='production',
        severity='low',
        link='/production',
    )


def sales_order_created(order, customer=None):
    number = _label(getattr(order, 'order_number', None), f'#{getattr(order, "id", "")}')
    buyer = ''
    if customer is not None:
        buyer = _label(
            getattr(customer, 'company_name', None)
            or getattr(customer, 'business_name', None)
            or getattr(customer, 'name', None),
            '',
        )
    suffix = f' for {buyer}' if buyer else ''
    return safe_notify(
        title='Sales order created',
        body=f'Order {number}{suffix}',
        category='sales',
        severity='medium',
        link='/sales',
    )


def invoice_created(invoice):
    number = _label(getattr(invoice, 'invoice_number', None), f'#{getattr(invoice, "id", "")}')
    amount = _qty(getattr(invoice, 'total_amount', 0))
    return safe_notify(
        title='Invoice created',
        body=f'Invoice {number} for ₹{amount:g}',
        category='finance',
        severity='medium',
        link='/finance',
    )


def payment_recorded(payment):
    amount = _qty(getattr(payment, 'amount', 0))
    ref = getattr(payment, 'payment_id', None) or getattr(payment, 'payment_number', None) or ''
    suffix = f' ({ref})' if ref else ''
    return safe_notify(
        title='Payment recorded',
        body=f'Payment of ₹{amount:g} recorded{suffix}',
        category='finance',
        severity='low',
        link='/finance',
    )


class NotificationService:
    """Compatibility wrappers used by inventory helpers."""

    create_notification = staticmethod(create_notification)

    @staticmethod
    def create_farmer_registration_notification(farmer):
        return farmer_registered(farmer)

    @staticmethod
    def create_production_batch_notification(batch_data):
        class _Batch:
            batch_number = (batch_data or {}).get('batch_number')
            id = (batch_data or {}).get('id')
            rice_output = (batch_data or {}).get('output_quantity')

        return batch_completed(_Batch())

    @staticmethod
    def create_inventory_low_stock_notification(item):
        class _Stock:
            id = (item or {}).get('id')
            product_name = (item or {}).get('name')
            variety = (item or {}).get('name')
            quantity = (item or {}).get('quantity', 0)
            minimum_stock_level = 0
            reorder_point = 0

        return notify_low_product_stock(_Stock())


def encode_sse(payload):
    return f"data: {json.dumps(payload)}\n\n"
