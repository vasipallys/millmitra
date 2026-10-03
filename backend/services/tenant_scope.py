"""Every tenant-owned read/write must go through these helpers."""

from flask import abort
from sqlalchemy import event

from extensions import db
from services.tenant_context import current_tenant_id


def tq(model):
    """Query scoped to the active tenant. A bare Model.query on mill data is a bug."""
    query = model.query
    tenant_id = current_tenant_id()
    if tenant_id and hasattr(model, 'tenant_id'):
        query = query.filter(model.tenant_id == tenant_id)
    return query


def t_get(model, ident):
    if ident is None:
        return None
    tenant_id = current_tenant_id()
    query = model.query.filter(model.id == ident)
    if tenant_id and hasattr(model, 'tenant_id'):
        query = query.filter(model.tenant_id == tenant_id)
    return query.first()


def t_get_or_404(model, ident):
    row = t_get(model, ident)
    if row is None:
        abort(404)
    return row


def stamp_tenant(obj, tenant_id=None):
    tid = tenant_id or current_tenant_id()
    if tid and hasattr(obj, 'tenant_id') and not getattr(obj, 'tenant_id', None):
        obj.tenant_id = tid
    return obj


_FLUSH_GUARD = False


def register_tenant_flush_guard():
    """Auto-stamp tenant_id on new mill rows when a request is bound."""
    global _FLUSH_GUARD
    if _FLUSH_GUARD:
        return
    _FLUSH_GUARD = True

    @event.listens_for(db.session, 'before_flush')
    def _stamp_new(session, flush_context, instances):
        tid = current_tenant_id()
        if not tid:
            return
        for obj in session.new:
            if hasattr(obj, 'tenant_id') and getattr(obj, 'tenant_id', None) in (None, ''):
                obj.tenant_id = tid
