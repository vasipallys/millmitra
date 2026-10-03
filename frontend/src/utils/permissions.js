export function storedUser() {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null');
  } catch {
    return null;
  }
}

export function userPermissions(user) {
  if (Array.isArray(user?.permissions)) return user.permissions;
  return [];
}

export function can(user, permission) {
  return userPermissions(user).includes(permission);
}

export const ROUTE_PERMISSIONS = {
  '/dashboard': 'dashboard',
  '/mill-flow': 'mill_flow',
  '/farmers': 'farmers',
  '/inventory': 'inventory',
  '/production': 'production',
  '/sales': 'sales',
  '/finance': 'finance',
  '/customers': 'customers',
  '/settings': 'settings',
  '/users': 'users',
  '/access': 'users',
  '/lookups': 'lookups',
  '/quality-control': 'quality',
  '/analytics': 'preview',
  '/financial-intelligence': 'preview',
  '/compliance-gst': 'preview',
  '/analytics-reporting': 'preview',
  '/notifications': 'dashboard',
};

export function permissionForPath(pathname) {
  const match = Object.keys(ROUTE_PERMISSIONS)
    .sort((a, b) => b.length - a.length)
    .find((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
  return match ? ROUTE_PERMISSIONS[match] : null;
}
