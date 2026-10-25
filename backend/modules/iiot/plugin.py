from routes.iiot import iiot_bp


def register(app, kernel):
    kernel.add_blueprint(iiot_bp, '/api/iiot')
    kernel.add_permissions(('iiot', 'reconciliation'))
    kernel.add_menu_items((
        {'key': 'iiot', 'path': '/iiot', 'permission': 'iiot'},
    ))
