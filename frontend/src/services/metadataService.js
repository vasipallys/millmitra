import api from './api';

export const metadataService = {
  getEntities: async () => (await api.get('/metadata/entities')).data,
  getFields: async (entity) => (await api.get('/metadata/fields', { params: { entity } })).data,
  createField: async (payload) => (await api.post('/metadata/fields', payload)).data,
  updateField: async (id, payload) => (await api.put(`/metadata/fields/${id}`, payload)).data,
  deleteField: async (id) => (await api.delete(`/metadata/fields/${id}`)).data,
  getForm: async (entity) => (await api.get(`/metadata/forms/${entity}`)).data,
  saveForm: async (entity, layout) => (await api.put(`/metadata/forms/${entity}`, { layout })).data,
  getValues: async (entity, recordId) => (await api.get(`/metadata/values/${entity}/${recordId}`)).data,
  saveValues: async (entity, recordId, values) => (
    await api.put(`/metadata/values/${entity}/${recordId}`, { values })
  ).data,
  getDashboardLayout: async () => (await api.get('/metadata/dashboard-layout')).data,
  saveDashboardLayout: async (widgets) => (
    await api.put('/metadata/dashboard-layout', { widgets })
  ).data,
  listRecords: async (entity) => (await api.get(`/metadata/records/${entity}`)).data,
  createRecord: async (entity, values) => (
    await api.post(`/metadata/records/${entity}`, { values })
  ).data,
};
