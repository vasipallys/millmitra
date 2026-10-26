import { FormControl, InputLabel, MenuItem, Select } from '@mui/material';
import { useI18n } from './I18nContext';

export default function LanguageSwitcher({ size = 'small', light = false }) {
  const { locale, setLocale, locales, t } = useI18n();
  const currentLabel = locales.find((item) => item.code === locale)?.label || locale;
  return (
    <FormControl size={size} sx={{ minWidth: { xs: 88, sm: 120 }, maxWidth: { xs: 120, sm: 'none' } }} data-testid="language-switcher">
      <InputLabel
        id="millmitra-language-label"
        sx={light ? { color: 'inherit' } : { color: 'text.primary' }}
      >
        {t('language')}
      </InputLabel>
      <Select
        labelId="millmitra-language-label"
        label={t('language')}
        value={locale}
        onChange={(event) => setLocale(event.target.value)}
        renderValue={() => currentLabel}
        SelectDisplayProps={{
          'aria-label': `${t('language')} ${currentLabel}`,
        }}
        sx={light ? { color: 'inherit' } : { color: 'text.primary' }}
      >
        {locales.map((item) => (
          <MenuItem key={item.code} value={item.code}>{item.label}</MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
