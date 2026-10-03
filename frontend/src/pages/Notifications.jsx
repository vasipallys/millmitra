/**
 * Enhanced Notifications Page
 * Full-page notification management interface
 */

import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Box, Card, CardContent, Grid, Tabs, Tab,
  List, ListItem, ListItemText, ListItemAvatar, ListItemSecondaryAction,
  Avatar, IconButton, Chip, Button, TextField, FormControl, InputLabel,
  Select, MenuItem, Divider, Badge, Tooltip, Dialog, DialogTitle,
  DialogContent, DialogActions, Checkbox, FormControlLabel
} from '@mui/material';
import {
  Notifications, MarkEmailRead, Delete, Search,
  Settings as SettingsIcon, Info,
  PersonAdd, Payment, Science, Inventory2, Factory, SystemUpdate,
  Refresh
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import notificationService from '../services/notificationService';

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [activeTab, setActiveTab] = useState(0);
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNotifications, setSelectedNotifications] = useState([]);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    notificationService.start();
    const unsubscribe = notificationService.subscribe(({ notifications: next, unreadCount: nextCount }) => {
      setNotifications(next);
      setUnreadCount(nextCount);
    });
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

    // Filter by priority
    if (filterPriority !== 'all') {
      filtered = filtered.filter((n) => (n.severity || n.priority) === filterPriority);
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
    }
  };

  const handleSelectNotification = (notificationId) => {
    setSelectedNotifications(prev => 
      prev.includes(notificationId)
        ? prev.filter(id => id !== notificationId)
        : [...prev, notificationId]
    );
  };

  const handleSelectAll = () => {
    const filteredNotifications = getFilteredNotifications();
    if (selectedNotifications.length === filteredNotifications.length) {
      setSelectedNotifications([]);
    } else {
      setSelectedNotifications(filteredNotifications.map(n => n.id));
    }
  };

  const handleBulkMarkRead = () => {
    selectedNotifications.forEach(id => {
      const notification = notifications.find(n => n.id === id);
      if (notification && !notification.read) {
        notificationService.markAsRead(id);
      }
    });
    setSelectedNotifications([]);
  };

  const handleBulkDelete = () => {
    selectedNotifications.forEach(id => {
      notificationService.deleteNotification(id);
    });
    setSelectedNotifications([]);
  };

  const handleMarkAllRead = () => {
    notificationService.markAllAsRead();
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

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Badge badgeContent={unreadCount} color="error">
            <Notifications sx={{ mr: 2, fontSize: 32 }} />
          </Badge>
          <Typography variant="h4" component="h1">
            Notifications
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton aria-label="Refresh notifications" onClick={() => notificationService.fetchNotifications()}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton aria-label="Notification settings" onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Card>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            variant="fullWidth"
          >
            <Tab label={`All (${notifications.length})`} />
            <Tab label={`Unread (${unreadCount})`} />
            <Tab label="Read" />
          </Tabs>
        </Box>

        {/* Filters and Search */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search notifications..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
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
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl size="small" fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value)}
                  label="Priority"
                >
                  <MenuItem value="all">All Priorities</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={handleMarkAllRead}
                startIcon={<MarkEmailRead />}
                disabled={unreadCount === 0}
              >
                Mark All Read
              </Button>
            </Grid>
          </Grid>
        </Box>

        {/* Bulk Actions */}
        {selectedNotifications.length > 0 && (
          <Box sx={{ p: 2, bgcolor: 'action.selected', borderBottom: 1, borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Typography variant="body2">
                {selectedNotifications.length} notification(s) selected
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  size="small"
                  startIcon={<MarkEmailRead />}
                  onClick={handleBulkMarkRead}
                >
                  Mark Read
                </Button>
                <Button
                  size="small"
                  startIcon={<Delete />}
                  onClick={handleBulkDelete}
                  color="error"
                >
                  Delete
                </Button>
              </Box>
            </Box>
          </Box>
        )}

        {/* Notifications List */}
        <Box sx={{ minHeight: 400 }}>
          {filteredNotifications.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Notifications sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {notifications.length === 0 ? 'No notifications yet' : 'No notifications found'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {notifications.length === 0
                  ? 'Mill events will appear here when farmers, stock, production, sales, or payments are recorded.'
                  : 'Try adjusting your filters'}
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              <ListItem>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={selectedNotifications.length === filteredNotifications.length}
                      indeterminate={selectedNotifications.length > 0 && selectedNotifications.length < filteredNotifications.length}
                      onChange={handleSelectAll}
                    />
                  }
                  label="Select All"
                />
              </ListItem>
              <Divider />
              
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
                    <Checkbox
                      checked={selectedNotifications.includes(notification.id)}
                      onChange={() => handleSelectNotification(notification.id)}
                      onClick={(e) => e.stopPropagation()}
                      sx={{ mr: 1 }}
                    />
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: `${getPriorityColor(notification.priority)}.main` }}>
                        {getCategoryIcon(notification.category)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography 
                            variant="subtitle2" 
                            sx={{ fontWeight: notification.read ? 'normal' : 'bold' }}
                          >
                            {notification.title}
                          </Typography>
                          <Chip
                            label={notification.severity || notification.priority}
                            size="small"
                            color={getPriorityColor(notification.severity || notification.priority)}
                            variant="outlined"
                          />
                          <Chip
                            label={(notification.category || 'system').replace('_', ' ')}
                            size="small"
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
                        onClick={(e) => {
                          e.stopPropagation();
                          notificationService.deleteNotification(notification.id);
                        }}
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
      </Card>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Notification Settings</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Configure your notification preferences
          </Typography>
          {/* Settings content would go here */}
          <Typography variant="body2">
            Advanced notification settings coming soon...
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default NotificationsPage;
