/**
 * Predefined toast messages for consistent user feedback across all modules
 */

// Farmer Management Messages
export const FARMER_MESSAGES = {
  // Success messages
  FARMER_CREATED: {
    type: 'success',
    title: 'Farmer Added',
    message: 'New farmer has been successfully added to the system',
    module: 'farmer',
    action: 'Create'
  },
  FARMER_UPDATED: {
    type: 'success',
    title: 'Farmer Updated',
    message: 'Farmer information has been successfully updated',
    module: 'farmer',
    action: 'Update'
  },
  FARMER_DELETED: {
    type: 'success',
    title: 'Farmer Removed',
    message: 'Farmer has been successfully removed from the system',
    module: 'farmer',
    action: 'Delete'
  },
  EDIT_REQUEST_SUBMITTED: {
    type: 'success',
    title: 'Edit Request Submitted',
    message: 'Your edit request has been submitted for approval',
    module: 'farmer',
    action: 'Edit Request'
  },
  EDIT_REQUEST_APPROVED: {
    type: 'success',
    title: 'Edit Request Approved',
    message: 'Edit request has been approved and changes applied',
    module: 'farmer',
    action: 'Approve'
  },
  EDIT_REQUEST_REJECTED: {
    type: 'warning',
    title: 'Edit Request Rejected',
    message: 'Edit request has been rejected',
    module: 'farmer',
    action: 'Reject'
  },

  // Error messages
  FARMER_CREATE_ERROR: {
    type: 'error',
    title: 'Failed to Add Farmer',
    message: 'Unable to add farmer. Please check the information and try again',
    module: 'farmer',
    action: 'Create'
  },
  FARMER_UPDATE_ERROR: {
    type: 'error',
    title: 'Failed to Update Farmer',
    message: 'Unable to update farmer information. Please try again',
    module: 'farmer',
    action: 'Update'
  },
  FARMER_DELETE_ERROR: {
    type: 'error',
    title: 'Failed to Remove Farmer',
    message: 'Unable to remove farmer. Please try again',
    module: 'farmer',
    action: 'Delete'
  },

  // Field-specific messages
  PHONE_INVALID: {
    type: 'error',
    title: 'Invalid Phone Number',
    message: 'Please enter a valid phone number',
    module: 'farmer',
    field: 'Phone'
  },
  EMAIL_INVALID: {
    type: 'error',
    title: 'Invalid Email',
    message: 'Please enter a valid email address',
    module: 'farmer',
    field: 'Email'
  },
  AADHAR_INVALID: {
    type: 'error',
    title: 'Invalid Aadhar Number',
    message: 'Please enter a valid 12-digit Aadhar number',
    module: 'farmer',
    field: 'Aadhar'
  }
};

// Inventory Management Messages
export const INVENTORY_MESSAGES = {
  // Success messages
  STOCK_ADDED: {
    type: 'success',
    title: 'Stock Added',
    message: 'New stock has been successfully added to inventory',
    module: 'inventory',
    action: 'Add Stock'
  },
  STOCK_UPDATED: {
    type: 'success',
    title: 'Stock Updated',
    message: 'Stock information has been successfully updated',
    module: 'inventory',
    action: 'Update Stock'
  },
  STOCK_MOVEMENT_RECORDED: {
    type: 'success',
    title: 'Movement Recorded',
    message: 'Stock movement has been successfully recorded',
    module: 'inventory',
    action: 'Stock Movement'
  },
  LOW_STOCK_ALERT: {
    type: 'warning',
    title: 'Low Stock Alert',
    message: 'Some items are running low in stock',
    module: 'inventory',
    action: 'Alert'
  },

  // Error messages
  STOCK_ADD_ERROR: {
    type: 'error',
    title: 'Failed to Add Stock',
    message: 'Unable to add stock. Please check the information and try again',
    module: 'inventory',
    action: 'Add Stock'
  },
  INSUFFICIENT_STOCK: {
    type: 'error',
    title: 'Insufficient Stock',
    message: 'Not enough stock available for this operation',
    module: 'inventory',
    action: 'Stock Check'
  }
};

// Production Management Messages
export const PRODUCTION_MESSAGES = {
  BATCH_STARTED: {
    type: 'success',
    title: 'Production Batch Started',
    message: 'New production batch has been initiated',
    module: 'production',
    action: 'Start Batch'
  },
  BATCH_COMPLETED: {
    type: 'success',
    title: 'Production Batch Completed',
    message: 'Production batch has been successfully completed',
    module: 'production',
    action: 'Complete Batch'
  },
  QUALITY_CHECK_PASSED: {
    type: 'success',
    title: 'Quality Check Passed',
    message: 'Product has passed quality inspection',
    module: 'production',
    action: 'Quality Check'
  },
  QUALITY_CHECK_FAILED: {
    type: 'error',
    title: 'Quality Check Failed',
    message: 'Product did not meet quality standards',
    module: 'production',
    action: 'Quality Check'
  }
};

// User Management Messages
export const USER_MESSAGES = {
  PROFILE_UPDATED: {
    type: 'success',
    title: 'Profile Updated',
    message: 'Your profile has been successfully updated',
    module: 'settings',
    action: 'Update Profile'
  },
  PASSWORD_CHANGED: {
    type: 'success',
    title: 'Password Changed',
    message: 'Your password has been successfully changed',
    module: 'settings',
    action: 'Change Password'
  },
  LOGIN_SUCCESS: {
    type: 'success',
    title: 'Login Successful',
    message: 'Welcome back! You have been successfully logged in',
    module: 'general',
    action: 'Login'
  },
  LOGOUT_SUCCESS: {
    type: 'info',
    title: 'Logged Out',
    message: 'You have been successfully logged out',
    module: 'general',
    action: 'Logout'
  },
  SESSION_EXPIRED: {
    type: 'warning',
    title: 'Session Expired',
    message: 'Your session has expired. Please log in again',
    module: 'general',
    action: 'Session'
  }
};

// Notification Messages
export const NOTIFICATION_MESSAGES = {
  MARKED_AS_READ: {
    type: 'success',
    title: 'Notification Read',
    message: 'Notification has been marked as read',
    module: 'notifications',
    action: 'Mark Read'
  },
  ALL_MARKED_AS_READ: {
    type: 'success',
    title: 'All Notifications Read',
    message: 'All notifications have been marked as read',
    module: 'notifications',
    action: 'Mark All Read'
  },
  NOTIFICATION_DELETED: {
    type: 'success',
    title: 'Notification Deleted',
    message: 'Notification has been successfully deleted',
    module: 'notifications',
    action: 'Delete'
  }
};

// Analytics Messages
export const ANALYTICS_MESSAGES = {
  REPORT_GENERATED: {
    type: 'success',
    title: 'Report Generated',
    message: 'Analytics report has been successfully generated',
    module: 'analytics',
    action: 'Generate Report'
  },
  DATA_EXPORTED: {
    type: 'success',
    title: 'Data Exported',
    message: 'Data has been successfully exported',
    module: 'analytics',
    action: 'Export Data'
  },
  FORECAST_UPDATED: {
    type: 'info',
    title: 'Forecast Updated',
    message: 'Demand forecast has been updated with latest data',
    module: 'analytics',
    action: 'Update Forecast'
  }
};

// General System Messages
export const SYSTEM_MESSAGES = {
  SAVE_SUCCESS: {
    type: 'success',
    title: 'Saved Successfully',
    message: 'Your changes have been saved',
    module: 'general',
    action: 'Save'
  },
  SAVE_ERROR: {
    type: 'error',
    title: 'Save Failed',
    message: 'Unable to save changes. Please try again',
    module: 'general',
    action: 'Save'
  },
  LOADING: {
    type: 'info',
    title: 'Loading',
    message: 'Please wait while we load your data',
    module: 'general',
    action: 'Load'
  },
  NETWORK_ERROR: {
    type: 'error',
    title: 'Network Error',
    message: 'Unable to connect to server. Please check your connection',
    module: 'general',
    action: 'Network'
  },
  VALIDATION_ERROR: {
    type: 'error',
    title: 'Validation Error',
    message: 'Please check the form for errors and try again',
    module: 'general',
    action: 'Validation'
  },
  PERMISSION_DENIED: {
    type: 'error',
    title: 'Permission Denied',
    message: 'You do not have permission to perform this action',
    module: 'general',
    action: 'Permission'
  }
};

// Helper function to create custom field messages
export const createFieldMessage = (field, type, message, module = 'general') => ({
  type,
  title: `${field} ${type === 'success' ? 'Updated' : 'Error'}`,
  message,
  module,
  field
});

// Helper function to create custom action messages
export const createActionMessage = (action, type, message, module = 'general') => ({
  type,
  title: `${action} ${type === 'success' ? 'Successful' : 'Failed'}`,
  message,
  module,
  action
});

// Validation messages for common fields
export const VALIDATION_MESSAGES = {
  REQUIRED_FIELD: (field) => ({
    type: 'error',
    title: 'Required Field',
    message: `${field} is required`,
    field
  }),
  INVALID_FORMAT: (field, format) => ({
    type: 'error',
    title: 'Invalid Format',
    message: `${field} must be in ${format} format`,
    field
  }),
  MIN_LENGTH: (field, length) => ({
    type: 'error',
    title: 'Too Short',
    message: `${field} must be at least ${length} characters`,
    field
  }),
  MAX_LENGTH: (field, length) => ({
    type: 'error',
    title: 'Too Long',
    message: `${field} cannot exceed ${length} characters`,
    field
  }),
  INVALID_RANGE: (field, min, max) => ({
    type: 'error',
    title: 'Invalid Range',
    message: `${field} must be between ${min} and ${max}`,
    field
  })
};

// Export all message categories
export const TOAST_MESSAGES = {
  FARMER: FARMER_MESSAGES,
  INVENTORY: INVENTORY_MESSAGES,
  PRODUCTION: PRODUCTION_MESSAGES,
  USER: USER_MESSAGES,
  NOTIFICATION: NOTIFICATION_MESSAGES,
  ANALYTICS: ANALYTICS_MESSAGES,
  SYSTEM: SYSTEM_MESSAGES,
  VALIDATION: VALIDATION_MESSAGES
};
