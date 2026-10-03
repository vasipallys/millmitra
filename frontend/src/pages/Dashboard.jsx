import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid, Card, CardContent, Typography, Box, Alert,
  Dialog, DialogTitle, DialogContent, DialogActions, Button,
  FormGroup, FormControlLabel, Checkbox
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Warning,
  Settings, Refresh, Insights
} from '@mui/icons-material';
import { dashboardService } from '../services/dashboardService';
import { farmerService } from '../services/farmerService';
import { inventoryService } from '../services/inventoryService';
import { productionService } from '../services/productionService';
import { useQuery, useQueryClient } from 'react-query';
import SmartWidget from '../components/SmartWidget';
import AIInsights from '../components/AIInsights';
import AlertsPanel from '../components/AlertsPanel';
import { PageHeader, PageLoading, PageShell, QueryErrorAlert } from '../components/common/PageChrome';
import { getApiErrorMessage } from '../utils/apiError';
import { useI18n } from '../i18n/I18nContext';
import { can, storedUser } from '../utils/permissions';
import { suggestMillStep, unwrapList } from '../utils/millFlowSuggestion';

const DEFAULT_WIDGETS = [
  { id: 'production', label: 'Production snapshot' },
  { id: 'inventory', label: 'Inventory value' },
  { id: 'sales', label: 'Pending orders' },
  { id: 'farmers', label: 'Active farmers' },
  { id: 'quality', label: 'Quality score' },
];

const Dashboard = () => {
  const { t } = useI18n();
  const navigate = useNavigate();
  const user = storedUser();
  const canMillFlow = can(user, 'mill_flow');
  const canFarmers = can(user, 'farmers');
  const canInventory = can(user, 'inventory');
  const canSales = can(user, 'sales');
  const canFinance = can(user, 'finance');
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

  const { data: farmersPayload } = useQuery(
    'dashboard-next-farmers',
    () => farmerService.getFarmers({}),
    { enabled: canFarmers, retry: false }
  );
  const { data: paddyPayload } = useQuery(
    'dashboard-next-paddy',
    () => inventoryService.getPaddyStock(),
    { enabled: canInventory, retry: false }
  );
  const { data: batchesPayload } = useQuery(
    'dashboard-next-batches',
    () => productionService.getBatches({ per_page: 20 }),
    { enabled: can(user, 'production'), retry: false }
  );

  const nextAction = useMemo(() => {
    const farmers = unwrapList(farmersPayload, ['farmers', 'items']);
    const paddyLots = unwrapList(paddyPayload, ['stocks', 'stock', 'paddy_stock', 'items']);
    const batches = unwrapList(batchesPayload, ['batches', 'items']);
    const emptyMill = farmers.length === 0 && paddyLots.length === 0 && batches.length === 0;
    if (emptyMill) {
      if (canFarmers) {
        return { title: t('nextActionRegisterFarmer'), reason: t('nextActionEmpty'), path: '/farmers', label: t('nextActionRegisterFarmer') };
      }
      if (canInventory) {
        return { title: t('nextActionAddStock'), reason: t('nextActionEmpty'), path: '/inventory', label: t('nextActionAddStock') };
      }
    }
    const suggested = suggestMillStep({ paddyLots, batches, products: [], invoices: [] });
    if (canMillFlow) {
      return {
        title: t(suggested.title) || t('millFlow'),
        reason: t(suggested.reason, suggested.reasonVars) || t('millFlowSubtitle'),
        path: '/mill-flow',
        label: t('nextActionGoMillFlow'),
      };
    }
    if (canFarmers) {
      return { title: t('nextActionRegisterFarmer'), reason: t('nextActionEmpty'), path: '/farmers', label: t('nextActionRegisterFarmer') };
    }
    return { title: t('nextAction'), reason: t('dashboardSubtitle'), path: '/dashboard', label: t('refresh') };
  }, [farmersPayload, paddyPayload, batchesPayload, canFarmers, canInventory, canMillFlow, t]);

  const handleRefresh = () => {
    queryClient.invalidateQueries('dashboard-overview');
    queryClient.invalidateQueries('dashboard-widgets');
    queryClient.invalidateQueries('dashboard-insights');
    queryClient.invalidateQueries('dashboard-alerts');
    queryClient.invalidateQueries('dashboard-next-farmers');
    queryClient.invalidateQueries('dashboard-next-paddy');
    queryClient.invalidateQueries('dashboard-next-batches');
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
        <PageLoading label={t('loadingDashboard')} />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageHeader
        title={t('dashboardTitle')}
        subtitle={t('dashboardSubtitle')}
        actions={
          <>
            <Button variant="outlined" startIcon={<Refresh />} onClick={handleRefresh} sx={{ minHeight: 40 }}>
              {t('refresh')}
            </Button>
            <Button variant="outlined" startIcon={<Settings />} onClick={handleCustomize} sx={{ minHeight: 40 }}>
              {t('customize')}
            </Button>
          </>
        }
      />

      <Card sx={{ mb: 3, border: '1px solid', borderColor: 'primary.light' }}>
        <CardContent sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, alignItems: { sm: 'center' } }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="overline" color="primary">{t('nextAction')}</Typography>
            <Typography variant="h6">{nextAction.title}</Typography>
            <Typography variant="body2" color="text.secondary">{nextAction.reason}</Typography>
          </Box>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate(nextAction.path)}
            sx={{ minHeight: 44, minWidth: 200 }}
          >
            {nextAction.label}
          </Button>
        </CardContent>
      </Card>

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
            title={t('dashProduction')}
            value={`${overview?.summary?.total_production?.toFixed(0) || 0} kg`}
            trend={overview?.trends?.production}
            icon={<TrendingUp />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title={t('dashQualityScore')}
            value={`${overview?.summary?.quality_score?.toFixed(1) || 0}%`}
            trend={overview?.trends?.quality}
            icon={<Insights />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title={t('dashInventoryValue')}
            value={`₹${(overview?.summary?.inventory_value || 0).toLocaleString()}`}
            trend={overview?.trends?.inventory}
            icon={<TrendingUp />}
            color="info"
          />
        </Grid>
        {(canSales || canFinance) && (
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title={t('dashPendingOrders')}
            value={overview?.summary?.pending_orders || 0}
            trend={overview?.trends?.orders}
            icon={<Warning />}
            color="warning"
          />
        </Grid>
        )}
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <MetricCard
            title={t('dashActiveFarmers')}
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
        <DialogTitle>{t('customizeDashboard')}</DialogTitle>
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
          <Button onClick={() => setCustomizeOpen(false)} disabled={customizeSaving}>{t('cancel')}</Button>
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