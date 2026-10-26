import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { useI18n } from '../../i18n/I18nContext';

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  cancelLabel,
  danger = false,
  onConfirm,
  onCancel,
}) {
  const { t } = useI18n();
  return (
    <Dialog open={open} onClose={onCancel} fullWidth maxWidth="xs">
      <DialogTitle>{title || t('pleaseConfirm')}</DialogTitle>
      <DialogContent>
        <DialogContentText>{message}</DialogContentText>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2, position: { xs: 'sticky', sm: 'static' }, bottom: 0 }}>
        <Button onClick={onCancel}>{cancelLabel || t('cancel')}</Button>
        <Button variant="contained" color={danger ? 'error' : 'primary'} onClick={onConfirm} autoFocus>
          {confirmLabel || t('confirm')}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
