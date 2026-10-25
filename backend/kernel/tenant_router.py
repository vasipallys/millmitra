"""Optional per-tenant SQLAlchemy engine. Default bind is the shared mill DB."""

import logging
import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from extensions import db
from services.tenant_context import current_tenant_id

logger = logging.getLogger(__name__)

_ALLOWED_PREFIXES = ('sqlite://', 'postgresql://', 'postgresql+psycopg://')


class TenantDatabaseRouter:
    def __init__(self):
        self._engines = {}
        self._sessions = {}
        self._lock = threading.Lock()

    def engine_for(self, tenant):
        url = (getattr(tenant, 'db_url', None) or '').strip()
        if not url:
            return db.engine
        if not url.startswith(_ALLOWED_PREFIXES):
            logger.warning('tenant_db_url_rejected')
            return db.engine
        with self._lock:
            engine = self._engines.get(url)
            if engine is None:
                engine = create_engine(url, future=True)
                db.Model.metadata.create_all(engine)
                self._engines[url] = engine
            return engine

    def session_for(self, tenant):
        engine = self.engine_for(tenant)
        if engine is db.engine:
            return db.session
        url = tenant.db_url
        with self._lock:
            session = self._sessions.get(url)
            if session is None:
                session = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=False))
                self._sessions[url] = session
            return session

    def bind_request(self, tenant):
        """Point the request session at tenant.db_url when set."""
        if not tenant or not (getattr(tenant, 'db_url', None) or '').strip():
            return db.engine
        engine = self.engine_for(tenant)
        db.session.bind = engine
        return engine


ROUTER = TenantDatabaseRouter()


def router_for_current():
    from models.tenant import Tenant
    tid = current_tenant_id()
    tenant = Tenant.query.get(tid) if tid else None
    return ROUTER, tenant


def register_tenant_router(app):
    """Reset Flask-SQLAlchemy bind after an optional per-tenant engine switch."""

    @app.teardown_request
    def _reset_bind(_exc):
        try:
            db.session.bind = None
        except Exception:
            pass
