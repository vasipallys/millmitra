"""OpenTelemetry traces for the mill API. Export failures must not break requests."""

import logging
import os
import time
from collections import defaultdict, deque

from flask import g, request

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = 'http://127.0.0.1:6006'
DEFAULT_SERVICE = 'millmitra-api'

_PROVIDER = None
_SQLA_INSTRUMENTED = False
_EXPORT_WARNED = False
_PROXY_WARNED = False
_PROXY_HITS = defaultdict(deque)
_PROXY_LIMIT = 60
_PROXY_WINDOW_SEC = 60.0


def _truthy(value, default=True):
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def otel_enabled(app=None):
    if app is not None and app.config.get('OTEL_ENABLED') is not None:
        return _truthy(app.config.get('OTEL_ENABLED'), True)
    return _truthy(os.environ.get('OTEL_ENABLED'), True)


def otel_endpoint(app=None):
    if app is not None and app.config.get('OTEL_EXPORTER_OTLP_ENDPOINT'):
        return str(app.config.get('OTEL_EXPORTER_OTLP_ENDPOINT')).rstrip('/')
    return (os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT') or DEFAULT_ENDPOINT).rstrip('/')


def otel_service_name(app=None):
    if app is not None and app.config.get('OTEL_SERVICE_NAME'):
        return str(app.config.get('OTEL_SERVICE_NAME'))
    return os.environ.get('OTEL_SERVICE_NAME') or DEFAULT_SERVICE


class _SafeSpanExporter:
    """Wrap OTLP export so a down collector never raises into the request."""

    def __init__(self, inner):
        self._inner = inner

    def export(self, spans):
        try:
            return self._inner.export(spans)
        except Exception:
            global _EXPORT_WARNED
            if not _EXPORT_WARNED:
                logger.warning('otel_export_failed')
                _EXPORT_WARNED = True
            from opentelemetry.sdk.trace.export import SpanExportResult
            return SpanExportResult.FAILURE

    def shutdown(self):
        try:
            self._inner.shutdown()
        except Exception:
            pass

    def force_flush(self, timeout_millis=30000):
        try:
            return bool(self._inner.force_flush(timeout_millis=timeout_millis))
        except Exception:
            return False


def _traces_url(endpoint):
    base = (endpoint or DEFAULT_ENDPOINT).rstrip('/')
    if base.endswith('/v1/traces'):
        return base
    return f'{base}/v1/traces'


def build_otlp_exporter(endpoint):
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    return _SafeSpanExporter(OTLPSpanExporter(endpoint=_traces_url(endpoint), timeout=3))


def init_tracer_provider(service_name=None, endpoint=None, enabled=None):
    """Idempotent TracerProvider. Safe when the OTLP port is closed."""
    global _PROVIDER
    if enabled is None:
        enabled = otel_enabled()
    if not enabled:
        return None
    if _PROVIDER is not None:
        return _PROVIDER

    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    resource = Resource.create({
        'service.name': service_name or otel_service_name(),
    })
    provider = TracerProvider(resource=resource)
    exporter = build_otlp_exporter(endpoint or otel_endpoint())
    provider.add_span_processor(BatchSpanProcessor(
        exporter,
        schedule_delay_millis=1000,
        max_export_batch_size=64,
        export_timeout_millis=3000,
    ))
    trace.set_tracer_provider(provider)
    _PROVIDER = provider
    return provider


def _set_request_span_attributes():
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        if span is None or not span.is_recording():
            return
        span.set_attribute('http.method', request.method)
        route = request.url_rule.rule if request.url_rule else request.path
        span.set_attribute('http.route', route)
        tenant_id = getattr(g, 'tenant_id', None)
        if tenant_id:
            span.set_attribute('tenant.id', str(tenant_id))
        user_id = getattr(g, 'otel_user_id', None)
        if user_id is None:
            try:
                from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
                verify_jwt_in_request(optional=True)
                identity = get_jwt_identity()
                if identity:
                    user_id = str(identity)
            except Exception:
                user_id = None
        if user_id:
            span.set_attribute('enduser.id', str(user_id))
    except Exception:
        logger.debug('otel_span_attributes_skipped', exc_info=True)


def _allow_proxy():
    ip = request.remote_addr or 'unknown'
    now = time.time()
    hits = _PROXY_HITS[ip]
    while hits and now - hits[0] > _PROXY_WINDOW_SEC:
        hits.popleft()
    if len(hits) >= _PROXY_LIMIT:
        return False
    hits.append(now)
    return True


def init_telemetry(app):
    """Wire tracer + Flask/SQLAlchemy instrumentors once. Never raises."""
    app.config.setdefault('OTEL_ENABLED', os.environ.get('OTEL_ENABLED', 'true'))
    app.config.setdefault('OTEL_EXPORTER_OTLP_ENDPOINT', os.environ.get(
        'OTEL_EXPORTER_OTLP_ENDPOINT', DEFAULT_ENDPOINT
    ))
    app.config.setdefault('OTEL_SERVICE_NAME', os.environ.get(
        'OTEL_SERVICE_NAME', DEFAULT_SERVICE
    ))

    if not otel_enabled(app):
        app.logger.info('otel_disabled')
        _register_proxy(app)
        return

    try:
        init_tracer_provider(
            service_name=otel_service_name(app),
            endpoint=otel_endpoint(app),
            enabled=True,
        )
    except Exception:
        app.logger.exception('otel_tracer_setup_failed')
        _register_proxy(app)
        return

    try:
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        if not getattr(app, '_otel_flask', False):
            FlaskInstrumentor().instrument_app(
                app,
                excluded_urls='api/health,api/ready,api/telemetry',
            )
            app._otel_flask = True
    except Exception:
        app.logger.exception('otel_flask_instrument_failed')

    try:
        global _SQLA_INSTRUMENTED
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from extensions import db
        if not _SQLA_INSTRUMENTED:
            with app.app_context():
                SQLAlchemyInstrumentor().instrument(engine=db.engine)
            _SQLA_INSTRUMENTED = True
    except Exception:
        app.logger.exception('otel_sqlalchemy_instrument_failed')

    @app.after_request
    def _otel_enrich_span(response):
        _set_request_span_attributes()
        return response

    _register_proxy(app)
    app.logger.info(
        'otel_enabled service=%s endpoint=%s',
        otel_service_name(app),
        otel_endpoint(app),
    )


def _register_proxy(app):
    if app.view_functions.get('telemetry_otlp_proxy'):
        return

    @app.route('/api/telemetry/v1/traces', methods=['POST', 'OPTIONS'])
    def telemetry_otlp_proxy():
        if request.method == 'OPTIONS':
            return ('', 204)
        if not _allow_proxy():
            return ('', 429)
        if not otel_enabled(app):
            return ('', 204)
        target = _traces_url(otel_endpoint(app))
        try:
            import requests
            body = request.get_data(cache=False) or b''
            if len(body) > 1_000_000:
                return ('', 413)
            incoming = request.headers.get('Content-Type') or request.content_type or ''
            if 'protobuf' in incoming.lower():
                content_type = 'application/x-protobuf'
            elif incoming.startswith('application/json'):
                content_type = incoming
            else:
                # Browser OTLP HTTP exporter sends JSON; Phoenix accepts JSON or protobuf.
                content_type = 'application/json'
            forwarded = requests.post(
                target,
                data=body,
                headers={
                    'Content-Type': content_type,
                    'Accept': request.headers.get('Accept') or '*/*',
                },
                timeout=3,
            )
            if forwarded.status_code >= 400:
                _log_proxy_issue(
                    'collector_rejected status=%s url=%s content_type=%s',
                    forwarded.status_code,
                    target,
                    content_type,
                )
            status = forwarded.status_code if forwarded.status_code < 500 else 202
            return ('', status)
        except (OSError, ConnectionError) as exc:
            _log_proxy_issue(
                'collector unreachable at %s (%s). start with `phoenix serve`',
                target,
                type(exc).__name__,
            )
            return ('', 202)
        except Exception as exc:
            _log_proxy_issue(
                'collector unreachable at %s (%s). start with `phoenix serve`',
                target,
                type(exc).__name__,
            )
            return ('', 202)


def _log_proxy_issue(message, *args):
    global _PROXY_WARNED
    if _PROXY_WARNED:
        return
    logger.warning(message, *args)
    _PROXY_WARNED = True
