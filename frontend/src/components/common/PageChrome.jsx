import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Typography,
} from '@mui/material';
import { getApiErrorMessage } from '../../utils/apiError';
import { useI18n } from '../../i18n/I18nContext';

export function PageShell({ children }) {
  return (
    <Box
      sx={{
        p: { xs: 2, sm: 3 },
        maxWidth: 1600,
        mx: 'auto',
        width: '100%',
        overflowX: 'hidden',
      }}
    >
      {children}
    </Box>
  );
}

export function PageHeader({ title, subtitle, actions }) {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: { xs: 'flex-start', sm: 'center' },
        flexDirection: { xs: 'column', sm: 'row' },
        gap: 2,
        mb: 3,
      }}
    >
      <Box>
        <Typography variant="h4" component="h1" fontWeight="bold">
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {subtitle}
          </Typography>
        )}
      </Box>
      {actions && (
        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: 1,
            width: { xs: '100%', sm: 'auto' },
            '& .MuiButton-root': {
              flex: { xs: '1 1 auto', sm: '0 0 auto' },
              minHeight: 40,
            },
          }}
        >
          {actions}
        </Box>
      )}
    </Box>
  );
}

export function PageLoading({ label }) {
  const { t } = useI18n();
  const text = label || t('loadingMill');
  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight={280}
      gap={2}
      role="status"
      aria-live="polite"
    >
      <CircularProgress />
      <Typography variant="body2" color="text.secondary">
        {text}
      </Typography>
    </Box>
  );
}

export function PageEmpty({ title, description, action }) {
  return (
    <Box
      sx={{
        textAlign: 'center',
        py: 6,
        px: 2,
        border: '1px dashed',
        borderColor: 'divider',
        borderRadius: 2,
        bgcolor: 'background.paper',
      }}
    >
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      {description && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: action ? 2 : 0 }}>
          {description}
        </Typography>
      )}
      {action}
    </Box>
  );
}

export function QueryErrorAlert({ error, onRetry, entity = 'data' }) {
  const { t } = useI18n();
  if (!error) return null;
  return (
    <Alert
      severity="error"
      sx={{ mb: 2 }}
      action={
        onRetry ? (
          <Button color="inherit" size="small" onClick={onRetry}>
            {t('retry')}
          </Button>
        ) : null
      }
    >
      {getApiErrorMessage(error, t('couldNotLoad', { entity }))}
    </Alert>
  );
}
