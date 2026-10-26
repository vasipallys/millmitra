import { useEffect, useState } from 'react';
import { Alert, Box, Button, Checkbox, FormControlLabel, Paper, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useI18n } from '../i18n/I18nContext';
import { authService } from '../services/authService';
import { storedUser } from '../utils/permissions';

const STEPS = [
  { id: 'farmer', textKey: 'gettingStartedFarmer', path: '/farmers' },
  { id: 'buy', textKey: 'gettingStartedBuy', path: '/farmers' },
  { id: 'mill', textKey: 'gettingStartedMill', path: '/mill-flow' },
  { id: 'sell', textKey: 'gettingStartedSell', path: '/sales' },
];

export default function GettingStarted() {
  const { t } = useI18n();
  const navigate = useNavigate();
  const user = storedUser();
  const prefs = user?.preferences || {};
  const [hidden, setHidden] = useState(Boolean(prefs.getting_started_dismissed));
  const [done, setDone] = useState(prefs.getting_started_done || []);

  useEffect(() => {
    setHidden(Boolean(user?.preferences?.getting_started_dismissed));
    setDone(user?.preferences?.getting_started_done || []);
  }, [user?.preferences?.getting_started_dismissed, user?.preferences?.getting_started_done]);

  if (hidden) return null;

  const persist = (patch) => {
    authService.updatePreferences(patch).catch(() => {});
  };

  const toggle = (id) => {
    const next = done.includes(id) ? done.filter((item) => item !== id) : [...done, id];
    setDone(next);
    persist({ getting_started_done: next });
  };

  const dismiss = () => {
    setHidden(true);
    persist({ getting_started_dismissed: true });
  };

  return (
    <Paper sx={{ p: 2, mb: 3 }} data-testid="getting-started">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h6">{t('gettingStarted')}</Typography>
        <Button onClick={dismiss} size="small">{t('dismissChecklist')}</Button>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {t('gettingStartedHelp')}
      </Typography>
      {STEPS.map((step) => (
        <FormControlLabel
          key={step.id}
          sx={{ display: 'flex', mb: 0.5 }}
          control={(
            <Checkbox
              checked={done.includes(step.id)}
              onChange={() => toggle(step.id)}
            />
          )}
          label={(
            <Button variant="text" onClick={() => navigate(step.path)} sx={{ textTransform: 'none' }}>
              {t(step.textKey)}
            </Button>
          )}
        />
      ))}
      {done.length === STEPS.length && (
        <Alert severity="success" sx={{ mt: 1 }}>{t('checklistDone')}</Alert>
      )}
    </Paper>
  );
}
