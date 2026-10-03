export function downloadBlob(filename, blob) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || 'download';
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function downloadText(filename, content, mime = 'text/plain;charset=utf-8') {
  downloadBlob(filename, new Blob([content], { type: mime }));
}

export function filenameFromDisposition(header, fallback) {
  const match = /filename\*?=(?:UTF-8''|")?([^\";]+)/i.exec(header || '');
  if (!match) return fallback;
  return decodeURIComponent(match[1].replace(/"/g, '').trim());
}

export function toCsv(rows) {
  if (!rows?.length) return '';
  const headers = Object.keys(rows[0]);
  const escape = (value) => `"${String(value ?? '').replace(/"/g, '""')}"`;
  return [
    headers.join(','),
    ...rows.map((row) => headers.map((key) => escape(row[key])).join(',')),
  ].join('\n');
}
