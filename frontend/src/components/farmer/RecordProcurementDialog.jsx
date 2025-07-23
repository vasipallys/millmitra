import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, FormControl, InputLabel,
  Select, MenuItem, Box, Typography, Alert,
  Autocomplete, CircularProgress, Card, CardContent
} from '@mui/material';
// import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useQuery } from 'react-query';
import { farmerService } from '../../services/farmerService';

const validationSchema = Yup.object({
  farmer_id: Yup.number().required('Farmer selection is required'),
  contract_id: Yup.number().nullable(), // Optional field
  procurement_date: Yup.date().required('Procurement date is required'),
  crop_type: Yup.string().required('Crop type is required'),
  paddy_variety: Yup.string().required('Paddy variety is required'),
  quantity: Yup.number()
    .min(0.1, 'Quantity must be greater than 0')
    .required('Quantity is required'),
  price_per_unit: Yup.number()
    .min(1, 'Price per unit must be greater than 0')
    .required('Price per unit is required'),
  base_price: Yup.number()
    .min(1, 'Base price must be greater than 0')
    .required('Base price is required'),
  moisture_content: Yup.number()
    .min(0)
    .max(30, 'Moisture content cannot exceed 30%')
    .required('Moisture content is required'),
  storage_location: Yup.string().required('Storage location is required')
});

const RecordProcurementDialog = ({ open, onClose, onSubmit, loading = false }) => {
  const [qualityAssessment, setQualityAssessment] = useState(null);
  const [pricingRecommendation, setPricingRecommendation] = useState(null);
  const [selectedFarmerId, setSelectedFarmerId] = useState('');

  const { data: farmersData } = useQuery(
    'farmers-list',
    () => farmerService.getFarmers({ status: 'active' }),
    { enabled: open }
  );

  const { data: contractsData } = useQuery(
    ['contracts', selectedFarmerId],
    () => farmerService.getContracts({
      farmer_id: selectedFarmerId,
      status: 'active'
    }),
    { enabled: open && !!selectedFarmerId }
  );

  const formik = useFormik({
    initialValues: {
      farmer_id: '',
      contract_id: '',
      crop_type: 'Basmati Rice',
      paddy_variety: '',
      procurement_date: new Date(),
      quantity: '',
      price_per_unit: '',
      base_price: '',
      moisture_content: '',
      foreign_matter: '',
      broken_grains: '',
      quality_grade: 'A',
      storage_location: 'Main Warehouse',
      vehicle_number: '',
      driver_name: '',
      inspector_notes: '',
      notes: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        console.log('Submitting procurement data:', values);

        // Format the data for backend
        const formattedValues = {
          ...values,
          procurement_date: values.procurement_date instanceof Date
            ? values.procurement_date.toISOString().split('T')[0]
            : values.procurement_date,
          farmer_id: parseInt(values.farmer_id),
          contract_id: values.contract_id ? parseInt(values.contract_id) : null,
          quantity: parseFloat(values.quantity),
          price_per_unit: parseFloat(values.price_per_unit),
          base_price: parseFloat(values.base_price),
          moisture_content: parseFloat(values.moisture_content || 0),
          foreign_matter: parseFloat(values.foreign_matter || 0),
          broken_grains: parseFloat(values.broken_grains || 0)
        };

        console.log('Formatted procurement data:', formattedValues);

        const result = await onSubmit(formattedValues);

        console.log('Procurement result:', result);

        // Handle AI responses if available
        if (result && typeof result === 'object') {
          if (result.quality_assessment) {
            setQualityAssessment(result.quality_assessment);
          }
          if (result.pricing_recommendation) {
            setPricingRecommendation(result.pricing_recommendation);
          }

          if (result.success) {
            handleClose();
          }
        } else {
          // If result is not an object or is undefined, assume success
          console.log('Procurement recording completed');
          handleClose();
        }
      } catch (error) {
        console.error('Procurement recording failed:', error);
        // You might want to show an error message to the user here
      }
    }
  });

  // Reset selectedFarmerId when dialog closes
  useEffect(() => {
    if (!open) {
      setSelectedFarmerId('');
    }
  }, [open]);

  // Debug form state (remove in production)
  useEffect(() => {
    if (Object.keys(formik.errors).length > 0) {
      console.log('Form validation errors:', formik.errors);
    }
  }, [formik.errors]);

  const handleClose = () => {
    formik.resetForm();
    setQualityAssessment(null);
    setPricingRecommendation(null);
    onClose();
  };

  const paddyVarieties = [
    'IR64', 'Swarna', 'Sona Masuri', 'Basmati 1121', 'Pusa Basmati',
    'PR106', 'PR121', 'Sharbati', 'Sugandha', 'Kranti'
  ];

  const storageLocations = [
    'Main Warehouse', 'Warehouse A', 'Warehouse B', 'Warehouse C',
    'Temporary Storage 1', 'Temporary Storage 2'
  ];

  // Calculate estimated quality score
  const calculateQualityScore = () => {
    const moisture = parseFloat(formik.values.moisture_content) || 14;
    const foreign = parseFloat(formik.values.foreign_matter) || 0;
    const broken = parseFloat(formik.values.broken_grains) || 0;

    const moistureScore = Math.max(0, 100 - (Math.abs(moisture - 14) * 5));
    const foreignScore = Math.max(0, 100 - (foreign * 10));
    const brokenScore = Math.max(0, 100 - (broken * 8));

    return Math.round((moistureScore + foreignScore + brokenScore) / 3);
  };

  const getQualityGrade = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    return 'D';
  };

  const estimatedScore = calculateQualityScore();
  const estimatedGrade = getQualityGrade(estimatedScore);

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        Record Paddy Procurement
      </DialogTitle>

      <DialogContent>
        {qualityAssessment && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="subtitle2">AI Quality Assessment</Typography>
            <Box sx={{ mt: 1 }}>
              Grade: {qualityAssessment.grade} | Score: {qualityAssessment.score}/100
              {qualityAssessment.bonus_rate > 0 && (
                <Typography variant="body2" color="success.main">
                  Quality Bonus: ₹{qualityAssessment.bonus_rate}/quintal
                </Typography>
              )}
              {qualityAssessment.penalty_rate > 0 && (
                <Typography variant="body2" color="error.main">
                  Quality Penalty: ₹{qualityAssessment.penalty_rate}/quintal
                </Typography>
              )}
            </Box>
          </Alert>
        )}

        {pricingRecommendation && (
          <Alert severity="success" sx={{ mb: 2 }}>
            <Typography variant="subtitle2">AI Price Recommendation</Typography>
            <Typography variant="body2">
              Recommended Price: ₹{pricingRecommendation.recommended_price}/quintal
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {pricingRecommendation.reasoning}
            </Typography>
          </Alert>
        )}

        <form id="procurement-form" onSubmit={formik.handleSubmit}>
          <Grid container spacing={3}>
            {/* Farmer and Contract Selection */}
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={farmersData?.farmers || []}
                getOptionLabel={(option) => `${option.name} (${option.farmer_code})`}
                value={farmersData?.farmers?.find(f => f.id === formik.values.farmer_id) || null}
                onChange={(event, newValue) => {
                  const farmerId = newValue?.id || '';
                  formik.setFieldValue('farmer_id', farmerId);
                  setSelectedFarmerId(farmerId);
                  formik.setFieldValue('contract_id', ''); // Reset contract selection
                }}
                isOptionEqualToValue={(option, value) => option?.id === value?.id}
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

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Contract (Optional)</InputLabel>
                <Select
                  name="contract_id"
                  value={formik.values.contract_id}
                  onChange={formik.handleChange}
                  label="Contract (Optional)"
                  disabled={!formik.values.farmer_id}
                >
                  <MenuItem value="">No Contract</MenuItem>
                  {contractsData?.contracts?.map((contract) => (
                    <MenuItem key={contract.id} value={contract.id}>
                      {contract.contract_number} - {contract.paddy_variety}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Procurement Details */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Procurement Date"
                name="procurement_date"
                type="date"
                value={formik.values.procurement_date ? formik.values.procurement_date.toISOString().split('T')[0] : ''}
                onChange={(e) => formik.setFieldValue('procurement_date', new Date(e.target.value))}
                error={formik.touched.procurement_date && Boolean(formik.errors.procurement_date)}
                helperText={formik.touched.procurement_date && formik.errors.procurement_date}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <Autocomplete
                options={paddyVarieties}
                value={formik.values.paddy_variety || null}
                onChange={(event, newValue) => {
                  formik.setFieldValue('paddy_variety', newValue || '');
                }}
                isOptionEqualToValue={(option, value) => option === value}
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

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="quantity"
                label="Quantity (quintals) *"
                type="number"
                value={formik.values.quantity}
                onChange={formik.handleChange}
                error={formik.touched.quantity && Boolean(formik.errors.quantity)}
                helperText={formik.touched.quantity && formik.errors.quantity}
              />
            </Grid>

            {/* Quality Parameters */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Quality Parameters
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="moisture_content"
                label="Moisture Content (%)"
                type="number"
                inputProps={{ step: 0.1, min: 0, max: 100 }}
                value={formik.values.moisture_content || ''}
                onChange={formik.handleChange}
                error={formik.touched.moisture_content && Boolean(formik.errors.moisture_content)}
                helperText={formik.touched.moisture_content && formik.errors.moisture_content}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="foreign_matter"
                label="Foreign Matter (%)"
                type="number"
                inputProps={{ step: 0.1, min: 0, max: 100 }}
                value={formik.values.foreign_matter || ''}
                onChange={formik.handleChange}
                error={formik.touched.foreign_matter && Boolean(formik.errors.foreign_matter)}
                helperText={formik.touched.foreign_matter && formik.errors.foreign_matter}
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                name="broken_grains"
                label="Broken Grains (%)"
                type="number"
                inputProps={{ step: 0.1, min: 0, max: 100 }}
                value={formik.values.broken_grains || ''}
                onChange={formik.handleChange}
                error={formik.touched.broken_grains && Boolean(formik.errors.broken_grains)}
                helperText={formik.touched.broken_grains && formik.errors.broken_grains}
              />
            </Grid>

            {/* Quality Preview */}
            {(formik.values.moisture_content || formik.values.foreign_matter || formik.values.broken_grains) && (
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      Estimated Quality Assessment
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Typography variant="body2">
                        Grade: <strong>{estimatedGrade}</strong>
                      </Typography>
                      <Typography variant="body2">
                        Score: <strong>{estimatedScore}/100</strong>
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Pricing */}
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="price_per_unit"
                label="Price per Unit (₹/quintal) *"
                type="number"
                value={formik.values.price_per_unit || ''}
                onChange={formik.handleChange}
                error={formik.touched.price_per_unit && Boolean(formik.errors.price_per_unit)}
                helperText={formik.touched.price_per_unit && formik.errors.price_per_unit}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="base_price"
                label="Base Price (₹/quintal) *"
                type="number"
                value={formik.values.base_price || ''}
                onChange={formik.handleChange}
                error={formik.touched.base_price && Boolean(formik.errors.base_price)}
                helperText={formik.touched.base_price && formik.errors.base_price}
              />
            </Grid>

            {/* Logistics */}
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={storageLocations}
                value={formik.values.storage_location || null}
                onChange={(event, newValue) => {
                  formik.setFieldValue('storage_location', newValue || '');
                }}
                isOptionEqualToValue={(option, value) => option === value}
                renderInput={(params) => (
                  <TextField {...params} label="Storage Location" />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="vehicle_number"
                label="Vehicle Number"
                value={formik.values.vehicle_number || ''}
                onChange={formik.handleChange}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="driver_name"
                label="Driver Name"
                value={formik.values.driver_name || ''}
                onChange={formik.handleChange}
              />
            </Grid>

            {/* Notes */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="inspector_notes"
                label="Inspector Notes"
                multiline
                rows={3}
                value={formik.values.inspector_notes || ''}
                onChange={formik.handleChange}
              />
            </Grid>
          </Grid>
        </form>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          type="submit"
          form="procurement-form"
          disabled={loading || !formik.isValid}
          variant="contained"
          startIcon={loading && <CircularProgress size={20} />}
        >
          Record Procurement
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RecordProcurementDialog;