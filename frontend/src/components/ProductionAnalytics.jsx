import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

const ProductionAnalytics = ({ data = null }) => {
  // Mock data if none provided
  const mockData = {
    dailyProduction: [
      { date: '2024-01-15', production: 4200, efficiency: 85, target: 4000 },
      { date: '2024-01-16', production: 4500, efficiency: 88, target: 4000 },
      { date: '2024-01-17', production: 3800, efficiency: 82, target: 4000 },
      { date: '2024-01-18', production: 4100, efficiency: 87, target: 4000 },
      { date: '2024-01-19', production: 4300, efficiency: 89, target: 4000 },
      { date: '2024-01-20', production: 4600, efficiency: 91, target: 4000 },
      { date: '2024-01-21', production: 4000, efficiency: 86, target: 4000 }
    ],
    productionByType: [
      { name: 'Basmati Rice', value: 45, color: '#8884d8' },
      { name: 'IR64 Rice', value: 30, color: '#82ca9d' },
      { name: 'Broken Rice', value: 15, color: '#ffc658' },
      { name: 'Premium Rice', value: 10, color: '#ff7300' }
    ],
    qualityTrends: [
      { date: '2024-01-15', gradeA: 65, gradeB: 25, gradeC: 10 },
      { date: '2024-01-16', gradeA: 70, gradeB: 22, gradeC: 8 },
      { date: '2024-01-17', gradeA: 68, gradeB: 24, gradeC: 8 },
      { date: '2024-01-18', gradeA: 72, gradeB: 20, gradeC: 8 },
      { date: '2024-01-19', gradeA: 75, gradeB: 18, gradeC: 7 },
      { date: '2024-01-20', gradeA: 78, gradeB: 17, gradeC: 5 },
      { date: '2024-01-21', gradeA: 76, gradeB: 19, gradeC: 5 }
    ]
  };

  const analyticsData = data || mockData;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
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
              {entry.name}: {entry.value}{entry.name.includes('efficiency') ? '%' : ' kg'}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  return (
    <Grid container spacing={3}>
      {/* Daily Production Trend */}
      <Grid item xs={12} lg={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Daily Production Trend
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analyticsData.dailyProduction}>
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
                    dataKey="production"
                    stroke="#2196F3"
                    strokeWidth={2}
                    name="Production (kg)"
                  />
                  <Line
                    type="monotone"
                    dataKey="target"
                    stroke="#FF9800"
                    strokeDasharray="5 5"
                    name="Target (kg)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Production by Type */}
      <Grid item xs={12} lg={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Production by Type
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analyticsData.productionByType}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {analyticsData.productionByType.map((entry, index) => (
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

      {/* Efficiency Trend */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Production Efficiency
            </Typography>
            <Box sx={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analyticsData.dailyProduction}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                  />
                  <YAxis domain={[70, 100]} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar 
                    dataKey="efficiency" 
                    fill="#4CAF50"
                    name="Efficiency (%)"
                  />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Quality Distribution */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quality Grade Trends
            </Typography>
            <Box sx={{ height: 250 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analyticsData.qualityTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                  />
                  <YAxis />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend />
                  <Bar dataKey="gradeA" stackId="a" fill="#4CAF50" name="Grade A %" />
                  <Bar dataKey="gradeB" stackId="a" fill="#FF9800" name="Grade B %" />
                  <Bar dataKey="gradeC" stackId="a" fill="#F44336" name="Grade C %" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Key Metrics Summary */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Key Performance Indicators
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary.main">
                    87.5%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Average Efficiency
                  </Typography>
                  <Chip label="+2.3%" color="success" size="small" sx={{ mt: 1 }} />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    4,167
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Daily Average (kg)
                  </Typography>
                  <Chip label="+5.2%" color="success" size="small" sx={{ mt: 1 }} />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    72%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Grade A Production
                  </Typography>
                  <Chip label="+7.1%" color="success" size="small" sx={{ mt: 1 }} />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    98.5%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Equipment Uptime
                  </Typography>
                  <Chip label="-0.5%" color="warning" size="small" sx={{ mt: 1 }} />
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default ProductionAnalytics;
