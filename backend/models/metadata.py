"""Tenant-scoped metadata for custom fields, forms, views, and translations."""

from datetime import datetime
import json

from extensions import db


class EntityDefinition(db.Model):
    __tablename__ = 'entity_definitions'
    __table_args__ = (db.UniqueConstraint('tenant_id', 'key', name='uq_entity_tenant_key'),)

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    key = db.Column(db.String(80), nullable=False)
    label = db.Column(db.String(160), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'key': self.key, 'label': self.label}


class FieldDefinition(db.Model):
    __tablename__ = 'field_definitions'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    entity_key = db.Column(db.String(80), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    field_type = db.Column(db.String(40), nullable=False, default='text')
    required = db.Column(db.Boolean, default=False)
    lookup_group = db.Column(db.String(80))
    translatable = db.Column(db.Boolean, default=False)
    label_en = db.Column(db.String(200), default='')
    label_hi = db.Column(db.String(200), default='')
    label_te = db.Column(db.String(200), default='')
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'entity_key': self.entity_key,
            'name': self.name,
            'field_type': self.field_type,
            'required': bool(self.required),
            'lookup_group': self.lookup_group,
            'translatable': bool(self.translatable),
            'label_en': self.label_en or self.name,
            'label_hi': self.label_hi or '',
            'label_te': self.label_te or '',
            'sort_order': self.sort_order,
        }


class FormLayout(db.Model):
    __tablename__ = 'form_layouts'
    __table_args__ = (db.UniqueConstraint('tenant_id', 'entity_key', name='uq_form_tenant_entity'),)

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    entity_key = db.Column(db.String(80), nullable=False)
    layout_json = db.Column(db.Text, default='{}')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        try:
            layout = json.loads(self.layout_json or '{}')
        except ValueError:
            layout = {}
        return {'id': self.id, 'entity_key': self.entity_key, 'layout': layout}


class ViewDefinition(db.Model):
    __tablename__ = 'view_definitions'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    entity_key = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    columns_json = db.Column(db.Text, default='[]')

    def to_dict(self):
        try:
            columns = json.loads(self.columns_json or '[]')
        except ValueError:
            columns = []
        return {'id': self.id, 'entity_key': self.entity_key, 'name': self.name, 'columns': columns}


class CustomFieldValue(db.Model):
    __tablename__ = 'custom_field_values'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'entity_key', 'record_id', 'field_name', name='uq_cfv_record_field'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    entity_key = db.Column(db.String(80), nullable=False, index=True)
    record_id = db.Column(db.String(64), nullable=False, index=True)
    field_name = db.Column(db.String(80), nullable=False)
    value_json = db.Column(db.Text, default='null')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def value(self):
        try:
            return json.loads(self.value_json)
        except ValueError:
            return self.value_json

    def to_dict(self):
        return {
            'id': self.id,
            'entity_key': self.entity_key,
            'record_id': self.record_id,
            'field_name': self.field_name,
            'value': self.value(),
        }


class TranslatedText(db.Model):
    __tablename__ = 'translated_texts'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'entity', 'record_id', 'field', 'lang', name='uq_tr_locale'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    entity = db.Column(db.String(80), nullable=False)
    record_id = db.Column(db.String(64), nullable=False)
    field = db.Column(db.String(80), nullable=False)
    lang = db.Column(db.String(12), nullable=False)
    text = db.Column(db.Text, default='')

    def to_dict(self):
        return {
            'id': self.id,
            'entity': self.entity,
            'record_id': self.record_id,
            'field': self.field,
            'lang': self.lang,
            'text': self.text,
        }


class DashboardLayout(db.Model):
    __tablename__ = 'dashboard_layouts'
    __table_args__ = (db.UniqueConstraint('tenant_id', 'user_id', name='uq_dash_tenant_user'),)

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    user_id = db.Column(db.Integer, index=True)
    widgets_json = db.Column(db.Text, default='[]')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def widgets(self):
        try:
            data = json.loads(self.widgets_json or '[]')
        except ValueError:
            return []
        return data if isinstance(data, list) else []

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'widgets': self.widgets()}


class MetadataRecord(db.Model):
    """Tenant-scoped rows for metadata-defined entities (standalone /forms/:entity)."""

    __tablename__ = 'metadata_records'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    entity_key = db.Column(db.String(80), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, values=None):
        payload = {
            'id': self.id,
            'entity_key': self.entity_key,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if values is not None:
            payload['values'] = values
        return payload
