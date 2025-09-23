import { useState, useEffect } from 'react';
import { 
  Card, CardContent, Typography, Box, CircularProgress, 
  Chip, Grid, Divider, LinearProgress 
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, Warning, Insights, 
  Storage, LocalShipping, MonetizationOn 
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, 
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';

const AIPredictions = ({ insights = [] }) => {
  const [loading, setLoading] = useState(false);
  const [predictionData, setPredictionData] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Generate mock prediction data for charts
  useEffect(() => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      const mockData = [
        { date: 'Jan 1', production: 2400, quality: 85, inventory: 12000, orders: 15 },
        { date: 'Jan 2', production: 2600, quality: 87, inventory: 11500, orders: 18 },
        { date: 'Jan 3', production: 2500, quality: 86, inventory: 11800, orders: 16 },
        { date: 'Jan 4', production: 2700, quality: 88, inventory: 11200, orders: 20 },
        { date: 'Jan 5', production: 2800, quality: 89, inventory: 10800, orders: 22 },
        { date: 'Jan 6', production: 2650, quality: 87, inventory: 11500, orders: 19 },
        { date: 'Jan 7', production: 2750, quality: 88, inventory: 11000, orders: 21 },
      ];
      setPredictionData(mockData);
      setLoading(false);
    }, 800);
  }, []);

  // Filter insights by category
  const filteredInsights = selectedCategory === 'all' 
    ? insights 
    : insights.filter(insight => insight.category === selectedCategory);

  // Get unique categories for filtering
  const categories = ['all', ...new Set(insights.map(insight => insight.category))];

  // Get icon based on category
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'production_efficiency': return <TrendingUp />;
      case 'quality_prediction': return <Insights />;
      case 'inventory_optimization': return <Storage />;
      case 'demand_forecast': return <LocalShipping />;
      case 'cost_optimization': return <MonetizationOn />;
      case 'maintenance_prediction': return <Warning />;
      default: return <Insights />;
    }
  };

  // Get color based on priority
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight="bold">
            AI Predictions & Insights
          </Typography>
          <Chip 
            label={`${insights.length} Active Insights`} 
            color="primary" 
            variant="outlined" 
          />
        </Box>

        {/* Category Filters */}
        <Box display="flex" flexWrap="wrap" gap={1} mb={3}>
          {categories.map(category => (
            <Chip
              key={category}
              label={category.replace('_', ' ').toUpperCase()}
              onClick={() => setSelectedCategory(category)}
              color={selectedCategory === category ? 'primary' : 'default'}
              variant={selectedCategory === category ? 'filled' : 'outlined'}
            />
          ))}
        </Box>

        <Grid container spacing={3}>
          {/* Prediction Charts */}
          <Grid item xs={12} md={8}>
            <Card variant="outlined" sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                  Production & Quality Trends
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={predictionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="production" 
                      stroke="#1976d2" 
                      name="Production (kg)" 
                      strokeWidth={2} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey="quality" 
                      stroke="#4caf50" 
                      name="Quality Score (%)" 
                      strokeWidth={2} 
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                  Inventory & Orders Forecast
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={predictionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area 
                      type="monotone" 
                      dataKey="inventory" 
                      name="Inventory Value (₹)" 
                      stroke="#ff9800" 
                      fill="#ff9800" 
                      fillOpacity={0.3} 
                    />
                    <Area 
                      type="monotone" 
                      dataKey="orders" 
                      name="Orders" 
                      stroke="#9c27b0" 
                      fill="#9c27b0" 
                      fillOpacity={0.3} 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Insights List */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined" sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                  Key Insights
                </Typography>
                <Box sx={{ maxHeight: 600, overflowY: 'auto' }}>
                  {filteredInsights.length > 0 ? (
                    filteredInsights.map((insight) => (
                      <Box key={insight.id} mb={2}>
                        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                          <Box display="flex" alignItems="center" gap={1}>
                            {getCategoryIcon(insight.category)}
                            <Typography variant="subtitle2" fontWeight="bold">
                              {insight.title}
                            </Typography>
                          </Box>
                          <Chip 
                            label={insight.priority} 
                            size="small" 
                            color={getPriorityColor(insight.priority)} 
                          />
                        </Box>
                        <Typography variant="body2" color="textSecondary" mb={1}>
                          {insight.summary}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                          <Typography variant="caption" color="textSecondary">
                            Confidence: {Math.round(insight.confidence * 100)}%
                          </Typography>
                          <LinearProgress 
                            variant="determinate" 
                            value={insight.confidence * 100} 
                            sx={{ flexGrow: 1, height: 6 }} 
                          />
                        </Box>
                        <Divider sx={{ mt: 1 }} />
                      </Box>
                    ))
                  ) : (
                    <Typography variant="body2" color="textSecondary">
                      No insights available for selected category
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default AIPredictions;
