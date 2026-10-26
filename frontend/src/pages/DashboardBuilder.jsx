import { useEffect, useMemo, useState } from 'react';
import { Alert, Box, Button, Card, CardContent, MenuItem, TextField, Typography } from '@mui/material';
import { PageHeader, PageShell } from '../components/common/PageChrome';
import { useI18n } from '../i18n/I18nContext';
import { dashboardService } from '../services/dashboardService';
import { metadataService } from '../services/metadataService';
import '../composable.css';

export default function DashboardBuilder() {
  const { t } = useI18n();
  const fallbackWidgets = useMemo(() => ([
    { id: 'production', label: t('widgetProduction'), size: 6 },
    { id: 'inventory', label: t('widgetInventory'), size: 6 },
    { id: 'sales', label: t('widgetSales'), size: 6 },
    { id: 'farmers', label: t('widgetFarmers'), size: 6 },
    { id: 'quality', label: t('widgetQuality'), size: 6 },
  ]), [t]);
  const [available, setAvailable] = useState(fallbackWidgets);
  const [widgets, setWidgets] = useState(fallbackWidgets);
  const [addId, setAddId] = useState('production');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      dashboardService.getWidgets().catch(() => ({ widgets: [] })),
      metadataService.getDashboardLayout().catch(() => ({ layout: { widgets: [] } })),
    ]).then(([live, saved]) => {
      const liveList = (live.widgets || []).map((item) => ({
        id: item.id,
        label: item.title || item.name || item.id,
        size: item.size || 6,
      }));
      setAvailable(liveList.length ? liveList : fallbackWidgets);
      const persisted = saved.layout?.widgets || [];
      if (persisted.length) {
        setWidgets(persisted.map((item) => (
          typeof item === 'string'
            ? { id: item, label: item, size: 6 }
            : { id: item.id, label: item.label || item.id, size: item.size || 6 }
        )));
      } else {
        setWidgets(liveList.length ? liveList : fallbackWidgets);
      }
    }).catch((err) => {
      setError(err.response?.data?.message || err.message);
      setAvailable(fallbackWidgets);
      setWidgets(fallbackWidgets);
    }).finally(() => setLoading(false));
  }, [fallbackWidgets]);

  const move = (index, delta) => {
    setWidgets((current) => {
      const next = [...current];
      const target = index + delta;
      if (target < 0 || target >= next.length) return current;
      const [item] = next.splice(index, 1);
      next.splice(target, 0, item);
      return next;
    });
  };

  const save = async () => {
    setMessage('');
    setError('');
    try {
      await metadataService.saveDashboardLayout(widgets);
      await dashboardService.saveCustomization({ widgets: widgets.map((item) => item.id) });
      setMessage(t('layoutSaved'));
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    }
  };

  return (
    <PageShell>
      <PageHeader title={t('dashboardBuilder')} subtitle={t('dashboardBuilderSubtitle')} pageKey="dashboard" />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {loading && <Typography sx={{ mb: 2 }}>{t('loading')}</Typography>}
      {!loading && !widgets.length && (
        <Typography color="text.secondary" sx={{ mb: 2 }}>{t('noWidgetsYet')}</Typography>
      )}
      <Card>
        <CardContent>
          {widgets.map((widget, index) => (
            <Box key={`${widget.id}-${index}`} sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 1 }}>
              <Typography sx={{ minWidth: 180 }}>{widget.label || widget.id}</Typography>
              <TextField
                size="small"
                type="number"
                label={t('size')}
                value={widget.size || 6}
                onChange={(e) => setWidgets((current) => current.map((item, i) => (
                  i === index ? { ...item, size: Number(e.target.value) || 6 } : item
                )))}
                sx={{ width: 100 }}
              />
              <Button onClick={() => move(index, -1)}>{t('moveUp')}</Button>
              <Button onClick={() => move(index, 1)}>{t('moveDown')}</Button>
              <Button color="error" onClick={() => setWidgets((current) => current.filter((_, i) => i !== index))}>{t('remove')}</Button>
            </Box>
          ))}
          <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
            <TextField select size="small" label={t('widget')} value={addId} onChange={(e) => setAddId(e.target.value)} sx={{ minWidth: 200 }}>
              {available.map((item) => <MenuItem key={item.id} value={item.id}>{item.label}</MenuItem>)}
            </TextField>
            <Button variant="outlined" onClick={() => {
              const found = available.find((item) => item.id === addId) || { id: addId, label: addId, size: 6 };
              setWidgets((current) => [...current, found]);
            }}>{t('addWidget')}</Button>
            <Button variant="contained" onClick={save}>{t('save')}</Button>
          </Box>
          {message && <Typography color="success.main" sx={{ mt: 2 }}>{message}</Typography>}
        </CardContent>
      </Card>
    </PageShell>
  );
}
