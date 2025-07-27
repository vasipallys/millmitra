import { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Alert,
  CircularProgress, Chip, IconButton, Menu, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions, Button
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Warning, Info, Error,
  Settings, Refresh, MoreVert, Insights
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { dashboardService } from '../services/dashboardService';
import { useQuery, useQueryClient } from 'react-query';
import SmartWidget from '../components/SmartWidget';
import AIInsights from '../components/AIInsights';
import AlertsPanel from '../components/AlertsPanel';
import NaturalLanguageQuery from '../components/NaturalLanguageQuery';

const Dashboard = () => {
  const [timeRange, setTimeRange] = useState(7);
  const [customizeOpen, setCustomizeOpen] = useState(false);
  const [selectedWidgets, setSelectedWidgets] = useState([]);
  const queryClient = useQueryClient();

  // Fetch dashboard data
  const { data: overview, isLoading: overviewLoading } = useQuery(
    ['dashboard-overview', timeRange],
    () => dashboardService.getOverview(timeRange),
    { refetchInterval: 30000 } // Refresh every 30 seconds
  );

  const { data: widgets, isLoading: widgetsLoading } = useQuery(
    'dashboard-widgets',
    dashboardService.getWidgets,
    { refetchInterval: 60000 } // Refresh every minute
  );

  const { data: insights } = useQuery(
    'dashboard-insights',
    dashboardService.getInsights,
    { refetchInterval: 120000 } // Refresh every 2 minutes
  );

  const { data: alerts } = useQuery(
    'dashboard-alerts',
    dashboardService.getAlerts,
    { refetchInterval: 30000 }
  );

  const handleRefresh = () => {
    queryClient.invalidateQueries('dashboard');
  };

  const handleCustomize = () => {
    setCustomizeOpen(true);
  };

  const saveCustomization = () => {
    dashboardService.saveCustomization({ widgets: selectedWidgets });
    setCustomizeOpen(false);
    queryClient.invalidateQueries('dashboard-widgets');
  };

  if (overviewLoading || widgetsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}> {/* Add padding to dashboard content */}
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Smart Dashboard
        </Typography>
        <Box>
          <IconButton onClick={handleRefresh}>
            <Refresh />
          </IconButton>
          <IconButton onClick={handleCustomize}>
            <Settings />
          </IconButton>
        </Box>
      </Box>

      {/* AI Insights Banner */}
      {insights?.insights?.length > 0 && (
        <AIInsights insights={insights.insights} />
      )}

      {/* Alerts Panel */}
      {alerts?.alerts?.length > 0 && (
        <AlertsPanel alerts={alerts.alerts} />
      )}

      {/* Natural Language Query Interface */}
      <Box mb={3}>
        <NaturalLanguageQuery
          onQueryResult={(result) => {
            console.log('Query result:', result);
            // Could trigger dashboard updates based on query results
          }}
        />
      </Box>

      {/* Key Metrics Summary */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Production"
            value={`${overview?.summary?.total_production?.toFixed(0) || 0} kg`}
            trend={overview?.trends?.production}
            icon={<TrendingUp />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Quality Score"
            value={`${overview?.summary?.quality_score?.toFixed(1) || 0}%`}
            trend={overview?.trends?.quality}
            icon={<Insights />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Inventory Value"
            value={`₹${(overview?.summary?.inventory_value || 0).toLocaleString()}`}
            trend={overview?.trends?.inventory}
            icon={<TrendingUp />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Pending Orders"
            value={overview?.summary?.pending_orders || 0}
            trend={overview?.trends?.orders}
            icon={<Warning />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
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
            Select which widgets to display on your dashboard. AI will automatically prioritize them based on your role and current context.
          </Typography>
          {/* Widget selection interface would go here */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCustomizeOpen(false)}>Cancel</Button>
          <Button onClick={saveCustomization} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
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