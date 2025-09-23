import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app

app = create_app()

print("Database URI from Flask app config:")
print(app.config['SQLALCHEMY_DATABASE_URI'])
print()

# Also check if there are any environment variables that might override this
print("Environment variables that might affect database connection:")
for key, value in os.environ.items():
    if 'DATABASE' in key.upper() or 'POSTGRES' in key.upper() or 'SQL' in key.upper():
        print(f"{key}: {value}")
