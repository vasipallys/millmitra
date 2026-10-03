"""Regression tests for the remediation pass. Uses the live Flask app (SQLite)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from routes.finance import parse_invoice_id, payment_status_for_amount


class RemediationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_liveness(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get('status'), 'ok')

    def test_ready_database(self):
        response = self.client.get('/api/ready')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get('database'), 'ok')

    def test_notifications_require_jwt(self):
        self.assertEqual(self.client.get('/api/notifications').status_code, 401)
        self.assertEqual(self.client.post('/api/notifications', json={'title': 'x'}).status_code, 401)
        self.assertEqual(self.client.delete('/api/notifications/1').status_code, 401)

    def test_invoice_create_requires_jwt(self):
        response = self.client.post('/api/finance/invoices', json={})
        self.assertEqual(response.status_code, 401)

    def test_invoice_create_requires_customer(self):
        from flask_jwt_extended import create_access_token
        from models import User
        with app.app_context():
            user = User.query.filter_by(is_active=True).first()
            if not user:
                self.skipTest('No mill user in the database')
            token = create_access_token(identity=str(user.id))
        response = self.client.post(
            '/api/finance/invoices',
            json={'items': [{'description': 'Rice', 'quantity': 1, 'unit_price': 10}]},
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('customer', (response.get_json() or {}).get('message', '').lower())

    def test_parse_invoice_id(self):
        self.assertEqual(parse_invoice_id('12'), 12)
        self.assertEqual(parse_invoice_id(12), 12)
        self.assertIsNone(parse_invoice_id(''))
        self.assertIsNone(parse_invoice_id('abc'))

    def test_payment_status_for_amount(self):
        self.assertEqual(payment_status_for_amount(100, 100), 'paid')
        self.assertEqual(payment_status_for_amount(100, 40), 'partial')
        self.assertEqual(payment_status_for_amount(100, 0), 'pending')


if __name__ == '__main__':
    unittest.main()
