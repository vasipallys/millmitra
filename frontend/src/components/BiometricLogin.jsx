import React, { useState, useRef, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Paper,
  IconButton,
} from '@mui/material';
import {
  Fingerprint,
  Face,
  Mic,
  Close,
  CameraAlt,
  Security,
} from '@mui/icons-material';

const BiometricLogin = ({ open, onClose, onSuccess }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [username, setUsername] = useState('');
  
  // Face recognition states
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  
  // Voice recognition states
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  
  // Fingerprint states
  const [fingerprintData, setFingerprintData] = useState('');

  useEffect(() => {
    if (open && activeTab === 1) {
      startCamera();
    } else {
      stopCamera();
    }
    
    return () => {
      stopCamera();
      stopRecording();
    };
  }, [open, activeTab]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setError('');
    setSuccess('');
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (error) {
      setError('Camera access denied. Please allow camera access for face recognition.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsCameraActive(false);
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

  const handleFaceLogin = async () => {
    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }

    setIsProcessing(true);
    setError('');
    
    try {
      const imageData = captureImage();
      if (!imageData) {
        setError('Failed to capture image');
        return;
      }

      const response = await fetch('/api/biometric/verify/face', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          image: imageData
        })
      });

      const result = await response.json();

      if (result.success) {
        setSuccess('Face verification successful!');
        localStorage.setItem('token', result.token);
        setTimeout(() => {
          onSuccess(result.user);
          onClose();
        }, 1000);
      } else {
        setError(result.error || 'Face verification failed');
      }
    } catch (error) {
      setError('Network error during face verification');
    } finally {
      setIsProcessing(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      
      // Auto-stop after 5 seconds
      setTimeout(() => {
        if (mediaRecorderRef.current && isRecording) {
          stopRecording();
        }
      }, 5000);
      
    } catch (error) {
      setError('Microphone access denied. Please allow microphone access for voice recognition.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleVoiceLogin = async () => {
    if (!audioBlob) {
      setError('Please record your voice first');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice.wav');
      formData.append('device_info', JSON.stringify({
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
      }));

      const response = await fetch('/api/biometric/login/voice', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (result.success) {
        setSuccess('Voice verification successful!');
        localStorage.setItem('token', result.token);
        setTimeout(() => {
          onSuccess({ id: result.user_id, username: result.username });
          onClose();
        }, 1000);
      } else {
        setError(result.error || 'Voice verification failed');
      }
    } catch (error) {
      setError('Network error during voice verification');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFingerprintLogin = async () => {
    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }

    if (!fingerprintData.trim()) {
      setError('Please provide fingerprint data');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const response = await fetch('/api/biometric/verify/fingerprint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          fingerprint_data: fingerprintData
        })
      });

      const result = await response.json();

      if (result.success) {
        setSuccess('Fingerprint verification successful!');
        localStorage.setItem('token', result.token);
        setTimeout(() => {
          onSuccess(result.user);
          onClose();
        }, 1000);
      } else {
        setError(result.error || 'Fingerprint verification failed');
      }
    } catch (error) {
      setError('Network error during fingerprint verification');
    } finally {
      setIsProcessing(false);
    }
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
    </div>
  );

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', color: 'white' }}>
        <Security sx={{ mr: 1 }} />
        Biometric Authentication
        <Box sx={{ flexGrow: 1 }} />
        <IconButton onClick={onClose} sx={{ color: 'white' }}>
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ color: 'white' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            mb: 2,
            '& .MuiTab-root': { color: 'rgba(255,255,255,0.7)' },
            '& .Mui-selected': { color: 'white' },
            '& .MuiTabs-indicator': { backgroundColor: 'white' }
          }}
        >
          <Tab icon={<Fingerprint />} label="Fingerprint" />
          <Tab icon={<Face />} label="Face Recognition" />
          <Tab icon={<Mic />} label="Voice Recognition" />
        </Tabs>

        {error && (
          <Alert severity="error" sx={{ mb: 2, backgroundColor: 'rgba(255,255,255,0.1)' }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2, backgroundColor: 'rgba(255,255,255,0.1)' }}>
            {success}
          </Alert>
        )}

        {/* Fingerprint Tab */}
        <TabPanel value={activeTab} index={0}>
          <Box sx={{ textAlign: 'center' }}>
            <Fingerprint sx={{ fontSize: 80, mb: 2, opacity: 0.8 }} />
            <Typography variant="h6" gutterBottom>
              Fingerprint Authentication
            </Typography>
            <Typography variant="body2" sx={{ mb: 3, opacity: 0.8 }}>
              Place your finger on the scanner and enter your username
            </Typography>
            
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                marginBottom: '16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '16px'
              }}
            />
            
            <input
              type="text"
              placeholder="Fingerprint Data (simulated)"
              value={fingerprintData}
              onChange={(e) => setFingerprintData(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                marginBottom: '16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '16px'
              }}
            />
            
            <Button
              variant="contained"
              onClick={handleFingerprintLogin}
              disabled={isProcessing}
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.3)' }
              }}
            >
              {isProcessing ? <CircularProgress size={24} /> : 'Verify Fingerprint'}
            </Button>
          </Box>
        </TabPanel>

        {/* Face Recognition Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Face Recognition
            </Typography>
            <Typography variant="body2" sx={{ mb: 2, opacity: 0.8 }}>
              Position your face in the camera frame
            </Typography>
            
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                marginBottom: '16px',
                borderRadius: '8px',
                border: 'none',
                fontSize: '16px'
              }}
            />
            
            <Paper sx={{ p: 2, mb: 2, backgroundColor: 'rgba(255,255,255,0.1)' }}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                style={{
                  width: '100%',
                  maxWidth: '400px',
                  height: '300px',
                  borderRadius: '8px',
                  backgroundColor: '#000'
                }}
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </Paper>
            
            <Button
              variant="contained"
              onClick={handleFaceLogin}
              disabled={isProcessing || !isCameraActive}
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.3)' }
              }}
            >
              {isProcessing ? <CircularProgress size={24} /> : 'Verify Face'}
            </Button>
          </Box>
        </TabPanel>

        {/* Voice Recognition Tab */}
        <TabPanel value={activeTab} index={2}>
          <Box sx={{ textAlign: 'center' }}>
            <Mic sx={{ fontSize: 80, mb: 2, opacity: 0.8 }} />
            <Typography variant="h6" gutterBottom>
              Voice Recognition
            </Typography>
            <Typography variant="body2" sx={{ mb: 3, opacity: 0.8 }}>
              Say "My username is [your username]" clearly
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Button
                variant={isRecording ? "outlined" : "contained"}
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isProcessing}
                sx={{
                  backgroundColor: isRecording ? 'transparent' : 'rgba(255,255,255,0.2)',
                  color: 'white',
                  borderColor: 'white',
                  '&:hover': { backgroundColor: 'rgba(255,255,255,0.3)' },
                  mb: 2
                }}
              >
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </Button>
              
              {audioBlob && (
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Voice recorded successfully
                </Typography>
              )}
            </Box>
            
            <Button
              variant="contained"
              onClick={handleVoiceLogin}
              disabled={isProcessing || !audioBlob}
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.3)' }
              }}
            >
              {isProcessing ? <CircularProgress size={24} /> : 'Verify Voice'}
            </Button>
          </Box>
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
};

export default BiometricLogin;
