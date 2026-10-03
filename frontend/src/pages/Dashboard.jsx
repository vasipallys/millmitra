import { useState } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Alert,
  IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  FormGroup, FormControlLabel, Checkbox
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Warning,
  Settings, Refresh, Insights
} from '@mui/icons-material';
import { dashboardService } from '../services/dashboardService';
import { useQuery, useQueryClient } from 'react-query';
import SmartWidget from '../components/SmartWidget';
import AIInsights from '../components/AIInsights';
import AlertsPanel from '../components/AlertsPanel';
import { PageHeader, PageLoading, PageShell, QueryErrorAlert } from '../components/common/PageChrome';
import { getApiErrorMessage } from '../utils/apiError';

const DEFAULT_WIDGETS = [
  { id: 'production', label: 'Production snapshot' },
  { id: 'inventory', label: 'Inventory value' },
  { id: 'sales', label: 'Pending orders' },
  { id: 'farmers', label: 'Active farmers' },
  { id: 'quality', label: 'Quality score' },
];

const Dashboard = () => {
  const [timeRange, setTimeRange] = useState(7);
  const [customizeOpen, setCustomizeOpen] = useState(false);
  const [selectedWidgets, setSelectedWidgets] = useState([]);
  const [availableWidgets, setAvailableWidgets] = useState(DEFAULT_WIDGETS);
  const [customizeError, setCustomizeError] = useState('');
  const [customizeSaving, setCustomizeSaving] = useState(false);
  const queryClient = useQueryClient();

  // Fetch dashboard data
  const { data: overview, isLoading: overviewLoading, isError: overviewError, error: overviewErr, refetch: refetchOverview } = useQuery(
    ['dashboard-overview', timeRange],
    () => dashboardService.getOverview(timeRange),
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  const { data: widgets, isLoading: widgetsLoading, isError: widgetsError, error: widgetsErr, refetch: refetchWidgets } = useQuery(
    'dashboard-widgets',
    () => dashboardService.getWidgets(),
    { refetchInterval: 60000 }
  );

  const { data: insights } = useQuery(
    'dashboard-insights',
    () => dashboardService.getInsights(),
    { refetchInterval: 120000 } // Refresh every 2 minutes
  );

  const { data: alerts } = useQuery(
    'dashboard-alerts',
    () => dashboardService.getAlerts(),
    { refetchInterval: 30000 }
  );

  const handleRefresh = () => {
    queryClient.invalidateQueries('dashboard-overview');
    queryClient.invalidateQueries('dashboard-widgets');
    queryClient.invalidateQueries('dashboard-insights');
    queryClient.invalidateQueries('dashboard-alerts');
  };

  const handleCustomize = () => {
    const fromApi = (widgets?.widgets || []).map((widget) => ({
      id: widget.id,
      label: widget.title || widget.name || widget.id,
    }));
    const list = fromApi.length ? fromApi : DEFAULT_WIDGETS;
    setAvailableWidgets(list);
    setSelectedWidgets(list.map((widget) => widget.id));
    setCustomizeError('');
    setCustomizeOpen(true);
  };

  const saveCustomization = async () => {
    setCustomizeSaving(true);
    setCustomizeError('');
    try {
      await dashboardService.saveCustomization({ widgets: selectedWidgets });
      setCustomizeOpen(false);
      queryClient.invalidateQueries('dashboard-widgets');
    } catch (err) {
      setCustomizeError(getApiErrorMessage(err, 'Could not save dashboard layout'));
    } finally {
      setCustomizeSaving(false);
    }
  };

  if (overviewLoading || widgetsLoading) {
    return (
      <PageShell>
        <PageLoading label="Loading dashboard…" />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageHeader
        title="Smart Dashboard"
        subtitle="Live mill snapshot from farmers, stock, batches, orders, and invoices"
        actions={
          <>
            <IconButton onClick={handleRefresh} aria-label="Refresh dashboard">
              <Refresh />
            </IconButton>
            <IconButton onClick={handleCustomize} aria-label="Customize dashboard widgets">
              <Settings />
            </IconButton>
          </>
        }
      />

      {/* AI Insights Banner */}
      {insights?.insights?.length > 0 && (
        <AIInsights insights={insights.insights} />
      )}

      {/* Alerts Panel */}
      {alerts?.alerts?.length > 0 && (
        <AlertsPanel alerts={alerts.alerts} />
      )}

      {overviewError && (
        <QueryErrorAlert error={overviewErr} onRetry={refetchOverview} entity="dashboard metrics" />
      )}
      {widgetsError && (
        <QueryErrorAlert error={widgetsErr} onRetry={refetchWidgets} entity="dashboard widgets" />
      )}

      {/* Key Metrics Summary */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title="Production"
            value={`${overview?.summary?.total_production?.toFixed(0) || 0} kg`}
            trend={overview?.trends?.production}
            icon={<TrendingUp />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title="Quality Score"
            value={`${overview?.summary?.quality_score?.toFixed(1) || 0}%`}
            trend={overview?.trends?.quality}
            icon={<Insights />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title="Inventory Value"
            value={`₹${(overview?.summary?.inventory_value || 0).toLocaleString()}`}
            trend={overview?.trends?.inventory}
            icon={<TrendingUp />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title="Pending Orders"
            value={overview?.summary?.pending_orders || 0}
            trend={overview?.trends?.orders}
            icon={<Warning />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title="Active Farmers"
            value={overview?.summary?.active_farmers || 0}
            trend={overview?.trends?.farmers}
            icon={<TrendingUp />}
            color="secondary"
          />
        </Grid>
      </Grid>

      {/* Smart Widgets */}
      <Grid container spacing={3}>
        {(!widgets?.widgets || widgets.widgets.length === 0) && (
          <Grid item xs={12}>
            <Alert severity="info">
              No widgets yet. Production, inventory, and sales data will appear here as you use the mill.
            </Alert>
          </Grid>
        )}
        {widgets?.widgets?.map((widget, index) => (
          <Grid item xs={12} md={widget.size || 6} key={widget.id}>
            <SmartWidget widget={widget} />
          </Grid>
        ))}
      </Grid>

      {/* Customization Dialog */}
      <Dialog open={customizeOpen} onClose={() => setCustomizeOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Customize Dashboard</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" mb={2}>
            Choose which metric cards to keep in view. The mill still shows live numbers from farmers, stock, batches, and invoices.
          </Typography>
          {customizeError && <Alert severity="error" sx={{ mb: 2 }}>{customizeError}</Alert>}
          <FormGroup>
            {availableWidgets.map((widget) => (
              <FormControlLabel
                key={widget.id}
                control={
                  <Checkbox
                    checked={selectedWidgets.includes(widget.id)}
                    onChange={(event) => {
                      const checked = event.target.checked;
                      setSelectedWidgets((prev) => (
                        checked ? [...prev, widget.id] : prev.filter((id) => id !== widget.id)
                      ));
                    }}
                  />
                }
                label={widget.label}
              />
            ))}
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCustomizeOpen(false)} disabled={customizeSaving}>Cancel</Button>
          <Button onClick={saveCustomization} variant="contained" disabled={customizeSaving}>
            {customizeSaving ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
};

const MetricCard = ({ title, value, trend, icon, color }) => {
  const getTrendIcon = () => {
    if (!trend) return null;
    if (trend.direction === 'up') return <TrendingUp color="success" fontSize="small" />;
    if (trend.direction === 'down') return <TrendingDown color="error" fontSize="small" />;
    return null;
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h5" component="div" fontWeight="bold">
              {value}
            </Typography>
            {trend && (
              <Box display="flex" alignItems="center" mt={1}>
                {getTrendIcon()}
                <Typography variant="body2" color={trend.direction === 'up' ? 'success.main' : 'error.main'} ml={0.5}>
                  {trend.percentage}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default Dashboard;