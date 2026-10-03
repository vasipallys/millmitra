import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, MenuItem, Box, Alert,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Chip, Typography, LinearProgress
} from '@mui/material';
import { Add, Delete } from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { salesAPI } from '../../services/api';
import { useI18n } from '../../i18n/I18nContext';

const validationSchema = Yup.object({
  customer_id: Yup.number().required('Customer is required'),
  delivery_date: Yup.date().required('Delivery date is required'),
  items: Yup.array().min(1, 'At least one item is required')
});

const CreateSalesOrderDialog = ({ open, onClose, onSubmit }) => {
  const { t } = useI18n();
  const [customers, setCustomers] = useState([]);
  const [aiInsights, setAiInsights] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      fetchCustomers();
    }
  }, [open]);

  const fetchCustomers = async () => {
    try {
      const response = await salesAPI.getCustomers();
      setCustomers(response.data.customers);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  const formik = useFormik({
    initialValues: {
      customer_id: '',
      delivery_date: '',
      order_type: 'standard',
      payment_terms: 'cash',
      delivery_address: '',
      items: [
        {
          product_name: '',
          product_variety: '',
          product_grade: 'A',
          quantity: '',
          unit: 'quintal',
          unit_price: ''
        }
      ]
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setLoading(true);
        const result = await onSubmit(values);
        setAiInsights(result.ai_insights);
        if (result.success) {
          handleClose();
        }
      } catch (error) {
        console.error('Order creation failed:', error);
      } finally {
        setLoading(false);
      }
    }
  });

  const handleClose = () => {
    formik.resetForm();
    setAiInsights(null);
    onClose();
  };

  const addItem = () => {
    const newItem = {
      product_name: '',
      product_variety: '',
      product_grade: 'A',
      quantity: '',
      unit: 'quintal',
      unit_price: ''
    };
    formik.setFieldValue('items', [...formik.values.items, newItem]);
  };

  const removeItem = (index) => {
    const items = formik.values.items.filter((_, i) => i !== index);
    formik.setFieldValue('items', items);
  };

  const updateItem = (index, field, value) => {
    const items = [...formik.values.items];
    items[index][field] = value;
    formik.setFieldValue('items', items);
  };

  const calculateTotal = () => {
    return formik.values.items.reduce((total, item) => {
      return total + (parseFloat(item.quantity || 0) * parseFloat(item.unit_price || 0));
    }, 0);
  };

  const orderTypes = [
    { value: 'standard', label: t('orderStandard') },
    { value: 'urgent', label: t('orderUrgent') },
    { value: 'export', label: t('orderExport') }
  ];

  const paymentTerms = [
    { value: 'cash', label: t('payCash') },
    { value: 'credit_15', label: t('credit15') },
    { value: 'credit_30', label: t('credit30') },
    { value: 'credit_60', label: t('credit60') }
  ];

  const productGrades = ['A', 'B', 'C'];
  const units = ['quintal', 'kg', 'ton'];

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>{t('createSalesOrder')}</DialogTitle>
      
      <form onSubmit={formik.handleSubmit}>
        <DialogContent>
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          
          {/* AI Insights Display */}
          {aiInsights && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                🤖 AI Order Insights
              </Typography>
              
              {aiInsights.fulfillment_prediction && (
                <Box mb={1}>
                  <Chip 
                    label={`Fulfillment: ${aiInsights.fulfillment_prediction.estimated_fulfillment_days} days`}
                    color="primary"
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip 
                    label={`Probability: ${aiInsights.fulfillment_prediction.fulfillment_probability}%`}
                    color="success"
                    size="small"
                  />
                </Box>
              )}
              
              {aiInsights.risk_assessment && (
                <Box mb={1}>
                  <Chip 
                    label={`Risk Level: ${aiInsights.risk_assessment.risk_level}`}
                    color={aiInsights.risk_assessment.risk_level === 'low' ? 'success' : 
                           aiInsights.risk_assessment.risk_level === 'medium' ? 'warning' : 'error'}
                    size="small"
                  />
                </Box>
              )}
              
              {aiInsights.recommendations?.map((rec, index) => (
                <Typography key={index} variant="body2">
                  • {rec}
                </Typography>
              ))}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Order Information */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                name="customer_id"
                label={t('customer')}
                value={formik.values.customer_id}
                onChange={formik.handleChange}
                error={formik.touched.customer_id && Boolean(formik.errors.customer_id)}
                helperText={formik.touched.customer_id && formik.errors.customer_id}
                required
              >
                {customers.map((customer) => (
                  <MenuItem key={customer.id} value={customer.id}>
                    {customer.name} ({customer.customer_code})
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="delivery_date"
                label={t('deliveryDate')}
                type="date"
                value={formik.values.delivery_date}
                onChange={formik.handleChange}
                error={formik.touched.delivery_date && Boolean(formik.errors.delivery_date)}
                helperText={formik.touched.delivery_date && formik.errors.delivery_date}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                name="order_type"
                label={t('orderType')}
                value={formik.values.order_type}
                onChange={formik.handleChange}
              >
                {orderTypes.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                select
                name="payment_terms"
                label={t('paymentTerms')}
                value={formik.values.payment_terms}
                onChange={formik.handleChange}
              >
                {paymentTerms.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="delivery_address"
                label={t('deliveryAddress')}
                multiline
                rows={2}
                value={formik.values.delivery_address}
                onChange={formik.handleChange}
              />
            </Grid>

            {/* Order Items */}
            <Grid item xs={12}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">{t('orderItems')}</Typography>
                <Button
                  startIcon={<Add />}
                  onClick={addItem}
                  variant="outlined"
                  size="small"
                >
                  {t('addItem')}
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('product')}</TableCell>
                      <TableCell>{t('variety')}</TableCell>
                      <TableCell>{t('grade')}</TableCell>
                      <TableCell>{t('quantity')}</TableCell>
                      <TableCell>{t('unit')}</TableCell>
                      <TableCell>{t('unitPrice')}</TableCell>
                      <TableCell>{t('totalAmount')}</TableCell>
                      <TableCell>{t('actions')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {formik.values.items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <TextField
                            size="small"
                            value={item.product_name}
                            onChange={(e) => updateItem(index, 'product_name', e.target.value)}
                            placeholder={t('productNamePh')}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            value={item.product_variety}
                            onChange={(e) => updateItem(index, 'product_variety', e.target.value)}
                            placeholder={t('variety')}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            select
                            value={item.product_grade}
                            onChange={(e) => updateItem(index, 'product_grade', e.target.value)}
                          >
                            {productGrades.map((grade) => (
                              <MenuItem key={grade} value={grade}>
                                {grade}
                              </MenuItem>
                            ))}
                          </TextField>
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={item.quantity}
                            onChange={(e) => updateItem(index, 'quantity', e.target.value)}
                            placeholder="0"
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            select
                            value={item.unit}
                            onChange={(e) => updateItem(index, 'unit', e.target.value)}
                          >
                            {units.map((unit) => (
                              <MenuItem key={unit} value={unit}>
                                {unit}
                              </MenuItem>
                            ))}
                          </TextField>
                        </TableCell>
                        <TableCell>
                          <TextField
                            size="small"
                            type="number"
                            value={item.unit_price}
                            onChange={(e) => updateItem(index, 'unit_price', e.target.value)}
                            placeholder="0"
                          />
                        </TableCell>
                        <TableCell>
                          ₹{(parseFloat(item.quantity || 0) * parseFloat(item.unit_price || 0)).toFixed(2)}
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            onClick={() => removeItem(index)}
                            disabled={formik.values.items.length === 1}
                          >
                            <Delete />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell colSpan={6} align="right">
                        <Typography variant="h6">{t('totalAmount')}:</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="h6">
                          ₹{calculateTotal().toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell />
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose}>{t('cancel')}</Button>
          <Button 
            type="submit" 
            variant="contained"
            disabled={loading}
          >
            {t('createOrder')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateSalesOrderDialog;