import api from './api';

export const userAdminService = {
  async listUsers() {
    const response = await api.get('/users');
    return response.data;
  },
  async createUser(payload) {
    const response = await api.post('/users', {
      username: payload.username,
      password: payload.password,
      role: payload.role,
    });
    return response.data;
  },
  async updateUser(id, payload) {
    const response = await api.patch(`/users/${id}`, payload);
    return response.data;
  },
  async getAccess() {
    const response = await api.get('/access');
    return response.data;
  },
  async saveAccess(payload) {
    const response = await api.put('/access', payload);
    return response.data;
  },
};
