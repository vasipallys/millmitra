import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, FormControl, InputLabel,
  Select, MenuItem, Box, Typography, Alert,
  Autocomplete, CircularProgress, Chip
} from '@mui/material';
// import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useQuery } from 'react-query';
import { farmerService } from '../../services/farmerService';

const validationSchema = Yup.object({
  farmer_id: Yup.number().required('Farmer selection is required'),
  crop_type: Yup.string().required('Crop type is required'),
  quantity_committed: Yup.number()
    .min(1, 'Quantity must be greater than 0')
    .required('Quantity committed is required'),
  base_price: Yup.number()
    .min(1, 'Price must be greater than 0')
    .required('Base price is required'),
  contract_start_date: Yup.date().required('Contract start date is required'),
  contract_end_date: Yup.date().required('Contract end date is required')
});

const CreateContractDialog = ({ open, onClose, onSubmit, loading = false }) => {
  const [aiOptimization, setAiOptimization] = useState(null);
  const [riskAssessment, setRiskAssessment] = useState(null);

  const { data: farmersData } = useQuery(
    'farmers-list',
    () => farmerService.getFarmers({ status: 'active' }),
    { enabled: open }
  );

  const formik = useFormik({
    initialValues: {
      farmer_id: '',
      crop_type: 'Basmati Rice',
      quantity_committed: '',
      base_price: '',
      quality_bonus: '',
      advance_amount: '',
      contract_start_date: new Date(),
      contract_end_date: null,
      terms_conditions: '',
      special_instructions: '',
      advance_payment_method: 'bank_transfer'
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const result = await onSubmit(values);
        setAiOptimization(result.optimization);
        setRiskAssessment(result.risk_assessment);
        if (result.success) {
          handleClose();
        }
      } catch (error) {
        console.error('Contract creation failed:', error);
      }
    }
  });

  const handleClose = () => {
    formik.resetForm();
    setAiOptimization(null);
    setRiskAssessment(null);
    onClose();
  };

  const paddyVarieties = [
    'IR64', 'Swarna', 'Sona Masuri', 'Basmati 1121', 'Pusa Basmati',
    'PR106', 'PR121', 'Sharbati', 'Sugandha', 'Kranti'
  ];

  const seasons = [
    { value: 'kharif', label: 'Kharif (Jun-Nov)' },
    { value: 'rabi', label: 'Rabi (Nov-Apr)' }
  ];

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Create Farmer Contract
      </DialogTitle>

      <DialogContent>
        {aiOptimization && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="subtitle2">AI Price Optimization</Typography>
            <Box sx={{ mt: 1 }}>
              Optimized Price: ₹{aiOptimization.optimized_price}/quintal
              {aiOptimization.recommendations?.map((rec, index) => (
                <Chip key={index} label={rec} size="small" sx={{ ml: 1 }} />
              ))}
            </Box>
          </Alert>
        )}

        {riskAssessment && (
          <Alert 
            severity={riskAssessment.risk_level === 'high' ? 'error' : 
                     riskAssessment.risk_level === 'medium' ? 'warning' : 'success'}
            sx={{ mb: 2 }}
          >
            <Typography variant="subtitle2">
              Risk Assessment: {riskAssessment.risk_level.toUpperCase()}
            </Typography>
            {riskAssessment.risk_factors?.length > 0 && (
              <Box sx={{ mt: 1 }}>
                Risk Factors: {riskAssessment.risk_factors.join(', ')}
              </Box>
            )}
          </Alert>
        )}

        <form onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            {/* Farmer Selection */}
            <Grid item xs={12}>
              <Autocomplete
                options={farmersData?.farmers || []}
                getOptionLabel={(option) => `${option.name} (${option.farmer_code}) - ${option.village}`}
                value={farmersData?.farmers?.find(f => f.id === formik.values.farmer_id) || null}
                onChange={(event, newValue) => {
                  formik.setFieldValue('farmer_id', newValue?.id || '');
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Farmer *"
                    error={formik.touched.farmer_id && Boolean(formik.errors.farmer_id)}
                    helperText={formik.touched.farmer_id && formik.errors.farmer_id}
                  />
                )}
              />
            </Grid>

            {/* Contract Details */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Season *</InputLabel>
                <Select
                  name="season"
                  value={formik.values.season}
                  onChange={formik.handleChange}
                  label="Season *"
                  error={formik.touched.season && Boolean(formik.errors.season)}
                >
                  {seasons.map((season) => (
                    <MenuItem key={season.value} value={season.value}>
                      {season.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="year"
                label="Year *"
                type="number"
                value={formik.values.year}
                onChange={formik.handleChange}
                error={formik.touched.year && Boolean(formik.errors.year)}
                helperText={formik.touched.year && formik.errors.year}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="crop_type"
                label="Crop Type *"
                value={formik.values.crop_type}
                onChange={formik.handleChange}
                error={formik.touched.crop_type && Boolean(formik.errors.crop_type)}
                helperText={formik.touched.crop_type && formik.errors.crop_type}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="quantity_committed"
                label="Quantity Committed (quintals) *"
                type="number"
                value={formik.values.quantity_committed}
                onChange={formik.handleChange}
                error={formik.touched.quantity_committed && Boolean(formik.errors.quantity_committed)}
                helperText={formik.touched.quantity_committed && formik.errors.quantity_committed}
              />
            </Grid>

            {/* Pricing */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="base_price"
                label="Base Price (₹/quintal) *"
                type="number"
                value={formik.values.base_price}
                onChange={formik.handleChange}
                error={formik.touched.base_price && Boolean(formik.errors.base_price)}
                helperText={formik.touched.base_price && formik.errors.base_price}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="quality_bonus"
                label="Quality Bonus (₹/quintal)"
                type="number"
                value={formik.values.quality_bonus}
                onChange={formik.handleChange}
              />
            </Grid>

            {/* Advance Payment */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="advance_amount"
                label="Advance Amount (₹)"
                type="number"
                value={formik.values.advance_amount}
                onChange={formik.handleChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Advance Payment Method</InputLabel>
                <Select
                  name="advance_payment_method"
                  value={formik.values.advance_payment_method}
                  onChange={formik.handleChange}
                  label="Advance Payment Method"
                >
                  <MenuItem value="bank_transfer">Bank Transfer</MenuItem>
                  <MenuItem value="cash">Cash</MenuItem>
                  <MenuItem value="cheque">Cheque</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Dates */}
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Contract Start Date"
                name="contract_start_date"
                type="date"
                value={formik.values.contract_start_date ? formik.values.contract_start_date.toISOString().split('T')[0] : ''}
                onChange={(e) => formik.setFieldValue('contract_start_date', new Date(e.target.value))}
                error={formik.touched.contract_start_date && Boolean(formik.errors.contract_start_date)}
                helperText={formik.touched.contract_start_date && formik.errors.contract_start_date}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contract End Date"
                name="contract_end_date"
                type="date"
                value={formik.values.contract_end_date ? formik.values.contract_end_date.toISOString().split('T')[0] : ''}
                onChange={(e) => formik.setFieldValue('contract_end_date', e.target.value ? new Date(e.target.value) : null)}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>

            {/* Terms and Conditions */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="terms_conditions"
                label="Terms & Conditions"
                multiline
                rows={3}
                value={formik.values.terms_conditions}
                onChange={formik.handleChange}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                name="special_instructions"
                label="Special Instructions"
                multiline
                rows={2}
                value={formik.values.special_instructions}
                onChange={formik.handleChange}
              />
            </Grid>
          </Grid>
        </form>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={formik.handleSubmit}
          disabled={loading}
          variant="contained"
          startIcon={loading && <CircularProgress size={20} />}
        >
          Create Contract
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CreateContractDialog;