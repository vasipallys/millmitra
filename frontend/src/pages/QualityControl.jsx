import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
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
  Tabs,
  Tab,
  LinearProgress,
} from '@mui/material';
import {
  CameraAlt,
  Analytics,
  Assessment,
  CheckCircle,
  Warning,
  Error,
  CloudUpload,
  Visibility,
  GetApp,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import DemoBanner from '../components/DemoBanner';
import { useI18n } from '../i18n/I18nContext';
import PreviewModeToggle from '../components/PreviewModeToggle';
import { usePreviewMode } from '../hooks/usePreviewMode';
import { productionAPI } from '../services/api';
import LookupSelect from '../components/common/LookupSelect';
import {
  gradeDistributionFromTests,
  normalizeQualityTests,
  qualityDashboardFromTests,
  qualityTrendFromTests,
} from '../utils/previewLiveData';

const QualityControl = () => {
  const { t } = useI18n();
  const { mode, setMode, isSample, isActual } = usePreviewMode('quality-control');
  const [activeTab, setActiveTab] = useState(0);
  const [showCameraDialog, setShowCameraDialog] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [recentTests, setRecentTests] = useState([]);
  const [qualityTrend, setQualityTrend] = useState([]);
  const [selectedVariety, setSelectedVariety] = useState('basmati');
  const [batchId, setBatchId] = useState('');
  const [pageMessage, setPageMessage] = useState(null);
  const [viewTest, setViewTest] = useState(null);
  const [previewTests, setPreviewTests] = useState([]);
  const [testsLoading, setTestsLoading] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);

  // Mock data for demonstration
  const mockQualityTrend = [
    { date: '2024-01-01', score: 87, tests: 5 },
    { date: '2024-01-02', score: 89, tests: 8 },
    { date: '2024-01-03', score: 85, tests: 6 },
    { date: '2024-01-04', score: 92, tests: 7 },
    { date: '2024-01-05', score: 88, tests: 9 },
    { date: '2024-01-06', score: 90, tests: 6 },
    { date: '2024-01-07', score: 94, tests: 8 },
  ];

  const mockRecentTests = [
    {
      id: 'QT20240115001',
      batch_id: 'PB001',
      variety: 'Basmati',
      grade: 'A',
      score: 92.5,
      date: '2024-01-15 10:30',
      status: 'completed'
    },
    {
      id: 'QT20240115002',
      batch_id: 'PB002',
      variety: 'Jasmine',
      grade: 'B',
      score: 85.2,
      date: '2024-01-15 11:15',
      status: 'completed'
    },
    {
      id: 'QT20240115003',
      batch_id: 'PB003',
      variety: 'Brown',
      grade: 'A',
      score: 89.8,
      date: '2024-01-15 14:20',
      status: 'verified'
    }
  ];

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      if (isSample) {
        setQualityTrend(mockQualityTrend);
        setRecentTests(mockRecentTests);
        setTestsLoading(false);
        return;
      }
      setTestsLoading(true);
      try {
        const response = await productionAPI.getQualityTests({ per_page: 50 });
        if (cancelled) return;
        const tests = normalizeQualityTests(response.data || response);
        setRecentTests(tests);
        setQualityTrend(qualityTrendFromTests(tests));
      } catch (error) {
        if (!cancelled) {
          setRecentTests([]);
          setQualityTrend([]);
          setPageMessage({
            severity: 'warning',
            text: error?.userMessage || 'Could not load quality tests from Production.',
          });
        }
      } finally {
        if (!cancelled) setTestsLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isSample]);

  const gradeDistribution = isSample
    ? [
      { name: 'Grade A', value: 45, color: '#4CAF50' },
      { name: 'Grade B', value: 30, color: '#FF9800' },
      { name: 'Grade C', value: 20, color: '#FFC107' },
      { name: 'Grade D', value: 4, color: '#FF5722' },
      { name: 'Grade E', value: 1, color: '#F44336' },
    ]
    : gradeDistributionFromTests(recentTests);

  const qualitySummary = isSample
    ? { passRate: 94.2, avgScore: 89.7, testsToday: 23, testCount: mockRecentTests.length }
    : qualityDashboardFromTests(recentTests);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setShowCameraDialog(true);
      }
    } catch (error) {
      setPageMessage({
        severity: 'warning',
        text: 'Camera access was denied. Use Upload Image instead, or allow the camera and try again.',
      });
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const captureImage = () => {
    if (!videoRef.current || !canvasRef.current) return null;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    return canvas.toDataURL('image/jpeg', 0.8);
  };

  const analyzeQuality = async (imageData) => {
    setIsAnalyzing(true);
    const preview = {
      overall_score: 88.0,
      overall_grade: 'B',
      grade: 'B',
      quality_score: 88.0,
      moisture_content: 12.4,
      broken_percentage: 4.1,
      variety: selectedVariety,
      batch_id: batchId || 'preview',
      grain_analysis: { broken_percentage: 4.1, average_length: 6.8 },
      foreign_matter: { foreign_matter_percentage: 0.3 },
      moisture_estimation: { estimated_moisture_percentage: 12.4 },
      note: 'Camera estimate only. Record official lab numbers on Production → Quality Test.',
    };
    setTimeout(() => {
      setAnalysisResult(preview);
      const cameraRow = {
        id: `QT-PREVIEW-${Date.now()}`,
        batch_id: preview.batch_id,
        variety: selectedVariety,
        grade: preview.grade,
        score: preview.overall_score,
        date: new Date().toLocaleString(),
        status: 'preview',
        details: preview,
      };
      setPreviewTests((prev) => [cameraRow, ...prev]);
      if (isSample) {
        setRecentTests((prev) => [cameraRow, ...prev]);
      }
      setShowCameraDialog(false);
      stopCamera();
      setPageMessage({
        severity: 'info',
        text: isSample
          ? 'Sample camera analysis added to this screen only.'
          : 'Camera preview shown. It did not change live quality tests from Production.',
      });
      setIsAnalyzing(false);
    }, 400);
    return imageData;
  };

  const handleCameraCapture = () => {
    const imageData = captureImage();
    if (imageData) {
      analyzeQuality(imageData);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        analyzeQuality(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const getGradeColor = (grade) => {
    switch (grade) {
      case 'A': return 'success';
      case 'B': return 'info';
      case 'C': return 'warning';
      case 'D': return 'error';
      case 'E': return 'error';
      default: return 'default';
    }
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box>
      <DemoBanner title={t('qualityControl')} mode={mode} />
      {pageMessage && (
        <Alert severity={pageMessage.severity} sx={{ mb: 2 }} onClose={() => setPageMessage(null)}>
          {pageMessage.text}
        </Alert>
      )}
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Quality Control
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Live quality tests from Production. Camera grading is optional and does not overwrite mill tests.
          </Typography>
        </Box>
        <PreviewModeToggle mode={mode} onChange={setMode} />
      </Box>

      {/* Quality Control Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab icon={<CameraAlt />} label={t('liveAnalysis')} />
          <Tab icon={<Analytics />} label={t('dashboard')} />
          <Tab icon={<Assessment />} label={t('testResults')} />
        </Tabs>
      </Paper>

      {/* Live Analysis Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quality Analysis Setup
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <LookupSelect
                    group="paddy_variety"
                    label={t('variety')}
                    value={selectedVariety}
                    onChange={(e) => setSelectedVariety(e.target.value)}
                    sx={{ mb: 2 }}
                  />
                  
                  <TextField
                    fullWidth
                    label={t('batch')}
                    value={batchId}
                    onChange={(e) => setBatchId(e.target.value)}
                    sx={{ mb: 2 }}
                  />
                </Box>

                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<CameraAlt />}
                    onClick={startCamera}
                    disabled={isAnalyzing}
                  >
                    Use Camera
                  </Button>
                  
                  <Button
                    variant="outlined"
                    startIcon={<CloudUpload />}
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isAnalyzing}
                  >
                    Upload Image
                  </Button>
                </Box>

                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept="image/*"
                  style={{ display: 'none' }}
                />

                {isAnalyzing && (
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress />
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Analyzing rice quality using AI...
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {analysisResult && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Analysis Results
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h4" sx={{ mr: 2 }}>
                        {analysisResult.overall_grade || analysisResult.grade}
                      </Typography>
                      <Chip
                        label={`${Number(analysisResult.quality_score ?? analysisResult.overall_score ?? 0).toFixed(1)}%`}
                        color={getGradeColor(analysisResult.overall_grade || analysisResult.grade)}
                        size="large"
                      />
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary">
                      Overall Quality Score
                    </Typography>
                  </Box>

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Broken Rice
                      </Typography>
                      <Typography variant="h6">
                        {analysisResult.grain_analysis?.broken_percentage?.toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Foreign Matter
                      </Typography>
                      <Typography variant="h6">
                        {analysisResult.foreign_matter?.foreign_matter_percentage?.toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Avg Length
                      </Typography>
                      <Typography variant="h6">
                        {analysisResult.grain_analysis?.average_length?.toFixed(1)}mm
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Moisture Est.
                      </Typography>
                      <Typography variant="h6">
                        {analysisResult.moisture_estimation?.estimated_moisture_percentage?.toFixed(1)}%
                      </Typography>
                    </Grid>
                  </Grid>

                  {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        AI Recommendations:
                      </Typography>
                      {analysisResult.recommendations.slice(0, 2).map((rec, index) => (
                        <Alert key={index} severity="info" sx={{ mb: 1 }}>
                          <Typography variant="body2">
                            {rec.recommendation}
                          </Typography>
                        </Alert>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Dashboard Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          {/* Quality Metrics Cards */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Pass Rate
                    </Typography>
                    <Typography variant="h4" component="div" color="success.main">
                      {qualitySummary.testCount ? `${qualitySummary.passRate.toFixed(1)}%` : '—'}
                    </Typography>
                  </Box>
                  <CheckCircle color="success" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Avg Quality Score
                    </Typography>
                    <Typography variant="h4" component="div" color="primary.main">
                      {qualitySummary.testCount ? qualitySummary.avgScore.toFixed(1) : '—'}
                    </Typography>
                  </Box>
                  <Analytics color="primary" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Tests recorded
                    </Typography>
                    <Typography variant="h4" component="div" color="info.main">
                      {qualitySummary.testCount}
                    </Typography>
                  </Box>
                  <Assessment color="info" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      Tests today
                    </Typography>
                    <Typography variant="h4" component="div" color="secondary.main">
                      {qualitySummary.testsToday}
                    </Typography>
                  </Box>
                  <CheckCircle color="secondary" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Quality Trend Chart */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quality Score Trend
                </Typography>
                {!qualityTrend.length ? (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 6, textAlign: 'center' }}>
                    No quality tests recorded yet.
                  </Typography>
                ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={qualityTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={isSample ? [70, 100] : ['auto', 'auto']} />
                    <Tooltip />
                    <Line type="monotone" dataKey="score" stroke="#2E7D32" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Grade Distribution */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Grade Distribution
                </Typography>
                {!gradeDistribution.length ? (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 6, textAlign: 'center' }}>
                    No grades to chart yet.
                  </Typography>
                ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={gradeDistribution}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {gradeDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Test Results Tab */}
      <TabPanel value={activeTab} index={2}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Quality Tests
            </Typography>
            {testsLoading && <LinearProgress sx={{ mb: 2 }} />}
            {!recentTests.length && !testsLoading && (
              <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                No quality tests on Production yet. Camera previews stay on the Live Analysis tab and do not create mill tests.
              </Typography>
            )}
            {isActual && previewTests.length > 0 && (
              <Alert severity="info" sx={{ mb: 2 }}>
                {previewTests.length} camera preview(s) on this session only — not saved as mill tests.
              </Alert>
            )}
            <TableContainer component={Paper} elevation={0}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Test ID</TableCell>
                    <TableCell>Batch ID</TableCell>
                    <TableCell>Variety</TableCell>
                    <TableCell>Grade</TableCell>
                    <TableCell>Score</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentTests.map((test) => (
                    <TableRow key={test.id}>
                      <TableCell>{test.id}</TableCell>
                      <TableCell>{test.batch_id}</TableCell>
                      <TableCell>{test.variety}</TableCell>
                      <TableCell>
                        <Chip
                          label={test.grade}
                          color={getGradeColor(test.grade)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{test.score}</TableCell>
                      <TableCell>{test.date}</TableCell>
                      <TableCell>
                        <Chip
                          label={test.status}
                          color={test.status === 'verified' ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Button size="small" startIcon={<Visibility />} onClick={() => setViewTest(test)}>
                          View
                        </Button>
                        <Button
                          size="small"
                          startIcon={<GetApp />}
                          onClick={() => {
                            const blob = new Blob([JSON.stringify(test, null, 2)], { type: 'application/json' });
                            const url = URL.createObjectURL(blob);
                            const link = document.createElement('a');
                            link.href = url;
                            link.download = `${test.id}.json`;
                            link.click();
                            URL.revokeObjectURL(url);
                            setPageMessage({ severity: 'success', text: `Downloaded ${test.id}` });
                          }}
                        >
                          Export
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>

      {/* Camera Dialog */}
      <Dialog
        open={showCameraDialog}
        onClose={() => {
          setShowCameraDialog(false);
          stopCamera();
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{t('captureSample')}</DialogTitle>
        <DialogContent>
          <Box sx={{ textAlign: 'center' }}>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              style={{
                width: '100%',
                maxWidth: '500px',
                height: '400px',
                borderRadius: '8px',
                backgroundColor: '#000'
              }}
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            <Typography variant="body2" sx={{ mt: 2 }}>
              {t('cameraHelp')}
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowCameraDialog(false);
            stopCamera();
          }}>
            {t('cancel')}
          </Button>
          <Button
            variant="contained"
            onClick={handleCameraCapture}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? <CircularProgress size={24} /> : t('captureAnalyze')}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(viewTest)} onClose={() => setViewTest(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{viewTest?.id}</DialogTitle>
        <DialogContent>
          {viewTest && (
            <Box sx={{ pt: 1 }}>
              <Typography>{t('batch')}: {viewTest.batch_id}</Typography>
              <Typography>{t('variety')}: {viewTest.variety}</Typography>
              <Typography>{t('grade')}: {viewTest.grade}</Typography>
              <Typography>{t('score')}: {viewTest.score}</Typography>
              <Typography>{t('date')}: {viewTest.date}</Typography>
              <Typography>{t('status')}: {viewTest.status}</Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                {t('cameraPreviewHelp')}
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewTest(null)}>{t('close')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default QualityControl;
