import { useState } from 'react';
import {
  Card, CardContent, Typography, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow,
  Paper, Chip, Button, Box, TextField, FormControl,
  InputLabel, Select, MenuItem, IconButton, Tooltip,
  Dialog, DialogTitle, DialogContent, DialogActions, LinearProgress,
  Grid, Alert
} from '@mui/material';
import {
  Visibility, GetApp, LocalShipping, Payment,
  TrendingUp, Analytics, Psychology
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { customerService } from '../services/customerService';
import { downloadText, toCsv } from '../utils/downloadFile';

const OrderHistory = ({ customerId, showAllOrders = false }) => {
  const [filters, setFilters] = useState({
    status: 'all',
    payment_status: 'all',
    date_range: '30',
    search: ''
  });
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [orderDetailsOpen, setOrderDetailsOpen] = useState(false);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);
  const [actionNote, setActionNote] = useState(null);

  const { data: orders, isLoading } = useQuery(
    ['orders', customerId, filters],
    () => customerService.getOrders({
      customer_id: showAllOrders ? undefined : customerId,
      ...filters
    }),
    {
      refetchInterval: 30000 // Refresh every 30 seconds
    }
  );

  const { data: orderDetails } = useQuery(
    ['order-details', selectedOrder?.id],
    () => customerService.getOrderDetails(selectedOrder.id),
    { enabled: !!selectedOrder }
  );

  const handleFilterChange = (field) => (e) => {
    setFilters(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const handleViewOrder = (order) => {
    setSelectedOrder(order);
    setOrderDetailsOpen(true);
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      confirmed: 'info',
      processing: 'primary',
      shipped: 'secondary',
      delivered: 'success',
      cancelled: 'error'
    };
    return colors[status] || 'default';
  };

  const getPaymentStatusColor = (status) => {
    const colors = {
      pending: 'warning',
      paid: 'success',
      overdue: 'error',
      partial: 'info'
    };
    return colors[status] || 'default';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  if (isLoading) {
    return <LinearProgress />;
  }

  return (
    <Box>
      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Order Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Search Orders"
                value={filters.search}
                onChange={handleFilterChange('search')}
                placeholder="Order number, product..."
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={handleFilterChange('status')}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="confirmed">Confirmed</MenuItem>
                  <MenuItem value="processing">Processing</MenuItem>
                  <MenuItem value="shipped">Shipped</MenuItem>
                  <MenuItem value="delivered">Delivered</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Payment Status</InputLabel>
                <Select
                  value={filters.payment_status}
                  onChange={handleFilterChange('payment_status')}
                >
                  <MenuItem value="all">All Payment</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="paid">Paid</MenuItem>
                  <MenuItem value="overdue">Overdue</MenuItem>
                  <MenuItem value="partial">Partial</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Date Range</InputLabel>
                <Select
                  value={filters.date_range}
                  onChange={handleFilterChange('date_range')}
                >
                  <MenuItem value="7">Last 7 days</MenuItem>
                  <MenuItem value="30">Last 30 days</MenuItem>
                  <MenuItem value="90">Last 3 months</MenuItem>
                  <MenuItem value="365">Last year</MenuItem>
                  <MenuItem value="all">All time</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', gap: 1, height: '100%', alignItems: 'center' }}>
                <Button
                  variant="outlined"
                  startIcon={<GetApp />}
                  onClick={() => {
                    const rows = (orders?.orders || []).map((order) => ({
                      order_number: order.order_number || order.id,
                      date: order.order_date || '',
                      amount: order.final_amount || order.total_amount || 0,
                      status: order.status || '',
                    }));
                    downloadText('customer-orders.csv', toCsv(rows) || 'order_number,date,amount,status', 'text/csv');
                  }}
                >
                  Export
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Analytics />}
                  onClick={() => {
                    setAnalyticsOpen(true);
                  }}
                >
                  Analytics
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* AI Insights */}
      {orders?.ai_insights && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            AI Order Insights
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {orders.ai_insights.patterns?.map((pattern, index) => (
              <Chip key={index} label={pattern} size="small" />
            ))}
          </Box>
          {orders.ai_insights.recommendations && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Recommendation: {orders.ai_insights.recommendations[0]}
            </Typography>
          )}
        </Alert>
      )}

      {/* Orders Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order Number</TableCell>
              <TableCell>Date</TableCell>
              {showAllOrders && <TableCell>Customer</TableCell>}
              <TableCell>Products</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Payment</TableCell>
              <TableCell>Delivery</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders?.orders?.map((order) => (
              <TableRow key={order.id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {order.order_number}
                  </Typography>
                  {order.ai_risk_score > 0.7 && (
                    <Chip
                      label="High Risk"
                      color="error"
                      size="small"
                      sx={{ mt: 0.5 }}
                    />
                  )}
                </TableCell>
                <TableCell>
                  {new Date(order.order_date).toLocaleDateString()}
                </TableCell>
                {showAllOrders && (
                  <TableCell>
                    <Typography variant="body2">
                      {order.customer_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {order.customer_code}
                    </Typography>
                  </TableCell>
                )}
                <TableCell>
                  <Typography variant="body2">
                    {order.items?.length || 0} items
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {order.primary_product}
                  </Typography>
                </TableCell>
                <TableCell>
                  {order.total_quantity} kg
                </TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="bold">
                    {formatCurrency(order.final_amount)}
                  </Typography>
                  {order.discount_amount > 0 && (
                    <Typography variant="caption" color="success.main">
                      -{formatCurrency(order.discount_amount)}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={order.status}
                    color={getStatusColor(order.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={order.payment_status}
                    color={getPaymentStatusColor(order.payment_status)}
                    size="small"
                  />
                  {order.payment_due_date && order.payment_status !== 'paid' && (
                    <Typography variant="caption" display="block" color="text.secondary">
                      Due: {new Date(order.payment_due_date).toLocaleDateString()}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  {order.estimated_delivery_date && (
                    <Typography variant="body2">
                      {new Date(order.estimated_delivery_date).toLocaleDateString()}
                    </Typography>
                  )}
                  {order.tracking_number && (
                    <Typography variant="caption" color="primary.main">
                      Track: {order.tracking_number}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        aria-label="View order details"
                        onClick={() => handleViewOrder(order)}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    {order.tracking_number && (
                      <Tooltip title="Track Shipment">
                        <IconButton
                          size="small"
                          aria-label="Track shipment"
                          onClick={() => setActionNote({
                            title: 'Track shipment',
                            text: `Tracking ${order.tracking_number} is not connected to a live carrier. Confirm delivery with the mill office.`,
                          })}
                        >
                          <LocalShipping />
                        </IconButton>
                      </Tooltip>
                    )}
                    {order.payment_status !== 'paid' && (
                      <Tooltip title="Payment">
                        <IconButton
                          size="small"
                          aria-label="Record payment"
                          onClick={() => setActionNote({
                            title: 'Payment',
                            text: `Record money for order ${order.order_number || order.id} on Finance → Record Payment.`,
                          })}
                        >
                          <Payment />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Order Details Dialog */}
      <Dialog
        open={orderDetailsOpen}
        onClose={() => setOrderDetailsOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Order Details - {selectedOrder?.order_number}
        </DialogTitle>
        <DialogContent>
          {orderDetails ? (
            <OrderDetailsContent order={orderDetails} />
          ) : (
            <LinearProgress />
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={analyticsOpen} onClose={() => setAnalyticsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Order analytics</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>
            {orders?.orders?.length || 0} orders in this filter. Live sales totals are on Sales and Finance.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalyticsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(actionNote)} onClose={() => setActionNote(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{actionNote?.title}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>{actionNote?.text}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setActionNote(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Summary Stats */}
      {orders?.summary && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Order Summary
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary.main">
                    {orders.summary.total_orders}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Orders
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {formatCurrency(orders.summary.total_value)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Value
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="info.main">
                    {formatCurrency(orders.summary.avg_order_value)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Order Value
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {orders.summary.pending_orders}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending Orders
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

// Order Details Component
const OrderDetailsContent = ({ order }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  return (
    <Box>
      {/* Order Header */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Order Information
          </Typography>
          <Typography variant="body2">
            <strong>Order Number:</strong> {order.order_number}
          </Typography>
          <Typography variant="body2">
            <strong>Date:</strong> {new Date(order.order_date).toLocaleDateString()}
          </Typography>
          <Typography variant="body2">
            <strong>Customer:</strong> {order.customer_name}
          </Typography>
          <Typography variant="body2">
            <strong>Status:</strong> <Chip label={order.status} size="small" />
          </Typography>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Payment & Delivery
          </Typography>
          <Typography variant="body2">
            <strong>Payment Status:</strong> <Chip label={order.payment_status} size="small" />
          </Typography>
          <Typography variant="body2">
            <strong>Payment Terms:</strong> {order.payment_terms}
          </Typography>
          {order.estimated_delivery_date && (
            <Typography variant="body2">
              <strong>Est. Delivery:</strong> {new Date(order.estimated_delivery_date).toLocaleDateString()}
            </Typography>
          )}
          {order.tracking_number && (
            <Typography variant="body2">
              <strong>Tracking:</strong> {order.tracking_number}
            </Typography>
          )}
        </Grid>
      </Grid>

      {/* AI Predictions */}
      {order.delivery_prediction && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            AI Delivery Prediction
          </Typography>
          <Typography variant="body2">
            Estimated delivery: {new Date(order.delivery_prediction.estimated_delivery_date).toLocaleDateString()}
          </Typography>
          <Typography variant="body2">
            Confidence: {Math.round(order.delivery_prediction.confidence * 100)}%
          </Typography>
        </Alert>
      )}

      {/* Order Items */}
      <Typography variant="h6" gutterBottom>
        Order Items
      </Typography>
      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product</TableCell>
              <TableCell>Variety</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Unit Price</TableCell>
              <TableCell>Total</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {order.items?.map((item, index) => (
              <TableRow key={index}>
                <TableCell>{item.product_name}</TableCell>
                <TableCell>{item.variety}</TableCell>
                <TableCell>{item.quantity} kg</TableCell>
                <TableCell>{formatCurrency(item.unit_price)}</TableCell>
                <TableCell>{formatCurrency(item.total_amount)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Order Totals */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Box sx={{ minWidth: 300 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography>Subtotal:</Typography>
            <Typography>{formatCurrency(order.subtotal_amount)}</Typography>
          </Box>
          {order.discount_amount > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="success.main">Discount:</Typography>
              <Typography color="success.main">-{formatCurrency(order.discount_amount)}</Typography>
            </Box>
          )}
          {order.tax_amount > 0 && (
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography>Tax:</Typography>
              <Typography>{formatCurrency(order.tax_amount)}</Typography>
            </Box>
          )}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', borderTop: 1, borderColor: 'divider', pt: 1 }}>
            <Typography variant="h6">Total:</Typography>
            <Typography variant="h6">{formatCurrency(order.final_amount)}</Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default OrderHistory;