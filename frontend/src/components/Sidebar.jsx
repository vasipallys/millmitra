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
} from '@mui/icons-material';

const drawerWidth = 240;

const menuItems = [
  {
    text: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/dashboard',
    description: 'Overview & Analytics'
  },
  {
    text: 'Farmers',
    icon: <FarmersIcon />,
    path: '/farmers',
    description: 'Farmer Management'
  },
  {
    text: 'Inventory',
    icon: <InventoryIcon />,
    path: '/inventory',
    description: 'Stock Management'
  },
  {
    text: 'Production',
    icon: <ProductionIcon />,
    path: '/production',
    description: 'Mill Operations'
  },
  {
    text: 'Sales',
    icon: <SalesIcon />,
    path: '/sales',
    description: 'Sales & Orders'
  },
  {
    text: 'Finance',
    icon: <FinanceIcon />,
    path: '/finance',
    description: 'Financial Management'
  },
  {
    text: 'Customers',
    icon: <CustomersIcon />,
    path: '/customers',
    description: 'Customer Relations'
  },
  {
    text: 'Analytics',
    icon: <AnalyticsIcon />,
    path: '/analytics',
    description: 'Business Intelligence'
  },
  {
    text: 'Quality Control',
    icon: <QualityIcon />,
    path: '/quality-control',
    description: 'AI Quality Assessment'
  },
  {
    text: 'Financial Intelligence',
    icon: <FinancialIntelligenceIcon />,
    path: '/financial-intelligence',
    description: 'Smart Financial Analytics'
  },
  {
    text: 'Compliance & GST',
    icon: <ComplianceIcon />,
    path: '/compliance-gst',
    description: 'Tax & Regulatory Compliance'
  },
  {
    text: 'Settings',
    icon: <SettingsIcon />,
    path: '/settings',
    description: 'System Configuration'
  },
];

const Sidebar = ({ open, onClose, user }) => {
  const navigate = useNavigate();
  const location = useLocation();

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
            Smart Mill
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ opacity: 0.8 }}>
          AI-Powered Rice Mill Management
        </Typography>
      </Box>

      {/* User Info */}
      <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
        <Typography variant="subtitle2" color="text.primary">
          Welcome, {user?.username || 'User'}
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
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                sx={{
                  mx: 1,
                  mb: 0.5,
                  borderRadius: 2,
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
                  primary={item.text}
                  secondary={item.description}
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
      </Box>

      {/* AI Status */}
      <Box sx={{ p: 2, bgcolor: 'success.light', color: 'success.contrastText' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AIIcon sx={{ mr: 1, fontSize: 20 }} />
          <Typography variant="subtitle2">
            AI Assistant Active
          </Typography>
        </Box>
        <Typography variant="caption" sx={{ opacity: 0.8 }}>
          Voice commands enabled • Smart insights ready
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
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          borderRight: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;
