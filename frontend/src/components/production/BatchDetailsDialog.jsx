import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Grid, Typography, Box, Chip, Card, CardContent,
  Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, LinearProgress, Tabs, Tab, Alert,
  IconButton, Divider
} from '@mui/material';
import {
  PlayArrow, Pause, Stop, Add, Edit, Assessment,
  Timeline, QualityControl, Settings
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import { productionAPI } from '../../services/api';
import { useI18n } from '../../i18n/I18nContext';
import AddProductionStepDialog from './AddProductionStepDialog';
import QualityTestDialog from './QualityTestDialog';

const BatchDetailsDialog = ({ open, onClose, batch, onUpdate }) => {
  const { t, statusLabel } = useI18n();
  const [tabValue, setTabValue] = useState(0);
  const [batchDetails, setBatchDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [addStepOpen, setAddStepOpen] = useState(false);
  const [qualityTestOpen, setQualityTestOpen] = useState(false);
  const [viewStep, setViewStep] = useState(null);
  const [viewTest, setViewTest] = useState(null);

  useEffect(() => {
    if (open && batch) {
      loadBatchDetails();
    }
  }, [open, batch]);

  const loadBatchDetails = async () => {
    if (!batch) return;
    
    setLoading(true);
    try {
      const response = await productionAPI.getBatchDetails(batch.id);
      setBatchDetails(response.data);
    } catch (error) {
      console.error('Failed to load batch details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchAction = async (action) => {
    try {
      await productionAPI.batchAction(batch.id, action);
      loadBatchDetails();
      onUpdate();
    } catch (error) {
      console.error(`Failed to ${action} batch:`, error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'planned': 'default',
      'in_progress': 'primary',
      'paused': 'warning',
      'completed': 'success',
      'cancelled': 'error'
    };
    return colors[status] || 'default';
  };

  const getStepStatusColor = (status) => {
    const colors = {
      'pending': 'default',
      'in_progress': 'primary',
      'completed': 'success',
      'failed': 'error',
      'paused': 'warning'
    };
    return colors[status] || 'default';
  };

  const calculateProgress = () => {
    if (!batchDetails?.steps?.length) return 0;
    
    const completedSteps = batchDetails.steps.filter(step => step.status === 'completed').length;
    return (completedSteps / batchDetails.steps.length) * 100;
  };

  const renderOverviewTab = () => (
    <Grid container spacing={3}>
      {/* Basic Information */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Batch Information
            </Typography>
            <Box display="flex" flexDirection="column" gap={1}>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="textSecondary">Batch Number:</Typography>
                <Typography variant="body2">{batchDetails.batch.batch_number}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="textSecondary">Paddy Variety:</Typography>
                <Typography variant="body2">{batchDetails.batch.paddy_variety}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="textSecondary">Input Quantity:</Typography>
                <Typography variant="body2">{batchDetails.batch.input_quantity} Q</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="textSecondary">Status:</Typography>
                <Chip
                  label={statusLabel(batchDetails.batch.status)}
                  color={getStatusColor(batchDetails.batch.status)}
                  size="small"
                />
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2" color="textSecondary">Priority:</Typography>
                <Chip
                  label={batchDetails.batch.priority}
                  variant="outlined"
                  size="small"
                />
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Progress and Metrics */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Progress & Metrics
            </Typography>
            <Box mb={2}>
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Overall Progress
              </Typography>
              <LinearProgress
                variant="determinate"
                value={calculateProgress()}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="textSecondary" align="center" mt={1}>
                {Math.round(calculateProgress())}% Complete
              </Typography>
            </Box>
            
            {batchDetails.batch.efficiency_score && (
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  Efficiency Score: {batchDetails.batch.efficiency_score}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={batchDetails.batch.efficiency_score}
                  color={batchDetails.batch.efficiency_score >= 80 ? 'success' : 'warning'}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            )}

            {batchDetails.batch.yield_percentage && (
              <Box>
                <Typography variant="body2" color="textSecondary">
                  Yield: {batchDetails.batch.yield_percentage}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={batchDetails.batch.yield_percentage}
                  color="info"
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* AI Insights */}
      {batchDetails.ai_insights && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Insights
              </Typography>
              {batchDetails.ai_insights.recommendations?.map((insight, index) => (
                <Alert key={index} severity="info" sx={{ mb: 1 }}>
                  {insight}
                </Alert>
              ))}
              
              {batchDetails.ai_insights.predictions && (
                <Box mt={2}>
                  <Typography variant="subtitle2" gutterBottom>
                    Predictions:
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(batchDetails.ai_insights.predictions).map(([key, value]) => (
                      <Grid item xs={6} sm={4} key={key}>
                        <Box textAlign="center">
                          <Typography variant="h6">{value}</Typography>
                          <Typography variant="body2" color="textSecondary">
                            {key.replace('_', ' ').toUpperCase()}
                          </Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      )}
    </Grid>
  );

  const renderStepsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Production Steps</Typography>
        {batchDetails.batch.status === 'in_progress' && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddStepOpen(true)}
          >
            Add Step
          </Button>
        )}
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Step</TableCell>
              <TableCell>Order</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Input Qty</TableCell>
              <TableCell>Output Qty</TableCell>
              <TableCell>Efficiency</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {batchDetails.steps?.map((step) => (
              <TableRow key={step.id}>
                <TableCell>{step.step_name}</TableCell>
                <TableCell>{step.step_order}</TableCell>
                <TableCell>
                  <Chip
                    label={step.status}
                    color={getStepStatusColor(step.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {step.actual_duration ? `${step.actual_duration} min` : 
                   step.expected_duration ? `${step.expected_duration} min (est)` : 'N/A'}
                </TableCell>
                <TableCell>{step.input_quantity || 'N/A'}</TableCell>
                <TableCell>{step.output_quantity || 'N/A'}</TableCell>
                <TableCell>
                  {step.step_efficiency ? `${step.step_efficiency}%` : 'N/A'}
                </TableCell>
                <TableCell>
                  <IconButton size="small" aria-label="View production step" onClick={() => setViewStep(step)}>
                    <Edit />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderQualityTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Quality Tests</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setQualityTestOpen(true)}
        >
          Add Test
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Test Number</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Stage</TableCell>
              <TableCell>Grade</TableCell>
              <TableCell>Score</TableCell>
              <TableCell>Pass/Fail</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {batchDetails.quality_tests?.map((test) => (
              <TableRow key={test.id}>
                <TableCell>{test.test_number}</TableCell>
                <TableCell>{test.test_type}</TableCell>
                <TableCell>{test.test_stage || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={test.overall_grade}
                    color={test.overall_grade === 'A' ? 'success' : 
                           test.overall_grade === 'B' ? 'info' :
                           test.overall_grade === 'C' ? 'warning' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{test.quality_score}%</TableCell>
                <TableCell>
                  <Chip
                    label={test.pass_fail ? 'Pass' : 'Fail'}
                    color={test.pass_fail ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(test.test_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <IconButton size="small" aria-label="View quality test" onClick={() => setViewTest(test)}>
                    <Assessment />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  if (!batch || !batchDetails) {
    return null;
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            Batch Details - {batchDetails.batch.batch_number}
          </Typography>
          <Box>
            {batchDetails.batch.status === 'planned' && (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={() => handleBatchAction('start')}
                sx={{ mr: 1 }}
              >
                Start
              </Button>
            )}
            {batchDetails.batch.status === 'in_progress' && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<Pause />}
                  onClick={() => handleBatchAction('pause')}
                  sx={{ mr: 1 }}
                >
                  Pause
                </Button>
                <Button
                  variant="contained"
                  startIcon={<Stop />}
                  onClick={() => handleBatchAction('complete')}
                  sx={{ mr: 1 }}
                >
                  Complete
                </Button>
              </>
            )}
            {batchDetails.batch.status === 'paused' && (
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={() => handleBatchAction('resume')}
                sx={{ mr: 1 }}
              >
                Resume
              </Button>
            )}
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label={t('overview')} icon={<Assessment />} />
          <Tab label={t('steps')} icon={<Timeline />} />
          <Tab label={t('quality')} icon={<QualityControl />} />
        </Tabs>

        <Box mt={3}>
          {tabValue === 0 && renderOverviewTab()}
          {tabValue === 1 && renderStepsTab()}
          {tabValue === 2 && renderQualityTab()}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>{t('close')}</Button>
      </DialogActions>

      {/* Sub-dialogs */}
      <AddProductionStepDialog
        open={addStepOpen}
        onClose={() => setAddStepOpen(false)}
        batch={batchDetails.batch}
        onSuccess={() => {
          setAddStepOpen(false);
          loadBatchDetails();
        }}
      />

      <QualityTestDialog
        open={qualityTestOpen}
        onClose={() => setQualityTestOpen(false)}
        batch={batchDetails.batch}
        onSuccess={() => {
          setQualityTestOpen(false);
          loadBatchDetails();
        }}
      />

      <Dialog open={Boolean(viewStep)} onClose={() => setViewStep(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{viewStep?.step_name || t('productionStep')}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>Status: {viewStep?.status || '—'}</Typography>
          <Typography>Order: {viewStep?.step_order ?? '—'}</Typography>
          <Typography>Input: {viewStep?.input_quantity || '—'}</Typography>
          <Typography>Output: {viewStep?.output_quantity || '—'}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewStep(null)}>{t('close')}</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(viewTest)} onClose={() => setViewTest(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{viewTest?.test_number || t('qualityTest')}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>Type: {viewTest?.test_type || '—'}</Typography>
          <Typography>Grade: {viewTest?.overall_grade || '—'}</Typography>
          <Typography>Score: {viewTest?.quality_score ?? '—'}%</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewTest(null)}>{t('close')}</Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default BatchDetailsDialog;