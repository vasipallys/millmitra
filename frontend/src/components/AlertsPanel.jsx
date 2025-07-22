import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
  Badge,
  Collapse,
  Alert,
  Button,
  Divider
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  ExpandMore,
  ExpandLess,
  Notifications,
  NotificationsActive,
  Clear,
  Refresh
} from '@mui/icons-material';

const AlertsPanel = ({ maxAlerts = 10, autoRefresh = true }) => {
  const [alerts, setAlerts] = useState([]);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);

  // Mock alerts data
  const mockAlerts = [
    {
      id: 1,
      type: 'warning',
      title: 'Low Stock Alert',
      message: 'Broken Rice stock is below reorder level (150 kg remaining)',
      category: 'inventory',
      priority: 'high',
      timestamp: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
      acknowledged: false,
      details: {
        current_stock: 150,
        reorder_level: 200,
        product: 'Broken Rice'
      }
    },
    {
      id: 2,
      type: 'error',
      title: 'Quality Test Failed',
      message: 'Batch #BT2024001 failed moisture content test (15.2% - exceeds limit)',
      category: 'quality',
      priority: 'urgent',
      timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      acknowledged: false,
      details: {
        batch_id: 'BT2024001',
        test_type: 'moisture_content',
        result: 15.2,
        limit: 14.0
      }
    },
    {
      id: 3,
      type: 'info',
      title: 'Production Target Achieved',
      message: 'Daily production target of 2,500 kg achieved at 2:30 PM',
      category: 'production',
      priority: 'low',
      timestamp: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
      acknowledged: true,
      details: {
        target: 2500,
        achieved: 2500,
        time_completed: '14:30'
      }
    },
    {
      id: 4,
      type: 'warning',
      title: 'Equipment Maintenance Due',
      message: 'Milling Machine #2 is due for scheduled maintenance',
      category: 'maintenance',
      priority: 'medium',
      timestamp: new Date(Date.now() - 10800000).toISOString(), // 3 hours ago
      acknowledged: false,
      details: {
        equipment: 'Milling Machine #2',
        last_maintenance: '2024-01-01',
        next_due: '2024-01-22'
      }
    },
    {
      id: 5,
      type: 'success',
      title: 'Payment Received',
      message: 'Payment of ₹1,25,000 received from Customer #C001',
      category: 'finance',
      priority: 'low',
      timestamp: new Date(Date.now() - 14400000).toISOString(), // 4 hours ago
      acknowledged: true,
      details: {
        amount: 125000,
        customer_id: 'C001',
        payment_method: 'bank_transfer'
      }
    }
  ];

  useEffect(() => {
    loadAlerts();
    
    if (autoRefresh) {
      const interval = setInterval(loadAlerts, 60000); // Refresh every minute
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // In real implementation, fetch from API
      // const response = await api.get('/alerts');
      // setAlerts(response.data.alerts);
      
      setAlerts(mockAlerts.slice(0, maxAlerts));
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAlertIcon = (type) => {
    const icons = {
      error: <Error color="error" />,
      warning: <Warning color="warning" />,
      info: <Info color="info" />,
      success: <CheckCircle color="success" />
    };
    return icons[type] || <Info color="info" />;
  };

  const getAlertColor = (type) => {
    const colors = {
      error: 'error',
      warning: 'warning',
      info: 'info',
      success: 'success'
    };
    return colors[type] || 'default';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'error',
      high: 'warning',
      medium: 'info',
      low: 'success'
    };
    return colors[priority] || 'default';
  };

  const acknowledgeAlert = (alertId) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, acknowledged: true }
          : alert
      )
    );
  };

  const dismissAlert = (alertId) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const unacknowledgedCount = alerts.filter(alert => !alert.acknowledged).length;
  const urgentCount = alerts.filter(alert => alert.priority === 'urgent' && !alert.acknowledged).length;

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Badge badgeContent={unacknowledgedCount} color="error">
              {urgentCount > 0 ? (
                <NotificationsActive color="error" />
              ) : (
                <Notifications color="primary" />
              )}
            </Badge>
            <Typography variant="h6">
              System Alerts
            </Typography>
            {unacknowledgedCount > 0 && (
              <Chip 
                label={`${unacknowledgedCount} new`} 
                color="error" 
                size="small" 
              />
            )}
          </Box>
          <Box>
            <IconButton onClick={loadAlerts} size="small" disabled={loading}>
              <Refresh />
            </IconButton>
            <IconButton 
              onClick={() => setExpanded(!expanded)} 
              size="small"
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </Box>

        {alerts.length === 0 ? (
          <Alert severity="success">
            No active alerts. All systems operating normally.
          </Alert>
        ) : (
          <>
            {/* Show first 3 alerts always */}
            <List sx={{ p: 0 }}>
              {alerts.slice(0, 3).map((alert, index) => (
                <React.Fragment key={alert.id}>
                  <ListItem
                    sx={{
                      border: 1,
                      borderColor: alert.acknowledged ? 'grey.300' : `${getAlertColor(alert.type)}.main`,
                      borderRadius: 1,
                      mb: 1,
                      opacity: alert.acknowledged ? 0.7 : 1,
                      bgcolor: alert.acknowledged ? 'grey.50' : 'background.paper'
                    }}
                  >
                    <ListItemIcon>
                      {getAlertIcon(alert.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                          <Typography variant="subtitle2">
                            {alert.title}
                          </Typography>
                          <Chip 
                            label={alert.priority} 
                            size="small" 
                            color={getPriorityColor(alert.priority)}
                          />
                          <Chip 
                            label={alert.category} 
                            size="small" 
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" sx={{ mb: 0.5 }}>
                            {alert.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(alert.timestamp).toLocaleString()}
                          </Typography>
                        </Box>
                      }
                    />
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {!alert.acknowledged && (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => acknowledgeAlert(alert.id)}
                        >
                          Acknowledge
                        </Button>
                      )}
                      <IconButton
                        size="small"
                        onClick={() => dismissAlert(alert.id)}
                      >
                        <Clear fontSize="small" />
                      </IconButton>
                    </Box>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>

            {/* Expandable section for remaining alerts */}
            {alerts.length > 3 && (
              <Collapse in={expanded} timeout="auto" unmountOnExit>
                <Divider sx={{ my: 1 }} />
                <List sx={{ p: 0 }}>
                  {alerts.slice(3).map((alert) => (
                    <ListItem
                      key={alert.id}
                      sx={{
                        border: 1,
                        borderColor: alert.acknowledged ? 'grey.300' : `${getAlertColor(alert.type)}.main`,
                        borderRadius: 1,
                        mb: 1,
                        opacity: alert.acknowledged ? 0.7 : 1,
                        bgcolor: alert.acknowledged ? 'grey.50' : 'background.paper'
                      }}
                    >
                      <ListItemIcon>
                        {getAlertIcon(alert.type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                            <Typography variant="subtitle2">
                              {alert.title}
                            </Typography>
                            <Chip 
                              label={alert.priority} 
                              size="small" 
                              color={getPriorityColor(alert.priority)}
                            />
                            <Chip 
                              label={alert.category} 
                              size="small" 
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" sx={{ mb: 0.5 }}>
                              {alert.message}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {new Date(alert.timestamp).toLocaleString()}
                            </Typography>
                          </Box>
                        }
                      />
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                        {!alert.acknowledged && (
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => acknowledgeAlert(alert.id)}
                          >
                            Acknowledge
                          </Button>
                        )}
                        <IconButton
                          size="small"
                          onClick={() => dismissAlert(alert.id)}
                        >
                          <Clear fontSize="small" />
                        </IconButton>
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </Collapse>
            )}

            {/* Summary */}
            <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Total: {alerts.length} alerts | 
                Unacknowledged: {unacknowledgedCount} | 
                Urgent: {urgentCount}
              </Typography>
            </Box>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default AlertsPanel;
