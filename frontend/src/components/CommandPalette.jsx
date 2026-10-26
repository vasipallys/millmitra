import { useEffect, useMemo, useState } from 'react';
import { Dialog, DialogContent, List, ListItemButton, ListItemText, TextField, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useI18n } from '../i18n/I18nContext';
import { can, storedUser } from '../utils/permissions';

const COMMANDS = [
  { id: 'dashboard', path: '/dashboard', textKey: 'dashboard', permission: 'dashboard' },
  { id: 'mill', path: '/mill-flow', textKey: 'millFlow', permission: 'mill_flow' },
  { id: 'farmers', path: '/farmers', textKey: 'farmers', permission: 'farmers' },
  { id: 'register', path: '/farmers', textKey: 'registerFarmer', permission: 'farmers', extra: 'register-farmer' },
  { id: 'inventory', path: '/inventory', textKey: 'inventory', permission: 'inventory' },
  { id: 'production', path: '/production', textKey: 'production', permission: 'production' },
  { id: 'sales', path: '/sales', textKey: 'sales', permission: 'sales' },
  { id: 'customers', path: '/customers', textKey: 'customers', permission: 'customers' },
  { id: 'finance', path: '/finance', textKey: 'finance', permission: 'finance' },
  { id: 'quality', path: '/quality-control', textKey: 'qualityControl', permission: 'quality' },
  { id: 'iiot', path: '/iiot', textKey: 'iiot', permission: 'iiot' },
  { id: 'settings', path: '/settings', textKey: 'settings', permission: 'settings' },
  { id: 'users', path: '/users', textKey: 'usersTitle', permission: 'users' },
  { id: 'lookups', path: '/lookups', textKey: 'lookupsTitle', permission: 'lookups' },
  { id: 'forms', path: '/forms/inspection', textKey: 'dynamicForms', permission: 'dashboard' },
];

export default function CommandPalette({ open, onClose }) {
  const { t } = useI18n();
  const navigate = useNavigate();
  const user = storedUser();
  const [query, setQuery] = useState('');

  useEffect(() => {
    if (open) setQuery('');
  }, [open]);

  const items = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return COMMANDS
      .filter((item) => can(user, item.permission))
      .filter((item) => {
        if (!needle) return true;
        return t(item.textKey).toLowerCase().includes(needle) || item.path.includes(needle);
      });
  }, [query, t, user]);

  const go = (item) => {
    navigate(item.path);
    if (item.extra) {
      window.dispatchEvent(new CustomEvent('mm-open', { detail: item.extra }));
    }
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm" aria-label={t('commandPalette')}>
      <DialogContent>
        <Typography variant="subtitle2" sx={{ mb: 1 }}>{t('commandPalette')}</Typography>
        <TextField
          autoFocus
          fullWidth
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          label={t('searchCommand')}
          helperText={t('commandPaletteHint')}
          inputProps={{ 'data-testid': 'command-palette-query' }}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && items[0]) go(items[0]);
          }}
        />
        <List data-testid="command-palette-list">
          {items.map((item) => (
            <ListItemButton key={item.id} onClick={() => go(item)}>
              <ListItemText primary={t(item.textKey)} secondary={item.path} />
            </ListItemButton>
          ))}
        </List>
      </DialogContent>
    </Dialog>
  );
}

export function useCommandPalette() {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const onKey = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setOpen(true);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);
  return { open, setOpen };
}
