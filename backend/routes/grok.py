"""Grok health and mill assistant. JWT required. Never returns the API key."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from utils import current_user

grok_bp = Blueprint('grok', __name__)


@grok_bp.route('/grok/health', methods=['GET'])
@jwt_required()
def grok_health():
    from services.grok_client import (
        GrokAPIError,
        GrokConfigError,
        configured_model,
        grok_ping,
    )
    try:
        grok_ping()
        return jsonify({'ok': True, 'model': configured_model()}), 200
    except GrokConfigError as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 200
    except GrokAPIError as exc:
        return jsonify({
            'ok': False,
            'error': str(exc),
            'model': configured_model(),
        }), 200
    except Exception:
        return jsonify({'ok': False, 'error': 'Grok health check failed'}), 200


@grok_bp.route('/assistant', methods=['POST'])
@jwt_required()
def assistant():
    payload = request.get_json(silent=True) or {}
    message = payload.get('message')
    if message is None:
        message = ''
    if not isinstance(message, str):
        return jsonify({'error': 'message must be text'}), 400
    message = message.strip()[:2000]
    route = str(payload.get('route') or '')[:120]
    language = str(payload.get('language') or 'en')[:8]
    user = current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    from services.assistant_service import run_assistant
    result = run_assistant(message, route=route, language=language, user=user)
    return jsonify({
        'reply': result.get('reply') or '',
        'actions': result.get('actions') or [],
        'engine': result.get('engine') or 'local',
    }), 200
