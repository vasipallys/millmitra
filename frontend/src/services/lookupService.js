import api from './api';

export const lookupService = {
  async listActive(group) {
    const response = await api.get('/lookups', { params: group ? { group } : {} });
    return response.data;
  },
  async listAdmin(group) {
    const response = await api.get('/lookups/admin', { params: group ? { group } : {} });
    return response.data;
  },
  async create(payload) {
    const response = await api.post('/lookups', payload);
    return response.data;
  },
  async update(id, payload) {
    const response = await api.put(`/lookups/${id}`, payload);
    return response.data;
  },
  async activate(id) {
    const response = await api.post(`/lookups/${id}/activate`);
    return response.data;
  },
  async deactivate(id) {
    const response = await api.post(`/lookups/${id}/deactivate`);
    return response.data;
  },
};

export function optionLabel(option, locale = 'en') {
  if (!option) return '';
  return option.labels?.[locale] || option.label || option.value || '';
}
