/**
 * Enhanced Notifications Panel
 * Comprehensive notification management with real-time updates
 */

import React, { useState, useEffect } from 'react';
import {
  Menu, MenuItem, Box, Typography, IconButton, Chip, Avatar,
  List, ListItem, ListItemText, ListItemAvatar, ListItemSecondaryAction,
  Divider, Button, Tabs, Tab, Tooltip, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, FormControl, InputLabel, Select
} from '@mui/material';
import {
  MarkEmailRead, Delete,
  Info, Settings as SettingsIcon,
  Search, PersonAdd, Payment, Science,
  Inventory2, Factory, SystemUpdate
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import notificationService from '../services/notificationService';

const focusFirstIn = (node, selector) => {
  const target = node?.querySelector?.(selector);
  if (target && typeof target.focus === 'function') {
    target.focus();
  }
};

const NotificationsPanel = ({ anchorEl, open, onClose }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [activeTab, setActiveTab] = useState(0);
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [openSettingsAfterMenu, setOpenSettingsAfterMenu] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Subscribe to notification updates
    const unsubscribe = notificationService.subscribe(({ notifications, unreadCount }) => {
      setNotifications(notifications);
      setUnreadCount(unreadCount);
    });

    // Initial load
    setNotifications(notificationService.getNotifications());
    setUnreadCount(notificationService.getUnreadCount());

    return unsubscribe;
  }, []);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'farmer_management': return <PersonAdd />;
      case 'production': return <Factory />;
      case 'inventory': return <Inventory2 />;
      case 'quality': return <Science />;
      case 'sales': return <Payment />;
      case 'finance': return <Payment />;
      case 'system': return <SystemUpdate />;
      default: return <Info />;
    }
  };

  const getFilteredNotifications = () => {
    let filtered = notifications;

    // Filter by tab (all, unread, read)
    if (activeTab === 1) {
      filtered = filtered.filter(n => !n.read);
    } else if (activeTab === 2) {
      filtered = filtered.filter(n => n.read);
    }

    // Filter by category
    if (filterCategory !== 'all') {
      filtered = filtered.filter(n => n.category === filterCategory);
    }

    if (searchTerm) {
      const needle = searchTerm.toLowerCase();
      filtered = filtered.filter((n) =>
        (n.title || '').toLowerCase().includes(needle)
        || (n.message || n.body || '').toLowerCase().includes(needle)
      );
    }

    return filtered;
  };

  const handleNotificationClick = (notification) => {
    // Mark as read
    if (!notification.read) {
      notificationService.markAsRead(notification.id);
    }

    // Navigate to relevant page
    const target = notification.link || notification.action_url;
    if (target) {
      navigate(target);
      onClose();
    }
  };

  const handleMarkAllRead = () => {
    notificationService.markAllAsRead();
  };

  const handleDeleteNotification = (notificationId, event) => {
    event.stopPropagation();
    notificationService.deleteNotification(notificationId);
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const filteredNotifications = getFilteredNotifications();

  return (
    <>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={onClose}
        disableAutoFocusItem
        MenuListProps={{ autoFocusItem: false }}
        TransitionProps={{
          onEntering: (node) => focusFirstIn(node, 'input, button, [tabindex]:not([tabindex="-1"])'),
          onExited: () => {
            if (openSettingsAfterMenu) {
              setOpenSettingsAfterMenu(false);
              setSettingsOpen(true);
            }
          },
        }}
        PaperProps={{
          elevation: 3,
          sx: {
            mt: 1.5,
            width: 400,
            maxHeight: 600,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          },
        }}
      >
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="h6">
              Notifications
            </Typography>
            <Box>
              <Tooltip title="Notification Settings">
                <IconButton
                  size="small"
                  aria-label="Notification settings"
                  onClick={() => {
                    setOpenSettingsAfterMenu(true);
                    onClose();
                  }}
                >
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Mark All Read">
                <IconButton size="small" aria-label="Mark all notifications read" onClick={handleMarkAllRead}>
                  <MarkEmailRead />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {/* Search */}
          <TextField
            fullWidth
            size="small"
            placeholder="Search notifications..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
            }}
            sx={{ mb: 1 }}
          />

          {/* Tabs */}
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            variant="fullWidth"
            size="small"
          >
            <Tab label={`All (${notifications.length})`} />
            <Tab label={`Unread (${unreadCount})`} />
            <Tab label="Read" />
          </Tabs>
        </Box>

        {/* Filter */}
        <Box sx={{ px: 2, py: 1, borderBottom: '1px solid', borderColor: 'divider' }}>
          <FormControl size="small" fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              label="Category"
            >
              <MenuItem value="all">All Categories</MenuItem>
              <MenuItem value="farmer_management">Farmer Management</MenuItem>
              <MenuItem value="production">Production</MenuItem>
              <MenuItem value="inventory">Inventory</MenuItem>
              <MenuItem value="quality">Quality Control</MenuItem>
              <MenuItem value="sales">Sales</MenuItem>
              <MenuItem value="finance">Finance</MenuItem>
              <MenuItem value="system">System</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Notifications List */}
        <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
          {filteredNotifications.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                {notifications.length === 0
                  ? 'No notifications yet'
                  : 'No notifications found'}
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {filteredNotifications.map((notification, index) => (
                <React.Fragment key={notification.id}>
                  <ListItem
                    button
                    onClick={() => handleNotificationClick(notification)}
                    sx={{
                      bgcolor: notification.read ? 'transparent' : 'action.hover',
                      '&:hover': { bgcolor: 'action.selected' }
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: `${getPriorityColor(notification.priority)}.main` }}>
                        {getCategoryIcon(notification.category)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: notification.read ? 'normal' : 'bold' }}>
                            {notification.title}
                          </Typography>
                          <Chip
                            label={notification.severity || notification.priority}
                            size="small"
                            color={getPriorityColor(notification.severity || notification.priority)}
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <React.Fragment>
                          <span style={{ display: 'block', marginBottom: '4px', color: 'rgba(0, 0, 0, 0.6)' }}>
                            {notification.message || notification.body}
                          </span>
                          <span style={{ fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                            {formatTimeAgo(notification.timestamp || notification.created_at)}
                          </span>
                        </React.Fragment>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton
                        size="small"
                        onClick={(e) => handleDeleteNotification(notification.id, e)}
                      >
                        <Delete />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < filteredNotifications.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>

        {/* Footer */}
        <Box sx={{ p: 1, borderTop: '1px solid', borderColor: 'divider' }}>
          <Button
            fullWidth
            variant="text"
            onClick={() => {
              navigate('/notifications');
              onClose();
            }}
          >
            View All Notifications
          </Button>
        </Box>
      </Menu>

      {/* Notification Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Notification Settings</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Configure your notification preferences
          </Typography>
          {/* Settings content would go here */}
          <Typography variant="body2">
            Settings panel coming soon...
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default NotificationsPanel;
