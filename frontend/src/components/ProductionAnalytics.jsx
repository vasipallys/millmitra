import React, { useEffect, useState } from 'react';
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
  const [fetched, setFetched] = useState(null);
  useEffect(() => {
    if (data) return undefined;
    let cancelled = false;
    import('../services/productionService').then(({ productionService }) =>
      Promise.all([
        productionService.getAnalytics(30),
        productionService.getBatches({ per_page: 50 }),
      ]).then(([analyticsPayload, batchesPayload]) => {
        if (cancelled) return;
        const analytics = analyticsPayload?.analytics || analyticsPayload || {};
        const batches = batchesPayload?.batches || batchesPayload?.items || [];
        const daily = (analytics.daily_production || []).map((row) => ({
          date: row.date || row.day,
          production: Number(row.production || row.output || row.total_output || 0),
          efficiency: Number(row.efficiency || analytics.average_efficiency || 0),
          target: Number(row.target || 0),
        }));
        const byType = {};
        batches.forEach((batch) => {
          const name = batch.paddy_variety || batch.target_rice_variety || 'Rice';
          byType[name] = (byType[name] || 0) + Number(batch.total_output || batch.rice_output || 0);
        });
        const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00C49F'];
        setFetched({
          dailyProduction: daily,
          productionByType: Object.entries(byType).map(([name, value], index) => ({
            name,
            value,
            color: colors[index % colors.length],
          })).filter((row) => row.value > 0),
          qualityTrends: [],
        });
      }).catch(() => {
        if (!cancelled) setFetched({ dailyProduction: [], productionByType: [], qualityTrends: [] });
      })
    );
    return () => { cancelled = true; };
  }, [data]);

  const analyticsData = data || fetched || { dailyProduction: [], productionByType: [], qualityTrends: [] };
  const dailyRows = analyticsData.dailyProduction || [];
  const avgEfficiency = dailyRows.length
    ? dailyRows.reduce((sum, row) => sum + Number(row.efficiency || 0), 0) / dailyRows.length
    : 0;
  const avgDailyKg = dailyRows.length
    ? dailyRows.reduce((sum, row) => sum + Number(row.production || 0), 0) / dailyRows.length
    : 0;
  const gradeA = (analyticsData.qualityTrends || []).length
    ? (analyticsData.qualityTrends.reduce((sum, row) => sum + Number(row.gradeA || 0), 0) / analyticsData.qualityTrends.length)
    : 0;


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
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {dailyRows.length === 0 ? (
                <Typography color="text.secondary">No records yet</Typography>
              ) : (
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
              )}
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
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {(analyticsData.productionByType || []).length === 0 ? (
                <Typography color="text.secondary">No records yet</Typography>
              ) : (
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
              )}
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
            <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {dailyRows.length === 0 ? (
                <Typography color="text.secondary">No records yet</Typography>
              ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analyticsData.dailyProduction}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                  />
                  <YAxis domain={[0, 100]} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar 
                    dataKey="efficiency" 
                    fill="#4CAF50"
                    name="Efficiency (%)"
                  />
                </BarChart>
              </ResponsiveContainer>
              )}
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
            <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {(analyticsData.qualityTrends || []).length === 0 ? (
                <Typography color="text.secondary">No records yet</Typography>
              ) : (
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
              )}
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
                    {avgEfficiency.toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Average Efficiency
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main">
                    {Math.round(avgDailyKg).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Daily Average (kg)
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    {gradeA.toFixed(0)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Grade A Production
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {dailyRows.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Days with production records
                  </Typography>
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
