import api from '../services/api';
import { parseLocalIntent } from './localIntent';

export function describeAssistantError(error) {
  const status = error?.response?.status;
  const data = error?.response?.data;
  const server = (typeof data?.message === 'string' && data.message.trim())
    || (typeof data?.error === 'string' && data.error.trim())
    || '';
  if (status === 404) {
    return 'HTTP 404: POST /api/ai/assistant is not loaded on this Flask process. Restart the mill API.';
  }
  if (status) {
    return server ? `HTTP ${status}: ${server}` : `HTTP ${status} from the mill API.`;
  }
  if (error?.code === 'ECONNABORTED') {
    return 'The mill API timed out.';
  }
  if (error?.code === 'ERR_NETWORK' || /network error/i.test(error?.message || '')) {
    return 'Network or CORS error reaching the mill API (no HTTP status).';
  }
  return error?.message || 'The assistant call failed with no HTTP status.';
}

export async function sendAssistantMessage({ message, route, language }) {
  try {
    const { data } = await api.post(
      '/ai/assistant',
      { message, route, language },
      { timeout: 35000 },
    );
    return {
      reply: data?.reply || '',
      actions: Array.isArray(data?.actions) ? data.actions : [],
      engine: data?.engine || 'local',
    };
  } catch (error) {
    error.assistantMessage = describeAssistantError(error);
    throw error;
  }
}

export function localAssistantFallback(message) {
  return parseLocalIntent(message);
}
