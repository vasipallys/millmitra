"""Safe SQLite/Postgres ALTER + default-tenant backfill. Never drops mill rows."""

import json
import logging

from sqlalchemy import inspect, text

from extensions import db
from models.tenant import STATUS_ACTIVE, Tenant, TenantMembership, new_tenant_id
from models.user import User

logger = logging.getLogger(__name__)

DEFAULT_SLUG = 'default'

TENANT_TABLES = (
    'farmers',
    'farmer_contracts',
    'paddy_procurements',
    'farmer_edit_requests',
    'paddy_stock',
    'product_stock',
    'stock_movements',
    'production_batches',
    'quality_tests',
    'customers',
    'sales_orders',
    'invoices',
    'payments',
    'payment_schedules',
    'expenses',
    'transactions',
    'notifications',
    'lookup_options',
    'mill_config',
    'gst_filing_records',
    'saved_reports',
    'role_permissions',
)


def _refresh_inspector():
    try:
        inspect(db.engine).clear_cache()
    except Exception:
        pass


def _inspector():
    _refresh_inspector()
    return inspect(db.engine)


def _table_names():
    return set(_inspector().get_table_names())


def _columns(table):
    if table not in _table_names():
        return set()
    return {col['name'] for col in _inspector().get_columns(table)}


def _indexes(table):
    if table not in _table_names():
        return set()
    names = set()
    for item in _inspector().get_indexes(table):
        if item.get('name'):
            names.add(item['name'])
    return names


def _add_column(table, column_sql):
    try:
        db.session.execute(text(f'ALTER TABLE {table} ADD COLUMN {column_sql}'))
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception('tenant_migrate_add_column_failed table=%s sql=%s', table, column_sql)
    _refresh_inspector()


def _ensure_index(table, name, column):
    if name in _indexes(table):
        return
    try:
        db.session.execute(text(f'CREATE INDEX IF NOT EXISTS {name} ON {table} ({column})'))
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception('tenant_migrate_index_failed table=%s name=%s', table, name)
    _refresh_inspector()


def _mill_name():
    if 'mill_config' not in _table_names():
        return 'MillMitra'
    try:
        row = db.session.execute(text('SELECT data_json FROM mill_config ORDER BY id ASC LIMIT 1')).first()
        if row and row[0]:
            data = json.loads(row[0])
            name = ((data or {}).get('business') or {}).get('companyName')
            if name and str(name).strip():
                return str(name).strip()
    except Exception:
        db.session.rollback()
    return 'MillMitra'


def ensure_default_tenant():
    tenant = Tenant.query.filter_by(slug=DEFAULT_SLUG).first()
    if tenant:
        return tenant
    tenant = Tenant(
        id=new_tenant_id(),
        name=_mill_name(),
        slug=DEFAULT_SLUG,
        status=STATUS_ACTIVE,
        timezone='Asia/Kolkata',
        locale='en',
        currency='INR',
    )
    db.session.add(tenant)
    db.session.commit()
    return tenant


def ensure_user_memberships(tenant):
    created = 0
    for user in User.query.all():
        existing = TenantMembership.query.filter_by(user_id=user.id, tenant_id=tenant.id).first()
        if existing:
            continue
        db.session.add(TenantMembership(
            user_id=user.id,
            tenant_id=tenant.id,
            role=user.role or 'operator',
        ))
        created += 1
    if created:
        db.session.commit()
    return created


def _backfill(table, tenant_id):
    if table not in _table_names() or 'tenant_id' not in _columns(table):
        return
    db.session.execute(
        text(f"UPDATE {table} SET tenant_id = :tid WHERE tenant_id IS NULL OR tenant_id = ''"),
        {'tid': tenant_id},
    )


def _rewrite_uniques():
    dialect = db.engine.dialect.name
    if dialect != 'sqlite':
        return
    try:
        if 'lookup_options' in _table_names():
            db.session.execute(text('DROP INDEX IF EXISTS uq_lookup_group_value'))
            db.session.execute(text(
                'CREATE UNIQUE INDEX IF NOT EXISTS uq_lookup_tenant_group_value '
                'ON lookup_options (tenant_id, group_key, value)'
            ))
        if 'role_permissions' in _table_names():
            db.session.execute(text('DROP INDEX IF EXISTS uq_role_permission'))
            db.session.execute(text(
                'CREATE UNIQUE INDEX IF NOT EXISTS uq_role_perm_tenant '
                'ON role_permissions (tenant_id, role, permission)'
            ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception('tenant_migrate_unique_rewrite_failed')


def migrate_tenant_schema():
    """Add tenant_id columns if missing, create default mill, backfill, index."""
    db.create_all()
    _refresh_inspector()
    if 'users' in _table_names() and 'is_platform_admin' not in _columns('users'):
        _add_column('users', 'is_platform_admin BOOLEAN DEFAULT 0')
    if 'users' in _table_names() and 'is_platform_admin' not in _columns('users'):
        raise RuntimeError('users.is_platform_admin is still missing after ALTER')

    for table in TENANT_TABLES:
        if table not in _table_names():
            continue
        if 'tenant_id' not in _columns(table):
            _add_column(table, 'tenant_id VARCHAR(36)')
        if 'tenant_id' in _columns(table):
            _ensure_index(table, f'ix_{table}_tenant_id', 'tenant_id')

    tenant = ensure_default_tenant()
    for table in TENANT_TABLES:
        _backfill(table, tenant.id)
    db.session.commit()
    _rewrite_uniques()
    ensure_user_memberships(tenant)
    return tenant
