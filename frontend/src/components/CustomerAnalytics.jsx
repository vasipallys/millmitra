import { useState } from 'react';
import {
  Card, CardContent, Typography, Grid, Box, Chip,
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, LinearProgress,
  Alert, Button, FormControl, InputLabel, Select,
  MenuItem, Tabs, Tab, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  TrendingUp, TrendingDown, People, MonetizationOn,
  Warning, Star, Timeline, PieChart
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { customerService } from '../services/customerService';

const CustomerAnalytics = ({ analytics }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [timeRange, setTimeRange] = useState('30');

  const { data: churnPrediction } = useQuery(
    ['churn-prediction', timeRange],
    () => customerService.getChurnPrediction(),
    { refetchInterval: 300000 } // Refresh every 5 minutes
  );

  const { data: ltvAnalysis } = useQuery(
    ['ltv-analysis', timeRange],
    () => customerService.getLifetimeValueAnalysis(),
    { refetchInterval: 300000 }
  );

  const { data: segments } = useQuery(
    ['customer-segments', timeRange],
    () => customerService.getCustomerSegments(),
    { refetchInterval: 300000 }
  );

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const getSegmentColor = (segment) => {
    const colors = {
      premium: 'success',
      regular: 'primary',
      budget: 'warning',
      inactive: 'default'
    };
    return colors[segment] || 'default';
  };

  const getTrendIcon = (trend) => {
    return trend === 'up' ? <TrendingUp color="success" /> : <TrendingDown color="error" />;
  };

  return (
    <Box>
      {/* Time Range Selector */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Customer Analytics</Typography>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <MenuItem value="7">Last 7 days</MenuItem>
            <MenuItem value="30">Last 30 days</MenuItem>
            <MenuItem value="90">Last 3 months</MenuItem>
            <MenuItem value="365">Last year</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <People sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">Total Customers</Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {analytics?.total_customers || 0}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {getTrendIcon(analytics?.customer_growth_trend)}
                <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                  {analytics?.customer_growth_rate || 0}% vs last period
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <MonetizationOn sx={{ mr: 1, color: 'success.main' }} />
                <Typography variant="h6">Total Revenue</Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {formatCurrency(analytics?.total_revenue || 0)}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {getTrendIcon(analytics?.revenue_trend)}
                <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                  {analytics?.revenue_growth_rate || 0}% vs last period
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Star sx={{ mr: 1, color: 'warning.main' }} />
                <Typography variant="h6">Avg LTV</Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {formatCurrency(ltvAnalysis?.average_ltv || 0)}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {getTrendIcon(ltvAnalysis?.ltv_trends?.growth_rate > 0 ? 'up' : 'down')}
                <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                  {Math.abs(ltvAnalysis?.ltv_trends?.growth_rate || 0)}% vs last period
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Warning sx={{ mr: 1, color: 'error.main' }} />
                <Typography variant="h6">Churn Risk</Typography>
              </Box>
              <Typography variant="h4" fontWeight="bold">
                {churnPrediction?.high_risk_customers?.length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                customers at high risk
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Segments" />
          <Tab label="Churn Analysis" />
          <Tab label="Lifetime Value" />
          <Tab label="AI Insights" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <SegmentAnalysis segments={segments} />
      )}

      {activeTab === 1 && (
        <ChurnAnalysis churnData={churnPrediction} />
      )}

      {activeTab === 2 && (
        <LifetimeValueAnalysis ltvData={ltvAnalysis} />
      )}

      {activeTab === 3 && (
        <AIInsights analytics={analytics} />
      )}
    </Box>
  );
};

// Segment Analysis Component
const SegmentAnalysis = ({ segments }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const getSegmentColor = (segment) => {
    const colors = {
      premium: 'success',
      regular: 'primary',
      budget: 'warning',
      inactive: 'default'
    };
    return colors[segment] || 'default';
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Customer Segments
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Segment</TableCell>
                    <TableCell>Customers</TableCell>
                    <TableCell>Avg LTV</TableCell>
                    <TableCell>Avg Order Value</TableCell>
                    <TableCell>Retention Rate</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {segments?.segments?.map((segment) => (
                    <TableRow key={segment.name}>
                      <TableCell>
                        <Chip
                          label={segment.name}
                          color={getSegmentColor(segment.name)}
                        />
                      </TableCell>
                      <TableCell>{segment.customer_count}</TableCell>
                      <TableCell>{formatCurrency(segment.avg_ltv)}</TableCell>
                      <TableCell>{formatCurrency(segment.avg_order_value)}</TableCell>
                      <TableCell>{Math.round(segment.retention_rate * 100)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Segment Performance
            </Typography>
            {segments?.ai_insights && (
              <Box>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">
                    Best Performing: {segments.ai_insights.performance_insights?.best_performing}
                  </Typography>
                </Alert>
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">
                    Growth Potential: {segments.ai_insights.performance_insights?.growth_potential}
                  </Typography>
                </Alert>
                <Typography variant="subtitle2" gutterBottom>
                  Optimization Suggestions:
                </Typography>
                {segments.ai_insights.optimization_suggestions?.map((suggestion, index) => (
                  <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                    • {suggestion}
                  </Typography>
                ))}
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Churn Analysis Component
const ChurnAnalysis = ({ churnData }) => {
  const [actionCustomer, setActionCustomer] = useState(null);
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              High Risk Customers
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Customer</TableCell>
                    <TableCell>Churn Probability</TableCell>
                    <TableCell>Last Order</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {churnData?.high_risk_customers?.map((customer) => (
                    <TableRow key={customer.customer_id}>
                      <TableCell>{customer.name}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <LinearProgress
                            variant="determinate"
                            value={customer.churn_probability * 100}
                            color="error"
                            sx={{ width: 100, mr: 1 }}
                          />
                          <Typography variant="body2">
                            {Math.round(customer.churn_probability * 100)}%
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        {customer.last_order_date ? 
                          new Date(customer.last_order_date).toLocaleDateString() : 
                          'Never'
                        }
                      </TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined" onClick={() => setActionCustomer(customer)}>
                          Take Action
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
        <Dialog open={Boolean(actionCustomer)} onClose={() => setActionCustomer(null)} maxWidth="sm" fullWidth>
          <DialogTitle>{actionCustomer?.name || 'Customer'}</DialogTitle>
          <DialogContent>
            <Typography sx={{ mt: 1 }}>
              Open Customers → that buyer → Add Interaction, or create a follow-up order on Sales. This screen does not auto-call or send mail.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setActionCustomer(null)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Grid>

      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Churn Insights
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Overall Churn Rate
              </Typography>
              <Typography variant="h4" color="error.main">
                {Math.round((churnData?.overall_churn_rate || 0) * 100)}%
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Trend
              </Typography>
              <Chip
                label={churnData?.trend || 'stable'}
                color={churnData?.trend === 'improving' ? 'success' : 'warning'}
                size="small"
              />
            </Box>
            <Typography variant="subtitle2" gutterBottom>
              Recommended Actions:
            </Typography>
            {churnData?.high_risk_customers?.[0]?.recommended_actions?.map((action, index) => (
              <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                • {action}
              </Typography>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Lifetime Value Analysis Component
const LifetimeValueAnalysis = ({ ltvData }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              LTV by Segment
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Segment</TableCell>
                    <TableCell>Average LTV</TableCell>
                    <TableCell>Growth</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(ltvData?.ltv_by_segment || {}).map(([segment, ltv]) => (
                    <TableRow key={segment}>
                      <TableCell>
                        <Chip label={segment} size="small" />
                      </TableCell>
                      <TableCell>{formatCurrency(ltv)}</TableCell>
                      <TableCell>
                        <TrendingUp color="success" />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              LTV Optimization
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Growth Rate
              </Typography>
              <Typography variant="h4" color="success.main">
                {Math.round((ltvData?.ltv_trends?.growth_rate || 0) * 100)}%
              </Typography>
            </Box>
            <Typography variant="subtitle2" gutterBottom>
              Top Factors:
            </Typography>
            {ltvData?.ltv_trends?.top_factors?.map((factor, index) => (
              <Chip
                key={index}
                label={factor.replace('_', ' ')}
                size="small"
                sx={{ mr: 1, mb: 1 }}
              />
            ))}
            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Recommendations:
            </Typography>
            {ltvData?.recommendations?.map((rec, index) => (
              <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                • {rec}
              </Typography>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// AI Insights Component
const AIInsights = ({ analytics }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              AI Recommendations
            </Typography>
            {analytics?.ai_insights?.recommendations?.map((rec, index) => (
              <Alert key={index} severity="info" sx={{ mb: 2 }}>
                {rec}
              </Alert>
            ))}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Predictive Insights
            </Typography>
            {analytics?.ai_insights?.predictions?.map((prediction, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Typography variant="subtitle2">
                  {prediction.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {prediction.description}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={prediction.confidence * 100}
                  sx={{ mt: 1 }}
                />
                <Typography variant="caption">
                  Confidence: {Math.round(prediction.confidence * 100)}%
                </Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Market Trends & Opportunities
            </Typography>
            <Grid container spacing={2}>
              {analytics?.ai_insights?.market_trends?.map((trend, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Alert severity="success">
                    <Typography variant="subtitle2">
                      {trend.category}
                    </Typography>
                    <Typography variant="body2">
                      {trend.insight}
                    </Typography>
                  </Alert>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default CustomerAnalytics;