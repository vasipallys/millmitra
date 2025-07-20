import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, FormControl, InputLabel,
  Select, MenuItem, Box, Typography, Stepper, Step, StepLabel,
  Alert, CircularProgress
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';

const validationSchema = Yup.object({
  name: Yup.string().required('Name is required'),
  phone: Yup.string()
    .matches(/^[0-9]{10}$/, 'Phone number must be 10 digits')
    .required('Phone number is required'),
  village: Yup.string().required('Village is required'),
  district: Yup.string().required('District is required'),
  state: Yup.string().required('State is required'),
  aadhar_number: Yup.string()
    .matches(/^[0-9]{12}$/, 'Aadhar number must be 12 digits'),
  pan_number: Yup.string()
    .matches(/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/, 'Invalid PAN format'),
  total_land_area: Yup.number().min(0, 'Land area must be positive'),
  bank_account_number: Yup.string(),
  bank_ifsc: Yup.string()
    .matches(/^[A-Z]{4}0[A-Z0-9]{6}$/, 'Invalid IFSC code format')
});

const steps = ['Basic Information', 'Contact Details', 'Farm Details', 'Bank Details'];

const RegisterFarmerDialog = ({ open, onClose, onSubmit, loading = false }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [aiVerification, setAiVerification] = useState(null);

  const formik = useFormik({
    initialValues: {
      name: '',
      father_name: '',
      phone: '',
      alternate_phone: '',
      email: '',
      aadhar_number: '',
      pan_number: '',
      village: '',
      district: '',
      state: '',
      pincode: '',
      total_land_area: '',
      irrigated_area: '',
      farming_experience: '',
      primary_crop: 'paddy',
      bank_account_number: '',
      bank_ifsc: '',
      bank_name: '',
      notes: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      try {
        const result = await onSubmit(values);
        setAiVerification(result.verification);
        if (result.success) {
          handleClose();
        }
      } catch (error) {
        console.error('Registration failed:', error);
      }
    }
  });

  const handleClose = () => {
    formik.resetForm();
    setActiveStep(0);
    setAiVerification(null);
    onClose();
  };

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const isStepValid = (step) => {
    switch (step) {
      case 0:
        return formik.values.name && formik.values.phone && formik.values.village;
      case 1:
        return !formik.errors.phone && !formik.errors.aadhar_number;
      case 2:
        return !formik.errors.total_land_area;
      case 3:
        return !formik.errors.bank_ifsc;
      default:
        return true;
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="name"
                label="Full Name *"
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="father_name"
                label="Father's Name"
                value={formik.values.father_name}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="phone"
                label="Phone Number *"
                value={formik.values.phone}
                onChange={formik.handleChange}
                error={formik.touched.phone && Boolean(formik.errors.phone)}
                helperText={formik.touched.phone && formik.errors.phone}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="alternate_phone"
                label="Alternate Phone"
                value={formik.values.alternate_phone}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="email"
                label="Email Address"
                type="email"
                value={formik.values.email}
                onChange={formik.handleChange}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="village"
                label="Village *"
                value={formik.values.village}
                onChange={formik.handleChange}
                error={formik.touched.village && Boolean(formik.errors.village)}
                helperText={formik.touched.village && formik.errors.village}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="district"
                label="District *"
                value={formik.values.district}
                onChange={formik.handleChange}
                error={formik.touched.district && Boolean(formik.errors.district)}
                helperText={formik.touched.district && formik.errors.district}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="state"
                label="State *"
                value={formik.values.state}
                onChange={formik.handleChange}
                error={formik.touched.state && Boolean(formik.errors.state)}
                helperText={formik.touched.state && formik.errors.state}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="pincode"
                label="Pincode"
                value={formik.values.pincode}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="aadhar_number"
                label="Aadhar Number"
                value={formik.values.aadhar_number}
                onChange={formik.handleChange}
                error={formik.touched.aadhar_number && Boolean(formik.errors.aadhar_number)}
                helperText={formik.touched.aadhar_number && formik.errors.aadhar_number}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="pan_number"
                label="PAN Number"
                value={formik.values.pan_number}
                onChange={formik.handleChange}
                error={formik.touched.pan_number && Boolean(formik.errors.pan_number)}
                helperText={formik.touched.pan_number && formik.errors.pan_number}
              />
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="total_land_area"
                label="Total Land Area (acres)"
                type="number"
                value={formik.values.total_land_area}
                onChange={formik.handleChange}
                error={formik.touched.total_land_area && Boolean(formik.errors.total_land_area)}
                helperText={formik.touched.total_land_area && formik.errors.total_land_area}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="irrigated_area"
                label="Irrigated Area (acres)"
                type="number"
                value={formik.values.irrigated_area}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="farming_experience"
                label="Farming Experience (years)"
                type="number"
                value={formik.values.farming_experience}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Primary Crop</InputLabel>
                <Select
                  name="primary_crop"
                  value={formik.values.primary_crop}
                  onChange={formik.handleChange}
                  label="Primary Crop"
                >
                  <MenuItem value="paddy">Paddy</MenuItem>
                  <MenuItem value="wheat">Wheat</MenuItem>
                  <MenuItem value="sugarcane">Sugarcane</MenuItem>
                  <MenuItem value="cotton">Cotton</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="bank_account_number"
                label="Bank Account Number"
                value={formik.values.bank_account_number}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="bank_ifsc"
                label="IFSC Code"
                value={formik.values.bank_ifsc}
                onChange={formik.handleChange}
                error={formik.touched.bank_ifsc && Boolean(formik.errors.bank_ifsc)}
                helperText={formik.touched.bank_ifsc && formik.errors.bank_ifsc}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="bank_name"
                label="Bank Name"
                value={formik.values.bank_name}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="notes"
                label="Additional Notes"
                multiline
                rows={3}
                value={formik.values.notes}
                onChange={formik.handleChange}
              />
            </Grid>
          </Grid>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6">Register New Farmer</Typography>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Stepper activeStep={activeStep} alternativeLabel>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>

        {aiVerification && (
          <Alert 
            severity={aiVerification.status === 'verified' ? 'success' : 'warning'}
            sx={{ mb: 2 }}
          >
            AI Verification: {aiVerification.status} (Score: {aiVerification.score}/100)
            {aiVerification.issues?.length > 0 && (
              <Box sx={{ mt: 1 }}>
                Issues: {aiVerification.issues.join(', ')}
              </Box>
            )}
          </Alert>
        )}

        <form onSubmit={formik.handleSubmit}>
          {renderStepContent(activeStep)}
        </form>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        
        {activeStep > 0 && (
          <Button onClick={handleBack}>Back</Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button
            onClick={handleNext}
            disabled={!isStepValid(activeStep)}
            variant="contained"
          >
            Next
          </Button>
        ) : (
          <Button
            onClick={formik.handleSubmit}
            disabled={loading || !isStepValid(activeStep)}
            variant="contained"
            startIcon={loading && <CircularProgress size={20} />}
          >
            Register Farmer
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default RegisterFarmerDialog;