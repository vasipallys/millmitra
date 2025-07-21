import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Alert,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Storage as StorageIcon,
  SmartToy as AIIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';

const Settings = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [settings, setSettings] = useState({
    notifications: {
      emailAlerts: true,
      smsAlerts: false,
      pushNotifications: true,
      lowStockAlerts: true,
      qualityAlerts: true,
      productionAlerts: true,
    },
    ai: {
      voiceCommands: true,
      predictiveAnalytics: true,
      autoOptimization: false,
      smartRecommendations: true,
    },
    business: {
      companyName: 'ABC Rice Mills',
      gstNumber: '27AABCU9603R1ZX',
      address: '123 Mill Street, Rice City',
      phone: '+91 9876543210',
      email: 'info@abcricemills.com',
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 30,
      passwordExpiry: 90,
      loginAttempts: 3,
    },
  });

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleSettingChange = (category, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value,
      },
    }));
  };

  const handleSave = () => {
    // Save settings logic
    console.log('Saving settings:', settings);
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          System Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure your rice mill management system
        </Typography>
      </Box>

      {/* Settings Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<BusinessIcon />} label="Business Info" />
          <Tab icon={<NotificationsIcon />} label="Notifications" />
          <Tab icon={<AIIcon />} label="AI Features" />
          <Tab icon={<SecurityIcon />} label="Security" />
          <Tab icon={<StorageIcon />} label="Data & Backup" />
        </Tabs>
      </Paper>

      {/* Business Information Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Company Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Company Name"
                      value={settings.business.companyName}
                      onChange={(e) => handleSettingChange('business', 'companyName', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="GST Number"
                      value={settings.business.gstNumber}
                      onChange={(e) => handleSettingChange('business', 'gstNumber', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address"
                      multiline
                      rows={3}
                      value={settings.business.address}
                      onChange={(e) => handleSettingChange('business', 'address', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Phone"
                      value={settings.business.phone}
                      onChange={(e) => handleSettingChange('business', 'phone', e.target.value)}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={settings.business.email}
                      onChange={(e) => handleSettingChange('business', 'email', e.target.value)}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Status
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Database" secondary="Connected" />
                    <Chip label="Online" color="success" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="AI Services" secondary="Active" />
                    <Chip label="Running" color="success" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Backup" secondary="Last: 2 hours ago" />
                    <Chip label="OK" color="success" size="small" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Notifications Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Alert Preferences
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Email Alerts" secondary="Receive alerts via email" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.notifications.emailAlerts}
                        onChange={(e) => handleSettingChange('notifications', 'emailAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="SMS Alerts" secondary="Receive alerts via SMS" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.notifications.smsAlerts}
                        onChange={(e) => handleSettingChange('notifications', 'smsAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Push Notifications" secondary="Browser notifications" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.notifications.pushNotifications}
                        onChange={(e) => handleSettingChange('notifications', 'pushNotifications', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Alert Types
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Low Stock Alerts" secondary="When inventory is low" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.notifications.lowStockAlerts}
                        onChange={(e) => handleSettingChange('notifications', 'lowStockAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Quality Alerts" secondary="Quality issues detected" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.notifications.qualityAlerts}
                        onChange={(e) => handleSettingChange('notifications', 'qualityAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Production Alerts" secondary="Production milestones" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.notifications.productionAlerts}
                        onChange={(e) => handleSettingChange('notifications', 'productionAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* AI Features Tab */}
      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info" sx={{ mb: 3 }}>
              AI features help optimize your rice mill operations through machine learning and automation.
            </Alert>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  AI Capabilities
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText 
                      primary="Voice Commands" 
                      secondary="Control system with voice" 
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.ai.voiceCommands}
                        onChange={(e) => handleSettingChange('ai', 'voiceCommands', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Predictive Analytics" 
                      secondary="Forecast demand and production" 
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.ai.predictiveAnalytics}
                        onChange={(e) => handleSettingChange('ai', 'predictiveAnalytics', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Auto Optimization" 
                      secondary="Automatically optimize processes" 
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.ai.autoOptimization}
                        onChange={(e) => handleSettingChange('ai', 'autoOptimization', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Smart Recommendations" 
                      secondary="AI-powered suggestions" 
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.ai.smartRecommendations}
                        onChange={(e) => handleSettingChange('ai', 'smartRecommendations', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  AI Performance
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Model Accuracy" secondary="Production forecasting" />
                    <Chip label="94.2%" color="success" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Quality Detection" secondary="Defect identification" />
                    <Chip label="97.8%" color="success" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Demand Prediction" secondary="Sales forecasting" />
                    <Chip label="89.5%" color="warning" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Cost Optimization" secondary="Efficiency improvements" />
                    <Chip label="92.1%" color="success" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Security Tab */}
      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Authentication
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText 
                      primary="Two-Factor Authentication" 
                      secondary="Extra security layer" 
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={settings.security.twoFactorAuth}
                        onChange={(e) => handleSettingChange('security', 'twoFactorAuth', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                </List>
                <Divider sx={{ my: 2 }} />
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Session Timeout (minutes)"
                      type="number"
                      value={settings.security.sessionTimeout}
                      onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Password Expiry (days)"
                      type="number"
                      value={settings.security.passwordExpiry}
                      onChange={(e) => handleSettingChange('security', 'passwordExpiry', parseInt(e.target.value))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Max Login Attempts"
                      type="number"
                      value={settings.security.loginAttempts}
                      onChange={(e) => handleSettingChange('security', 'loginAttempts', parseInt(e.target.value))}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security Status
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="SSL Certificate" secondary="Valid until Dec 2024" />
                    <Chip label="Active" color="success" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Firewall" secondary="All ports secured" />
                    <Chip label="Protected" color="success" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Data Encryption" secondary="AES-256 encryption" />
                    <Chip label="Enabled" color="success" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Audit Logs" secondary="All activities logged" />
                    <Chip label="Active" color="success" size="small" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Data & Backup Tab */}
      <TabPanel value={activeTab} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Backup Settings
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Auto Backup" secondary="Daily at 2:00 AM" />
                    <Button variant="outlined" size="small">Configure</Button>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Backup Location" secondary="Cloud Storage" />
                    <Button variant="outlined" size="small">Change</Button>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Retention Period" secondary="30 days" />
                    <Button variant="outlined" size="small">Modify</Button>
                  </ListItem>
                </List>
                <Box sx={{ mt: 2 }}>
                  <Button variant="contained" fullWidth>
                    Create Backup Now
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Data Management
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Database Size" secondary="2.4 GB" />
                    <Chip label="Normal" color="success" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Storage Used" secondary="45% of 10 GB" />
                    <Chip label="OK" color="success" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Last Cleanup" secondary="3 days ago" />
                    <Button variant="outlined" size="small">Run Now</Button>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Save Button */}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button variant="contained" size="large" onClick={handleSave}>
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default Settings;
