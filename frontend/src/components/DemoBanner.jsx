import { Alert } from '@mui/material';
import { useI18n } from '../i18n/I18nContext';

const DemoBanner = ({ title, mode = 'actual' }) => {
  const { t } = useI18n();
  const heading = title || t('previewGroup');
  return (
    <Alert severity={mode === 'sample' ? 'warning' : 'info'} sx={{ mb: 3 }}>
      {mode === 'sample'
        ? t('previewSampleBanner', { title: heading })
        : t('previewActualBanner', { title: heading })}
    </Alert>
  );
};

export default DemoBanner;
