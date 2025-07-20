import axios from 'axios';

const API_BASE = '/api/finance';

class FinanceService {
  async createInvoice(invoiceData) {
    const response = await axios.post(`${API_BASE}/invoices`, invoiceData);
    return response.data;
  }

  async getInvoices(params = {}) {
    const response = await axios.get(`${API_BASE}/invoices`, { params });
    return response.data;
  }

  async recordPayment(paymentData) {
    const response = await axios.post(`${API_BASE}/payments`, paymentData);
    return response.data;
  }

  async getCashFlow(period = 'monthly') {
    const response = await axios.get(`${API_BASE}/cash-flow`, {
      params: { period }
    });
    return response.data;
  }

  async getAccountsReceivable() {
    const response = await axios.get(`${API_BASE}/accounts-receivable`);
    return response.data;
  }

  async getFinancialSummary(periodDays = 30) {
    const response = await axios.get(`${API_BASE}/financial-summary`, {
      params: { period_days: periodDays }
    });
    return response.data;
  }

  async createBudget(budgetData) {
    const response = await axios.post(`${API_BASE}/budgets`, budgetData);
    return response.data;
  }

  async getProfitLossReport(startDate, endDate) {
    const response = await axios.get(`${API_BASE}/reports/profit-loss`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  }

  async getBalanceSheet(asOfDate) {
    const response = await axios.get(`${API_BASE}/reports/balance-sheet`, {
      params: { as_of_date: asOfDate }
    });
    return response.data;
  }
}

export const financeService = new FinanceService();