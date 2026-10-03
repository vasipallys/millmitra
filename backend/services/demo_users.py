"""Idempotent demo mill accounts for local/dev SQLite."""
from extensions import db
from models.user import User

DEMO_USERS = (
    {
        'username': 'admin',
        'email': 'admin@ricemill.com',
        'password': 'admin123',
        'first_name': 'System',
        'last_name': 'Administrator',
        'role': 'admin',
        'department': 'Management',
    },
    {
        'username': 'manager',
        'email': 'manager@ricemill.com',
        'password': 'manager123',
        'first_name': 'Production',
        'last_name': 'Manager',
        'role': 'manager',
        'department': 'Production',
    },
    {
        'username': 'operator',
        'email': 'operator@ricemill.com',
        'password': 'operator123',
        'first_name': 'Mill',
        'last_name': 'Operator',
        'role': 'operator',
        'department': 'Production',
    },
    {
        'username': 'quality',
        'email': 'quality@ricemill.com',
        'password': 'quality123',
        'first_name': 'Quality',
        'last_name': 'Controller',
        'role': 'quality_control',
        'department': 'Quality',
    },
    {
        'username': 'sales',
        'email': 'sales@ricemill.com',
        'password': 'sales123',
        'first_name': 'Sales',
        'last_name': 'Representative',
        'role': 'sales',
        'department': 'Sales',
    },
    {
        'username': 'accountant',
        'email': 'accountant@ricemill.com',
        'password': 'accountant123',
        'first_name': 'Mill',
        'last_name': 'Accountant',
        'role': 'accountant',
        'department': 'Accounts',
    },
)


def ensure_demo_users():
    """Create any missing demo users. Does not reset existing passwords."""
    created = 0
    for spec in DEMO_USERS:
        existing = User.query.filter(
            (User.username == spec['username']) | (User.email == spec['email'])
        ).first()
        if existing:
            continue
        user = User(
            username=spec['username'],
            email=spec['email'],
            first_name=spec['first_name'],
            last_name=spec['last_name'],
            role=spec['role'],
            department=spec['department'],
            is_active=True,
            is_verified=True,
        )
        user.set_password(spec['password'])
        db.session.add(user)
        created += 1
    if created:
        db.session.commit()
    return created
