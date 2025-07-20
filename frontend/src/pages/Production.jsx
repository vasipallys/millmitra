import { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Select, MenuItem, FormControl, InputLabel, Alert, LinearProgress,
  Tabs, Tab, IconButton, Tooltip
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

const Production = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [createBatchOpen, setCreateBatchOpen] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [batchDetailsOpen, setBatchDetailsOpen] = useState(false);
  const [qualityTestOpen, setQualityTestOpen] = useState(false);
  const queryClient = useQueryClient();

  // Fetch production data
  const { data: batches, isLoading: batchesLoading } = useQuery(
    'production-batches',
    () => productionService.getBatches(),
    { refetchInterval: 30000 }
  );

  const { data: currentStatus } = useQuery(
    'production-status',
    productionService.getCurrentStatus,
    { refetchInterval: 10000 }
  );

  const { data: recommendations } = useQuery(
    'production-recommendations',
    productionService.getRecommendations,
    { refetchInterval: 60000 }
  );

  // Mutations
  const createBatchMutation = useMutation(productionService.createBatch, {
    onSuccess: () => {
      queryClient.invalidateQueries('production-batches');
      setCreateBatchOpen(false);
    }
  });

  const startBatchMutation = useMutation(productionService.startBatch, {
    onSuccess: () => {
      queryClient.invalidateQueries(['production-batches', 'production-status']);
    }
  });

  const completeBatchMutation = useMutation(productionService.completeBatch, {
    onSuccess: () => {
      queryClient.invalidateQueries(['production-batches', 'production-status']);
    }
  });

  const handleCreateBatch = (batchData) => {
    createBatchMutation.mutate(batchData);
  };

  const handleStartBatch = (batchId) => {
    startBatchMutation.mutate(batchId);
  };

  const handleCompleteBatch = (batchId, completionData) => {
    completeBatchMutation.mutate({ batchId, ...completionData });
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
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Production Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateBatchOpen(true)}
        >
          New Batch
        </Button>
      </Box>

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
                  In Progress
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
                  Planned
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
                  Machines in Use
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
          <Tab label="Active Batches" />
          <Tab label="All Batches" />
          <Tab label="Analytics" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {currentStatus?.batches?.map((batch) => (
            <Grid item xs={12} md={6} lg={4} key={batch.id}>
              <BatchCard
                batch={batch}
                onStart={() => handleStartBatch(batch.id)}
                onComplete={(data) => handleCompleteBatch(batch.id, data)}
                onView={() => handleViewBatch(batch)}
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
                  {batches?.batches?.map((batch) => (
                    <TableRow key={batch.id}>
                      <TableCell>{batch.batch_number}</TableCell>
                      <TableCell>{batch.paddy_variety}</TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(batch.status)}
                          label={batch.status}
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
                        <Tooltip title="View Details">
                          <IconButton onClick={() => handleViewBatch(batch)}>
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        {batch.status === 'planned' && (
                          <Tooltip title="Start Batch">
                            <IconButton onClick={() => handleStartBatch(batch.id)}>
                              <PlayArrow />
                            </IconButton>
                          </Tooltip>
                        )}
                        {batch.status === 'in_progress' && (
                          <Tooltip title="Quality Test">
                            <IconButton onClick={() => {
                              setSelectedBatch(batch);
                              setQualityTestOpen(true);
                            }}>
                              <Assessment />
                            </IconButton>
                          </Tooltip>
                        )}
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
          // Handle quality test submission
          setQualityTestOpen(false);
        }}
      />
    </Box>
  );
};

const CreateBatchDialog = ({ open, onClose, onSubmit, loading }) => {
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
      <DialogTitle>Create New Production Batch</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Paddy Variety</InputLabel>
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
              label="Input Quantity (kg)"
              type="number"
              value={formData.input_quantity}
              onChange={(e) => setFormData({...formData, input_quantity: e.target.value})}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Quality Grade</InputLabel>
              <Select
                value={formData.quality_grade}
                onChange={(e) => setFormData({...formData, quality_grade: e.target.value})}
              >
                <MenuItem value="A">Grade A</MenuItem>
                <MenuItem value="B">Grade B</MenuItem>
                <MenuItem value="C">Grade C</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Planned Start Time"
              type="datetime-local"
              value={formData.planned_start_time}
              onChange={(e) => setFormData({...formData, planned_start_time: e.target.value})}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Special Instructions"
              multiline
              rows={3}
              value={formData.special_instructions}
              onChange={(e) => setFormData({...formData, special_instructions: e.target.value})}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? 'Creating...' : 'Create Batch'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const BatchDetailsDialog = ({ open, onClose, batch }) => {
  if (!batch) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>Batch Details - {batch.batch_number}</DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>Basic Information</Typography>
            <Typography><strong>Variety:</strong> {batch.paddy_variety}</Typography>
            <Typography><strong>Status:</strong> {batch.status}</Typography>
            <Typography><strong>Input Quantity:</strong> {batch.input_quantity} kg</Typography>
            <Typography><strong>Output Quantity:</strong> {batch.output_quantity || 'N/A'} kg</Typography>
            <Typography><strong>Efficiency:</strong> {batch.efficiency_score ? `${batch.efficiency_score.toFixed(1)}%` : 'N/A'}</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>Timeline</Typography>
            <Typography><strong>Planned Start:</strong> {new Date(batch.planned_start_time).toLocaleString()}</Typography>
            <Typography><strong>Actual Start:</strong> {batch.start_time ? new Date(batch.start_time).toLocaleString() : 'N/A'}</Typography>
            <Typography><strong>Completion:</strong> {batch.end_time ? new Date(batch.end_time).toLocaleString() : 'N/A'}</Typography>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default Production;