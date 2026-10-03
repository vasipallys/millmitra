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
import { useI18n } from '../i18n/I18nContext';

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
  const { t } = useI18n();
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
        setSaveError(getApiErrorMessage(err, t('couldNotLoadSettings')));
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
      setSaveMessage(response.data?.message || t('settingsSaved'));
    } catch (err) {
      setSaveError(getApiErrorMessage(err, t('couldNotSaveSettings')));
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
      setSaveMessage(t('backupSettingsSaved'));
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
      setSaveError(t('passwordRequiredBoth'));
      return;
    }
    if (password.next !== password.confirm) {
      setSaveError(t('passwordMismatch'));
      return;
    }
    try {
      const response = await api.post('/user/change-password', {
        current_password: password.current,
        new_password: password.next,
      });
      setPassword({ current: '', next: '', confirm: '' });
      setSaveMessage(response.data?.message || t('passwordChanged'));
    } catch (err) {
      setSaveError(getApiErrorMessage(err, t('couldNotChangePassword')));
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
        title={t('settingsTitle')}
        subtitle={t('settingsSubtitle')}
      />
      {saveMessage && <Alert severity="success" sx={{ mb: 2 }} role="status">{saveMessage}</Alert>}
      {saveError && <Alert severity="error" sx={{ mb: 2 }} role="alert">{saveError}</Alert>}

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_e, value) => setActiveTab(value)} variant="scrollable" scrollButtons="auto">
          <Tab icon={<BusinessIcon />} label={t('tabBusiness')} />
          <Tab icon={<NotificationsIcon />} label={t('tabNotifications')} />
          <Tab icon={<AIIcon />} label={t('tabAi')} />
          <Tab icon={<SecurityIcon />} label={t('tabSecurity')} />
          <Tab icon={<StorageIcon />} label={t('tabBackup')} />
        </Tabs>
      </Paper>

      <TabPanel value={activeTab} index={0}>
        {!meta.can_edit_business && (
          <Alert severity="info" sx={{ mb: 2 }}>{t('onlyAdminBusiness')}</Alert>
        )}
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>{t('companyInfo')}</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label={t('millName')}
                      value={settings.business.companyName}
                      onChange={(e) => handleSettingChange('business', 'companyName', e.target.value)}
                      disabled={!meta.can_edit_business}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label={t('gstin')}
                      value={settings.business.gstNumber}
                      onChange={(e) => handleSettingChange('business', 'gstNumber', e.target.value)}
                      disabled={!meta.can_edit_business}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label={t('address')}
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
                      label={t('phone')}
                      value={settings.business.phone}
                      onChange={(e) => handleSettingChange('business', 'phone', e.target.value)}
                      disabled={!meta.can_edit_business}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label={t('email')}
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
                <Typography variant="h6" gutterBottom>{t('systemStatus')}</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary={t('database')}
                      secondary={backup.database_exists ? backup.database_size_label : backup.database_size_label || t('notFound')}
                    />
                    <Chip label={backup.database_exists ? t('found') : t('missing')} color={backup.database_exists ? 'success' : 'warning'} size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary={t('aiFlags')} secondary={t('aiFlagsHelp')} />
                    <Chip label={t('aiFlags')} size="small" />
                  </ListItem>
                  <ListItem>
                    <ListItemText primary={t('lastBackup')} secondary={backup.last_backup_at || t('never')} />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Alert severity="info" sx={{ mb: 2 }}>
          {t('notifPrefHelp')}{' '}
          {meta.can_edit_business ? t('notifPrefHelpAdmin') : t('notifPrefHelpOp')}
        </Alert>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>{t('channels')}</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary={t('email')}
                      secondary={meta.mail_configured ? t('mailConfigured') : t('mailNotConfigured')}
                    />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={Boolean(settings.notifications.emailAlerts)}
                        onChange={(e) => handleSettingChange('notifications', 'emailAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary={t('inApp')} secondary={t('inAppHelp')} />
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
                <Typography variant="h6" gutterBottom>{t('eventTypes')}</Typography>
                <List>
                  <ListItem>
                    <ListItemText primary={t('lowStockPref')} secondary={t('lowStockHelp')} />
                    <ListItemSecondaryAction>
                      <Switch
                        checked={Boolean(settings.notifications.lowStockAlerts)}
                        onChange={(e) => handleSettingChange('notifications', 'lowStockAlerts', e.target.checked)}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <ListItem>
                    <ListItemText primary={t('batchCompletePref')} secondary={t('batchCompleteHelp')} />
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
          {t('aiFlagsAlert')}
        </Alert>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>{t('optionalUiFlags')}</Typography>
            <List>
              <ListItem>
                <ListItemText primary={t('voiceBanner')} secondary={t('voiceBannerHelp')} />
                <ListItemSecondaryAction>
                  <Switch
                    checked={Boolean(settings.ai.voiceCommands)}
                    onChange={(e) => handleSettingChange('ai', 'voiceCommands', e.target.checked)}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText primary={t('predictiveBanner')} secondary={t('predictiveBannerHelp')} />
                <ListItemSecondaryAction>
                  <Switch
                    checked={Boolean(settings.ai.predictiveAnalytics)}
                    onChange={(e) => handleSettingChange('ai', 'predictiveAnalytics', e.target.checked)}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText primary={t('autoOpt')} secondary={t('autoOptHelp')} />
                <ListItemSecondaryAction>
                  <Switch
                    checked={Boolean(settings.ai.autoOptimization)}
                    onChange={(e) => handleSettingChange('ai', 'autoOptimization', e.target.checked)}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <ListItem>
                <ListItemText primary={t('aiChipPref')} secondary={t('aiChipHelp')} />
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
                <Typography variant="h6" gutterBottom>{t('changePassword')}</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      type="password"
                      label={t('currentPassword')}
                      value={password.current}
                      onChange={(e) => setPassword((prev) => ({ ...prev, current: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      type="password"
                      label={t('newPassword')}
                      value={password.next}
                      onChange={(e) => setPassword((prev) => ({ ...prev, next: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      type="password"
                      label={t('confirmPassword')}
                      value={password.confirm}
                      onChange={(e) => setPassword((prev) => ({ ...prev, confirm: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Button variant="contained" onClick={handlePasswordChange}>{t('changePassword')}</Button>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>{t('session')}</Typography>
                <TextField
                  fullWidth
                  type="number"
                  label={t('sessionTimeout')}
                  helperText={t('sessionTimeoutHelp')}
                  value={settings.security.sessionTimeout}
                  onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value, 10) || 0)}
                  sx={{ mb: 2 }}
                />
                <Alert severity="info">
                  {t('twoFaUnavailable')}
                </Alert>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={4}>
        {!meta.can_manage_backup && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {t('backupOperatorHelp')}
          </Alert>
        )}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>{t('backupSettings')}</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary={t('autoBackup')}
                      secondary={settings.backup.autoEnabled
                        ? t('autoBackupOn', { time: settings.backup.autoTime })
                        : t('autoBackupOff')}
                    />
                    <Button variant="outlined" size="small" disabled={!meta.can_manage_backup} onClick={() => openDialog('auto')}>
                      {t('configure')}
                    </Button>
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary={t('backupLocation')}
                      secondary={t('backupLocationPath', { folder: settings.backup.folder || 'backups' })}
                    />
                    <Button variant="outlined" size="small" disabled={!meta.can_manage_backup} onClick={() => openDialog('location')}>
                      {t('change')}
                    </Button>
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary={t('retention')}
                      secondary={t('retentionHelp', { days: settings.backup.retentionDays || 30 })}
                    />
                    <Button variant="outlined" size="small" disabled={!meta.can_manage_backup} onClick={() => openDialog('retention')}>
                      {t('modify')}
                    </Button>
                  </ListItem>
                </List>
                <Box sx={{ mt: 2 }}>
                  <Button variant="contained" fullWidth disabled={busy} onClick={handleCreateBackup}>
                    {t('createBackupNow')}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>{t('dataManagement')}</Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary={t('databaseSize')}
                      secondary={backup.database_exists
                        ? `${backup.database_size_label} (${backup.database_path})`
                        : (backup.database_path ? `${t('notFound')} ${backup.database_path}` : t('notFound'))}
                    />
                    <Chip label={backup.database_exists ? t('sqlite') : t('missing')} size="small" color={backup.database_exists ? 'success' : 'warning'} />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary={t('backupsFolder')}
                      secondary={t('backupsIn', { size: backup.backups_size_label || '0 bytes', folder: backup.backups_folder || 'instance/backups' })}
                    />
                  </ListItem>
                  {backup.disk_free_label && (
                    <ListItem>
                      <ListItemText
                        primary={t('freeSpace')}
                        secondary={backup.disk_free_label}
                      />
                    </ListItem>
                  )}
                  <ListItem>
                    <ListItemText primary={t('lastCleanup')} secondary={backup.last_cleanup_label || t('never')} />
                    <Button variant="outlined" size="small" disabled={!meta.can_manage_backup || busy} onClick={handleCleanup}>
                      {t('runNow')}
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
          {t('saveSettings')}
        </Button>
      </Box>

      <Dialog open={Boolean(dialog)} onClose={() => setDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog === 'auto' && t('autoBackup')}
          {dialog === 'location' && t('backupLocation')}
          {dialog === 'retention' && t('retention')}
        </DialogTitle>
        <DialogContent>
          {dialog === 'auto' && (
            <Box sx={{ pt: 1 }}>
              <Switch
                checked={Boolean(draft.autoEnabled)}
                onChange={(e) => setDraft((prev) => ({ ...prev, autoEnabled: e.target.checked }))}
              />
              {' '}{t('enabled')}
              <TextField
                fullWidth
                type="time"
                label={t('localTime')}
                value={draft.autoTime || '02:00'}
                onChange={(e) => setDraft((prev) => ({ ...prev, autoTime: e.target.value }))}
                sx={{ mt: 2 }}
                helperText={t('autoBackupHelp')}
              />
            </Box>
          )}
          {dialog === 'location' && (
            <TextField
              fullWidth
              sx={{ mt: 1 }}
              label={t('backupFolder')}
              value={draft.folder || 'backups'}
              onChange={(e) => setDraft((prev) => ({ ...prev, folder: e.target.value }))}
              helperText={t('backupFolderHelp')}
            />
          )}
          {dialog === 'retention' && (
            <TextField
              fullWidth
              sx={{ mt: 1 }}
              type="number"
              label={t('keepBackups')}
              value={draft.retentionDays || 30}
              onChange={(e) => setDraft((prev) => ({ ...prev, retentionDays: parseInt(e.target.value, 10) || 1 }))}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog(null)}>{t('cancel')}</Button>
          <Button variant="contained" onClick={saveBackupDraft}>{t('save')}</Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
};

export default Settings;
