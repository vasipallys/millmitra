import { useCallback, useEffect, useState } from 'react';
import {
  Alert, Box, Button, Card, CardContent, Dialog, DialogActions, DialogContent,
  DialogTitle, MenuItem, Table, TableBody, TableCell, TableHead, TableRow,
  TextField, Typography,
} from '@mui/material';
import { PageHeader, PageLoading, PageShell } from '../components/common/PageChrome';
import '../composable.css';
import { useI18n } from '../i18n/I18nContext';
import { iiotService } from '../services/iiotService';
import { can, storedUser } from '../utils/permissions';
import { enqueueManual, failedItems, flushQueue, queuedCount, requestBackgroundSync } from '../utils/offlineQueue';

export default function Iiot() {
  const { t } = useI18n();
  const user = storedUser();
  const canResolve = can(user, 'reconciliation');
  const [devices, setDevices] = useState([]);
  const [readings, setReadings] = useState([]);
  const [discrepancies, setDiscrepancies] = useState([]);
  const [queued, setQueued] = useState(0);
  const [failed, setFailed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState({ device_id: 'mill-dryer-1', metric: 'moisture_pct', value: '', reason: '' });
  const [resolveRow, setResolveRow] = useState(null);
  const [resolution, setResolution] = useState('');

  const refreshQueue = useCallback(async () => {
    setQueued(await queuedCount());
    setFailed(await failedItems());
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [devicePayload, readingPayload, discPayload] = await Promise.all([
        iiotService.getDevices(),
        iiotService.getReadings(),
        iiotService.getDiscrepancies(),
      ]);
      setDevices(devicePayload.devices || []);
      setReadings(readingPayload.readings || []);
      setDiscrepancies(discPayload.discrepancies || []);
      await refreshQueue();
    } finally {
      setLoading(false);
    }
  }, [refreshQueue]);

  const syncQueued = useCallback(async () => {
    if (!navigator.onLine) return;
    try {
      await flushQueue((payload) => iiotService.manual(payload));
      await load();
    } catch {
      await refreshQueue();
    }
  }, [load, refreshQueue]);

  useEffect(() => {
    load().catch((err) => setError(err.response?.data?.message || err.message));
  }, [load]);

  useEffect(() => {
    const onOnline = () => { syncQueued(); };
    window.addEventListener('online', onOnline);
    const onMessage = (event) => {
      if (event.data?.type === 'MM_SYNC_IIOT') syncQueued();
    };
    navigator.serviceWorker?.addEventListener?.('message', onMessage);
    return () => {
      window.removeEventListener('online', onOnline);
      navigator.serviceWorker?.removeEventListener?.('message', onMessage);
    };
  }, [syncQueued]);

  const submitManual = async () => {
    setError('');
    const payload = {
      device_id: form.device_id,
      metric: form.metric,
      value: Number(form.value),
      reason: form.reason,
    };
    if (!payload.reason) {
      setError(t('reasonRequired'));
      return;
    }
    if (!navigator.onLine) {
      await enqueueManual(payload);
      await requestBackgroundSync();
      await refreshQueue();
      return;
    }
    try {
      await iiotService.manual(payload);
      setForm((current) => ({ ...current, value: '', reason: '' }));
      await load();
    } catch (err) {
      if (!navigator.onLine) {
        await enqueueManual(payload);
        await refreshQueue();
      } else {
        setError(err.response?.data?.message || err.message);
      }
    }
  };

  const resolve = async () => {
    if (!resolveRow) return;
    await iiotService.resolve(resolveRow.id, resolution);
    setResolveRow(null);
    setResolution('');
    await load();
  };

  if (loading && !devices.length && !readings.length) {
    return <PageShell><PageLoading label={t('iiot')} /></PageShell>;
  }

  return (
    <PageShell>
      <PageHeader
        title={t('iiot')}
        subtitle={t('iiotSubtitle')}
        actions={(
          <Button variant="outlined" onClick={syncQueued}>{t('syncNow')} ({queued})</Button>
        )}
      />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {queued > 0 && <Alert severity="info" sx={{ mb: 2 }}>{t('queuedCount', { count: queued })}</Alert>}
      {failed.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {t('syncFailedCount', { count: failed.length })}
        </Alert>
      )}

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 1 }}>{t('manualEntry')}</Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <TextField
              select
              size="small"
              label={t('device')}
              value={form.device_id}
              onChange={(e) => setForm({ ...form, device_id: e.target.value })}
              sx={{ minWidth: 180 }}
            >
              {(devices.length ? devices : [{ device_id: 'mill-dryer-1', name: 'Mill dryer 1' }]).map((device) => (
                <MenuItem key={device.device_id} value={device.device_id}>{device.name || device.device_id}</MenuItem>
              ))}
            </TextField>
            <TextField size="small" label={t('metric')} value={form.metric} onChange={(e) => setForm({ ...form, metric: e.target.value })} />
            <TextField size="small" type="number" label={t('value')} value={form.value} onChange={(e) => setForm({ ...form, value: e.target.value })} />
            <TextField size="small" label={t('reason')} value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
            <Button variant="contained" onClick={submitManual} data-testid="iiot-manual-submit">{t('save')}</Button>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6">{t('devices')}</Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t('device')}</TableCell>
                <TableCell>{t('location')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {!devices.length && (
                <TableRow><TableCell colSpan={2}>{t('noDevices')}</TableCell></TableRow>
              )}
              {devices.map((device) => (
                <TableRow key={device.device_id}>
                  <TableCell>{device.name}</TableCell>
                  <TableCell>{device.location}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6">{t('latestReadings')}</Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t('device')}</TableCell>
                <TableCell>{t('metric')}</TableCell>
                <TableCell>{t('value')}</TableCell>
                <TableCell>{t('source')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {!readings.length && (
                <TableRow><TableCell colSpan={4}>{t('noReadings')}</TableCell></TableRow>
              )}
              {readings.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.device_id}</TableCell>
                  <TableCell>{row.metric}</TableCell>
                  <TableCell>{row.value}</TableCell>
                  <TableCell>{row.source}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6">{t('discrepancies')}</Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>{t('device')}</TableCell>
                <TableCell>{t('metric')}</TableCell>
                <TableCell>{t('sensorValue')}</TableCell>
                <TableCell>{t('manualValue')}</TableCell>
                <TableCell>{t('status')}</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {!discrepancies.length && (
                <TableRow><TableCell colSpan={6}>{t('noDiscrepancies')}</TableCell></TableRow>
              )}
              {discrepancies.map((row) => (
                <TableRow key={row.id}>
                  <TableCell>{row.device_id}</TableCell>
                  <TableCell>{row.metric}</TableCell>
                  <TableCell>{row.sensor_value}</TableCell>
                  <TableCell>{row.manual_value}</TableCell>
                  <TableCell>{row.status}</TableCell>
                  <TableCell>
                    {canResolve && row.status === 'open' && (
                      <Button size="small" onClick={() => setResolveRow(row)}>{t('resolve')}</Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={Boolean(resolveRow)} onClose={() => setResolveRow(null)}>
        <DialogTitle>{t('resolveDiscrepancy')}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            sx={{ mt: 1 }}
            label={t('resolution')}
            value={resolution}
            onChange={(e) => setResolution(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResolveRow(null)}>{t('cancel')}</Button>
          <Button variant="contained" onClick={resolve}>{t('resolve')}</Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
