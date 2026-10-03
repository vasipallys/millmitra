import React, { useState } from 'react';
import {
  Button,
  Typography,
  Box,
  Snackbar,
  Alert,
} from '@mui/material';
import { GetApp } from '@mui/icons-material';
import { usePWA } from '../hooks/usePWA';

const PWAInstallPrompt = () => {
  const {
    isInstallable,
    isInstalled,
    updateAvailable,
    installPWA,
    updateServiceWorker,
    isOnline,
  } = usePWA();

  const [installing, setInstalling] = useState(false);
  const [showUpdateSnackbar, setShowUpdateSnackbar] = useState(false);

  React.useEffect(() => {
    setShowUpdateSnackbar(updateAvailable);
  }, [updateAvailable]);

  const handleInstall = async () => {
    setInstalling(true);
    await installPWA();
    setInstalling(false);
  };

  return (
    <>
      <Snackbar
        open={showUpdateSnackbar}
        onClose={() => setShowUpdateSnackbar(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setShowUpdateSnackbar(false)}
          severity="info"
          action={(
            <Button color="inherit" size="small" onClick={updateServiceWorker}>
              Reload
            </Button>
          )}
        >
          A newer MillMitra build is ready.
        </Alert>
      </Snackbar>

      {!isOnline && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bgcolor: 'warning.main',
            color: 'warning.contrastText',
            px: 2,
            py: 1,
            textAlign: 'center',
            zIndex: 9999,
          }}
        >
          <Typography variant="body2">
            You are offline. Live mill data needs a connection.
          </Typography>
        </Box>
      )}

      {isInstallable && !isInstalled && (
        <Box
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            zIndex: 1000,
          }}
        >
          <Button
            variant="contained"
            color="primary"
            startIcon={<GetApp />}
            onClick={handleInstall}
            disabled={installing}
            aria-label="Install MillMitra"
            sx={{
              borderRadius: 2,
              px: 2.5,
              py: 1,
              boxShadow: 3,
            }}
          >
            {installing ? 'Installing…' : 'Install MillMitra'}
          </Button>
        </Box>
      )}
    </>
  );
};

export default PWAInstallPrompt;
