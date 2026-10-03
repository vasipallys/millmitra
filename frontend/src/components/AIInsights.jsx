import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Alert,
  Button
} from '@mui/material';
import {
  Psychology,
  ExpandMore,
  ExpandLess,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Lightbulb,
  Refresh
} from '@mui/icons-material';

const AIInsights = ({ refreshInterval = 300000 }) => { // 5 minutes default
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedInsight, setExpandedInsight] = useState(null);

  // Mock AI insights data
  const mockInsights = [
    {
      id: 1,
      category: 'production_efficiency',
      title: 'Production Optimization Opportunity',
      summary: 'AI detected 15% efficiency improvement potential in milling process',
      confidence: 0.89,
      impact: 'high',
      priority: 'high',
      details: [
        'Peak efficiency hours: 10 AM - 2 PM',
        'Recommended batch size: 2,500 kg',
        'Optimal moisture content: 12.5%',
        'Expected cost savings: ₹25,000/month'
      ],
      recommendations: [
        'Adjust production schedule to peak hours',
        'Implement automated moisture monitoring',
        'Optimize batch processing workflow'
      ],
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      category: 'quality_prediction',
      title: 'Quality Trend Analysis',
      summary: 'Quality scores trending upward with new sorting equipment',
      confidence: 0.92,
      impact: 'medium',
      priority: 'medium',
      details: [
        'Average quality score: 87.5%',
        'Improvement rate: +3.2% this week',
        'Grade A percentage: 78%',
        'Defect reduction: 45%'
      ],
      recommendations: [
        'Continue current quality protocols',
        'Monitor equipment calibration',
        'Train staff on new procedures'
      ],
      timestamp: new Date(Date.now() - 3600000).toISOString()
    },
    {
      id: 3,
      category: 'demand_forecast',
      title: 'Demand Surge Prediction',
      summary: 'AI predicts 25% demand increase in next 2 weeks',
      confidence: 0.85,
      impact: 'high',
      priority: 'urgent',
      details: [
        'Predicted demand: 3,125 kg/day',
        'Current capacity: 2,500 kg/day',
        'Capacity gap: 625 kg/day',
        'Revenue opportunity: ₹1.2L additional'
      ],
      recommendations: [
        'Increase production shifts',
        'Secure additional raw materials',
        'Optimize inventory levels',
        'Consider temporary capacity expansion'
      ],
      timestamp: new Date(Date.now() - 7200000).toISOString()
    },
    {
      id: 4,
      category: 'cost_optimization',
      title: 'Energy Cost Reduction',
      summary: 'AI identified energy optimization opportunities',
      confidence: 0.78,
      impact: 'medium',
      priority: 'low',
      details: [
        'Current energy cost: ₹45,000/month',
        'Potential savings: ₹8,500/month',
        'Peak usage hours: 2 PM - 6 PM',
        'Efficiency rating: 72%'
      ],
      recommendations: [
        'Shift high-energy operations to off-peak hours',
        'Implement smart power management',
        'Regular equipment maintenance',
        'Consider solar power integration'
      ],
      timestamp: new Date(Date.now() - 10800000).toISOString()
    }
  ];

  useEffect(() => {
    loadInsights();
    
    // Set up auto-refresh
    const interval = setInterval(loadInsights, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // In real implementation, fetch from API
      // const response = await api.get('/ai/insights/generate');
      // setInsights(response.data.insights);
      
      setInsights(mockInsights);
    } catch (err) {
      setError('Failed to load AI insights');
      console.error('Error loading insights:', err);
    } finally {
      setLoading(false);
    }
  };

  const getInsightIcon = (category) => {
    const icons = {
      production_efficiency: <TrendingUp color="primary" />,
      quality_prediction: <CheckCircle color="success" />,
      demand_forecast: <TrendingUp color="info" />,
      cost_optimization: <TrendingDown color="warning" />,
      risk_assessment: <Warning color="error" />
    };
    return icons[category] || <Lightbulb color="secondary" />;
  };

  const getImpactColor = (impact) => {
    const colors = {
      high: 'error',
      medium: 'warning',
      low: 'info'
    };
    return colors[impact] || 'default';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'error',
      high: 'warning',
      medium: 'info',
      low: 'success'
    };
    return colors[priority] || 'default';
  };

  const handleExpandClick = (insightId) => {
    setExpandedInsight(expandedInsight === insightId ? null : insightId);
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Psychology color="primary" />
            <Typography variant="h6">AI Insights</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Psychology color="primary" />
            <Typography variant="h6">AI Insights</Typography>
          </Box>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Button onClick={loadInsights} startIcon={<Refresh />}>
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Psychology color="primary" />
            <Typography variant="h6">AI Insights</Typography>
            <Chip 
              label={`${insights.length} insights`} 
              size="small" 
              color="primary" 
              variant="outlined" 
            />
          </Box>
          <IconButton onClick={loadInsights} size="small">
            <Refresh />
          </IconButton>
        </Box>

        {insights.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 3 }}>
            No AI insights available at the moment.
          </Typography>
        ) : (
          <List sx={{ p: 0 }}>
            {insights.map((insight) => (
              <Box key={insight.id} sx={{ mb: 1 }}>
                <ListItem
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover'
                    }
                  }}
                  onClick={() => handleExpandClick(insight.id)}
                >
                  <ListItemIcon>
                    {getInsightIcon(insight.category)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography variant="subtitle2">
                          {insight.title}
                        </Typography>
                        <Chip 
                          label={insight.priority} 
                          size="small" 
                          color={getPriorityColor(insight.priority)}
                        />
                        <Chip 
                          label={`${(insight.confidence * 100).toFixed(0)}% confidence`} 
                          size="small" 
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={insight.summary}
                  />
                  <IconButton size="small" aria-label={expandedInsight === insight.id ? 'Collapse insight' : 'Expand insight'}>
                    {expandedInsight === insight.id ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </ListItem>

                <Collapse in={expandedInsight === insight.id} timeout="auto" unmountOnExit>
                  <Box sx={{ pl: 4, pr: 2, pb: 2 }}>
                    {/* Details */}
                    <Typography variant="subtitle2" gutterBottom>
                      Key Details:
                    </Typography>
                    <List dense>
                      {insight.details.map((detail, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemText 
                            primary={detail}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    {/* Recommendations */}
                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                      AI Recommendations:
                    </Typography>
                    <List dense>
                      {insight.recommendations.map((recommendation, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <Lightbulb fontSize="small" color="primary" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={recommendation}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    {/* Metadata */}
                    <Box sx={{ mt: 2, pt: 1, borderTop: 1, borderColor: 'divider' }}>
                      <Typography variant="caption" color="text.secondary">
                        Generated: {new Date(insight.timestamp).toLocaleString()} | 
                        Impact: {insight.impact} | 
                        Category: {insight.category.replace('_', ' ')}
                      </Typography>
                    </Box>
                  </Box>
                </Collapse>
              </Box>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
};

export default AIInsights;
