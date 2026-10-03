import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  Analytics,
  TrendingUp,
  Assessment,
  PictureAsPdf,
  GetApp,
  Insights,
  AutoGraph,
  SmartToy,
  ExpandMore,
  Visibility,
  Timeline,
  BarChart,
  ShowChart,
  PieChart,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart as RechartsBarChart, Bar, PieChart as RechartsPieChart, Pie, Cell, AreaChart, Area } from 'recharts';
import DemoBanner from '../components/DemoBanner';
import PreviewModeToggle from '../components/PreviewModeToggle';
import { usePreviewMode } from '../hooks/usePreviewMode';
import { dashboardService } from '../services/dashboardService';
import { financeService } from '../services/financeService';
import { productionService } from '../services/productionService';
import api, { productionAPI } from '../services/api';
import {
  mapDashboardInsights,
  normalizeQualityTests,
  productionTrendFromRecords,
  qualityDashboardFromTests,
  unwrapList,
} from '../utils/previewLiveData';

const AnalyticsReporting = () => {
  const { mode, setMode, isSample } = usePreviewMode('analytics-reporting');
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState(null);
  const [reports, setReports] = useState([]);
  const [insights, setInsights] = useState([]);
  const [kpis, setKpis] = useState({});
  const [loading, setLoading] = useState(true);
  const [showReportDialog, setShowReportDialog] = useState(false);
  const [showPredictiveDialog, setShowPredictiveDialog] = useState(false);
  const [reportForm, setReportForm] = useState({
    report_type: 'production_summary',
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    language: 'english'
  });
  const [predictiveForm, setPredictiveForm] = useState({
    analysis_type: 'production_forecast',
    forecast_period: 30
  });
  const [pageMessage, setPageMessage] = useState(null);
  const [insightItem, setInsightItem] = useState(null);
  const [viewReport, setViewReport] = useState(null);

  // Mock data for demonstration
  const mockDashboardData = {
    overview: {
      total_production_30d: 125000,
      average_quality_score: 87.5,
      revenue_30d: 2500000,
      profit_30d: 450000,
      production_batches: 45,
      quality_tests: 120
    },
    trends: {
      production_trend: 'increasing',
      quality_trend: 'stable',
      financial_trend: 'positive'
    },
    alerts: [
      {
        type: 'info',
        message: 'Production efficiency improved by 5% this month',
        category: 'production'
      }
    ]
  };

  const mockKPIs = {
    production: {
      total_output: 125000,
      efficiency_rate: 92.5,
      downtime_hours: 8,
      yield_percentage: 78.5,
      batches_completed: 45
    },
    quality: {
      average_grade: 'B+',
      defect_rate: 2.3,
      grade_a_percentage: 65.0,
      quality_score: 87.5,
      tests_conducted: 120
    },
    financial: {
      revenue: 2500000,
      profit_margin: 18.5,
      cost_per_kg: 35.50,
      roi: 22.3,
      cash_flow: 450000
    }
  };

  const mockTrendData = [
    { date: '2024-01-01', production: 2800, quality: 85, revenue: 52000 },
    { date: '2024-01-02', production: 2950, quality: 87, revenue: 54000 },
    { date: '2024-01-03', production: 2750, quality: 86, revenue: 51000 },
    { date: '2024-01-04', production: 3100, quality: 89, revenue: 56000 },
    { date: '2024-01-05', production: 3200, quality: 88, revenue: 58000 },
    { date: '2024-01-06', production: 3050, quality: 90, revenue: 55000 },
    { date: '2024-01-07', production: 3300, quality: 91, revenue: 60000 },
  ];

  const mockInsights = [
    {
      category: 'production_efficiency',
      insight: 'Total production volume indicates high operational capacity',
      confidence: 0.85,
      priority_level: 'high'
    },
    {
      category: 'quality_performance',
      insight: 'Quality consistency is excellent with 91% average score',
      confidence: 0.90,
      priority_level: 'high'
    },
    {
      category: 'financial_health',
      insight: 'Revenue generation shows strong performance with 18.5% profit margin',
      confidence: 0.88,
      priority_level: 'medium'
    }
  ];

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      if (isSample) {
        setDashboardData(mockDashboardData);
        setKpis(mockKPIs);
        setInsights(mockInsights);
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const [overview, productionPayload, finance, testsRes, insightsRes, batchesRes, savedRes] = await Promise.all([
          dashboardService.getOverview(30),
          productionService.getAnalytics(30),
          financeService.getFinancialSummary(30),
          productionAPI.getQualityTests({ per_page: 50 }),
          dashboardService.getInsights(),
          productionService.getBatches({ per_page: 50 }),
          api.get('/analytics/reporting/saved').catch(() => ({ data: { reports: [] } })),
        ]);
        if (cancelled) return;
        setReports((savedRes?.data?.reports || []).map((row) => ({
          report_id: row.report_id,
          title: row.title,
          generated_at: row.generated_at,
          language: row.payload?.language || 'english',
          confidence_score: row.payload?.confidence_score || 80,
          period: row.payload?.period,
          kpis: row.payload?.kpis,
          note: row.payload?.note,
          ...row.payload,
          id: row.id,
        })));
        const production = productionPayload?.analytics || productionPayload || {};
        const tests = normalizeQualityTests(testsRes?.data || testsRes);
        const quality = qualityDashboardFromTests(tests);
        const batches = unwrapList(batchesRes, ['batches', 'items']);
        const revenue = Number(finance?.total_revenue || 0);
        const profit = Number(finance?.net_profit || 0);
        setDashboardData({
          overview: {
            total_production_30d: Number(overview?.summary?.total_production || production.total_output || 0),
            average_quality_score: Number(overview?.summary?.quality_score || quality.avgScore || 0),
            revenue_30d: revenue,
            profit_30d: profit,
            production_batches: Number(production.total_batches || batches.length || 0),
            quality_tests: quality.testCount,
          },
          trends: {
            production_trend: production.total_output ? 'from mill batches' : 'no data',
            quality_trend: quality.testCount ? 'from quality tests' : 'no data',
            financial_trend: revenue ? 'from invoices' : 'no data',
          },
          alerts: [],
          trendSeries: productionTrendFromRecords(production, batches),
        });
        setKpis({
          production: {
            total_output: Number(production.total_output || 0),
            efficiency_rate: Number(production.average_efficiency || 0),
            downtime_hours: 0,
            yield_percentage: Number(production.average_yield || 0),
            batches_completed: Number(production.completed_batches || 0),
          },
          quality: {
            average_grade: '—',
            defect_rate: 0,
            grade_a_percentage: 0,
            quality_score: quality.avgScore,
            tests_conducted: quality.testCount,
          },
          financial: {
            revenue,
            profit_margin: revenue ? (profit / revenue) * 100 : 0,
            cost_per_kg: 0,
            roi: 0,
            cash_flow: Number(finance?.net_profit || 0),
          },
        });
        setInsights(mapDashboardInsights(insightsRes).map((item) => ({
          category: item.type,
          insight: item.description || item.title,
          confidence: item.confidence,
          priority_level: String(item.impact || 'medium').toLowerCase(),
        })));
      } catch (error) {
        if (!cancelled) {
          console.error('Failed to load dashboard data:', error);
          setDashboardData({
            overview: {
              total_production_30d: 0,
              average_quality_score: 0,
              revenue_30d: 0,
              profit_30d: 0,
              production_batches: 0,
              quality_tests: 0,
            },
            trends: { production_trend: 'no data', quality_trend: 'no data', financial_trend: 'no data' },
            alerts: [],
            trendSeries: [],
          });
          setKpis({ production: {}, quality: {}, financial: {} });
          setInsights([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isSample]);

  const downloadJson = (filename, payload) => {
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const generateReport = async () => {
    const report = {
      report_id: `RPT-${Date.now()}`,
      title: reportForm.report_type.replace(/_/g, ' '),
      generated_at: new Date().toISOString(),
      language: reportForm.language,
      confidence_score: 80,
      period: { start_date: reportForm.start_date, end_date: reportForm.end_date },
      kpis,
      note: isSample
        ? 'Preview report from sample figures.'
        : 'Report built from mill records on Dashboard, Production, Quality tests, and Finance.',
    };
    if (!isSample) {
      try {
        const saved = await api.post('/analytics/reporting/saved', {
          title: report.title,
          report_type: reportForm.report_type,
          payload: report,
        });
        const row = saved?.data?.report;
        if (row?.report_id) {
          report.report_id = row.report_id;
          report.id = row.id;
          report.generated_at = row.generated_at || report.generated_at;
        }
      } catch (error) {
        setPageMessage({
          severity: 'error',
          text: error?.userMessage || 'Could not save the report on the mill',
        });
        return;
      }
    }
    setReports((prev) => [report, ...prev]);
    downloadJson(`${report.report_id}.json`, report);
    setShowReportDialog(false);
    setPageMessage({
      severity: 'success',
      text: isSample
        ? `Downloaded ${report.report_id}. This is a sample preview.`
        : `Saved and downloaded ${report.report_id} from mill records.`,
    });
  };

  const runPredictiveAnalysis = () => {
    const result = {
      analysis_type: predictiveForm.analysis_type,
      forecast_period: predictiveForm.forecast_period,
      summary: 'Outlook export only. MillMitra does not run a production ML model here.',
      sample_outlook: isSample ? mockTrendData : (dashboardData?.trendSeries || []),
    };
    downloadJson(`predictive-${predictiveForm.analysis_type}.json`, result);
    setShowPredictiveDialog(false);
    setPageMessage({
      severity: 'info',
      text: `Preview ${predictiveForm.analysis_type.replace(/_/g, ' ')} for ${predictiveForm.forecast_period} days downloaded.`,
    });
  };

  const getInsightIcon = (category) => {
    switch (category) {
      case 'production_efficiency': return <BarChart color="primary" />;
      case 'quality_performance': return <Assessment color="success" />;
      case 'financial_health': return <TrendingUp color="info" />;
      default: return <Insights color="secondary" />;
    }
  };

  const getInsightColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Analytics...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <DemoBanner title="Analytics & Reporting" mode={mode} />
      {pageMessage && (
        <Alert severity={pageMessage.severity} sx={{ mb: 2 }} onClose={() => setPageMessage(null)}>
          {pageMessage.text}
        </Alert>
      )}
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Analytics & Reporting
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Mill records from Dashboard, Production, Quality tests, and Finance. Sample is opt-in.
          </Typography>
        </Box>
        <PreviewModeToggle mode={mode} onChange={setMode} />
      </Box>

      {/* Quick Actions */}
      <Box sx={{ mb: 3 }}>
        <Button
          variant="contained"
          startIcon={<PictureAsPdf />}
          onClick={() => setShowReportDialog(true)}
          sx={{ mr: 2 }}
        >
          Generate Report
        </Button>
        <Button
          variant="outlined"
          startIcon={<AutoGraph />}
          onClick={() => setShowPredictiveDialog(true)}
          sx={{ mr: 2 }}
        >
          Predictive Analysis
        </Button>
        <Button
          variant="outlined"
          startIcon={<SmartToy />}
          onClick={() => setActiveTab(3)}
        >
          AI Insights
        </Button>
      </Box>

      {/* Analytics Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab icon={<Analytics />} label="Dashboard" />
          <Tab icon={<Assessment />} label="KPIs" />
          <Tab icon={<Timeline />} label="Trends" />
          <Tab icon={<Insights />} label="AI Insights" />
          <Tab icon={<PictureAsPdf />} label="Reports" />
        </Tabs>
      </Paper>

      {/* Dashboard Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          {/* Key Metrics Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Production (30d)
                </Typography>
                <Typography variant="h4" component="div" color="primary.main">
                  {dashboardData?.overview?.total_production_30d?.toLocaleString()} kg
                </Typography>
                <Chip 
                  label={dashboardData?.trends?.production_trend} 
                  color="success" 
                  size="small" 
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Quality Score
                </Typography>
                <Typography variant="h4" component="div" color="success.main">
                  {dashboardData?.overview?.average_quality_score}%
                </Typography>
                <Chip 
                  label={dashboardData?.trends?.quality_trend} 
                  color="info" 
                  size="small" 
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Revenue (30d)
                </Typography>
                <Typography variant="h4" component="div" color="info.main">
                  ₹{(dashboardData?.overview?.revenue_30d / 100000)?.toFixed(1)}L
                </Typography>
                <Chip 
                  label={dashboardData?.trends?.financial_trend} 
                  color="success" 
                  size="small" 
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Profit (30d)
                </Typography>
                <Typography variant="h4" component="div" color="warning.main">
                  ₹{(dashboardData?.overview?.profit_30d / 100000)?.toFixed(1)}L
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {((dashboardData?.overview?.profit_30d / dashboardData?.overview?.revenue_30d) * 100)?.toFixed(1)}% margin
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Trend Chart */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Trends
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={isSample ? mockTrendData : (dashboardData?.trendSeries || [])}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="production" stroke="#2196F3" strokeWidth={2} name="Production" />
                    <Line type="monotone" dataKey="quality" stroke="#4CAF50" strokeWidth={2} name="Quality" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Quick Stats */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Stats
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Production Batches
                  </Typography>
                  <Typography variant="h6">
                    {dashboardData?.overview?.production_batches}
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Quality Tests
                  </Typography>
                  <Typography variant="h6">
                    {dashboardData?.overview?.quality_tests}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Efficiency Rate
                  </Typography>
                    <Typography variant="h6" color="success.main">
                    {Number(kpis.production?.efficiency_rate || 0).toFixed(1)}%
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* KPIs Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          {/* Production KPIs */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary.main">
                  Production KPIs
                </Typography>
                {Object.entries(kpis.production || {}).map(([key, value]) => (
                  <Box key={key} sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                      {key.replace('_', ' ')}
                    </Typography>
                    <Typography variant="h6">
                      {typeof value === 'number' ? 
                        (key.includes('percentage') || key.includes('rate') ? `${value}%` : 
                         key.includes('hours') ? `${value}h` : 
                         value.toLocaleString()) : 
                        value}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Quality KPIs */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="success.main">
                  Quality KPIs
                </Typography>
                {Object.entries(kpis.quality || {}).map(([key, value]) => (
                  <Box key={key} sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                      {key.replace('_', ' ')}
                    </Typography>
                    <Typography variant="h6">
                      {typeof value === 'number' ? 
                        (key.includes('percentage') || key.includes('rate') || key.includes('score') ? `${value}%` : 
                         value.toLocaleString()) : 
                        value}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Financial KPIs */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="info.main">
                  Financial KPIs
                </Typography>
                {Object.entries(kpis.financial || {}).map(([key, value]) => (
                  <Box key={key} sx={{ mb: 1 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                      {key.replace('_', ' ')}
                    </Typography>
                    <Typography variant="h6">
                      {typeof value === 'number' ? 
                        (key.includes('percentage') || key.includes('margin') || key.includes('roi') ? `${value}%` : 
                         key.includes('revenue') || key.includes('cash') ? `₹${(value / 100000).toFixed(1)}L` :
                         key.includes('cost') ? `₹${value}` :
                         value.toLocaleString()) : 
                        value}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Trends Tab */}
      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Multi-Metric Trend Analysis
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={isSample ? mockTrendData : (dashboardData?.trendSeries || [])}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="production" stackId="1" stroke="#2196F3" fill="#2196F3" fillOpacity={0.3} />
                    <Area type="monotone" dataKey="quality" stackId="2" stroke="#4CAF50" fill="#4CAF50" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* AI Insights Tab */}
      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          {insights.map((insight, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    {getInsightIcon(insight.category)}
                    <Box sx={{ ml: 2, flexGrow: 1 }}>
                      <Typography variant="h6" gutterBottom>
                        {insight.category.replace('_', ' ').toUpperCase()}
                      </Typography>
                      <Chip 
                        label={insight.priority_level} 
                        color={getInsightColor(insight.priority_level)} 
                        size="small" 
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {(insight.confidence * 100).toFixed(0)}% confidence
                    </Typography>
                  </Box>
                  
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {insight.insight}
                  </Typography>
                  
                  <Button size="small" variant="outlined" onClick={() => setInsightItem(insight)}>
                    View Details
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Reports Tab */}
      <TabPanel value={activeTab} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Generated Reports
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Report ID</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Generated</TableCell>
                        <TableCell>Language</TableCell>
                        <TableCell>Confidence</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {reports.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={6} align="center">
                            <Typography variant="body2" color="text.secondary">
                              No reports generated yet. Click "Generate Report" to create your first report.
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ) : (
                        reports.map((report) => (
                          <TableRow key={report.report_id}>
                            <TableCell>{report.report_id}</TableCell>
                            <TableCell>{report.title}</TableCell>
                            <TableCell>{new Date(report.generated_at).toLocaleDateString()}</TableCell>
                            <TableCell>{report.language}</TableCell>
                            <TableCell>{report.confidence_score}%</TableCell>
                            <TableCell>
                              <Button size="small" startIcon={<Visibility />} sx={{ mr: 1 }} onClick={() => setViewReport(report)}>
                                View
                              </Button>
                              <Button
                                size="small"
                                startIcon={<GetApp />}
                                onClick={() => {
                                  downloadJson(`${report.report_id}.json`, report);
                                  setPageMessage({ severity: 'success', text: `Downloaded ${report.report_id}` });
                                }}
                              >
                                Download
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Generate Report Dialog */}
      <Dialog open={showReportDialog} onClose={() => setShowReportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Generate Natural Language Report</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            select
            label="Report Type"
            value={reportForm.report_type}
            onChange={(e) => setReportForm({ ...reportForm, report_type: e.target.value })}
            margin="normal"
          >
            <MenuItem value="production_summary">Production Summary</MenuItem>
            <MenuItem value="financial_performance">Financial Performance</MenuItem>
            <MenuItem value="quality_analysis">Quality Analysis</MenuItem>
            <MenuItem value="sales_performance">Sales Performance</MenuItem>
            <MenuItem value="operational_efficiency">Operational Efficiency</MenuItem>
          </TextField>
          
          <TextField
            fullWidth
            label="Start Date"
            type="date"
            value={reportForm.start_date}
            onChange={(e) => setReportForm({ ...reportForm, start_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          
          <TextField
            fullWidth
            label="End Date"
            type="date"
            value={reportForm.end_date}
            onChange={(e) => setReportForm({ ...reportForm, end_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          
          <TextField
            fullWidth
            select
            label="Language"
            value={reportForm.language}
            onChange={(e) => setReportForm({ ...reportForm, language: e.target.value })}
            margin="normal"
          >
            <MenuItem value="english">English</MenuItem>
            <MenuItem value="hindi">Hindi</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowReportDialog(false)}>Cancel</Button>
          <Button onClick={generateReport} variant="contained">
            Generate Report
          </Button>
        </DialogActions>
      </Dialog>

      {/* Predictive Analysis Dialog */}
      <Dialog open={showPredictiveDialog} onClose={() => setShowPredictiveDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Run Predictive Analysis</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            select
            label="Analysis Type"
            value={predictiveForm.analysis_type}
            onChange={(e) => setPredictiveForm({ ...predictiveForm, analysis_type: e.target.value })}
            margin="normal"
          >
            <MenuItem value="production_forecast">Production Forecast</MenuItem>
            <MenuItem value="demand_prediction">Demand Prediction</MenuItem>
            <MenuItem value="quality_prediction">Quality Prediction</MenuItem>
            <MenuItem value="financial_forecast">Financial Forecast</MenuItem>
            <MenuItem value="market_analysis">Market Analysis</MenuItem>
          </TextField>
          
          <TextField
            fullWidth
            label="Forecast Period (days)"
            type="number"
            value={predictiveForm.forecast_period}
            onChange={(e) => setPredictiveForm({ ...predictiveForm, forecast_period: parseInt(e.target.value) })}
            margin="normal"
            inputProps={{ min: 1, max: 365 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPredictiveDialog(false)}>Cancel</Button>
          <Button onClick={runPredictiveAnalysis} variant="contained">
            Run Analysis
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(insightItem)} onClose={() => setInsightItem(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{insightItem?.category?.replace(/_/g, ' ')}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>{insightItem?.insight}</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Priority: {insightItem?.priority_level} · Confidence: {insightItem ? Math.round(insightItem.confidence * 100) : 0}%
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>Sample insight. Live mill figures are on Dashboard and Finance.</Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInsightItem(null)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(viewReport)} onClose={() => setViewReport(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{viewReport?.title}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>{viewReport?.report_id}</Typography>
          <Typography variant="body2">{viewReport?.note}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewReport(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AnalyticsReporting;
