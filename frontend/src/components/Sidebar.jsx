import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Divider,
  Chip,
} from '@mui/material';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import SecurityIcon from '@mui/icons-material/Security';
import ListAltIcon from '@mui/icons-material/ListAlt';
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

const coreMenuItems = [
  { textKey: 'dashboard', descKey: 'navDashboard', icon: <DashboardIcon />, path: '/dashboard', permission: 'dashboard' },
  { textKey: 'millFlow', descKey: 'navMillFlow', icon: <MillFlowIcon />, path: '/mill-flow', permission: 'mill_flow' },
  { textKey: 'farmers', descKey: 'navFarmers', icon: <FarmersIcon />, path: '/farmers', permission: 'farmers' },
  { textKey: 'inventory', descKey: 'navInventory', icon: <InventoryIcon />, path: '/inventory', permission: 'inventory' },
  { textKey: 'production', descKey: 'navProduction', icon: <ProductionIcon />, path: '/production', permission: 'production' },
  { textKey: 'sales', descKey: 'navSales', icon: <SalesIcon />, path: '/sales', permission: 'sales' },
  { textKey: 'finance', descKey: 'navFinance', icon: <FinanceIcon />, path: '/finance', permission: 'finance' },
  { textKey: 'customers', descKey: 'navCustomers', icon: <CustomersIcon />, path: '/customers', permission: 'customers' },
  { textKey: 'settings', descKey: 'navSettings', icon: <SettingsIcon />, path: '/settings', permission: 'settings' },
  { textKey: 'users', descKey: 'navUsers', icon: <AdminPanelSettingsIcon />, path: '/users', permission: 'users' },
  { textKey: 'access', descKey: 'navAccess', icon: <SecurityIcon />, path: '/access', permission: 'users' },
  { textKey: 'lookupsTitle', descKey: 'navLookups', icon: <ListAltIcon />, path: '/lookups', permission: 'lookups' },
];

const previewMenuItems = [
  { textKey: 'analytics', descKey: 'navDashboard', icon: <AnalyticsIcon />, path: '/analytics', permission: 'preview' },
  { textKey: 'qualityControl', descKey: 'navProduction', icon: <QualityIcon />, path: '/quality-control', permission: 'quality' },
  { textKey: 'financialIntelligence', descKey: 'navFinance', icon: <FinancialIntelligenceIcon />, path: '/financial-intelligence', permission: 'preview' },
  { textKey: 'complianceGst', descKey: 'navFinance', icon: <ComplianceIcon />, path: '/compliance-gst', permission: 'preview' },
];

const Sidebar = ({ open, onClose, user }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useI18n();
  const visibleCore = coreMenuItems.filter((item) => can(user, item.permission));
  const visiblePreview = previewMenuItems.filter((item) => can(user, item.permission));

  const handleNavigation = (path) => {
    navigate(path);
    if (window.innerWidth < 768) {
      onClose();
    }
  };

  const isActive = (path) => {
    return location.pathname.startsWith(path);
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AIIcon sx={{ mr: 1 }} />
          <Typography variant="h6" component="div">
            {t('appName')}
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ opacity: 0.8 }}>
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
          variant="outlined"
          sx={{ mt: 0.5 }}
        />
      </Box>

      <Divider />

      {/* Navigation Menu */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List sx={{ pt: 1 }}>
          {visibleCore.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                aria-current={isActive(item.path) ? 'page' : undefined}
                sx={{
                  mx: 1,
                  mb: 0.5,
                  borderRadius: 2,
                  borderLeft: '4px solid',
                  borderLeftColor: isActive(item.path) ? 'primary.dark' : 'transparent',
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
                    color: isActive(item.path) ? 'rgba(255,255,255,0.7)' : 'text.secondary',
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        {visiblePreview.length > 0 && (
        <>
        <Divider sx={{ my: 1 }} />
        <Typography variant="caption" color="text.secondary" sx={{ px: 2 }}>
          {t('previewGroup')}
        </Typography>
        <List dense>
          {visiblePreview.map((item) => (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                aria-current={isActive(item.path) ? 'page' : undefined}
                sx={{
                  mx: 1,
                  mb: 0.5,
                  borderRadius: 2,
                  borderLeft: '4px solid',
                  borderLeftColor: isActive(item.path) ? 'primary.main' : 'transparent',
                  minHeight: 40,
                }}
              >
                <ListItemIcon sx={{ minWidth: 40, color: 'text.secondary' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={t(item.textKey)}
                  secondary={t(item.descKey)}
                  primaryTypographyProps={{ fontSize: '0.85rem' }}
                  secondaryTypographyProps={{ fontSize: '0.7rem' }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        </>
        )}
      </Box>

      <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
        <Typography variant="subtitle2">{t('appName')}</Typography>
        <Typography variant="caption" color="text.secondary">
          {t('sidebarHint')}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: open ? drawerWidth : 0, // Dynamic width based on open state
        flexShrink: 0,
        transition: 'width 0.3s ease-in-out', // Smooth width transition
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          borderRight: '1px solid',
          borderColor: 'divider',
          transition: 'transform 0.3s ease-in-out', // Smooth transform transition
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;
