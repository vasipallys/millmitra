import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, Grid, MenuItem, Box, Typography,
  Alert, Chip, Card, CardContent, Divider
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { productionAPI, inventoryAPI } from '../../services/api';
import ValidationErrorDisplay, { useValidation } from '../common/ValidationErrorDisplay';

const validationSchema = Yup.object({
  paddy_variety: Yup.string().required('Paddy variety is required'),
  input_quantity: Yup.number().positive('Must be positive').required('Input quantity is required'),
  target_rice_variety: Yup.string().required('Target rice variety is required'),
  planned_start_time: Yup.date().required('Planned start time is required'),
  priority: Yup.string().required('Priority is required')
});

const CreateBatchDialog = ({ open, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [aiRecommendations, setAiRecommendations] = useState(null);
  const [paddyStock, setPaddyStock] = useState([]);
  const [machineSettings, setMachineSettings] = useState({});
  const validation = useValidation();

  useEffect(() => {
    if (open) {
      loadPaddyStock();
    }
  }, [open]);

  const loadPaddyStock = async () => {
    try {
      const response = await inventoryAPI.getPaddyStock();
      setPaddyStock(response.data.stock);
    } catch (error) {
      console.error('Failed to load paddy stock:', error);
    }
  };

  const formik = useFormik({
    initialValues: {
      paddy_variety: '',
      input_quantity: '',
      input_source: 'procurement',
      source_reference_id: '',
      target_rice_variety: '',
      planned_start_time: new Date(),
      planned_end_time: null,
      priority: 'normal',
      supervisor_id: '',
      notes: ''
    },
    validationSchema,
    onSubmit: async (values) => {
      setLoading(true);
      try {
        const batchData = {
          ...values,
          machine_settings: machineSettings,
          planned_end_time: values.planned_end_time || 
            new Date(values.planned_start_time.getTime() + 8 * 60 * 60 * 1000) // Default 8 hours
        };

        const response = await productionAPI.createBatch(batchData);
        setAiRecommendations(response.data.ai_recommendations);
        
        if (response.data.success) {
          onSuccess();
          handleClose();
        }
      } catch (error) {
        console.error('Failed to create batch:', error);
      } finally {
        setLoading(false);
      }
    }
  });

  const handleClose = () => {
    formik.resetForm();
    setAiRecommendations(null);
    setMachineSettings({});
    onClose();
  };

  const handleVarietyChange = (variety) => {
    formik.setFieldValue('paddy_variety', variety);
    
    // Get AI recommendations for machine settings
    getAiRecommendations(variety, formik.values.input_quantity);
  };

  const getAiRecommendations = async (variety, quantity) => {
    if (!variety || !quantity) return;

    try {
      const response = await productionAPI.getAiRecommendations({
        paddy_variety: variety,
        input_quantity: quantity,
        target_rice_variety: formik.values.target_rice_variety
      });
      
      setAiRecommendations(response.data.recommendations);
      setMachineSettings(response.data.optimized_settings || {});
    } catch (error) {
      console.error('Failed to get AI recommendations:', error);
    }
  };

  const paddyVarieties = ['IR64', 'Swarna', 'Sona Masuri', 'Basmati 1121', 'Pusa Basmati'];
  const riceVarieties = ['White Rice', 'Parboiled Rice', 'Brown Rice', 'Basmati Rice'];
  const priorities = ['low', 'normal', 'high', 'urgent'];

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Production Batch</DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent>
          {/* Validation Error Display */}
          <ValidationErrorDisplay
            errors={validation.errors}
            warnings={validation.warnings}
            title="Production Batch Validation"
            onClose={() => validation.clearAll()}
          />

          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Paddy Variety"
                name="paddy_variety"
                value={formik.values.paddy_variety}
                onChange={(e) => handleVarietyChange(e.target.value)}
                error={formik.touched.paddy_variety && Boolean(formik.errors.paddy_variety)}
                helperText={formik.touched.paddy_variety && formik.errors.paddy_variety}
              >
                {paddyVarieties.map((variety) => (
                  <MenuItem key={variety} value={variety}>
                    {variety}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Input Quantity (Quintals)"
                name="input_quantity"
                type="number"
                value={formik.values.input_quantity}
                onChange={(e) => {
                  formik.handleChange(e);
                  getAiRecommendations(formik.values.paddy_variety, e.target.value);
                }}
                error={formik.touched.input_quantity && Boolean(formik.errors.input_quantity)}
                helperText={formik.touched.input_quantity && formik.errors.input_quantity}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Target Rice Variety"
                name="target_rice_variety"
                value={formik.values.target_rice_variety}
                onChange={formik.handleChange}
                error={formik.touched.target_rice_variety && Boolean(formik.errors.target_rice_variety)}
                helperText={formik.touched.target_rice_variety && formik.errors.target_rice_variety}
              >
                {riceVarieties.map((variety) => (
                  <MenuItem key={variety} value={variety}>
                    {variety}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Priority"
                name="priority"
                value={formik.values.priority}
                onChange={formik.handleChange}
                error={formik.touched.priority && Boolean(formik.errors.priority)}
                helperText={formik.touched.priority && formik.errors.priority}
              >
                {priorities.map((priority) => (
                  <MenuItem key={priority} value={priority}>
                    {priority.charAt(0).toUpperCase() + priority.slice(1)}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Scheduling */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Scheduling
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <DateTimePicker
                label="Planned Start Time"
                value={formik.values.planned_start_time}
                onChange={(value) => formik.setFieldValue('planned_start_time', value)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    fullWidth
                    error={formik.touched.planned_start_time && Boolean(formik.errors.planned_start_time)}
                    helperText={formik.touched.planned_start_time && formik.errors.planned_start_time}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <DateTimePicker
                label="Planned End Time (Optional)"
                value={formik.values.planned_end_time}
                onChange={(value) => formik.setFieldValue('planned_end_time', value)}
                renderInput={(params) => (
                  <TextField {...params} fullWidth />
                )}
              />
            </Grid>

            {/* Source Information */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Source Information
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Input Source"
                name="input_source"
                value={formik.values.input_source}
                onChange={formik.handleChange}
              >
                <MenuItem value="procurement">Fresh Procurement</MenuItem>
                <MenuItem value="inventory">Existing Stock</MenuItem>
              </TextField>
            </Grid>

            {formik.values.input_source === 'inventory' && (
              <Grid item xs={12} sm={6}>
                <TextField
                  select
                  fullWidth
                  label="Stock Reference"
                  name="source_reference_id"
                  value={formik.values.source_reference_id}
                  onChange={formik.handleChange}
                >
                  {paddyStock
                    .filter(stock => stock.variety === formik.values.paddy_variety)
                    .map((stock) => (
                      <MenuItem key={stock.id} value={stock.id}>
                        {stock.lot_number} - {stock.available_quantity}Q
                      </MenuItem>
                    ))}
                </TextField>
              </Grid>
            )}

            {/* Notes */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Production Notes"
                name="notes"
                value={formik.values.notes}
                onChange={formik.handleChange}
              />
            </Grid>

            {/* AI Recommendations */}
            {aiRecommendations && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      AI Recommendations
                    </Typography>
                    {aiRecommendations.map((recommendation, index) => (
                      <Alert key={index} severity="info" sx={{ mb: 1 }}>
                        {recommendation}
                      </Alert>
                    ))}
                    
                    {Object.keys(machineSettings).length > 0 && (
                      <Box mt={2}>
                        <Typography variant="subtitle2" gutterBottom>
                          Optimized Machine Settings:
                        </Typography>
                        <Box display="flex" flexWrap="wrap" gap={1}>
                          {Object.entries(machineSettings).map(([key, value]) => (
                            <Chip
                              key={key}
                              label={`${key}: ${value}`}
                              variant="outlined"
                              size="small"
                            />
                          ))}
                        </Box>
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
            {loading ? 'Creating...' : 'Create Batch'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default CreateBatchDialog;