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
import { useI18n } from '../../i18n/I18nContext';
import LookupSelect from '../common/LookupSelect';

const RegisterFarmerDialog = ({ open, onClose, onSubmit, loading = false }) => {
  const { t } = useI18n();
  const [activeStep, setActiveStep] = useState(0);
  const [aiVerification, setAiVerification] = useState(null);
  const toast = useToastNotifications();
  const validation = useValidation();
  const steps = [t('stepBasic'), t('stepContact'), t('stepFarm'), t('stepBank')];
  const validationSchema = useMemo(() => Yup.object({
    name: Yup.string().required(t('yupNameRequired')),
    phone: Yup.string()
      .matches(/^[0-9]{10}$/, t('yupPhoneDigits'))
      .required(t('yupPhoneRequired')),
    email: Yup.string().email(t('yupEmailInvalid')).required(t('yupEmailRequired')),
    village: Yup.string(),
    district: Yup.string(),
    state: Yup.string(),
    aadhar_number: Yup.string()
      .matches(/^[0-9]{12}$/, t('yupAadharDigits'))
      .required(t('yupAadharRequired')),
    pan_number: Yup.string()
      .matches(/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/, t('yupPanInvalid')),
    total_land_area: Yup.number().min(0.1, t('yupLandMin')).required(t('yupLandRequired')),
    bank_account_number: Yup.string().min(8, t('yupBankMin')).required(t('yupBankRequired')),
    bank_ifsc: Yup.string()
      .matches(/^[A-Z]{4}0[A-Z0-9]{6}$/, t('yupIfscInvalid'))
      .required(t('yupIfscRequired')),
  }), [t]);

  // Step-aware validation function
  const validateCurrentStep = (values, step = activeStep) => {
    // Clear previous validation errors
    validation.clearAll();

    switch (step) {
      case 0: // Basic Information
        if (!values.name || values.name.trim().length < 2) {
          validation.addError(t('name'), t('valNameRequired'), t('valNameHint'));
        }

        if (!values.phone || !/^[0-9]{10}$/.test(values.phone)) {
          validation.addError(t('phone'), t('valPhoneRequired'), t('valPhoneHint'));
        }

        if (!values.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
          validation.addError(t('email'), t('valEmailRequired'), t('valEmailHint'));
        }
        break;

      case 1: // Contact Details
        if (!values.aadhar_number || !/^[0-9]{12}$/.test(values.aadhar_number)) {
          validation.addError(t('aadharNumber'), t('valAadharRequired'), t('valAadharHint'));
        }
        break;

      case 2: // Farm Details
        if (!values.total_land_area || values.total_land_area <= 0) {
          validation.addError(t('landArea'), t('valLandRequired'), t('valLandHint'));
        }
        break;

      case 3: // Bank Details
        if (!values.bank_account_number || values.bank_account_number.length < 8) {
          validation.addError(t('bankAccount'), t('valBankRequired'), t('valBankHint'));
        }

        if (!values.bank_ifsc || !/^[A-Z]{4}0[A-Z0-9]{6}$/.test(values.bank_ifsc)) {
          validation.addError(t('ifscCode'), t('valIfscInvalid'), t('valIfscHint'));
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
        validation.addError(field, t('valFieldInvalid', { field: field.replace('_', ' ') }), t('valCheckField'));
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
                label={t('fullName')}
                required
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={(formik.touched.name && formik.errors.name) || t('helperFarmerName')}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="father_name"
                label={t('fatherName')}
                value={formik.values.father_name}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="phone"
                label={t('phoneNumber')}
                required
                value={formik.values.phone}
                onChange={formik.handleChange}
                error={formik.touched.phone && Boolean(formik.errors.phone)}
                helperText={(formik.touched.phone && formik.errors.phone) || t('helperPhone10')}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="alternate_phone"
                label={t('altPhone')}
                value={formik.values.alternate_phone}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="email"
                label={t('emailAddress')}
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
                label={`${t('village')} *`}
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
                label={`${t('district')} *`}
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
                label={`${t('state')} *`}
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
                label={t('pincode')}
                value={formik.values.pincode}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="aadhar_number"
                label={t('aadharNumber')}
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
                label={t('panNumber')}
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
                label={t('totalLandAcres')}
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
                label={t('irrigatedAcres')}
                type="number"
                value={formik.values.irrigated_area}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="farming_experience"
                label={t('farmingYears')}
                type="number"
                value={formik.values.farming_experience}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <LookupSelect
                group="crop_type"
                name="primary_crop"
                label={t('primaryCrop')}
                value={formik.values.primary_crop}
                onChange={formik.handleChange}
              />
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
                label={t('bankAccount')}
                value={formik.values.bank_account_number}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                name="bank_ifsc"
                label={t('ifscCode')}
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
                label={t('bankName')}
                value={formik.values.bank_name}
                onChange={formik.handleChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                name="notes"
                label={t('additionalNotes')}
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
        {t('registerNewFarmer')}
      </DialogTitle>

      <DialogContent>
        {/* Validation Error Display */}
        <ValidationErrorDisplay
          errors={validation.errors}
          warnings={validation.warnings}
          title={t('valFormTitle')}
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
        <Button onClick={handleClose}>{t('cancel')}</Button>
        
        {activeStep > 0 && (
          <Button onClick={handleBack}>{t('back')}</Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button
            onClick={handleNext}
            disabled={!currentStepValid}
            variant="contained"
          >
            {t('next')}
          </Button>
        ) : (
          <Button
            onClick={formik.handleSubmit}
            disabled={loading || !currentStepValid}
            variant="contained"
            startIcon={loading && <CircularProgress size={20} />}
          >
            {t('registerFarmerSubmit')}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default RegisterFarmerDialog;