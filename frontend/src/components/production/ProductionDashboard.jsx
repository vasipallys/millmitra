import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Chip, LinearProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Button, Dialog, DialogTitle, DialogContent,
  Alert, CircularProgress
} from '@mui/material';
import {
  PlayArrow, Pause, Stop, Visibility, Add, Refresh,
  TrendingUp, Assessment, Warning, CheckCircle
} from '@mui/icons-material';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { productionAPI } from '../../services/api';
import CreateBatchDialog from './CreateBatchDialog';
import BatchDetailsDialog from './BatchDetailsDialog';

const ProductionDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [createBatchOpen, setCreateBatchOpen] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await productionAPI.getDashboard();
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchAction = async (batchId, action) => {
    try {
      await productionAPI.batchAction(batchId, action);
      loadDashboardData();
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

  const getEfficiencyColor = (efficiency) => {
    if (efficiency >= 90) return 'success';
    if (efficiency >= 75) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!dashboardData) {
    return <Alert severity="warning">Production dashboard data is unavailable.</Alert>;
  }

  const { current_status, weekly_analytics, ai_insights } = dashboardData;

  // Chart data
  const efficiencyChartData = {
    labels: weekly_analytics.daily_production.map(d => new Date(d.date).toLocaleDateString()),
    datasets: [{
      label: 'Efficiency %',
      data: weekly_analytics.daily_production.map(d => d.average_efficiency),
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      tension: 0.1
    }]
  };

  const productionChartData = {
    labels: weekly_analytics.daily_production.map(d => new Date(d.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Input (Quintals)',
        data: weekly_analytics.daily_production.map(d => d.input_quantity),
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
      },
      {
        label: 'Output (Quintals)',
        data: weekly_analytics.daily_production.map(d => d.output_quantity),
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
      }
    ]
  };

  const qualityDistributionData = {
    labels: Object.keys(current_status.quality_stats.grade_distribution || {}),
    datasets: [{
      data: Object.values(current_status.quality_stats.grade_distribution || {}),
      backgroundColor: [
        'rgba(76, 175, 80, 0.8)',  // A - Green
        'rgba(255, 193, 7, 0.8)',   // B - Yellow
        'rgba(255, 152, 0, 0.8)',   // C - Orange
        'rgba(244, 67, 54, 0.8)'    // D - Red
      ]
    }]
  };

  return (
    <Box p={3}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Production Dashboard
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateBatchOpen(true)}
            sx={{ mr: 2 }}
          >
            New Batch
          </Button>
          <IconButton onClick={loadDashboardData}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* AI Insights Alert */}
      {ai_insights?.alerts?.length > 0 && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle2">AI Insights:</Typography>
          {ai_insights.alerts.map((alert, index) => (
            <Typography key={index} variant="body2">• {alert}</Typography>
          ))}
        </Alert>
      )}

      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Batches
                  </Typography>
                  <Typography variant="h4">
                    {current_status.active_batches}
                  </Typography>
                </Box>
                <PlayArrow color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Capacity Utilization
                  </Typography>
                  <Typography variant="h4">
                    {current_status.capacity_utilization}%
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={current_status.capacity_utilization}
                    color={current_status.capacity_utilization > 85 ? 'success' : 'primary'}
                    sx={{ mt: 1 }}
                  />
                </Box>
                <TrendingUp color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Today's Output
                  </Typography>
                  <Typography variant="h4">
                    {current_status.total_output_today}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    quintals
                  </Typography>
                </Box>
                <Assessment color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Efficiency
                  </Typography>
                  <Typography variant="h4">
                    {current_status.average_efficiency}%
                  </Typography>
                  <Chip
                    size="small"
                    label={getEfficiencyColor(current_status.average_efficiency)}
                    color={getEfficiencyColor(current_status.average_efficiency)}
                    sx={{ mt: 1 }}
                  />
                </Box>
                <CheckCircle color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Weekly Production Trend
              </Typography>
              <Box height={300}>
                <Bar data={productionChartData} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quality Distribution
              </Typography>
              <Box height={300}>
                <Doughnut data={qualityDistributionData} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Efficiency Trend */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Efficiency Trend
              </Typography>
              <Box height={300}>
                <Line data={efficiencyChartData} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Active Batches Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Batches
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Batch Number</TableCell>
                  <TableCell>Variety</TableCell>
                  <TableCell>Input Qty</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Progress</TableCell>
                  <TableCell>Efficiency</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {current_status.active_batch_details.map((batch) => (
                  <TableRow key={batch.id}>
                    <TableCell>{batch.batch_number}</TableCell>
                    <TableCell>{batch.paddy_variety}</TableCell>
                    <TableCell>{batch.input_quantity} Q</TableCell>
                    <TableCell>
                      <Chip
                        label={batch.status}
                        color={getStatusColor(batch.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <LinearProgress
                        variant="determinate"
                        value={batch.progress || 0}
                        sx={{ width: 100 }}
                      />
                    </TableCell>
                    <TableCell>
                      {batch.efficiency_score ? `${batch.efficiency_score}%` : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedBatch(batch);
                          setDetailsOpen(true);
                        }}
                      >
                        <Visibility />
                      </IconButton>
                      {batch.status === 'in_progress' && (
                        <IconButton
                          size="small"
                          onClick={() => handleBatchAction(batch.id, 'pause')}
                        >
                          <Pause />
                        </IconButton>
                      )}
                      {batch.status === 'paused' && (
                        <IconButton
                          size="small"
                          onClick={() => handleBatchAction(batch.id, 'resume')}
                        >
                          <PlayArrow />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Dialogs */}
      <CreateBatchDialog
        open={createBatchOpen}
        onClose={() => setCreateBatchOpen(false)}
        onSuccess={loadDashboardData}
      />

      <BatchDetailsDialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        batch={selectedBatch}
        onUpdate={loadDashboardData}
      />
    </Box>
  );
};

export default ProductionDashboard;