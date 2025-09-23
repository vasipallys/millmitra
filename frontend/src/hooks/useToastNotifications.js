import { useToast } from '../components/common/ToastProvider';
import { TOAST_MESSAGES } from '../utils/toastMessages';

/**
 * Enhanced toast hook with predefined messages and smart error handling
 */
export const useToastNotifications = () => {
  const toast = useToast();

  // Farmer-related notifications
  const farmer = {
    created: (farmerName) => toast.success(
      `Farmer "${farmerName}" has been successfully added`,
      { ...TOAST_MESSAGES.FARMER.FARMER_CREATED, details: `Name: ${farmerName}` }
    ),
    
    updated: (farmerName, field = null) => toast.success(
      field 
        ? `${field} updated for farmer "${farmerName}"`
        : `Farmer "${farmerName}" has been successfully updated`,
      { 
        ...TOAST_MESSAGES.FARMER.FARMER_UPDATED, 
        field,
        details: `Name: ${farmerName}` 
      }
    ),
    
    deleted: (farmerName) => toast.success(
      `Farmer "${farmerName}" has been removed from the system`,
      { ...TOAST_MESSAGES.FARMER.FARMER_DELETED, details: `Name: ${farmerName}` }
    ),
    
    editRequestSubmitted: (farmerName, changes) => toast.success(
      `Edit request submitted for farmer "${farmerName}"`,
      { 
        ...TOAST_MESSAGES.FARMER.EDIT_REQUEST_SUBMITTED,
        details: `Changes: ${Object.keys(changes).join(', ')}`
      }
    ),
    
    editRequestApproved: (farmerName) => toast.success(
      `Edit request for farmer "${farmerName}" has been approved`,
      { ...TOAST_MESSAGES.FARMER.EDIT_REQUEST_APPROVED, details: `Name: ${farmerName}` }
    ),
    
    editRequestRejected: (farmerName, reason) => toast.warning(
      `Edit request for farmer "${farmerName}" has been rejected`,
      { 
        ...TOAST_MESSAGES.FARMER.EDIT_REQUEST_REJECTED,
        details: reason ? `Reason: ${reason}` : `Name: ${farmerName}`
      }
    ),
    
    error: (action, error) => toast.error(
      `Failed to ${action.toLowerCase()} farmer: ${error}`,
      { 
        module: 'farmer',
        action,
        details: error
      }
    ),
    
    validationError: (field, message) => toast.error(
      message,
      {
        title: `Invalid ${field}`,
        module: 'farmer',
        field,
        action: 'Validation'
      }
    )
  };

  // Inventory-related notifications
  const inventory = {
    stockAdded: (item, quantity) => toast.success(
      `${quantity} units of ${item} added to inventory`,
      { 
        ...TOAST_MESSAGES.INVENTORY.STOCK_ADDED,
        details: `Item: ${item}, Quantity: ${quantity}`
      }
    ),
    
    stockUpdated: (item, field = null) => toast.success(
      field 
        ? `${field} updated for ${item}`
        : `Stock information updated for ${item}`,
      { 
        ...TOAST_MESSAGES.INVENTORY.STOCK_UPDATED,
        field,
        details: `Item: ${item}`
      }
    ),
    
    movementRecorded: (type, item, quantity) => toast.success(
      `${type} movement recorded: ${quantity} units of ${item}`,
      { 
        ...TOAST_MESSAGES.INVENTORY.STOCK_MOVEMENT_RECORDED,
        details: `Type: ${type}, Item: ${item}, Quantity: ${quantity}`
      }
    ),
    
    lowStockAlert: (items) => toast.warning(
      `Low stock alert for ${items.length} item(s)`,
      { 
        ...TOAST_MESSAGES.INVENTORY.LOW_STOCK_ALERT,
        details: `Items: ${items.join(', ')}`,
        persistent: true
      }
    ),
    
    error: (action, error) => toast.error(
      `Failed to ${action.toLowerCase()}: ${error}`,
      { 
        module: 'inventory',
        action,
        details: error
      }
    )
  };

  // Production-related notifications
  const production = {
    batchStarted: (batchId, product) => toast.success(
      `Production batch ${batchId} started for ${product}`,
      { 
        ...TOAST_MESSAGES.PRODUCTION.BATCH_STARTED,
        details: `Batch: ${batchId}, Product: ${product}`
      }
    ),
    
    batchCompleted: (batchId, quantity) => toast.success(
      `Production batch ${batchId} completed - ${quantity} units produced`,
      { 
        ...TOAST_MESSAGES.PRODUCTION.BATCH_COMPLETED,
        details: `Batch: ${batchId}, Output: ${quantity} units`
      }
    ),
    
    qualityCheckPassed: (batchId, grade) => toast.success(
      `Quality check passed for batch ${batchId} - Grade: ${grade}`,
      { 
        ...TOAST_MESSAGES.PRODUCTION.QUALITY_CHECK_PASSED,
        details: `Batch: ${batchId}, Grade: ${grade}`
      }
    ),
    
    qualityCheckFailed: (batchId, issues) => toast.error(
      `Quality check failed for batch ${batchId}`,
      { 
        ...TOAST_MESSAGES.PRODUCTION.QUALITY_CHECK_FAILED,
        details: `Issues: ${issues.join(', ')}`,
        persistent: true
      }
    ),
    
    error: (action, error) => toast.error(
      `Production ${action.toLowerCase()} failed: ${error}`,
      { 
        module: 'production',
        action,
        details: error
      }
    )
  };

  // User-related notifications
  const user = {
    profileUpdated: (field = null) => toast.success(
      field 
        ? `${field} has been updated successfully`
        : 'Your profile has been updated successfully',
      { 
        ...TOAST_MESSAGES.USER.PROFILE_UPDATED,
        field
      }
    ),
    
    passwordChanged: () => toast.success(
      'Your password has been changed successfully',
      TOAST_MESSAGES.USER.PASSWORD_CHANGED
    ),
    
    loginSuccess: (username) => toast.success(
      `Welcome back, ${username}!`,
      { 
        ...TOAST_MESSAGES.USER.LOGIN_SUCCESS,
        details: `User: ${username}`
      }
    ),
    
    logoutSuccess: () => toast.info(
      'You have been logged out successfully',
      TOAST_MESSAGES.USER.LOGOUT_SUCCESS
    ),
    
    sessionExpired: () => toast.warning(
      'Your session has expired. Please log in again',
      { 
        ...TOAST_MESSAGES.USER.SESSION_EXPIRED,
        persistent: true
      }
    ),
    
    error: (action, error) => toast.error(
      `${action} failed: ${error}`,
      { 
        module: 'settings',
        action,
        details: error
      }
    )
  };

  // Notification-related notifications
  const notifications = {
    markedAsRead: (count = 1) => toast.success(
      count === 1 
        ? 'Notification marked as read'
        : `${count} notifications marked as read`,
      { 
        ...TOAST_MESSAGES.NOTIFICATION.MARKED_AS_READ,
        details: `Count: ${count}`
      }
    ),
    
    allMarkedAsRead: (count) => toast.success(
      `All ${count} notifications marked as read`,
      { 
        ...TOAST_MESSAGES.NOTIFICATION.ALL_MARKED_AS_READ,
        details: `Total: ${count}`
      }
    ),
    
    deleted: (count = 1) => toast.success(
      count === 1 
        ? 'Notification deleted'
        : `${count} notifications deleted`,
      { 
        ...TOAST_MESSAGES.NOTIFICATION.NOTIFICATION_DELETED,
        details: `Count: ${count}`
      }
    )
  };

  // System-related notifications
  const system = {
    saveSuccess: (item = 'Changes') => toast.success(
      `${item} saved successfully`,
      TOAST_MESSAGES.SYSTEM.SAVE_SUCCESS
    ),
    
    saveError: (error) => toast.error(
      `Failed to save: ${error}`,
      { 
        ...TOAST_MESSAGES.SYSTEM.SAVE_ERROR,
        details: error
      }
    ),
    
    loading: (message = 'Loading data...') => toast.info(
      message,
      { 
        ...TOAST_MESSAGES.SYSTEM.LOADING,
        duration: 2000
      }
    ),
    
    networkError: () => toast.error(
      'Network connection error. Please check your internet connection',
      { 
        ...TOAST_MESSAGES.SYSTEM.NETWORK_ERROR,
        persistent: true
      }
    ),
    
    validationError: (errors) => toast.error(
      `Please fix ${errors.length} validation error(s)`,
      { 
        ...TOAST_MESSAGES.SYSTEM.VALIDATION_ERROR,
        details: errors.join(', ')
      }
    ),
    
    permissionDenied: (action) => toast.error(
      `You don't have permission to ${action.toLowerCase()}`,
      { 
        ...TOAST_MESSAGES.SYSTEM.PERMISSION_DENIED,
        action
      }
    )
  };

  // Generic methods
  const showSuccess = (message, options = {}) => toast.success(message, options);
  const showError = (message, options = {}) => toast.error(message, options);
  const showWarning = (message, options = {}) => toast.warning(message, options);
  const showInfo = (message, options = {}) => toast.info(message, options);

  // Field validation helper
  const showFieldError = (field, message, module = 'general') => {
    return toast.fieldError(field, message, { module });
  };

  // Action feedback helper
  const showActionResult = (action, success, message, module = 'general') => {
    if (success) {
      return toast.actionSuccess(action, message, { module });
    } else {
      return toast.actionError(action, message, { module });
    }
  };

  return {
    // Module-specific methods
    farmer,
    inventory,
    production,
    user,
    notifications,
    system,
    
    // Generic methods
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showFieldError,
    showActionResult,
    
    // Direct access to toast methods
    ...toast
  };
};

export default useToastNotifications;
