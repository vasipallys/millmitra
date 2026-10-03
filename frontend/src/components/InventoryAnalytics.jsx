import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts';

const InventoryAnalytics = ({ data = null }) => {
  const liveOverview = data && (
    typeof data.total_valuation === 'number' ||
    typeof data.paddy_count === 'number' ||
    typeof data.low_stock_items === 'number' ||
    Array.isArray(data.stockLevels)
  );
  const analyticsData = liveOverview
    ? {
        stockLevels: data.stockLevels || [
          { category: 'Paddy lots', current: data.paddy_count || 0, max: Math.max(data.paddy_count || 0, 1), reorder: 0 },
          { category: 'Product lots', current: data.product_count || 0, max: Math.max(data.product_count || 0, 1), reorder: 0 },
          { category: 'Low stock items', current: data.low_stock_items || 0, max: Math.max(data.low_stock_items || 0, 1), reorder: 0 },
        ],
        stockMovement: data.stockMovement || [],
        categoryDistribution: data.categoryDistribution || [
          { name: 'Paddy value', value: Number(data.paddy_valuation || 0), color: '#82ca9d' },
          { name: 'Product value', value: Number(data.product_valuation || 0), color: '#8884d8' },
        ].filter((row) => row.value > 0),
        turnoverRates: data.turnoverRates || [],
      }
    : { stockLevels: [], stockMovement: [], categoryDistribution: [], turnoverRates: [] };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const getStockStatus = (current, reorder, max) => {
    const percentage = (current / max) * 100;
    if (current <= reorder) return { status: 'low', color: 'error' };
    if (percentage > 90) return { status: 'high', color: 'warning' };
    return { status: 'normal', color: 'success' };
  };

  const getTurnoverStatus = (rate) => {
    if (rate >= 8) return { label: 'Excellent', color: 'success' };
    if (rate >= 6) return { label: 'Good', color: 'info' };
    if (rate >= 4) return { label: 'Average', color: 'warning' };
    return { label: 'Slow', color: 'error' };
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            bgcolor: 'background.paper',
            p: 2,
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            boxShadow: 2
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            {formatDate(label)}
          </Typography>
          {payload.map((entry, index) => (
            <Typography
              key={index}
              variant="body2"
              sx={{ color: entry.color }}
            >
              {entry.name}: {entry.value} kg
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  return (
    <Grid container spacing={3}>
      {liveOverview && (
        <>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Total valuation</Typography>
                <Typography variant="h5">
                  ₹{Number(data.total_valuation || 0).toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Paddy lots</Typography>
                <Typography variant="h5">{data.paddy_count || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Product lots</Typography>
                <Typography variant="h5">{data.product_count || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Low stock items</Typography>
                <Typography variant="h5">{data.low_stock_items || 0}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </>
      )}
      <>
      {/* Stock Levels Overview */}
      <Grid item xs={12} lg={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Stock Levels
            </Typography>
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {analyticsData.stockLevels.length === 0 ? (
                <Typography color="text.secondary">No records yet</Typography>
              ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analyticsData.stockLevels}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="current" fill="#2196F3" name="Current Stock" />
                  <Bar dataKey="reorder" fill="#FF9800" name="Reorder Level" />
                  <Bar dataKey="max" fill="#E0E0E0" name="Max Capacity" />
                </BarChart>
              </ResponsiveContainer>
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Category Distribution */}
      <Grid item xs={12} lg={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Inventory Distribution
            </Typography>
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {analyticsData.categoryDistribution.length === 0 ? (
                <Typography color="text.secondary">No records yet</Typography>
              ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analyticsData.categoryDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {analyticsData.categoryDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Stock Movement Trend */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Stock Movement Trend
            </Typography>
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {analyticsData.stockMovement.length === 0 ? (
                <Typography color="text.secondary">No records yet</Typography>
              ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analyticsData.stockMovement}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                  />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="inbound"
                    stroke="#4CAF50"
                    strokeWidth={2}
                    name="Inbound"
                  />
                  <Line
                    type="monotone"
                    dataKey="outbound"
                    stroke="#F44336"
                    strokeWidth={2}
                    name="Outbound"
                  />
                  <Line
                    type="monotone"
                    dataKey="net"
                    stroke="#2196F3"
                    strokeWidth={3}
                    name="Net Movement"
                  />
                </LineChart>
              </ResponsiveContainer>
              )}
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Stock Status Cards */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Stock Status by Category
            </Typography>
            {analyticsData.stockLevels.length === 0 && (
              <Typography color="text.secondary">No records yet</Typography>
            )}
            {analyticsData.stockLevels.map((item, index) => {
              const status = getStockStatus(item.current, item.reorder, item.max);
              const percentage = (item.current / item.max) * 100;
              
              return (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">
                      {item.category}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" fontWeight="medium">
                        {item.current} / {item.max} kg
                      </Typography>
                      <Chip 
                        label={status.status.toUpperCase()} 
                        color={status.color}
                        size="small"
                      />
                    </Box>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={percentage} 
                    sx={{ height: 8, borderRadius: 4 }}
                    color={status.color}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                    {percentage.toFixed(1)}% of capacity | Reorder at {item.reorder} kg
                  </Typography>
                </Box>
              );
            })}
          </CardContent>
        </Card>
      </Grid>

      {/* Turnover Rates */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Inventory Turnover Rates
            </Typography>
            {analyticsData.turnoverRates.length === 0 && (
              <Typography color="text.secondary">No records yet</Typography>
            )}
            {analyticsData.turnoverRates.map((item, index) => {
              const status = getTurnoverStatus(item.turnover);
              
              return (
                <Box key={index} sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  py: 1,
                  borderBottom: index < analyticsData.turnoverRates.length - 1 ? 1 : 0,
                  borderColor: 'divider'
                }}>
                  <Typography variant="body2">
                    {item.product}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" fontWeight="medium">
                      {item.turnover}x/year
                    </Typography>
                    <Chip 
                      label={status.label} 
                      color={status.color}
                      size="small"
                    />
                  </Box>
                </Box>
              );
            })}
            
            <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Turnover Rate = Annual Sales / Average Inventory
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Key Metrics Summary */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Inventory Key Metrics
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary.main">
                    {Number(data?.paddy_count || 0) + Number(data?.product_count || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Paddy + product lots
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {Number(data?.low_stock_items || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Low Stock Items
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    ₹{Number(data?.total_valuation || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total valuation
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    ₹{Number(data?.paddy_valuation || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Paddy valuation
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
      </>
    </Grid>
  );
};

export default InventoryAnalytics;
