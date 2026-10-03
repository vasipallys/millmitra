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

const normalizeAlert = (item, index) => ({
  id: item.id || index,
  type: item.type || 'info',
  title: item.title || 'Mill alert',
  message: item.message || item.action || '',
  category: item.category || 'mill',
  priority: item.priority,
  timestamp: item.timestamp || item.created_at,
  acknowledged: Boolean(item.acknowledged),
  details: item.details || {},
});

const AlertsPanel = ({ alerts: incoming, maxAlerts = 10, autoRefresh = true }) => {
  const [alerts, setAlerts] = useState([]);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(!incoming);

  useEffect(() => {
    if (Array.isArray(incoming)) {
      setAlerts(incoming.slice(0, maxAlerts).map(normalizeAlert));
      setLoading(false);
      return undefined;
    }
    loadAlerts();
    if (autoRefresh) {
      const interval = setInterval(loadAlerts, 60000);
      return () => clearInterval(interval);
    }
    return undefined;
  }, [incoming, autoRefresh, maxAlerts]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const { dashboardService } = await import('../services/dashboardService');
      const payload = await dashboardService.getAlerts();
      const rows = Array.isArray(payload) ? payload : (payload?.alerts || []);
      setAlerts(rows.slice(0, maxAlerts).map(normalizeAlert));
    } catch (error) {
      setAlerts([]);
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
            <IconButton aria-label="Refresh alerts" onClick={loadAlerts} size="small" disabled={loading}>
              <Refresh />
            </IconButton>
            <IconButton
              aria-label={expanded ? 'Collapse alerts' : 'Expand alerts'}
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
                        aria-label="Dismiss alert"
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
                        aria-label="Dismiss alert"
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
