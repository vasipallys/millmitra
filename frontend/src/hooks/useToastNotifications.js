import { useToast } from '../components/common/ToastProvider';
import { TOAST_MESSAGES } from '../utils/toastMessages';
import { useI18n } from '../i18n/I18nContext';

/**
 * Enhanced toast hook with predefined messages and smart error handling
 */
const preset = (entry) => {
  if (!entry) return {};
  const { title, message, ...rest } = entry;
  return rest;
};

export const useToastNotifications = () => {
  const toast = useToast();
  const { t } = useI18n();

  // Farmer-related notifications
  const farmer = {
    created: (farmerName) => toast.success(
      t('toastFarmerCreated', { name: farmerName }),
      { ...preset(TOAST_MESSAGES.FARMER.FARMER_CREATED), details: t('toastName', { name: farmerName }) }
    ),
    
    updated: (farmerName, field = null) => toast.success(
      field 
        ? t('toastFarmerUpdatedField', { field, name: farmerName })
        : t('toastFarmerUpdated', { name: farmerName }),
      { 
        ...preset(TOAST_MESSAGES.FARMER.FARMER_UPDATED), 
        field,
        details: t('toastName', { name: farmerName }) 
      }
    ),
    
    deleted: (farmerName) => toast.success(
      t('toastFarmerDeleted', { name: farmerName }),
      { ...preset(TOAST_MESSAGES.FARMER.FARMER_DELETED), details: t('toastName', { name: farmerName }) }
    ),
    
    editRequestSubmitted: (farmerName, changes) => toast.success(
      t('toastEditSubmitted', { name: farmerName }),
      { 
        ...preset(TOAST_MESSAGES.FARMER.EDIT_REQUEST_SUBMITTED),
        details: Object.keys(changes).join(', ')
      }
    ),
    
    editRequestApproved: (farmerName) => toast.success(
      t('toastFarmerUpdated', { name: farmerName }),
      { ...preset(TOAST_MESSAGES.FARMER.EDIT_REQUEST_APPROVED), details: t('toastName', { name: farmerName }) }
    ),
    
    editRequestRejected: (farmerName, reason) => toast.warning(
      t('toastFarmerFailed', { action: t('edit'), error: reason || farmerName }),
      { 
        ...preset(TOAST_MESSAGES.FARMER.EDIT_REQUEST_REJECTED),
        details: reason || farmerName
      }
    ),
    
    error: (action, error) => toast.error(
      t('toastFarmerFailed', { action: String(action).toLowerCase(), error }),
      { 
        module: 'farmer',
        action,
        details: error
      }
    ),
    
    validationError: (field, message) => toast.error(
      message,
      {
        title: t('toastInvalidField', { field }),
        module: 'farmer',
        field,
        action: 'Validation'
      }
    )
  };

  // Inventory-related notifications
  const inventory = {
    stockAdded: (item, quantity) => toast.success(
      t('toastStockAdded', { quantity, item }),
      { 
        ...preset(TOAST_MESSAGES.INVENTORY.STOCK_ADDED),
        details: `${item}, ${quantity}`
      }
    ),
    
    stockUpdated: (item, field = null) => toast.success(
      field 
        ? t('toastStockUpdatedField', { field, item })
        : t('toastStockUpdated', { item }),
      { 
        ...preset(TOAST_MESSAGES.INVENTORY.STOCK_UPDATED),
        field,
        details: item
      }
    ),
    
    movementRecorded: (type, item, quantity) => toast.success(
      t('toastMovement', { type, quantity, item }),
      { 
        ...preset(TOAST_MESSAGES.INVENTORY.STOCK_MOVEMENT_RECORDED),
        details: `${type}, ${item}, ${quantity}`
      }
    ),
    
    lowStockAlert: (items) => toast.warning(
      t('toastLowStock', { count: items.length }),
      { 
        ...preset(TOAST_MESSAGES.INVENTORY.LOW_STOCK_ALERT),
        details: items.join(', '),
        persistent: true
      }
    ),
    
    error: (action, error) => toast.error(
      t('toastInvFailed', { action: String(action).toLowerCase(), error }),
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
      t('toastBatchStarted', { batch: batchId, product }),
      { 
        ...preset(TOAST_MESSAGES.PRODUCTION.BATCH_STARTED),
        details: `${batchId}, ${product}`
      }
    ),
    
    batchCompleted: (batchId, quantity) => toast.success(
      t('toastBatchCompleted', { batch: batchId, quantity }),
      { 
        ...preset(TOAST_MESSAGES.PRODUCTION.BATCH_COMPLETED),
        details: `${batchId}, ${quantity}`
      }
    ),
    
    qualityCheckPassed: (batchId, grade) => toast.success(
      t('toastQualityPass', { batch: batchId, grade }),
      { 
        ...preset(TOAST_MESSAGES.PRODUCTION.QUALITY_CHECK_PASSED),
        details: `${batchId}, ${grade}`
      }
    ),
    
    qualityCheckFailed: (batchId, issues) => toast.error(
      t('toastQualityFail', { batch: batchId }),
      { 
        ...preset(TOAST_MESSAGES.PRODUCTION.QUALITY_CHECK_FAILED),
        details: issues.join(', '),
        persistent: true
      }
    ),
    
    error: (action, error) => toast.error(
      t('toastProdFailed', { action: String(action).toLowerCase(), error }),
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
        ? t('toastProfileField', { field })
        : t('toastProfileUpdated'),
      { 
        ...preset(TOAST_MESSAGES.USER.PROFILE_UPDATED),
        field
      }
    ),
    
    passwordChanged: () => toast.success(
      t('toastPasswordChanged'),
      preset(TOAST_MESSAGES.USER.PASSWORD_CHANGED)
    ),
    
    loginSuccess: (username) => toast.success(
      t('toastWelcomeBack', { name: username }),
      { 
        ...preset(TOAST_MESSAGES.USER.LOGIN_SUCCESS),
        details: username
      }
    ),
    
    logoutSuccess: () => toast.info(
      t('toastLoggedOut'),
      preset(TOAST_MESSAGES.USER.LOGOUT_SUCCESS)
    ),
    
    sessionExpired: () => toast.warning(
      t('toastSessionExpired'),
      { 
        ...preset(TOAST_MESSAGES.USER.SESSION_EXPIRED),
        persistent: true
      }
    ),
    
    error: (action, error) => toast.error(
      t('toastActionFailed', { action, error }),
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
        ? t('toastNotifRead')
        : t('toastNotifReadMany', { count }),
      { 
        ...preset(TOAST_MESSAGES.NOTIFICATION.MARKED_AS_READ),
        details: String(count)
      }
    ),
    
    allMarkedAsRead: (count) => toast.success(
      t('toastAllRead', { count }),
      { 
        ...preset(TOAST_MESSAGES.NOTIFICATION.ALL_MARKED_AS_READ),
        details: String(count)
      }
    ),
    
    deleted: (count = 1) => toast.success(
      count === 1 
        ? t('toastNotifDeleted')
        : t('toastNotifDeletedMany', { count }),
      { 
        ...preset(TOAST_MESSAGES.NOTIFICATION.NOTIFICATION_DELETED),
        details: String(count)
      }
    )
  };

  // System-related notifications
  const system = {
    saveSuccess: (item) => toast.success(
      t('toastSaved', { item: item || t('save') }),
      preset(TOAST_MESSAGES.SYSTEM.SAVE_SUCCESS)
    ),
    
    saveError: (error) => toast.error(
      t('toastSaveFailed', { error }),
      { 
        ...preset(TOAST_MESSAGES.SYSTEM.SAVE_ERROR),
        details: error
      }
    ),
    
    loading: (message = t('loading')) => toast.info(
      message,
      { 
        ...preset(TOAST_MESSAGES.SYSTEM.LOADING),
        duration: 2000
      }
    ),
    
    networkError: () => toast.error(
      t('toastNetwork'),
      { 
        ...preset(TOAST_MESSAGES.SYSTEM.NETWORK_ERROR),
        persistent: true
      }
    ),
    
    validationError: (errors) => toast.error(
      t('toastValidationCount', { count: errors.length }),
      { 
        ...preset(TOAST_MESSAGES.SYSTEM.VALIDATION_ERROR),
        details: errors.join(', ')
      }
    ),
    
    permissionDenied: (action) => toast.error(
      t('toastNoPermission', { action: String(action).toLowerCase() }),
      { 
        ...preset(TOAST_MESSAGES.SYSTEM.PERMISSION_DENIED),
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
