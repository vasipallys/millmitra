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
  Chip
} from '@mui/material';

const RecordPaymentDialog = ({ open, onClose, onSubmit, invoice = null }) => {
  const [formData, setFormData] = useState({
    invoice_id: invoice?.id || '',
    amount: invoice?.total_amount || '',
    payment_method: 'cash',
    payment_date: new Date().toISOString().split('T')[0],
    reference_number: '',
    notes: '',
    payment_type: 'full' // full, partial
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
    onClose();
    // Reset form
    setFormData({
      invoice_id: '',
      amount: '',
      payment_method: 'cash',
      payment_date: new Date().toISOString().split('T')[0],
      reference_number: '',
      notes: '',
      payment_type: 'full'
    });
  };

  const paymentMethods = [
    { value: 'cash', label: 'Cash' },
    { value: 'bank_transfer', label: 'Bank Transfer' },
    { value: 'cheque', label: 'Cheque' },
    { value: 'upi', label: 'UPI' },
    { value: 'card', label: 'Card Payment' },
    { value: 'online', label: 'Online Payment' }
  ];

  const getPaymentMethodColor = (method) => {
    const colors = {
      cash: 'success',
      bank_transfer: 'primary',
      cheque: 'warning',
      upi: 'info',
      card: 'secondary',
      online: 'default'
    };
    return colors[method] || 'default';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Record Payment</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Invoice Information */}
          {invoice && (
            <Grid item xs={12}>
              <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1, mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Invoice Details
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Invoice ID: {invoice.id}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Customer: {invoice.customer_name || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Amount: ₹{invoice.total_amount}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Outstanding: ₹{invoice.outstanding_amount || invoice.total_amount}
                </Typography>
              </Box>
            </Grid>
          )}

          {/* Invoice ID (if not pre-filled) */}
          {!invoice && (
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Invoice ID"
                type="number"
                value={formData.invoice_id}
                onChange={(e) => handleInputChange('invoice_id', e.target.value)}
                required
                helperText="Enter the invoice ID for this payment"
              />
            </Grid>
          )}

          {/* Payment Type */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Payment Type</InputLabel>
              <Select
                value={formData.payment_type}
                onChange={(e) => handleInputChange('payment_type', e.target.value)}
                label="Payment Type"
              >
                <MenuItem value="full">Full Payment</MenuItem>
                <MenuItem value="partial">Partial Payment</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Payment Amount */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Payment Amount"
              type="number"
              value={formData.amount}
              onChange={(e) => handleInputChange('amount', e.target.value)}
              inputProps={{ min: 0, step: 0.01 }}
              required
              helperText={formData.payment_type === 'partial' ? 'Enter partial amount' : 'Full invoice amount'}
            />
          </Grid>

          {/* Payment Method */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Payment Method</InputLabel>
              <Select
                value={formData.payment_method}
                onChange={(e) => handleInputChange('payment_method', e.target.value)}
                label="Payment Method"
              >
                {paymentMethods.map((method) => (
                  <MenuItem key={method.value} value={method.value}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip 
                        label={method.label} 
                        size="small" 
                        color={getPaymentMethodColor(method.value)}
                      />
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Payment Date */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Payment Date"
              type="date"
              value={formData.payment_date}
              onChange={(e) => handleInputChange('payment_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
              required
            />
          </Grid>

          {/* Reference Number */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Reference Number"
              value={formData.reference_number}
              onChange={(e) => handleInputChange('reference_number', e.target.value)}
              placeholder="Transaction ID, Cheque number, etc."
              helperText="Optional: Enter transaction reference for tracking"
            />
          </Grid>

          {/* Notes */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              placeholder="Additional payment notes..."
            />
          </Grid>

          {/* Payment Summary */}
          <Grid item xs={12}>
            <Box sx={{ p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Payment Summary
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Payment Amount:</Typography>
                <Typography variant="body2" fontWeight="bold">
                  ₹{formData.amount || '0.00'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Payment Method:</Typography>
                <Chip 
                  label={paymentMethods.find(m => m.value === formData.payment_method)?.label || 'Cash'} 
                  size="small"
                  color={getPaymentMethodColor(formData.payment_method)}
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Payment Type:</Typography>
                <Typography variant="body2" fontWeight="bold">
                  {formData.payment_type === 'full' ? 'Full Payment' : 'Partial Payment'}
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          disabled={!formData.amount || !formData.invoice_id}
        >
          Record Payment
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RecordPaymentDialog;
