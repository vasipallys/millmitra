import { useEffect, useState } from 'react';
import { Alert, Box, Button, Card, CardContent, Typography } from '@mui/material';
import { useParams } from 'react-router-dom';
import { PageHeader, PageLoading, PageShell } from '../components/common/PageChrome';
import CustomFieldsSection from '../components/metadata/CustomFieldsSection';
import { useI18n } from '../i18n/I18nContext';
import { metadataService } from '../services/metadataService';
import '../composable.css';

export default function DynamicEntity() {
  const { entity } = useParams();
  const { t } = useI18n();
  const [values, setValues] = useState({});
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const payload = await metadataService.listRecords(entity);
      setRecords(payload.records || []);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError('');
      try {
        const payload = await metadataService.listRecords(entity);
        if (!cancelled) setRecords(payload.records || []);
      } catch (err) {
        if (!cancelled) setError(err.response?.data?.message || err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [entity]);

  const save = async () => {
    setMessage('');
    try {
      await metadataService.createRecord(entity, values);
      setValues({});
      setMessage(t('recordSaved'));
      await load();
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    }
  };

  if (loading) {
    return <PageShell><PageLoading label={t('dynamicForms')} /></PageShell>;
  }

  return (
    <PageShell>
      <PageHeader title={t('dynamicForms')} subtitle={t('dynamicFormsSubtitle', { entity })} />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
      <Card sx={{ mb: 2 }} className="tw-max-w-4xl">
        <CardContent>
          <CustomFieldsSection entity={entity} values={values} onChange={setValues} />
          <Box sx={{ mt: 2 }}>
            <Button variant="contained" onClick={save} data-testid="dynamic-form-save">{t('save')}</Button>
          </Box>
        </CardContent>
      </Card>
      <Card>
        <CardContent>
          <Typography variant="h6">{t('records')}</Typography>
          {!records.length && <Typography color="text.secondary">{t('noRecords')}</Typography>}
          {records.map((row) => (
            <Box key={row.id} sx={{ py: 1 }} data-testid="dynamic-record">
              <Typography variant="body2">#{row.id} {JSON.stringify(row.values || {})}</Typography>
            </Box>
          ))}
        </CardContent>
      </Card>
    </PageShell>
  );
}
