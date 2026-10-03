"""OTEL setup must not break the mill API when Phoenix is down."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TelemetrySetupTests(unittest.TestCase):
    def test_tracer_setup_does_not_throw_when_exporter_closed(self):
        from telemetry import build_otlp_exporter, init_tracer_provider
        exporter = build_otlp_exporter('http://127.0.0.1:1')
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        tracer = provider.get_tracer('millmitra-test')
        with tracer.start_as_current_span('probe') as span:
            span.set_attribute('probe', True)
        provider.force_flush(timeout_millis=2000)
        provider.shutdown()
        second = init_tracer_provider(
            service_name='millmitra-api-test',
            endpoint='http://127.0.0.1:1',
            enabled=True,
        )
        self.assertIsNotNone(second)

    def test_proxy_and_login_without_phoenix(self):
        from app import app
        client = app.test_client()
        proxy = client.post('/api/telemetry/v1/traces', json={'resourceSpans': []})
        self.assertIn(proxy.status_code, (200, 202, 204, 400))
        login = client.post(
            '/api/auth/login',
            json={'username': 'admin', 'password': 'admin123', 'method': 'password'},
        )
        self.assertEqual(login.status_code, 200, login.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
