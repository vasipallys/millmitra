from flask import Flask
from flask_cors import CORS
from extensions import db, jwt, init_extensions
from config import Config

# Import all blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.farmer import farmer_bp
from routes.inventory import inventory_bp
from routes.production import production_bp
from routes.sales import sales_bp
from routes.finance import finance_bp
from routes.customers import customers_bp
# TODO: Re-enable these routes after implementation
# from routes.supply_chain import supply_chain_bp
# from routes.analytics import analytics_bp
# from routes.logistics import logistics_bp
# from routes.compliance import compliance_bp
# from routes.quality import quality_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    init_extensions(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    # Temporarily disabled due to route conflicts - will be fixed
    # app.register_blueprint(farmer_bp, url_prefix='/api/farmers')
    # app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    # app.register_blueprint(production_bp, url_prefix='/api/production')
    # app.register_blueprint(sales_bp, url_prefix='/api/sales')
    # app.register_blueprint(finance_bp, url_prefix='/api/finance')
    # app.register_blueprint(customers_bp, url_prefix='/api/customers')
    # TODO: Re-enable these routes after implementation
    # app.register_blueprint(supply_chain_bp, url_prefix='/api/supply-chain')
    # app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    # app.register_blueprint(logistics_bp, url_prefix='/api/logistics')
    # app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    # app.register_blueprint(quality_bp, url_prefix='/api/quality')
    
    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)


