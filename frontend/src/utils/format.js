/** Shared display formatters. Indian grouping, mill units, mill dates. */

export function formatINR(value, { empty = '—' } = {}) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return empty;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: amount >= 100 ? 0 : 2,
  }).format(amount);
}

export function formatQty(value, unit = 'kg', { empty = '—' } = {}) {
  const qty = Number(value);
  if (!Number.isFinite(qty)) return empty;
  const text = new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: qty >= 100 ? 1 : 2,
  }).format(qty);
  return unit ? `${text} ${unit}` : text;
}

export function formatDate(value, { empty = '—', withTime = false } = {}) {
  if (!value) return empty;
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return empty;
  const datePart = new Intl.DateTimeFormat('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(date);
  if (!withTime) return datePart;
  const timePart = new Intl.DateTimeFormat('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
  return `${datePart} ${timePart}`;
}

export function formatNumber(value, { empty = '—', digits = 0 } = {}) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return empty;
  return new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: digits,
  }).format(amount);
}
