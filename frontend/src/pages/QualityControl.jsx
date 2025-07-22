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
  MenuItem,
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

const QualityControl = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [showCameraDialog, setShowCameraDialog] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [recentTests, setRecentTests] = useState([]);
  const [qualityTrend, setQualityTrend] = useState([]);
  const [selectedVariety, setSelectedVariety] = useState('basmati');
  const [batchId, setBatchId] = useState('');
  
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

  const gradeDistribution = [
    { name: 'Grade A', value: 45, color: '#4CAF50' },
    { name: 'Grade B', value: 30, color: '#FF9800' },
    { name: 'Grade C', value: 20, color: '#FFC107' },
    { name: 'Grade D', value: 4, color: '#FF5722' },
    { name: 'Grade E', value: 1, color: '#F44336' },
  ];

  useEffect(() => {
    setQualityTrend(mockQualityTrend);
    setRecentTests(mockRecentTests);
  }, []);

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
      alert('Camera access denied. Please allow camera access for quality analysis.');
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
    
    try {
      const response = await fetch('/api/quality-vision/analyze/image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          image: imageData,
          variety: selectedVariety,
          batch_id: batchId || null,
          sample_type: 'manual_test'
        })
      });

      const result = await response.json();

      if (result.success) {
        setAnalysisResult(result.analysis);
        setShowCameraDialog(false);
        stopCamera();
      } else {
        alert('Analysis failed: ' + result.error);
      }
    } catch (error) {
      alert('Network error during analysis');
    } finally {
      setIsAnalyzing(false);
    }
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
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          AI Quality Control
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Computer vision-powered rice quality assessment
        </Typography>
      </Box>

      {/* Quality Control Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab icon={<CameraAlt />} label="Live Analysis" />
          <Tab icon={<Analytics />} label="Dashboard" />
          <Tab icon={<Assessment />} label="Test Results" />
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
                  <TextField
                    fullWidth
                    select
                    label="Rice Variety"
                    value={selectedVariety}
                    onChange={(e) => setSelectedVariety(e.target.value)}
                    sx={{ mb: 2 }}
                  >
                    <MenuItem value="basmati">Basmati Rice</MenuItem>
                    <MenuItem value="jasmine">Jasmine Rice</MenuItem>
                    <MenuItem value="brown">Brown Rice</MenuItem>
                  </TextField>
                  
                  <TextField
                    fullWidth
                    label="Batch ID (Optional)"
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
                        {analysisResult.overall_grade}
                      </Typography>
                      <Chip
                        label={`${analysisResult.quality_score?.toFixed(1)}%`}
                        color={getGradeColor(analysisResult.overall_grade)}
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
                      94.2%
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
                      89.7
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
                      Tests Today
                    </Typography>
                    <Typography variant="h4" component="div" color="info.main">
                      23
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
                      AI Accuracy
                    </Typography>
                    <Typography variant="h4" component="div" color="secondary.main">
                      96.8%
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
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={qualityTrend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis domain={[70, 100]} />
                    <Tooltip />
                    <Line type="monotone" dataKey="score" stroke="#2E7D32" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
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
                        <Button size="small" startIcon={<Visibility />}>
                          View
                        </Button>
                        <Button size="small" startIcon={<GetApp />}>
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
        <DialogTitle>Capture Rice Sample</DialogTitle>
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
              Position rice sample in the camera frame and click capture
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowCameraDialog(false);
            stopCamera();
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleCameraCapture}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? <CircularProgress size={24} /> : 'Capture & Analyze'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default QualityControl;
