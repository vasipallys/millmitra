"""
Lightweight operational visibility for the mill API.

No Redis, Prometheus, or extra process. Logs one line per request and
returns a safe JSON body on unexpected 500s.
"""
import logging
import time
import uuid
from datetime import datetime

from flask import g, jsonify, request
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

from extensions import db

_SKIP_ACCESS_LOG = frozenset({
    '/api/health',
    '/api/ready',
    '/favicon.ico',
})

_SENSITIVE_QUERY_KEYS = frozenset({
    'password', 'token', 'access_token', 'refresh_token',
    'secret', 'jwt', 'authorization', 'otp', 'session_token',
})


def configure_logging(app):
    """Idempotent console logging. Does not attach extra handlers on reload."""
    if app.logger.handlers:
        app.logger.setLevel(logging.INFO)
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False


def _safe_query_string():
    if not request.query_string:
        return ''
    parts = []
    for key, values in request.args.lists():
        if key.lower() in _SENSITIVE_QUERY_KEYS:
            parts.append(f'{key}=***')
        else:
            parts.append(f'{key}={",".join(values)}')
    return '&'.join(parts)


def init_observability(app):
    configure_logging(app)

    @app.before_request
    def _start_request_timer():
        g.request_started = time.perf_counter()
        g.request_id = request.headers.get('X-Request-ID') or uuid.uuid4().hex[:12]

    @app.after_request
    def _log_request(response):
        request_id = getattr(g, 'request_id', '-')
        response.headers['X-Request-ID'] = request_id
        if request.path in _SKIP_ACCESS_LOG or request.method == 'OPTIONS':
            return response
        started = getattr(g, 'request_started', None)
        duration_ms = round((time.perf_counter() - started) * 1000, 1) if started else None
        app.logger.info(
            'request method=%s path=%s status=%s duration_ms=%s request_id=%s query=%s',
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            request_id,
            _safe_query_string(),
        )
        return response

    @app.errorhandler(HTTPException)
    def _http_error(error):
        payload = {
            'success': False,
            'message': error.description or error.name,
        }
        if error.code >= 500:
            error_id = getattr(g, 'request_id', uuid.uuid4().hex[:12])
            payload['error_id'] = error_id
            app.logger.error(
                'http_error status=%s path=%s request_id=%s message=%s',
                error.code,
                request.path,
                error_id,
                error.description,
            )
        return jsonify(payload), error.code

    @app.errorhandler(Exception)
    def _unhandled_error(error):
        if isinstance(error, HTTPException):
            return _http_error(error)
        error_id = getattr(g, 'request_id', uuid.uuid4().hex[:12])
        app.logger.exception(
            'unhandled_error request_id=%s method=%s path=%s',
            error_id,
            request.method,
            request.path,
        )
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Try again or contact the mill administrator.',
            'error_id': error_id,
        }), 500

    @app.route('/api/health', methods=['GET'])
    def liveness():
        return jsonify({
            'status': 'ok',
            'check': 'liveness',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
        }), 200

    @app.route('/api/ready', methods=['GET'])
    def readiness():
        db_ok = False
        db_error = None
        try:
            db.session.execute(text('SELECT 1'))
            db_ok = True
        except Exception as exc:
            db.session.rollback()
            db_error = type(exc).__name__
            app.logger.warning('readiness db_check_failed error=%s', db_error)

        payload = {
            'status': 'ok' if db_ok else 'unavailable',
            'check': 'readiness',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'database': 'ok' if db_ok else 'error',
        }
        if db_error:
            payload['database_error'] = db_error
        return jsonify(payload), 200 if db_ok else 503
