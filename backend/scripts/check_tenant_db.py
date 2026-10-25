"""Postgres smoke check for shared-schema + optional RLS.

Not run in this workspace (no Postgres). Usage when DATABASE_URL is Postgres:

  python scripts/check_tenant_db.py

Checks:
- connect
- required composable tables exist
- tenant_id columns exist
- RLS enabled on machine_telemetry / custom_field_values when the server is Postgres
"""

import os
import sys

REQUIRED_TABLES = (
    'tenants',
    'entity_definitions',
    'field_definitions',
    'form_layouts',
    'custom_field_values',
    'translated_texts',
    'dashboard_layouts',
    'metadata_records',
    'iiot_devices',
    'machine_telemetry',
    'iiot_discrepancies',
)


def main():
    url = os.environ.get('DATABASE_URL') or ''
    if not url.startswith('postgres'):
        print('skip: DATABASE_URL is not Postgres; this script is not a SQLite check')
        return 2
    try:
        import psycopg
    except ImportError:
        print('skip: psycopg is not installed')
        return 2
    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )
            tables = {row[0] for row in cur.fetchall()}
            missing = [name for name in REQUIRED_TABLES if name not in tables]
            if missing:
                print('missing tables:', ', '.join(missing))
                return 1
            cur.execute(
                """
                SELECT table_name FROM information_schema.columns
                WHERE table_schema = 'public' AND column_name = 'tenant_id'
                """
            )
            with_tenant = {row[0] for row in cur.fetchall()}
            need = [name for name in REQUIRED_TABLES if name != 'tenants' and name not in with_tenant]
            if need:
                print('missing tenant_id:', ', '.join(need))
                return 1
            cur.execute(
                """
                SELECT relname, relrowsecurity FROM pg_class
                WHERE relname IN ('machine_telemetry', 'custom_field_values', 'farmers')
                """
            )
            for name, enabled in cur.fetchall():
                print('rls', name, bool(enabled))
    print('ok: postgres schema looks tenant-ready')
    print('not verified here: live RLS policies against two roles')
    return 0


if __name__ == '__main__':
    sys.exit(main())
