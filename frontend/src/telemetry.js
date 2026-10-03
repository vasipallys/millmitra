import { context, propagation, SpanKind, SpanStatusCode, trace } from '@opentelemetry/api';
import { ZoneContextManager } from '@opentelemetry/context-zone';
import { W3CTraceContextPropagator } from '@opentelemetry/core';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { BatchSpanProcessor, WebTracerProvider } from '@opentelemetry/sdk-trace-web';

const TRACER_NAME = 'millmitra-web';

function apiBaseUrl() {
  const base = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
  return String(base).replace(/\/$/, '');
}

function tracesUrl() {
  return `${apiBaseUrl()}/telemetry/v1/traces`;
}

export function otelEnabled() {
  const value = import.meta.env.VITE_OTEL_ENABLED;
  if (value == null || value === '') {
    return true;
  }
  return String(value).toLowerCase() !== 'false' && value !== '0';
}

export function isTelemetryRequest(url) {
  return typeof url === 'string' && url.includes('/telemetry/');
}

export function initWebTelemetry() {
  if (!otelEnabled() || typeof window === 'undefined') {
    return;
  }
  if (window.__millmitraOtelStarted) {
    return;
  }
  try {
    const exporter = new OTLPTraceExporter({
      url: tracesUrl(),
      headers: {},
    });
    const provider = new WebTracerProvider({
      resource: new Resource({
        'service.name': 'millmitra-web',
      }),
    });
    provider.addSpanProcessor(new BatchSpanProcessor(exporter, {
      scheduledDelayMillis: 1000,
      maxExportBatchSize: 32,
    }));
    try {
      provider.register({
        contextManager: new ZoneContextManager(),
        propagator: new W3CTraceContextPropagator(),
      });
    } catch {
      provider.register({
        propagator: new W3CTraceContextPropagator(),
      });
    }
    propagation.setGlobalPropagator(new W3CTraceContextPropagator());
    window.__millmitraOtelStarted = true;
  } catch {
    // Tracing must never block login or mill screens.
  }
}

export function attachApiTrace(config) {
  if (!otelEnabled() || !config || isTelemetryRequest(config.url || '')) {
    return config;
  }
  try {
    const tracer = trace.getTracer(TRACER_NAME);
    const method = (config.method || 'GET').toUpperCase();
    const path = config.url || '';
    const span = tracer.startSpan(`HTTP ${method} ${path}`, { kind: SpanKind.CLIENT });
    span.setAttribute('http.method', method);
    span.setAttribute('http.url', `${config.baseURL || apiBaseUrl()}${path}`);
    const carrier = {};
    const spanContext = trace.setSpan(context.active(), span);
    propagation.inject(spanContext, carrier);
    config.headers = config.headers || {};
    if (carrier.traceparent) {
      config.headers.traceparent = carrier.traceparent;
    }
    if (carrier.tracestate) {
      config.headers.tracestate = carrier.tracestate;
    }
    config._otelSpan = span;
  } catch {
    // keep the request
  }
  return config;
}

export function endApiTrace(config, status, error) {
  const span = config && config._otelSpan;
  if (!span) {
    return;
  }
  try {
    if (status) {
      span.setAttribute('http.status_code', status);
    }
    if (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: 'request failed' });
    }
    span.end();
  } catch {
    // ignore
  }
}

export function recordNavigation(pathname) {
  if (!otelEnabled() || !pathname) {
    return;
  }
  try {
    const tracer = trace.getTracer(TRACER_NAME);
    const span = tracer.startSpan(`navigation ${pathname}`);
    span.setAttribute('http.route', pathname);
    span.end();
  } catch {
    // ignore
  }
}
