"""Snapshots of reports the user generated from mill records."""

import json
from datetime import datetime

from extensions import db


class SavedReport(db.Model):
    __tablename__ = 'saved_reports'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(80))
    payload_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        payload = {}
        try:
            payload = json.loads(self.payload_json or '{}')
        except (TypeError, ValueError):
            payload = {}
        return {
            'id': self.id,
            'report_id': f'RPT-{self.id}',
            'title': self.title,
            'report_type': self.report_type,
            'generated_at': self.created_at.isoformat() if self.created_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'payload': payload,
        }
