"""Grok health. JWT required. Never returns the API key."""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

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
