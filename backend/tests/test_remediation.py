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

    def test_dashboard_overview_as_manager(self):
        from flask_jwt_extended import create_access_token
        from models import User
        with app.app_context():
            user = (
                User.query.filter(User.role.ilike('manager')).first()
                or User.query.filter_by(is_active=True).first()
            )
            if not user:
                self.skipTest('No mill user in the database')
            token = create_access_token(identity=str(user.id))
        response = self.client.get(
            '/api/dashboard/overview?days=7',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        body = response.get_json() or {}
        summary = body.get('summary') or {}
        self.assertIn('total_production', summary)
        self.assertGreaterEqual(float(summary.get('total_production') or 0), 0)
        self.assertGreaterEqual(float(summary.get('quality_score') or 0), 0)
        self.assertGreaterEqual(float(summary.get('inventory_value') or 0), 0)
        self.assertGreaterEqual(int(summary.get('pending_orders') or 0), 0)
        self.assertGreaterEqual(int(summary.get('active_farmers') or 0), 0)
        self.assertIn('role_data', body)

    def _overview_as(self, role_needles):
        from flask_jwt_extended import create_access_token
        from models import User
        with app.app_context():
            user = None
            for needle in role_needles:
                user = User.query.filter(User.role.ilike(needle)).first()
                if user:
                    break
            if not user:
                self.skipTest(f'No mill user with role {role_needles}')
            token = create_access_token(identity=str(user.id))
        response = self.client.get(
            '/api/dashboard/overview?days=7',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        body = response.get_json() or {}
        summary = body.get('summary') or {}
        self.assertIn('total_production', summary)
        self.assertIn('role_data', body)
        return body

    def test_dashboard_overview_as_admin(self):
        body = self._overview_as(['admin', 'administrator', 'super_admin'])
        self.assertIn('profit_margin', body.get('role_data') or {})

    def test_login_quality_user_and_wrong_password(self):
        from services.demo_users import ensure_demo_users
        with app.app_context():
            ensure_demo_users()
        ok = self.client.post(
            '/api/auth/login',
            json={'username': 'quality', 'password': 'quality123', 'method': 'password'},
        )
        self.assertEqual(ok.status_code, 200, ok.get_data(as_text=True))
        payload = ok.get_json() or {}
        self.assertTrue(payload.get('access_token'))
        self.assertEqual((payload.get('user') or {}).get('username'), 'quality')
        bad = self.client.post(
            '/api/auth/login',
            json={'username': 'quality', 'password': 'not-the-password', 'method': 'password'},
        )
        self.assertEqual(bad.status_code, 401)
        message = ((bad.get_json() or {}).get('error') or (bad.get_json() or {}).get('message') or '')
        self.assertIn('not recognized', message.lower())
        with app.app_context():
            from flask_jwt_extended import decode_token
            from models.tenant import TenantMembership
            claims = decode_token(payload.get('access_token'))
            tenant_id = claims.get('tenant_id')
            self.assertTrue(tenant_id)
            self.assertEqual(tenant_id, ((payload.get('user') or {}).get('tenant') or {}).get('id'))
            membership = TenantMembership.query.filter_by(
                user_id=(payload.get('user') or {}).get('id'),
                tenant_id=tenant_id,
            ).first()
            self.assertIsNotNone(membership)

    def test_login_admin_token_tenant_matches_membership(self):
        from flask_jwt_extended import decode_token
        from models.tenant import TenantMembership
        from services.demo_users import ensure_demo_users
        from services.tenant_migration import ensure_default_tenant, ensure_user_memberships, migrate_tenant_schema

        with app.app_context():
            migrate_tenant_schema()
            ensure_demo_users()
            ensure_user_memberships(ensure_default_tenant())
        ok = self.client.post(
            '/api/auth/login',
            json={'username': 'admin', 'password': 'admin123', 'method': 'password'},
        )
        self.assertEqual(ok.status_code, 200, ok.get_data(as_text=True))
        payload = ok.get_json() or {}
        token = payload.get('access_token')
        user = payload.get('user') or {}
        self.assertTrue(token)
        self.assertEqual((user.get('tenant') or {}).get('slug'), 'default')
        with app.app_context():
            claims = decode_token(token)
            tenant_id = claims.get('tenant_id')
            self.assertTrue(tenant_id)
            self.assertEqual(tenant_id, (user.get('tenant') or {}).get('id'))
            membership = TenantMembership.query.filter_by(
                user_id=user.get('id'),
                tenant_id=tenant_id,
            ).first()
            self.assertIsNotNone(membership)

    def test_roles_access_and_sales_user(self):
        from flask_jwt_extended import create_access_token
        from models import User
        from services.demo_users import ensure_demo_users
        from services.access_control import ensure_role_permissions
        with app.app_context():
            ensure_demo_users()
            ensure_role_permissions()
            sales = User.query.filter_by(username='sales').first()
            self.assertIsNotNone(sales)
            operator = User.query.filter_by(username='operator').first()
            admin = User.query.filter_by(username='admin').first()
            self.assertIsNotNone(operator)
            self.assertIsNotNone(admin)
            op_token = create_access_token(identity=str(operator.id))
            ad_token = create_access_token(identity=str(admin.id))
        forbidden = self.client.post(
            '/api/finance/invoices',
            json={'customer_id': 1, 'items': [{'description': 'Rice', 'quantity': 1, 'unit_price': 10}]},
            headers={'Authorization': f'Bearer {op_token}'},
        )
        self.assertEqual(forbidden.status_code, 403, forbidden.get_data(as_text=True))
        listed = self.client.get(
            '/api/users',
            headers={'Authorization': f'Bearer {ad_token}'},
        )
        self.assertEqual(listed.status_code, 200, listed.get_data(as_text=True))
        names = [item.get('username') for item in (listed.get_json() or {}).get('users', [])]
        self.assertIn('sales', names)

    def test_notifications_create_list_and_mark_read(self):
        from flask_jwt_extended import create_access_token
        from models import User
        from services.notification_service import create_notification

        with app.app_context():
            user = User.query.filter_by(is_active=True).first()
            if not user:
                self.skipTest('No mill user in the database')
            row = create_notification(
                title='Test mill event',
                body='Created by remediation test',
                category='system',
                severity='low',
                link='/notifications',
            )
            self.assertIsNotNone(row.id)
            note_id = row.id
            token = create_access_token(identity=str(user.id))

        listed = self.client.get(
            '/api/notifications',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(listed.status_code, 200, listed.get_data(as_text=True))
        payload = listed.get_json() or {}
        items = payload.get('notifications') or []
        self.assertTrue(isinstance(items, list))
        found = next((item for item in items if item.get('id') == note_id), None)
        self.assertIsNotNone(found)
        self.assertEqual(found.get('title'), 'Test mill event')
        self.assertFalse(found.get('read'))
        fake_bodies = ' '.join(
            f"{item.get('title', '')} {item.get('body', '')} {item.get('message', '')}"
            for item in items
        )
        self.assertNotIn('PB001', fake_bodies)
        self.assertNotIn('Siva Kumar reddy Vasipally', fake_bodies)

        marked = self.client.post(
            f'/api/notifications/{note_id}/read',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(marked.status_code, 200, marked.get_data(as_text=True))
        again = self.client.get(
            '/api/notifications',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(again.status_code, 200)
        reread = next(
            (item for item in (again.get_json() or {}).get('notifications', []) if item.get('id') == note_id),
            None,
        )
        self.assertIsNotNone(reread)
        self.assertTrue(reread.get('read'))

    def test_backup_admin_file_operator_forbidden(self):
        from flask_jwt_extended import create_access_token
        from models import User
        from services.demo_users import ensure_demo_users
        from services.mill_settings_service import sqlite_file_path

        with app.app_context():
            ensure_demo_users()
            admin = User.query.filter_by(username='admin').first()
            operator = User.query.filter_by(username='operator').first()
            if not admin or not operator:
                self.skipTest('Demo admin/operator missing')
            db_file = sqlite_file_path()
            if not db_file.exists():
                self.skipTest('SQLite database file not found')
            admin_token = create_access_token(identity=str(admin.id))
            operator_token = create_access_token(identity=str(operator.id))

        created = self.client.post(
            '/api/user/backup',
            headers={'Authorization': f'Bearer {admin_token}'},
        )
        self.assertEqual(created.status_code, 200, created.headers.get('Content-Disposition'))
        disposition = created.headers.get('Content-Disposition') or ''
        self.assertIn('attachment', disposition.lower())
        self.assertGreater(len(created.data), 100)

        forbidden = self.client.post(
            '/api/user/backup',
            headers={'Authorization': f'Bearer {operator_token}'},
        )
        self.assertEqual(forbidden.status_code, 403, forbidden.get_data(as_text=True))
        message = ((forbidden.get_json() or {}).get('message') or '').lower()
        self.assertIn('admin', message)

    def test_previously_hardcoded_lists_return_saved_rows_only(self):
        from flask_jwt_extended import create_access_token
        from extensions import db
        from models import User
        from models.farmer import FarmerContract
        from models.gst_filing import GstFilingRecord

        with app.app_context():
            user = User.query.filter_by(is_active=True).first()
            if not user:
                self.skipTest('No mill user in the database')
            token = create_access_token(identity=str(user.id))
            contract_count = FarmerContract.query.count()
            filing_count = GstFilingRecord.query.count()

        first = self.client.get(
            '/api/farmer/contracts?status=all',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(first.status_code, 200, first.get_data(as_text=True))
        first_rows = (first.get_json() or {}).get('contracts') or []
        self.assertEqual(len(first_rows), contract_count)

        second = self.client.get(
            '/api/farmer/contracts?status=all',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(len((second.get_json() or {}).get('contracts') or []), len(first_rows))

        listed = self.client.get(
            '/api/compliance/gst/filings',
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(listed.status_code, 200, listed.get_data(as_text=True))
        existing = (listed.get_json() or {}).get('filings') or []
        self.assertEqual(len(existing), filing_count)
        marker = 'TEST-EMPTY-LIST'
        created = self.client.post(
            '/api/compliance/gst/filings',
            json={'form': marker, 'due_date': '2026-10-11', 'amount': 0, 'notes': 'test row'},
            headers={'Authorization': f'Bearer {token}'},
        )
        self.assertEqual(created.status_code, 201, created.get_data(as_text=True))
        created_id = ((created.get_json() or {}).get('filing') or {}).get('id')
        again = self.client.get(
            '/api/compliance/gst/filings',
            headers={'Authorization': f'Bearer {token}'},
        )
        again_rows = (again.get_json() or {}).get('filings') or []
        self.assertEqual(len(again_rows), filing_count + 1)
        self.assertTrue(any(row.get('form') == marker for row in again_rows))
        with app.app_context():
            row = GstFilingRecord.query.get(created_id)
            if row:
                db.session.delete(row)
                db.session.commit()

    def test_lookups_operator_cannot_create_and_inactive_hidden(self):
        from flask_jwt_extended import create_access_token
        from extensions import db
        from models.lookup import LookupOption
        from models.user import User
        from services.access_control import ensure_role_permissions
        from services.demo_users import ensure_demo_users
        from services.lookup_service import ensure_lookup_options

        with app.app_context():
            db.create_all()
            ensure_demo_users()
            ensure_role_permissions()
            ensure_lookup_options()
            operator = User.query.filter_by(username='operator').first()
            admin = User.query.filter_by(username='admin').first()
            self.assertIsNotNone(operator)
            self.assertIsNotNone(admin)
            op_token = create_access_token(identity=str(operator.id))
            ad_token = create_access_token(identity=str(admin.id))
            row = LookupOption.query.filter_by(
                group_key='product_type',
                value='zz_inactive_test',
            ).first()
            if not row:
                row = LookupOption(
                    group_key='product_type',
                    value='zz_inactive_test',
                    label_en='Inactive test',
                    label_hi='Inactive test',
                    label_te='Inactive test',
                    sort_order=99,
                    is_active=False,
                    is_locked=False,
                )
                db.session.add(row)
            else:
                row.is_active = False
            db.session.commit()

        forbidden = self.client.post(
            '/api/lookups',
            json={'group_key': 'product_type', 'value': 'zz_operator_create', 'label_en': 'Nope'},
            headers={'Authorization': f'Bearer {op_token}'},
        )
        self.assertEqual(forbidden.status_code, 403, forbidden.get_data(as_text=True))

        listed = self.client.get(
            '/api/lookups?group=product_type',
            headers={'Authorization': f'Bearer {op_token}'},
        )
        self.assertEqual(listed.status_code, 200, listed.get_data(as_text=True))
        values = [item.get('value') for item in (listed.get_json() or {}).get('options', [])]
        self.assertNotIn('zz_inactive_test', values)
        self.assertTrue(values, 'active product types should be seeded')

        admin_list = self.client.get(
            '/api/lookups/admin?group=product_type',
            headers={'Authorization': f'Bearer {ad_token}'},
        )
        self.assertEqual(admin_list.status_code, 200, admin_list.get_data(as_text=True))
        admin_values = [item.get('value') for item in (admin_list.get_json() or {}).get('options', [])]
        self.assertIn('zz_inactive_test', admin_values)


if __name__ == '__main__':
    unittest.main()
