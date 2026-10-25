import api from './api';

export const iiotService = {
  getDevices: async () => (await api.get('/iiot/devices')).data,
  createDevice: async (payload) => (await api.post('/iiot/devices', payload)).data,
  getReadings: async (deviceId) => (
    await api.get('/iiot/readings', { params: deviceId ? { device_id: deviceId } : {} })
  ).data,
  manual: async (payload) => (await api.post('/iiot/manual', payload)).data,
  getDiscrepancies: async (status) => (
    await api.get('/iiot/discrepancies', { params: status ? { status } : {} })
  ).data,
  resolve: async (id, resolution) => (
    await api.post(`/iiot/discrepancies/${id}/resolve`, { resolution })
  ).data,
};
