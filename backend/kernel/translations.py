"""DB-stored translatable content with locale fallback."""

from services.tenant_scope import stamp_tenant, tq


def upsert_text(entity, record_id, field, lang, text, model=None):
    from models.metadata import TranslatedText
    model = model or TranslatedText
    lang = (lang or 'en')[:8]
    row = tq(model).filter_by(
        entity=entity, record_id=str(record_id), field=field, lang=lang,
    ).first()
    if row:
        row.text = text or ''
        return row
    row = stamp_tenant(model(
        entity=entity,
        record_id=str(record_id),
        field=field,
        lang=lang,
        text=text or '',
    ))
    from extensions import db
    db.session.add(row)
    return row


def get_text(entity, record_id, field, lang, fallback='en', model=None):
    from models.metadata import TranslatedText
    model = model or TranslatedText
    lang = (lang or 'en')[:8]
    query = tq(model).filter_by(entity=entity, record_id=str(record_id), field=field)
    row = query.filter_by(lang=lang).first()
    if row and (row.text or '').strip():
        return row.text
    if fallback and fallback != lang:
        row = query.filter_by(lang=fallback).first()
        if row:
            return row.text
    return None
