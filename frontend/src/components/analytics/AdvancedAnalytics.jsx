import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  IconButton,
  Chip,
  LinearProgress,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Analytics,
  PieChart,
  BarChart,
  Timeline,
  Refresh,
  Download,
  FilterList,
  Insights
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { usePWA } from '../../hooks/usePWA';
import { downloadText } from '../../utils/downloadFile';

const AdvancedAnalytics = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [timeRange, setTimeRange] = useState('30d');
  const [selectedMetrics, setSelectedMetrics] = useState(['production', 'quality', 'finance']);
  const { isOnline, getCachedData, cacheData } = usePWA();

  // Fetch analytics data
  const { data: analyticsData, isLoading, refetch } = useQuery(
    ['advanced-analytics', timeRange, selectedMetrics],
    () => fetchAnalyticsData(timeRange, selectedMetrics),
    {
      refetchInterval: isOnline ? 300000 : false, // 5 minutes when online
      staleTime: 600000, // 10 minutes
      onSuccess: (data) => {
        // Cache data for offline use
        cacheData(`analytics-${timeRange}`, data);
      },
      onError: async () => {
        // Try to get cached data when offline
        if (!isOnline) {
          const cached = await getCachedData(`analytics-${timeRange}`);
          return cached;
        }
      }
    }
  );

  const fetchAnalyticsData = async (range, metrics) => {
    // Simulate API call - replace with actual API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      overview: {
        totalProduction: 15420,
        productionGrowth: 12.5,
        qualityScore: 94.2,
        qualityTrend: 2.1,
        revenue: 2840000,
        revenueGrowth: 8.7,
        efficiency: 87.3,
        efficiencyTrend: -1.2
      },
      trends: {
        production: generateTrendData(30),
        quality: generateTrendData(30),
        revenue: generateTrendData(30),
        efficiency: generateTrendData(30)
      },
      insights: [
        {
          type: 'success',
          title: 'Production Efficiency Up',
          description: 'Production efficiency increased by 5% this month',
          impact: 'high',
          recommendation: 'Continue current optimization strategies'
        },
        {
          type: 'warning',
          title: 'Quality Variance Detected',
          description: 'Quality scores show increased variance in the last week',
          impact: 'medium',
          recommendation: 'Review quality control processes'
        },
        {
          type: 'info',
          title: 'Market Opportunity',
          description: 'Premium rice demand increased by 15% in target markets',
          impact: 'high',
          recommendation: 'Consider expanding premium rice production'
        }
      ],
      predictions: {
        nextMonthProduction: 16200,
        nextMonthQuality: 95.1,
        nextMonthRevenue: 3100000,
        confidence: 0.87
      }
    };
  };

  const generateTrendData = (days) => {
    return Array.from({ length: days }, (_, i) => ({
      date: new Date(Date.now() - (days - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      value: Math.floor(Math.random() * 100) + 50
    }));
  };

  const MetricCard = ({ title, value, growth, icon, color = 'primary' }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" fontWeight="bold">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </Typography>
            {growth !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                {growth > 0 ? (
                  <TrendingUp color="success" fontSize="small" />
                ) : (
                  <TrendingDown color="error" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={growth > 0 ? 'success.main' : 'error.main'}
                  ml={0.5}
                >
                  {Math.abs(growth)}%
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

  const InsightCard = ({ insight }) => (
    <Alert
      severity={insight.type}
      sx={{ mb: 2 }}
      action={
        <Chip
          label={insight.impact}
          size="small"
          color={insight.impact === 'high' ? 'error' : insight.impact === 'medium' ? 'warning' : 'info'}
        />
      }
    >
      <Typography variant="subtitle2" fontWeight="bold">
        {insight.title}
      </Typography>
      <Typography variant="body2" sx={{ mt: 0.5 }}>
        {insight.description}
      </Typography>
      <Typography variant="caption" sx={{ mt: 1, display: 'block', fontStyle: 'italic' }}>
        💡 {insight.recommendation}
      </Typography>
    </Alert>
  );

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );

  if (isLoading) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Advanced Analytics
        </Typography>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>
          Loading analytics data...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          📊 Advanced Analytics
        </Typography>
        <Box display="flex" gap={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="7d">Last 7 days</MenuItem>
              <MenuItem value="30d">Last 30 days</MenuItem>
              <MenuItem value="90d">Last 3 months</MenuItem>
              <MenuItem value="1y">Last year</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={refetch} disabled={isLoading} aria-label="Refresh analytics">
            <Refresh />
          </IconButton>
          <Button
            startIcon={<Download />}
            variant="outlined"
            onClick={() => downloadText(
              `millmitra-analytics-${timeRange}.json`,
              JSON.stringify(analyticsData || { note: 'No analytics snapshot yet' }, null, 2),
              'application/json'
            )}
          >
            Export
          </Button>
        </Box>
      </Box>

      {/* Offline Indicator */}
      {!isOnline && (
        <Alert severity="info" sx={{ mb: 2 }}>
          📡 Showing cached data - You're currently offline
        </Alert>
      )}

      {/* Key Metrics Overview */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Production"
            value={`${analyticsData?.overview?.totalProduction || 0} kg`}
            growth={analyticsData?.overview?.productionGrowth}
            icon={<Analytics fontSize="large" />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Quality Score"
            value={`${analyticsData?.overview?.qualityScore || 0}%`}
            growth={analyticsData?.overview?.qualityTrend}
            icon={<PieChart fontSize="large" />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Revenue"
            value={`₹${(analyticsData?.overview?.revenue || 0).toLocaleString()}`}
            growth={analyticsData?.overview?.revenueGrowth}
            icon={<TrendingUp fontSize="large" />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Efficiency"
            value={`${analyticsData?.overview?.efficiency || 0}%`}
            growth={analyticsData?.overview?.efficiencyTrend}
            icon={<BarChart fontSize="large" />}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Detailed Analytics Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="📈 Trends" />
            <Tab label="🔮 Predictions" />
            <Tab label="💡 Insights" />
            <Tab label="📊 Custom Reports" />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <Typography variant="h6" gutterBottom>
            Performance Trends
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Trend analysis will be displayed here with interactive charts
          </Typography>
          {/* Chart components would go here */}
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <Typography variant="h6" gutterBottom>
            AI Predictions
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" color="textSecondary">
                    Next Month Production
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {analyticsData?.predictions?.nextMonthProduction?.toLocaleString()} kg
                  </Typography>
                  <Typography variant="caption" color="success.main">
                    Confidence: {(analyticsData?.predictions?.confidence * 100).toFixed(0)}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            {/* Add more prediction cards */}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Typography variant="h6" gutterBottom>
            AI-Powered Insights
          </Typography>
          {analyticsData?.insights?.map((insight, index) => (
            <InsightCard key={index} insight={insight} />
          ))}
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Typography variant="h6" gutterBottom>
            Custom Reports
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Build custom reports and dashboards
          </Typography>
          {/* Custom report builder would go here */}
        </TabPanel>
      </Card>
    </Box>
  );
};

export default AdvancedAnalytics;
