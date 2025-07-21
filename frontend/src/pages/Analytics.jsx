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

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('30d');
  const [loading, setLoading] = useState(true);
  const [aiInsights, setAiInsights] = useState([]);

  // Mock data
  const performanceMetrics = {
    efficiency: 87.5,
    profitMargin: 23.8,
    customerSatisfaction: 94.2,
    qualityScore: 91.7,
  };

  const productionTrend = [
    { date: '2024-01-01', production: 2400, efficiency: 85, quality: 92 },
    { date: '2024-01-02', production: 2600, efficiency: 88, quality: 94 },
    { date: '2024-01-03', production: 2200, efficiency: 82, quality: 89 },
    { date: '2024-01-04', production: 2800, efficiency: 91, quality: 96 },
    { date: '2024-01-05', production: 2500, efficiency: 87, quality: 93 },
    { date: '2024-01-06', production: 2700, efficiency: 89, quality: 95 },
    { date: '2024-01-07', production: 2900, efficiency: 93, quality: 97 },
  ];

  const salesByProduct = [
    { name: 'Basmati Rice', value: 35, color: '#2E7D32' },
    { name: 'Jasmine Rice', value: 25, color: '#FF9800' },
    { name: 'Brown Rice', value: 20, color: '#1976D2' },
    { name: 'White Rice', value: 15, color: '#9C27B0' },
    { name: 'Others', value: 5, color: '#607D8B' },
  ];

  const financialData = [
    { month: 'Jan', revenue: 450000, costs: 320000, profit: 130000 },
    { month: 'Feb', revenue: 520000, costs: 350000, profit: 170000 },
    { month: 'Mar', revenue: 480000, costs: 340000, profit: 140000 },
    { month: 'Apr', revenue: 580000, costs: 380000, profit: 200000 },
    { month: 'May', revenue: 620000, costs: 400000, profit: 220000 },
    { month: 'Jun', revenue: 680000, costs: 420000, profit: 260000 },
  ];

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
    // Simulate API call
    setTimeout(() => {
      setAiInsights(mockInsights);
      setLoading(false);
    }, 1500);
  }, [timeRange]);

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
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Business Analytics
        </Typography>
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

      {/* AI Insights Alert */}
      <Alert
        severity="info"
        icon={<AIIcon />}
        sx={{ mb: 3 }}
      >
        <Typography variant="subtitle2">
          AI Analysis Complete
        </Typography>
        <Typography variant="body2">
          {aiInsights.length} insights generated based on your data patterns
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
                    {performanceMetrics.efficiency}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingUpIcon color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      +2.3% from last month
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
                    {performanceMetrics.profitMargin}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingUpIcon color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      +1.8% from last month
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
                    Customer Satisfaction
                  </Typography>
                  <Typography variant="h4" component="div" color="info.main">
                    {performanceMetrics.customerSatisfaction}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingUpIcon color="success" sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="body2" color="success.main">
                      +5.2% from last month
                    </Typography>
                  </Box>
                </Box>
                <CircularProgress
                  variant="determinate"
                  value={performanceMetrics.customerSatisfaction}
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
                    {performanceMetrics.qualityScore}%
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <TrendingDownIcon color="error" sx={{ fontSize: 16, mr: 0.5 }} />
                    <Typography variant="body2" color="error.main">
                      -0.8% from last month
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
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sales by Product
              </Typography>
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
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AI Insights */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <AIIcon sx={{ mr: 1 }} />
            AI-Generated Insights
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
