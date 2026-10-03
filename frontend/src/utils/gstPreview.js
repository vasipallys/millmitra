/** Preview-only GST helpers for Compliance & GST. Not a filing engine. */

export const GST_CATEGORIES = {
  paddy: { rate: 0, label: 'Paddy (unprocessed)', hsn: '1006' },
  raw_rice: { rate: 5, label: 'Raw Rice', hsn: '1006' },
  processed_rice: { rate: 5, label: 'Processed Rice', hsn: '1006' },
  premium_rice: { rate: 5, label: 'Premium Rice', hsn: '1006' },
  broken_rice: { rate: 5, label: 'Broken Rice', hsn: '1006' },
  rice_bran: { rate: 5, label: 'Rice Bran', hsn: '2302' },
};

export const CALENDAR_TASKS = {
  'GSTR-1 Filing': {
    form: 'GSTR-1',
    meaning: 'Monthly (or quarterly) return of outward supplies — sales you made.',
    typicalDue: 'Usually the 11th of the following month.',
  },
  'GSTR-3B Filing': {
    form: 'GSTR-3B',
    meaning: 'Monthly summary return and tax payment for the period.',
    typicalDue: 'Usually the 20th of the following month.',
  },
  'Annual Return': {
    form: 'GSTR-9',
    meaning: 'Annual GST return consolidating the year’s filings.',
    typicalDue: 'Usually 31 December after the financial year (confirm on the GST portal).',
  },
  'TDS Return Q4': {
    form: 'TDS (Q4)',
    meaning: 'Quarterly tax-deducted-at-source return for January–March.',
    typicalDue: 'Usually mid-April after the quarter.',
  },
};

export function roundMoney(value) {
  return Math.round((Number(value) || 0) * 100) / 100;
}

export function computeGst({
  amount,
  product_category = 'processed_rice',
  transaction_type = 'sale',
  supply = 'intra',
}) {
  const taxable = Number(amount);
  if (!Number.isFinite(taxable) || taxable <= 0) {
    return { success: false, message: 'Enter an amount greater than 0' };
  }
  const category = GST_CATEGORIES[product_category] || GST_CATEGORIES.processed_rice;
  const gstAmount = roundMoney((taxable * category.rate) / 100);
  const intra = supply !== 'inter';
  const half = roundMoney(gstAmount / 2);
  return {
    success: true,
    base_amount: taxable,
    gst_rate: category.rate,
    cgst: intra ? half : 0,
    sgst: intra ? (intra ? roundMoney(gstAmount - half) : 0) : 0,
    igst: intra ? 0 : gstAmount,
    gst_amount: gstAmount,
    total_amount: roundMoney(taxable + gstAmount),
    category_label: category.label,
    hsn: category.hsn,
    product_category,
    transaction_type,
    supply: intra ? 'Intra-state (CGST + SGST)' : 'Inter-state (IGST)',
  };
}

export function downloadText(filename, content, mime = 'text/plain;charset=utf-8') {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function toCsv(rows) {
  if (!rows.length) return '';
  const headers = Object.keys(rows[0]);
  const escape = (value) => `"${String(value ?? '').replace(/"/g, '""')}"`;
  return [
    headers.join(','),
    ...rows.map((row) => headers.map((key) => escape(row[key])).join(',')),
  ].join('\n');
}

export function formatInr(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`;
}

export function invoicesToGstr1Rows(invoices) {
  if (!Array.isArray(invoices) || !invoices.length) return [];
  return invoices.map((invoice, index) => {
    const taxable = Number(invoice.subtotal ?? invoice.total_amount ?? 0);
    const tax = Number(invoice.tax_amount ?? 0);
    return {
      sr: index + 1,
      invoice_number: invoice.invoice_number || invoice.id || `INV-${index + 1}`,
      invoice_date: invoice.invoice_date || '',
      customer: invoice.customer?.name || invoice.customer_name || invoice.customer_id || '',
      taxable_value: roundMoney(taxable),
      gst_amount: roundMoney(tax || taxable * 0.05),
      total: roundMoney(invoice.total_amount ?? taxable + tax),
      status: invoice.status || '',
    };
  });
}

export function sampleGstr1Rows() {
  return [
    { sr: 1, invoice_number: 'INV000001', invoice_date: '2024-01-10', customer: 'Sample trader', taxable_value: 50000, gst_amount: 2500, total: 52500, status: 'sample' },
    { sr: 2, invoice_number: 'INV000002', invoice_date: '2024-01-18', customer: 'Sample distributor', taxable_value: 75000, gst_amount: 3750, total: 78750, status: 'sample' },
  ];
}

export function sampleGstr2bRows() {
  return [
    { sr: 1, invoice_number: 'PUR-104', invoice_date: '2024-01-08', supplier: 'Sample paddy seller', taxable_value: 40000, gst_amount: 2000, total: 42000, status: 'sample' },
    { sr: 2, invoice_number: 'PUR-118', invoice_date: '2024-01-22', supplier: 'Sample packing vendor', taxable_value: 12000, gst_amount: 600, total: 12600, status: 'sample' },
  ];
}

export function sampleGstr3bSummary(rows) {
  const taxable = rows.reduce((sum, row) => sum + Number(row.taxable_value || 0), 0);
  const gst = rows.reduce((sum, row) => sum + Number(row.gst_amount || 0), 0);
  return [
    { nature: 'Outward taxable supplies', taxable_value: roundMoney(taxable), igst: 0, cgst: roundMoney(gst / 2), sgst: roundMoney(gst / 2) },
    { nature: 'Inward supplies (reverse charge)', taxable_value: 0, igst: 0, cgst: 0, sgst: 0 },
    { nature: 'Tax payable', taxable_value: '', igst: 0, cgst: roundMoney(gst / 2), sgst: roundMoney(gst / 2) },
  ];
}

export function buildInvoiceText(form, lines) {
  const subtotal = lines.reduce((sum, line) => sum + line.taxable, 0);
  const gst = lines.reduce((sum, line) => sum + line.gst_amount, 0);
  const body = lines.map((line, i) => (
    `${i + 1}. ${line.description || line.category_label}  qty ${line.quantity} x ${formatInr(line.unit_price)}  taxable ${formatInr(line.taxable)}  GST ${line.gst_rate}% ${formatInr(line.gst_amount)}  line ${formatInr(line.total)}`
  )).join('\n');
  return [
    'MillMitra preview GST invoice (not a statutory tax invoice)',
    `Customer ID: ${form.customer_id || '—'}`,
    `Invoice date: ${form.invoice_date || '—'}`,
    `Due date: ${form.due_date || '—'}`,
    `Payment terms: ${form.payment_terms || '—'}`,
    '',
    body,
    '',
    `Taxable value: ${formatInr(subtotal)}`,
    `GST: ${formatInr(gst)}`,
    `Total: ${formatInr(subtotal + gst)}`,
    '',
    'This file is a demonstration download from Compliance & GST preview.',
  ].join('\n');
}
