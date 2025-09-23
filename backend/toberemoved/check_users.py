from app import create_app
from models.user import User

app = create_app()

with app.app_context():
    try:
        # Check if users table exists and has records
        user_count = User.query.count()
        print(f"Users table accessible. Total users: {user_count}")
        
        if user_count > 0:
            # Get first user as sample
            first_user = User.query.first()
            print(f"Sample user: {first_user.username}")
            print(f"User ID: {first_user.id}")
            print(f"User role: {first_user.role}")
        else:
            print("No users found in the database.")
            
    except Exception as e:
        print(f"Error accessing users table: {e}")
        import traceback
        traceback.print_exc()
