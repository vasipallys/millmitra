/** User-visible message from an Axios/React Query error. Never dumps tokens. */
export function getApiErrorMessage(error, fallback = 'Could not complete that request') {
  if (!error) return fallback;
  const data = error.response?.data;
  if (typeof data?.message === 'string' && data.message.trim()) {
    return data.error_id ? `${data.message} (ref ${data.error_id})` : data.message;
  }
  if (typeof data?.error === 'string' && data.error.trim()) {
    return data.error;
  }
  if (error.userMessage) return error.userMessage;
  if (error.message && !/request failed with status code/i.test(error.message)) {
    return error.message;
  }
  if (!error.response) {
    return 'Cannot reach the mill server. Confirm it is running on port 5000.';
  }
  return fallback;
}
