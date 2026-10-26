"""CORS preflight on JWT-protected routes must be 2xx with allow headers."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db

PREFLIGHT = {
    'Origin': 'http://localhost:3000',
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'Authorization, X-Tenant-ID',
}


class CorsPreflightTests(unittest.TestCase):
    def setUp(self):
        handle, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(handle)
        uri = 'sqlite:///' + self.db_path.replace('\\', '/')
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': uri,
            'SQLALCHEMY_ENGINE_OPTIONS': {'pool_pre_ping': True},
            'MQTT_BROKER_URL': None,
            'REDIS_URL': None,
        })
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def _assert_preflight(self, path):
        response = self.client.options(path, headers=PREFLIGHT)
        self.assertIn(
            response.status_code,
            (200, 204),
            '%s OPTIONS %s %s' % (path, response.status_code, response.get_data(as_text=True)[:200]),
        )
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), 'http://localhost:3000')
        allow_headers = (response.headers.get('Access-Control-Allow-Headers') or '').lower()
        self.assertIn('authorization', allow_headers)
        self.assertIn('x-tenant-id', allow_headers)

    def test_options_jwt_protected_sales_orders(self):
        self._assert_preflight('/api/sales/orders')

    def test_options_sales_orders_trailing_slash(self):
        self._assert_preflight('/api/sales/orders/')

    def test_options_metadata_records_inspection(self):
        self._assert_preflight('/api/metadata/records/inspection')

    def test_options_analytics_churn_and_ltv(self):
        self._assert_preflight('/api/analytics/churn-prediction')
        self._assert_preflight('/api/analytics/lifetime-value')

    def test_authenticated_analytics_uses_order_records(self):
        login = self.client.post(
            '/api/auth/login',
            json={'username': 'admin', 'password': 'admin123', 'method': 'password'},
        )
        self.assertEqual(login.status_code, 200, login.get_data(as_text=True))
        token = login.get_json()['access_token']
        headers = {'Authorization': 'Bearer %s' % token, 'Origin': 'http://localhost:3000'}
        churn = self.client.get('/api/analytics/churn-prediction', headers=headers)
        self.assertEqual(churn.status_code, 200, churn.get_data(as_text=True))
        body = churn.get_json() or {}
        self.assertIn('high_risk_customers', body)
        self.assertEqual(body.get('method'), 'order_recency')
        ltv = self.client.get('/api/analytics/lifetime-value', headers=headers)
        self.assertEqual(ltv.status_code, 200, ltv.get_data(as_text=True))
        ltv_body = ltv.get_json() or {}
        self.assertIn('average_ltv', ltv_body)
        self.assertEqual(ltv_body.get('method'), 'order_totals')


if __name__ == '__main__':
    unittest.main()
