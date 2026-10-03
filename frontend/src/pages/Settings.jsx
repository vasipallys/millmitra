import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Switch,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
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
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Storage as StorageIcon,
  SmartToy as AIIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';
import api from '../services/api';
import { getApiErrorMessage } from '../utils/apiError';
import { downloadBlob, filenameFromDisposition } from '../utils/downloadFile';
import { PageHeader, PageShell } from '../components/common/PageChrome';

const emptySettings = {
  notifications: {
    emailAlerts: false,
    smsAlerts: false,
    inApp: true,
    pushNotifications: true,
    lowStockAlerts: true,
    qualityAlerts: true,
    productionAlerts: true,
  },
  ai: {
    voiceCommands: false,
    predictiveAnalytics: false,
    autoOptimization: false,
    smartRecommendations: false,
    showAiChip: false,
  },
  business: {
    companyName: '',
    gstNumber: '',
    address: '',
    phone: '',
    email: '',
  },
  security: {
    sessionTimeout: 30,
  },
  backup: {
    autoEnabled: false,
    autoTime: '02:00',
    folder: 'backups',
    retentionDays: 30,
  },
};

const mergeSettings = (incoming) => ({
  ...emptySettings,
  ...(incoming || {}),
  notifications: { ...emptySettings.notifications, ...(incoming?.notifications || {}) },
  ai: { ...emptySettings.ai, ...(incoming?.ai || {}) },
  business: { ...emptySettings.business, ...(incoming?.business || {}) },
  security: { ...emptySettings.security, ...(incoming?.security || {}) },
  backup: { ...emptySettings.backup, ...(incoming?.backup || {}) },
});

const TabPanel = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const Settings = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [saveMessage, setSaveMessage] = useState('');
  const [saveError, setSaveError] = useState('');
  const [settings, setSettings] = useState(emptySettings);
  const [meta, setMeta] = useState({
    mail_configured: false,
    can_edit_business: false,
    can_manage_backup: false,
    notification_scope: 'per_user',
    backup: {},
  });
  const [dialog, setDialog] = useState(null);
  const [draft, setDraft] = useState({});
  const [password, setPassword] = useState({ current: '', next: '', confirm: '' });
  const [busy, setBusy] = useState(false);

  const applyPayload = (data) => {
    if (data?.settings) {
      setSettings(mergeSettings(data.settings));
    }
    setMeta((prev) => ({
      ...prev,
      mail_configured: Boolean(data?.mail_configured),
      can_edit_business: Boolean(data?.can_edit_business),
      can_manage_backup: Boolean(data?.can_manage_backup),
      notification_scope: data?.notification_scope || 'per_user',
      backup: data?.backup || prev.backup || {},
    }));
  };

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get('/user/mill-settings');
        applyPayload(response.data);
      } catch (err) {
        setSaveError(getApiErrorMessage(err, 'Could not load mill settings from the server.'));
      }
    };
    load();
  }, []);

  const handleSettingChange = (category, setting, value) => {
    setSettings((prev) => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value,
      },
    }));
  };

  const tabName = ['business', 'notifications', 'ai', 'security', 'backup'][activeTab];

  const handleSave = async () => {
    setSaveMessage('');
    setSaveError('');
    try {
      const response = await api.put('/user/mill-settings', { tab: tabName, settings });
      applyPayload(response.data);
      setSaveMessage(response.data?.message || 'Settings saved');
    } catch (err) {
      setSaveError(getApiErrorMessage(err, 'Could not save settings.'));
    }
  };

  const saveBackupDraft = async () => {
    setSaveMessage('');
    setSaveError('');
    try {
      const nextBackup = { ...settings.backup, ...draft };
      const response = await api.put('/user/mill-settings', {
        tab: 'backup',
        settings: { backup: nextBackup },
      });
      applyPayload(response.data);
      setSettings((prev) => ({ ...prev, backup: { ...prev.backup, ...nextBackup } }));
      setDialog(null);
      setSaveMessage('Backup settings saved');
    } catch (err) {
      setSaveError(getApiErrorMessage(err, 'Could not save backup settings.'));
    }
  };

  const readBlobError = async (err) => {
    const data = err.response?.data;
    if (data instanceof Blob) {
      try {
        const parsed = JSON.parse(await data.text());
        return parsed.message || parsed.error || 'Backup failed';
      } catch (inner) {
        return 'Backup failed';
      }
    }
    return getApiErrorMessage(err, 'Backup failed');
  };

  const downloadResponse = (response, fallback) => {
    const name = filenameFromDisposition(response.headers['content-disposition'], fallback);
    downloadBlob(name, response.data);
  };

  const handleCreateBackup = async () => {
    setSaveMessage('');
    setSaveError('');
    setBusy(true);
    try {
      if (meta.can_manage_backup) {
        const response = await api.post('/user/backup', {}, { responseType: 'blob' });
        downloadResponse(response, 'rice_mill_erp.db');
        const status = await api.get('/user/backup/status');
        applyPayload(status.data);
        setSaveMessage('Backup saved on the mill server and downloaded to this computer.');
      } else {
        const response = await api.get('/user/backup/download', { responseType: 'blob' });
        downloadResponse(response, 'rice_mill_erp_copy.db');
        setSaveMessage('Downloaded a copy of the mill database. Server archives are admin/manager only.');
      }
    } catch (err) {
      setSaveError(await readBlobError(err));
    } finally {
      setBusy(false);
    }
  };

  const handleCleanup = async () => {
    setSaveMessage('');
    setSaveError('');
    setBusy(true);
    try {
      const response = await api.post('/user/backup/cleanup', {
        retentionDays: settings.backup.retentionDays,
      });
      if (response.data?.backup) {
        setMeta((prev) => ({ ...prev, backup: response.data.backup }));
      }
      setSaveMessage(`Cleanup finished. Removed ${response.data?.removed ?? 0} old backup file(s).`);
    } catch (err) {
      setSaveError(getApiErrorMessage(err, 'Cleanup failed.'));
    } finally {
      setBusy(false);
    }
  };

  const handlePasswordChange = async () => {
    setSaveMessage('');
    setSaveError('');
    if (!password.current || !password.next) {
      setSaveError('Current password and new password are required.');
      return;
    }
    if (password.next !== password.confirm) {
      setSaveError('New password and confirmation do not match.');
      return;
    }
    try {
      const response = await api.post('/user/change-password', {
        current_password: password.current,
        new_password: password.next,
      });
      setPassword({ current: '', next: '', confirm: '' });
      setSaveMessage(response.data?.message || 'Password changed');
    } catch (err) {
      setSaveError(getApiErrorMessage(err, 'Could not change password.'));
    }
  };

  const backup = meta.backup || {};
  const openDialog = (kind) => {
    if (kind === 'auto') {
      setDraft({ autoEnabled: settings.backup.autoEnabled, autoTime: settings.backup.autoTime || '02:00' });
    } else if (kind === 'location') {
      setDraft({ folder: settings.backup.folder || 'backups' });
    } else {
      setDraft({ retentionDays: settings.backup.retentionDays || 30 });
    }
    setDialog(kind);
  };

  return (
    <PageShell>
      <PageHeader
        title="System Settings"
        subtitle="Saved values come from the mill server. Backup numbers are the SQLite file and the backups folder on this computer."
      />
      {saveMessage && <Alert severity="success" sx={{ mb: 2 }} role="status">{saveMessage}</Alert>}
      {saveError && <Alert severity="error" sx={{ mb: 2 }} role="alert">{saveError}</Alert>}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_e, value) => setActiveTab(value)} variant="scrollable" scrollButtons="auto">
          <Tab icon={<BusinessIcon />} label="Business Info" />
          <Tab icon={<NotificationsIcon />} label="Notifications" />
          <Tab icon={<AIIcon />} label="AI Features" />
          <Tab icon={<SecurityIcon />} label="Security" />
          <Tab icon={<StorageIcon />} label="Data & Backup" />
        </Tabs>
      </Paper>

      <TabPanel value={activeTab} index={0}>
        {!meta.can_edit_business && (
          <Alert severity="info" sx={{ mb: 2 }}>Only admin or manager can edit mill business info.</Alert>
        )}
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Company Information</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Mill name"
                      value={settings.business.companyName}
                      onChange={(e) => handleSettingChange('business', 'companyName', e.target.value)}
                      disabled={!meta.can_edit_business}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="GSTIN (optional)"
                      value={settings.business.gstNumber}
                      onChange={(e) => handleSettingChange('business', 'gstNumber', e.target.value)}
                      disabled={!meta.can_edit_business}
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
                      disabled={!meta.can_edit_business}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Phone"
                      value={settings.business.phone}
                      onChange={(e) => handleSettingChange('business', 'phone', e.target.value)}
                      disabled={!meta.can_edit_business}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={settings.business.email}
                      onChange={(e) => handleSettingChange('business', 'email', e.target.value)}
                      disabled={!meta.can_edit_business}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>System Status</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Database"
                      secondary={backup.database_exists ? backup.database_size_label : backup.database_size_label || 'Not found'}
                    />
                    <Chip label={backup.database_exists ? 'Found' : 'Missing'} color={backup.database_exists ? 'success' : 'warning'} size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="AI flags" secondary="Saved preferences only — no models are running" />
                    <Chip label="Flags" size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Last backup" secondary={backup.last_backup_at || 'Never'} />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Alert severity="info" sx={{ mb: 2 }}>
          These preferences are stored for your account. In-app is the live channel.
          {meta.can_edit_business
            ? ' Saving as admin/manager also updates mill-wide low-stock and batch-complete writers.'
            : ' Low-stock and batch-complete writes follow mill-wide flags set by admin or manager.'}
        </Alert>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Channels</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Email"
                      secondary={meta.mail_configured ? 'Saved preference (mail server is configured)' : 'Saved preference, not sent — no mail server is configured'}
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={Boolean(settings.notifications.emailAlerts)}
                        onChange={(e) => handleSettingChange('notifications', 'emailAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="In-app" secondary="Bell panel and Notifications page" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={Boolean(settings.notifications.inApp)}
                        onChange={(e) => handleSettingChange('notifications', 'inApp', e.target.checked)}
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
                <Typography variant="h6" gutterBottom>Event types</Typography>
                <List>
                  <ListItem>
                    <ListItemText primary="Low stock" secondary="Skip writing a low-stock row when this mill flag is off" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={Boolean(settings.notifications.lowStockAlerts)}
                        onChange={(e) => handleSettingChange('notifications', 'lowStockAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary="Batch complete" secondary="Skip production-complete rows when off" />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={Boolean(settings.notifications.productionAlerts)}
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

      <TabPanel value={activeTab} index={2}>
        <Alert severity="info" sx={{ mb: 3 }}>
          These flags are saved. They do not start machine-learning models. The navbar chip appears only when you turn on a banner flag below.
        </Alert>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Optional UI flags</Typography>
            <List>
              <ListItem>
                <ListItemText primary="Voice commands banner" secondary="Shows the experimental mic control. Voice login is not a real sign-in method." />
                <ListItemSecondaryAction>
                  <Switch
                    checked={Boolean(settings.ai.voiceCommands)}
                    onChange={(e) => handleSettingChange('ai', 'voiceCommands', e.target.checked)}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText primary="Predictive analytics banner" secondary="UI only. No forecast model is running." />
                <ListItemSecondaryAction>
                  <Switch
                    checked={Boolean(settings.ai.predictiveAnalytics)}
                    onChange={(e) => handleSettingChange('ai', 'predictiveAnalytics', e.target.checked)}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText primary="Auto optimization" secondary="UI only. Processes are not changed automatically." />
                <ListItemSecondaryAction>
                  <Switch
                    checked={Boolean(settings.ai.autoOptimization)}
                    onChange={(e) => handleSettingChange('ai', 'autoOptimization', e.target.checked)}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText primary="Smart recommendations / AI Active chip" secondary="Shows the navbar chip. Insight cards stay optional." />
                <ListItemSecondaryAction>
                  <Switch
                    checked={Boolean(settings.ai.smartRecommendations)}
                    onChange={(e) => handleSettingChange('ai', 'smartRecommendations', e.target.checked)}
                  />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Change password</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      type="password"
                      label="Current password"
                      value={password.current}
                      onChange={(e) => setPassword((prev) => ({ ...prev, current: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      type="password"
                      label="New password"
                      value={password.next}
                      onChange={(e) => setPassword((prev) => ({ ...prev, next: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      type="password"
                      label="Confirm new password"
                      value={password.confirm}
                      onChange={(e) => setPassword((prev) => ({ ...prev, confirm: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" onClick={handlePasswordChange}>Change password</Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Session</Typography>
                <TextField
                  fullWidth
                  type="number"
                  label="Session timeout (minutes)"
                  helperText="Stored preference. Sign-in tokens still last up to 24 hours unless you sign out."
                  value={settings.security.sessionTimeout}
                  onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value, 10) || 0)}
                  sx={{ mb: 2 }}
                />
                <Alert severity="info">
                  Two-factor enrollment is not available in this deployment. The 2FA API returns 501.
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={4}>
        {!meta.can_manage_backup && (
          <Alert severity="info" sx={{ mb: 2 }}>
            You can download a copy of the database. Saving the archive folder, schedule, and cleanup is admin/manager only.
          </Alert>
        )}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Backup Settings</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Auto backup"
                      secondary={settings.backup.autoEnabled
                        ? `Enabled daily at ${settings.backup.autoTime} while Flask is running`
                        : 'Off — no backup is pretended when the server is stopped'}
                    />
                    <Button variant="outlined" size="small" disabled={!meta.can_manage_backup} onClick={() => openDialog('auto')}>
                      Configure
                    </Button>
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Backup location"
                      secondary={`This computer → instance/${settings.backup.folder || 'backups'}`}
                    />
                    <Button variant="outlined" size="small" disabled={!meta.can_manage_backup} onClick={() => openDialog('location')}>
                      Change
                    </Button>
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Retention"
                      secondary={`Keep files ${settings.backup.retentionDays || 30} days, then delete on Run Now or the daily job`}
                    />
                    <Button variant="outlined" size="small" disabled={!meta.can_manage_backup} onClick={() => openDialog('retention')}>
                      Modify
                    </Button>
                  </ListItem>
                </List>
                <Box sx={{ mt: 2 }}>
                  <Button variant="contained" fullWidth disabled={busy} onClick={handleCreateBackup}>
                    Create Backup Now
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Data Management</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Database size"
                      secondary={backup.database_exists
                        ? `${backup.database_size_label} (${backup.database_path})`
                        : `Not found${backup.database_path ? ` at ${backup.database_path}` : ''}`}
                    />
                    <Chip label={backup.database_exists ? 'SQLite' : 'Missing'} size="small" color={backup.database_exists ? 'success' : 'warning'} />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Backups folder"
                      secondary={`${backup.backups_size_label || '0 bytes'} in ${backup.backups_folder || 'instance/backups'}`}
                    />
                  </ListItem>
                  {backup.disk_free_label && (
                    <ListItem>
                      <ListItemText
                        primary="This computer's free space"
                        secondary={backup.disk_free_label}
                      />
                    </ListItem>
                  )}
                  <ListItem>
                    <ListItemText primary="Last cleanup" secondary={backup.last_cleanup_label || 'Never'} />
                    <Button variant="outlined" size="small" disabled={!meta.can_manage_backup || busy} onClick={handleCleanup}>
                      Run Now
                    </Button>
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button variant="contained" size="large" onClick={handleSave}>
          Save Settings
        </Button>
      </Box>

      <Dialog open={Boolean(dialog)} onClose={() => setDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog === 'auto' && 'Auto backup'}
          {dialog === 'location' && 'Backup location'}
          {dialog === 'retention' && 'Retention'}
        </DialogTitle>
        <DialogContent>
          {dialog === 'auto' && (
            <Box sx={{ pt: 1 }}>
              <Switch
                checked={Boolean(draft.autoEnabled)}
                onChange={(e) => setDraft((prev) => ({ ...prev, autoEnabled: e.target.checked }))}
              />
              {' '}Enabled
              <TextField
                fullWidth
                type="time"
                label="Local time"
                value={draft.autoTime || '02:00'}
                onChange={(e) => setDraft((prev) => ({ ...prev, autoTime: e.target.value }))}
                sx={{ mt: 2 }}
                helperText="Runs once a day at this time only while Flask is running."
              />
            </Box>
          )}
          {dialog === 'location' && (
            <TextField
              fullWidth
              sx={{ mt: 1 }}
              label="Folder under instance/"
              value={draft.folder || 'backups'}
              onChange={(e) => setDraft((prev) => ({ ...prev, folder: e.target.value }))}
              helperText="Relative folder only, for example backups. System paths are rejected."
            />
          )}
          {dialog === 'retention' && (
            <TextField
              fullWidth
              sx={{ mt: 1 }}
              type="number"
              label="Keep backups (days)"
              value={draft.retentionDays || 30}
              onChange={(e) => setDraft((prev) => ({ ...prev, retentionDays: parseInt(e.target.value, 10) || 1 }))}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog(null)}>Cancel</Button>
          <Button variant="contained" onClick={saveBackupDraft}>Save</Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
};

export default Settings;
