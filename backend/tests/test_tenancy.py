"""Tenant isolation for shared-schema Model A. Uses a temp SQLite file."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db


class TenancyIsolationTests(unittest.TestCase):
    def setUp(self):
        handle, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(handle)
        uri = 'sqlite:///' + self.db_path.replace('\\', '/')
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': uri,
            'SQLALCHEMY_ENGINE_OPTIONS': {'pool_pre_ping': True},
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

    def _login(self, username, password):
        response = self.client.post(
            '/api/auth/login',
            json={'username': username, 'password': password, 'method': 'password'},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        payload = response.get_json() or {}
        token = payload.get('access_token')
        self.assertTrue(token)
        return token, payload.get('user') or {}

    def _auth(self, token):
        return {'Authorization': f'Bearer {token}'}

    def _register_farmer(self, token, name, phone, district):
        response = self.client.post(
            '/api/farmer/register',
            json={
                'name': name,
                'phone': phone,
                'village': 'Village',
                'district': district,
                'state': 'Telangana',
            },
            headers=self._auth(token),
        )
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        return (response.get_json() or {}).get('farmer') or {}

    def test_demo_admin_lands_on_default_tenant(self):
        token, user = self._login('admin', 'admin123')
        self.assertTrue(token)
        self.assertEqual((user.get('tenant') or {}).get('slug'), 'default')
        with self.app.app_context():
            from flask_jwt_extended import decode_token
            from models.tenant import TenantMembership
            claims = decode_token(token)
            tenant_id = claims.get('tenant_id')
            self.assertTrue(tenant_id)
            self.assertEqual(tenant_id, (user.get('tenant') or {}).get('id'))
            membership = TenantMembership.query.filter_by(
                user_id=user.get('id'),
                tenant_id=tenant_id,
            ).first()
            self.assertIsNotNone(membership)
        mine = self.client.get('/api/tenants/mine', headers=self._auth(token))
        self.assertEqual(mine.status_code, 200)
        slugs = [row.get('slug') for row in (mine.get_json() or {}).get('tenants', [])]
        self.assertIn('default', slugs)

    def test_tenant_a_cannot_read_or_list_tenant_b(self):
        token_a, _ = self._login('admin', 'admin123')
        farmer_a = self._register_farmer(token_a, 'Farmer A', '9000000001', 'Nizamabad')

        created = self.client.post(
            '/api/tenants',
            json={
                'name': 'Mill B',
                'slug': 'mill-b',
                'username': 'adminb',
                'password': 'adminb123',
                'email': 'adminb@ricemill.com',
            },
        )
        self.assertEqual(created.status_code, 201, created.get_data(as_text=True))

        token_b, user_b = self._login('adminb', 'adminb123')
        self.assertEqual((user_b.get('tenant') or {}).get('slug'), 'mill-b')
        farmer_b = self._register_farmer(token_b, 'Farmer B', '9000000002', 'Karimnagar')

        listed_a = self.client.get('/api/farmer/list', headers=self._auth(token_a))
        self.assertEqual(listed_a.status_code, 200, listed_a.get_data(as_text=True))
        names_a = [row.get('name') for row in (listed_a.get_json() or {}).get('farmers', [])]
        self.assertIn('Farmer A', names_a)
        self.assertNotIn('Farmer B', names_a)

        listed_b = self.client.get('/api/farmer/list', headers=self._auth(token_b))
        names_b = [row.get('name') for row in (listed_b.get_json() or {}).get('farmers', [])]
        self.assertIn('Farmer B', names_b)
        self.assertNotIn('Farmer A', names_b)

        own = self.client.get(f"/api/farmer/{farmer_a['id']}", headers=self._auth(token_a))
        self.assertEqual(own.status_code, 200)

        leaked = self.client.get(f"/api/farmer/{farmer_b['id']}", headers=self._auth(token_a))
        self.assertEqual(leaked.status_code, 404, leaked.get_data(as_text=True))

        option = self.client.post(
            '/api/lookups',
            json={'group_key': 'product_type', 'value': 'zz_tenant_b_only', 'label_en': 'B only'},
            headers=self._auth(token_b),
        )
        self.assertIn(option.status_code, (200, 201), option.get_data(as_text=True))

        lookups_a = self.client.get(
            '/api/lookups?group=product_type',
            headers=self._auth(token_a),
        )
        values_a = [row.get('value') for row in (lookups_a.get_json() or {}).get('options', [])]
        self.assertNotIn('zz_tenant_b_only', values_a)

        lookups_b = self.client.get(
            '/api/lookups?group=product_type',
            headers=self._auth(token_b),
        )
        values_b = [row.get('value') for row in (lookups_b.get_json() or {}).get('options', [])]
        self.assertIn('zz_tenant_b_only', values_b)


class LegacySqliteLoginTests(unittest.TestCase):
    """Existing mill SQLite before tenant columns must migrate and still login."""

    def tearDown(self):
        if getattr(self, 'app', None):
            with self.app.app_context():
                db.session.remove()
                db.engine.dispose()
        path = getattr(self, 'db_path', None)
        if path:
            try:
                os.remove(path)
            except OSError:
                pass

    def test_login_after_existing_sqlite_without_tenant_columns(self):
        import sqlite3
        from werkzeug.security import generate_password_hash

        handle, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(handle)
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            '''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                email VARCHAR(120) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                phone VARCHAR(20),
                role VARCHAR(50),
                department VARCHAR(50),
                is_active BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 1,
                last_login DATETIME,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until DATETIME,
                voice_print_data TEXT,
                face_encoding TEXT,
                fingerprint_data TEXT,
                preferences TEXT,
                dashboard_layout TEXT,
                notification_settings TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
            '''
        )
        conn.execute(
            '''
            INSERT INTO users (
                username, email, password_hash, first_name, last_name,
                role, department, is_active, is_verified
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                'admin',
                'admin@ricemill.com',
                generate_password_hash('admin123'),
                'System',
                'Administrator',
                'admin',
                'Management',
                1,
                1,
            ),
        )
        conn.commit()
        conn.close()

        uri = 'sqlite:///' + self.db_path.replace('\\', '/')
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': uri,
            'SQLALCHEMY_ENGINE_OPTIONS': {'pool_pre_ping': True},
        })
        client = self.app.test_client()
        with self.app.app_context():
            from models.user import User
            admin = User.query.filter_by(username='admin').one()
            self.assertTrue(admin.is_active)
            self.assertGreaterEqual(User.query.count(), 1)

        response = client.post(
            '/api/auth/login',
            json={'username': 'admin', 'password': 'admin123', 'method': 'password'},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        payload = response.get_json() or {}
        token = payload.get('access_token')
        user = payload.get('user') or {}
        self.assertTrue(token)
        self.assertEqual((user.get('tenant') or {}).get('slug'), 'default')

        with self.app.app_context():
            from flask_jwt_extended import decode_token
            from models.tenant import TenantMembership
            claims = decode_token(token)
            tenant_id = claims.get('tenant_id')
            self.assertTrue(tenant_id)
            self.assertEqual(tenant_id, (user.get('tenant') or {}).get('id'))
            membership = TenantMembership.query.filter_by(
                user_id=user.get('id'),
                tenant_id=tenant_id,
            ).first()
            self.assertIsNotNone(membership)


if __name__ == '__main__':
    unittest.main()
