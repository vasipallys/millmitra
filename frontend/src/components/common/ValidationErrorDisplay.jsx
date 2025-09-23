import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  IconButton
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';

const ValidationErrorDisplay = ({ 
  errors = [], 
  warnings = [], 
  title = "Validation Errors",
  showDetails = true,
  onClose,
  sx = {}
}) => {
  const [expanded, setExpanded] = React.useState(true);
  
  // Don't render if no errors or warnings
  if (errors.length === 0 && warnings.length === 0) {
    return null;
  }

  const hasErrors = errors.length > 0;
  const hasWarnings = warnings.length > 0;

  return (
    <Box sx={{ mb: 2, ...sx }}>
      <Alert 
        severity={hasErrors ? "error" : "warning"}
        onClose={onClose}
        action={
          showDetails && (
            <IconButton
              aria-label="toggle details"
              color="inherit"
              size="small"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          )
        }
        sx={{
          '& .MuiAlert-message': {
            width: '100%'
          }
        }}
      >
        <AlertTitle>
          {title} ({errors.length + warnings.length} issue{errors.length + warnings.length !== 1 ? 's' : ''})
        </AlertTitle>
        
        {!showDetails && (
          <Typography variant="body2">
            Please fix the highlighted fields below to continue.
          </Typography>
        )}

        <Collapse in={expanded && showDetails}>
          <Box sx={{ mt: 1 }}>
            {hasErrors && (
              <Box sx={{ mb: hasWarnings ? 2 : 0 }}>
                <Typography variant="subtitle2" color="error" sx={{ mb: 1, fontWeight: 'bold' }}>
                  Errors ({errors.length}):
                </Typography>
                <List dense sx={{ py: 0 }}>
                  {errors.map((error, index) => (
                    <ListItem key={`error-${index}`} sx={{ py: 0.5, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <ErrorIcon color="error" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" color="error">
                            <strong>{error.field}:</strong> {error.message}
                          </Typography>
                        }
                        secondary={error.details && (
                          <Typography variant="caption" color="error.dark">
                            {error.details}
                          </Typography>
                        )}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {hasWarnings && (
              <Box>
                <Typography variant="subtitle2" color="warning.main" sx={{ mb: 1, fontWeight: 'bold' }}>
                  Warnings ({warnings.length}):
                </Typography>
                <List dense sx={{ py: 0 }}>
                  {warnings.map((warning, index) => (
                    <ListItem key={`warning-${index}`} sx={{ py: 0.5, px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <WarningIcon color="warning" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2" color="warning.main">
                            <strong>{warning.field}:</strong> {warning.message}
                          </Typography>
                        }
                        secondary={warning.details && (
                          <Typography variant="caption" color="warning.dark">
                            {warning.details}
                          </Typography>
                        )}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Box>
        </Collapse>
      </Alert>
    </Box>
  );
};

// Helper function to create validation error objects
export const createValidationError = (field, message, details = null) => ({
  field,
  message,
  details
});

// Helper function to create validation warning objects
export const createValidationWarning = (field, message, details = null) => ({
  field,
  message,
  details
});

// Hook for managing validation state
export const useValidation = () => {
  const [errors, setErrors] = React.useState([]);
  const [warnings, setWarnings] = React.useState([]);

  const addError = (field, message, details = null) => {
    const error = createValidationError(field, message, details);
    setErrors(prev => {
      // Remove existing error for this field
      const filtered = prev.filter(e => e.field !== field);
      return [...filtered, error];
    });
  };

  const addWarning = (field, message, details = null) => {
    const warning = createValidationWarning(field, message, details);
    setWarnings(prev => {
      // Remove existing warning for this field
      const filtered = prev.filter(w => w.field !== field);
      return [...filtered, warning];
    });
  };

  const removeError = (field) => {
    setErrors(prev => prev.filter(e => e.field !== field));
  };

  const removeWarning = (field) => {
    setWarnings(prev => prev.filter(w => w.field !== field));
  };

  const clearErrors = () => setErrors([]);
  const clearWarnings = () => setWarnings([]);
  const clearAll = () => {
    clearErrors();
    clearWarnings();
  };

  const hasErrors = errors.length > 0;
  const hasWarnings = warnings.length > 0;
  const hasIssues = hasErrors || hasWarnings;

  return {
    errors,
    warnings,
    hasErrors,
    hasWarnings,
    hasIssues,
    addError,
    addWarning,
    removeError,
    removeWarning,
    clearErrors,
    clearWarnings,
    clearAll
  };
};

export default ValidationErrorDisplay;
