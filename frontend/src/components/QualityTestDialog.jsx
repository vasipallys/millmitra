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
  Chip,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent
} from '@mui/material';
import { Assignment, Science, CheckCircle } from '@mui/icons-material';
import { useI18n } from '../i18n/I18nContext';

const QualityTestDialog = ({ open, onClose, onSubmit, batch = null }) => {
  const { t } = useI18n();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    batch_id: batch?.id || batch?.batch_id || '',
    test_type: 'comprehensive',
    test_parameters: {
      moisture_content: '',
      broken_percentage: '',
      foreign_matter: '',
      chalky_kernels: '',
      grain_length: '',
      grain_width: '',
      color_uniformity: ''
    },
    test_conditions: {
      temperature: '',
      humidity: '',
      equipment_used: 'moisture_meter_1'
    },
    notes: '',
    tester_name: ''
  });

  const steps = [t('stepTestSetup'), t('stepMeasurements'), t('stepReviewSubmit')];

  const testTypes = [
    { value: 'comprehensive', label: t('testComprehensive') },
    { value: 'moisture_only', label: t('testMoistureOnly') },
    { value: 'physical_properties', label: t('testPhysical') },
    { value: 'visual_inspection', label: t('testVisual') },
    { value: 'custom', label: t('testCustom') }
  ];

  const equipmentOptions = [
    { value: 'moisture_meter_1', label: t('equipMoisture1') },
    { value: 'moisture_meter_2', label: t('equipMoisture2') },
    { value: 'grain_analyzer', label: t('equipGrainAnalyzer') },
    { value: 'color_sorter', label: t('equipColorSorter') },
    { value: 'manual_inspection', label: t('equipManual') }
  ];

  const handleInputChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleNext = () => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleSubmit = () => {
    onSubmit(formData);
    onClose();
    // Reset form
    setFormData({
      batch_id: '',
      test_type: 'comprehensive',
      test_parameters: {
        moisture_content: '',
        broken_percentage: '',
        foreign_matter: '',
        chalky_kernels: '',
        grain_length: '',
        grain_width: '',
        color_uniformity: ''
      },
      test_conditions: {
        temperature: '',
        humidity: '',
        equipment_used: 'moisture_meter_1'
      },
      notes: '',
      tester_name: ''
    });
    setActiveStep(0);
  };

  const getQualityGrade = () => {
    const { moisture_content, broken_percentage, foreign_matter } = formData.test_parameters;
    
    if (!moisture_content || !broken_percentage || !foreign_matter) return null;
    
    const moisture = parseFloat(moisture_content);
    const broken = parseFloat(broken_percentage);
    const foreign = parseFloat(foreign_matter);
    
    if (moisture <= 13 && broken <= 2 && foreign <= 0.5) return 'A+';
    if (moisture <= 14 && broken <= 3 && foreign <= 1) return 'A';
    if (moisture <= 15 && broken <= 5 && foreign <= 2) return 'B';
    return 'C';
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 2 }}>
                {t('testSetupHelp')}
              </Alert>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('batch')}
                value={formData.batch_id}
                onChange={(e) => handleInputChange('batch_id', e.target.value)}
                required
                disabled={!!batch}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('testType')}</InputLabel>
                <Select
                  value={formData.test_type}
                  onChange={(e) => handleInputChange('test_type', e.target.value)}
                  label={t('testType')}
                >
                  {testTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('testerName')}
                value={formData.tester_name}
                onChange={(e) => handleInputChange('tester_name', e.target.value)}
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('equipmentUsed')}</InputLabel>
                <Select
                  value={formData.test_conditions.equipment_used}
                  onChange={(e) => handleInputChange('test_conditions.equipment_used', e.target.value)}
                  label={t('equipmentUsed')}
                >
                  {equipmentOptions.map((equipment) => (
                    <MenuItem key={equipment.value} value={equipment.value}>
                      {equipment.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('temperatureC')}
                type="number"
                value={formData.test_conditions.temperature}
                onChange={(e) => handleInputChange('test_conditions.temperature', e.target.value)}
                inputProps={{ step: 0.1 }}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('humidityPct')}
                type="number"
                value={formData.test_conditions.humidity}
                onChange={(e) => handleInputChange('test_conditions.humidity', e.target.value)}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
              />
            </Grid>
          </Grid>
        );
        
      case 1:
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Alert severity="info" sx={{ mb: 2 }}>
                Enter the test measurements. All values should be accurate to ensure proper quality grading.
              </Alert>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('moisture')}
                type="number"
                value={formData.test_parameters.moisture_content}
                onChange={(e) => handleInputChange('test_parameters.moisture_content', e.target.value)}
                inputProps={{ min: 0, max: 25, step: 0.1 }}
                helperText="Acceptable range: 10-14%"
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('brokenGrains')}
                type="number"
                value={formData.test_parameters.broken_percentage}
                onChange={(e) => handleInputChange('test_parameters.broken_percentage', e.target.value)}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
                helperText="Acceptable range: 0-5%"
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('foreignMatter')}
                type="number"
                value={formData.test_parameters.foreign_matter}
                onChange={(e) => handleInputChange('test_parameters.foreign_matter', e.target.value)}
                inputProps={{ min: 0, max: 10, step: 0.1 }}
                helperText="Acceptable range: 0-1%"
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('chalkyGrains')}
                type="number"
                value={formData.test_parameters.chalky_kernels}
                onChange={(e) => handleInputChange('test_parameters.chalky_kernels', e.target.value)}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
                helperText="Acceptable range: 0-3%"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('grainLength')}
                type="number"
                value={formData.test_parameters.grain_length}
                onChange={(e) => handleInputChange('test_parameters.grain_length', e.target.value)}
                inputProps={{ min: 0, step: 0.1 }}
                helperText="Typical range: 5-7mm"
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('grainWidth')}
                type="number"
                value={formData.test_parameters.grain_width}
                onChange={(e) => handleInputChange('test_parameters.grain_width', e.target.value)}
                inputProps={{ min: 0, step: 0.1 }}
                helperText="Typical range: 2-3mm"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('colorUniformity')}
                type="number"
                value={formData.test_parameters.color_uniformity}
                onChange={(e) => handleInputChange('test_parameters.color_uniformity', e.target.value)}
                inputProps={{ min: 0, max: 100, step: 1 }}
                helperText="Score from 0-100 (100 = perfect uniformity)"
              />
            </Grid>
          </Grid>
        );
        
      case 2:
        const qualityGrade = getQualityGrade();
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Alert severity="success" sx={{ mb: 2 }}>
                Review the test results before submitting
              </Alert>
            </Grid>
            
            {/* Quality Grade Prediction */}
            {qualityGrade && (
              <Grid item xs={12}>
                <Card sx={{ bgcolor: 'primary.50', mb: 2 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <CheckCircle color="success" />
                      <Box>
                        <Typography variant="h6">
                          Predicted Quality Grade: {qualityGrade}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Based on moisture content, broken percentage, and foreign matter
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
            
            {/* Test Summary */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Test Summary
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Batch ID
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {formData.batch_id}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Test Type
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {testTypes.find(t => t.value === formData.test_type)?.label}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Tester
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {formData.tester_name}
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Equipment
              </Typography>
              <Typography variant="body1" fontWeight="medium">
                {equipmentOptions.find(e => e.value === formData.test_conditions.equipment_used)?.label}
              </Typography>
            </Grid>
            
            {/* Key Measurements */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Key Measurements
              </Typography>
            </Grid>
            
            {Object.entries(formData.test_parameters).map(([key, value]) => {
              if (!value) return null;
              return (
                <Grid item xs={12} sm={6} key={key}>
                  <Typography variant="body2" color="text.secondary">
                    {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {value}{key.includes('percentage') || key.includes('content') ? '%' : 
                           key.includes('length') || key.includes('width') ? 'mm' : ''}
                  </Typography>
                </Grid>
              );
            })}
            
            {/* Notes */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('additionalNotes')}
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Any additional observations or comments..."
              />
            </Grid>
          </Grid>
        );
        
      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Science color="primary" />
          {t('qualityTest')}
          {batch && (
            <Chip label={`${t('batch')}: ${batch.batch_id}`} color="primary" variant="outlined" />
          )}
        </Box>
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
        
        {renderStepContent(activeStep)}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>{t('cancel')}</Button>
        <Box sx={{ flex: '1 1 auto' }} />
        {activeStep > 0 && (
          <Button onClick={handleBack}>
            {t('back')}
          </Button>
        )}
        {activeStep < steps.length - 1 ? (
          <Button 
            onClick={handleNext} 
            variant="contained"
            disabled={
              (activeStep === 0 && (!formData.batch_id || !formData.tester_name)) ||
              (activeStep === 1 && (!formData.test_parameters.moisture_content || 
                                   !formData.test_parameters.broken_percentage || 
                                   !formData.test_parameters.foreign_matter))
            }
          >
            {t('next')}
          </Button>
        ) : (
          <Button onClick={handleSubmit} variant="contained">
            {t('submitTest')}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default QualityTestDialog;
