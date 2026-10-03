import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, MenuItem, Box, Alert,
  Chip, Typography, LinearProgress
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useI18n } from '../../i18n/I18nContext';
import LookupSelect from '../common/LookupSelect';

const validationSchema = Yup.object({
  name: Yup.string().required('Customer name is required'),
  customer_type: Yup.string().required('Customer type is required'),
  email: Yup.string().email('Invalid email'),
  phone: Yup.string().required('Phone number is required'),
  credit_limit: Yup.number().min(0, 'Credit limit must be positive')
});

const CreateCustomerDialog = ({ open, onClose, onSubmit }) => {
  const { t } = useI18n();
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const formik = useFormik({
    initialValues: {
      name: '',
      company_name: '',
      customer_type: 'retail',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      pincode: '',
      gst_number: '',
      pan_number: '',
      credit_limit: 0,
      payment_terms: 'cash'
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        setLoading(true);
        const result = await onSubmit(values);
        setAiAnalysis(result.ai_analysis);
        if (result.success) {
          handleClose();
        }
      } catch (error) {
        console.error('Customer creation failed:', error);
      } finally {
        setLoading(false);
      }
    }
  });

  const handleClose = () => {
    formik.resetForm();
    setAiAnalysis(null);
    onClose();
  };

  const customerTypes = [
    { value: 'retail', label: t('typeRetail') },
    { value: 'wholesale', label: t('typeWholesale') },
    { value: 'distributor', label: t('typeDistributor') },
    { value: 'export', label: t('typeExport') }
  ];

  const paymentTerms = [
    { value: 'cash', label: t('payCash') },
    { value: 'credit_15', label: t('credit15') },
    { value: 'credit_30', label: t('credit30') },
    { value: 'credit_60', label: t('credit60') }
  ];

  const getRiskColor = (rating) => {
    switch (rating) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>{t('createCustomer')}</DialogTitle>
      
      <form onSubmit={formik.handleSubmit}>
        <DialogContent>
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          
          {/* AI Analysis Display */}
          {aiAnalysis && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                🤖 AI Customer Analysis
              </Typography>
              <Box display="flex" gap={1} mb={1}>
                <Chip 
                  label={`Score: ${aiAnalysis.customer_score}/100`}
                  color="primary"
                  size="small"
                />
                <Chip 
                  label={`Risk: ${aiAnalysis.risk_rating}`}
                  color={getRiskColor(aiAnalysis.risk_rating)}
                  size="small"
                />
              </Box>
              {aiAnalysis.recommendations?.map((rec, index) => (
                <Typography key={index} variant="body2">
                  • {rec}
                </Typography>
              ))}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                {t('basicInfo')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="name"
                label={t('customerName')}
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="company_name"
                label={t('companyName')}
                value={formik.values.company_name}
                onChange={formik.handleChange}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <LookupSelect
                group="customer_type"
                name="customer_type"
                label={t('customerType')}
                value={formik.values.customer_type}
                onChange={formik.handleChange}
                required
                error={formik.touched.customer_type && Boolean(formik.errors.customer_type)}
                helperText={formik.touched.customer_type && formik.errors.customer_type}
              />
            </Grid>

            {/* Contact Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                {t('contactInfo')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="email"
                label={t('email')}
                type="email"
                value={formik.values.email}
                onChange={formik.handleChange}
                error={formik.touched.email && Boolean(formik.errors.email)}
                helperText={formik.touched.email && formik.errors.email}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="phone"
                label={t('phoneNumber')}
                value={formik.values.phone}
                onChange={formik.handleChange}
                error={formik.touched.phone && Boolean(formik.errors.phone)}
                helperText={formik.touched.phone && formik.errors.phone}
                required
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="address"
                label={t('address')}
                multiline
                rows={2}
                value={formik.values.address}
                onChange={formik.handleChange}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="city"
                label={t('city')}
                value={formik.values.city}
                onChange={formik.handleChange}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="state"
                label={t('state')}
                value={formik.values.state}
                onChange={formik.handleChange}
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="pincode"
                label={t('pincode')}
                value={formik.values.pincode}
                onChange={formik.handleChange}
              />
            </Grid>

            {/* Business Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                {t('businessInfo')}
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="gst_number"
                label={t('gstNumber')}
                value={formik.values.gst_number}
                onChange={formik.handleChange}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="pan_number"
                label={t('panNumber')}
                value={formik.values.pan_number}
                onChange={formik.handleChange}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="credit_limit"
                label={t('creditLimit')}
                type="number"
                value={formik.values.credit_limit}
                onChange={formik.handleChange}
                error={formik.touched.credit_limit && Boolean(formik.errors.credit_limit)}
                helperText={formik.touched.credit_limit && formik.errors.credit_limit}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <LookupSelect
                group="payment_terms"
                name="payment_terms"
                label={t('paymentTerms')}
                value={formik.values.payment_terms}
                onChange={formik.handleChange}
              />
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
            {t('createCustomer')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateCustomerDialog;