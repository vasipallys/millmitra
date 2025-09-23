from app import create_app
from models.user import User

app = create_app()

with app.app_context():
    try:
        # Get all users
        users = User.query.all()
        print(f"Total users: {len(users)}")
        
        for user in users:
            print(f"\nUser ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Is active: {user.is_active}")
            print(f"Password hash: {user.password_hash[:20]}...")
            
    except Exception as e:
        print(f"Error accessing users table: {e}")
        import traceback
        traceback.print_exc()
