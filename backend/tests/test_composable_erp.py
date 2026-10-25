"""Kernel, metadata, translations, IIoT, and optional per-tenant SQLite router."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db


class ComposableErpTests(unittest.TestCase):
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

    def _login(self, username='admin', password='admin123'):
        response = self.client.post(
            '/api/auth/login',
            json={'username': username, 'password': password, 'method': 'password'},
        )
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        payload = response.get_json() or {}
        return payload.get('access_token'), payload.get('user') or {}

    def _auth(self, token):
        return {'Authorization': 'Bearer %s' % token}

    def test_plugin_registration_keeps_farmer_urls(self):
        with self.app.app_context():
            kernel = self.app.extensions.get('millmitra_kernel')
            self.assertIsNotNone(kernel)
            self.assertIn('farmers', kernel.modules)
            self.assertIn('inventory', kernel.modules)
            self.assertIn('metadata', kernel.modules)
            self.assertIn('iiot', kernel.modules)
        token, _ = self._login()
        response = self.client.get('/api/farmer/list', headers=self._auth(token))
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        inventory = self.client.get('/api/inventory/paddy', headers=self._auth(token))
        self.assertIn(inventory.status_code, (200, 404))

    def test_custom_field_crud_tenant_isolation(self):
        token, _ = self._login()
        headers = self._auth(token)
        created = self.client.post('/api/metadata/fields', json={
            'entity_key': 'farmer',
            'name': 'soil_type',
            'field_type': 'text',
            'label_en': 'Soil type',
            'required': False,
        }, headers=headers)
        self.assertEqual(created.status_code, 201, created.get_data(as_text=True))
        saved = self.client.put('/api/metadata/values/farmer/1', json={
            'values': {'soil_type': 'black'},
        }, headers=headers)
        self.assertEqual(saved.status_code, 200, saved.get_data(as_text=True))
        got = self.client.get('/api/metadata/values/farmer/1', headers=headers)
        self.assertEqual((got.get_json() or {}).get('values', {}).get('soil_type'), 'black')

        with self.app.app_context():
            from models.tenant import Tenant, TenantMembership
            from models.user import User
            other = Tenant(name='Other mill', slug='other-mill')
            db.session.add(other)
            db.session.flush()
            admin = User.query.filter_by(username='admin').first()
            db.session.add(TenantMembership(user_id=admin.id, tenant_id=other.id, role='admin'))
            db.session.commit()
            other_id = other.id
        switched = self.client.get(
            '/api/metadata/values/farmer/1',
            headers={**headers, 'X-Tenant-ID': other_id},
        )
        self.assertEqual(switched.status_code, 200, switched.get_data(as_text=True))
        self.assertEqual((switched.get_json() or {}).get('values') or {}, {})

    def test_translation_fallback(self):
        token, _ = self._login()
        headers = self._auth(token)
        put = self.client.put('/api/metadata/translations', json={
            'entity': 'product',
            'record_id': '9',
            'field': 'description',
            'lang': 'en',
            'text': 'Sona Masuri rice',
        }, headers=headers)
        self.assertEqual(put.status_code, 200, put.get_data(as_text=True))
        with self.app.app_context():
            from kernel.translations import get_text
            from services.tenant_context import bind_tenant
            from models.user import User
            from flask import Flask  # noqa: F401
            with self.app.test_request_context():
                admin = User.query.filter_by(username='admin').first()
                bind_tenant(admin, '/api/metadata')
                self.assertEqual(get_text('product', '9', 'description', 'ur'), 'Sona Masuri rice')
                self.assertEqual(get_text('product', '9', 'description', 'en'), 'Sona Masuri rice')

    def test_ingest_requires_device_token(self):
        missing = self.client.post('/api/iiot/ingest', json={'metric': 'temp', 'value': 40})
        self.assertEqual(missing.status_code, 401)
        ok = self.client.post(
            '/api/iiot/ingest',
            json={'metric': 'dryer_temp_c', 'value': 51.2},
            headers={'X-Device-Token': 'demo-device-token'},
        )
        self.assertEqual(ok.status_code, 201, ok.get_data(as_text=True))

    def test_discrepancy_create_and_resolve(self):
        token, _ = self._login()
        headers = self._auth(token)
        sensor = self.client.post(
            '/api/iiot/ingest',
            json={'metric': 'moisture_pct', 'value': 12.0},
            headers={'X-Device-Token': 'demo-device-token'},
        )
        self.assertEqual(sensor.status_code, 201, sensor.get_data(as_text=True))
        manual = self.client.post('/api/iiot/manual', json={
            'device_id': 'mill-dryer-1',
            'metric': 'moisture_pct',
            'value': 18.0,
            'reason': 'lab sample',
        }, headers=headers)
        self.assertEqual(manual.status_code, 201, manual.get_data(as_text=True))
        listed = self.client.get('/api/iiot/discrepancies', headers=headers)
        rows = (listed.get_json() or {}).get('discrepancies') or []
        open_rows = [row for row in rows if row.get('status') == 'open']
        self.assertTrue(open_rows)
        resolved = self.client.post(
            '/api/iiot/discrepancies/%s/resolve' % open_rows[0]['id'],
            json={'resolution': 'accepted lab'},
            headers=headers,
        )
        self.assertEqual(resolved.status_code, 200, resolved.get_data(as_text=True))
        self.assertEqual((resolved.get_json() or {}).get('discrepancy', {}).get('status'), 'resolved')

    def test_iiot_tenant_isolation(self):
        token, _ = self._login()
        self.client.post(
            '/api/iiot/ingest',
            json={'metric': 'motor_amps', 'value': 9.1},
            headers={'X-Device-Token': 'demo-device-token'},
        )
        with self.app.app_context():
            from models.tenant import Tenant, TenantMembership
            from models.user import User
            other = Tenant(name='Second mill', slug='second-mill')
            db.session.add(other)
            db.session.flush()
            admin = User.query.filter_by(username='admin').first()
            db.session.add(TenantMembership(user_id=admin.id, tenant_id=other.id, role='admin'))
            db.session.commit()
            other_id = other.id
        listed = self.client.get(
            '/api/iiot/readings',
            headers={**self._auth(token), 'X-Tenant-ID': other_id},
        )
        self.assertEqual(listed.status_code, 200, listed.get_data(as_text=True))
        self.assertEqual((listed.get_json() or {}).get('readings') or [], [])

    def test_tenant_database_router_second_sqlite(self):
        handle, other_path = tempfile.mkstemp(suffix='-tenant.db')
        os.close(handle)
        other_uri = 'sqlite:///' + other_path.replace('\\', '/')
        try:
            with self.app.app_context():
                from kernel.tenant_router import TenantDatabaseRouter
                from models.metadata import CustomFieldValue
                from models.tenant import Tenant
                tenant = Tenant(name='Routed mill', slug='routed-mill', db_url=other_uri)
                db.session.add(tenant)
                db.session.commit()
                router = TenantDatabaseRouter()
                engine = router.engine_for(tenant)
                self.assertIsNot(engine, db.engine)
                session = router.session_for(tenant)
                row = CustomFieldValue(
                    tenant_id=tenant.id,
                    entity_key='farmer',
                    record_id='77',
                    field_name='note',
                    value_json='"routed"',
                )
                session.add(row)
                session.commit()
                found = session.query(CustomFieldValue).filter_by(record_id='77').first()
                self.assertIsNotNone(found)
                self.assertEqual(found.value(), 'routed')
                shared = CustomFieldValue.query.filter_by(record_id='77').first()
                self.assertIsNone(shared)
                session.remove()
                engine.dispose()
        finally:
            try:
                os.remove(other_path)
            except OSError:
                pass

    def _other_tenant(self, token):
        with self.app.app_context():
            from models.tenant import Tenant, TenantMembership
            from models.user import User
            other = Tenant(name='Locked mill', slug='locked-mill-%s' % os.urandom(3).hex())
            db.session.add(other)
            db.session.flush()
            admin = User.query.filter_by(username='admin').first()
            db.session.add(TenantMembership(user_id=admin.id, tenant_id=other.id, role='admin'))
            db.session.commit()
            return other.id

    def test_cross_tenant_metadata_write_denied(self):
        token, _ = self._login()
        headers = self._auth(token)
        self.client.put('/api/metadata/values/farmer/1', json={'values': {'soil': 'black'}}, headers=headers)
        other_id = self._other_tenant(token)
        switched = {**headers, 'X-Tenant-ID': other_id}
        got = self.client.get('/api/metadata/values/farmer/1', headers=switched)
        self.assertEqual((got.get_json() or {}).get('values') or {}, {})
        self.client.put('/api/metadata/values/farmer/1', json={'values': {'soil': 'hacked'}}, headers=switched)
        original = self.client.get('/api/metadata/values/farmer/1', headers=headers)
        self.assertEqual((original.get_json() or {}).get('values', {}).get('soil'), 'black')

    def test_cross_tenant_form_layout_isolated(self):
        token, _ = self._login()
        headers = self._auth(token)
        save = self.client.put('/api/metadata/forms/farmer', json={
            'layout': {'fields': [{'name': 'plot_code', 'label_en': 'Plot', 'field_type': 'text'}]},
        }, headers=headers)
        self.assertEqual(save.status_code, 200, save.get_data(as_text=True))
        other_id = self._other_tenant(token)
        other = self.client.get('/api/metadata/forms/farmer', headers={**headers, 'X-Tenant-ID': other_id})
        fields = (other.get_json() or {}).get('fields') or []
        self.assertFalse(any(item.get('name') == 'plot_code' for item in fields))

    def test_device_list_never_returns_token(self):
        token, _ = self._login()
        listed = self.client.get('/api/iiot/devices?include_token=1', headers=self._auth(token))
        self.assertEqual(listed.status_code, 200)
        for device in (listed.get_json() or {}).get('devices') or []:
            self.assertNotIn('token', device)

    def test_ingest_cannot_use_foreign_tenant_device(self):
        token, _ = self._login()
        with self.app.app_context():
            from models.iiot import Device
            from models.tenant import Tenant, TenantMembership
            from models.user import User
            other = Tenant(name='IoT mill', slug='iot-mill')
            db.session.add(other)
            db.session.flush()
            admin = User.query.filter_by(username='admin').first()
            db.session.add(TenantMembership(user_id=admin.id, tenant_id=other.id, role='admin'))
            foreign = Device(
                tenant_id=other.id,
                device_id='foreign-dryer',
                name='Foreign',
                token='foreign-secret-token',
                is_active=True,
            )
            db.session.add(foreign)
            db.session.commit()
        spoof = self.client.post(
            '/api/iiot/ingest',
            json={'metric': 'temp', 'value': 1, 'device_id': 'foreign-dryer'},
            headers={'X-Device-Token': 'demo-device-token'},
        )
        self.assertEqual(spoof.status_code, 201)
        self.assertEqual((spoof.get_json() or {}).get('reading', {}).get('device_id'), 'mill-dryer-1')
        listed = self.client.get('/api/iiot/readings', headers=self._auth(token))
        ids = {row.get('device_id') for row in (listed.get_json() or {}).get('readings') or []}
        self.assertNotIn('foreign-dryer', ids)

    def test_operator_cannot_resolve_or_admin_metadata(self):
        token, _ = self._login('operator', 'operator123')
        headers = self._auth(token)
        denied = self.client.post('/api/metadata/fields', json={
            'entity_key': 'farmer', 'name': 'blocked',
        }, headers=headers)
        self.assertEqual(denied.status_code, 403)
        resolve = self.client.post('/api/iiot/discrepancies/1/resolve', json={'resolution': 'no'}, headers=headers)
        self.assertEqual(resolve.status_code, 403)

    def test_ingest_rejects_invalid_value_and_manual_source(self):
        bad = self.client.post(
            '/api/iiot/ingest',
            json={'metric': 'temp', 'value': 'hot', 'source': 'manual'},
            headers={'X-Device-Token': 'demo-device-token'},
        )
        self.assertEqual(bad.status_code, 400)
        ok = self.client.post(
            '/api/iiot/ingest',
            json={'metric': 'temp', 'value': 40, 'source': 'manual'},
            headers={'X-Device-Token': 'demo-device-token'},
        )
        self.assertEqual(ok.status_code, 201)
        self.assertEqual((ok.get_json() or {}).get('reading', {}).get('source'), 'sensor')

    def test_cross_tenant_records_isolated(self):
        token, _ = self._login()
        headers = self._auth(token)
        created = self.client.post('/api/metadata/records/inspection', json={
            'values': {'note': 'default-tenant'},
        }, headers=headers)
        self.assertEqual(created.status_code, 201, created.get_data(as_text=True))
        other_id = self._other_tenant(token)
        other = self.client.get(
            '/api/metadata/records/inspection',
            headers={**headers, 'X-Tenant-ID': other_id},
        )
        self.assertEqual((other.get_json() or {}).get('records') or [], [])

    def test_dynamic_record_roundtrip(self):
        token, _ = self._login()
        headers = self._auth(token)
        created = self.client.post('/api/metadata/records/inspection', json={
            'values': {'note': 'ok', 'score': 9},
        }, headers=headers)
        self.assertEqual(created.status_code, 201, created.get_data(as_text=True))
        listed = self.client.get('/api/metadata/records/inspection', headers=headers)
        records = (listed.get_json() or {}).get('records') or []
        self.assertTrue(records)
        self.assertEqual(records[0]['values'].get('note'), 'ok')

    def test_two_sqlite_router_urls(self):
        handle_a, path_a = tempfile.mkstemp(suffix='-a.db')
        handle_b, path_b = tempfile.mkstemp(suffix='-b.db')
        os.close(handle_a)
        os.close(handle_b)
        try:
            with self.app.app_context():
                from kernel.tenant_router import TenantDatabaseRouter
                from models.metadata import MetadataRecord
                from models.tenant import Tenant
                router = TenantDatabaseRouter()
                a = Tenant(name='A', slug='sqlite-a', db_url='sqlite:///' + path_a.replace('\\', '/'))
                b = Tenant(name='B', slug='sqlite-b', db_url='sqlite:///' + path_b.replace('\\', '/'))
                db.session.add_all([a, b])
                db.session.commit()
                sa = router.session_for(a)
                sb = router.session_for(b)
                sa.add(MetadataRecord(tenant_id=a.id, entity_key='note'))
                sb.add(MetadataRecord(tenant_id=b.id, entity_key='note'))
                sa.commit()
                sb.commit()
                self.assertEqual(sa.query(MetadataRecord).count(), 1)
                self.assertEqual(sb.query(MetadataRecord).count(), 1)
                sa.remove()
                sb.remove()
        finally:
            for path in (path_a, path_b):
                try:
                    os.remove(path)
                except OSError:
                    pass

    def test_migrate_copy_of_live_sqlite(self):
        live = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'rice_mill_erp.db')
        if not os.path.isfile(live):
            self.skipTest('live sqlite missing')
        handle, copy_path = tempfile.mkstemp(suffix='-copy.db')
        os.close(handle)
        try:
            with open(live, 'rb') as src, open(copy_path, 'wb') as dest:
                dest.write(src.read())
            uri = 'sqlite:///' + copy_path.replace('\\', '/')
            app = create_app({
                'TESTING': True,
                'SQLALCHEMY_DATABASE_URI': uri,
                'MQTT_BROKER_URL': None,
                'REDIS_URL': None,
            })
            with app.app_context():
                from services.tenant_migration import migrate_tenant_schema
                migrate_tenant_schema()
                self.assertIn('machine_telemetry', db.metadata.tables)
        finally:
            try:
                os.remove(copy_path)
            except OSError:
                pass


if __name__ == '__main__':
    unittest.main()

