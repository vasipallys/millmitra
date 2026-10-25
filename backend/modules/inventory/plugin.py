"""Register the existing inventory blueprint through the kernel. URLs stay /api/inventory."""

from routes.inventory import inventory_bp


def register(app, kernel):
    kernel.add_blueprint(inventory_bp, '/api/inventory')
    kernel.add_permissions(('inventory',))
    kernel.add_lookup_groups(('stock_type', 'product_type', 'quality_grade', 'unit'))
    kernel.add_menu_items((
        {'key': 'inventory', 'path': '/inventory', 'permission': 'inventory'},
    ))
