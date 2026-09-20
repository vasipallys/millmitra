import React, { useMemo, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  ShoppingCart as OrderIcon,
  AttachMoney as RevenueIcon,
  People as CustomerIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { salesAPI } from '../services/api';

const Sales = () => {
  const queryClient = useQueryClient();
  const [openDialog, setOpenDialog] = useState(false);
  const [formError, setFormError] = useState('');
  const [form, setForm] = useState({
    customer_id: '',
    order_date: new Date().toISOString().split('T')[0],
    description: 'Basmati Rice',
    quantity: '',
    unit_price: '',
  });

  const { data: ordersPayload, isLoading } = useQuery(
    'sales-orders',
    async () => (await salesAPI.getOrders({ per_page: 50 })).data,
    { refetchInterval: 60000 }
  );

  const { data: analyticsPayload } = useQuery(
    'sales-analytics',
    async () => (await salesAPI.getAnalytics()).data,
    { refetchInterval: 120000 }
  );

  const { data: customersPayload } = useQuery(
    'sales-customers',
    async () => (await salesAPI.getCustomers({ per_page: 100 })).data,
    { enabled: openDialog }
  );

  const orders = ordersPayload?.orders || [];
  const customers = customersPayload?.customers || [];
  const analytics = analyticsPayload?.analytics || {};

  const salesMetrics = {
    totalRevenue: analytics.total_revenue || 0,
    totalOrders: analytics.total_orders || orders.length,
    avgOrderValue: analytics.average_order_value || 0,
    recentOrders: analytics.recent_orders_count || 0,
  };

  const salesTrend = useMemo(() => {
    const buckets = {};
    orders.forEach((order) => {
      const raw = order.order_date || order.created_at;
      if (!raw) return;
      const month = new Date(raw).toLocaleString('en-IN', { month: 'short' });
      buckets[month] = buckets[month] || { month, revenue: 0, orders: 0 };
      buckets[month].revenue += order.total_amount || 0;
      buckets[month].orders += 1;
    });
    return Object.values(buckets);
  }, [orders]);

  const createOrderMutation = useMutation(
    async (payload) => (await salesAPI.createOrder(payload)).data,
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['sales-orders', 'sales-analytics']);
        setOpenDialog(false);
        setFormError('');
      },
      onError: (error) => {
        setFormError(error.response?.data?.message || 'Could not create order');
      }
    }
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'success';
      case 'processing': return 'warning';
      case 'confirmed': return 'info';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getPaymentStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'success';
      case 'pending': return 'warning';
      case 'overdue': return 'error';
      default: return 'default';
    }
  };

  const formatItems = (order) => {
    const items = order.order_items || order.items;
    if (Array.isArray(items) && items.length) {
      return items.map((item) => `${item.description || item.variety || 'Rice'} - ${item.quantity || 0}kg`).join(', ');
    }
    if (typeof items === 'string') return items;
    return order.total_quantity ? `${order.total_quantity} kg` : '—';
  };

  const handleSubmit = () => {
    if (!form.customer_id) {
      setFormError('Select a customer');
      return;
    }
    const quantity = parseFloat(form.quantity);
    const unitPrice = parseFloat(form.unit_price);
    if (!quantity || quantity <= 0 || !unitPrice || unitPrice <= 0) {
      setFormError('Quantity and unit price must be greater than 0');
      return;
    }
    createOrderMutation.mutate({
      customer_id: Number(form.customer_id),
      order_date: form.order_date,
      items: [{
        description: form.description,
        variety: form.description,
        quantity,
        unit_price: unitPrice
      }]
    });
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Sales Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setFormError('');
            setOpenDialog(true);
          }}
          size="large"
        >
          New Order
        </Button>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Revenue
                  </Typography>
                  <Typography variant="h5" component="div">
                    ₹{Number(salesMetrics.totalRevenue).toLocaleString()}
                  </Typography>
                </Box>
                <RevenueIcon color="primary" sx={{ fontSize: 40 }} />
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
                    Total Orders
                  </Typography>
                  <Typography variant="h5" component="div">
                    {salesMetrics.totalOrders}
                  </Typography>
                </Box>
                <OrderIcon color="secondary" sx={{ fontSize: 40 }} />
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
                    Avg Order Value
                  </Typography>
                  <Typography variant="h5" component="div">
                    ₹{Number(salesMetrics.avgOrderValue).toLocaleString()}
                  </Typography>
                </Box>
                <TrendingUpIcon color="success" sx={{ fontSize: 40 }} />
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
                    Recent Orders (30d)
                  </Typography>
                  <Typography variant="h5" component="div">
                    {salesMetrics.recentOrders}
                  </Typography>
                </Box>
                <CustomerIcon color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {salesTrend.length > 0 && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sales Trend
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={salesTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value, name) => [
                      name === 'revenue' ? `₹${value.toLocaleString()}` : value,
                      name === 'revenue' ? 'Revenue' : 'Orders'
                    ]} />
                    <Line type="monotone" dataKey="revenue" stroke="#2E7D32" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Order Volume
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={salesTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="orders" fill="#FF9800" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Orders
          </Typography>
          {isLoading && <LinearProgress />}
          {!isLoading && orders.length === 0 && (
            <Alert severity="info">No sales orders yet. Use New Order to create one.</Alert>
          )}
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Order ID</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Items</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Payment</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell>{order.order_number || order.id}</TableCell>
                    <TableCell>{order.customer_name || order.customer || `#${order.customer_id}`}</TableCell>
                    <TableCell>
                      {order.order_date ? new Date(order.order_date).toLocaleDateString() : '—'}
                    </TableCell>
                    <TableCell>{formatItems(order)}</TableCell>
                    <TableCell>₹{Number(order.total_amount || 0).toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={order.status || 'pending'}
                        color={getStatusColor(order.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={order.payment_status || 'pending'}
                        color={getPaymentStatusColor(order.payment_status)}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Order</DialogTitle>
        <DialogContent>
          {formError && <Alert severity="error" sx={{ mt: 2 }}>{formError}</Alert>}
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                label="Customer"
                value={form.customer_id}
                onChange={(e) => setForm({ ...form, customer_id: e.target.value })}
                required
              >
                {customers.map((customer) => (
                  <MenuItem key={customer.id} value={customer.id}>
                    {customer.name} {customer.phone ? `(${customer.phone})` : ''}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Order Date"
                type="date"
                value={form.order_date}
                onChange={(e) => setForm({ ...form, order_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Item / variety"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                    helperText="Match a product name/variety in Inventory so stock is deducted"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Quantity (kg)"
                type="number"
                value={form.quantity}
                onChange={(e) => setForm({ ...form, quantity: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Unit price (₹/kg)"
                type="number"
                value={form.unit_price}
                onChange={(e) => setForm({ ...form, unit_price: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={createOrderMutation.isLoading}
          >
            {createOrderMutation.isLoading ? 'Saving...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Sales;
