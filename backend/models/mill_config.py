"""Singleton mill-wide settings (business, backup, AI flags)."""

from datetime import datetime

from extensions import db


class MillConfig(db.Model):
    __tablename__ = 'mill_config'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(36), index=True)
    data_json = db.Column(db.Text, default='{}')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
