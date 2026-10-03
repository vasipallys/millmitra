import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Tooltip,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  Logout,
  Settings,
  Mic,
  MicOff,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import NotificationsPanel from './NotificationsPanel';
import ProfilePanel from './ProfilePanel';
import notificationService from '../services/notificationService';
import LanguageSwitcher from '../i18n/LanguageSwitcher';
import { useI18n } from '../i18n/I18nContext';
import api from '../services/api';

const accountLabel = (account) => (
  account?.username || account?.email || 'Account'
);

const accountInitial = (account) => (
  (accountLabel(account)[0] || 'A').toUpperCase()
);

const focusFirstIn = (node, selector) => {
  const target = node?.querySelector?.(selector);
  if (target && typeof target.focus === 'function') {
    target.focus();
  }
};

const Navbar = ({ onMenuClick, onLogout, user }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [openProfileAfterMenu, setOpenProfileAfterMenu] = useState(false);
  const [infoOpen, setInfoOpen] = useState(false);
  const [voiceNoteOpen, setVoiceNoteOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [aiFlags, setAiFlags] = useState({ showChip: false, voiceCommands: false });
  const navigate = useNavigate();
  const { t, roleLabel } = useI18n();

  useEffect(() => {
    if (!user) {
      setUnreadCount(0);
      setAiFlags({ showChip: false, voiceCommands: false });
      return undefined;
    }
    let cancelled = false;
    api.get('/user/mill-settings').then((response) => {
      if (cancelled) return;
      const ai = response.data?.settings?.ai || {};
      const notes = response.data?.settings?.notifications || {};
      setAiFlags({
        showChip: Boolean(ai.showAiChip || ai.smartRecommendations || ai.predictiveAnalytics),
        voiceCommands: Boolean(ai.voiceCommands),
      });
      if (notes.inApp !== false) {
        notificationService.start();
      }
    }).catch(() => {
      if (!cancelled) notificationService.start();
    });
    const unsubscribe = notificationService.subscribe(({ unreadCount: nextCount }) => {
      setUnreadCount(nextCount);
    });
    setUnreadCount(notificationService.getUnreadCount());
    return () => {
      cancelled = true;
      unsubscribe();
    };
  }, [user]);

  const handleProfileMenuOpen = (event) => {
    setOpenProfileAfterMenu(false);
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationMenuOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchor(null);
  };

  const handleProfileClick = () => {
    setOpenProfileAfterMenu(true);
    handleProfileMenuClose();
  };

  const handleSettingsClick = () => {
    setOpenProfileAfterMenu(false);
    handleProfileMenuClose();
    navigate('/settings');
  };

  const toggleVoice = () => {
    setVoiceNoteOpen(true);
    setIsVoiceActive(false);
  };



  return (
    <AppBar 
      position="sticky" 
      elevation={1}
      sx={{ 
        bgcolor: 'background.paper', 
        color: 'text.primary',
        borderBottom: '1px solid',
        borderColor: 'divider'
      }}
    >
      <Toolbar>
        {/* Menu Button */}
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        {/* Title */}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {t('appTitle')}
        </Typography>

        <Chip
          label={roleLabel(user?.role)}
          size="small"
          color="primary"
          variant="outlined"
          sx={{ mr: 1 }}
        />
        <LanguageSwitcher />

        {aiFlags.showChip && (
          <Chip
            label={t('aiActive')}
            color="success"
            size="small"
            sx={{ mr: 2, cursor: 'pointer' }}
            onClick={() => setInfoOpen(true)}
          />
        )}

        {aiFlags.voiceCommands && (
          <Tooltip title={isVoiceActive ? 'Disable Voice' : 'Enable Voice'}>
            <IconButton
              color={isVoiceActive ? 'primary' : 'default'}
              onClick={toggleVoice}
              sx={{ mr: 1 }}
              aria-label={isVoiceActive ? 'Disable voice commands' : 'Voice commands (experimental)'}
            >
              {isVoiceActive ? <Mic /> : <MicOff />}
            </IconButton>
          </Tooltip>
        )}

        {/* Notifications */}
        <Tooltip title={t('notifications')}>
          <IconButton
            color="inherit"
            onClick={handleNotificationMenuOpen}
            sx={{ mr: 1 }}
            aria-label={t('notifications')}
          >
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>

        {/* User Profile */}
        <Tooltip title={t('account')}>
          <IconButton
            edge="end"
            color="inherit"
            onClick={handleProfileMenuOpen}
            aria-label="Account menu"
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
              {accountInitial(user)}
            </Avatar>
          </IconButton>
        </Tooltip>

        {/* Profile Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleProfileMenuClose}
          MenuListProps={{ autoFocusItem: true }}
          TransitionProps={{
            onEntering: (node) => focusFirstIn(node, '[role="menuitem"]'),
            onExited: () => {
              if (openProfileAfterMenu) {
                setOpenProfileAfterMenu(false);
                setProfileOpen(true);
              }
            },
          }}
          PaperProps={{
            elevation: 3,
            sx: {
              mt: 1.5,
              minWidth: 200,
            },
          }}
        >
          <Box sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Typography variant="subtitle2">{accountLabel(user)}</Typography>
            <Typography variant="body2" color="text.secondary">
              {roleLabel(user?.role)}
            </Typography>
          </Box>
          <MenuItem autoFocus onClick={handleProfileClick}>
            <AccountCircle sx={{ mr: 1 }} />
            {t('profile')}
          </MenuItem>
          <MenuItem onClick={handleSettingsClick}>
            <Settings sx={{ mr: 1 }} />
            {t('settings')}
          </MenuItem>
          <MenuItem onClick={() => { handleProfileMenuClose(); onLogout(); }}>
            <Logout sx={{ mr: 1 }} />
            {t('logout')}
          </MenuItem>
        </Menu>

        {/* Enhanced Notifications Panel */}
        <NotificationsPanel
          anchorEl={notificationAnchor}
          open={Boolean(notificationAnchor)}
          onClose={handleNotificationMenuClose}
        />

        {/* Enhanced Profile Panel */}
        <ProfilePanel
          open={profileOpen}
          onClose={() => setProfileOpen(false)}
          user={user}
        />

        <Dialog open={infoOpen} onClose={() => setInfoOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Optional AI banners</DialogTitle>
          <DialogContent>
            <Typography variant="body2">
              Insight chips on mill pages are optional. Empty or wrong suggestions do not block saving farmers, stock, batches, orders, or invoices.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setInfoOpen(false)}>{t('close')}</Button>
          </DialogActions>
        </Dialog>

        <Dialog open={voiceNoteOpen} onClose={() => setVoiceNoteOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Voice commands</DialogTitle>
          <DialogContent>
            <Typography variant="body2">
              Voice control is experimental and is not required for mill work. Use the Password login and the sidebar menus.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setVoiceNoteOpen(false)}>{t('close')}</Button>
          </DialogActions>
        </Dialog>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
