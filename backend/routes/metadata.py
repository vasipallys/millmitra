"""Admin metadata APIs: entities, fields, form layouts, custom values, translations."""

import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from kernel.translations import get_text, upsert_text
from models.metadata import (
    CustomFieldValue,
    DashboardLayout,
    EntityDefinition,
    FieldDefinition,
    FormLayout,
    MetadataRecord,
    TranslatedText,
    ViewDefinition,
)
from services.access_control import has_permission
from services.tenant_scope import stamp_tenant, t_get, tq
from utils import current_user

metadata_bp = Blueprint('metadata', __name__)

BUILTIN_ENTITIES = (
    {'key': 'farmer', 'label': 'Farmer'},
    {'key': 'customer', 'label': 'Customer'},
    {'key': 'product', 'label': 'Product'},
)


def _admin():
    user = current_user()
    if not user or not has_permission(user, 'metadata'):
        return None
    return user


MAX_JSON = 16000
ALLOWED_FIELD_TYPES = frozenset(('text', 'number', 'boolean', 'select', 'date'))


def _parse_json(raw, default):
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw or json.dumps(default))
    except ValueError:
        return default


def _safe_key(value, default=''):
    text = ''.join(ch for ch in str(value or default) if ch.isalnum() or ch in ('_', '-'))
    return text[:80]


def _bounded_json(data):
    encoded = json.dumps(data, default=str)
    if len(encoded) > MAX_JSON:
        return None, 'payload too large'
    return encoded, None


@metadata_bp.route('/entities', methods=['GET'])
@jwt_required()
def list_entities():
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    stored = {row.key: row.to_dict() for row in tq(EntityDefinition).all()}
    items = []
    for item in BUILTIN_ENTITIES:
        items.append(stored.get(item['key'], item))
    for row in stored.values():
        if row['key'] not in {item['key'] for item in BUILTIN_ENTITIES}:
            items.append(row)
    return jsonify({'success': True, 'entities': items})


@metadata_bp.route('/entities', methods=['POST'])
@jwt_required()
def create_entity():
    if not _admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    payload = request.get_json() or {}
    key = _safe_key(payload.get('key')).lower()
    label = (payload.get('label') or key).strip()[:160]
    if not key:
        return jsonify({'success': False, 'message': 'key is required'}), 400
    existing = tq(EntityDefinition).filter_by(key=key).first()
    if existing:
        existing.label = label
        db.session.commit()
        return jsonify({'success': True, 'entity': existing.to_dict()})
    row = stamp_tenant(EntityDefinition(key=key, label=label))
    db.session.add(row)
    db.session.commit()
    return jsonify({'success': True, 'entity': row.to_dict()}), 201


@metadata_bp.route('/fields', methods=['GET'])
@jwt_required()
def list_fields():
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    entity = (request.args.get('entity') or '').strip()
    query = tq(FieldDefinition)
    if entity:
        query = query.filter_by(entity_key=entity)
    rows = query.order_by(FieldDefinition.sort_order, FieldDefinition.id).all()
    return jsonify({'success': True, 'fields': [row.to_dict() for row in rows]})


@metadata_bp.route('/fields', methods=['POST'])
@jwt_required()
def create_field():
    if not _admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    payload = request.get_json() or {}
    entity = _safe_key(payload.get('entity_key') or payload.get('entity'))
    name = _safe_key(payload.get('name'))
    if not entity or not name:
        return jsonify({'success': False, 'message': 'entity_key and name are required'}), 400
    field_type = payload.get('field_type') or 'text'
    if field_type not in ALLOWED_FIELD_TYPES:
        field_type = 'text'
    row = stamp_tenant(FieldDefinition(
        entity_key=entity,
        name=name,
        field_type=field_type,
        required=bool(payload.get('required')),
        lookup_group=payload.get('lookup_group') or None,
        translatable=bool(payload.get('translatable')),
        label_en=payload.get('label_en') or name,
        label_hi=payload.get('label_hi') or '',
        label_te=payload.get('label_te') or '',
        sort_order=int(payload.get('sort_order') or 0),
    ))
    db.session.add(row)
    db.session.commit()
    return jsonify({'success': True, 'field': row.to_dict()}), 201


@metadata_bp.route('/fields/<int:field_id>', methods=['PUT'])
@jwt_required()
def update_field(field_id):
    if not _admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    row = t_get(FieldDefinition, field_id)
    if not row:
        return jsonify({'success': False, 'message': 'Field not found'}), 404
    payload = request.get_json() or {}
    for key in ('name', 'field_type', 'lookup_group', 'label_en', 'label_hi', 'label_te'):
        if key in payload:
            setattr(row, key, payload.get(key))
    if 'required' in payload:
        row.required = bool(payload.get('required'))
    if 'translatable' in payload:
        row.translatable = bool(payload.get('translatable'))
    if 'sort_order' in payload:
        row.sort_order = int(payload.get('sort_order') or 0)
    db.session.commit()
    return jsonify({'success': True, 'field': row.to_dict()})


@metadata_bp.route('/fields/<int:field_id>', methods=['DELETE'])
@jwt_required()
def delete_field(field_id):
    if not _admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    row = t_get(FieldDefinition, field_id)
    if not row:
        return jsonify({'success': False, 'message': 'Field not found'}), 404
    db.session.delete(row)
    db.session.commit()
    return jsonify({'success': True})


@metadata_bp.route('/forms/<entity_key>', methods=['GET'])
@jwt_required()
def get_form(entity_key):
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    row = tq(FormLayout).filter_by(entity_key=entity_key).first()
    fields = tq(FieldDefinition).filter_by(entity_key=entity_key).order_by(
        FieldDefinition.sort_order, FieldDefinition.id
    ).all()
    layout = row.to_dict()['layout'] if row else {'fields': [item.to_dict() for item in fields]}
    if not layout.get('fields'):
        layout['fields'] = [item.to_dict() for item in fields]
    return jsonify({
        'success': True,
        'entity_key': entity_key,
        'layout': layout,
        'fields': [item.to_dict() for item in fields],
    })


@metadata_bp.route('/forms/<entity_key>', methods=['PUT'])
@jwt_required()
def save_form(entity_key):
    if not _admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    payload = request.get_json() or {}
    layout = payload.get('layout') or payload
    fields = layout.get('fields') if isinstance(layout, dict) else None
    if isinstance(fields, list):
        existing = {row.name: row for row in tq(FieldDefinition).filter_by(entity_key=entity_key).all()}
        seen = set()
        for index, item in enumerate(fields):
            name = (item.get('name') or '').strip()
            if not name:
                continue
            seen.add(name)
            row = existing.get(name)
            if row is None:
                row = stamp_tenant(FieldDefinition(entity_key=entity_key, name=name))
                db.session.add(row)
            row.field_type = item.get('field_type') or row.field_type or 'text'
            row.required = bool(item.get('required'))
            row.lookup_group = item.get('lookup_group') or None
            row.translatable = bool(item.get('translatable'))
            row.label_en = item.get('label_en') or item.get('label') or name
            row.label_hi = item.get('label_hi') or ''
            row.label_te = item.get('label_te') or ''
            row.sort_order = int(item.get('sort_order') if item.get('sort_order') is not None else index)
        for name, row in existing.items():
            if name not in seen:
                db.session.delete(row)
    row = tq(FormLayout).filter_by(entity_key=entity_key).first()
    if row is None:
        row = stamp_tenant(FormLayout(entity_key=entity_key))
        db.session.add(row)
    encoded, error = _bounded_json(layout)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    row.layout_json = encoded
    db.session.commit()
    return jsonify({'success': True, 'form': row.to_dict()})


@metadata_bp.route('/records/<entity_key>', methods=['GET'])
@jwt_required()
def list_records(entity_key):
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    entity = _safe_key(entity_key)
    rows = tq(MetadataRecord).filter_by(entity_key=entity).order_by(MetadataRecord.id.desc()).limit(100).all()
    ids = [str(row.id) for row in rows]
    values_by_record = {}
    if ids:
        for item in tq(CustomFieldValue).filter(
            CustomFieldValue.entity_key == entity,
            CustomFieldValue.record_id.in_(ids),
        ).all():
            values_by_record.setdefault(item.record_id, {})[item.field_name] = item.value()
    items = [row.to_dict(values_by_record.get(str(row.id), {})) for row in rows]
    return jsonify({'success': True, 'entity_key': entity, 'records': items})


@metadata_bp.route('/records/<entity_key>', methods=['POST'])
@jwt_required()
def create_record(entity_key):
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    entity = _safe_key(entity_key)
    payload = request.get_json() or {}
    values = payload.get('values') if isinstance(payload.get('values'), dict) else payload
    encoded, error = _bounded_json(values or {})
    if error:
        return jsonify({'success': False, 'message': error}), 400
    row = stamp_tenant(MetadataRecord(entity_key=entity))
    db.session.add(row)
    db.session.flush()
    for name, value in (values or {}).items():
        field = _safe_key(name)
        if not field:
            continue
        packed, pack_error = _bounded_json(value)
        if pack_error:
            return jsonify({'success': False, 'message': pack_error}), 400
        db.session.add(stamp_tenant(CustomFieldValue(
            entity_key=entity,
            record_id=str(row.id),
            field_name=field,
            value_json=packed,
        )))
    db.session.commit()
    stored = {
        item.field_name: item.value()
        for item in tq(CustomFieldValue).filter_by(entity_key=entity, record_id=str(row.id)).all()
    }
    return jsonify({'success': True, 'record': row.to_dict(stored)}), 201


@metadata_bp.route('/values/<entity_key>/<record_id>', methods=['GET'])
@jwt_required()
def get_values(entity_key, record_id):
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    rows = tq(CustomFieldValue).filter_by(
        entity_key=_safe_key(entity_key), record_id=str(record_id)[:80],
    ).all()
    return jsonify({
        'success': True,
        'values': {row.field_name: row.value() for row in rows},
        'items': [row.to_dict() for row in rows],
    })


@metadata_bp.route('/values/<entity_key>/<record_id>', methods=['PUT'])
@jwt_required()
def save_values(entity_key, record_id):
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    payload = request.get_json() or {}
    values = payload.get('values') if isinstance(payload.get('values'), dict) else payload
    saved = []
    entity = _safe_key(entity_key)
    rid = str(record_id)[:80]
    for name, value in (values or {}).items():
        field = _safe_key(name)
        if not field:
            continue
        row = tq(CustomFieldValue).filter_by(
            entity_key=entity, record_id=rid, field_name=field,
        ).first()
        encoded, error = _bounded_json(value)
        if error:
            return jsonify({'success': False, 'message': error}), 400
        if row:
            row.value_json = encoded
        else:
            row = stamp_tenant(CustomFieldValue(
                entity_key=entity,
                record_id=rid,
                field_name=field,
                value_json=encoded,
            ))
            db.session.add(row)
        saved.append(row)
    db.session.commit()
    return jsonify({'success': True, 'items': [row.to_dict() for row in saved]})


@metadata_bp.route('/translations', methods=['GET'])
@jwt_required()
def list_translations():
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    entity = request.args.get('entity')
    record_id = request.args.get('record_id')
    field = request.args.get('field')
    lang = request.args.get('lang') or 'en'
    if entity and record_id and field:
        return jsonify({
            'success': True,
            'text': get_text(entity, record_id, field, lang),
        })
    query = tq(TranslatedText)
    if entity:
        query = query.filter_by(entity=entity)
    rows = query.limit(200).all()
    return jsonify({'success': True, 'items': [row.to_dict() for row in rows]})


@metadata_bp.route('/translations', methods=['PUT'])
@jwt_required()
def save_translation():
    if not _admin():
        return jsonify({'success': False, 'message': 'You do not have access'}), 403
    payload = request.get_json() or {}
    row = upsert_text(
        payload.get('entity'),
        payload.get('record_id'),
        payload.get('field'),
        payload.get('lang') or 'en',
        payload.get('text') or '',
    )
    db.session.commit()
    return jsonify({'success': True, 'item': row.to_dict()})


@metadata_bp.route('/views', methods=['GET'])
@jwt_required()
def list_views():
    if not current_user():
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    entity = (request.args.get('entity') or '').strip()
    query = tq(ViewDefinition)
    if entity:
        query = query.filter_by(entity_key=entity)
    return jsonify({'success': True, 'views': [row.to_dict() for row in query.all()]})


@metadata_bp.route('/dashboard-layout', methods=['GET'])
@jwt_required()
def get_dashboard_layout():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    row = tq(DashboardLayout).filter_by(user_id=user.id).first()
    return jsonify({
        'success': True,
        'layout': row.to_dict() if row else {'widgets': []},
    })


@metadata_bp.route('/dashboard-layout', methods=['PUT'])
@jwt_required()
def save_dashboard_layout():
    user = current_user()
    if not user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    payload = request.get_json() or {}
    widgets = payload.get('widgets') if isinstance(payload.get('widgets'), list) else payload
    encoded, error = _bounded_json(widgets)
    if error:
        return jsonify({'success': False, 'message': error}), 400
    row = tq(DashboardLayout).filter_by(user_id=user.id).first()
    if row is None:
        row = stamp_tenant(DashboardLayout(user_id=user.id))
        db.session.add(row)
    row.widgets_json = encoded
    db.session.commit()
    return jsonify({'success': True, 'layout': row.to_dict()})
