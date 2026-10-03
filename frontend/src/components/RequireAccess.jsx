import { Alert, Box, Typography } from '@mui/material';
import { useI18n } from '../i18n/I18nContext';
import { can } from '../utils/permissions';

export default function RequireAccess({ user, permission, children }) {
  const { t } = useI18n();
  if (!permission || can(user, permission)) {
    return children;
  }
  return (
    <Box sx={{ p: 3, maxWidth: 560 }}>
      <Alert severity="warning" role="alert">
        <Typography variant="h6">{t('deniedTitle')}</Typography>
        <Typography variant="body2">{t('deniedBody')}</Typography>
      </Alert>
    </Box>
  );
}
