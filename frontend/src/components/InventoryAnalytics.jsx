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
  // Mock data if none provided
  const mockData = {
    stockLevels: [
      { category: 'Processed Rice', current: 2500, max: 5000, reorder: 500 },
      { category: 'Raw Rice', current: 1800, max: 3000, reorder: 300 },
      { category: 'Broken Rice', current: 150, max: 1000, reorder: 200 },
      { category: 'Rice Bran', current: 800, max: 1500, reorder: 100 },
      { category: 'Packaging', current: 1200, max: 2000, reorder: 400 }
    ],
    stockMovement: [
      { date: '2024-01-15', inbound: 1200, outbound: 800, net: 400 },
      { date: '2024-01-16', inbound: 800, outbound: 1100, net: -300 },
      { date: '2024-01-17', inbound: 1500, outbound: 900, net: 600 },
      { date: '2024-01-18', inbound: 600, outbound: 1200, net: -600 },
      { date: '2024-01-19', inbound: 1800, outbound: 1000, net: 800 },
      { date: '2024-01-20', inbound: 1000, outbound: 1300, net: -300 },
      { date: '2024-01-21', inbound: 1400, outbound: 950, net: 450 }
    ],
    categoryDistribution: [
      { name: 'Processed Rice', value: 45, color: '#8884d8' },
      { name: 'Raw Rice', value: 25, color: '#82ca9d' },
      { name: 'Broken Rice', value: 10, color: '#ffc658' },
      { name: 'Rice Bran', value: 15, color: '#ff7300' },
      { name: 'Packaging', value: 5, color: '#00ff88' }
    ],
    turnoverRates: [
      { product: 'Basmati Rice', turnover: 8.5, status: 'excellent' },
      { product: 'IR64 Rice', turnover: 6.2, status: 'good' },
      { product: 'Broken Rice', turnover: 12.1, status: 'excellent' },
      { product: 'Rice Bran', turnover: 4.8, status: 'average' },
      { product: 'Premium Rice', turnover: 3.2, status: 'slow' }
    ]
  };

  const analyticsData = data || mockData;

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
      {/* Stock Levels Overview */}
      <Grid item xs={12} lg={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Stock Levels
            </Typography>
            <Box sx={{ height: 300 }}>
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
            <Box sx={{ height: 300 }}>
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
            <Box sx={{ height: 300 }}>
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
                    6,450
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Stock (kg)
                  </Typography>
                  <Chip label="+3.2%" color="success" size="small" sx={{ mt: 1 }} />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    1
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Low Stock Items
                  </Typography>
                  <Chip label="Needs attention" color="warning" size="small" sx={{ mt: 1 }} />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    7.2
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Turnover Rate
                  </Typography>
                  <Chip label="Good" color="success" size="small" sx={{ mt: 1 }} />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    78.5%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Warehouse Utilization
                  </Typography>
                  <Chip label="Optimal" color="info" size="small" sx={{ mt: 1 }} />
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default InventoryAnalytics;
