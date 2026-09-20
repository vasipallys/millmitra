import api from './api';

function queryParams(params) {
  if (!params || typeof params !== 'object' || Array.isArray(params)) {
    return {};
  }
  if (params.queryKey || params.signal || typeof params.pageParam !== 'undefined') {
    return {};
  }
  return params;
}

export const inventoryService = {
  // Product Stock Management
  async getProductStock(params = {}) {
    try {
      const response = await api.get('/inventory/products', { params: queryParams(params) });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch product stock');
    }
  },

  async updateProductStock(productId, updateData) {
    try {
      const response = await api.put(`/inventory/products/${productId}`, updateData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update product stock');
    }
  },

  async addProductStock(stockData) {
    try {
      const response = await api.post('/inventory/products', stockData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to add product stock');
    }
  },

  // Paddy Stock Management
  async getPaddyStock(params = {}) {
    try {
      const response = await api.get('/inventory/paddy', { params: queryParams(params) });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch paddy stock');
    }
  },

  async updatePaddyStock(paddyId, updateData) {
    try {
      const response = await api.put(`/inventory/paddy/${paddyId}`, updateData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update paddy stock');
    }
  },

  async addPaddyStock(stockData) {
    try {
      const response = await api.post('/inventory/paddy', stockData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to add paddy stock');
    }
  },

  // Inventory Analytics
  async getInventoryAnalytics(params = {}) {
    try {
      const response = await api.get('/inventory/analytics', { params: queryParams(params) });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch inventory analytics');
    }
  },

  async getStockMovements(params = {}) {
    try {
      const response = await api.get('/inventory/movements', { params: queryParams(params) });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch stock movements');
    }
  },

  async getLowStockAlerts() {
    try {
      const response = await api.get('/inventory/alerts/low-stock');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch low stock alerts');
    }
  },

  async getReorderAlerts() {
    return this.getLowStockAlerts();
  },

  async getInventoryOverview(params = {}) {
    try {
      const response = await api.get('/inventory/analytics', { params: queryParams(params) });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch inventory overview');
    }
  },

  async getInventoryValuation() {
    try {
      const response = await api.get('/inventory/valuation');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch inventory valuation');
    }
  },

  async createStockMovement(movementData) {
    try {
      const response = await api.post('/inventory/transactions', movementData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to record stock movement');
    }
  },

  // Mock data for development
  generateMockInventoryData() {
    return {
      productStock: [
        {
          id: 1,
          product_name: 'Basmati Rice Premium',
          category: 'processed_rice',
          current_stock: 2500,
          unit: 'kg',
          reorder_level: 500,
          max_stock: 5000,
          last_updated: new Date().toISOString(),
          status: 'in_stock'
        },
        {
          id: 2,
          product_name: 'Broken Rice',
          category: 'broken_rice',
          current_stock: 150,
          unit: 'kg',
          reorder_level: 200,
          max_stock: 1000,
          last_updated: new Date().toISOString(),
          status: 'low_stock'
        },
        {
          id: 3,
          product_name: 'Rice Bran',
          category: 'rice_bran',
          current_stock: 800,
          unit: 'kg',
          reorder_level: 100,
          max_stock: 1500,
          last_updated: new Date().toISOString(),
          status: 'in_stock'
        }
      ],
      paddyStock: [
        {
          id: 1,
          variety: 'Basmati 1121',
          farmer_name: 'Rajesh Kumar',
          quantity: 5000,
          unit: 'kg',
          moisture_content: 12.5,
          quality_grade: 'A',
          purchase_date: '2024-01-15',
          storage_location: 'Warehouse A',
          status: 'stored'
        },
        {
          id: 2,
          variety: 'IR64',
          farmer_name: 'Suresh Patel',
          quantity: 3200,
          unit: 'kg',
          moisture_content: 13.2,
          quality_grade: 'B',
          purchase_date: '2024-01-18',
          storage_location: 'Warehouse B',
          status: 'processing'
        }
      ],
      analytics: {
        totalProductStock: 3450,
        totalPaddyStock: 8200,
        lowStockItems: 1,
        stockTurnover: 4.2,
        warehouseUtilization: 78.5,
        monthlyConsumption: 12500
      }
    };
  }
};

export default inventoryService;
