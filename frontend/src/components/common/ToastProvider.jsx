import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  Snackbar, Alert, AlertTitle, Slide, Grow, Fade,
  Box, Typography, IconButton, Chip, Stack
} from '@mui/material';
import {
  CheckCircle, Error, Warning, Info, Close,
  Person, Inventory, Factory, Analytics,
  Settings, Notifications as NotificationIcon
} from '@mui/icons-material';

// Toast Context
const ToastContext = createContext();

// Toast types with configurations
const TOAST_TYPES = {
  success: {
    severity: 'success',
    icon: CheckCircle,
    color: '#4caf50',
    duration: 4000
  },
  error: {
    severity: 'error',
    icon: Error,
    color: '#f44336',
    duration: 6000
  },
  warning: {
    severity: 'warning',
    icon: Warning,
    color: '#ff9800',
    duration: 5000
  },
  info: {
    severity: 'info',
    icon: Info,
    color: '#2196f3',
    duration: 4000
  }
};

// Module icons mapping
const MODULE_ICONS = {
  farmer: Person,
  inventory: Inventory,
  production: Factory,
  analytics: Analytics,
  settings: Settings,
  notifications: NotificationIcon,
  general: Info
};

// Transition components
const SlideTransition = (props) => <Slide {...props} direction="up" />;
const GrowTransition = (props) => <Grow {...props} />;
const FadeTransition = (props) => <Fade {...props} />;

const TRANSITIONS = {
  slide: SlideTransition,
  grow: GrowTransition,
  fade: FadeTransition
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const showToast = useCallback((options) => {
    const {
      type = 'info',
      title,
      message,
      module = 'general',
      field = null,
      action = null,
      duration = null,
      transition = 'slide',
      persistent = false,
      details = null,
      onAction = null
    } = options;

    const toastConfig = TOAST_TYPES[type];
    const id = Date.now() + Math.random();

    const toast = {
      id,
      type,
      title,
      message,
      module,
      field,
      action,
      duration: persistent ? null : (duration || toastConfig.duration),
      transition,
      details,
      onAction,
      severity: toastConfig.severity,
      icon: toastConfig.icon,
      color: toastConfig.color,
      timestamp: new Date()
    };

    setToasts(prev => [...prev, toast]);

    // Auto-remove non-persistent toasts
    if (!persistent && toast.duration) {
      setTimeout(() => {
        removeToast(id);
      }, toast.duration);
    }

    return id;
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const clearAllToasts = useCallback(() => {
    setToasts([]);
  }, []);

  // Predefined toast methods for common scenarios
  const success = useCallback((message, options = {}) => {
    return showToast({
      type: 'success',
      title: options.title || 'Success',
      message,
      ...options
    });
  }, [showToast]);

  const error = useCallback((message, options = {}) => {
    return showToast({
      type: 'error',
      title: options.title || 'Error',
      message,
      ...options
    });
  }, [showToast]);

  const warning = useCallback((message, options = {}) => {
    return showToast({
      type: 'warning',
      title: options.title || 'Warning',
      message,
      ...options
    });
  }, [showToast]);

  const info = useCallback((message, options = {}) => {
    return showToast({
      type: 'info',
      title: options.title || 'Information',
      message,
      ...options
    });
  }, [showToast]);

  // Field-specific toast methods
  const fieldSuccess = useCallback((field, message, options = {}) => {
    return success(message, {
      field,
      title: `${field} Updated`,
      ...options
    });
  }, [success]);

  const fieldError = useCallback((field, message, options = {}) => {
    return error(message, {
      field,
      title: `${field} Error`,
      ...options
    });
  }, [error]);

  // Action-specific toast methods
  const actionSuccess = useCallback((action, message, options = {}) => {
    return success(message, {
      action,
      title: `${action} Successful`,
      ...options
    });
  }, [success]);

  const actionError = useCallback((action, message, options = {}) => {
    return error(message, {
      action,
      title: `${action} Failed`,
      ...options
    });
  }, [error]);

  const value = {
    showToast,
    removeToast,
    clearAllToasts,
    success,
    error,
    warning,
    info,
    fieldSuccess,
    fieldError,
    actionSuccess,
    actionError,
    toasts
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
};

// Toast Container Component
const ToastContainer = ({ toasts, removeToast }) => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 80,
        right: 20,
        zIndex: 9999,
        maxWidth: 400,
        width: '100%'
      }}
    >
      <Stack spacing={1}>
        {toasts.map((toast) => (
          <ToastItem
            key={toast.id}
            toast={toast}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </Stack>
    </Box>
  );
};

// Individual Toast Item Component
const ToastItem = ({ toast, onClose }) => {
  const TransitionComponent = TRANSITIONS[toast.transition] || SlideTransition;
  const ModuleIcon = MODULE_ICONS[toast.module] || Info;
  const ToastIcon = toast.icon;

  const handleAction = () => {
    if (toast.onAction) {
      toast.onAction();
    }
    onClose();
  };

  return (
    <TransitionComponent in={true} timeout={300}>
      <Alert
        severity={toast.severity}
        onClose={onClose}
        sx={{
          width: '100%',
          boxShadow: 3,
          borderRadius: 2,
          '& .MuiAlert-message': {
            width: '100%'
          }
        }}
        icon={<ToastIcon />}
        action={
          <IconButton
            size="small"
            onClick={onClose}
            sx={{ color: 'inherit' }}
          >
            <Close fontSize="small" />
          </IconButton>
        }
      >
        <Box>
          {/* Header with title and module */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <ModuleIcon sx={{ fontSize: 16 }} />
            <AlertTitle sx={{ margin: 0, fontSize: '0.875rem' }}>
              {toast.title}
            </AlertTitle>
            {toast.module !== 'general' && (
              <Chip
                label={toast.module}
                size="small"
                sx={{
                  height: 20,
                  fontSize: '0.75rem',
                  textTransform: 'capitalize'
                }}
              />
            )}
          </Box>

          {/* Main message */}
          <Typography variant="body2" sx={{ mb: 1 }}>
            {toast.message}
          </Typography>

          {/* Field and action tags */}
          {(toast.field || toast.action) && (
            <Box sx={{ display: 'flex', gap: 0.5, mb: 1 }}>
              {toast.field && (
                <Chip
                  label={`Field: ${toast.field}`}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem', height: 18 }}
                />
              )}
              {toast.action && (
                <Chip
                  label={`Action: ${toast.action}`}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem', height: 18 }}
                />
              )}
            </Box>
          )}

          {/* Additional details */}
          {toast.details && (
            <Typography variant="caption" color="text.secondary">
              {toast.details}
            </Typography>
          )}

          {/* Action button if provided */}
          {toast.onAction && (
            <Box sx={{ mt: 1 }}>
              <Typography
                variant="caption"
                sx={{
                  color: toast.color,
                  cursor: 'pointer',
                  textDecoration: 'underline'
                }}
                onClick={handleAction}
              >
                Click to view details
              </Typography>
            </Box>
          )}
        </Box>
      </Alert>
    </TransitionComponent>
  );
};

// Hook to use toast
export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

export default ToastProvider;
