import { useState } from 'react';
import { Button, Popover, Typography, Box, List, ListItem, ListItemText } from '@mui/material';
import HelpOutline from '@mui/icons-material/HelpOutline';
import { useI18n } from '../../i18n/I18nContext';

export const PAGE_TIPS = {
  dashboard: ['tipDashboard1', 'tipDashboard2', 'tipDashboard3'],
  millFlow: ['tipMillFlow1', 'tipMillFlow2'],
  farmers: ['tipFarmers1', 'tipFarmers2'],
  inventory: ['tipInventory1', 'tipInventory2'],
  production: ['tipProduction1', 'tipProduction2'],
  sales: ['tipSales1', 'tipSales2'],
  customers: ['tipCustomers1', 'tipCustomers2'],
  finance: ['tipFinance1', 'tipFinance2'],
  quality: ['tipQuality1', 'tipQuality2'],
  settings: ['tipSettings1', 'tipSettings2'],
  users: ['tipUsers1', 'tipUsers2'],
  lookups: ['tipLookups1', 'tipLookups2'],
  iiot: ['tipIiot1', 'tipIiot2'],
  formBuilder: ['tipFormBuilder1', 'tipFormBuilder2'],
  dynamicForms: ['tipDynamic1', 'tipDynamic2'],
  access: ['tipAccess1', 'tipAccess2'],
  financialIntelligence: ['tipFi1', 'tipFi2'],
  complianceGst: ['tipGst1', 'tipGst2'],
  analytics: ['tipAnalytics1', 'tipAnalytics2'],
  reporting: ['tipReporting1', 'tipReporting2'],
  notifications: ['tipNotifications1', 'tipNotifications2'],
};

export default function HelpTips({ pageKey }) {
  const { t } = useI18n();
  const keys = PAGE_TIPS[pageKey] || [];
  const [anchor, setAnchor] = useState(null);
  if (!keys.length) return null;
  return (
    <>
      <Button
        aria-label={t('pageHelp')}
        onClick={(event) => setAnchor(event.currentTarget)}
        size="small"
        startIcon={<HelpOutline />}
        sx={{ minHeight: 44 }}
      >
        {t('pageHelp')}
      </Button>
      <Popover
        open={Boolean(anchor)}
        anchorEl={anchor}
        onClose={() => setAnchor(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Box sx={{ p: 2, maxWidth: 320 }} role="dialog" aria-label={t('pageHelp')}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>{t('pageHelp')}</Typography>
          <List dense>
            {keys.map((key) => (
              <ListItem key={key} sx={{ px: 0 }}>
                <ListItemText primary={t(key)} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Popover>
    </>
  );
}
