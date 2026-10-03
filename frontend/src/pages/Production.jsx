import { useState } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Select, MenuItem, FormControl, InputLabel, Alert, LinearProgress,
  Tabs, Tab
} from '@mui/material';
import {
  Add, PlayArrow, Stop, Visibility, Assessment, Settings,
  CheckCircle, Warning, Error, Schedule, TrendingUp
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { productionService } from '../services/productionService';
import BatchCard from '../components/BatchCard';
import QualityTestDialog from '../components/QualityTestDialog';
import ProductionAnalytics from '../components/ProductionAnalytics';
import AIRecommendations from '../components/AIRecommendations';
import { getApiErrorMessage } from '../utils/apiError';
import { PageEmpty, PageHeader, PageShell, QueryErrorAlert } from '../components/common/PageChrome';
import { useI18n } from '../i18n/I18nContext';

const Production = () => {
  const { t, statusLabel } = useI18n();
  const [activeTab, setActiveTab] = useState(0);
  const [createBatchOpen, setCreateBatchOpen] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [batchDetailsOpen, setBatchDetailsOpen] = useState(false);
  const [qualityTestOpen, setQualityTestOpen] = useState(false);
  const [completeOpen, setCompleteOpen] = useState(false);
  const [completeForm, setCompleteForm] = useState({
    rice_output: '',
    broken_rice_output: '',
    bran_output: '',
    husk_output: ''
  });
  const queryClient = useQueryClient();

  // Fetch production data
  const { data: batches, isLoading: batchesLoading, isError: batchesError, error: batchesErr, refetch: refetchBatches } = useQuery(
    'production-batches',
    () => productionService.getBatches(),
    { refetchInterval: 30000 }
  );

  const { data: currentStatus } = useQuery(
    'production-status',
    () => productionService.getCurrentStatus(),
    { refetchInterval: 10000 }
  );

  const { data: recommendations } = useQuery(
    'production-recommendations',
    () => productionService.getRecommendations(),
    { refetchInterval: 60000 }
  );

  // Mutations
  const [actionError, setActionError] = useState('');

  const refreshBatches = () => {
    queryClient.invalidateQueries('production-batches');
    queryClient.invalidateQueries('production-status');
  };

  const createBatchMutation = useMutation(productionService.createBatch, {
    onSuccess: () => {
      refreshBatches();
      setCreateBatchOpen(false);
      setActionError('');
    },
    onError: (error) => setActionError(getApiErrorMessage(error, 'Could not create batch'))
  });

  const startBatchMutation = useMutation(productionService.startBatch, {
    onSuccess: () => {
      refreshBatches();
      setActionError('');
    },
    onError: (error) => setActionError(getApiErrorMessage(error, 'Could not start batch'))
  });

  const pauseBatchMutation = useMutation(
    ({ batchId, reason }) => productionService.pauseBatch(batchId, { reason }),
    {
      onSuccess: () => {
        refreshBatches();
        setActionError('');
      },
      onError: (error) => setActionError(getApiErrorMessage(error, 'Could not pause batch'))
    }
  );

  const resumeBatchMutation = useMutation(productionService.resumeBatch, {
    onSuccess: () => {
      refreshBatches();
      setActionError('');
    },
    onError: (error) => setActionError(getApiErrorMessage(error, 'Could not resume batch'))
  });

  const completeBatchMutation = useMutation(
    ({ batchId, ...completionData }) => productionService.completeBatch(batchId, completionData),
    {
      onSuccess: () => {
        refreshBatches();
        setCompleteOpen(false);
        setSelectedBatch(null);
        setActionError('');
      },
      onError: (error) => setActionError(getApiErrorMessage(error, 'Could not complete batch'))
    }
  );

  const handleCreateBatch = (batchData) => {
    createBatchMutation.mutate(batchData);
  };

  const handleStartBatch = (batchId) => {
    startBatchMutation.mutate(batchId);
  };

  const handlePauseBatch = (batchId, reason = 'Paused from mill floor') => {
    pauseBatchMutation.mutate({ batchId, reason });
  };

  const handleResumeBatch = (batchId) => {
    resumeBatchMutation.mutate(batchId);
  };

  const handleOpenComplete = (batch) => {
    setSelectedBatch(batch);
    setCompleteForm({
      rice_output: '',
      broken_rice_output: '',
      bran_output: '',
      husk_output: ''
    });
    setCompleteOpen(true);
  };

  const handleCompleteBatch = () => {
    if (!selectedBatch?.id) return;
    completeBatchMutation.mutate({
      batchId: selectedBatch.id,
      rice_output: completeForm.rice_output,
      output_quantity: completeForm.rice_output,
      broken_rice_output: completeForm.broken_rice_output,
      bran_output: completeForm.bran_output,
      husk_output: completeForm.husk_output
    });
  };

  const handleViewBatch = (batch) => {
    setSelectedBatch(batch);
    setBatchDetailsOpen(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'primary';
      case 'planned': return 'warning';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle />;
      case 'in_progress': return <PlayArrow />;
      case 'planned': return <Schedule />;
      case 'cancelled': return <Error />;
      default: return null;
    }
  };

  return (
    <PageShell>
      <PageHeader
        title={t('productionTitle')}
        subtitle={t('productionSubtitle')}
        actions={
          <Button variant="contained" startIcon={<Add />} onClick={() => setCreateBatchOpen(true)}>
            {t('newBatch')}
          </Button>
        }
      />
      {batchesError && <QueryErrorAlert error={batchesErr} onRetry={refetchBatches} entity="production batches" />}
      {actionError && <QueryErrorAlert error={new Error(actionError)} entity="production action" />}
      {batchesLoading && <LinearProgress sx={{ mb: 2 }} />}

      {/* AI Recommendations */}
      {recommendations?.recommendations?.length > 0 && (
        <AIRecommendations recommendations={recommendations.recommendations} />
      )}

      {/* Current Status Overview */}
      {currentStatus && (
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Active Batches
                </Typography>
                <Typography variant="h4" color="primary">
                  {currentStatus.active_batches}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  {t('inProgress')}
                </Typography>
                <Typography variant="h4" color="success.main">
                  {currentStatus.in_progress}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  {t('status_planned')}
                </Typography>
                <Typography variant="h4" color="warning.main">
                  {currentStatus.planned}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  {t('machinesInUse')}
                </Typography>
                <Typography variant="h4" color="info.main">
                  {currentStatus.machines_in_use}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label={t('activeBatches')} />
          <Tab label={t('allBatches')} />
          <Tab label={t('analytics')} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {!currentStatus?.batches?.length && (
            <Grid item xs={12}>
              <PageEmpty
                title={t('noActiveBatches')}
                description={t('noActiveBatchesHint')}
                action={
                  <Button variant="contained" startIcon={<Add />} onClick={() => setCreateBatchOpen(true)}>
                    {t('newBatch')}
                  </Button>
                }
              />
            </Grid>
          )}
          {currentStatus?.batches?.map((batch) => (
            <Grid item xs={12} md={6} lg={4} key={batch.id}>
              <BatchCard
                batch={batch}
                onStart={() => handleStartBatch(batch.id)}
                onPause={() => handlePauseBatch(batch.id)}
                onStop={() => handlePauseBatch(batch.id, 'Stopped from mill floor')}
                onResume={() => handleResumeBatch(batch.id)}
                onComplete={() => handleOpenComplete(batch)}
                onViewDetails={() => handleViewBatch(batch)}
                onQualityTest={() => {
                  setSelectedBatch(batch);
                  setQualityTestOpen(true);
                }}
              />
            </Grid>
          ))}
        </Grid>
      )}

      {activeTab === 1 && (
        <Card>
          <CardContent>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Batch Number</TableCell>
                    <TableCell>Variety</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Input (kg)</TableCell>
                    <TableCell>Output (kg)</TableCell>
                    <TableCell>Efficiency</TableCell>
                    <TableCell>Quality</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {!(batches?.batches?.length) && (
                    <TableRow>
                      <TableCell colSpan={8}>
                        <PageEmpty
                          title={t('noBatchesYet')}
                          description={t('noBatchesHint')}
                          action={
                            <Button variant="contained" startIcon={<Add />} onClick={() => setCreateBatchOpen(true)} sx={{ minHeight: 40 }}>
                              {t('newBatch')}
                            </Button>
                          }
                        />
                      </TableCell>
                    </TableRow>
                  )}
                  {batches?.batches?.map((batch) => (
                    <TableRow key={batch.id}>
                      <TableCell>{batch.batch_number}</TableCell>
                      <TableCell>{batch.paddy_variety}</TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(batch.status)}
                          label={statusLabel(batch.status)}
                          color={getStatusColor(batch.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{batch.input_quantity}</TableCell>
                      <TableCell>{batch.output_quantity || '-'}</TableCell>
                      <TableCell>
                        {batch.efficiency_score ? `${batch.efficiency_score.toFixed(1)}%` : '-'}
                      </TableCell>
                      <TableCell>
                        {batch.current_quality_score ? `${batch.current_quality_score.toFixed(1)}%` : '-'}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          <Button size="small" startIcon={<Visibility />} onClick={() => handleViewBatch(batch)} sx={{ minHeight: 40 }}>
                            View
                          </Button>
                          {batch.status === 'planned' && (
                            <Button size="small" startIcon={<PlayArrow />} onClick={() => handleStartBatch(batch.id)} sx={{ minHeight: 40 }}>
                              Start
                            </Button>
                          )}
                          {batch.status === 'paused' && (
                            <Button size="small" startIcon={<PlayArrow />} onClick={() => handleResumeBatch(batch.id)} sx={{ minHeight: 40 }}>
                              Resume
                            </Button>
                          )}
                          {batch.status === 'in_progress' && (
                            <Button size="small" startIcon={<Stop />} onClick={() => handlePauseBatch(batch.id)} sx={{ minHeight: 40 }}>
                              Pause
                            </Button>
                          )}
                          {(batch.status === 'in_progress' || batch.status === 'paused') && (
                            <>
                              <Button
                                size="small"
                                startIcon={<Assessment />}
                                onClick={() => {
                                  setSelectedBatch(batch);
                                  setQualityTestOpen(true);
                                }}
                                sx={{ minHeight: 40 }}
                              >
                                Quality
                              </Button>
                              <Button size="small" startIcon={<CheckCircle />} onClick={() => handleOpenComplete(batch)} sx={{ minHeight: 40 }}>
                                Complete
                              </Button>
                            </>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {activeTab === 2 && (
        <ProductionAnalytics />
      )}

      {/* Create Batch Dialog */}
      <CreateBatchDialog
        open={createBatchOpen}
        onClose={() => setCreateBatchOpen(false)}
        onSubmit={handleCreateBatch}
        loading={createBatchMutation.isLoading}
      />

      {/* Batch Details Dialog */}
      <BatchDetailsDialog
        open={batchDetailsOpen}
        onClose={() => setBatchDetailsOpen(false)}
        batch={selectedBatch}
      />

      {/* Quality Test Dialog */}
      <QualityTestDialog
        open={qualityTestOpen}
        onClose={() => setQualityTestOpen(false)}
        batch={selectedBatch}
        onSubmit={(testData) => {
          if (selectedBatch?.id) {
            productionService.createQualityTest({
              ...testData,
              batch_id: selectedBatch.id
            });
          }
          setQualityTestOpen(false);
        }}
      />

      <CompleteBatchDialog
        open={completeOpen}
        batch={selectedBatch}
        form={completeForm}
        onChange={setCompleteForm}
        onClose={() => setCompleteOpen(false)}
        onSubmit={handleCompleteBatch}
        loading={completeBatchMutation.isLoading}
      />
    </PageShell>
  );
};

const CompleteBatchDialog = ({ open, onClose, onSubmit, batch, form, onChange, loading }) => {
  const { t } = useI18n();
  return (
  <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
    <DialogTitle>
      {t('markCompleteNamed', { batch: batch?.batch_number || batch?.batch_id || '' })}
    </DialogTitle>
    <DialogContent>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 2 }}>
        {t('completeBatchHelp')}
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label={t('riceOutputKg')}
            type="number"
            value={form.rice_output}
            onChange={(e) => onChange({ ...form, rice_output: e.target.value })}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label={t('brokenRiceKg')}
            type="number"
            value={form.broken_rice_output}
            onChange={(e) => onChange({ ...form, broken_rice_output: e.target.value })}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label={t('branKg')}
            type="number"
            value={form.bran_output}
            onChange={(e) => onChange({ ...form, bran_output: e.target.value })}
          />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label={t('huskKg')}
            type="number"
            value={form.husk_output}
            onChange={(e) => onChange({ ...form, husk_output: e.target.value })}
          />
        </Grid>
      </Grid>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose}>{t('cancel')}</Button>
      <Button onClick={onSubmit} variant="contained" disabled={loading}>
        {loading ? t('saving') : t('markComplete')}
      </Button>
    </DialogActions>
  </Dialog>
  );
};

const CreateBatchDialog = ({ open, onClose, onSubmit, loading }) => {
  const { t } = useI18n();
  const [formData, setFormData] = useState({
    paddy_variety: '',
    input_quantity: '',
    quality_grade: 'A',
    planned_start_time: '',
    estimated_duration: 240,
    special_instructions: ''
  });

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>{t('createNewBatch')}</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>{t('paddyVariety')}</InputLabel>
              <Select
                value={formData.paddy_variety}
                onChange={(e) => setFormData({...formData, paddy_variety: e.target.value})}
              >
                <MenuItem value="basmati">Basmati</MenuItem>
                <MenuItem value="jasmine">Jasmine</MenuItem>
                <MenuItem value="long_grain">Long Grain</MenuItem>
                <MenuItem value="short_grain">Short Grain</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={t('inputQtyKg')}
              type="number"
              value={formData.input_quantity}
              onChange={(e) => setFormData({...formData, input_quantity: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>{t('qualityGrade')}</InputLabel>
              <Select
                value={formData.quality_grade}
                onChange={(e) => setFormData({...formData, quality_grade: e.target.value})}
              >
                <MenuItem value="A">{t('gradeA')}</MenuItem>
                <MenuItem value="B">{t('gradeB')}</MenuItem>
                <MenuItem value="C">{t('gradeC')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={t('plannedStart')}
              type="datetime-local"
              value={formData.planned_start_time}
              onChange={(e) => setFormData({...formData, planned_start_time: e.target.value})}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label={t('specialInstructions')}
              multiline
              rows={3}
              value={formData.special_instructions}
              onChange={(e) => setFormData({...formData, special_instructions: e.target.value})}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('cancel')}</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? t('creating') : t('createBatch')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const BatchDetailsDialog = ({ open, onClose, batch }) => {
  const { t, statusLabel } = useI18n();
  if (!batch) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>{t('batchDetailsNamed', { batch: batch.batch_number })}</DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>{t('basicInfo')}</Typography>
            <Typography><strong>{t('variety')}:</strong> {batch.paddy_variety}</Typography>
            <Typography><strong>{t('status')}:</strong> {statusLabel(batch.status)}</Typography>
            <Typography><strong>{t('inputQuantityLabel')}:</strong> {batch.input_quantity} kg</Typography>
            <Typography><strong>{t('outputQty')}:</strong> {batch.output_quantity || t('na')} kg</Typography>
            <Typography><strong>{t('efficiency')}:</strong> {batch.efficiency_score ? `${batch.efficiency_score.toFixed(1)}%` : t('na')}</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>{t('timeline')}</Typography>
            <Typography><strong>{t('plannedStart')}:</strong> {new Date(batch.planned_start_time).toLocaleString()}</Typography>
            <Typography><strong>{t('actualStart')}:</strong> {batch.start_time ? new Date(batch.start_time).toLocaleString() : t('na')}</Typography>
            <Typography><strong>{t('completion')}:</strong> {batch.end_time ? new Date(batch.end_time).toLocaleString() : t('na')}</Typography>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('close')}</Button>
      </DialogActions>
    </Dialog>
  );
};

export default Production;