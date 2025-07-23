import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
  Snackbar,
  Alert,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Close,
  GetApp,
  CloudOff,
  Speed,
  Notifications,
  Security,
  Storage
} from '@mui/icons-material';
import { usePWA } from '../hooks/usePWA';

const PWAInstallPrompt = () => {
  const {
    isInstallable,
    isInstalled,
    updateAvailable,
    installPWA,
    updateServiceWorker,
    isOnline
  } = usePWA();

  const [showInstallDialog, setShowInstallDialog] = useState(false);
  const [showUpdateSnackbar, setShowUpdateSnackbar] = useState(updateAvailable);
  const [installing, setInstalling] = useState(false);

  const handleInstall = async () => {
    setInstalling(true);
    const success = await installPWA();
    setInstalling(false);
    
    if (success) {
      setShowInstallDialog(false);
    }
  };

  const handleUpdate = () => {
    updateServiceWorker();
    setShowUpdateSnackbar(false);
  };

  const features = [
    {
      icon: <CloudOff color="primary" />,
      title: 'Offline Access',
      description: 'Work without internet connection'
    },
    {
      icon: <Speed color="primary" />,
      title: 'Fast Loading',
      description: 'Instant app-like performance'
    },
    {
      icon: <Notifications color="primary" />,
      title: 'Push Notifications',
      description: 'Stay updated with real-time alerts'
    },
    {
      icon: <Security color="primary" />,
      title: 'Secure',
      description: 'Enhanced security and privacy'
    },
    {
      icon: <Storage color="primary" />,
      title: 'Local Storage',
      description: 'Cache data for offline use'
    }
  ];

  // Show install prompt if installable and not installed
  React.useEffect(() => {
    if (isInstallable && !isInstalled) {
      // Show install prompt after a delay
      const timer = setTimeout(() => {
        setShowInstallDialog(true);
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [isInstallable, isInstalled]);

  return (
    <>
      {/* Install Dialog */}
      <Dialog
        open={showInstallDialog}
        onClose={() => setShowInstallDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              📱 Install Smart Mill ERP
            </Typography>
            <IconButton onClick={() => setShowInstallDialog(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Get the full app experience! Install Smart Mill ERP for faster access and offline functionality.
          </Typography>

          <Card sx={{ mt: 2, mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                🌟 App Features:
              </Typography>
              <List dense>
                {features.map((feature, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {feature.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={feature.title}
                      secondary={feature.description}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          <Box sx={{ 
            p: 2, 
            bgcolor: 'primary.light', 
            color: 'primary.contrastText',
            borderRadius: 1,
            textAlign: 'center'
          }}>
            <Typography variant="body2">
              💡 <strong>Pro Tip:</strong> Once installed, you can access the app even without internet!
            </Typography>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setShowInstallDialog(false)}>
            Maybe Later
          </Button>
          <Button
            onClick={handleInstall}
            variant="contained"
            startIcon={<GetApp />}
            disabled={installing}
          >
            {installing ? 'Installing...' : 'Install App'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Update Available Snackbar */}
      <Snackbar
        open={showUpdateSnackbar}
        onClose={() => setShowUpdateSnackbar(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setShowUpdateSnackbar(false)}
          severity="info"
          action={
            <Button color="inherit" size="small" onClick={handleUpdate}>
              Update
            </Button>
          }
        >
          🚀 New version available! Click Update to get the latest features.
        </Alert>
      </Snackbar>

      {/* Offline Status Indicator */}
      {!isOnline && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bgcolor: 'warning.main',
            color: 'warning.contrastText',
            p: 1,
            textAlign: 'center',
            zIndex: 9999
          }}
        >
          <Typography variant="body2">
            📡 You're offline - Some features may be limited
          </Typography>
        </Box>
      )}

      {/* Install Button for Manual Install */}
      {isInstallable && !showInstallDialog && (
        <Box
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            zIndex: 1000
          }}
        >
          <Button
            variant="contained"
            color="primary"
            startIcon={<GetApp />}
            onClick={() => setShowInstallDialog(true)}
            sx={{
              borderRadius: 25,
              px: 3,
              py: 1.5,
              boxShadow: 3
            }}
          >
            Install App
          </Button>
        </Box>
      )}
    </>
  );
};

export default PWAInstallPrompt;
