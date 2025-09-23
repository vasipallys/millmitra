import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from extensions import db
from app import create_app
from models.user import User

app = create_app()

with app.app_context():
    print("Checking users...")
    
    # Get all users
    users = User.query.all()
    
    for user in users:
        print(f"User ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print("---")
    
    print(f"Total users: {len(users)}")
