import re
from flask import Flask
from flask_cors import CORS
from extensions import db, jwt, init_extensions
from config import Config

# Import models to ensure they're registered
from models.farmer_edit_request import FarmerEditRequest
from models.inventory import StockMovement  # noqa: F401
from models.notification import Notification  # noqa: F401
from models.mill_config import MillConfig  # noqa: F401
from models.gst_filing import GstFilingRecord  # noqa: F401
from models.saved_report import SavedReport  # noqa: F401
from models.lookup import LookupOption  # noqa: F401
from models.tenant import Tenant, TenantMembership  # noqa: F401

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
from routes.users_admin import users_admin_bp
from routes.lookups import lookups_bp
from routes.tenants import tenants_bp

def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    # Initialize extensions
    init_extensions(app)
    CORS(app, origins=[
        re.compile(r'^http://localhost:\d+$'),
        re.compile(r'^http://127\.0\.0\.1:\d+$'),
    ])

    # Initialize session middleware
    from middleware.session_middleware import session_middleware
    session_middleware.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(biometric_bp, url_prefix='/api/biometric')
    app.register_blueprint(quality_vision_bp, url_prefix='/api/quality-vision')
    app.register_blueprint(financial_intelligence_bp, url_prefix='/api/financial-intelligence')
    app.register_blueprint(compliance_gst_bp, url_prefix='/api/compliance/gst')
    app.register_blueprint(analytics_reporting_bp, url_prefix='/api/analytics/reporting')
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
    app.register_blueprint(users_admin_bp, url_prefix='/api')
    app.register_blueprint(lookups_bp, url_prefix='/api')
    app.register_blueprint(tenants_bp, url_prefix='/api')

    from telemetry import init_telemetry
    from observability import init_observability
    init_telemetry(app)
    init_observability(app)
    from services.access_control import register_access_guard
    from services.tenant_scope import register_tenant_flush_guard
    register_access_guard(app)
    register_tenant_flush_guard()

    with app.app_context():
        try:
            db.create_all()
            from services.demo_users import ensure_demo_users
            from services.access_control import ensure_role_permissions
            from services.lookup_service import ensure_lookup_options
            from services.tenant_migration import (
                ensure_default_tenant,
                ensure_user_memberships,
                migrate_tenant_schema,
            )
            # Tenant columns must exist before any User ORM query.
            migrate_tenant_schema()
            ensure_demo_users()
            ensure_user_memberships(ensure_default_tenant())
            ensure_role_permissions()
            ensure_lookup_options()
        except Exception:
            app.logger.exception('startup_schema_failed')
            try:
                db.session.rollback()
            except Exception:
                pass
        if not app.config.get('TESTING'):
            from services.mill_settings_service import start_backup_scheduler
            start_backup_scheduler(app)

    return app

app = create_app()

if __name__ == '__main__':
    import os
    with app.app_context():
        db.create_all()
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)


