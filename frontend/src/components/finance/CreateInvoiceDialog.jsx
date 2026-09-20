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
  IconButton,
  Divider
} from '@mui/material';
import { Add, Remove } from '@mui/icons-material';

const CreateInvoiceDialog = ({ open, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    customer_id: '',
    invoice_date: new Date().toISOString().split('T')[0],
    due_date: '',
    payment_terms: 'Net 30',
    items: [
      {
        description: '',
        quantity: 1,
        unit_price: 0,
        product_category: 'processed_rice'
      }
    ],
    notes: ''
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleItemChange = (index, field, value) => {
    const updatedItems = [...formData.items];
    updatedItems[index][field] = value;
    setFormData(prev => ({
      ...prev,
      items: updatedItems
    }));
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [
        ...prev.items,
        {
          description: '',
          quantity: 1,
          unit_price: 0,
          product_category: 'processed_rice'
        }
      ]
    }));
  };

  const removeItem = (index) => {
    if (formData.items.length > 1) {
      const updatedItems = formData.items.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        items: updatedItems
      }));
    }
  };

  const calculateTotal = () => {
    return formData.items.reduce((total, item) => {
      return total + (item.quantity * item.unit_price);
    }, 0);
  };

  const handleSubmit = () => {
    onSubmit(formData);
    onClose();
    // Reset form
    setFormData({
      customer_id: '',
      invoice_date: new Date().toISOString().split('T')[0],
      due_date: '',
      payment_terms: 'Net 30',
      items: [
        {
          description: '',
          quantity: 1,
          unit_price: 0,
          product_category: 'processed_rice'
        }
      ],
      notes: ''
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Invoice</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {/* Customer and Date Information */}
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Customer ID"
              type="number"
              value={formData.customer_id}
              onChange={(e) => handleInputChange('customer_id', e.target.value)}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Invoice Date"
              type="date"
              value={formData.invoice_date}
              onChange={(e) => handleInputChange('invoice_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
              required
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Due Date"
              type="date"
              value={formData.due_date}
              onChange={(e) => handleInputChange('due_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              select
              label="Payment Terms"
              value={formData.payment_terms}
              onChange={(e) => handleInputChange('payment_terms', e.target.value)}
            >
              <MenuItem value="Net 15">Net 15</MenuItem>
              <MenuItem value="Net 30">Net 30</MenuItem>
              <MenuItem value="Net 45">Net 45</MenuItem>
              <MenuItem value="Net 60">Net 60</MenuItem>
              <MenuItem value="Due on Receipt">Due on Receipt</MenuItem>
            </TextField>
          </Grid>

          {/* Invoice Items */}
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Invoice Items
            </Typography>
          </Grid>

          {formData.items.map((item, index) => (
            <Grid item xs={12} key={index}>
              <Box sx={{ border: '1px solid #ddd', p: 2, borderRadius: 1, mb: 2 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={4}>
                    <TextField
                      fullWidth
                      label="Description"
                      value={item.description}
                      onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                      helperText="Use a product name from Inventory (e.g. Basmati)"
                      required
                    />
                  </Grid>
                  <Grid item xs={6} sm={2}>
                    <TextField
                      fullWidth
                      label="Quantity"
                      type="number"
                      value={item.quantity}
                      onChange={(e) => handleItemChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                      inputProps={{ min: 0, step: 0.01 }}
                      required
                    />
                  </Grid>
                  <Grid item xs={6} sm={2}>
                    <TextField
                      fullWidth
                      label="Unit Price"
                      type="number"
                      value={item.unit_price}
                      onChange={(e) => handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                      inputProps={{ min: 0, step: 0.01 }}
                      required
                    />
                  </Grid>
                  <Grid item xs={8} sm={3}>
                    <TextField
                      fullWidth
                      select
                      label="Category"
                      value={item.product_category}
                      onChange={(e) => handleItemChange(index, 'product_category', e.target.value)}
                    >
                      <MenuItem value="raw_rice">Raw Rice</MenuItem>
                      <MenuItem value="processed_rice">Processed Rice</MenuItem>
                      <MenuItem value="premium_rice">Premium Rice</MenuItem>
                      <MenuItem value="broken_rice">Broken Rice</MenuItem>
                      <MenuItem value="rice_bran">Rice Bran</MenuItem>
                    </TextField>
                  </Grid>
                  <Grid item xs={4} sm={1}>
                    <IconButton
                      onClick={() => removeItem(index)}
                      disabled={formData.items.length === 1}
                      color="error"
                    >
                      <Remove />
                    </IconButton>
                  </Grid>
                </Grid>
                <Box sx={{ mt: 1, textAlign: 'right' }}>
                  <Typography variant="body2" color="text.secondary">
                    Line Total: ₹{(item.quantity * item.unit_price).toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          ))}

          <Grid item xs={12}>
            <Button
              startIcon={<Add />}
              onClick={addItem}
              variant="outlined"
              sx={{ mb: 2 }}
            >
              Add Item
            </Button>
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
              placeholder="Additional notes or terms..."
            />
          </Grid>

          {/* Total */}
          <Grid item xs={12}>
            <Box sx={{ textAlign: 'right', mt: 2 }}>
              <Typography variant="h6">
                Total Amount: ₹{calculateTotal().toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                (Excluding taxes)
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          disabled={!formData.customer_id || formData.items.some(item => !item.description)}
        >
          Create Invoice
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateInvoiceDialog;
