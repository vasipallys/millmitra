"""Discover backend/modules/*/plugin.py and register blueprints with the app."""

import importlib
import logging
import pkgutil
from pathlib import Path

logger = logging.getLogger(__name__)

_KERNEL = None


class Kernel:
    def __init__(self):
        self.blueprints = []
        self.permissions = set()
        self.lookup_groups = set()
        self.menu_items = []
        self.modules = []

    def add_blueprint(self, blueprint, url_prefix=None):
        self.blueprints.append((blueprint, url_prefix))

    def add_permissions(self, keys):
        for key in keys or ():
            if key:
                self.permissions.add(key)

    def add_lookup_groups(self, groups):
        for group in groups or ():
            if group:
                self.lookup_groups.add(group)

    def add_menu_items(self, items):
        for item in items or ():
            if item:
                self.menu_items.append(item)

    def discover(self, package_name='modules'):
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.exception('kernel_modules_missing')
            return
        root = Path(package.__file__).resolve().parent
        for info in pkgutil.iter_modules([str(root)]):
            if info.name.startswith('_'):
                continue
            module_name = '%s.%s.plugin' % (package_name, info.name)
            try:
                plugin = importlib.import_module(module_name)
            except ImportError:
                continue
            register = getattr(plugin, 'register', None)
            if not callable(register):
                continue
            register(None, self)
            self.modules.append(info.name)
            logger.info('kernel_module_loaded name=%s', info.name)

    def attach(self, app):
        seen = set()
        for blueprint, prefix in self.blueprints:
            key = getattr(blueprint, 'name', None) or id(blueprint)
            if key in seen:
                continue
            seen.add(key)
            if prefix:
                app.register_blueprint(blueprint, url_prefix=prefix)
            else:
                app.register_blueprint(blueprint)

    def snapshot(self):
        return {
            'modules': list(self.modules),
            'permissions': sorted(self.permissions),
            'lookup_groups': sorted(self.lookup_groups),
            'menu_items': list(self.menu_items),
        }


def get_kernel():
    global _KERNEL
    if _KERNEL is None:
        _KERNEL = Kernel()
    return _KERNEL


def boot_kernel(app):
    """Fresh kernel per app so tests do not double-register blueprints."""
    global _KERNEL
    kernel = Kernel()
    kernel.discover()
    kernel.attach(app)
    _KERNEL = kernel
    app.extensions = getattr(app, 'extensions', {})
    app.extensions['millmitra_kernel'] = kernel
    return kernel
