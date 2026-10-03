import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { useI18n } from './I18nContext';

export default function LanguageSwitcher({ size = 'small', light = false }) {
  const { locale, setLocale, locales, t } = useI18n();
  return (
    <FormControl size={size} sx={{ minWidth: 120 }}>
      <InputLabel
        id="millmitra-language-label"
        sx={light ? { color: 'inherit' } : undefined}
      >
        {t('language')}
      </InputLabel>
      <Select
        labelId="millmitra-language-label"
        label={t('language')}
        value={locale}
        onChange={(event) => setLocale(event.target.value)}
        sx={light ? { color: 'inherit' } : undefined}
      >
        {locales.map((item) => (
          <MenuItem key={item.code} value={item.code}>{item.label}</MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
