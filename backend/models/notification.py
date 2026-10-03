"""Mill notifications persisted in SQLite (or the configured database)."""

from datetime import datetime

from extensions import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False, default='')
    category = db.Column(db.String(50))
    severity = db.Column(db.String(20), default='medium')
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(200))

    def to_dict(self):
        created = self.created_at.isoformat() if self.created_at else None
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'body': self.body or '',
            'message': self.body or '',
            'category': self.category,
            'severity': self.severity or 'medium',
            'priority': self.severity or 'medium',
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'read': self.read_at is not None,
            'created_at': created,
            'timestamp': created,
            'link': self.link,
            'action_url': self.link,
        }
