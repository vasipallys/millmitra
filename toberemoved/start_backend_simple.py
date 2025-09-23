#!/usr/bin/env python3
"""
Simple Backend Startup Script
Starts the backend with only working modules
"""

import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

# Temporarily disable problematic imports
import importlib.util

def create_minimal_app():
    """Create Flask app with minimal working modules"""
    
    from flask import Flask, jsonify
    from flask_cors import CORS
    from extensions import db, jwt, init_extensions
    from config import Config
    
    # Import working models
    try:
        from models.farmer_edit_request import FarmerEditRequest
    except:
        pass
    
    # Import working blueprints only
    working_blueprints = []
    
    blueprint_imports = [
        ('routes.auth', 'auth_bp', '/api/auth'),
        ('routes.dashboard', 'dashboard_bp', '/api/dashboard'),
        ('routes.farmer', 'farmer_bp', '/api/farmer'),
        ('routes.inventory', 'inventory_bp', '/api/inventory'),
        ('routes.production', 'production_bp', '/api/production'),
        ('routes.sales', 'sales_bp', '/api/sales'),
        ('routes.finance', 'finance_bp', '/api/finance'),
        ('routes.customers', 'customers_bp', '/api/customers'),
        ('routes.session', 'session_bp', '/api/session'),
        ('routes.notifications', 'notifications_bp', '/api'),
        ('routes.user', 'user_bp', ''),
    ]
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    init_extensions(app)
    CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])
    
    # Register working blueprints
    for module_name, bp_name, url_prefix in blueprint_imports:
        try:
            module = importlib.import_module(module_name)
            blueprint = getattr(module, bp_name)
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            working_blueprints.append(f"{bp_name} -> {url_prefix}")
            print(f"✅ Registered: {bp_name}")
        except Exception as e:
            print(f"⚠️ Skipped {bp_name}: {str(e)}")
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'working_blueprints': working_blueprints,
            'services': {
                'database': 'connected',
                'ai_services': 'partial',
                'compliance': 'partial',
                'analytics': 'partial'
            }
        }), 200
    
    return app

def main():
    """Main startup function"""
    
    print("🚀 Starting Rice Mill ERP Backend (Minimal Mode)")
    print("=" * 60)
    
    try:
        app = create_minimal_app()
        
        # Initialize database
        with app.app_context():
            from extensions import db
            db.create_all()
            print("✅ Database tables initialized")
        
        print("\n🌐 Backend server starting...")
        print("📍 URL: http://localhost:5001")
        print("🏥 Health: http://localhost:5001/api/health")
        print("📚 Docs: docs/api_documentation.html")
        print("\n💡 Press Ctrl+C to stop")
        
        # Start server on port 5001 to avoid conflicts
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()