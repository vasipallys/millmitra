"""Notification API backed by the notifications table."""

import queue

from flask import Blueprint, Response, jsonify, request, stream_with_context
from flask_jwt_extended import decode_token, jwt_required

from models.user import User
from services import notification_service as notes
from utils import current_user

notifications_bp = Blueprint('notifications', __name__)

CATEGORIES = [
    {'id': 'farmer_management', 'name': 'Farmer Management'},
    {'id': 'production', 'name': 'Production'},
    {'id': 'inventory', 'name': 'Inventory'},
    {'id': 'quality', 'name': 'Quality Control'},
    {'id': 'sales', 'name': 'Sales'},
    {'id': 'finance', 'name': 'Finance'},
    {'id': 'system', 'name': 'System'},
]


def _require_user():
    user = current_user()
    if not user:
        return None, (jsonify({'success': False, 'message': 'Authentication required'}), 401)
    return user, None


def _user_from_header_or_query():
    header = request.headers.get('Authorization') or ''
    token = ''
    if header.lower().startswith('bearer '):
        token = header.split(' ', 1)[1].strip()
    if not token:
        token = (request.args.get('access_token') or '').strip()
    if not token:
        return None
    try:
        payload = decode_token(token)
        identity = payload.get('sub')
        return User.query.get(int(identity))
    except Exception:
        return None


@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user, error = _require_user()
    if error:
        return error
    items = notes.list_notifications(user.id)
    return jsonify({
        'success': True,
        'notifications': items,
        'unread_count': notes.unread_count(user.id),
        'total': len(items),
    })


@notifications_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    user, error = _require_user()
    if error:
        return error
    row = notes.mark_read(user.id, notification_id)
    if not row:
        return jsonify({'success': False, 'error': 'Notification not found'}), 404
    return jsonify({'success': True, 'message': 'Notification marked as read', 'notification': row.to_dict()})


@notifications_bp.route('/notifications/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    user, error = _require_user()
    if error:
        return error
    notes.mark_all_read(user.id)
    return jsonify({'success': True, 'message': 'All notifications marked as read'})


@notifications_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    user, error = _require_user()
    if error:
        return error
    if not notes.delete_notification(user.id, notification_id):
        return jsonify({'success': False, 'error': 'Notification not found'}), 404
    return jsonify({'success': True, 'message': 'Notification deleted'})


@notifications_bp.route('/notifications', methods=['POST'])
@jwt_required()
def create_notification():
    user, error = _require_user()
    if error:
        return error
    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'title is required'}), 400
    row = notes.create_notification(
        title=title,
        body=data.get('body') or data.get('message') or '',
        category=data.get('category') or 'system',
        severity=data.get('severity') or data.get('priority') or 'medium',
        link=data.get('link') or data.get('action_url'),
        user_id=data.get('user_id'),
    )
    return jsonify({
        'success': True,
        'notification': row.to_dict(),
        'message': 'Notification created',
    }), 201


@notifications_bp.route('/notifications/categories', methods=['GET'])
@jwt_required()
def get_notification_categories():
    return jsonify({'success': True, 'categories': CATEGORIES})


@notifications_bp.route('/notifications/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    user, error = _require_user()
    if error:
        return error
    items = notes.list_notifications(user.id)
    unread = sum(1 for item in items if not item.get('read'))
    priority = {'high': 0, 'medium': 0, 'low': 0}
    categories = {}
    for item in items:
        key = item.get('severity') or 'medium'
        if key in priority:
            priority[key] += 1
        category = item.get('category') or 'system'
        categories[category] = categories.get(category, 0) + 1
    return jsonify({
        'success': True,
        'stats': {
            'total': len(items),
            'unread': unread,
            'read': len(items) - unread,
            'priority': priority,
            'categories': categories,
        },
    })


@notifications_bp.route('/notifications/stream', methods=['GET'])
def stream_notifications():
    """SSE of new rows. Auth: Authorization Bearer, or access_token query for EventSource."""
    user = _user_from_header_or_query()
    if not user:
        return jsonify({'success': False, 'message': 'Authentication required'}), 401
    viewer_id = user.id

    waiter = notes.subscribe()

    def generate():
        try:
            yield 'event: ready\ndata: {}\n\n'
            while True:
                try:
                    event = waiter.get(timeout=25)
                except queue.Empty:
                    yield ': keepalive\n\n'
                    continue
                owner = event.get('user_id')
                if owner is not None and int(owner) != int(viewer_id):
                    continue
                yield notes.encode_sse({'notification': event.get('notification')})
        finally:
            notes.unsubscribe(waiter)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )
