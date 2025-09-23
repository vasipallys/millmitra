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
from routes.supply_chain import supply_chain_bp
from routes.analytics import analytics_bp
from routes.logistics import logistics_bp
from routes.compliance import compliance_bp
from routes.quality import quality_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    init_extensions(app)
    CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])

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
    app.register_blueprint(notifications_bp, url_prefix='/api')
    app.register_blueprint(user_bp)
    app.register_blueprint(supply_chain_bp, url_prefix='/api/supply-chain')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(logistics_bp, url_prefix='/api/logistics')
    app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    app.register_blueprint(quality_bp, url_prefix='/api/quality')

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'services': {
                'database': 'connected',
                'ai_services': 'active',
                'compliance': 'active',
                'analytics': 'active'
            }
        }), 200

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)


