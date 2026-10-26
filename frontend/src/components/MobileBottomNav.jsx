import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import InventoryIcon from '@mui/icons-material/Inventory';
import MenuIcon from '@mui/icons-material/Menu';
import { useLocation, useNavigate } from 'react-router-dom';
import { useI18n } from '../i18n/I18nContext';
import { can, storedUser } from '../utils/permissions';

const ITEMS = [
  { path: '/dashboard', textKey: 'dashboard', icon: <DashboardIcon />, permission: 'dashboard' },
  { path: '/mill-flow', textKey: 'millFlow', icon: <AccountTreeIcon />, permission: 'mill_flow' },
  { path: '/farmers', textKey: 'farmers', icon: <AgricultureIcon />, permission: 'farmers' },
  { path: '/inventory', textKey: 'inventory', icon: <InventoryIcon />, permission: 'inventory' },
];

export default function MobileBottomNav({ onOpenMenu }) {
  const { t } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();
  const user = storedUser();
  const visible = ITEMS.filter((item) => can(user, item.permission));
  const current = visible.find((item) => location.pathname.startsWith(item.path))?.path || '';

  return (
    <Paper
      elevation={8}
      sx={{
        display: { xs: 'block', md: 'none' },
        position: 'fixed',
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 1200,
      }}
    >
      <BottomNavigation
        value={current}
        onChange={(_, value) => {
          if (value === 'menu') {
            onOpenMenu?.();
            return;
          }
          navigate(value);
        }}
        showLabels
      >
        {visible.map((item) => (
          <BottomNavigationAction
            key={item.path}
            value={item.path}
            label={t(item.textKey)}
            icon={item.icon}
            sx={{ minWidth: 0, px: 0.5 }}
          />
        ))}
        <BottomNavigationAction value="menu" label={t('more')} icon={<MenuIcon />} />
      </BottomNavigation>
    </Paper>
  );
}
