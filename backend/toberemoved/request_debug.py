import sys
import os
import threading
import time
import requests

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app
from extensions import db

# Set debug mode
os.environ['FLASK_ENV'] = 'development'

app = create_app()
app.config['DEBUG'] = True

# Add a route to check the database URI
@app.route('/debug/db-uri')
def debug_db_uri():
    # Check the current database URI
    if hasattr(db, 'engine') and db.engine:
        engine_url = str(db.engine.url)
    else:
        engine_url = 'Engine not initialized'
    
    return {
        'config_uri': app.config.get('SQLALCHEMY_DATABASE_URI'),
        'engine_url': engine_url
    }

print("Starting Flask app in debug mode...")
print(f"Initial Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Start the app in a separate thread
def run_app():
    app.run(host='127.0.0.1', port=5001, debug=False)

thread = threading.Thread(target=run_app)
thread.daemon = True
thread.start()

# Wait for the app to start
time.sleep(3)

# Make a request to the debug endpoint
try:
    response = requests.get('http://127.0.0.1:5001/debug/db-uri')
    print(f"Database URI after request: {response.json()}")
except Exception as e:
    print(f"Error making request: {e}")

# Make a login request to see if we can reproduce the error
try:
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'method': 'password'
    }
    response = requests.post('http://127.0.0.1:5001/api/auth/login', json=login_data)
    print(f"Login response status: {response.status_code}")
    print(f"Login response: {response.text}")
except Exception as e:
    print(f"Error making login request: {e}")

# Keep the script running for a bit
time.sleep(2)
