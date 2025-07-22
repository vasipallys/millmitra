import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  MenuItem,
  Box,
  Typography,
  FormControl,
  InputLabel,
  Select,
  Chip,
  Alert,
  Divider
} from '@mui/material';
import { Add, Remove, SwapHoriz } from '@mui/icons-material';

const StockMovementDialog = ({ open, onClose, onSubmit, stockItem = null, movementType = 'in' }) => {
  const [formData, setFormData] = useState({
    stock_id: stockItem?.id || '',
    movement_type: movementType, // 'in', 'out', 'transfer'
    quantity: '',
    unit_price: stockItem?.unit_price || '',
    reference_number: '',
    supplier_customer: '',
    reason: '',
    notes: '',
    location_from: stockItem?.storage_location || '',
    location_to: '',
    batch_number: '',
    expiry_date: ''
  });

  const movementTypes = [
    { value: 'in', label: 'Stock In', icon: <Add />, color: 'success' },
    { value: 'out', label: 'Stock Out', icon: <Remove />, color: 'error' },
    { value: 'transfer', label: 'Transfer', icon: <SwapHoriz />, color: 'info' }
  ];

  const reasonOptions = {
    in: [
      'Purchase',
      'Production',
      'Return from Customer',
      'Adjustment - Increase',
      'Transfer In',
      'Other'
    ],
    out: [
      'Sale',
      'Production Consumption',
      'Wastage',
      'Damage',
      'Adjustment - Decrease',
      'Transfer Out',
      'Other'
    ],
    transfer: [
      'Warehouse Transfer',
      'Location Change',
      'Reorganization',
      'Quality Segregation',
      'Other'
    ]
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMovementTypeChange = (newType) => {
    setFormData(prev => ({
      ...prev,
      movement_type: newType,
      reason: '', // Reset reason when type changes
      supplier_customer: '',
      location_to: newType === 'transfer' ? prev.location_to : ''
    }));
  };

  const calculateTotalValue = () => {
    const quantity = parseFloat(formData.quantity) || 0;
    const unitPrice = parseFloat(formData.unit_price) || 0;
    return quantity * unitPrice;
  };

  const handleSubmit = () => {
    const movementData = {
      ...formData,
      quantity: parseFloat(formData.quantity),
      unit_price: parseFloat(formData.unit_price),
      total_value: calculateTotalValue(),
      movement_date: new Date().toISOString(),
      stock_name: stockItem?.product_name || 'Unknown'
    };

    onSubmit(movementData);
    onClose();
    
    // Reset form
    setFormData({
      stock_id: '',
      movement_type: 'in',
      quantity: '',
      unit_price: '',
      reference_number: '',
      supplier_customer: '',
      reason: '',
      notes: '',
      location_from: '',
      location_to: '',
      batch_number: '',
      expiry_date: ''
    });
  };

  const getMovementTypeData = () => {
    return movementTypes.find(type => type.value === formData.movement_type);
  };

  const currentMovementType = getMovementTypeData();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {currentMovementType?.icon}
          Record Stock Movement
          {stockItem && (
            <Chip 
              label={stockItem.product_name} 
              color="primary" 
              variant="outlined" 
            />
          )}
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Movement Type Selection */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Movement Type
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              {movementTypes.map((type) => (
                <Chip
                  key={type.value}
                  label={type.label}
                  icon={type.icon}
                  color={formData.movement_type === type.value ? type.color : 'default'}
                  variant={formData.movement_type === type.value ? 'filled' : 'outlined'}
                  onClick={() => handleMovementTypeChange(type.value)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Grid>

          {/* Stock Information */}
          {stockItem && (
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Current Stock:</strong> {stockItem.current_stock} {stockItem.unit} | 
                  <strong> Location:</strong> {stockItem.storage_location || 'N/A'}
                </Typography>
              </Alert>
            </Grid>
          )}

          {/* Basic Movement Details */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Quantity"
              type="number"
              value={formData.quantity}
              onChange={(e) => handleInputChange('quantity', e.target.value)}
              inputProps={{ min: 0, step: 0.01 }}
              required
              helperText={stockItem ? `Unit: ${stockItem.unit}` : 'Enter quantity'}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Unit Price"
              type="number"
              value={formData.unit_price}
              onChange={(e) => handleInputChange('unit_price', e.target.value)}
              inputProps={{ min: 0, step: 0.01 }}
              helperText="Price per unit"
            />
          </Grid>

          {/* Reason for Movement */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required>
              <InputLabel>Reason</InputLabel>
              <Select
                value={formData.reason}
                onChange={(e) => handleInputChange('reason', e.target.value)}
                label="Reason"
              >
                {reasonOptions[formData.movement_type]?.map((reason) => (
                  <MenuItem key={reason} value={reason}>
                    {reason}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Reference Number */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Reference Number"
              value={formData.reference_number}
              onChange={(e) => handleInputChange('reference_number', e.target.value)}
              placeholder="PO#, Invoice#, etc."
              helperText="Optional reference for tracking"
            />
          </Grid>

          {/* Supplier/Customer based on movement type */}
          {(formData.movement_type === 'in' || formData.movement_type === 'out') && (
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={formData.movement_type === 'in' ? 'Supplier' : 'Customer'}
                value={formData.supplier_customer}
                onChange={(e) => handleInputChange('supplier_customer', e.target.value)}
                placeholder={formData.movement_type === 'in' ? 'Supplier name' : 'Customer name'}
              />
            </Grid>
          )}

          {/* Location Details */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="From Location"
              value={formData.location_from}
              onChange={(e) => handleInputChange('location_from', e.target.value)}
              disabled={formData.movement_type === 'in'}
              placeholder="Source location"
            />
          </Grid>

          {formData.movement_type === 'transfer' && (
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="To Location"
                value={formData.location_to}
                onChange={(e) => handleInputChange('location_to', e.target.value)}
                required
                placeholder="Destination location"
              />
            </Grid>
          )}

          {/* Additional Details */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Batch Number"
              value={formData.batch_number}
              onChange={(e) => handleInputChange('batch_number', e.target.value)}
              placeholder="Batch/Lot number"
            />
          </Grid>

          {formData.movement_type === 'in' && (
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Expiry Date"
                type="date"
                value={formData.expiry_date}
                onChange={(e) => handleInputChange('expiry_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                helperText="Optional for perishable items"
              />
            </Grid>
          )}

          {/* Notes */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              placeholder="Additional notes about this movement..."
            />
          </Grid>

          {/* Movement Summary */}
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" gutterBottom>
              Movement Summary
            </Typography>
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" color="text.secondary">
                    Type
                  </Typography>
                  <Chip 
                    label={currentMovementType?.label} 
                    color={currentMovementType?.color}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" color="text.secondary">
                    Quantity
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {formData.quantity || '0'} {stockItem?.unit || 'units'}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" color="text.secondary">
                    Unit Price
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    ₹{formData.unit_price || '0'}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="body2" color="text.secondary">
                    Total Value
                  </Typography>
                  <Typography variant="body1" fontWeight="medium" color="primary.main">
                    ₹{calculateTotalValue().toFixed(2)}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          </Grid>

          {/* Impact on Stock Level */}
          {stockItem && formData.quantity && (
            <Grid item xs={12}>
              <Alert 
                severity={
                  formData.movement_type === 'in' ? 'success' : 
                  formData.movement_type === 'out' ? 'warning' : 'info'
                }
              >
                <Typography variant="body2">
                  <strong>Stock Impact:</strong> Current stock will change from {stockItem.current_stock} to{' '}
                  {formData.movement_type === 'in' 
                    ? stockItem.current_stock + parseFloat(formData.quantity || 0)
                    : formData.movement_type === 'out'
                    ? stockItem.current_stock - parseFloat(formData.quantity || 0)
                    : stockItem.current_stock
                  } {stockItem.unit}
                </Typography>
              </Alert>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          color={currentMovementType?.color}
          disabled={
            !formData.quantity || 
            !formData.reason || 
            (formData.movement_type === 'transfer' && !formData.location_to)
          }
        >
          Record Movement
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default StockMovementDialog;
