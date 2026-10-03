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
import { useI18n } from '../i18n/I18nContext';

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
  const { t, roleLabel } = useI18n();
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
          <Tab label={t('profile')} icon={<Person />} />
          <Tab label={t('security')} icon={<Security />} />
          <Tab label={t('preferences')} icon={<Settings />} />
          <Tab label={t('activity')} icon={<History />} />
        </Tabs>

        {/* Profile Tab */}
        <TabPanel value={activeTab} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">{t('personalInfo')}</Typography>
            <Button
              startIcon={editMode ? <Cancel /> : <Edit />}
              onClick={() => setEditMode(!editMode)}
              variant={editMode ? "outlined" : "contained"}
            >
              {editMode ? t('cancel') : t('edit')}
            </Button>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={t('firstName')}
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
                label={t('lastName')}
                value={profileData.last_name}
                onChange={(e) => handleProfileChange('last_name', e.target.value)}
                disabled={!editMode}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={t('email')}
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
                label={t('phone')}
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
                label={t('department')}
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
                label={t('role')}
                value={roleLabel(profileData.role)}
                disabled
                InputProps={{
                  startAdornment: <Shield sx={{ mr: 1, color: 'text.secondary' }} />
                }}
                helperText={t('roleReadonly')}
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
                {updateProfileMutation.isLoading ? t('saving') : t('saveChanges')}
              </Button>
            </Box>
          )}
        </TabPanel>

        {/* Security Tab */}
        <TabPanel value={activeTab} index={1}>
          <Typography variant="h6" gutterBottom>{t('changePassword')}</Typography>
          {passwordError && <Alert severity="error" sx={{ mb: 2 }}>{passwordError}</Alert>}
          
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('currentPassword')}
                type={showPassword ? 'text' : 'password'}
                value={passwordData.current_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                InputProps={{
                  startAdornment: <Key sx={{ mr: 1, color: 'text.secondary' }} />,
                  endAdornment: (
                    <IconButton
                      aria-label={showPassword ? t('hidePassword') : t('showPassword')}
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
                label={t('newPassword')}
                type={showPassword ? 'text' : 'password'}
                value={passwordData.new_password}
                onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={t('confirmPassword')}
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
            {changePasswordMutation.isLoading ? t('changing') : t('changePassword')}
          </Button>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>{t('securitySettings')}</Typography>
          <List>
            <ListItem>
              <ListItemIcon><Shield /></ListItemIcon>
              <ListItemText 
                primary={t('twoFactor')} 
                secondary={t('twoFactorHelp')}
              />
              <Switch />
            </ListItem>
            <ListItem>
              <ListItemIcon><AccessTime /></ListItemIcon>
              <ListItemText 
                primary={t('sessionTimeout')} 
                secondary={t('sessionTimeoutDesc')}
              />
              <Switch defaultChecked />
            </ListItem>
          </List>
        </TabPanel>

        {/* Preferences Tab */}
        <TabPanel value={activeTab} index={2}>
          <Typography variant="h6" gutterBottom>{t('appPreferences')}</Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>{t('theme')}</InputLabel>
                <Select
                  value={profileData.preferences?.theme || 'light'}
                  onChange={(e) => handlePreferenceChange('theme', null, e.target.value)}
                  label={t('theme')}
                >
                  <MenuItem value="light">{t('themeLight')}</MenuItem>
                  <MenuItem value="dark">{t('themeDark')}</MenuItem>
                  <MenuItem value="auto">{t('themeAuto')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>{t('language')}</InputLabel>
                <Select
                  value={profileData.preferences?.language || 'en'}
                  onChange={(e) => handlePreferenceChange('language', null, e.target.value)}
                  label={t('language')}
                >
                  <MenuItem value="en">{t('langEnglish')}</MenuItem>
                  <MenuItem value="hi">{t('langHindi')}</MenuItem>
                  <MenuItem value="te">{t('langTelugu')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>{t('timezone')}</InputLabel>
                <Select
                  value={profileData.preferences?.timezone || 'Asia/Kolkata'}
                  onChange={(e) => handlePreferenceChange('timezone', null, e.target.value)}
                  label={t('timezone')}
                >
                  <MenuItem value="Asia/Kolkata">Asia/Kolkata (IST)</MenuItem>
                  <MenuItem value="UTC">UTC</MenuItem>
                  <MenuItem value="America/New_York">America/New_York (EST)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>{t('notifPreferences')}</Typography>
          <List>
            <ListItem>
              <ListItemIcon><Email /></ListItemIcon>
              <ListItemText primary={t('emailNotif')} secondary={t('emailNotifHelp')} />
              <Switch
                checked={Boolean(profileData.preferences?.notifications?.email)}
                onChange={(e) => handlePreferenceChange('notifications', 'email', e.target.checked)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><Notifications /></ListItemIcon>
              <ListItemText primary={t('pushNotif')} secondary={t('pushNotifHelp')} />
              <Switch
                checked={Boolean(profileData.preferences?.notifications?.push)}
                onChange={(e) => handlePreferenceChange('notifications', 'push', e.target.checked)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><Phone /></ListItemIcon>
              <ListItemText primary={t('smsNotif')} secondary={t('smsNotifHelp')} />
              <Switch
                checked={Boolean(profileData.preferences?.notifications?.sms)}
                onChange={(e) => handlePreferenceChange('notifications', 'sms', e.target.checked)}
              />
            </ListItem>
          </List>
        </TabPanel>

        {/* Activity Tab */}
        <TabPanel value={activeTab} index={3}>
          <Typography variant="h6" gutterBottom>{t('recentActivity')}</Typography>
          
          <Card>
            <CardContent>
              <List>
                <ListItem>
                  <ListItemIcon><AccessTime /></ListItemIcon>
                  <ListItemText 
                    primary={t('lastLogin')} 
                    secondary={user?.last_login ? new Date(user.last_login).toLocaleString() : t('never')}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><DeviceHub /></ListItemIcon>
                  <ListItemText 
                    primary={t('activeSessions')} 
                    secondary={t('activeSessionsCount', { count: 2 })}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon><History /></ListItemIcon>
                  <ListItemText 
                    primary={t('toastProfileUpdated')} 
                    secondary={t('profileUpdatedAgo')}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </TabPanel>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>{t('close')}</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ProfilePanel;
