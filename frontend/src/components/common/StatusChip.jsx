import { Chip } from '@mui/material';
import CheckCircleOutline from '@mui/icons-material/CheckCircleOutline';
import ErrorOutline from '@mui/icons-material/ErrorOutline';
import HourglassEmpty from '@mui/icons-material/HourglassEmpty';
import PauseCircleOutline from '@mui/icons-material/PauseCircleOutline';
import CancelOutlined from '@mui/icons-material/CancelOutlined';
import InfoOutlined from '@mui/icons-material/InfoOutlined';
import { useI18n } from '../../i18n/I18nContext';

const TONE = {
  success: { color: 'success', icon: <CheckCircleOutline fontSize="small" /> },
  warning: { color: 'warning', icon: <HourglassEmpty fontSize="small" /> },
  error: { color: 'error', icon: <ErrorOutline fontSize="small" /> },
  info: { color: 'info', icon: <InfoOutlined fontSize="small" /> },
  idle: { color: 'default', icon: <PauseCircleOutline fontSize="small" /> },
  stopped: { color: 'default', icon: <CancelOutlined fontSize="small" /> },
};

const STATUS_TONE = {
  active: 'success',
  open: 'warning',
  pending: 'warning',
  in_progress: 'info',
  running: 'info',
  completed: 'success',
  delivered: 'success',
  confirmed: 'info',
  processing: 'warning',
  paid: 'success',
  partial: 'info',
  verified: 'success',
  resolved: 'success',
  approved: 'success',
  inactive: 'idle',
  closed: 'idle',
  cancelled: 'stopped',
  canceled: 'stopped',
  failed: 'error',
  overdue: 'error',
  rejected: 'error',
  discrepancy: 'warning',
  draft: 'idle',
  locked: 'idle',
  sensor: 'info',
  manual: 'warning',
  in: 'success',
  out: 'error',
  a: 'success',
  b: 'info',
  c: 'warning',
  d: 'error',
  high: 'error',
  medium: 'warning',
  low: 'info',
};

export function statusTone(status) {
  return STATUS_TONE[String(status || '').toLowerCase()] || 'info';
}

export default function StatusChip({ status, label, tone }) {
  const { statusLabel } = useI18n();
  const resolved = tone || statusTone(status);
  const look = TONE[resolved] || TONE.info;
  const text = label || statusLabel(status) || String(status || '');
  const contrast = resolved === 'warning'
    ? { bgcolor: '#fff7ed', color: '#9a3412', '& .MuiChip-label': { color: '#9a3412' }, '& .MuiChip-icon': { color: '#9a3412' } }
    : resolved === 'info'
      ? { bgcolor: '#e3f2fd', color: '#0d47a1', '& .MuiChip-label': { color: '#0d47a1' }, '& .MuiChip-icon': { color: '#0d47a1' } }
      : {};
  return (
    <Chip
      size="small"
      color={look.color}
      icon={look.icon}
      label={text}
      sx={{ '& .MuiChip-icon': { ml: 0.5 }, ...contrast }}
    />
  );
}
