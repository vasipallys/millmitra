import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app
from extensions import db

# Set debug mode
os.environ['FLASK_ENV'] = 'development'

app = create_app()
app.config['DEBUG'] = True

if __name__ == '__main__':
    with app.app_context():
        print("Starting Flask app in debug mode...")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
    app.run(host='0.0.0.0', port=5000, debug=True)
