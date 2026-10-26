import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Typography,
  Box,
  Divider,
  Chip,
} from '@mui/material';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import SecurityIcon from '@mui/icons-material/Security';
import ListAltIcon from '@mui/icons-material/ListAlt';
import DeviceHubIcon from '@mui/icons-material/DeviceHub';
import ViewQuiltIcon from '@mui/icons-material/ViewQuilt';
import WidgetsIcon from '@mui/icons-material/Widgets';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useI18n } from '../i18n/I18nContext';
import { can } from '../utils/permissions';
import {
  Dashboard as DashboardIcon,
  Agriculture as FarmersIcon,
  Inventory as InventoryIcon,
  PrecisionManufacturing as ProductionIcon,
  ShoppingCart as SalesIcon,
  AccountBalance as FinanceIcon,
  People as CustomersIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  SmartToy as AIIcon,
  HighQuality as QualityIcon,
  PsychologyAlt as FinancialIntelligenceIcon,
  Gavel as ComplianceIcon,
  AccountTree as MillFlowIcon,
} from '@mui/icons-material';

const drawerWidth = 240;

const MENU_GROUPS = [
  {
    key: 'navGroupDaily',
    items: [
      { textKey: 'dashboard', descKey: 'navDashboard', icon: <DashboardIcon />, path: '/dashboard', permission: 'dashboard' },
      { textKey: 'millFlow', descKey: 'navMillFlow', icon: <MillFlowIcon />, path: '/mill-flow', permission: 'mill_flow' },
      { textKey: 'farmers', descKey: 'navFarmers', icon: <FarmersIcon />, path: '/farmers', permission: 'farmers' },
      { textKey: 'iiot', descKey: 'navIiot', icon: <DeviceHubIcon />, path: '/iiot', permission: 'iiot' },
    ],
  },
  {
    key: 'navGroupOps',
    items: [
      { textKey: 'inventory', descKey: 'navInventory', icon: <InventoryIcon />, path: '/inventory', permission: 'inventory' },
      { textKey: 'production', descKey: 'navProduction', icon: <ProductionIcon />, path: '/production', permission: 'production' },
    ],
  },
  {
    key: 'navGroupSales',
    items: [
      { textKey: 'sales', descKey: 'navSales', icon: <SalesIcon />, path: '/sales', permission: 'sales' },
      { textKey: 'customers', descKey: 'navCustomers', icon: <CustomersIcon />, path: '/customers', permission: 'customers' },
      { textKey: 'finance', descKey: 'navFinance', icon: <FinanceIcon />, path: '/finance', permission: 'finance' },
    ],
  },
  {
    key: 'navGroupQuality',
    items: [
      { textKey: 'qualityControl', descKey: 'navProduction', icon: <QualityIcon />, path: '/quality-control', permission: 'quality' },
      { textKey: 'complianceGst', descKey: 'navFinance', icon: <ComplianceIcon />, path: '/compliance-gst', permission: 'preview' },
    ],
  },
  {
    key: 'navGroupAdmin',
    items: [
      { textKey: 'users', descKey: 'navUsers', icon: <AdminPanelSettingsIcon />, path: '/users', permission: 'users' },
      { textKey: 'access', descKey: 'navAccess', icon: <SecurityIcon />, path: '/access', permission: 'users' },
      { textKey: 'lookupsTitle', descKey: 'navLookups', icon: <ListAltIcon />, path: '/lookups', permission: 'lookups' },
      { textKey: 'formBuilder', descKey: 'navFormBuilder', icon: <ViewQuiltIcon />, path: '/form-builder', permission: 'metadata' },
      { textKey: 'dashboardBuilder', descKey: 'navDashboardBuilder', icon: <WidgetsIcon />, path: '/dashboard-builder', permission: 'dashboard' },
      { textKey: 'dynamicForms', descKey: 'navDynamicForms', icon: <ViewQuiltIcon />, path: '/forms/inspection', permission: 'dashboard' },
    ],
  },
  {
    key: 'navGroupSettings',
    items: [
      { textKey: 'settings', descKey: 'navSettings', icon: <SettingsIcon />, path: '/settings', permission: 'settings' },
    ],
  },
  {
    key: 'navGroupPreview',
    items: [
      { textKey: 'analytics', descKey: 'navDashboard', icon: <AnalyticsIcon />, path: '/analytics', permission: 'preview' },
      { textKey: 'financialIntelligence', descKey: 'navFinance', icon: <FinancialIntelligenceIcon />, path: '/financial-intelligence', permission: 'preview' },
    ],
  },
];

const Sidebar = ({ open, onClose, user }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useI18n();
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));
  const side = theme.direction === 'rtl' ? 'right' : 'left';
  const visibleGroups = MENU_GROUPS
    .map((group) => ({ ...group, items: group.items.filter((item) => can(user, item.permission)) }))
    .filter((group) => group.items.length);

  const handleNavigation = (path) => {
    navigate(path);
    if (!isDesktop) {
      onClose();
    }
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(`${path}/`);
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AIIcon sx={{ me: 1 }} />
          <Typography variant="h6" component="div">
            {t('appName')}
          </Typography>
        </Box>
        <Typography variant="body2">
          {t('navMillFlow')}
        </Typography>
      </Box>

      {/* User Info */}
      <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
        <Typography variant="subtitle2" color="text.primary">
          {t('welcome')}, {user?.username || 'User'}
        </Typography>
        <Chip 
          label={user?.role || 'Operator'} 
          size="small" 
          color="primary" 
          sx={{ mt: 0.5 }}
        />
      </Box>

      <Divider />

      {/* Navigation Menu */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {visibleGroups.map((group) => (
        <List
          key={group.key}
          sx={{ pt: 1 }}
          subheader={(
            <ListSubheader
              disableSticky
              sx={{
                lineHeight: 2,
                bgcolor: 'background.paper',
                color: 'text.primary',
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            >
              {t(group.key)}
            </ListSubheader>
          )}
        >
          {group.items.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                aria-current={isActive(item.path) ? 'page' : undefined}
                sx={{
                  mx: 1,
                  mb: 0.5,
                  borderRadius: 2,
                  borderInlineStart: '4px solid',
                  borderInlineStartColor: isActive(item.path) ? 'primary.dark' : 'transparent',
                  minHeight: 44,
                  '&.Mui-selected': {
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                  '&:hover': {
                    bgcolor: 'grey.100',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive(item.path) ? 'white' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={t(item.textKey)}
                  secondary={t(item.descKey)}
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                    fontWeight: isActive(item.path) ? 600 : 400,
                  }}
                  secondaryTypographyProps={{
                    fontSize: '0.75rem',
                    color: isActive(item.path) ? 'rgba(255,255,255,0.95)' : 'text.primary',
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        ))}
      </Box>

      <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
        <Typography variant="subtitle2">{t('appName')}</Typography>
        <Typography variant="caption" color="text.primary">
          {t('sidebarHint')}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant={isDesktop ? 'persistent' : 'temporary'}
      anchor={side}
      open={open}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
      data-testid="sidebar"
      sx={isDesktop ? {
        width: open ? drawerWidth : 0,
        flexShrink: 0,
        transition: 'width 0.3s ease-in-out',
        '& .MuiDrawer-paper': {
          position: 'relative',
          width: drawerWidth,
          boxSizing: 'border-box',
          borderInlineEnd: '1px solid',
          borderColor: 'divider',
          transition: 'transform 0.3s ease-in-out',
        },
      } : {
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;
