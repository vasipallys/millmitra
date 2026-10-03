import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Analytics,
  Payment,
  Assessment,
  Warning,
  CheckCircle,
  MonetizationOn,
  Psychology,
  AutoGraph,
  SmartToy,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import DemoBanner from '../components/DemoBanner';
import PreviewModeToggle from '../components/PreviewModeToggle';
import { usePreviewMode } from '../hooks/usePreviewMode';
import { financeService } from '../services/financeService';
import {
  cashFlowFromInvoices,
  derivedFinanceHealth,
  financeInsightsFromRecords,
  financialSeriesFromCashFlow,
  unwrapList,
} from '../utils/previewLiveData';

const FinancialIntelligence = () => {
  const { mode, setMode, isSample } = usePreviewMode('financial-intelligence');
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState(null);
  const [cashFlowData, setCashFlowData] = useState(null);
  const [healthScore, setHealthScore] = useState(null);
  const [insights, setInsights] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [paymentForm, setPaymentForm] = useState({
    farmer_id: '',
    amount: '',
    payment_type: 'procurement'
  });
  const [pageMessage, setPageMessage] = useState(null);
  const [paymentError, setPaymentError] = useState('');
  const [alertItem, setAlertItem] = useState(null);
  const [scheduledPayments, setScheduledPayments] = useState([]);

  // Mock data for demonstration
  const mockCashFlowTrend = [
    { date: '2024-01-01', inflow: 45000, outflow: 32000, net: 13000 },
    { date: '2024-01-02', inflow: 52000, outflow: 38000, net: 14000 },
    { date: '2024-01-03', inflow: 48000, outflow: 35000, net: 13000 },
    { date: '2024-01-04', inflow: 55000, outflow: 42000, net: 13000 },
    { date: '2024-01-05', inflow: 58000, outflow: 45000, net: 13000 },
    { date: '2024-01-06', inflow: 62000, outflow: 48000, net: 14000 },
    { date: '2024-01-07', inflow: 59000, outflow: 44000, net: 15000 },
  ];

  const mockHealthScoreData = {
    overall_score: 87.5,
    health_grade: 'B',
    health_status: 'Good',
    component_scores: {
      liquidity: 92.0,
      leverage: 78.0,
      profitability: 89.0,
      efficiency: 85.0,
      cash_flow: 88.0
    }
  };

  const mockInsights = [
    {
      category: 'cash_flow',
      type: 'positive',
      title: 'Strong Cash Flow Performance',
      description: 'Cash flow improved by 15% compared to last month',
      recommendation: 'Consider investing surplus cash for better returns'
    },
    {
      category: 'payment_optimization',
      type: 'warning',
      title: 'Payment Processing Inefficiency',
      description: '12 pending payments could be optimized through batching',
      recommendation: 'Implement batch payment processing to reduce costs'
    },
    {
      category: 'forecast',
      type: 'positive',
      title: 'Revenue Growth Predicted',
      description: 'AI forecasts 8% revenue growth in next quarter',
      recommendation: 'Prepare for increased working capital requirements'
    }
  ];

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      if (isSample) {
        setDashboardData({
          summary: {
            monthly_revenue: 1250000,
            monthly_expenses: 980000,
            monthly_profit: 270000,
            profit_margin: 21.6,
            pending_payments: 8,
            pending_amount: 145000
          }
        });
        setCashFlowData(mockCashFlowTrend);
        setHealthScore(mockHealthScoreData);
        setInsights(mockInsights);
        setAlerts([
          {
            type: 'warning',
            category: 'payments',
            title: 'Overdue Payments',
            message: '3 payments are overdue',
            action_required: true
          }
        ]);
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const [summary, cashFlow, receivables, invoicesPayload] = await Promise.all([
          financeService.getFinancialSummary(30),
          financeService.getCashFlow('monthly'),
          financeService.getAccountsReceivable(),
          financeService.getInvoices({ limit: 50 }),
        ]);
        if (cancelled) return;
        const invoices = unwrapList(invoicesPayload, ['invoices', 'items']);
        const revenue = Number(summary?.total_revenue || 0);
        const expenses = Number(summary?.total_expenses || 0);
        const profit = Number(summary?.net_profit ?? (revenue - expenses));
        setDashboardData({
          summary: {
            monthly_revenue: revenue,
            monthly_expenses: expenses,
            monthly_profit: profit,
            profit_margin: revenue ? (profit / revenue) * 100 : 0,
            pending_payments: Number(receivables?.overdue_count || invoices.filter((inv) => String(inv.status).toLowerCase() !== 'paid').length),
            pending_amount: Number(receivables?.total_outstanding || summary?.outstanding_receivables || 0),
          }
        });
        const series = financialSeriesFromCashFlow(cashFlow);
        setCashFlowData(series.length ? series : cashFlowFromInvoices(invoices));
        setHealthScore(derivedFinanceHealth(summary, receivables));
        setInsights(financeInsightsFromRecords({ summary, receivables, invoices }));
        setAlerts(
          Number(receivables?.overdue_count) > 0
            ? [{
                type: 'warning',
                category: 'payments',
                title: 'Overdue invoices',
                message: `${receivables.overdue_count} invoice(s) overdue totaling ₹${Number(receivables.total_overdue || 0).toLocaleString('en-IN')}`,
                action_required: true
              }]
            : []
        );
      } catch (error) {
        if (!cancelled) {
          console.error('Failed to load dashboard data:', error);
          setDashboardData({
            summary: {
              monthly_revenue: 0,
              monthly_expenses: 0,
              monthly_profit: 0,
              profit_margin: 0,
              pending_payments: 0,
              pending_amount: 0,
            }
          });
          setCashFlowData([]);
          setHealthScore(derivedFinanceHealth({}, {}));
          setInsights(financeInsightsFromRecords({ summary: {}, receivables: {}, invoices: [] }));
          setAlerts([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isSample]);

  const handleSmartPaymentScheduling = () => {
    const amount = Number(paymentForm.amount);
    if (!paymentForm.farmer_id) {
      setPaymentError('Farmer ID is required');
      return;
    }
    if (!Number.isFinite(amount) || amount <= 0) {
      setPaymentError('Amount must be greater than 0');
      return;
    }
    setPaymentError('');
    setScheduledPayments((prev) => [
      {
        id: Date.now(),
        ...paymentForm,
        amount,
        created_at: new Date().toISOString(),
      },
      ...prev,
    ]);
    setShowPaymentDialog(false);
    setPaymentForm({ farmer_id: '', amount: '', payment_type: 'procurement' });
    setPageMessage({
      severity: 'success',
      text: `Preview payment of ₹${amount.toLocaleString('en-IN')} stored on this screen only. Use Finance → Record Payment for mill-of-record money.`,
    });
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'positive': return <CheckCircle color="success" />;
      case 'warning': return <Warning color="warning" />;
      case 'critical': return <Warning color="error" />;
      default: return <Psychology color="info" />;
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case 'positive': return 'success';
      case 'warning': return 'warning';
      case 'critical': return 'error';
      default: return 'info';
    }
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Financial Intelligence...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <DemoBanner title="Financial Intelligence" mode={mode} />
      {pageMessage && (
        <Alert severity={pageMessage.severity} sx={{ mb: 2 }} onClose={() => setPageMessage(null)}>
          {pageMessage.text}
        </Alert>
      )}
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Financial Intelligence
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Invoices, payments, aging, and cash flow from Finance. Sample figures are opt-in.
          </Typography>
        </Box>
        <PreviewModeToggle mode={mode} onChange={setMode} />
      </Box>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {alerts.map((alert, index) => (
            <Alert 
              key={index} 
              severity={alert.type} 
              sx={{ mb: 1 }}
              action={
                alert.action_required && (
                  <Button color="inherit" size="small" onClick={() => setAlertItem(alert)}>
                    Action Required
                  </Button>
                )
              }
            >
              <strong>{alert.title}:</strong> {alert.message}
            </Alert>
          ))}
        </Box>
      )}

      {/* Financial Intelligence Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab icon={<Analytics />} label="Dashboard" />
          <Tab icon={<TrendingUp />} label="Cash Flow" />
          <Tab icon={<Assessment />} label="Health Score" />
          <Tab icon={<Psychology />} label="AI Insights" />
          <Tab icon={<Payment />} label="Smart Payments" />
        </Tabs>
      </Paper>

      {/* Dashboard Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          {/* Key Metrics Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Monthly Revenue
                    </Typography>
                    <Typography variant="h4" component="div" color="success.main">
                      ₹{dashboardData?.summary?.monthly_revenue?.toLocaleString()}
                    </Typography>
                  </Box>
                  <MonetizationOn color="success" sx={{ fontSize: 40 }} />
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
                      Monthly Profit
                    </Typography>
                    <Typography variant="h4" component="div" color="primary.main">
                      ₹{dashboardData?.summary?.monthly_profit?.toLocaleString()}
                    </Typography>
                  </Box>
                  <TrendingUp color="primary" sx={{ fontSize: 40 }} />
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
                    <Typography variant="h4" component="div" color="info.main">
                      {dashboardData?.summary?.profit_margin?.toFixed(1)}%
                    </Typography>
                  </Box>
                  <Analytics color="info" sx={{ fontSize: 40 }} />
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
                      Pending Payments
                    </Typography>
                    <Typography variant="h4" component="div" color="warning.main">
                      {dashboardData?.summary?.pending_payments}
                    </Typography>
                  </Box>
                  <Payment color="warning" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Cash Flow Chart */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cash Flow Trend
                </Typography>
                {!cashFlowData?.length ? (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 6, textAlign: 'center' }}>
                    No invoice or cash-flow series yet.
                  </Typography>
                ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={cashFlowData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                    <Area type="monotone" dataKey="net" stroke="#2E7D32" fill="#4CAF50" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Financial Health Score */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {isSample ? 'Financial Health Score' : 'Collection rate'}
                </Typography>
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Typography variant="h2" color="primary.main">
                    {healthScore?.overall_score}
                  </Typography>
                  <Chip 
                    label={`Grade ${healthScore?.health_grade}`} 
                    color="primary" 
                    size="large" 
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {healthScore?.health_status}
                  </Typography>
                </Box>
                
                {/* Component Scores */}
                {healthScore?.component_scores && Object.entries(healthScore.component_scores).map(([key, value]) => (
                  <Box key={key} sx={{ mb: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                        {key.replace('_', ' ')}
                      </Typography>
                      <Typography variant="body2">{value}%</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={value} 
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Cash Flow Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Detailed Cash Flow Analysis
                </Typography>
                {!cashFlowData?.length ? (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 6, textAlign: 'center' }}>
                    No cash-flow records yet.
                  </Typography>
                ) : (
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={cashFlowData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                    <Line type="monotone" dataKey="inflow" stroke="#4CAF50" strokeWidth={3} name="Cash Inflow" />
                    <Line type="monotone" dataKey="outflow" stroke="#F44336" strokeWidth={3} name="Cash Outflow" />
                    <Line type="monotone" dataKey="net" stroke="#2196F3" strokeWidth={3} name="Net Cash Flow" />
                  </LineChart>
                </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Health Score Tab */}
      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Financial Health Assessment
                </Typography>
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  <Typography variant="h1" color="primary.main">
                    {healthScore?.overall_score}
                  </Typography>
                  <Typography variant="h5" color="text.secondary">
                    Grade {healthScore?.health_grade} - {healthScore?.health_status}
                  </Typography>
                </Box>
                
                <Typography variant="h6" gutterBottom>
                  Component Analysis
                </Typography>
                {healthScore?.component_scores && Object.entries(healthScore.component_scores).map(([key, value]) => (
                  <Box key={key} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body1" sx={{ textTransform: 'capitalize', fontWeight: 500 }}>
                        {key.replace('_', ' ')}
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">{value}%</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={value} 
                      sx={{ height: 8, borderRadius: 4 }}
                      color={value >= 80 ? 'success' : value >= 60 ? 'warning' : 'error'}
                    />
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Improvement Recommendations
                </Typography>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    {isSample
                      ? 'Sample health notes. Focus on the areas below.'
                      : 'These percentages are derived from Finance invoices and payments, not a credit rating or ML score.'}
                  </Typography>
                </Alert>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="warning.main">
                    • Improve Leverage Ratio
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Consider reducing debt levels to improve leverage score
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="info.main">
                    • Optimize Efficiency
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Review operational processes to improve efficiency metrics
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="subtitle2" color="success.main">
                    • Maintain Liquidity
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Excellent liquidity position - continue current practices
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* AI Insights Tab */}
      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          {insights.map((insight, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    {getInsightIcon(insight.type)}
                    <Box sx={{ ml: 2, flexGrow: 1 }}>
                      <Typography variant="h6" gutterBottom>
                        {insight.title}
                      </Typography>
                      <Chip 
                        label={insight.category.replace('_', ' ')} 
                        color={getInsightColor(insight.type)} 
                        size="small" 
                        sx={{ mb: 1 }}
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {insight.description}
                  </Typography>
                  
                  <Alert severity={getInsightColor(insight.type)} variant="outlined">
                    <Typography variant="body2">
                      <strong>Recommendation:</strong> {insight.recommendation}
                    </Typography>
                  </Alert>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Smart Payments Tab */}
      <TabPanel value={activeTab} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Smart Payment Scheduling
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  AI-powered payment optimization based on risk analysis and cash flow predictions
                </Typography>
                
                <Button
                  variant="contained"
                  startIcon={<SmartToy />}
                  onClick={() => setShowPaymentDialog(true)}
                  size="large"
                >
                  Schedule Smart Payment
                </Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Payment Optimization Benefits
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="primary.main">
                    • Risk-Based Scheduling
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    AI analyzes farmer payment history to optimize terms
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="primary.main">
                    • Cash Flow Prediction
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Predicts impact on cash flow before scheduling
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="subtitle2" color="primary.main">
                    • Automated Recommendations
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Suggests optimal payment terms and timing
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Smart Payment Dialog */}
      <Dialog open={showPaymentDialog} onClose={() => setShowPaymentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Schedule Smart Payment</DialogTitle>
        <DialogContent>
          {paymentError && <Alert severity="error" sx={{ mt: 1 }}>{paymentError}</Alert>}
          <TextField
            fullWidth
            label="Farmer ID"
            value={paymentForm.farmer_id}
            onChange={(e) => setPaymentForm({ ...paymentForm, farmer_id: e.target.value })}
            margin="normal"
            type="number"
          />
          <TextField
            fullWidth
            label="Amount (₹)"
            value={paymentForm.amount}
            onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })}
            margin="normal"
            type="number"
          />
          <TextField
            fullWidth
            select
            label="Payment Type"
            value={paymentForm.payment_type}
            onChange={(e) => setPaymentForm({ ...paymentForm, payment_type: e.target.value })}
            margin="normal"
          >
            <MenuItem value="procurement">Procurement</MenuItem>
            <MenuItem value="advance">Advance</MenuItem>
            <MenuItem value="bonus">Bonus</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPaymentDialog(false)}>Cancel</Button>
          <Button onClick={handleSmartPaymentScheduling} variant="contained">
            Schedule Payment
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(alertItem)} onClose={() => setAlertItem(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{alertItem?.title}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>{alertItem?.message}</Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Preview reminder. Record real collections on Finance → Record Payment.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAlertItem(null)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              setAlertItem(null);
              setActiveTab(4);
            }}
          >
            Open Smart Payments
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FinancialIntelligence;
