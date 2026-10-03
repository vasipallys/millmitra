"""Mill-wide settings, SQLite backups, and a once-a-minute backup checker."""

import json
import os
import re
import shutil
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path

from flask import current_app
from extensions import db
from models.mill_config import MillConfig
from services.access_control import normalize_role

DEFAULT_FOLDER = 'backups'
FOLDER_OK = re.compile(r'^[A-Za-z0-9._/-]+$')

DEFAULT_CONFIG = {
    'business': {
        'companyName': '',
        'gstNumber': '',
        'address': '',
        'phone': '',
        'email': '',
    },
    'backup': {
        'autoEnabled': False,
        'autoTime': '02:00',
        'folder': DEFAULT_FOLDER,
        'retentionDays': 30,
        'lastCleanupAt': None,
        'lastAutoBackupDate': None,
        'lastBackupAt': None,
    },
    'ai': {
        'voiceCommands': False,
        'predictiveAnalytics': False,
        'autoOptimization': False,
        'smartRecommendations': False,
        'showAiChip': False,
    },
    'notifications': {
        'emailAlerts': False,
        'inApp': True,
        'lowStockAlerts': True,
        'productionAlerts': True,
        'qualityAlerts': True,
        'smsAlerts': False,
    },
    'security': {
        'sessionTimeout': 30,
    },
}

_scheduler_started = False
_scheduler_lock = threading.Lock()


def can_manage_mill(user):
    return normalize_role(getattr(user, 'role', None)) in ('admin', 'manager')


def mail_configured(app=None):
    cfg = (app or current_app).config
    server = (cfg.get('MAIL_SERVER') or '').strip()
    username = (cfg.get('MAIL_USERNAME') or '').strip()
    return bool(server and username)


def _deep_merge(base, incoming):
    out = dict(base)
    if not isinstance(incoming, dict):
        return out
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _row():
    row = MillConfig.query.order_by(MillConfig.id.asc()).first()
    if row:
        return row
    row = MillConfig(data_json=json.dumps(DEFAULT_CONFIG), updated_at=datetime.utcnow())
    db.session.add(row)
    db.session.commit()
    return row


def get_mill_config():
    row = _row()
    try:
        stored = json.loads(row.data_json or '{}')
    except (TypeError, ValueError):
        stored = {}
    return _deep_merge(DEFAULT_CONFIG, stored if isinstance(stored, dict) else {})


def save_mill_config(updates, allowed_keys=None):
    current = get_mill_config()
    if not isinstance(updates, dict):
        return current
    incoming = updates
    if allowed_keys is not None:
        incoming = {key: updates[key] for key in allowed_keys if key in updates}
    merged = _deep_merge(current, incoming)
    if 'backup' in merged:
        merged['backup']['folder'] = sanitize_folder(merged['backup'].get('folder'))
        merged['backup']['autoTime'] = sanitize_time(merged['backup'].get('autoTime'))
        try:
            days = int(merged['backup'].get('retentionDays') or 30)
        except (TypeError, ValueError):
            days = 30
        merged['backup']['retentionDays'] = max(1, min(days, 3650))
    if 'ai' in merged:
        flags = merged['ai']
        flags['showAiChip'] = bool(
            flags.get('showAiChip')
            or flags.get('voiceCommands')
            or flags.get('smartRecommendations')
            or flags.get('predictiveAnalytics')
        )
    row = _row()
    row.data_json = json.dumps(merged)
    row.updated_at = datetime.utcnow()
    db.session.commit()
    return merged


def sanitize_time(value):
    text = str(value or '02:00').strip()
    try:
        parsed = datetime.strptime(text, '%H:%M')
        return parsed.strftime('%H:%M')
    except ValueError:
        return '02:00'


def sanitize_folder(value):
    text = str(value or DEFAULT_FOLDER).replace('\\', '/').strip().strip('/')
    if not text or '..' in text.split('/') or text.startswith('/') or not FOLDER_OK.match(text):
        return DEFAULT_FOLDER
    return text


def instance_dir(app=None):
    flask_app = app or current_app
    path = Path(flask_app.instance_path)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def sqlite_file_path(app=None):
    flask_app = app or current_app
    candidates = []
    try:
        database = db.engine.url.database
        if database:
            candidates.append(Path(database))
    except Exception:
        pass
    uri = flask_app.config.get('SQLALCHEMY_DATABASE_URI') or ''
    if uri.startswith('sqlite:///'):
        raw = uri[len('sqlite:///'):]
        if raw and raw != ':memory:':
            candidates.append(Path(raw))
    candidates.append(instance_dir(flask_app) / 'rice_mill_erp.db')
    for candidate in candidates:
        try:
            resolved = candidate if candidate.is_absolute() else (Path.cwd() / candidate)
            if resolved.exists() and resolved.is_file():
                return resolved.resolve()
        except OSError:
            continue
    expected = instance_dir(flask_app) / 'rice_mill_erp.db'
    return expected.resolve()


def backup_dir(app=None, folder=None):
    flask_app = app or current_app
    inst = instance_dir(flask_app)
    rel = sanitize_folder(folder if folder is not None else get_mill_config()['backup'].get('folder'))
    dest = (inst / rel).resolve()
    if inst not in dest.parents and dest != inst:
        dest = (inst / DEFAULT_FOLDER).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def format_bytes(size):
    if size is None:
        return None
    size = float(size)
    if size < 1024:
        return f'{int(size)} bytes'
    if size < 1024 * 1024:
        return f'{size / 1024:.1f} KB'
    return f'{size / (1024 * 1024):.2f} MB'


def _folder_size(path):
    total = 0
    if not path.exists():
        return 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                continue
    return total


def backup_status(app=None):
    flask_app = app or current_app
    cfg = get_mill_config()
    db_path = sqlite_file_path(flask_app)
    folder = backup_dir(flask_app, cfg['backup'].get('folder'))
    db_exists = db_path.exists() and db_path.is_file()
    db_size = db_path.stat().st_size if db_exists else None
    backups_size = _folder_size(folder)
    free = None
    try:
        free = shutil.disk_usage(str(folder)).free
    except OSError:
        free = None
    last_cleanup = cfg['backup'].get('lastCleanupAt')
    return {
        'database_path': str(db_path),
        'database_exists': db_exists,
        'database_size_bytes': db_size,
        'database_size_label': format_bytes(db_size) if db_exists else 'Database file not found',
        'backups_folder': str(folder),
        'backups_folder_relative': sanitize_folder(cfg['backup'].get('folder')),
        'backups_size_bytes': backups_size,
        'backups_size_label': format_bytes(backups_size),
        'disk_free_bytes': free,
        'disk_free_label': format_bytes(free) if free is not None else None,
        'auto_enabled': bool(cfg['backup'].get('autoEnabled')),
        'auto_time': cfg['backup'].get('autoTime') or '02:00',
        'retention_days': cfg['backup'].get('retentionDays') or 30,
        'last_backup_at': cfg['backup'].get('lastBackupAt'),
        'last_cleanup_at': last_cleanup,
        'last_cleanup_label': last_cleanup or 'Never',
    }


def _copy_sqlite(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    source = sqlite3.connect(str(src))
    target = sqlite3.connect(str(dest))
    try:
        source.backup(target)
    finally:
        target.close()
        source.close()


def create_backup_file(app=None):
    flask_app = app or current_app
    src = sqlite_file_path(flask_app)
    if not src.exists():
        return None, 'SQLite database file was not found'
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dest = backup_dir(flask_app) / f'rice_mill_erp_{stamp}.db'
    _copy_sqlite(src, dest)
    save_mill_config({'backup': {'lastBackupAt': datetime.now().isoformat(timespec='seconds')}})
    return dest, None


def copy_for_download(app=None):
    """Read-only copy streamed to the browser; stored in the default backups folder."""
    return create_backup_file(app)


def cleanup_old_backups(app=None, days=None):
    flask_app = app or current_app
    cfg = get_mill_config()
    try:
        keep = int(days if days is not None else cfg['backup'].get('retentionDays') or 30)
    except (TypeError, ValueError):
        keep = 30
    keep = max(1, keep)
    folder = backup_dir(flask_app)
    cutoff = datetime.now() - timedelta(days=keep)
    removed = 0
    for item in folder.glob('rice_mill_erp_*.db'):
        try:
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
        except OSError:
            continue
        if mtime < cutoff:
            try:
                item.unlink()
                removed += 1
            except OSError:
                continue
    stamp = datetime.now().isoformat(timespec='seconds')
    save_mill_config({'backup': {'lastCleanupAt': stamp, 'retentionDays': keep}})
    return {'removed': removed, 'last_cleanup_at': stamp, 'retention_days': keep}


def run_scheduled_backup(app):
    with app.app_context():
        cfg = get_mill_config()
        backup_cfg = cfg.get('backup') or {}
        if not backup_cfg.get('autoEnabled'):
            return False
        now = datetime.now()
        if now.strftime('%H:%M') != sanitize_time(backup_cfg.get('autoTime')):
            return False
        today = now.strftime('%Y-%m-%d')
        if backup_cfg.get('lastAutoBackupDate') == today:
            return False
        dest, error = create_backup_file(app)
        if error or dest is None:
            return False
        save_mill_config({'backup': {'lastAutoBackupDate': today}})
        cleanup_old_backups(app)
        return True


def start_backup_scheduler(app):
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return
        _scheduler_started = True

    def loop():
        while True:
            try:
                run_scheduled_backup(app)
            except Exception:
                pass
            threading.Event().wait(60)

    thread = threading.Thread(target=loop, name='millmitra-backup', daemon=True)
    thread.start()


def notification_writer_enabled(flag, default=True):
    flags = (get_mill_config().get('notifications') or {})
    if flag not in flags:
        return default
    return bool(flags.get(flag))
