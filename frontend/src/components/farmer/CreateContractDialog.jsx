import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, FormControl, InputLabel,
  Select, MenuItem, Box, Typography, Alert,
  Autocomplete, CircularProgress, Chip
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useQuery } from 'react-query';
import { farmerService } from '../../services/farmerService';

const validationSchema = Yup.object({
  farmer_id: Yup.number().required('Farmer selection is required'),
  season: Yup.string().required('Season is required'),
  year: Yup.number().required('Year is required'),
  paddy_variety: Yup.string().required('Paddy variety is required'),
  expected_quantity: Yup.number()
    .min(1, 'Quantity must be greater than 0')
    .required('Expected quantity is required'),
  base_price: Yup.number()
    .min(1, 'Price must be greater than 0')
    .required('Base price is required'),
  contract_date: Yup.date().required('Contract date is required')
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
      season: '',
      year: new Date().getFullYear(),
      paddy_variety: '',
      expected_quantity: '',
      base_price: '',
      quality_bonus: '',
      advance_amount: '',
      contract_date: new Date(),
      expected_delivery_start: null,
      expected_delivery_end: null,
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
        <Typography variant="h6">Create Farmer Contract</Typography>
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
              <Autocomplete
                options={paddyVarieties}
                value={formik.values.paddy_variety}
                onChange={(event, newValue) => {
                  formik.setFieldValue('paddy_variety', newValue || '');
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Paddy Variety *"
                    error={formik.touched.paddy_variety && Boolean(formik.errors.paddy_variety)}
                    helperText={formik.touched.paddy_variety && formik.errors.paddy_variety}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="expected_quantity"
                label="Expected Quantity (quintals) *"
                type="number"
                value={formik.values.expected_quantity}
                onChange={formik.handleChange}
                error={formik.touched.expected_quantity && Boolean(formik.errors.expected_quantity)}
                helperText={formik.touched.expected_quantity && formik.errors.expected_quantity}
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
              <DatePicker
                label="Contract Date *"
                value={formik.values.contract_date}
                onChange={(newValue) => formik.setFieldValue('contract_date', newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    fullWidth
                    error={formik.touched.contract_date && Boolean(formik.errors.contract_date)}
                    helperText={formik.touched.contract_date && formik.errors.contract_date}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <DatePicker
                label="Expected Delivery Start"
                value={formik.values.expected_delivery_start}
                onChange={(newValue) => formik.setFieldValue('expected_delivery_start', newValue)}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Grid>

            <Grid item xs={12} sm={4}>
              <DatePicker
                label="Expected Delivery End"
                value={formik.values.expected_delivery_end}
                onChange={(newValue) => formik.setFieldValue('expected_delivery_end', newValue)}
                renderInput={(params) => <TextField {...params} fullWidth />}
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