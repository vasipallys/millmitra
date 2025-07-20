import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, MenuItem, Box, Typography,
  Card, CardContent, Alert, Chip, Divider
} from '@mui/material';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { productionAPI } from '../../services/api';

const validationSchema = Yup.object({
  test_type: Yup.string().required('Test type is required'),
  moisture_content: Yup.number().min(0).max(30).required('Moisture content is required'),
  broken_grains: Yup.number().min(0).max(100).required('Broken grains percentage is required'),
  foreign_matter: Yup.number().min(0).max(100).required('Foreign matter percentage is required')
});

const QualityTestDialog = ({ open, onClose, batch, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [estimatedGrade, setEstimatedGrade] = useState(null);

  const formik = useFormik({
    initialValues: {
      batch_id: batch?.id || '',
      test_type: 'intermediate',
      test_stage: '',
      sample_size: 1.0,
      moisture_content: '',
      broken_grains: '',
      foreign_matter: '',
      chalky_grains: '',
      head_rice_recovery: '',
      milling_degree: '',
      whiteness_index: '',
      transparency: '',
      grain_length: '',
      grain_width: '',
      test_method: 'manual',
      notes: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      setLoading(true);
      try {
        const response = await productionAPI.createQualityTest({
          ...values,
          batch_id: batch.id
        });
        
        setAiAnalysis(response.data.ai_analysis);
        
        if (response.data.success) {
          onSuccess();
        }
      } catch (error) {
        console.error('Failed to create quality test:', error);
      } finally {
        setLoading(false);
      }
    }
  });

  const handleClose = () => {
    formik.resetForm();
    setAiAnalysis(null);
    setEstimatedGrade(null);
    onClose();
  };

  // Calculate estimated quality score in real-time
  const calculateEstimatedScore = () => {
    const moisture = parseFloat(formik.values.moisture_content) || 14;
    const broken = parseFloat(formik.values.broken_grains) || 0;
    const foreign = parseFloat(formik.values.foreign_matter) || 0;

    let score = 100;

    // Moisture content penalty (optimal: 12-14%)
    if (moisture < 12 || moisture > 14) {
      score -= Math.abs(moisture - 13) * 2;
    }

    // Broken grains penalty
    score -= broken * 1.5;

    // Foreign matter penalty
    score -= foreign * 3;

    return Math.max(0, Math.min(100, score));
  };

  const getEstimatedGrade = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    return 'D';
  };

  const estimatedScore = calculateEstimatedScore();
  const currentGrade = getEstimatedGrade(estimatedScore);

  const testTypes = ['input', 'intermediate', 'final'];
  const testStages = ['cleaning', 'dehusking', 'polishing', 'sorting', 'packaging'];
  const testMethods = ['manual', 'automated', 'ai'];

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Create Quality Test - {batch?.batch_number}</DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent>
          <Grid container spacing={3}>
            {/* Test Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Test Information
              </Typography>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                label="Test Type"
                name="test_type"
                value={formik.values.test_type}
                onChange={formik.handleChange}
                error={formik.touched.test_type && Boolean(formik.errors.test_type)}
                helperText={formik.touched.test_type && formik.errors.test_type}
              >
                {testTypes.map((type) => (
                  <MenuItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                label="Test Stage"
                name="test_stage"
                value={formik.values.test_stage}
                onChange={formik.handleChange}
              >
                {testStages.map((stage) => (
                  <MenuItem key={stage} value={stage}>
                    {stage.charAt(0).toUpperCase() + stage.slice(1)}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Sample Size (kg)"
                name="sample_size"
                type="number"
                value={formik.values.sample_size}
                onChange={formik.handleChange}
                inputProps={{ step: 0.1, min: 0.1 }}
              />
            </Grid>

            {/* Quality Parameters */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Quality Parameters
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Moisture Content (%)"
                name="moisture_content"
                type="number"
                value={formik.values.moisture_content}
                onChange={formik.handleChange}
                error={formik.touched.moisture_content && Boolean(formik.errors.moisture_content)}
                helperText={formik.touched.moisture_content && formik.errors.moisture_content}
                inputProps={{ step: 0.1, min: 0, max: 30 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Broken Grains (%)"
                name="broken_grains"
                type="number"
                value={formik.values.broken_grains}
                onChange={formik.handleChange}
                error={formik.touched.broken_grains && Boolean(formik.errors.broken_grains)}
                helperText={formik.touched.broken_grains && formik.errors.broken_grains}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Foreign Matter (%)"
                name="foreign_matter"
                type="number"
                value={formik.values.foreign_matter}
                onChange={formik.handleChange}
                error={formik.touched.foreign_matter && Boolean(formik.errors.foreign_matter)}
                helperText={formik.touched.foreign_matter && formik.errors.foreign_matter}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Chalky Grains (%)"
                name="chalky_grains"
                type="number"
                value={formik.values.chalky_grains}
                onChange={formik.handleChange}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Head Rice Recovery (%)"
                name="head_rice_recovery"
                type="number"
                value={formik.values.head_rice_recovery}
                onChange={formik.handleChange}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Milling Degree"
                name="milling_degree"
                type="number"
                value={formik.values.milling_degree}
                onChange={formik.handleChange}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>

            {/* Physical Properties */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Physical Properties
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Whiteness Index"
                name="whiteness_index"
                type="number"
                value={formik.values.whiteness_index}
                onChange={formik.handleChange}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Transparency"
                name="transparency"
                type="number"
                value={formik.values.transparency}
                onChange={formik.handleChange}
                inputProps={{ step: 0.1, min: 0, max: 100 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Grain Length (mm)"
                name="grain_length"
                type="number"
                value={formik.values.grain_length}
                onChange={formik.handleChange}
                inputProps={{ step: 0.1, min: 0 }}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Grain Width (mm)"
                name="grain_width"
                type="number"
                value={formik.values.grain_width}
                onChange={formik.handleChange}
                inputProps={{ step: 0.1, min: 0 }}
              />
            </Grid>

            {/* Test Method and Notes */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Test Details
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Test Method"
                name="test_method"
                value={formik.values.test_method}
                onChange={formik.handleChange}
              >
                {testMethods.map((method) => (
                  <MenuItem key={method} value={method}>
                    {method.charAt(0).toUpperCase() + method.slice(1)}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Test Notes"
                name="notes"
                value={formik.values.notes}
                onChange={formik.handleChange}
              />
            </Grid>

            {/* Real-time Quality Estimation */}
            {(formik.values.moisture_content || formik.values.broken_grains || formik.values.foreign_matter) && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Estimated Quality Assessment
                    </Typography>
                    <Box display="flex" alignItems="center" gap={2} mb={2}>
                      <Typography variant="h4">
                        {Math.round(estimatedScore)}%
                      </Typography>
                      <Chip
                        label={`Grade ${currentGrade}`}
                        color={
                          currentGrade === 'A' ? 'success' :
                          currentGrade === 'B' ? 'info' :
                          currentGrade === 'C' ? 'warning' : 'error'
                        }
                        size="large"
                      />
                    </Box>
                    <Typography variant="body2" color="textSecondary">
                      This is a preliminary estimate based on entered parameters.
                      Final grade will be calculated after AI analysis.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* AI Analysis Results */}
            {aiAnalysis && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      AI Analysis Results
                    </Typography>
                    {aiAnalysis.recommendations?.map((recommendation, index) => (
                      <Alert key={index} severity="info" sx={{ mb: 1 }}>
                        {recommendation}
                      </Alert>
                    ))}
                    
                    {aiAnalysis.confidence && (
                      <Box mt={2}>
                        <Typography variant="body2" color="textSecondary">
                          AI Confidence: {Math.round(aiAnalysis.confidence * 100)}%
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Creating Test...' : 'Create Test'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default QualityTestDialog;