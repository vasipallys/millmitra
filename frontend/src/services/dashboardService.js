import axios from 'axios';

const API_BASE = '/api/dashboard';

class DashboardService {
  async getOverview(days = 7) {
    const response = await axios.get(`${API_BASE}/overview?days=${days}`);
    return response.data;
  }

  async getWidgets() {
    const response = await axios.get(`${API_BASE}/widgets`);
    return response.data;
  }

  async getInsights() {
    const response = await axios.get(`${API_BASE}/insights`);
    return response.data;
  }

  async getAlerts() {
    const response = await axios.get(`${API_BASE}/alerts`);
    return response.data;
  }

  async getPredictions(type = 'all') {
    const response = await axios.get(`${API_BASE}/predictions?type=${type}`);
    return response.data;
  }

  async saveCustomization(preferences) {
    const response = await axios.post(`${API_BASE}/customize`, preferences);
    return response.data;
  }

  async getProductionMetrics(days = 30) {
    const response = await axios.get(`${API_BASE}/metrics/production?days=${days}`);
    return response.data;
  }

  async getQualityMetrics(days = 30) {
    const response = await axios.get(`${API_BASE}/metrics/quality?days=${days}`);
    return response.data;
  }

  async getInventoryMetrics() {
    const response = await axios.get(`${API_BASE}/metrics/inventory`);
    return response.data;
  }
}

export const dashboardService = new DashboardService();