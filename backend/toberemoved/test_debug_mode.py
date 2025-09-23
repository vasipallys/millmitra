import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Set the same environment variables as in run_debug.py
os.environ['FLASK_ENV'] = 'development'

from app import create_app
from extensions import db
from models.user import User

app = create_app()
app.config['DEBUG'] = True

print("Testing Flask database connection in debug mode...")
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"Debug mode: {app.config['DEBUG']}")
print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")

with app.app_context():
    try:
        # Try a simple query
        user_count = User.query.count()
        print(f"Successfully queried database. User count: {user_count}")
        
        # Try to find a specific user (like in the login function)
        user = User.query.filter(User.username == 'admin').first()
        print(f"Admin user found: {user.username if user else 'None'}")
        
    except Exception as e:
        print(f"Failed to query database: {e}")
        import traceback
        traceback.print_exc()
