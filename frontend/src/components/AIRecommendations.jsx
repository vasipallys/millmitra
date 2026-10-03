import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  IconButton,
  Collapse,
  Alert,
  Divider,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Psychology,
  Lightbulb,
  TrendingUp,
  Speed,
  Security,
  Nature,
  ExpandMore,
  ExpandLess,
  CheckCircle,
  Schedule,
  Refresh
} from '@mui/icons-material';

const normalizeRec = (item, index) => {
  if (typeof item === 'string') {
    return {
      id: index,
      category: 'mill',
      title: item,
      summary: item,
      priority: 'medium',
      confidence: 0,
      impact: 'medium',
      implementation_time: '',
      expected_benefit: '',
      details: [],
      steps: [item],
      metrics: {},
    };
  }
  const rec = item && typeof item === 'object' ? item : {};
  return {
    id: rec.id || rec.title || index,
    category: rec.category || rec.type || 'mill',
    title: rec.title || rec.message || rec.recommendation || 'Mill suggestion',
    summary: rec.summary || rec.description || rec.recommendation || rec.message || '',
    priority: rec.priority || 'medium',
    confidence: Number(rec.confidence) || 0,
    impact: rec.impact || 'medium',
    implementation_time: rec.implementation_time || rec.implementation_timeline || '',
    expected_benefit: rec.expected_benefit || '',
    details: Array.isArray(rec.details) ? rec.details : [],
    steps: Array.isArray(rec.steps) ? rec.steps : (rec.recommendation ? [rec.recommendation] : []),
    metrics: rec.metrics || rec.data || {},
  };
};

const AIRecommendations = ({ recommendations: incoming, context = 'production', refreshInterval = 300000 }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(!incoming);
  const [expandedRec, setExpandedRec] = useState(null);
  const [detailRec, setDetailRec] = useState(null);
  const [implementNote, setImplementNote] = useState('');

  useEffect(() => {
    if (Array.isArray(incoming)) {
      setRecommendations(incoming.map(normalizeRec));
      setLoading(false);
      return undefined;
    }
    loadRecommendations();
    const interval = setInterval(loadRecommendations, refreshInterval);
    return () => clearInterval(interval);
  }, [incoming, context, refreshInterval]);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const { productionService } = await import('../services/productionService');
      const payload = await productionService.getRecommendations();
      const rows = payload?.recommendations || [];
      setRecommendations(rows.map(normalizeRec));
    } catch (error) {
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      efficiency: <Speed color="primary" />,
      quality: <CheckCircle color="success" />,
      maintenance: <Schedule color="warning" />,
      optimization: <TrendingUp color="info" />,
      automation: <Psychology color="secondary" />,
      sustainability: <Nature color="success" />,
      security: <Security color="error" />
    };
    return icons[category] || <Lightbulb color="primary" />;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'error',
      medium: 'warning',
      low: 'info'
    };
    return colors[priority] || 'default';
  };

  const getImpactColor = (impact) => {
    const colors = {
      high: 'success',
      medium: 'info',
      low: 'default'
    };
    return colors[impact] || 'default';
  };

  const handleExpandClick = (recId) => {
    setExpandedRec(expandedRec === recId ? null : recId);
  };

  const handleImplement = (recommendation) => {
    setImplementNote(`${recommendation.title} is a preview checklist, not an automated mill change. Apply the steps on Production or Quality if they match live data.`);
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Psychology color="primary" />
            <Typography variant="h6">AI Recommendations</Typography>
          </Box>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Analyzing data and generating recommendations...
          </Typography>
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
            <Typography variant="h6">AI Recommendations</Typography>
            <Chip 
              label={`${recommendations.length} suggestions`} 
              size="small" 
              color="primary" 
              variant="outlined" 
            />
          </Box>
          <IconButton onClick={loadRecommendations} size="small">
            <Refresh />
          </IconButton>
        </Box>

        {recommendations.length === 0 ? (
          <Alert severity="info">
            No AI recommendations available for {context} at the moment. 
            The system is continuously analyzing data to provide insights.
          </Alert>
        ) : (
          <List sx={{ p: 0 }}>
            {recommendations.map((rec) => (
              <Box key={rec.id} sx={{ mb: 1 }}>
                <ListItem
                  sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    cursor: 'pointer',
                    '&:hover': {
                      bgcolor: 'action.hover'
                    }
                  }}
                  onClick={() => handleExpandClick(rec.id)}
                >
                  <ListItemIcon>
                    {getCategoryIcon(rec.category)}
                  </ListItemIcon>
                  <ListItemText
                    primaryTypographyProps={{ component: 'div' }}
                    secondaryTypographyProps={{ component: 'div' }}
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography variant="subtitle2" component="span">
                          {rec.title}
                        </Typography>
                        <Chip 
                          label={rec.priority.toUpperCase()} 
                          size="small" 
                          color={getPriorityColor(rec.priority)}
                        />
                        <Chip 
                          label={`${(rec.confidence * 100).toFixed(0)}% confidence`} 
                          size="small" 
                          variant="outlined"
                        />
                        <Chip 
                          label={`${rec.impact} impact`} 
                          size="small" 
                          color={getImpactColor(rec.impact)}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" component="span" display="block" sx={{ mb: 0.5 }}>
                          {rec.summary}
                        </Typography>
                        <Typography variant="caption" component="span" display="block" color="text.secondary">
                          Implementation: {rec.implementation_time} | Expected: {rec.expected_benefit}
                        </Typography>
                      </Box>
                    }
                  />
                  <IconButton size="small" aria-label={expandedRec === rec.id ? 'Collapse recommendation' : 'Expand recommendation'}>
                    {expandedRec === rec.id ? <ExpandLess /> : <ExpandMore />}
                  </IconButton>
                </ListItem>

                <Collapse in={expandedRec === rec.id} timeout="auto" unmountOnExit>
                  <Box sx={{ pl: 4, pr: 2, pb: 2 }}>
                    {/* Details */}
                    <Typography variant="subtitle2" gutterBottom>
                      Analysis Details:
                    </Typography>
                    <List dense>
                      {rec.details.map((detail, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemText 
                            primary={detail}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    {/* Implementation Steps */}
                    <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                      Implementation Steps:
                    </Typography>
                    <List dense>
                      {rec.steps.map((step, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <Typography variant="body2" color="primary.main" fontWeight="bold">
                              {index + 1}
                            </Typography>
                          </ListItemIcon>
                          <ListItemText 
                            primary={step}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    {/* Metrics */}
                    {rec.metrics && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Expected Impact:
                        </Typography>
                        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          {Object.entries(rec.metrics).map(([key, value]) => (
                            <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2" color="text.secondary">
                                {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                              </Typography>
                              <Typography variant="body2" fontWeight="medium">
                                {typeof value === 'number' && key.includes('cost') ? `₹${value.toLocaleString()}` : 
                                 typeof value === 'number' && key.includes('rate') ? `${value}%` :
                                 typeof value === 'number' && key.includes('efficiency') ? `${value}%` :
                                 value}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </Box>
                    )}

                    {/* Actions */}
                    <Box sx={{ mt: 2, pt: 1, borderTop: 1, borderColor: 'divider' }}>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleImplement(rec)}
                          color={getPriorityColor(rec.priority)}
                        >
                          Implement
                        </Button>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => setDetailRec(rec)}
                        >
                          More Details
                        </Button>
                      </Box>
                    </Box>
                  </Box>
                </Collapse>
              </Box>
            ))}
          </List>
        )}

        {/* Summary */}
        {recommendations.length > 0 && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Recommendation Summary
            </Typography>
            <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  High Priority
                </Typography>
                <Typography variant="h6" color="error.main">
                  {recommendations.filter(r => r.priority === 'high').length}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Avg Confidence
                </Typography>
                <Typography variant="h6" color="primary.main">
                  {(recommendations.reduce((sum, r) => sum + r.confidence, 0) / recommendations.length * 100).toFixed(0)}%
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Quick Wins
                </Typography>
                <Typography variant="h6" color="success.main">
                  {recommendations.filter((r) => String(r?.implementation_time || '').toLowerCase().includes('hour')).length}
                </Typography>
              </Box>
            </Box>
          </Box>
        )}
      </CardContent>

      <Dialog open={Boolean(detailRec)} onClose={() => setDetailRec(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{detailRec?.title}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>{detailRec?.summary}</Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>{detailRec?.expected_benefit}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailRec(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(implementNote)} onClose={() => setImplementNote('')} maxWidth="sm" fullWidth>
        <DialogTitle>Preview recommendation</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>{implementNote}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImplementNote('')}>Close</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default AIRecommendations;
