import { Button, ButtonGroup } from '@mui/material';
import { useI18n } from '../i18n/I18nContext';

const PreviewModeToggle = ({ mode, onChange }) => {
  const { t } = useI18n();
  return (
    <ButtonGroup variant="outlined" size="small" aria-label={t('previewGroup')}>
      <Button
        variant={mode === 'actual' ? 'contained' : 'outlined'}
        onClick={() => onChange('actual')}
      >
        {t('viewActual')}
      </Button>
      <Button
        variant={mode === 'sample' ? 'contained' : 'outlined'}
        onClick={() => onChange('sample')}
      >
        {t('viewSample')}
      </Button>
    </ButtonGroup>
  );
};

export default PreviewModeToggle;
