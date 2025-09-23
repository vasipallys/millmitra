import sys
sys.path.insert(0, 'backend')
from app import create_app
from models.user import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print('Users in database:')
    for user in users:
        print(f'- {user.username} ({user.email}) - {user.role}')
