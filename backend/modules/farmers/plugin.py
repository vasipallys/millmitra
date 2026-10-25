"""Register the existing farmer blueprint through the kernel. URLs stay /api/farmer."""

from routes.farmer import farmer_bp


def register(app, kernel):
    kernel.add_blueprint(farmer_bp, '/api/farmer')
    kernel.add_permissions(('farmers',))
    kernel.add_lookup_groups((
        'paddy_variety',
        'farming_type',
        'irrigation_type',
        'crop_type',
        'season',
        'farmer_payment_type',
    ))
    kernel.add_menu_items((
        {'key': 'farmers', 'path': '/farmers', 'permission': 'farmers'},
    ))
