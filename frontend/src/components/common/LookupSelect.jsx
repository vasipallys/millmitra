import { useEffect } from 'react';
import {
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
  CircularProgress,
  Box,
} from '@mui/material';
import { useLookup } from '../../hooks/useLookup';
import { useI18n } from '../../i18n/I18nContext';

export function LookupFilterSelect({
  group,
  value,
  onChange,
  label,
  allValue = 'all',
  allLabel,
  fullWidth = true,
}) {
  const { t } = useI18n();
  const { options, isLoading, labelOf } = useLookup(group);
  return (
    <FormControl fullWidth={fullWidth} disabled={isLoading}>
      {label ? <InputLabel id={`filter-${group}-label`}>{label}</InputLabel> : null}
      <Select
        labelId={label ? `filter-${group}-label` : undefined}
        label={label}
        value={value}
        onChange={onChange}
      >
        <MenuItem value={allValue}>{allLabel || t('lookupAll')}</MenuItem>
        {options.map((item) => (
          <MenuItem key={`${group}-${item.value}`} value={item.value}>
            {labelOf(item)}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

export default function LookupSelect({
  group,
  value,
  onChange,
  label,
  name,
  required = false,
  fullWidth = true,
  disabled = false,
  helperText,
  error = false,
  MenuProps,
  includeValue,
  size,
  sx,
  id,
}) {
  const { t } = useI18n();
  const { options, isLoading, isError, labelOf } = useLookup(group);
  const current = value == null ? '' : String(value);
  const extra = includeValue || current;
  const hasCurrent = extra && options.some((item) => String(item.value) === String(extra));
  const items = hasCurrent || !extra
    ? options
    : [...options, { value: extra, label: extra, labels: { en: extra, hi: extra, te: extra } }];
  const emptyAfterLoad = !isLoading && !isError && options.length === 0;
  const selectValue = items.some((item) => String(item.value) === current) ? current : (items[0]?.value || current);
  const labelId = id || `lookup-${group}`;

  useEffect(() => {
    if (isLoading || !options.length || !onChange) return;
    const known = options.some((item) => String(item.value) === current) || (extra && String(extra) === current);
    if (!current || !known) {
      onChange({ target: { name: name || group, value: options[0].value } });
    }
  }, [isLoading, options, current, extra, group, name, onChange]);

  return (
    <FormControl fullWidth={fullWidth} required={required} error={error || isError} disabled={disabled} size={size} sx={sx}>
      {label ? <InputLabel id={`${labelId}-label`}>{label}</InputLabel> : null}
      <Select
        labelId={label ? `${labelId}-label` : undefined}
        label={label}
        name={name}
        value={selectValue}
        onChange={onChange}
        MenuProps={MenuProps}
        disabled={disabled || isLoading}
        displayEmpty={false}
      >
        {items.map((item) => (
          <MenuItem key={`${group}-${item.value}`} value={item.value}>
            {labelOf(item)}
          </MenuItem>
        ))}
      </Select>
      {isLoading && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
          <CircularProgress size={12} />
          <FormHelperText sx={{ m: 0 }}>{t('loading')}</FormHelperText>
        </Box>
      )}
      {!isLoading && emptyAfterLoad && (
        <FormHelperText>{t('lookupAskAdmin')}</FormHelperText>
      )}
      {!isLoading && isError && (
        <FormHelperText>{t('lookupLoadError')}</FormHelperText>
      )}
      {!isLoading && !emptyAfterLoad && helperText ? (
        <FormHelperText>{helperText}</FormHelperText>
      ) : null}
    </FormControl>
  );
}
