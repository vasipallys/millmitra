import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, LinearProgress, Alert
} from '@mui/material';
import {
  TrendingUp, TrendingDown, People, ShoppingCart,
  AttachMoney, Assessment
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { salesAPI } from '../../services/api';

const SalesDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await salesAPI.getDashboard(timeRange);
      setDashboardData(response.data.dashboard);
      setAiInsights(response.data.ai_insights);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ title, value, growth, icon, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
            {growth !== undefined && (
              <Box display="flex" alignItems="center" mt={1}>
                {growth >= 0 ? (
                  <TrendingUp color="success" fontSize="small" />
                ) : (
                  <TrendingDown color="error" fontSize="small" />
                )}
                <Typography
                  variant="body2"
                  color={growth >= 0 ? 'success.main' : 'error.main'}
                  ml={0.5}
                >
                  {Math.abs(growth).toFixed(1)}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box color={`${color}.main`}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return <LinearProgress />;
  }

  if (!dashboardData) {
    return <Alert severity="error">Failed to load dashboard data</Alert>;
  }

  const pipelineColors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300'];

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Sales Dashboard
      </Typography>

      {/* AI Insights */}
      {aiInsights && (
        <Card sx={{ mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              🤖 AI Insights
            </Typography>
            {aiInsights.key_insights?.map((insight, index) => (
              <Typography key={index} variant="body2" sx={{ mb: 1 }}>
                • {insight}
              </Typography>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Revenue"
            value={`₹${(dashboardData.current_revenue / 100000).toFixed(1)}L`}
            growth={dashboardData.revenue_growth}
            icon={<AttachMoney fontSize="large" />}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Orders"
            value={dashboardData.current_orders}
            growth={dashboardData.order_growth}
            icon={<ShoppingCart fontSize="large" />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Order Value"
            value={`₹${(dashboardData.average_order_value / 1000).toFixed(0)}K`}
            icon={<Assessment fontSize="large" />}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Customers"
            value={dashboardData.top_customers?.length || 0}
            icon={<People fontSize="large" />}
            color="secondary"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Sales Pipeline */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sales Pipeline
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={dashboardData.pipeline}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ status, value }) => `${status}: ₹${(value/100000).toFixed(1)}L`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {dashboardData.pipeline.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={pipelineColors[index % pipelineColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `₹${(value/100000).toFixed(1)}L`} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Customers */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Customers
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Customer</TableCell>
                      <TableCell align="right">Value</TableCell>
                      <TableCell align="right">Orders</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {dashboardData.top_customers?.map((customer, index) => (
                      <TableRow key={index}>
                        <TableCell>{customer.name}</TableCell>
                        <TableCell align="right">
                          ₹{(customer.total_value / 100000).toFixed(1)}L
                        </TableCell>
                        <TableCell align="right">{customer.order_count}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* AI Recommendations */}
        {aiInsights?.recommendations && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  AI Recommendations
                </Typography>
                <Grid container spacing={2}>
                  {aiInsights.recommendations.map((recommendation, index) => (
                    <Grid item xs={12} md={6} key={index}>
                      <Chip
                        label={recommendation}
                        variant="outlined"
                        color="primary"
                        sx={{ width: '100%', justifyContent: 'flex-start' }}
                      />
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default SalesDashboard;