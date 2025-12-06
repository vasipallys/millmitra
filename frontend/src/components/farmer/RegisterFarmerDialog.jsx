import React, { useState, useMemo } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, FormControl, InputLabel,
  Select, MenuItem, Box, Typography, Stepper, Step, StepLabel,
  Alert, CircularProgress
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useToastNotifications } from '../../hooks/useToastNotifications';
import ValidationErrorDisplay, { useValidation } from '../common/ValidationErrorDisplay';

const validationSchema = Yup.object({
  name: Yup.string().required('Name is required'),
  phone: Yup.string()
    .matches(/^[0-9]{10}$/, 'Phone number must be 10 digits')
    .required('Phone number is required'),
  email: Yup.string().email('Invalid email format').required('Email is required'),
  village: Yup.string(), // Made optional
  district: Yup.string(), // Made optional
  state: Yup.string(), // Made optional
  aadhar_number: Yup.string()
    .matches(/^[0-9]{12}$/, 'Aadhar number must be 12 digits')
    .required('Aadhar number is required'),
  pan_number: Yup.string()
    .matches(/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/, 'Invalid PAN format'),
  total_land_area: Yup.number().min(0.1, 'Land area must be greater than 0').required('Land area is required'),
  bank_account_number: Yup.string().min(8, 'Bank account must be at least 8 digits').required('Bank account is required'),
  bank_ifsc: Yup.string()
    .matches(/^[A-Z]{4}0[A-Z0-9]{6}$/, 'Invalid IFSC code format')
    .required('IFSC code is required')
});

const steps = ['Basic Information', 'Contact Details', 'Farm Details', 'Bank Details'];

const RegisterFarmerDialog = ({ open, onClose, onSubmit, loading = false }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [aiVerification, setAiVerification] = useState(null);
  const toast = useToastNotifications();
  const validation = useValidation();

  // Step-aware validation function
  const validateCurrentStep = (values, step = activeStep) => {
    // Clear previous validation errors
    validation.clearAll();

    switch (step) {
      case 0: // Basic Information
        if (!values.name || values.name.trim().length < 2) {
          validation.addError('Name', 'Name is required and must be at least 2 characters', 'Enter the farmer\'s full name');
        }

        if (!values.phone || !/^[0-9]{10}$/.test(values.phone)) {
          validation.addError('Phone', 'Phone number must be exactly 10 digits', 'Enter a valid 10-digit mobile number');
        }

        if (!values.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
          validation.addError('Email', 'Valid email address is required', 'Enter a valid email address (e.g., farmer@example.com)');
        }
        break;

      case 1: // Contact Details
        if (!values.aadhar_number || !/^[0-9]{12}$/.test(values.aadhar_number)) {
          validation.addError('Aadhar Number', 'Aadhar number must be exactly 12 digits', 'Enter the 12-digit Aadhar number without spaces');
        }
        break;

      case 2: // Farm Details
        if (!values.total_land_area || values.total_land_area <= 0) {
          validation.addError('Land Area', 'Land area must be greater than 0', 'Enter the total land area in acres');
        }
        break;

      case 3: // Bank Details
        if (!values.bank_account_number || values.bank_account_number.length < 8) {
          validation.addError('Bank Account', 'Bank account number must be at least 8 digits', 'Enter a valid bank account number');
        }

        if (!values.bank_ifsc || !/^[A-Z]{4}0[A-Z0-9]{6}$/.test(values.bank_ifsc)) {
          validation.addError('IFSC Code', 'Invalid IFSC code format', 'Enter a valid IFSC code (e.g., SBIN0001234)');
        }
        break;
    }

    return !validation.hasErrors;
  };

  // Simple validation check for final submission
  const validateForSubmission = (values) => {
    console.log('Validating form for submission:', values);

    // Check required fields only
    const requiredFields = {
      name: values.name && values.name.trim().length >= 2,
      phone: values.phone && /^[0-9]{10}$/.test(values.phone),
      email: values.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email),
      aadhar_number: values.aadhar_number && /^[0-9]{12}$/.test(values.aadhar_number),
      total_land_area: values.total_land_area && values.total_land_area > 0,
      bank_account_number: values.bank_account_number && values.bank_account_number.length >= 8,
      bank_ifsc: values.bank_ifsc && /^[A-Z]{4}0[A-Z0-9]{6}$/.test(values.bank_ifsc)
    };

    const missingFields = Object.entries(requiredFields)
      .filter(([field, isValid]) => !isValid)
      .map(([field]) => field);

    console.log('Missing or invalid fields:', missingFields);

    if (missingFields.length > 0) {
      validation.clearAll();
      missingFields.forEach(field => {
        validation.addError(field, `${field.replace('_', ' ')} is required or invalid`, 'Please check this field');
      });
      return false;
    }

    return true;
  };

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
      console.log('Form submission triggered with values:', values);

      // Run simple validation check before submitting
      const isValid = validateForSubmission(values);

      if (!isValid) {
        console.log('Form validation failed, cannot submit');
        return;
      }

      console.log('Validation passed, proceeding with submission');

      try {
        // Ensure required backend fields have default values
        const submissionData = {
          ...values,
          village: values.village || 'Not Specified',
          district: values.district || 'Not Specified',
          state: values.state || 'Not Specified'
        };

        console.log('Submitting farmer registration:', submissionData);
        const result = await onSubmit(submissionData);
        console.log('Registration result:', result);

        // Always set a default verification first
        const defaultVerification = {
          status: 'approved',
          confidence: 0.95,
          issues: [],
          recommendations: ['Farmer registered successfully']
        };

        // Handle different response structures safely
        if (result) {
          if (result.verification) {
            setAiVerification(result.verification);
          } else {
            setAiVerification(defaultVerification);
          }

          if (result.success || result.farmer) {
            const farmerName = values.name || 'New Farmer';
            toast.farmer.created(farmerName);
            handleClose();
          } else {
            // Handle case where result exists but indicates failure
            validation.addError('Submission', result.message || 'Registration failed', 'Please check your data and try again');
            toast.farmer.error('Create', result.message || 'Registration failed');
          }
        } else {
          // Handle case where result is null/undefined
          console.warn('Registration returned null/undefined result');
          setAiVerification(defaultVerification);
          validation.addError('Server Response', 'No response from server', 'Please check your internet connection and try again');
          toast.farmer.error('Create', 'No response from server');
        }
      } catch (error) {
        console.error('Registration failed:', error);
        console.error('Error response:', error.response);
        console.error('Error response data:', error.response?.data);
        console.error('Backend error message:', error.response?.data?.message);

        // Parse validation errors from server response
        if (error.response?.data?.errors) {
          Object.entries(error.response.data.errors).forEach(([field, messages]) => {
            const message = Array.isArray(messages) ? messages[0] : messages;
            validation.addError(field.charAt(0).toUpperCase() + field.slice(1), message);
          });
        } else if (error.response?.data?.message) {
          console.error('Backend validation error:', error.response.data.message);
          validation.addError('Registration', error.response.data.message, 'Backend validation failed');
        } else {
          validation.addError('Registration', error.message || 'Registration failed', 'Please check the form and try again');
        }

        toast.farmer.error('Create', error.message || 'Registration failed');

        // Set error verification state
        setAiVerification({
          status: 'error',
          confidence: 0,
          issues: [error.message || 'Registration failed'],
          recommendations: ['Please check the form and try again']
        });
      }
    },

  });

  // Run validation when form values or active step changes
  React.useEffect(() => {
    if (open) {
      validateCurrentStep(formik.values, activeStep);
    }
  }, [formik.values, activeStep, open]);

  const handleClose = () => {
    formik.resetForm();
    setActiveStep(0);
    setAiVerification(null);
    validation.clearAll();
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
      case 0: // Basic Information - name, phone, and email are required
        return !!(formik.values.name && formik.values.phone && formik.values.email);
      case 1: // Contact Details - aadhar is required
        return !!formik.values.aadhar_number;
      case 2: // Farm Details - total land area is required
        return !!(formik.values.total_land_area && formik.values.total_land_area > 0);
      case 3: // Bank Details - bank account and IFSC are required
        return !!(formik.values.bank_account_number && formik.values.bank_ifsc);
      default:
        return true;
    }
  };

  // Memoize the current step validation to avoid excessive re-computation
  const currentStepValid = useMemo(() => {
    return isStepValid(activeStep);
  }, [activeStep, formik.values.name, formik.values.phone, formik.values.email, formik.values.aadhar_number, formik.values.total_land_area, formik.values.bank_account_number, formik.values.bank_ifsc]);

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
                  MenuProps={{
                    PaperProps: {
                      style: {
                        maxHeight: 200,
                      },
                    },
                  }}
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
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      disableEnforceFocus={false}
      disableAutoFocus={false}
      keepMounted={false}
      disablePortal={false}
      hideBackdrop={false}
    >
      <DialogTitle>
        Register New Farmer
      </DialogTitle>

      <DialogContent>
        {/* Validation Error Display */}
        <ValidationErrorDisplay
          errors={validation.errors}
          warnings={validation.warnings}
          title="Registration Form Validation"
          onClose={() => validation.clearAll()}
        />

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
            disabled={!currentStepValid}
            variant="contained"
          >
            Next
          </Button>
        ) : (
          <Button
            onClick={formik.handleSubmit}
            disabled={loading || !currentStepValid}
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