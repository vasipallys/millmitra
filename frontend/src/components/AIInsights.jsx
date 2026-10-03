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

const normalizeInsight = (item, index) => ({
  id: item.id || item.title || index,
  category: item.category || item.type || 'operational',
  title: item.title || 'Mill note',
  summary: item.summary || item.description || item.insight || '',
  confidence: item.confidence,
  impact: item.impact || item.priority || 'medium',
  priority: item.priority || 'medium',
  details: item.details || (item.data ? Object.entries(item.data).map(([key, value]) => `${key}: ${value}`) : []),
  recommendations: item.recommendations || (item.recommendation ? [item.recommendation] : []),
  timestamp: item.timestamp || item.created_at,
});

const AIInsights = ({ insights: incoming, refreshInterval = 300000 }) => {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(!incoming);
  const [error, setError] = useState(null);
  const [expandedInsight, setExpandedInsight] = useState(null);

  useEffect(() => {
    if (Array.isArray(incoming)) {
      setInsights(incoming.map(normalizeInsight));
      setLoading(false);
      return undefined;
    }
    loadInsights();
    const interval = setInterval(loadInsights, refreshInterval);
    return () => clearInterval(interval);
  }, [incoming, refreshInterval]);

  const loadInsights = async () => {
    try {
      setLoading(true);
      setError(null);
      const { dashboardService } = await import('../services/dashboardService');
      const payload = await dashboardService.getInsights();
      const rows = Array.isArray(payload) ? payload : (payload?.insights || []);
      setInsights(rows.map(normalizeInsight));
    } catch (err) {
      setError('Could not load mill insights');
      setInsights([]);
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
