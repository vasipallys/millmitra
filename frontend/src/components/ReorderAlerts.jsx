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
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Grid,
  Divider
} from '@mui/material';
import {
  Warning,
  ShoppingCart,
  Inventory,
  Close,
  Add,
  TrendingDown,
  Schedule
} from '@mui/icons-material';

const ReorderAlerts = ({ onReorder, autoRefresh = true }) => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [reorderDialog, setReorderDialog] = useState({ open: false, item: null });
  const [reorderForm, setReorderForm] = useState({
    quantity: '',
    supplier: '',
    expected_delivery: '',
    notes: ''
  });

  // Mock reorder alerts data
  const mockAlerts = [
    {
      id: 1,
      product_name: 'Broken Rice',
      category: 'broken_rice',
      current_stock: 150,
      reorder_level: 200,
      max_stock: 1000,
      unit: 'kg',
      last_reorder: '2024-01-10',
      consumption_rate: 25, // kg per day
      days_remaining: 6,
      priority: 'high',
      supplier: 'Local Supplier A',
      unit_cost: 35
    },
    {
      id: 2,
      product_name: 'Rice Bran',
      category: 'rice_bran',
      current_stock: 95,
      reorder_level: 100,
      max_stock: 500,
      unit: 'kg',
      last_reorder: '2024-01-08',
      consumption_rate: 8,
      days_remaining: 12,
      priority: 'medium',
      supplier: 'Supplier B',
      unit_cost: 15
    },
    {
      id: 3,
      product_name: 'Packaging Material',
      category: 'packaging',
      current_stock: 480,
      reorder_level: 500,
      max_stock: 2000,
      unit: 'pieces',
      last_reorder: '2024-01-12',
      consumption_rate: 50,
      days_remaining: 10,
      priority: 'low',
      supplier: 'Packaging Co.',
      unit_cost: 2.5
    }
  ];

  useEffect(() => {
    loadReorderAlerts();
    
    if (autoRefresh) {
      const interval = setInterval(loadReorderAlerts, 300000); // 5 minutes
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadReorderAlerts = async () => {
    try {
      setLoading(true);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // In real implementation, fetch from API
      // const response = await api.get('/inventory/reorder-alerts');
      // setAlerts(response.data.alerts);
      
      setAlerts(mockAlerts);
    } catch (error) {
      console.error('Failed to load reorder alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'error',
      medium: 'warning',
      low: 'info'
    };
    return colors[priority] || 'default';
  };

  const getPriorityIcon = (priority) => {
    if (priority === 'high') return <Warning color="error" />;
    if (priority === 'medium') return <TrendingDown color="warning" />;
    return <Schedule color="info" />;
  };

  const calculateRecommendedQuantity = (item) => {
    // Calculate recommended reorder quantity based on consumption and lead time
    const leadTimeDays = 7; // Assume 7 days lead time
    const safetyStock = item.consumption_rate * 3; // 3 days safety stock
    const reorderQuantity = (item.consumption_rate * leadTimeDays) + safetyStock;
    
    // Round up to nearest 50 for practical ordering
    return Math.ceil(reorderQuantity / 50) * 50;
  };

  const handleReorderClick = (item) => {
    const recommendedQty = calculateRecommendedQuantity(item);
    setReorderForm({
      quantity: recommendedQty.toString(),
      supplier: item.supplier,
      expected_delivery: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      notes: `Reorder for ${item.product_name} - Stock below reorder level`
    });
    setReorderDialog({ open: true, item });
  };

  const handleReorderSubmit = async () => {
    try {
      const reorderData = {
        product_id: reorderDialog.item.id,
        quantity: parseInt(reorderForm.quantity),
        supplier: reorderForm.supplier,
        expected_delivery: reorderForm.expected_delivery,
        notes: reorderForm.notes,
        estimated_cost: parseInt(reorderForm.quantity) * reorderDialog.item.unit_cost
      };

      // Call parent callback
      if (onReorder) {
        await onReorder(reorderData);
      }

      // Remove from alerts list
      setAlerts(prev => prev.filter(alert => alert.id !== reorderDialog.item.id));
      
      setReorderDialog({ open: false, item: null });
      setReorderForm({
        quantity: '',
        supplier: '',
        expected_delivery: '',
        notes: ''
      });

      // Show success message (in real app, use snackbar)
      console.log('Reorder submitted successfully');
      
    } catch (error) {
      console.error('Failed to submit reorder:', error);
    }
  };

  const dismissAlert = (alertId) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(amount);
  };

  return (
    <>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <ShoppingCart color="warning" />
              <Typography variant="h6">
                Reorder Alerts
              </Typography>
              {alerts.length > 0 && (
                <Chip 
                  label={`${alerts.length} items`} 
                  color="warning" 
                  size="small" 
                />
              )}
            </Box>
            <Button 
              onClick={loadReorderAlerts} 
              size="small" 
              disabled={loading}
            >
              Refresh
            </Button>
          </Box>

          {alerts.length === 0 ? (
            <Alert severity="success">
              All inventory levels are above reorder points. No immediate action required.
            </Alert>
          ) : (
            <List sx={{ p: 0 }}>
              {alerts.map((alert, index) => (
                <React.Fragment key={alert.id}>
                  <ListItem
                    sx={{
                      border: 1,
                      borderColor: `${getPriorityColor(alert.priority)}.main`,
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: `${getPriorityColor(alert.priority)}.50`
                    }}
                  >
                    <ListItemIcon>
                      {getPriorityIcon(alert.priority)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                          <Typography variant="subtitle2">
                            {alert.product_name}
                          </Typography>
                          <Chip 
                            label={alert.priority.toUpperCase()} 
                            color={getPriorityColor(alert.priority)}
                            size="small"
                          />
                          <Chip 
                            label={`${alert.days_remaining} days left`} 
                            size="small" 
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Typography variant="body2" gutterBottom>
                            Current: {alert.current_stock} {alert.unit} | 
                            Reorder Level: {alert.reorder_level} {alert.unit} | 
                            Consumption: {alert.consumption_rate} {alert.unit}/day
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Supplier: {alert.supplier} | 
                            Unit Cost: {formatCurrency(alert.unit_cost)} | 
                            Recommended Order: {calculateRecommendedQuantity(alert)} {alert.unit}
                          </Typography>
                        </Box>
                      }
                    />
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, ml: 2 }}>
                      <Button
                        variant="contained"
                        color={getPriorityColor(alert.priority)}
                        size="small"
                        startIcon={<Add />}
                        onClick={() => handleReorderClick(alert)}
                      >
                        Reorder
                      </Button>
                      <IconButton
                        size="small"
                        onClick={() => dismissAlert(alert.id)}
                      >
                        <Close fontSize="small" />
                      </IconButton>
                    </Box>
                  </ListItem>
                  {index < alerts.length - 1 && <Divider sx={{ my: 1 }} />}
                </React.Fragment>
              ))}
            </List>
          )}

          {/* Summary */}
          {alerts.length > 0 && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Reorder Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    High Priority
                  </Typography>
                  <Typography variant="h6" color="error.main">
                    {alerts.filter(a => a.priority === 'high').length}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    Medium Priority
                  </Typography>
                  <Typography variant="h6" color="warning.main">
                    {alerts.filter(a => a.priority === 'medium').length}
                  </Typography>
                </Grid>
                <Grid item xs={4}>
                  <Typography variant="body2" color="text.secondary">
                    Total Est. Cost
                  </Typography>
                  <Typography variant="h6" color="primary.main">
                    {formatCurrency(
                      alerts.reduce((total, alert) => 
                        total + (calculateRecommendedQuantity(alert) * alert.unit_cost), 0
                      )
                    )}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Reorder Dialog */}
      <Dialog open={reorderDialog.open} onClose={() => setReorderDialog({ open: false, item: null })} maxWidth="sm" fullWidth>
        <DialogTitle>
          Create Reorder Request
          {reorderDialog.item && (
            <Typography variant="subtitle2" color="text.secondary">
              {reorderDialog.item.product_name}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Quantity"
                type="number"
                value={reorderForm.quantity}
                onChange={(e) => setReorderForm(prev => ({ ...prev, quantity: e.target.value }))}
                inputProps={{ min: 1 }}
                required
                helperText={reorderDialog.item ? `Unit: ${reorderDialog.item.unit}` : ''}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Supplier"
                value={reorderForm.supplier}
                onChange={(e) => setReorderForm(prev => ({ ...prev, supplier: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Expected Delivery"
                type="date"
                value={reorderForm.expected_delivery}
                onChange={(e) => setReorderForm(prev => ({ ...prev, expected_delivery: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Estimated Cost"
                value={reorderDialog.item ? formatCurrency(parseInt(reorderForm.quantity || 0) * reorderDialog.item.unit_cost) : ''}
                disabled
                helperText="Calculated automatically"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={reorderForm.notes}
                onChange={(e) => setReorderForm(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Additional notes for the reorder..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReorderDialog({ open: false, item: null })}>
            Cancel
          </Button>
          <Button 
            onClick={handleReorderSubmit} 
            variant="contained"
            disabled={!reorderForm.quantity || !reorderForm.supplier || !reorderForm.expected_delivery}
          >
            Submit Reorder
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ReorderAlerts;
