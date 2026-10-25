from routes.metadata import metadata_bp


def register(app, kernel):
    kernel.add_blueprint(metadata_bp, '/api/metadata')
    kernel.add_permissions(('metadata',))
    kernel.add_menu_items((
        {'key': 'formBuilder', 'path': '/form-builder', 'permission': 'metadata'},
        {'key': 'dashboardBuilder', 'path': '/dashboard-builder', 'permission': 'dashboard'},
    ))
