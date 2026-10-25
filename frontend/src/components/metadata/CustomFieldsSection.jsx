import { useEffect, useState } from 'react';
import { Box, Checkbox, FormControlLabel, MenuItem, TextField, Typography } from '@mui/material';
import { useI18n } from '../../i18n/I18nContext';
import { metadataService } from '../../services/metadataService';

function labelFor(field, locale) {
  if (locale === 'hi' && field.label_hi) return field.label_hi;
  if (locale === 'te' && field.label_te) return field.label_te;
  return field.label_en || field.name;
}

export default function CustomFieldsSection({
  entity,
  recordId,
  values,
  onChange,
  persistOnChange = false,
}) {
  const { t, locale } = useI18n();
  const [fields, setFields] = useState([]);
  const [localValues, setLocalValues] = useState(values || {});

  useEffect(() => {
    let cancelled = false;
    metadataService.getForm(entity).then((payload) => {
      if (cancelled) return;
      const next = payload.layout?.fields?.length ? payload.layout.fields : (payload.fields || []);
      setFields(next);
    }).catch(() => {
      if (!cancelled) setFields([]);
    });
    return () => { cancelled = true; };
  }, [entity]);

  useEffect(() => {
    if (!recordId) return undefined;
    let cancelled = false;
    metadataService.getValues(entity, recordId).then((payload) => {
      if (!cancelled) {
        const next = payload.values || {};
        setLocalValues(next);
        onChange?.(next);
      }
    }).catch(() => {});
    return () => { cancelled = true; };
  }, [entity, recordId]);

  if (!fields.length) {
    return null;
  }

  const update = async (name, value) => {
    const next = { ...localValues, [name]: value };
    setLocalValues(next);
    onChange?.(next);
    if (persistOnChange && recordId) {
      try {
        await metadataService.saveValues(entity, recordId, next);
      } catch {
        // keep local values
      }
    }
  };

  return (
    <Box sx={{ mt: 2 }} data-testid={`custom-fields-${entity}`}>
      <Typography variant="subtitle1" sx={{ mb: 1 }}>{t('customFields')}</Typography>
      {fields.map((field) => {
        const name = field.name;
        const value = localValues[name] ?? '';
        if (field.field_type === 'boolean') {
          return (
            <FormControlLabel
              key={name}
              control={(
                <Checkbox
                  checked={Boolean(value)}
                  onChange={(event) => update(name, event.target.checked)}
                />
              )}
              label={labelFor(field, locale)}
            />
          );
        }
        if (field.field_type === 'select' || field.lookup_group) {
          return (
            <TextField
              key={name}
              select
              fullWidth
              sx={{ mb: 1.5 }}
              required={Boolean(field.required)}
              label={labelFor(field, locale)}
              value={value}
              onChange={(event) => update(name, event.target.value)}
            >
              <MenuItem value="">{t('select')}</MenuItem>
              {(field.options || []).map((option) => (
                <MenuItem key={option.value || option} value={option.value || option}>
                  {option.label || option}
                </MenuItem>
              ))}
            </TextField>
          );
        }
        return (
          <TextField
            key={name}
            fullWidth
            sx={{ mb: 1.5 }}
            required={Boolean(field.required)}
            type={field.field_type === 'number' ? 'number' : 'text'}
            label={labelFor(field, locale)}
            value={value}
            onChange={(event) => update(name, field.field_type === 'number' ? event.target.value : event.target.value)}
          />
        );
      })}
    </Box>
  );
}
