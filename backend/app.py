import re
from flask import Flask, make_response, request
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
from models.metadata import (  # noqa: F401
    CustomFieldValue, DashboardLayout, EntityDefinition, FieldDefinition,
    FormLayout, MetadataRecord, TranslatedText, ViewDefinition,
)
from models.iiot import Device, Discrepancy, IiotAudit, MachineTelemetry  # noqa: F401

# Import all blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.biometric import biometric_bp
from routes.quality_vision import quality_vision_bp
from routes.financial_intelligence import financial_intelligence_bp
from routes.compliance_gst import compliance_gst_bp
from routes.analytics_reporting import analytics_reporting_bp
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
from routes.grok import grok_bp

def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    # Initialize extensions
    init_extensions(app)
    app.url_map.strict_slashes = False
    CORS(app, origins=[
        re.compile(r'^http://localhost:\d+$'),
        re.compile(r'^http://127\.0\.0\.1:\d+$'),
    ], methods=['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'], allow_headers=[
        'Content-Type',
        'Authorization',
        'X-Tenant-ID',
        'X-Session-Token',
        'X-Request-ID',
    ], expose_headers=['X-Request-ID', 'X-User-ID', 'X-User-Role'], max_age=86400)

    @app.before_request
    def _short_circuit_cors_preflight():
        if request.method == 'OPTIONS':
            return make_response('', 204)

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
    app.register_blueprint(grok_bp, url_prefix='/api/ai')

    from kernel.events import BUS, KafkaAdapter, RedisStreamsAdapter
    from kernel.registry import boot_kernel
    from kernel.tenant_router import register_tenant_router
    boot_kernel(app)
    register_tenant_router(app)
    kafka_servers = app.config.get('KAFKA_BOOTSTRAP_SERVERS')
    if kafka_servers:
        try:
            BUS.use(KafkaAdapter(kafka_servers))
        except Exception:
            app.logger.info('event_bus_kafka_unavailable')
    redis_url = app.config.get('REDIS_URL')
    if redis_url and not kafka_servers:
        try:
            BUS.use(RedisStreamsAdapter(redis_url))
        except Exception:
            app.logger.info('event_bus_redis_unavailable')

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
            from services.iiot_service import ensure_demo_device
            ensure_demo_device(ensure_default_tenant())
        except Exception:
            app.logger.exception('startup_schema_failed')
            try:
                db.session.rollback()
            except Exception:
                pass
        if not app.config.get('TESTING'):
            from services.mill_settings_service import start_backup_scheduler
            from services.iiot_mqtt import start_mqtt_subscriber
            start_backup_scheduler(app)
            start_mqtt_subscriber(app)

    return app

app = create_app()

if __name__ == '__main__':
    import os
    with app.app_context():
        db.create_all()
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)


