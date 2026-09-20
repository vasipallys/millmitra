import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  Grid
} from '@mui/material';
import {
  MoreVert,
  PlayArrow,
  Pause,
  Stop,
  CheckCircle,
  Warning,
  Schedule,
  Assignment
} from '@mui/icons-material';

const BatchCard = ({ 
  batch, 
  onStart, 
  onPause, 
  onStop,
  onResume,
  onComplete, 
  onViewDetails,
  onView,
  onQualityTest 
}) => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const getStatusColor = (status) => {
    const colors = {
      'pending': 'warning',
      'planned': 'warning',
      'in_progress': 'info',
      'paused': 'warning',
      'completed': 'success',
      'failed': 'error',
      'cancelled': 'error',
      'quality_check': 'secondary'
    };
    return colors[status] || 'default';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'pending': <Schedule />,
      'planned': <Schedule />,
      'in_progress': <PlayArrow />,
      'paused': <Pause />,
      'completed': <CheckCircle />,
      'failed': <Warning />,
      'quality_check': <Assignment />
    };
    return icons[status] || <Schedule />;
  };

  const calculateProgress = () => {
    if (typeof batch.completion_percentage === 'number') {
      return Math.min(batch.completion_percentage, 100);
    }
    if (!batch.target_quantity || batch.target_quantity === 0) {
      return batch.status === 'in_progress' ? 50 : 0;
    }
    return Math.min(((batch.produced_quantity || 0) / batch.target_quantity) * 100, 100);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: batch.status === 'in_progress' ? 2 : 1,
        borderColor: batch.status === 'in_progress' ? 'primary.main' : 'divider',
        '&:hover': {
          boxShadow: 3,
          transform: 'translateY(-2px)',
          transition: 'all 0.2s ease-in-out'
        }
      }}
    >
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography variant="h6" component="div" gutterBottom>
              {batch.batch_id || batch.batch_number || `Batch ${batch.id}`}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getStatusIcon(batch.status)}
              <Chip 
                label={(batch.status || 'planned').replace('_', ' ').toUpperCase()} 
                color={getStatusColor(batch.status)}
                size="small"
              />
            </Box>
          </Box>
          <IconButton onClick={handleMenuClick} size="small">
            <MoreVert />
          </IconButton>
        </Box>

        {/* Batch Details */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Product Type
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {batch.product_type || 'Basmati Rice'}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Quality Grade
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {batch.quality_grade || 'A'}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Start Date
            </Typography>
            <Typography variant="body1">
              {formatDate(batch.production_date)}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Start Time
            </Typography>
            <Typography variant="body1">
              {batch.start_time ? formatTime(batch.start_time) : 'Not started'}
            </Typography>
          </Grid>
        </Grid>

        {/* Progress Section */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Production Progress
            </Typography>
            <Typography variant="body2" fontWeight="medium">
              {batch.produced_quantity || 0} / {batch.target_quantity || 0} kg
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={calculateProgress()} 
            sx={{ height: 8, borderRadius: 4 }}
            color={batch.status === 'completed' ? 'success' : 'primary'}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            {calculateProgress().toFixed(1)}% Complete
          </Typography>
        </Box>

        {/* Quality Metrics */}
        {batch.quality_metrics && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Quality Metrics
            </Typography>
            <Grid container spacing={1}>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Moisture
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {batch.quality_metrics.moisture_content || 'N/A'}%
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" color="text.secondary">
                  Broken
                </Typography>
                <Typography variant="body2" fontWeight="medium">
                  {batch.quality_metrics.broken_percentage || 'N/A'}%
                </Typography>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Timing Information */}
        <Box sx={{ mb: 2 }}>
          <Grid container spacing={1}>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">
                Estimated Duration
              </Typography>
              <Typography variant="body2">
                {batch.estimated_duration || '4'} hours
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">
                Remaining Time
              </Typography>
              <Typography variant="body2">
                {batch.remaining_time || 'Calculating...'}
              </Typography>
            </Grid>
          </Grid>
        </Box>

        {/* Efficiency Indicator */}
        {batch.efficiency_score && (
          <Box sx={{ p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Efficiency Score
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <LinearProgress 
                variant="determinate" 
                value={batch.efficiency_score} 
                sx={{ flexGrow: 1, height: 4 }}
                color={batch.efficiency_score > 80 ? 'success' : batch.efficiency_score > 60 ? 'warning' : 'error'}
              />
              <Typography variant="body2" fontWeight="medium">
                {batch.efficiency_score}%
              </Typography>
            </Box>
          </Box>
        )}

        {/* Action Menu */}
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleMenuClose}
          PaperProps={{
            elevation: 3,
            sx: { minWidth: 180 }
          }}
        >
          {(batch.status === 'pending' || batch.status === 'planned') && (
            <MenuItem onClick={() => { onStart?.(batch); handleMenuClose(); }}>
              <PlayArrow sx={{ mr: 1 }} fontSize="small" />
              Start Batch
            </MenuItem>
          )}
          
          {batch.status === 'in_progress' && (
            <>
              <MenuItem onClick={() => { onPause?.(batch); handleMenuClose(); }}>
                <Pause sx={{ mr: 1 }} fontSize="small" />
                Pause Batch
              </MenuItem>
              <MenuItem onClick={() => { (onStop || onPause)?.(batch); handleMenuClose(); }}>
                <Stop sx={{ mr: 1 }} fontSize="small" />
                Stop Batch
              </MenuItem>
            </>
          )}
          
          {batch.status === 'paused' && (
            <MenuItem onClick={() => { (onResume || onStart)?.(batch); handleMenuClose(); }}>
              <PlayArrow sx={{ mr: 1 }} fontSize="small" />
              Resume Batch
            </MenuItem>
          )}
          
          {(batch.status === 'completed' || batch.status === 'in_progress' || batch.status === 'paused') && (
            <MenuItem onClick={() => { onQualityTest?.(batch); handleMenuClose(); }}>
              <Assignment sx={{ mr: 1 }} fontSize="small" />
              Quality Test
            </MenuItem>
          )}
          
          <Divider />
          
          <MenuItem onClick={() => { (onViewDetails || onView)?.(batch); handleMenuClose(); }}>
            View Details
          </MenuItem>
          
          {(batch.status === 'in_progress' || batch.status === 'paused') && (
            <>
              <Divider />
              <MenuItem 
                onClick={() => { onComplete?.(batch); handleMenuClose(); }}
                sx={{ color: 'success.main' }}
              >
                <CheckCircle sx={{ mr: 1 }} fontSize="small" />
                Mark Complete
              </MenuItem>
            </>
          )}
        </Menu>
      </CardContent>
    </Card>
  );
};

export default BatchCard;
