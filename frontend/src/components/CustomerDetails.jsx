import { useState } from 'react';
import {
  Card, CardContent, Typography, Box, Grid, Chip, Button,
  Tabs, Tab, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Avatar, Divider, IconButton,
  Tooltip, LinearProgress, Alert
} from '@mui/material';
import {
  Person, Business, Phone, Email, LocationOn, CreditCard,
  TrendingUp, Warning, Edit, Chat, ShoppingCart, Analytics,
  Star, Timeline, Feedback
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { customerService } from '../services/customerService';

const CustomerDetails = ({ customerId, onInteraction }) => {
  const [activeTab, setActiveTab] = useState(0);

  const { data: customer, isLoading } = useQuery(
    ['customer-details', customerId],
    () => customerService.getCustomerDetails(customerId),
    { enabled: !!customerId }
  );

  const { data: recommendations } = useQuery(
    ['customer-recommendations', customerId],
    () => customerService.getCustomerRecommendations(customerId),
    { enabled: !!customerId }
  );

  const { data: nextBestAction } = useQuery(
    ['next-best-action', customerId],
    () => customerService.getNextBestAction(customerId),
    { enabled: !!customerId }
  );

  if (isLoading) {
    return <LinearProgress />;
  }

  if (!customer) {
    return <Alert severity="error">Customer not found</Alert>;
  }

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

  const getChurnRiskColor = (score) => {
    if (score >= 0.7) return 'error';
    if (score >= 0.4) return 'warning';
    return 'success';
  };

  return (
    <Box>
      {/* Customer Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ width: 60, height: 60, mr: 2, bgcolor: 'primary.main' }}>
                  {customer.customer_type === 'business' ? <Business /> : <Person />}
                </Avatar>
                <Box flexGrow={1}>
                  <Typography variant="h5" fontWeight="bold">
                    {customer.name}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {customer.customer_code}
                  </Typography>
                  {customer.company_name && (
                    <Typography variant="body2" color="text.secondary">
                      {customer.company_name}
                    </Typography>
                  )}
                </Box>
                <Box>
                  <Tooltip title="Edit Customer">
                    <IconButton>
                      <Edit />
                    </IconButton>
                  </Tooltip>
                  <Button
                    variant="contained"
                    startIcon={<Chat />}
                    onClick={onInteraction}
                    sx={{ ml: 1 }}
                  >
                    Add Interaction
                  </Button>
                </Box>
              </Box>

              {/* Contact Information */}
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Phone sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography>{customer.phone || 'No phone'}</Typography>
                  </Box>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Email sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography>{customer.email || 'No email'}</Typography>
                  </Box>
                  <Box display="flex" alignItems="center">
                    <LocationOn sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography>
                      {customer.city && customer.state 
                        ? `${customer.city}, ${customer.state}` 
                        : 'No address'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box display="flex" gap={1} mb={2}>
                    <Chip
                      label={customer.customer_segment}
                      color={getSegmentColor(customer.customer_segment)}
                    />
                    <Chip
                      label={customer.status}
                      variant="outlined"
                    />
                    <Chip
                      label={customer.customer_type}
                      variant="outlined"
                    />
                  </Box>
                  {customer.gst_number && (
                    <Typography variant="body2" color="text.secondary">
                      GST: {customer.gst_number}
                    </Typography>
                  )}
                  <Typography variant="body2" color="text.secondary">
                    Payment Terms: {customer.payment_terms}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Credit Limit: {formatCurrency(customer.credit_limit)}
                  </Typography>
                </Grid>
              </Grid>
            </Grid>

            <Grid item xs={12} md={4}>
              {/* Key Metrics */}
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" color="primary.main">
                      {customer.metrics.total_orders}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Orders
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" color="success.main">
                      {formatCurrency(customer.metrics.total_spent).replace('₹', '₹')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Spent
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" color="info.main">
                      {formatCurrency(customer.metrics.avg_order_value).replace('₹', '₹')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Order Value
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" color="warning.main">
                      {formatCurrency(customer.lifetime_value).replace('₹', '₹')}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Lifetime Value
                    </Typography>
                  </Box>
                </Grid>
              </Grid>

              {/* Churn Risk */}
              <Box mt={3}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2" fontWeight="bold">
                    Churn Risk
                  </Typography>
                  <Typography 
                    variant="body2" 
                    fontWeight="bold"
                    color={`${getChurnRiskColor(customer.churn_risk_score)}.main`}
                  >
                    {Math.round(customer.churn_risk_score * 100)}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={customer.churn_risk_score * 100}
                  color={getChurnRiskColor(customer.churn_risk_score)}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* AI Recommendations */}
      {nextBestAction && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            AI Recommendation: {nextBestAction.action}
          </Typography>
          <Typography variant="body2">
            {nextBestAction.reason}
          </Typography>
        </Alert>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Recent Orders" />
          <Tab label="Interactions" />
          <Tab label="Analytics" />
          <Tab label="Communications" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <RecentOrdersTab orders={customer.recent_orders} />
      )}

      {activeTab === 1 && (
        <InteractionsTab interactions={customer.recent_interactions} />
      )}

      {activeTab === 2 && (
        <CustomerAnalyticsTab customerId={customerId} />
      )}

      {activeTab === 3 && (
        <CommunicationsTab customerId={customerId} />
      )}

      {/* AI Insights */}
      {recommendations && (
        <Card sx={{ mt: 3, bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              AI Insights & Recommendations
            </Typography>
            <Grid container spacing={2}>
              {recommendations.product_recommendations && (
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Recommended Products
                  </Typography>
                  {recommendations.product_recommendations.map((product, index) => (
                    <Chip
                      key={index}
                      label={product}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Grid>
              )}
              {recommendations.cross_sell_opportunities && (
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Cross-sell Opportunities
                  </Typography>
                  {recommendations.cross_sell_opportunities.map((opportunity, index) => (
                    <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                      • {opportunity}
                    </Typography>
                  ))}
                </Grid>
              )}
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

// Recent Orders Tab
const RecentOrdersTab = ({ orders }) => (
  <TableContainer component={Paper}>
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Order Number</TableCell>
          <TableCell>Date</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Amount</TableCell>
          <TableCell>Payment Status</TableCell>
          <TableCell>Actions</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {orders?.map((order) => (
          <TableRow key={order.id}>
            <TableCell>{order.order_number}</TableCell>
            <TableCell>{new Date(order.order_date).toLocaleDateString()}</TableCell>
            <TableCell>
              <Chip label={order.status} size="small" />
            </TableCell>
            <TableCell>
              {new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR'
              }).format(order.final_amount)}
            </TableCell>
            <TableCell>
              <Chip 
                label={order.payment_status} 
                size="small"
                color={order.payment_status === 'paid' ? 'success' : 'warning'}
              />
            </TableCell>
            <TableCell>
              <Button size="small">View</Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </TableContainer>
);

// Interactions Tab
const InteractionsTab = ({ interactions }) => (
  <TableContainer component={Paper}>
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>Type</TableCell>
          <TableCell>Subject</TableCell>
          <TableCell>Date</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Sentiment</TableCell>
          <TableCell>Actions</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {interactions?.map((interaction) => (
          <TableRow key={interaction.id}>
            <TableCell>
              <Chip label={interaction.interaction_type} size="small" />
            </TableCell>
            <TableCell>{interaction.subject}</TableCell>
            <TableCell>{new Date(interaction.created_at).toLocaleDateString()}</TableCell>
            <TableCell>
              <Chip label={interaction.status} size="small" />
            </TableCell>
            <TableCell>
              {interaction.sentiment_score && (
                <Chip
                  label={interaction.sentiment_score > 0 ? 'Positive' : 'Negative'}
                  size="small"
                  color={interaction.sentiment_score > 0 ? 'success' : 'error'}
                />
              )}
            </TableCell>
            <TableCell>
              <Button size="small">View</Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </TableContainer>
);

// Customer Analytics Tab
const CustomerAnalyticsTab = ({ customerId }) => {
  const { data: analytics } = useQuery(
    ['customer-analytics-detail', customerId],
    () => customerService.getCustomerAnalyticsDetail(customerId),
    { enabled: !!customerId }
  );

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Order Trends
            </Typography>
            {/* Add chart component here */}
            <Typography variant="body2" color="text.secondary">
              Order trends chart will be displayed here
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Purchase Patterns
            </Typography>
            {/* Add chart component here */}
            <Typography variant="body2" color="text.secondary">
              Purchase patterns analysis will be displayed here
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

// Communications Tab
const CommunicationsTab = ({ customerId }) => {
  const { data: communications } = useQuery(
    ['customer-communications', customerId],
    () => customerService.getCustomerCommunications(customerId),
    { enabled: !!customerId }
  );

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Type</TableCell>
            <TableCell>Subject</TableCell>
            <TableCell>Sent Date</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Response Rate</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {communications?.communications?.map((comm) => (
            <TableRow key={comm.id}>
              <TableCell>
                <Chip label={comm.communication_type} size="small" />
              </TableCell>
              <TableCell>{comm.subject}</TableCell>
              <TableCell>{new Date(comm.sent_at).toLocaleDateString()}</TableCell>
              <TableCell>
                <Chip label={comm.status} size="small" />
              </TableCell>
              <TableCell>
                {comm.predicted_response_rate && 
                  `${Math.round(comm.predicted_response_rate * 100)}%`
                }
              </TableCell>
              <TableCell>
                <Button size="small">View</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default CustomerDetails;