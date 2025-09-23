import React, { useState } from 'react';
import {
  Box, Typography, Button, Card, CardContent, Grid,
  TextField, FormControl, InputLabel, Select, MenuItem,
  Divider, Stack, Chip, Alert, Paper
} from '@mui/material';
import {
  CheckCircle, Error, Warning, Info, Person, Inventory,
  Factory, Analytics, Settings, Notifications
} from '@mui/icons-material';
import { useToastNotifications } from '../hooks/useToastNotifications';

const ToastDemo = () => {
  const toast = useToastNotifications();
  const [customMessage, setCustomMessage] = useState('');
  const [customModule, setCustomModule] = useState('general');
  const [customField, setCustomField] = useState('');
  const [customAction, setCustomAction] = useState('');

  // Demo data
  const modules = [
    { value: 'general', label: 'General', icon: Info },
    { value: 'farmer', label: 'Farmer Management', icon: Person },
    { value: 'inventory', label: 'Inventory', icon: Inventory },
    { value: 'production', label: 'Production', icon: Factory },
    { value: 'analytics', label: 'Analytics', icon: Analytics },
    { value: 'settings', label: 'Settings', icon: Settings },
    { value: 'notifications', label: 'Notifications', icon: Notifications }
  ];

  const toastTypes = [
    { type: 'success', label: 'Success', color: '#4caf50', icon: CheckCircle },
    { type: 'error', label: 'Error', color: '#f44336', icon: Error },
    { type: 'warning', label: 'Warning', color: '#ff9800', icon: Warning },
    { type: 'info', label: 'Info', color: '#2196f3', icon: Info }
  ];

  // Demo functions
  const showFarmerDemos = () => {
    toast.farmer.created('John Doe');
    setTimeout(() => toast.farmer.updated('John Doe', 'Phone Number'), 1000);
    setTimeout(() => toast.farmer.editRequestSubmitted('John Doe', { phone: '+91 9876543210', email: 'john@example.com' }), 2000);
    setTimeout(() => toast.farmer.editRequestApproved('John Doe'), 3000);
  };

  const showInventoryDemos = () => {
    toast.inventory.stockAdded('Basmati Rice', 500);
    setTimeout(() => toast.inventory.movementRecorded('Inbound', 'Basmati Rice', 200), 1000);
    setTimeout(() => toast.inventory.lowStockAlert(['Jasmine Rice', 'Brown Rice']), 2000);
  };

  const showProductionDemos = () => {
    toast.production.batchStarted('BATCH001', 'Premium Basmati');
    setTimeout(() => toast.production.qualityCheckPassed('BATCH001', 'Grade A'), 1500);
    setTimeout(() => toast.production.batchCompleted('BATCH001', 450), 2500);
  };

  const showUserDemos = () => {
    toast.user.loginSuccess('Admin User');
    setTimeout(() => toast.user.profileUpdated('Email Address'), 1000);
    setTimeout(() => toast.user.passwordChanged(), 2000);
  };

  const showSystemDemos = () => {
    toast.system.loading('Fetching farmer data...');
    setTimeout(() => toast.system.saveSuccess('Farmer Profile'), 1000);
    setTimeout(() => toast.system.validationError(['Name is required', 'Invalid phone number']), 2000);
    setTimeout(() => toast.system.networkError(), 3000);
  };

  const showFieldValidationDemos = () => {
    toast.farmer.validationError('Phone', 'Please enter a valid 10-digit phone number');
    setTimeout(() => toast.farmer.validationError('Email', 'Email address is already registered'), 1000);
    setTimeout(() => toast.farmer.validationError('Aadhar', 'Aadhar number must be 12 digits'), 2000);
  };

  const showCustomToast = () => {
    if (!customMessage.trim()) {
      toast.showError('Please enter a message for the custom toast');
      return;
    }

    toast.showSuccess(customMessage, {
      module: customModule,
      field: customField || undefined,
      action: customAction || undefined,
      details: `Custom toast with module: ${customModule}`
    });
  };

  const showAdvancedFeatures = () => {
    // Persistent toast
    toast.showError('This is a persistent error that requires user action', {
      persistent: true,
      module: 'system',
      action: 'Critical Error'
    });

    // Toast with action callback
    setTimeout(() => {
      toast.showInfo('Click this toast to view details', {
        module: 'analytics',
        action: 'Report Ready',
        onAction: () => {
          toast.showSuccess('You clicked the toast! This could open a detailed view.');
        }
      });
    }, 1000);

    // Toast with different transition
    setTimeout(() => {
      toast.showWarning('This toast uses a different animation', {
        transition: 'grow',
        module: 'inventory',
        action: 'Stock Alert'
      });
    }, 2000);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        🍞 Toast Notification System Demo
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        This demo showcases the comprehensive toast notification system with field tagging, 
        module categorization, and action feedback across all ERP modules.
      </Alert>

      <Grid container spacing={3}>
        {/* Toast Type Demos */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Basic Toast Types
              </Typography>
              <Stack spacing={2}>
                {toastTypes.map(({ type, label, color, icon: Icon }) => (
                  <Button
                    key={type}
                    variant="outlined"
                    startIcon={<Icon />}
                    onClick={() => toast[`show${label}`](`This is a ${type} message`, {
                      module: 'general',
                      action: 'Demo'
                    })}
                    sx={{ 
                      borderColor: color, 
                      color: color,
                      '&:hover': { borderColor: color, backgroundColor: `${color}10` }
                    }}
                  >
                    Show {label} Toast
                  </Button>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Module-Specific Demos */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Module-Specific Demos
              </Typography>
              <Stack spacing={2}>
                <Button variant="contained" onClick={showFarmerDemos} startIcon={<Person />}>
                  Farmer Management Flow
                </Button>
                <Button variant="contained" onClick={showInventoryDemos} startIcon={<Inventory />}>
                  Inventory Operations
                </Button>
                <Button variant="contained" onClick={showProductionDemos} startIcon={<Factory />}>
                  Production Workflow
                </Button>
                <Button variant="contained" onClick={showUserDemos} startIcon={<Settings />}>
                  User Management
                </Button>
                <Button variant="contained" onClick={showSystemDemos} startIcon={<Info />}>
                  System Messages
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Field Validation Demos */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Field Validation Examples
              </Typography>
              <Button 
                variant="outlined" 
                color="error" 
                fullWidth
                onClick={showFieldValidationDemos}
                startIcon={<Error />}
              >
                Show Field Validation Errors
              </Button>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Demonstrates field-specific error messages with proper tagging
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Advanced Features */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Advanced Features
              </Typography>
              <Button 
                variant="outlined" 
                color="secondary" 
                fullWidth
                onClick={showAdvancedFeatures}
                startIcon={<CheckCircle />}
              >
                Show Advanced Features
              </Button>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Persistent toasts, action callbacks, custom transitions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Custom Toast Builder */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Custom Toast Builder
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Toast Message"
                    value={customMessage}
                    onChange={(e) => setCustomMessage(e.target.value)}
                    placeholder="Enter your custom message..."
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Module</InputLabel>
                    <Select
                      value={customModule}
                      onChange={(e) => setCustomModule(e.target.value)}
                      label="Module"
                    >
                      {modules.map(({ value, label }) => (
                        <MenuItem key={value} value={value}>{label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <TextField
                    fullWidth
                    label="Field (Optional)"
                    value={customField}
                    onChange={(e) => setCustomField(e.target.value)}
                    placeholder="e.g., Phone"
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <TextField
                    fullWidth
                    label="Action (Optional)"
                    value={customAction}
                    onChange={(e) => setCustomAction(e.target.value)}
                    placeholder="e.g., Update"
                  />
                </Grid>
              </Grid>
              <Box sx={{ mt: 2 }}>
                <Button 
                  variant="contained" 
                  onClick={showCustomToast}
                  disabled={!customMessage.trim()}
                >
                  Show Custom Toast
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Toast Features Overview */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              🎯 Toast System Features
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" gutterBottom>Module Categorization</Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {modules.map(({ value, label, icon: Icon }) => (
                    <Chip 
                      key={value}
                      icon={<Icon />}
                      label={label}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Stack>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" gutterBottom>Field Tagging</Typography>
                <Typography variant="body2" color="text.secondary">
                  • Specific field validation errors<br/>
                  • Field-level success messages<br/>
                  • Context-aware feedback
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" gutterBottom>Action Feedback</Typography>
                <Typography variant="body2" color="text.secondary">
                  • Create, Update, Delete operations<br/>
                  • Approval workflow status<br/>
                  • System operation results
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ToastDemo;
