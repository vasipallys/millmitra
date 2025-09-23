#!/usr/bin/env python3
"""
Minimal Backend Startup - Just Core Features
"""

import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

def create_minimal_app():
    """Create minimal Flask app with just working features"""
    
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    from datetime import datetime
    
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = 'rLlKR1rfRNZsErdE_O04UUtMMWTDu3AoEU3pGBXW9_8'
    app.config['JWT_SECRET_KEY'] = 'Hok3RgkabbuPJTFydRm8FqyREgyPh4y5OsAVAqMCKwI'
    
    # Enable CORS
    CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'service': 'Rice Mill ERP Backend',
            'port': 5001,
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth/*',
                'dashboard': '/api/dashboard/*',
                'farmer': '/api/farmer/*',
                'inventory': '/api/inventory/*'
            }
        }), 200
    
    # Simple auth endpoint
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # Simple authentication (for testing)
        if username == 'admin' and password == 'admin123':
            return jsonify({
                'success': True,
                'access_token': 'test-token-12345',
                'user': {
                    'id': 1,
                    'username': 'admin',
                    'role': 'admin'
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
    
    # Simple dashboard endpoint
    @app.route('/api/dashboard/overview', methods=['GET'])
    def dashboard_overview():
        return jsonify({
            'success': True,
            'data': {
                'total_farmers': 150,
                'total_inventory': 5000,
                'active_batches': 12,
                'pending_orders': 8,
                'quality_score': 95.5,
                'revenue_today': 125000
            }
        }), 200
    
    # Simple farmer endpoints
    @app.route('/api/farmer/list', methods=['GET'])
    def farmer_list():
        return jsonify({
            'success': True,
            'data': [
                {'id': 1, 'name': 'John Doe', 'phone': '9876543210', 'status': 'active'},
                {'id': 2, 'name': 'Jane Smith', 'phone': '9876543211', 'status': 'active'},
                {'id': 3, 'name': 'Bob Johnson', 'phone': '9876543212', 'status': 'active'}
            ],
            'total': 3
        }), 200
    
    @app.route('/api/farmer/create', methods=['POST'])
    def create_farmer():
        data = request.get_json()
        return jsonify({
            'success': True,
            'message': 'Farmer created successfully',
            'data': {
                'id': 4,
                'name': data.get('name'),
                'phone': data.get('phone'),
                'status': 'active'
            }
        }), 201
    
    # Simple inventory endpoint
    @app.route('/api/inventory/stock', methods=['GET'])
    def inventory_stock():
        return jsonify({
            'success': True,
            'data': {
                'paddy_stock': 2500,
                'rice_stock': 1800,
                'broken_rice': 200,
                'husk': 300,
                'bran': 150
            }
        }), 200
    
    # Catch-all for undefined endpoints
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'path': request.path,
            'available_endpoints': [
                '/api/health',
                '/api/auth/login',
                '/api/dashboard/overview',
                '/api/farmer/list',
                '/api/farmer/create',
                '/api/inventory/stock'
            ]
        }), 404
    
    return app

def main():
    """Main startup function"""
    
    print("🚀 Starting Rice Mill ERP Backend (Minimal Mode)")
    print("=" * 60)
    
    try:
        app = create_minimal_app()
        
        print("✅ Minimal backend created successfully")
        print("\n🌐 Backend server starting...")
        print("📍 URL: http://localhost:5001")
        print("🏥 Health: http://localhost:5001/api/health")
        print("🔐 Login: POST http://localhost:5001/api/auth/login")
        print("📊 Dashboard: http://localhost:5001/api/dashboard/overview")
        print("\n💡 Press Ctrl+C to stop")
        
        # Start server
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()