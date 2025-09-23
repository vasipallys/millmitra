import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app
from extensions import db

# Set debug mode
os.environ['FLASK_ENV'] = 'development'

app = create_app()
app.config['DEBUG'] = True

print("Configuration at app creation:")
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"Debug mode: {app.config['DEBUG']}")
print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")

# Let's also check the engine configuration
with app.app_context():
    print()
    print("Engine configuration:")
    if hasattr(db, 'engine') and db.engine:
        print(f"Engine URL: {db.engine.url}")
    else:
        print("Engine not yet initialized")
    
    # Try to get the engine URL from the app config
    print(f"App config SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
