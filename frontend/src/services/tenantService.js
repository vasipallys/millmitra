import api from './api';

export const tenantService = {
  async mine() {
    const response = await api.get('/tenants/mine');
    return response.data;
  },
  async switchTo(tenantId) {
    const response = await api.post(`/tenants/${tenantId}/switch`);
    return response.data;
  },
};
