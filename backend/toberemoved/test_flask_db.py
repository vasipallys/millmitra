import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app
from extensions import db
from models.user import User

app = create_app()

print("Testing Flask database connection...")
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        # Try a simple query
        user_count = User.query.count()
        print(f"Successfully queried database. User count: {user_count}")
    except Exception as e:
        print(f"Failed to query database: {e}")
        import traceback
        traceback.print_exc()
