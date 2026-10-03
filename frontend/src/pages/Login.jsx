import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, TextField, Button, Typography,
  Alert, CircularProgress, Tabs, Tab, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import { Mic, MicOff, Fingerprint, Face, Visibility, VisibilityOff } from '@mui/icons-material';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';
import { useBiometric } from '../hooks/useBiometric';
import { authService } from '../services/authService';
import BiometricLogin from '../components/BiometricLogin';

const Login = ({ onLogin }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [otpCode, setOtpCode] = useState('');
  const [otpMethod, setOtpMethod] = useState('');
  const [showBiometricLogin, setShowBiometricLogin] = useState(false);

  // Voice recognition hook
  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript
  } = useVoiceRecognition();

  // Biometric hook
  const { captureFingerprint, captureFace } = useBiometric();

  // AI-powered username suggestions
  const [usernameSuggestions, setUsernameSuggestions] = useState([]);

  useEffect(() => {
    if (transcript) {
      // Extract login command from voice
      const voiceLogin = extractLoginFromVoice(transcript);
      if (voiceLogin) {
        handleVoiceLogin(voiceLogin);
      }
    }
  }, [transcript]);

  const extractLoginFromVoice = (text) => {
    const patterns = [
      /login as (\w+)/i,
      /i am (\w+)/i,
      /(\w+) here/i,
      /this is (\w+)/i
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        return match[1];
      }
    }
    return null;
  };

  const handleUsernameChange = async (value) => {
    setFormData({ ...formData, username: value });
    
    // AI-powered username suggestions and typo correction
    if (value.length > 2) {
      try {
        const suggestions = await authService.getUsernameSuggestions(value);
        setUsernameSuggestions(suggestions);
      } catch (error) {
        console.error('Error getting suggestions:', error);
      }
    } else {
      setUsernameSuggestions([]);
    }
  };

  const handlePasswordLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const deviceInfo = await getDeviceInfo();
      const result = await authService.login({
        username: formData.username,
        password: formData.password,
        method: 'password',
        device_info: deviceInfo
      });

      if (result.requires_2fa) {
        setRequires2FA(true);
        setOtpMethod(result.method);
      } else {
        localStorage.setItem('token', result.access_token);
        localStorage.setItem('user', JSON.stringify(result.user));
        // Call the onLogin callback to update App state immediately
        if (onLogin) {
          onLogin(result.user);
        }
        navigate('/', { replace: true });
      }
    } catch (error) {
      setError(error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceLogin = async (username) => {
    setLoading(true);
    setError('');

    try {
      const deviceInfo = await getDeviceInfo();
      const audioBlob = await recordVoiceForAuthentication();
      
      const result = await authService.voiceLogin({
        username,
        voice_data: audioBlob,
        device_info: deviceInfo
      });

      if (result.requires_2fa) {
        setRequires2FA(true);
        setOtpMethod(result.method);
        setFormData({ ...formData, username });
      } else {
        localStorage.setItem('token', result.access_token);
        localStorage.setItem('user', JSON.stringify(result.user));
        // Call the onLogin callback to update App state immediately
        if (onLogin) {
          onLogin(result.user);
        }
        navigate('/', { replace: true });
      }
    } catch (error) {
      setError(error.message || 'Voice login failed');
    } finally {
      setLoading(false);
      resetTranscript();
    }
  };

  const handleBiometricLogin = async (type) => {
    setLoading(true);
    setError('');

    try {
      const deviceInfo = await getDeviceInfo();
      let biometricData;

      if (type === 'fingerprint') {
        biometricData = await captureFingerprint();
      } else if (type === 'face') {
        biometricData = await captureFace();
      }

      const result = await authService.biometricLogin({
        username: formData.username,
        biometric_data: biometricData,
        biometric_type: type,
        device_info: deviceInfo
      });

      if (result.requires_2fa) {
        setRequires2FA(true);
        setOtpMethod(result.method);
      } else {
        localStorage.setItem('token', result.access_token);
        localStorage.setItem('user', JSON.stringify(result.user));
        // Call the onLogin callback to update App state immediately
        if (onLogin) {
          onLogin(result.user);
        }
        navigate('/', { replace: true });
      }
    } catch (error) {
      setError(error.message || 'Biometric login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleOTPVerification = async () => {
    try {
      const result = await authService.verifyOTP({
        username: formData.username,
        otp: otpCode,
        device_info: await getDeviceInfo(),
      });

      if (result.access_token && result.user) {
        if (onLogin) {
          onLogin(result.user);
        }
        navigate('/', { replace: true });
        return;
      }
      setError('Invalid OTP');
    } catch (error) {
      setError('Invalid OTP');
    }
  };

  const handleBiometricSuccess = (user) => {
    setShowBiometricLogin(false);
    onLogin(user);
  };

  const getDeviceInfo = async () => {
    return {
      user_agent: navigator.userAgent,
      screen_resolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      has_camera: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      has_microphone: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      fingerprint: await generateDeviceFingerprint()
    };
  };

  const generateDeviceFingerprint = async () => {
    // Generate unique device fingerprint
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillText('Device fingerprint', 2, 2);
    
    return btoa(JSON.stringify({
      canvas: canvas.toDataURL(),
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform,
      cookieEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack
    }));
  };

  const recordVoiceForAuthentication = async () => {
    return new Promise((resolve, reject) => {
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          const mediaRecorder = new MediaRecorder(stream);
          const chunks = [];

          mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
          mediaRecorder.onstop = () => {
            const blob = new Blob(chunks, { type: 'audio/wav' });
            resolve(blob);
          };

          mediaRecorder.start();
          setTimeout(() => mediaRecorder.stop(), 3000); // 3 seconds
        })
        .catch(reject);
    });
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ background: 'linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%)' }}
    >
      <Card sx={{ maxWidth: 400, width: '100%', m: 2 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" align="center" gutterBottom color="primary">
            Rice Mill AI
          </Typography>
          <Typography variant="subtitle1" align="center" color="textSecondary" mb={1}>
            Sign in to MillMitra
          </Typography>
          <Typography variant="body2" align="center" color="text.secondary" mb={3}>
            Use the Password tab for daily work. Voice and Biometric are experimental.
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2 }} role="alert">{error}</Alert>}

          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }} aria-label="Sign-in method">
            <Tab label="Password" />
            <Tab label="Voice" />
            <Tab label="Biometric" />
          </Tabs>

          {/* Password Login */}
          {activeTab === 0 && (
            <form onSubmit={handlePasswordLogin}>
              <TextField
                fullWidth
                label="Username / Email / Phone"
                value={formData.username}
                onChange={(e) => handleUsernameChange(e.target.value)}
                margin="normal"
                autoComplete="username"
                required
                autoFocus
                helperText="Username, email, or 10-digit phone"
              />
              
              {usernameSuggestions.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption">Suggestions:</Typography>
                  {usernameSuggestions.map((suggestion, index) => (
                    <Button
                      key={index}
                      size="small"
                      onClick={() => setFormData({ ...formData, username: suggestion })}
                      sx={{ mr: 1, mt: 0.5 }}
                    >
                      {suggestion}
                    </Button>
                  ))}
                </Box>
              )}

              <TextField
                fullWidth
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                margin="normal"
                autoComplete="current-password"
                required
                InputProps={{
                  endAdornment: (
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  )
                }}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{ mt: 3, mb: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Login'}
              </Button>
            </form>
          )}

          {/* Voice Login */}
          {activeTab === 1 && (
            <Box textAlign="center">
              <Alert severity="info" sx={{ mb: 2, textAlign: 'left' }}>
                Experimental. Use Password for mill sign-in.
              </Alert>
              <Typography variant="body2" color="textSecondary" mb={2}>
                Say "Login as [your username]" or "I am [your username]"
              </Typography>
              
              <IconButton
                size="large"
                aria-label={isListening ? 'Stop voice prompt' : 'Start voice prompt'}
                onClick={isListening ? stopListening : startListening}
                sx={{
                  bgcolor: isListening ? 'error.main' : 'primary.main',
                  color: 'white',
                  mb: 2,
                  '&:hover': {
                    bgcolor: isListening ? 'error.dark' : 'primary.dark'
                  }
                }}
              >
                {isListening ? <MicOff /> : <Mic />}
              </IconButton>
              
              <Typography variant="body2">
                {isListening ? 'Listening...' : 'Click to speak'}
              </Typography>
              
              {transcript && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  You said: "{transcript}"
                </Alert>
              )}
            </Box>
          )}

          {/* Biometric Login */}
          {activeTab === 2 && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                Experimental. Use Password for mill sign-in.
              </Alert>
              <TextField
                fullWidth
                label="Username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                margin="normal"
                required
              />
              
              <Box display="flex" gap={2} mt={2}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Fingerprint />}
                  onClick={() => setShowBiometricLogin(true)}
                  disabled={loading}
                >
                  Biometric Login
                </Button>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* 2FA Dialog */}
      <Dialog open={requires2FA} onClose={() => setRequires2FA(false)}>
        <DialogTitle>Two-Factor Authentication</DialogTitle>
        <DialogContent>
          <Typography variant="body2" mb={2}>
            Enter the OTP sent to your {otpMethod}
          </Typography>
          <TextField
            fullWidth
            label="OTP Code"
            value={otpCode}
            onChange={(e) => setOtpCode(e.target.value)}
            inputProps={{ maxLength: 6 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRequires2FA(false)}>Cancel</Button>
          <Button onClick={handleOTPVerification} variant="contained">
            Verify
          </Button>
        </DialogActions>
      </Dialog>

      {/* Biometric Login Dialog */}
      <BiometricLogin
        open={showBiometricLogin}
        onClose={() => setShowBiometricLogin(false)}
        onSuccess={handleBiometricSuccess}
      />
    </Box>
  );
};

export default Login;