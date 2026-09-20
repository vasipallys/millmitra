"""Shared request helpers."""
from flask_jwt_extended import get_jwt_identity
from models import User


def current_user_id():
    """Return the authenticated user id as an int when possible."""
    identity = get_jwt_identity()
    if identity is None:
        return None
    try:
        return int(identity)
    except (TypeError, ValueError):
        return identity


def current_user():
    """Load the authenticated User, or None."""
    user_id = current_user_id()
    if user_id is None:
        return None
    return User.query.get(user_id)


def parse_datetime(value, fallback=None):
    """Parse ISO / HTML datetime-local strings."""
    from datetime import datetime

    if not value:
        return fallback
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    for fmt in (
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    ):
        try:
            return datetime.strptime(text.replace('Z', ''), fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text.replace('Z', ''))
    except ValueError:
        return fallback
