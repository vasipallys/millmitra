"""User-recorded GST checklist rows. Not government filings."""

from datetime import datetime

from extensions import db


class GstFilingRecord(db.Model):
    __tablename__ = 'gst_filing_records'

    id = db.Column(db.Integer, primary_key=True)
    form = db.Column(db.String(40), nullable=False)
    due_date = db.Column(db.String(20))
    amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)
    status = db.Column(db.String(30), default='recorded')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'form': self.form,
            'due_date': self.due_date,
            'amount': self.amount or 0,
            'notes': self.notes or '',
            'status': self.status or 'recorded',
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'created_by': self.created_by,
            'activity': f'{self.form} recorded in MillMitra',
            'date': (self.recorded_at.isoformat() if self.recorded_at else '')[:10],
        }
