import api from './api';

const API_BASE = '/finance';

class FinanceService {
  async createInvoice(invoiceData) {
    const response = await api.post(`${API_BASE}/invoices`, invoiceData);
    return response.data;
  }

  async getInvoices(params = {}) {
    const safeParams = params && !params.queryKey ? params : {};
    const response = await api.get(`${API_BASE}/invoices`, { params: safeParams });
    return response.data;
  }

  async recordPayment(paymentData) {
    const response = await api.post(`${API_BASE}/payments`, paymentData);
    return response.data;
  }

  async getCashFlow(period = 'monthly') {
    const safePeriod = typeof period === 'string' ? period : 'monthly';
    const response = await api.get(`${API_BASE}/cash-flow`, {
      params: { period: safePeriod }
    });
    const data = response.data || {};
    if (Array.isArray(data)) return data;
    if (Array.isArray(data.series)) return data.series;
    if (Array.isArray(data.cash_flow)) return data.cash_flow;
    return data;
  }

  async getAccountsReceivable() {
    const response = await api.get(`${API_BASE}/accounts-receivable`);
    const data = response.data || {};
    const receivables = data.receivables || data;
    return {
      ...receivables,
      total_outstanding: receivables.total_outstanding ?? 0,
      total_overdue: receivables.total_overdue ?? receivables.overdue_amount ?? 0,
      overdue_count: receivables.overdue_count ?? 0
    };
  }

  async getFinancialSummary(periodDays = 30) {
    const days = typeof periodDays === 'number' ? periodDays : 30;
    const response = await api.get(`${API_BASE}/financial-summary`, {
      params: { period_days: days }
    });
    const data = response.data || {};
    const summary = data.summary || data;
    return {
      ...summary,
      total_revenue: summary.total_revenue ?? 0,
      total_expenses: summary.total_expenses ?? 0,
      net_profit: summary.net_profit ?? 0,
      outstanding_receivables: summary.outstanding_receivables ?? 0
    };
  }

  async createBudget(budgetData) {
    const response = await api.post(`${API_BASE}/budgets`, budgetData);
    return response.data;
  }

  async getProfitLossReport(startDate, endDate) {
    const response = await api.get(`${API_BASE}/reports/profit-loss`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  }

  async getBalanceSheet(asOfDate) {
    const response = await api.get(`${API_BASE}/reports/balance-sheet`, {
      params: { as_of_date: asOfDate }
    });
    return response.data;
  }
}

export const financeService = new FinanceService();