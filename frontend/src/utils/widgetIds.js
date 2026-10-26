export const LEGACY_WIDGET_IDS = {
  production: 'production_overview',
  inventory: 'inventory_alerts',
  sales: 'sales_pipeline',
  quality: 'quality_trends',
  quality_score: 'quality_trends',
  pending_orders: 'sales_pipeline',
};

export function normalizeWidgetId(id) {
  if (!id) return id;
  return LEGACY_WIDGET_IDS[id] || id;
}

export function normalizeWidget(item) {
  if (typeof item === 'string') {
    const id = normalizeWidgetId(item);
    return { id, label: id, size: 6 };
  }
  const id = normalizeWidgetId(item.id);
  return {
    ...item,
    id,
    label: item.label || item.title || item.name || id,
    size: item.size || 6,
  };
}

export function selectValueInOptions(value, options) {
  const ids = options.map((item) => item.id);
  if (ids.includes(value)) return value;
  return '';
}
