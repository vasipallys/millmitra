import { invoicesToGstr1Rows, roundMoney } from './gstPreview';

export function daysFromRange(timeRange) {
  if (timeRange === '7d' || timeRange === 7) return 7;
  if (timeRange === '90d' || timeRange === 90) return 90;
  return 30;
}

export function asNumber(value, fallback = 0) {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

export function formatDateLabel(value) {
  if (!value) return '';
  const parsed = new Date(value);
  if (!Number.isNaN(parsed.getTime())) {
    return parsed.toISOString().slice(0, 10);
  }
  return String(value).slice(0, 10);
}

export function unwrapList(payload, keys = []) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

export function normalizeQualityTests(payload) {
  const tests = unwrapList(payload, ['quality_tests', 'tests', 'items']);
  return tests.map((test) => ({
    id: test.test_id || test.id,
    batch_id: test.batch_id ?? '—',
    variety: test.sample_type || test.variety || test.product_type || '—',
    grade: test.grade || '—',
    score: asNumber(test.quality_score ?? test.grade_confidence ?? test.score),
    date: test.test_date || test.created_at || '',
    status: test.status || 'completed',
    details: test,
  }));
}

export function qualityDashboardFromTests(tests) {
  const scores = tests.map((test) => asNumber(test.score)).filter((score) => score > 0);
  const avg = scores.length ? scores.reduce((sum, score) => sum + score, 0) / scores.length : 0;
  const pass = tests.filter((test) => {
    const grade = String(test.grade || '').toUpperCase();
    return grade.startsWith('A') || grade.startsWith('B');
  }).length;
  const today = new Date().toISOString().slice(0, 10);
  return {
    passRate: tests.length ? (pass / tests.length) * 100 : 0,
    avgScore: avg,
    testsToday: tests.filter((test) => String(test.date || '').startsWith(today)).length,
    testCount: tests.length,
  };
}

export function qualityTrendFromTests(tests) {
  const byDay = {};
  tests.forEach((test) => {
    const day = formatDateLabel(test.date);
    if (!day) return;
    if (!byDay[day]) byDay[day] = { date: day, scoreSum: 0, tests: 0 };
    byDay[day].scoreSum += asNumber(test.score);
    byDay[day].tests += 1;
  });
  return Object.values(byDay)
    .sort((left, right) => left.date.localeCompare(right.date))
    .map((row) => ({
      date: row.date,
      score: row.tests ? row.scoreSum / row.tests : 0,
      tests: row.tests,
    }));
}

const GRADE_COLORS = {
  A: '#4CAF50',
  B: '#FF9800',
  C: '#FFC107',
  D: '#FF5722',
  E: '#F44336',
};

export function gradeDistributionFromTests(tests) {
  if (!tests.length) return [];
  const counts = {};
  tests.forEach((test) => {
    const raw = String(test.grade || '—').toUpperCase().replace('GRADE ', '');
    const key = raw[0] && 'ABCDE'.includes(raw[0]) ? raw[0] : 'Other';
    counts[key] = (counts[key] || 0) + 1;
  });
  return Object.entries(counts).map(([name, count]) => ({
    name: name === 'Other' ? 'Other' : `Grade ${name}`,
    value: Math.round((count / tests.length) * 100),
    count,
    color: GRADE_COLORS[name] || '#607D8B',
  }));
}

export function productionTrendFromRecords(analytics, batches = []) {
  const daily = analytics?.daily_production;
  if (Array.isArray(daily) && daily.length) {
    return daily.map((row) => ({
      date: formatDateLabel(row.date || row.day),
      production: asNumber(row.production || row.output || row.total_output),
      efficiency: asNumber(row.efficiency || analytics.average_efficiency),
      quality: asNumber(row.quality),
    }));
  }
  const byDay = {};
  batches.forEach((batch) => {
    const day = formatDateLabel(batch.start_time || batch.completed_at || batch.created_at);
    if (!day) return;
    if (!byDay[day]) byDay[day] = { date: day, production: 0, efficiencySum: 0, n: 0 };
    byDay[day].production += asNumber(batch.total_output || batch.paddy_input_quantity);
    byDay[day].efficiencySum += asNumber(batch.efficiency_percentage);
    byDay[day].n += 1;
  });
  return Object.values(byDay)
    .sort((left, right) => left.date.localeCompare(right.date))
    .map((row) => ({
      date: row.date,
      production: row.production,
      efficiency: row.n ? row.efficiencySum / row.n : 0,
      quality: 0,
    }));
}

export function salesByProductFromOrders(orders) {
  const colors = ['#2E7D32', '#FF9800', '#1976D2', '#9C27B0', '#607D8B'];
  const totals = {};
  orders.forEach((order) => {
    const name = order.description || order.product_name || order.product || 'Other';
    totals[name] = (totals[name] || 0) + asNumber(order.total_amount || order.quantity || 1);
  });
  const entries = Object.entries(totals);
  const sum = entries.reduce((acc, [, value]) => acc + value, 0) || 1;
  return entries.map(([name, value], index) => ({
    name,
    value: Math.round((value / sum) * 100),
    color: colors[index % colors.length],
  }));
}

export function financialSeriesFromCashFlow(cashFlow) {
  const series = Array.isArray(cashFlow)
    ? cashFlow
    : unwrapList(cashFlow, ['series', 'cash_flow', 'items']);
  return series.map((row) => {
    const inflow = asNumber(row.inflow || row.revenue);
    const outflow = asNumber(row.outflow || row.costs || row.expenses);
    return {
      month: row.month || row.period || formatDateLabel(row.date),
      date: formatDateLabel(row.date || row.period || row.month),
      revenue: asNumber(row.revenue || row.inflow),
      costs: asNumber(row.costs || row.outflow || row.expenses),
      profit: asNumber(row.profit ?? (inflow - outflow)),
      inflow,
      outflow,
      net: asNumber(row.net ?? row.netFlow ?? (inflow - outflow)),
    };
  });
}

export function cashFlowFromInvoices(invoices) {
  const byDay = {};
  invoices.forEach((invoice) => {
    const day = formatDateLabel(invoice.invoice_date || invoice.created_at);
    if (!day) return;
    if (!byDay[day]) byDay[day] = { date: day, inflow: 0, outflow: 0, net: 0 };
    const total = asNumber(invoice.total_amount);
    const paid = asNumber(invoice.paid_amount || invoice.amount_paid);
    const status = String(invoice.status || '').toLowerCase();
    byDay[day].inflow += paid || (status === 'paid' ? total : 0);
    byDay[day].net = byDay[day].inflow - byDay[day].outflow;
  });
  return Object.values(byDay).sort((left, right) => left.date.localeCompare(right.date));
}

export function derivedFinanceHealth(summary, receivables) {
  const revenue = asNumber(summary?.total_revenue);
  const expenses = asNumber(summary?.total_expenses);
  const profit = asNumber(summary?.net_profit ?? (revenue - expenses));
  const outstanding = asNumber(receivables?.total_outstanding ?? summary?.outstanding_receivables);
  const overdue = asNumber(receivables?.total_overdue);
  const collection = revenue + outstanding > 0 ? (revenue / (revenue + outstanding)) * 100 : 0;
  const margin = revenue > 0 ? (profit / revenue) * 100 : 0;
  const overdueControl = outstanding > 0 ? Math.max(0, 100 - (overdue / outstanding) * 100) : (revenue ? 100 : 0);
  return {
    overall_score: Math.round(collection * 10) / 10,
    health_grade: '—',
    health_status: 'Collection rate from invoices and payments — not a credit score',
    derived: true,
    component_scores: {
      collections: Math.round(collection),
      profit_margin: Math.round(margin),
      overdue_control: Math.round(overdueControl),
    },
  };
}

export function financeInsightsFromRecords({ summary, receivables, invoices }) {
  const insights = [];
  const overdueCount = asNumber(receivables?.overdue_count);
  const overdueAmt = asNumber(receivables?.total_overdue);
  if (overdueCount > 0) {
    insights.push({
      category: 'payments',
      type: 'warning',
      title: 'Overdue invoices',
      description: `${overdueCount} invoice(s) overdue totaling ₹${overdueAmt.toLocaleString('en-IN')}`,
      recommendation: 'Record collections on Finance → Record Payment',
    });
  }
  const revenue = asNumber(summary?.total_revenue);
  const profit = asNumber(summary?.net_profit);
  if (revenue > 0) {
    insights.push({
      category: 'cash_flow',
      type: 'positive',
      title: 'Invoice revenue in period',
      description: `₹${revenue.toLocaleString('en-IN')} billed, net ₹${profit.toLocaleString('en-IN')}`,
      recommendation: 'Compare with Finance → Financial Summary',
    });
  }
  if (!(invoices || []).length) {
    insights.push({
      category: 'forecast',
      type: 'warning',
      title: 'No invoices yet',
      description: 'Financial Intelligence has no mill invoices to summarize.',
      recommendation: 'Create invoices on Finance',
    });
  }
  return insights;
}

export function mapDashboardInsights(payload) {
  const list = unwrapList(payload, ['insights', 'items']);
  return list.map((item, index) => ({
    id: item.id || index + 1,
    type: item.type || item.severity || 'info',
    title: item.title || item.category || 'Insight',
    description: item.description || item.message || item.insight || '',
    impact: item.impact || item.priority || 'Medium',
    confidence: item.confidence != null ? asNumber(item.confidence) : null,
  }));
}

export function typicalGstDueDates(from = new Date()) {
  const next = new Date(from.getFullYear(), from.getMonth() + 1, 1);
  const year = next.getFullYear();
  const month = String(next.getMonth() + 1).padStart(2, '0');
  return {
    gstr1: `11-${month}-${year}`,
    gstr3b: `20-${month}-${year}`,
    annual: `31-12-${from.getFullYear()}`,
    tds: `15-04-${from.getMonth() >= 3 ? from.getFullYear() + 1 : from.getFullYear()}`,
  };
}

export function statutoryGstCalendar() {
  const dues = typicalGstDueDates();
  return [
    { date: dues.gstr1, task: 'GSTR-1 Filing', status: 'checklist', priority: 'high' },
    { date: dues.gstr3b, task: 'GSTR-3B Filing', status: 'checklist', priority: 'high' },
    { date: dues.annual, task: 'Annual Return', status: 'checklist', priority: 'medium' },
    { date: dues.tds, task: 'TDS Return Q4', status: 'checklist', priority: 'medium' },
  ];
}

export function gstDashboardFromInvoices(invoices) {
  const rows = invoicesToGstr1Rows(invoices);
  const taxable = rows.reduce((sum, row) => sum + asNumber(row.taxable_value), 0);
  const gst = rows.reduce((sum, row) => sum + asNumber(row.gst_amount), 0);
  return {
    monthly_summary: {
      total_sales: roundMoney(taxable),
      total_gst_collected: roundMoney(gst),
      invoice_count: rows.length,
      gstr1_filed: false,
      gstr3b_filed: false,
      due_dates: typicalGstDueDates(),
    },
    tax_breakdown: [
      { name: '5% GST', value: roundMoney(gst), color: '#4CAF50' },
      { name: '12% GST', value: 0, color: '#FF9800' },
      { name: '18% GST', value: 0, color: '#F44336' },
      { name: '28% GST', value: 0, color: '#9C27B0' },
    ],
  };
}

export function gstActivitiesFromInvoices(invoices) {
  return invoices.slice(0, 10).map((invoice) => ({
    date: formatDateLabel(invoice.invoice_date || invoice.created_at),
    activity: `Invoice ${invoice.invoice_number || invoice.id}`,
    status: invoice.status || 'recorded',
    amount: asNumber(invoice.tax_amount ?? invoice.total_amount),
    form: 'Invoice',
  }));
}

export function actualComplianceStatus(invoices) {
  const rows = invoicesToGstr1Rows(invoices);
  const gst = rows.reduce((sum, row) => sum + asNumber(row.gst_amount), 0);
  const issues = rows.length
    ? [`${rows.length} invoice(s), GST ${roundMoney(gst).toLocaleString('en-IN')} at preview rates. Not a filed return.`]
    : ['No invoices yet. GST totals will appear after Finance invoices exist.'];
  return {
    overall_status: rows.length ? 'invoice preview' : 'no invoices',
    compliance_score: null,
    invoice_count: rows.length,
    gst_total: gst,
    checks: [
      {
        category: 'GST from invoices',
        status: 'preview',
        issues,
      },
      {
        category: 'Statutory filings',
        status: 'checklist',
        issues: ['GSTR-1 and GSTR-3B must be filed on the GST portal. MillMitra does not file returns.'],
      },
    ],
    alerts: [],
  };
}

export function procurementsToGstr2bRows(procurements) {
  if (!Array.isArray(procurements) || !procurements.length) return [];
  return procurements.map((row, index) => {
    const taxable = asNumber(row.total_amount ?? row.amount ?? row.quantity * row.rate);
    const gst = asNumber(row.tax_amount ?? taxable * 0.05);
    return {
      sr: index + 1,
      invoice_number: row.invoice_number || row.procurement_id || row.id || `PUR-${index + 1}`,
      invoice_date: formatDateLabel(row.procurement_date || row.date || row.created_at),
      supplier: row.farmer?.name || row.farmer_name || row.supplier || '',
      taxable_value: roundMoney(taxable),
      gst_amount: roundMoney(gst),
      total: roundMoney(taxable + gst),
      status: row.status || 'recorded',
    };
  });
}

