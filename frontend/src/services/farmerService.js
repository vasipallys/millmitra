import api from './api';

export const farmerService = {
  // Farmer registration and management
  registerFarmer: async (farmerData) => {
    const response = await api.post('/farmer/register', farmerData);
    return response.data;
  },

  getFarmers: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });
    
    const response = await api.get(`/farmer/list?${params}`);
    return response.data;
  },

  getFarmerDetails: async (farmerId) => {
    const response = await api.get(`/farmer/${farmerId}`);
    return response.data;
  },

  updateFarmer: async (farmerId, updateData) => {
    const response = await api.put(`/farmer/${farmerId}`, updateData);
    return response.data;
  },

  // Edit request management
  getEditRequests: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });

    const response = await api.get(`/farmer/edit-requests?${params}`);
    return response.data;
  },

  approveEditRequest: async (requestId, comments = '') => {
    const response = await api.post(`/farmer/edit-requests/${requestId}/approve`, {
      comments
    });
    return response.data;
  },

  rejectEditRequest: async (requestId, comments) => {
    const response = await api.post(`/farmer/edit-requests/${requestId}/reject`, {
      comments
    });
    return response.data;
  },

  // Contract management
  createContract: async (contractData) => {
    const response = await api.post('/farmer/contracts', contractData);
    return response.data;
  },

  getContracts: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });
    
    const response = await api.get(`/farmer/contracts?${params}`);
    return response.data;
  },

  updateContract: async (contractId, updateData) => {
    const response = await api.put(`/farmer/contracts/${contractId}`, updateData);
    return response.data;
  },

  // Procurement management
  recordProcurement: async (procurementData) => {
    const response = await api.post('/farmer/procurements', procurementData);
    return response.data;
  },

  getProcurements: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });
    
    const response = await api.get(`/farmer/procurements?${params}`);
    return response.data;
  },

  updateProcurement: async (procurementId, updateData) => {
    const response = await api.put(`/farmer/procurements/${procurementId}`, updateData);
    return response.data;
  },

  // Payment management
  processPayment: async (paymentData) => {
    const response = await api.post('/farmer/payments', paymentData);
    return response.data;
  },

  getPayments: async (filters = {}) => {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key]) params.append(key, filters[key]);
    });
    
    const response = await api.get(`/farmer/payments?${params}`);
    return response.data;
  },

  // Analytics and reporting
  getFarmerAnalytics: async (period = 'monthly', district = null) => {
    const params = new URLSearchParams({ period });
    if (district) params.append('district', district);
    
    const response = await api.get(`/farmer/analytics/overview?${params}`);
    return response.data;
  },

  getQualityTrends: async (farmerId = null, period = 'yearly') => {
    const params = new URLSearchParams({ period });
    if (farmerId) params.append('farmer_id', farmerId);
    
    const response = await api.get(`/farmer/quality-trends?${params}`);
    return response.data;
  },

  // Seasonal planning
  createSeasonalPlan: async (planData) => {
    const response = await api.post('/farmer/seasonal-planning', planData);
    return response.data;
  },

  // Document management
  uploadDocument: async (farmerId, documentType, file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    
    const response = await api.post(`/farmer/${farmerId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getDocuments: async (farmerId) => {
    const response = await api.get(`/farmer/${farmerId}/documents`);
    return response.data;
  },

  verifyDocument: async (documentId, verificationData) => {
    const response = await api.put(`/farmer/documents/${documentId}/verify`, verificationData);
    return response.data;
  }
};