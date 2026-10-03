import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  ButtonGroup,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Analytics as AnalyticsIcon,
  SmartToy as AIIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import DemoBanner from '../components/DemoBanner';
import PreviewModeToggle from '../components/PreviewModeToggle';
import { usePreviewMode } from '../hooks/usePreviewMode';
import { useI18n } from '../i18n/I18nContext';
import { dashboardService } from '../services/dashboardService';
import { financeService } from '../services/financeService';
import { productionService } from '../services/productionService';
import { productionAPI, salesAPI } from '../services/api';
import {
  daysFromRange,
  financialSeriesFromCashFlow,
  mapDashboardInsights,
  normalizeQualityTests,
  productionTrendFromRecords,
  qualityDashboardFromTests,
  salesByProductFromOrders,
  unwrapList,
} from '../utils/previewLiveData';

const Analytics = () => {
  const { t } = useI18n();
  const { mode, setMode, isSample } = usePreviewMode('analytics');
  const [timeRange, setTimeRange] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [aiInsights, setAiInsights] = useState([]);
  const [liveMetrics, setLiveMetrics] = useState(null);
  const [liveProductionTrend, setLiveProductionTrend] = useState([]);
  const [liveSalesByProduct, setLiveSalesByProduct] = useState([]);
  const [liveFinancial, setLiveFinancial] = useState([]);
  const [loadError, setLoadError] = useState('');

  const mockInsights = [
    {
      id: 1,
      type: 'opportunity',
      title: 'Production Optimization',
      description: 'AI detected 15% efficiency improvement potential in evening shift',
      impact: 'High',
      confidence: 92,
    },
    {
      id: 2,
      type: 'warning',
      title: 'Quality Trend Alert',
      description: 'Slight decline in quality metrics for Basmati rice production',
      impact: 'Medium',
      confidence: 87,
    },
    {
      id: 3,
      type: 'success',
      title: 'Customer Retention',
      description: 'Customer satisfaction increased by 8% this month',
      impact: 'High',
      confidence: 95,
    },
  ];

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      if (isSample) {
        setAiInsights(mockInsights);
        setLiveMetrics(null);
        setLiveProductionTrend([]);
        setLiveSalesByProduct([]);
        setLiveFinancial([]);
        setLoadError('');
        setLoading(false);
        return;
      }
      setLoading(true);
      setLoadError('');
      const days = daysFromRange(timeRange);
      try {
        const [overviewRes, prodRes, financeRes, salesRes, ordersRes, testsRes, insightsRes, batchesRes, cashRes] = await Promise.allSettled([
          dashboardService.getOverview(days),
          productionService.getAnalytics(days),
          financeService.getFinancialSummary(days),
          salesAPI.getAnalytics(),
          salesAPI.getOrders({ per_page: 50 }),
          productionAPI.getQualityTests({ per_page: 50 }),
          dashboardService.getInsights(),
          productionService.getBatches({ per_page: 50 }),
          financeService.getCashFlow('monthly'),
        ]);
        if (cancelled) return;
        const overview = overviewRes.status === 'fulfilled' ? overviewRes.value : {};
        const production = prodRes.status === 'fulfilled' ? (prodRes.value?.analytics || prodRes.value) : {};
        const finance = financeRes.status === 'fulfilled' ? financeRes.value : {};
        const salesPayload = salesRes.status === 'fulfilled' ? salesRes.value?.data || salesRes.value : {};
        const tests = normalizeQualityTests(testsRes.status === 'fulfilled' ? testsRes.value?.data || testsRes.value : {});
        const batches = unwrapList(
          batchesRes.status === 'fulfilled' ? batchesRes.value : {},
          ['batches', 'items']
        );
        const quality = qualityDashboardFromTests(tests);
        const revenue = Number(finance.total_revenue || 0);
        const profit = Number(finance.net_profit || 0);
        setLiveMetrics({
          efficiency: Number(production.average_efficiency || 0),
          profitMargin: revenue ? (profit / revenue) * 100 : 0,
          pendingOrders: Number(overview?.summary?.pending_orders || salesPayload?.analytics?.total_orders || 0),
          qualityScore: Number(overview?.summary?.quality_score || quality.avgScore || 0),
          productionKg: Number(overview?.summary?.total_production || production.total_output || 0),
        });
        setLiveProductionTrend(productionTrendFromRecords(production, batches));
        const salesAnalytics = salesPayload?.analytics || {};
        const ordersPayload = ordersRes.status === 'fulfilled' ? ordersRes.value?.data || ordersRes.value : {};
        const orders = unwrapList(ordersPayload, ['orders']).concat(unwrapList(salesAnalytics, ['by_product', 'orders']));
        setLiveSalesByProduct(salesByProductFromOrders(orders));
        const cash = financialSeriesFromCashFlow(cashRes.status === 'fulfilled' ? cashRes.value : []);
        setLiveFinancial(cash);
        setAiInsights(mapDashboardInsights(insightsRes.status === 'fulfilled' ? insightsRes.value : []));
        if ([overviewRes, prodRes, financeRes].every((result) => result.status === 'rejected')) {
          setLoadError('Could not load mill records. Check that the API is running, or use View sample.');
        }
      } catch (error) {
        if (!cancelled) {
          setLoadError(error?.userMessage || 'Could not load mill records.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isSample, timeRange]);

  const performanceMetrics = isSample
    ? {
        efficiency: 87.5,
        profitMargin: 23.8,
        pendingOrders: 94.2,
        qualityScore: 91.7,
        pendingLabel: 'Customer Satisfaction',
      }
    : {
        efficiency: liveMetrics?.efficiency || 0,
        profitMargin: liveMetrics?.profitMargin || 0,
        pendingOrders: liveMetrics?.pendingOrders || 0,
        qualityScore: liveMetrics?.qualityScore || 0,
        pendingLabel: 'Pending / total orders',
      };

  const productionTrend = isSample ? [
    { date: '2024-01-01', production: 2400, efficiency: 85, quality: 92 },
    { date: '2024-01-02', production: 2600, efficiency: 88, quality: 94 },
    { date: '2024-01-03', production: 2200, efficiency: 82, quality: 89 },
    { date: '2024-01-04', production: 2800, efficiency: 91, quality: 96 },
    { date: '2024-01-05', production: 2500, efficiency: 87, quality: 93 },
    { date: '2024-01-06', production: 2700, efficiency: 89, quality: 95 },
    { date: '2024-01-07', production: 2900, efficiency: 93, quality: 97 },
  ] : liveProductionTrend;

  const salesByProduct = isSample ? [
    { name: 'Basmati Rice', value: 35, color: '#2E7D32' },
    { name: 'Jasmine Rice', value: 25, color: '#FF9800' },
    { name: 'Brown Rice', value: 20, color: '#1976D2' },
    { name: 'White Rice', value: 15, color: '#9C27B0' },
    { name: 'Others', value: 5, color: '#607D8B' },
  ] : liveSalesByProduct;

  const financialData = isSample ? [
    { month: 'Jan', revenue: 450000, costs: 320000, profit: 130000 },
    { month: 'Feb', revenue: 520000, costs: 350000, profit: 170000 },
    { month: 'Mar', revenue: 480000, costs: 340000, profit: 140000 },
    { month: 'Apr', revenue: 580000, costs: 380000, profit: 200000 },
    { month: 'May', revenue: 620000, costs: 400000, profit: 220000 },
    { month: 'Jun', revenue: 680000, costs: 420000, profit: 260000 },
  ] : liveFinancial;

  const getInsightIcon = (type) => {
    switch (type) {
      case 'opportunity': return <TrendingUpIcon color="success" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'success': return <SuccessIcon color="success" />;
      default: return <AnalyticsIcon />;
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case 'opportunity': return 'info';
      case 'warning': return 'warning';
      case 'success': return 'success';
      default: return 'default';
    }
  };

  const formatCurrency = (value) => `₹${(value / 1000).toFixed(0)}K`;

  return (
    <Box>
      <DemoBanner title={t('businessAnalytics')} mode={mode} />
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Business Analytics
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
        <PreviewModeToggle mode={mode} onChange={setMode} />
        <ButtonGroup variant="outlined">
          <Button
            variant={timeRange === '7d' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('7d')}
          >
            7 Days
          </Button>
          <Button
            variant={timeRange === '30d' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('30d')}
          >
            30 Days
          </Button>
          <Button
            variant={timeRange === '90d' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('90d')}
          >
            90 Days
          </Button>
        </ButtonGroup>
        </Box>
      </Box>

      {loadError && (
        <Alert severity="warning" sx={{ mb: 2 }}>{loadError}</Alert>
      )}

      {/* Insights Alert */}
      <Alert
        severity="info"
        icon={<AIIcon />}
        sx={{ mb: 3 }}
      >
        <Typography variant="subtitle2">
          {isSample ? 'Sample insights' : 'Mill record snapshot'}
        </Typography>
        <Typography variant="body2">
          {isSample
            ? `${aiInsights.length} demonstration insights`
            : aiInsights.length
              ? `${aiInsights.length} notes from dashboard records`
              : 'No dashboard notes yet. Charts stay empty until production, sales, or invoices exist.'}
        </Typography>
      </Alert>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Overall Efficiency
                  </Typography>
                    <Typography variant="h4" component="div" color="success.main">
                    {Number(performanceMetrics.efficiency || 0).toFixed(1)}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingUpIcon color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      {isSample ? '+2.3% from last month' : 'From completed production batches'}
                    </Typography>
                  </Box>
                </Box>
                <CircularProgress
                  variant="determinate"
                  value={performanceMetrics.efficiency}
                  size={60}
                  thickness={4}
                  sx={{ color: 'success.main' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Profit Margin
                  </Typography>
                    <Typography variant="h4" component="div" color="primary.main">
                    {Number(performanceMetrics.profitMargin || 0).toFixed(1)}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingUpIcon color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      {isSample ? '+1.8% from last month' : 'Revenue vs profit from Finance'}
                    </Typography>
                  </Box>
                </Box>
                <CircularProgress
                  variant="determinate"
                  value={performanceMetrics.profitMargin * 4}
                  size={60}
                  thickness={4}
                  sx={{ color: 'primary.main' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    {performanceMetrics.pendingLabel || 'Pending / total orders'}
                  </Typography>
                  <Typography variant="h4" component="div" color="info.main">
                    {isSample ? `${performanceMetrics.pendingOrders}%` : performanceMetrics.pendingOrders}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingUpIcon color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      {isSample ? '+5.2% from last month' : 'From Dashboard / Sales'}
                    </Typography>
                  </Box>
                </Box>
                <CircularProgress
                  variant="determinate"
                  value={Math.min(100, Number(isSample ? performanceMetrics.pendingOrders : performanceMetrics.qualityScore) || 0)}
                  size={60}
                  thickness={4}
                  sx={{ color: 'info.main' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Quality Score
                  </Typography>
                  <Typography variant="h4" component="div" color="warning.main">
                    {Number(performanceMetrics.qualityScore || 0).toFixed(1)}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingDownIcon color="error" sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="body2" color={isSample ? 'error.main' : 'text.secondary'}>
                      {isSample ? '-0.8% from last month' : 'From quality tests / dashboard'}
                    </Typography>
                  </Box>
                </Box>
                <CircularProgress
                  variant="determinate"
                  value={performanceMetrics.qualityScore}
                  size={60}
                  thickness={4}
                  sx={{ color: 'warning.main' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Production & Quality Trends
              </Typography>
              {!productionTrend.length ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
                  No production batches in this period yet.
                </Typography>
              ) : (
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={productionTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="production"
                    stroke="#2E7D32"
                    strokeWidth={3}
                    name="Production (kg)"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="efficiency"
                    stroke="#FF9800"
                    strokeWidth={2}
                    name="Efficiency (%)"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="quality"
                    stroke="#1976D2"
                    strokeWidth={2}
                    name="Quality (%)"
                  />
                </LineChart>
              </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sales by Product
              </Typography>
              {!salesByProduct.length ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
                  No sales orders to chart yet.
                </Typography>
              ) : (
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={salesByProduct}
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {salesByProduct.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Financial Analysis */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Performance
              </Typography>
              {!financialData.length ? (
                <Typography variant="body2" color="text.secondary" sx={{ py: 8, textAlign: 'center' }}>
                  No cash-flow or invoice series yet.
                </Typography>
              ) : (
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={financialData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={formatCurrency} />
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stackId="1"
                    stroke="#2E7D32"
                    fill="#2E7D32"
                    fillOpacity={0.6}
                    name="Revenue"
                  />
                  <Area
                    type="monotone"
                    dataKey="costs"
                    stackId="2"
                    stroke="#F44336"
                    fill="#F44336"
                    fillOpacity={0.6}
                    name="Costs"
                  />
                  <Line
                    type="monotone"
                    dataKey="profit"
                    stroke="#FF9800"
                    strokeWidth={3}
                    name="Profit"
                  />
                </AreaChart>
              </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AI Insights */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <AIIcon sx={{ mr: 1 }} />
            {isSample ? 'Sample insights' : 'Record notes'}
          </Typography>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper} elevation={0}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Insight</TableCell>
                    <TableCell>Impact</TableCell>
                    <TableCell>Confidence</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {!aiInsights.length && (
                    <TableRow>
                      <TableCell colSpan={4}>
                        <Typography variant="body2" color="text.secondary">No notes from mill records yet.</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                  {aiInsights.map((insight) => (
                    <TableRow key={insight.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getInsightIcon(insight.type)}
                          <Chip
                            label={insight.type}
                            color={getInsightColor(insight.type)}
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="subtitle2">{insight.title}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {insight.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={insight.impact}
                          color={insight.impact === 'High' ? 'error' : insight.impact === 'Medium' ? 'warning' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {insight.confidence == null ? (
                          <Typography variant="body2" color="text.secondary">—</Typography>
                        ) : (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <CircularProgress
                            variant="determinate"
                            value={insight.confidence}
                            size={24}
                            thickness={4}
                          />
                          <Typography variant="body2" sx={{ ml: 1 }}>
                            {insight.confidence}%
                          </Typography>
                        </Box>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Analytics;
