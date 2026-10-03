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
  Grid,
  Avatar
} from '@mui/material';
import {
  MoreVert,
  Add,
  Remove,
  Edit,
  Visibility,
  Warning,
  CheckCircle,
  Inventory,
  TrendingUp,
  TrendingDown
} from '@mui/icons-material';

const StockCard = ({ 
  stock, 
  onAddStock, 
  onRemoveStock, 
  onEditStock, 
  onViewDetails,
  onReorder 
}) => {
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  // Return early if stock is not provided
  if (!stock) {
    return null;
  }

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const getStockStatus = () => {
    const { current_stock = 0, reorder_level = 0, max_stock = 100 } = stock || {};
    
    if (current_stock <= reorder_level) {
      return { status: 'low', color: 'error', label: 'Low Stock' };
    } else if (current_stock >= max_stock * 0.9) {
      return { status: 'high', color: 'warning', label: 'High Stock' };
    } else {
      return { status: 'normal', color: 'success', label: 'In Stock' };
    }
  };

  const calculateStockPercentage = () => {
    const { current_stock, max_stock } = stock;
    if (!max_stock || max_stock === 0) return 0;
    return Math.min((current_stock / max_stock) * 100, 100);
  };

  const getStockTrend = () => {
    // Mock trend calculation - in real app, this would be based on historical data
    const trend = stock.trend || Math.random() > 0.5 ? 'up' : 'down';
    const percentage = stock.trend_percentage || (Math.random() * 20).toFixed(1);
    
    return { trend, percentage };
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'processed_rice': '🍚',
      'raw_rice': '🌾',
      'broken_rice': '🍚',
      'rice_bran': '🌾',
      'premium_rice': '✨',
      'paddy': '🌾'
    };
    return icons[category] || '📦';
  };

  const formatLastUpdated = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      return date.toLocaleDateString('en-IN', { 
        day: '2-digit', 
        month: 'short' 
      });
    }
  };

  const stockStatus = getStockStatus();
  const stockPercentage = calculateStockPercentage();
  const { trend, percentage } = getStockTrend();

  return (
    <Card 
      sx={{ 
        height: '100%',
        border: stockStatus.status === 'low' ? 2 : 1,
        borderColor: stockStatus.status === 'low' ? 'error.main' : 'divider',
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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: 'primary.light' }}>
              {getCategoryIcon(stock.category)}
            </Avatar>
            <Box>
              <Typography variant="h6" component="div" noWrap>
                {stock?.product_name || 'Unknown Product'}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip 
                  label={stockStatus.label} 
                  color={stockStatus.color}
                  size="small"
                  icon={stockStatus.status === 'low' ? <Warning /> : <CheckCircle />}
                />
              </Box>
            </Box>
          </Box>
          <IconButton onClick={handleMenuClick} size="small">
            <MoreVert />
          </IconButton>
        </Box>

        {/* Stock Levels */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Current Stock
            </Typography>
            <Typography variant="h6" fontWeight="bold" color={stockStatus.color + '.main'}>
              {(stock?.current_stock || 0).toLocaleString()} {stock?.unit || 'kg'}
            </Typography>
          </Box>
          
          <LinearProgress 
            variant="determinate" 
            value={stockPercentage} 
            sx={{ height: 8, borderRadius: 4, mb: 1 }}
            color={stockStatus.color}
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="caption" color="text.secondary">
              Reorder: {stock?.reorder_level || 0} {stock?.unit || 'kg'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Max: {stock?.max_stock || 100} {stock?.unit || 'kg'}
            </Typography>
          </Box>
        </Box>

        {/* Stock Details Grid */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Category
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {(stock?.category || 'general').replace('_', ' ').toUpperCase()}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Location
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              {stock.storage_location || 'Warehouse A'}
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Unit Price
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              ₹{stock.unit_price || 45}/kg
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body2" color="text.secondary">
              Total Value
            </Typography>
            <Typography variant="body1" fontWeight="medium">
              ₹{(((stock?.current_stock || 0) * (stock?.unit_price || 45)) / 1000).toFixed(0)}K
            </Typography>
          </Grid>
        </Grid>

        {/* Stock Trend */}
        <Box sx={{ mb: 2, p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              Stock Trend (7 days)
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {trend === 'up' ? (
                <TrendingUp fontSize="small" color="success" />
              ) : (
                <TrendingDown fontSize="small" color="error" />
              )}
              <Typography 
                variant="body2" 
                color={trend === 'up' ? 'success.main' : 'error.main'}
                fontWeight="medium"
              >
                {percentage}%
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Last Updated */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Updated: {formatLastUpdated(stock.last_updated)}
          </Typography>
          {stockStatus.status === 'low' && (
            <Chip 
              label="Reorder Now" 
              color="error" 
              size="small" 
              variant="outlined"
              onClick={() => onReorder?.(stock)}
              sx={{ cursor: 'pointer' }}
            />
          )}
        </Box>

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
          <MenuItem onClick={() => { onAddStock?.(stock); handleMenuClose(); }}>
            <Add sx={{ mr: 1 }} fontSize="small" />
            Add Stock
          </MenuItem>
          
          <MenuItem onClick={() => { onRemoveStock?.(stock); handleMenuClose(); }}>
            <Remove sx={{ mr: 1 }} fontSize="small" />
            Remove Stock
          </MenuItem>
          
          <MenuItem onClick={() => { onEditStock?.(stock); handleMenuClose(); }}>
            <Edit sx={{ mr: 1 }} fontSize="small" />
            Edit Details
          </MenuItem>
          
          <Divider />
          
          <MenuItem onClick={() => { onViewDetails?.(stock); handleMenuClose(); }}>
            <Visibility sx={{ mr: 1 }} fontSize="small" />
            View Details
          </MenuItem>
          
          {stockStatus.status === 'low' && (
            <>
              <Divider />
              <MenuItem 
                onClick={() => { onReorder?.(stock); handleMenuClose(); }}
                sx={{ color: 'error.main' }}
              >
                <Warning sx={{ mr: 1 }} fontSize="small" />
                Reorder Stock
              </MenuItem>
            </>
          )}
        </Menu>
      </CardContent>
    </Card>
  );
};

export default StockCard;
