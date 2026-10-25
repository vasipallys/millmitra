import { useEffect, useState } from 'react';
import {
  Alert, Box, Button, Card, CardContent, Checkbox, FormControlLabel, MenuItem,
  TextField, Typography,
} from '@mui/material';
import { PageHeader, PageShell } from '../components/common/PageChrome';
import { useI18n } from '../i18n/I18nContext';
import { metadataService } from '../services/metadataService';
import '../composable.css';

const FIELD_TYPES = ['text', 'number', 'boolean', 'select', 'date'];

const emptyField = () => ({
  name: '',
  field_type: 'text',
  required: false,
  lookup_group: '',
  label_en: '',
  label_hi: '',
  label_te: '',
});

export default function FormBuilder() {
  const { t } = useI18n();
  const [entities, setEntities] = useState([]);
  const [entity, setEntity] = useState('farmer');
  const [fields, setFields] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  const load = async (key) => {
    setLoading(true);
    setError('');
    try {
      const payload = await metadataService.getForm(key);
      const next = payload.layout?.fields?.length ? payload.layout.fields : (payload.fields || []);
      setFields(next.length ? next : []);
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    metadataService.getEntities().then((payload) => {
      setEntities(payload.entities || []);
    }).catch(() => setEntities([{ key: 'farmer', label: 'Farmer' }]));
  }, []);

  useEffect(() => {
    load(entity).catch(() => setFields([]));
  }, [entity]);

  const updateField = (index, patch) => {
    setFields((current) => current.map((item, i) => (i === index ? { ...item, ...patch } : item)));
  };

  const move = (index, delta) => {
    setFields((current) => {
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
    const layout = {
      fields: fields.filter((item) => item.name).map((item, index) => ({ ...item, sort_order: index })),
    };
    try {
      await metadataService.saveForm(entity, layout);
      setMessage(t('formSaved'));
    } catch (err) {
      setError(err.response?.data?.message || err.message);
    }
  };

  return (
    <PageShell>
      <PageHeader title={t('formBuilder')} subtitle={t('formBuilderSubtitle')} />
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {loading && <Typography sx={{ mb: 2 }}>{t('loading')}</Typography>}
      <Card>
        <CardContent>
          <TextField
            select
            label={t('entity')}
            value={entity}
            onChange={(event) => setEntity(event.target.value)}
            sx={{ minWidth: 220, mb: 2 }}
          >
            {(entities.length ? entities : [{ key: 'farmer', label: t('farmerEntity') }]).map((item) => (
              <MenuItem key={item.key} value={item.key}>{item.label || item.key}</MenuItem>
            ))}
          </TextField>
          {!loading && !fields.length && (
            <Typography color="text.secondary" sx={{ mb: 2 }}>{t('noFieldsYet')}</Typography>
          )}
          {fields.map((field, index) => (
            <Box key={`${field.name || 'new'}-${index}`} sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
              <TextField size="small" label={t('fieldName')} value={field.name || ''} onChange={(e) => updateField(index, { name: e.target.value })} />
              <TextField size="small" select label={t('fieldType')} value={field.field_type || 'text'} onChange={(e) => updateField(index, { field_type: e.target.value })} sx={{ minWidth: 120 }}>
                {FIELD_TYPES.map((type) => <MenuItem key={type} value={type}>{type}</MenuItem>)}
              </TextField>
              <TextField size="small" label={t('labelEn')} value={field.label_en || ''} onChange={(e) => updateField(index, { label_en: e.target.value })} />
              <TextField size="small" label={t('labelHi')} value={field.label_hi || ''} onChange={(e) => updateField(index, { label_hi: e.target.value })} />
              <TextField size="small" label={t('labelTe')} value={field.label_te || ''} onChange={(e) => updateField(index, { label_te: e.target.value })} />
              <TextField size="small" label={t('lookupGroup')} value={field.lookup_group || ''} onChange={(e) => updateField(index, { lookup_group: e.target.value })} />
              <FormControlLabel
                control={<Checkbox checked={Boolean(field.required)} onChange={(e) => updateField(index, { required: e.target.checked })} />}
                label={t('required')}
              />
              <Button onClick={() => move(index, -1)}>{t('moveUp')}</Button>
              <Button onClick={() => move(index, 1)}>{t('moveDown')}</Button>
              <Button color="error" onClick={() => setFields((current) => current.filter((_, i) => i !== index))}>{t('remove')}</Button>
            </Box>
          ))}
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button variant="outlined" onClick={() => setFields((current) => [...current, emptyField()])}>{t('addField')}</Button>
            <Button variant="contained" onClick={save} data-testid="save-form-layout">{t('save')}</Button>
          </Box>
          {message && <Typography color="success.main" sx={{ mt: 2 }}>{message}</Typography>}
        </CardContent>
      </Card>
    </PageShell>
  );
}
