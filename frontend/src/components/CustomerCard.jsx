import {
  Card, CardContent, CardActions, Typography, Box, Chip,
  Button, Avatar, IconButton, Tooltip, LinearProgress
} from '@mui/material';
import {
  Person, Business, Phone, Email, TrendingUp, Warning,
  Chat, ShoppingCart, Star, LocationOn
} from '@mui/icons-material';

const CustomerCard = ({ customer, onSelect, onInteraction, onViewOrders }) => {
  const getSegmentColor = (segment) => {
    const colors = {
      premium: 'success',
      regular: 'primary',
      budget: 'warning',
      inactive: 'default'
    };
    return colors[segment] || 'default';
  };

  const getChurnRiskColor = (score) => {
    if (score >= 0.7) return 'error';
    if (score >= 0.4) return 'warning';
    return 'success';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        {/* Header */}
        <Box display="flex" alignItems="center" mb={2}>
          <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
            {customer.customer_type === 'business' ? <Business /> : <Person />}
          </Avatar>
          <Box flexGrow={1}>
            <Typography variant="h6" noWrap>
              {customer.name}
            </Typography>
            <Typography variant="body2" color="text.secondary" noWrap>
              {customer.customer_code}
            </Typography>
          </Box>
          {customer.churn_risk_score >= 0.7 && (
            <Tooltip title="High churn risk">
              <Warning color="error" />
            </Tooltip>
          )}
        </Box>

        {/* Company Info */}
        {customer.company_name && (
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {customer.company_name}
          </Typography>
        )}

        {/* Contact Info */}
        <Box display="flex" alignItems="center" mb={1}>
          <Phone sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary">
            {customer.phone || 'No phone'}
          </Typography>
        </Box>
        
        <Box display="flex" alignItems="center" mb={2}>
          <Email sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary" noWrap>
            {customer.email || 'No email'}
          </Typography>
        </Box>

        {/* Location */}
        {customer.city && (
          <Box display="flex" alignItems="center" mb={2}>
            <LocationOn sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {customer.city}, {customer.state}
            </Typography>
          </Box>
        )}

        {/* Segment and Status */}
        <Box display="flex" gap={1} mb={2}>
          <Chip
            label={customer.customer_segment}
            color={getSegmentColor(customer.customer_segment)}
            size="small"
          />
          <Chip
            label={customer.status}
            variant="outlined"
            size="small"
          />
        </Box>

        {/* Metrics */}
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Total Orders
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {customer.total_orders}
            </Typography>
          </Box>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Total Spent
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {formatCurrency(customer.total_spent)}
            </Typography>
          </Box>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Lifetime Value
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {formatCurrency(customer.lifetime_value)}
            </Typography>
          </Box>
        </Box>

        {/* Churn Risk */}
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Churn Risk
            </Typography>
            <Typography 
              variant="body2" 
              fontWeight="bold"
              color={`${getChurnRiskColor(customer.churn_risk_score)}.main`}
            >
              {Math.round(customer.churn_risk_score * 100)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={customer.churn_risk_score * 100}
            color={getChurnRiskColor(customer.churn_risk_score)}
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>

        {/* Last Order */}
        {customer.last_order_date && (
          <Typography variant="body2" color="text.secondary">
            Last order: {new Date(customer.last_order_date).toLocaleDateString()}
          </Typography>
        )}

        {/* Next Order Prediction */}
        {customer.next_order_prediction && (
          <Typography variant="body2" color="primary.main">
            Next order predicted: {new Date(customer.next_order_prediction).toLocaleDateString()}
          </Typography>
        )}
      </CardContent>

      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
        <Box>
          <Tooltip title="Add Interaction">
            <IconButton size="small" aria-label="Add interaction" onClick={onInteraction}>
              <Chat />
            </IconButton>
          </Tooltip>
          <Tooltip title="View Orders">
            <IconButton size="small" aria-label="View orders" onClick={onViewOrders || onSelect}>
              <ShoppingCart />
            </IconButton>
          </Tooltip>
        </Box>
        <Button size="small" variant="outlined" onClick={onSelect}>
          View Details
        </Button>
      </CardActions>
    </Card>
  );
};

export default CustomerCard;