from .auth import auth_bp
from .dashboard import dashboard_bp
from .inventory import inventory_bp
from .production import production_bp
from .sales import sales_bp
from .farmer import farmer_bp
from .finance import finance_bp
from .customers import customers_bp
# TODO: Re-enable after implementation
# from .ai import ai_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(production_bp, url_prefix='/api/production')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')