import api from './api';

export const customerService = {
  // Customer Management
  async getCustomers(params = {}) {
    const response = await api.get('/customers/', { params });
    return response.data;
  },

  async createCustomer(customerData) {
    const response = await api.post('/customers/', customerData);
    return response.data;
  },

  async getCustomerDetails(customerId) {
    const response = await api.get(`/customers/${customerId}`);
    return response.data;
  },

  async updateCustomer(customerId, updateData) {
    const response = await api.put(`/customers/${customerId}`, updateData);
    return response.data;
  },

  // Customer Interactions
  async getCustomerInteractions(customerId) {
    const response = await api.get(`/customers/${customerId}/interactions`);
    return response.data;
  },

  async createInteraction(interactionData) {
    const { customerId, ...data } = interactionData;
    const response = await api.post(`/customers/${customerId}/interactions`, data);
    return response.data;
  },

  async resolveInteraction(interactionId, resolutionData) {
    const response = await api.post(`/interactions/${interactionId}/resolve`, resolutionData);
    return response.data;
  },

  // Order Management
  async getOrders(params = {}) {
    const response = await api.get('/sales/orders/', { params });
    return response.data;
  },

  async createOrder(orderData) {
    const response = await api.post('/sales/orders/', orderData);
    return response.data;
  },

  async getOrderDetails(orderId) {
    const response = await api.get(`/sales/orders/${orderId}`);
    return response.data;
  },

  async updateOrderStatus(orderId, statusData) {
    const response = await api.put(`/sales/orders/${orderId}/status`, statusData);
    return response.data;
  },

  // Analytics
  async getCustomerAnalytics() {
    const response = await api.get('/customers/analytics/overview');
    return response.data;
  },

  async getCustomerSegments() {
    const response = await api.get('/customers/analytics/segments');
    return response.data;
  },

  async getChurnPrediction() {
    const response = await api.get('/analytics/churn-prediction');
    return response.data;
  },

  async getLifetimeValueAnalysis() {
    const response = await api.get('/analytics/lifetime-value');
    return response.data;
  },

  // Communication
  async getCustomerCommunications(customerId) {
    const response = await api.get(`/customers/${customerId}/communications`);
    return response.data;
  },

  async sendCommunication(customerId, commData) {
    const response = await api.post(`/customers/${customerId}/communications`, commData);
    return response.data;
  },

  async sendBulkCommunication(bulkData) {
    const response = await api.post('/communications/bulk', bulkData);
    return response.data;
  },

  // AI-Enhanced Features
  async getCustomerRecommendations(customerId) {
    const response = await api.get(`/customers/${customerId}/ai/recommendations`);
    return response.data;
  },

  async getNextBestAction(customerId) {
    const response = await api.get(`/customers/${customerId}/ai/next-best-action`);
    return response.data;
  },

  async getCustomerAnalyticsDetail(customerId) {
    const response = await api.get(`/customers/${customerId}/analytics`);
    return response.data;
  },

  async intelligentSearch(query) {
    const response = await api.post('/customers/ai/intelligent-search', { query });
    return response.data;
  },

  async findSimilarCustomers(customerId) {
    const response = await api.get(`/customers/${customerId}/ai/similar`);
    return response.data;
  },

  async optimizePricing(pricingData) {
    const response = await api.post('/customers/ai/optimize-pricing', pricingData);
    return response.data;
  },

  async identifyCrossSellOpportunities(data) {
    const response = await api.post('/customers/ai/cross-sell', data);
    return response.data;
  },

  async analyzeFeedback(feedbackData) {
    const response = await api.post('/customers/ai/analyze-feedback', feedbackData);
    return response.data;
  },

  // Segmentation
  async optimizeSegments() {
    const response = await api.post('/customers/ai/optimize-segments');
    return response.data;
  },

  async predictCustomerSegment(customerData) {
    const response = await api.post('/customers/ai/predict-segment', customerData);
    return response.data;
  },

  // Reports
  async getAcquisitionReport(params = {}) {
    const response = await api.get('/customers/reports/acquisition', { params });
    return response.data;
  },

  async getRetentionReport(params = {}) {
    const response = await api.get('/customers/reports/retention', { params });
    return response.data;
  },

  async getFeedbackReport(params = {}) {
    const response = await api.get('/customers/reports/feedback', { params });
    return response.data;
  },

  // Bulk Operations
  async bulkUpdateCustomers(updateData) {
    const response = await api.post('/customers/bulk-update', updateData);
    return response.data;
  },

  async exportCustomers(params = {}) {
    const response = await api.get('/customers/export', { 
      params,
      responseType: 'blob'
    });
    return response.data;
  },

  async importCustomers(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/customers/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};
