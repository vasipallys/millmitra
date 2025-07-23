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

const Navbar = ({ onMenuClick, onLogout, user }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const navigate = useNavigate();

  // Subscribe to notification updates
  useEffect(() => {
    const unsubscribe = notificationService.subscribe(({ unreadCount }) => {
      setUnreadCount(unreadCount);
    });

    // Initial load
    setUnreadCount(notificationService.getUnreadCount());

    return unsubscribe;
  }, []);

  const handleProfileMenuOpen = (event) => {
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
    setProfileOpen(true);
    handleProfileMenuClose();
  };

  const handleSettingsClick = () => {
    navigate('/settings');
    handleProfileMenuClose();
  };

  const toggleVoice = () => {
    setIsVoiceActive(!isVoiceActive);
    // Voice interface logic will be handled by VoiceInterface component
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
          Rice Mill Management System
        </Typography>

        {/* AI Status Indicator */}
        <Chip
          label="AI Active"
          color="success"
          size="small"
          sx={{ mr: 2 }}
        />

        {/* Voice Control Button */}
        <Tooltip title={isVoiceActive ? "Disable Voice" : "Enable Voice"}>
          <IconButton
            color={isVoiceActive ? "primary" : "default"}
            onClick={toggleVoice}
            sx={{ mr: 1 }}
          >
            {isVoiceActive ? <Mic /> : <MicOff />}
          </IconButton>
        </Tooltip>

        {/* Notifications */}
        <Tooltip title="Notifications">
          <IconButton
            color="inherit"
            onClick={handleNotificationMenuOpen}
            sx={{ mr: 1 }}
          >
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>

        {/* User Profile */}
        <Tooltip title="Account">
          <IconButton
            edge="end"
            color="inherit"
            onClick={handleProfileMenuOpen}
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </Avatar>
          </IconButton>
        </Tooltip>

        {/* Profile Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleProfileMenuClose}
          onClick={handleProfileMenuClose}
          PaperProps={{
            elevation: 3,
            sx: {
              mt: 1.5,
              minWidth: 200,
            },
          }}
        >
          <Box sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Typography variant="subtitle2">{user?.username}</Typography>
            <Typography variant="body2" color="text.secondary">
              {user?.role || 'Operator'}
            </Typography>
          </Box>
          <MenuItem onClick={handleProfileClick}>
            <AccountCircle sx={{ mr: 1 }} />
            Profile
          </MenuItem>
          <MenuItem onClick={handleSettingsClick}>
            <Settings sx={{ mr: 1 }} />
            Settings
          </MenuItem>
          <MenuItem onClick={onLogout}>
            <Logout sx={{ mr: 1 }} />
            Logout
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
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
