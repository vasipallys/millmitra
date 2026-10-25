/** IndexedDB outbox for IIoT manual entries. Works without a service worker. */

import { isDevRuntime } from './pwaRuntime';

const DB_NAME = 'millmitra-offline';
const STORE = 'iiot-manual';

function fingerprint(payload) {
  return JSON.stringify({
    device_id: payload.device_id,
    metric: payload.metric,
    value: payload.value,
    reason: payload.reason,
  });
}

function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 2);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: 'id', autoIncrement: true });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function enqueueManual(payload) {
  const rows = await listQueued();
  const mark = fingerprint(payload);
  if (rows.some((row) => fingerprint(row.payload || {}) === mark && row.status !== 'failed')) {
    return null;
  }
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    const request = tx.objectStore(STORE).add({
      payload,
      createdAt: Date.now(),
      attempts: 0,
      status: 'queued',
      lastError: '',
      nextRetryAt: 0,
    });
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function listQueued() {
  const db = await openDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly');
    const request = tx.objectStore(STORE).getAll();
    request.onsuccess = () => resolve(request.result || []);
    request.onerror = () => reject(request.error);
  });
}

export async function queuedCount() {
  const rows = await listQueued();
  return rows.filter((row) => row.status !== 'sent').length;
}

export async function failedItems() {
  const rows = await listQueued();
  return rows.filter((row) => row.status === 'failed');
}

export async function flushQueue(sender) {
  const rows = await listQueued();
  const db = await openDb();
  let sent = 0;
  const now = Date.now();
  for (const row of rows) {
    if (row.status === 'sent') continue;
    if (row.nextRetryAt && row.nextRetryAt > now) continue;
    try {
      await sender(row.payload);
      await updateRow(db, { ...row, status: 'sent' });
      await deleteRow(db, row.id);
      sent += 1;
    } catch (error) {
      const attempts = (row.attempts || 0) + 1;
      const backoff = Math.min(60_000, 1000 * (2 ** attempts));
      await updateRow(db, {
        ...row,
        attempts,
        status: attempts >= 5 ? 'failed' : 'queued',
        lastError: error?.response?.data?.message || error?.message || 'sync failed',
        nextRetryAt: Date.now() + backoff,
      });
    }
  }
  return sent;
}

function updateRow(db, row) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    tx.objectStore(STORE).put(row);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

function deleteRow(db, id) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite');
    tx.objectStore(STORE).delete(id);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

export function requestBackgroundSync() {
  if (isDevRuntime()) {
    return Promise.resolve(false);
  }
  if (!('serviceWorker' in navigator) || !navigator.serviceWorker.controller) {
    return Promise.resolve(false);
  }
  return navigator.serviceWorker.ready
    .then((reg) => {
      if (reg.sync) {
        return reg.sync.register('mm-iiot-manual');
      }
      return false;
    })
    .then(() => true)
    .catch(() => false);
}
