/**
 * Enhanced Profile Panel
 * Comprehensive user profile management and settings
 */

import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography,
  Avatar, Grid, TextField, FormControl, InputLabel, Select, MenuItem,
  Switch, FormControlLabel, Divider, Chip, Card, CardContent, List,
  ListItem, ListItemText, ListItemIcon, IconButton, Tabs, Tab, Alert
} from '@mui/material';
import {
  Person, Email, Phone, Business, Security, Notifications,
  Edit, Save, Cancel, Visibility, VisibilityOff, History,
  Settings, Shield, Key, AccessTime, DeviceHub
} from '@mui/icons-material';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import authService from '../services/authService';

const DEFAULT_PREFERENCES = {
  theme: 'light',
  language: 'en',
  timezone: 'Asia/Kolkata',
  notifications: {
    email: true,
    push: true,
    sms: false,
  },
};

const emptyProfile = () => ({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  department: '',
  role: '',
  username: '',
  preferences: {
    ...DEFAULT_PREFERENCES,
    notifications: { ...DEFAULT_PREFERENCES.notifications },
  },
});

const pickAccount = (source) => {
  if (!source || typeof source !== 'object') return {};
  return source.user && typeof source.user === 'object' ? source.user : source;
};

const mergeProfile = (...sources) => {
  const next = emptyProfile();
  sources.forEach((raw) => {
    const source = pickAccount(raw);
    if (!source || Object.keys(source).length === 0) return;
    ['first_name', 'last_name', 'email', 'phone', 'department', 'role', 'username', 'last_login'].forEach((field) => {
      if (source[field] != null && source[field] !== '') {
        next[field] = source[field];
      }
    });
    const incomingPrefs = source.preferences && typeof source.preferences === 'object'
      ? source.preferences
      : {};
    const incomingNotes = incomingPrefs.notifications && typeof incomingPrefs.notifications === 'object'
      ? incomingPrefs.notifications
      : {};
    next.preferences = {
      ...next.preferences,
      theme: incomingPrefs.theme || next.preferences.theme,
      language: incomingPrefs.language || next.preferences.language,
      timezone: incomingPrefs.timezone || next.preferences.timezone,
      notifications: {
        ...next.preferences.notifications,
        email: incomingNotes.email ?? incomingNotes.emailAlerts ?? next.preferences.notifications.email,
        push: incomingNotes.push ?? incomingNotes.pushNotifications ?? next.preferences.notifications.push,
        sms: incomingNotes.sms ?? incomingNotes.smsAlerts ?? next.preferences.notifications.sms,
      },
    };
  });
  return next;
};

const accountInitials = (account) => {
  const first = (account?.first_name || '').trim();
  const last = (account?.last_name || '').trim();
  if (first && last) return `${first[0]}${last[0]}`.toUpperCase();
  const label = account?.username || account?.email || 'Account';
  return (label[0] || 'A').toUpperCase();
};

const accountDisplayName = (account) => {
  const first = (account?.first_name || '').trim();
  const last = (account?.last_name || '').trim();
  if (first || last) return `${first} ${last}`.trim();
  return account?.username || account?.email || 'Account';
};

const ProfilePanel = ({ open, onClose, user }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [editMode, setEditMode] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [profileData, setProfileData] = useState(emptyProfile);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const queryClient = useQueryClient();

  useEffect(() => {
    setProfileData((prev) => mergeProfile(prev, user));
  }, [user]);

  const { isLoading } = useQuery(
    'user-profile',
    () => authService.getUserProfile(),
    {
      enabled: open,
      retry: false,
      onSuccess: (data) => {
        setProfileData((prev) => mergeProfile(prev, user, data));
      },
    }
  );

  // Update profile mutation
  const updateProfileMutation = useMutation(
    (data) => authService.updateProfile(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('user-profile');
        setEditMode(false);
      }
    }
  );

  // Change password mutation
  const changePasswordMutation = useMutation(
    (data) => authService.changePassword(data),
    {
      onSuccess: () => {
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
      }
    }
  );

  const handleProfileChange = (field, value) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePreferenceChange = (category, field, value) => {
    setProfileData((prev) => {
      const preferences = prev.preferences || { ...DEFAULT_PREFERENCES };
      const current = preferences[category];
      return {
        ...prev,
        preferences: {
          ...DEFAULT_PREFERENCES,
          ...preferences,
          notifications: { ...DEFAULT_PREFERENCES.notifications, ...(preferences.notifications || {}) },
          [category]: current && typeof current === 'object' && field != null
            ? { ...current, [field]: value }
            : value,
        },
      };
    });
  };

  const handleSaveProfile = () => {
    updateProfileMutation.mutate(profileData);
  };

  const handleChangePassword = () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setPasswordError('New passwords do not match');
      return;
    }
    if (!passwordData.current_password || !passwordData.new_password) {
      setPasswordError('Current and new password are required');
      return;
    }
    setPasswordError('');
    changePasswordMutation.mutate(passwordData);
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      TransitionProps={{
        onEntering: (node) => {
          const target = node.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
          if (target && typeof target.focus === 'function') target.focus();
        },
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ width: 56, height: 56, bgcolor: 'primary.main' }}>
            {accountInitials(profileData)}
          </Avatar>
          <Box>
            <Typography variant="h6">
              {isLoading && !profileData.username && !profileData.email ? 'Account' : accountDisplayName(profileData)}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip label={profileData.role || 'Operator'} size="small" color="primary" />
              <Chip label={profileData.department || 'General'} size="small" variant="outlined" />
            </Box>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Profile" icon={<Person />} />
          <Tab label="Security" icon={<Security />} />
          <Tab label="Preferences" icon={<Settings />} />
          <Tab label="Activity" icon={<History />} />
        </Tabs>

        {/* Profile Tab */}
        <TabPanel value={activeTab} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Personal Information</Typography>
            <Button
              startIcon={editMode ? <Cancel /> : <Edit />}
              onClick={() => setEditMode(!editMode)}
              variant={editMode ? "outlined" : "contained"}
            >
              {editMode ? 'Cancel' : 'Edit'}
            </Button>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="First Name"
                value={profileData.first_name}
                onChange={(e) => handleProfileChange('first_name', e.target.value)}
                disabled={!editMode}
                InputProps={{
                  startAdornment: <Person sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Last Name"
                value={profileData.last_name}
                onChange={(e) => handleProfileChange('last_name', e.target.value)}
                disabled={!editMode}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={profileData.email}
                onChange={(e) => handleProfileChange('email', e.target.value)}
                disabled={!editMode}
                InputProps={{
                  startAdornment: <Email sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone"
                value={profileData.phone}
                onChange={(e) => handleProfileChange('phone', e.target.value)}
                disabled={!editMode}
                InputProps={{
                  startAdornment: <Phone sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Department"
                value={profileData.department}
                onChange={(e) => handleProfileChange('department', e.target.value)}
                disabled={!editMode}
                InputProps={{
                  startAdornment: <Business sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Role"
                value={profileData.role}
                disabled
                InputProps={{
                  startAdornment: <Shield sx={{ mr: 1, color: 'text.secondary' }} />
                }}
                helperText="Role can only be changed by administrators"
              />
            </Grid>
          </Grid>

          {editMode && (
            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={handleSaveProfile}
                disabled={updateProfileMutation.isLoading}
              >
                {updateProfileMutation.isLoading ? 'Saving...' : 'Save Changes'}
              </Button>
            </Box>
          )}
        </TabPanel>

        {/* Security Tab */}
        <TabPanel value={activeTab} index={1}>
          <Typography variant="h6" gutterBottom>Change Password</Typography>
          {passwordError && <Alert severity="error" sx={{ mb: 2 }}>{passwordError}</Alert>}
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Current Password"
                type={showPassword ? 'text' : 'password'}
                value={passwordData.current_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                InputProps={{
                  startAdornment: <Key sx={{ mr: 1, color: 'text.secondary' }} />,
                  endAdornment: (
                    <IconButton
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="New Password"
                type={showPassword ? 'text' : 'password'}
                value={passwordData.new_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Confirm New Password"
                type={showPassword ? 'text' : 'password'}
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, confirm_password: e.target.value }))}
              />
            </Grid>
          </Grid>

          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleChangePassword}
            disabled={changePasswordMutation.isLoading}
            sx={{ mt: 2 }}
          >
            {changePasswordMutation.isLoading ? 'Changing...' : 'Change Password'}
          </Button>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>Security Settings</Typography>
          <List>
            <ListItem>
              <ListItemIcon><Shield /></ListItemIcon>
              <ListItemText 
                primary="Two-Factor Authentication" 
                secondary="Add an extra layer of security to your account"
              />
              <Switch />
            </ListItem>
            <ListItem>
              <ListItemIcon><AccessTime /></ListItemIcon>
              <ListItemText 
                primary="Session Timeout" 
                secondary="Automatically log out after 30 minutes of inactivity"
              />
              <Switch defaultChecked />
            </ListItem>
          </List>
        </TabPanel>

        {/* Preferences Tab */}
        <TabPanel value={activeTab} index={2}>
          <Typography variant="h6" gutterBottom>Application Preferences</Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Theme</InputLabel>
                <Select
                  value={profileData.preferences?.theme || 'light'}
                  onChange={(e) => handlePreferenceChange('theme', null, e.target.value)}
                  label="Theme"
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="auto">Auto</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select
                  value={profileData.preferences?.language || 'en'}
                  onChange={(e) => handlePreferenceChange('language', null, e.target.value)}
                  label="Language"
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="hi">Hindi</MenuItem>
                  <MenuItem value="te">Telugu</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Timezone</InputLabel>
                <Select
                  value={profileData.preferences?.timezone || 'Asia/Kolkata'}
                  onChange={(e) => handlePreferenceChange('timezone', null, e.target.value)}
                  label="Timezone"
                >
                  <MenuItem value="Asia/Kolkata">Asia/Kolkata (IST)</MenuItem>
                  <MenuItem value="UTC">UTC</MenuItem>
                  <MenuItem value="America/New_York">America/New_York (EST)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>Notification Preferences</Typography>
          <List>
            <ListItem>
              <ListItemIcon><Email /></ListItemIcon>
              <ListItemText primary="Email Notifications" secondary="Receive notifications via email" />
              <Switch
                checked={Boolean(profileData.preferences?.notifications?.email)}
                onChange={(e) => handlePreferenceChange('notifications', 'email', e.target.checked)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><Notifications /></ListItemIcon>
              <ListItemText primary="Push Notifications" secondary="Receive browser push notifications" />
              <Switch
                checked={Boolean(profileData.preferences?.notifications?.push)}
                onChange={(e) => handlePreferenceChange('notifications', 'push', e.target.checked)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><Phone /></ListItemIcon>
              <ListItemText primary="SMS Notifications" secondary="Receive notifications via SMS" />
              <Switch
                checked={Boolean(profileData.preferences?.notifications?.sms)}
                onChange={(e) => handlePreferenceChange('notifications', 'sms', e.target.checked)}
              />
            </ListItem>
          </List>
        </TabPanel>

        {/* Activity Tab */}
        <TabPanel value={activeTab} index={3}>
          <Typography variant="h6" gutterBottom>Recent Activity</Typography>
          
          <Card>
            <CardContent>
              <List>
                <ListItem>
                  <ListItemIcon><AccessTime /></ListItemIcon>
                  <ListItemText 
                    primary="Last Login" 
                    secondary={user?.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><DeviceHub /></ListItemIcon>
                  <ListItemText 
                    primary="Active Sessions" 
                    secondary="2 active sessions"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><History /></ListItemIcon>
                  <ListItemText 
                    primary="Profile Updated" 
                    secondary="2 days ago"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </TabPanel>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProfilePanel;
