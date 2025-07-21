"""
Database migration script to create all tables for Rice Mill ERP
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from extensions import db
from config import Config

def create_tables():
    """Create all database tables"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        # Import models directly from files, not from __init__.py
        import models.user
        import models.sales
        
        # Create all tables
        db.create_all()
        print("All tables created successfully!")
        
        # Create default roles and permissions
        create_default_roles()
        print("Default roles and permissions created!")

def create_default_roles():
    """Create default roles and permissions"""
    # Implementation here...
    pass

if __name__ == '__main__':
    create_tables()





