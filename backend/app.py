from flask import Flask, jsonify
from flask_cors import CORS
from extensions import db, jwt, init_extensions
from config import Config

# Import models to ensure they're registered
from models.farmer_edit_request import FarmerEditRequest

# Import all blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.biometric import biometric_bp
from routes.quality_vision import quality_vision_bp
from routes.financial_intelligence import financial_intelligence_bp
from routes.compliance_gst import compliance_gst_bp
from routes.analytics_reporting import analytics_reporting_bp
from routes.farmer import farmer_bp
from routes.inventory import inventory_bp
from routes.production import production_bp
from routes.sales import sales_bp
from routes.finance import finance_bp
from routes.customers import customers_bp
from routes.session import session_bp
from routes.notifications import notifications_bp
from routes.user import user_bp
from routes.natural_language import natural_language_bp
# TODO: Re-enable these routes after implementation
# from routes.supply_chain import supply_chain_bp
# from routes.analytics import analytics_bp
# from routes.logistics import logistics_bp
# from routes.compliance import compliance_bp
# from routes.quality import quality_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with error handling
    try:
        init_extensions(app)
        print("✅ Extensions initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing extensions: {e}")
        raise

    # Enhanced CORS configuration
    CORS(app,
         origins=['http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:3000'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # Initialize session middleware
    from middleware.session_middleware import session_middleware
    session_middleware.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(biometric_bp, url_prefix='/api/biometric')
    app.register_blueprint(quality_vision_bp, url_prefix='/api/quality-vision')
    app.register_blueprint(financial_intelligence_bp, url_prefix='/api/financial-intelligence')
    app.register_blueprint(compliance_gst_bp, url_prefix='/api/compliance')
    app.register_blueprint(analytics_reporting_bp, url_prefix='/api/analytics')
    # Farmer routes enabled
    app.register_blueprint(farmer_bp, url_prefix='/api/farmer')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(production_bp, url_prefix='/api/production')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(finance_bp, url_prefix='/api/finance')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(session_bp, url_prefix='/api/session')
    app.register_blueprint(notifications_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(natural_language_bp, url_prefix='/api/ai')
    # TODO: Re-enable these routes after implementation
    # app.register_blueprint(supply_chain_bp, url_prefix='/api/supply-chain')
    # app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    # app.register_blueprint(logistics_bp, url_prefix='/api/logistics')
    # app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    # app.register_blueprint(quality_bp, url_prefix='/api/quality')

    # Enhanced health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from datetime import datetime

        # Check database connection
        db_status = 'connected'
        try:
            db.session.execute('SELECT 1')
        except Exception as e:
            db_status = f'error: {str(e)}'

        # Check AI services
        ai_status = 'active'
        try:
            import requests
            response = requests.get('http://127.0.0.1:8000/health', timeout=2)
            ai_status = 'active' if response.status_code == 200 else 'inactive'
        except:
            ai_status = 'inactive'

        return jsonify({
            'status': 'healthy' if db_status == 'connected' else 'degraded',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'services': {
                'database': db_status,
                'ai_services': ai_status,
                'compliance': 'active',
                'analytics': 'active'
            }
        }), 200

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found',
            'error': 'NOT_FOUND'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'error': 'INTERNAL_ERROR'
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e),
            'error': 'UNEXPECTED_ERROR'
        }), 500

    return app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Rice Mill Management System...")

    try:
        with app.app_context():
            print("📊 Initializing database...")
            db.create_all()
            print("✅ Database initialized successfully")

        print("🌐 Starting Flask server on http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)

    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        raise


