import React, { useEffect, useRef, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Typography,
} from '@mui/material';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useI18n } from '../../i18n/I18nContext';
import { farmerService } from '../../services/farmerService';

const MAX_BYTES = 8 * 1024 * 1024;
const ACCEPT = 'image/jpeg,image/png,image/webp';

export function mapExtractedFields(fields) {
  const source = fields || {};
  const mapped = {};
  if (source.fullName) mapped.name = source.fullName;
  if (source.fatherName) mapped.father_name = source.fatherName;
  if (source.phone) mapped.phone = source.phone;
  if (source.email) mapped.email = source.email;
  if (source.village) mapped.village = source.village;
  if (source.district) mapped.district = source.district;
  if (source.state) mapped.state = source.state;
  if (source.pincode) mapped.pincode = source.pincode;
  if (source.address) mapped.address = source.address;
  if (source.totalLandArea != null && source.totalLandArea !== '') {
    mapped.total_land_area = source.totalLandArea;
  }
  if (source.bankAccount) mapped.bank_account_number = source.bankAccount;
  if (source.bankIfsc) mapped.bank_ifsc = source.bankIfsc;
  if (source.bankName) mapped.bank_name = source.bankName;
  if (source.surveyNumber) mapped.surveyNumber = source.surveyNumber;
  return mapped;
}

export default function IdDocumentCapture({ onExtracted }) {
  const { t } = useI18n();
  const fileRef = useRef(null);
  const videoRef = useRef(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [reading, setReading] = useState(false);
  const [message, setMessage] = useState('');
  const [severity, setSeverity] = useState('info');
  const [cameraOpen, setCameraOpen] = useState(false);
  const streamRef = useRef(null);

  useEffect(() => () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    stopCamera();
  }, []);

  const stopCamera = () => {
    const stream = streamRef.current;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraOpen(false);
  };

  const showPreview = (file) => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(URL.createObjectURL(file));
  };

  const submitFile = async (file) => {
    if (!file) {
      return;
    }
    if (!/^image\/(jpeg|jpg|png|webp)$/i.test(file.type) && !/\.(jpe?g|png|webp)$/i.test(file.name || '')) {
      setSeverity('warning');
      setMessage(t('idFileType'));
      return;
    }
    if (file.size > MAX_BYTES) {
      setSeverity('warning');
      setMessage(t('idFileTooBig'));
      return;
    }
    showPreview(file);
    setReading(true);
    setSeverity('info');
    setMessage(t('readingDocument'));
    try {
      const result = await farmerService.extractId(file);
      const fields = result?.fields || result?.extracted || {};
      const mapped = mapExtractedFields(fields);
      const hasValues = Object.keys(mapped).filter((key) => key !== 'surveyNumber').length > 0
        || Boolean(mapped.surveyNumber);
      if (!hasValues) {
        setSeverity('warning');
        setMessage(result?.notes || t('idExtractNone'));
        onExtracted?.({}, result?.notes || '');
        return;
      }
      setSeverity('success');
      setMessage(result?.notes || t('idExtractReady'));
      onExtracted?.(mapped, result?.notes || '');
    } catch (error) {
      setSeverity('warning');
      setMessage(error.userMessage || error.response?.data?.notes || t('idExtractNone'));
    } finally {
      setReading(false);
    }
  };

  const openCamera = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setSeverity('warning');
      setMessage(t('idCameraError'));
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: 'environment' } },
        audio: false,
      });
      streamRef.current = stream;
      setCameraOpen(true);
    } catch {
      setSeverity('warning');
      setMessage(t('idCameraError'));
    }
  };

  useEffect(() => {
    if (cameraOpen && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
    }
  }, [cameraOpen]);

  const captureStill = () => {
    const video = videoRef.current;
    if (!video || !video.videoWidth) {
      return;
    }
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      stopCamera();
      if (blob) {
        submitFile(new File([blob], 'id-capture.jpg', { type: 'image/jpeg' }));
      }
    }, 'image/jpeg', 0.9);
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        {t('idDocumentHelp')}
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        <Button
          size="small"
          variant="outlined"
          startIcon={<UploadFileIcon />}
          onClick={() => fileRef.current?.click()}
          disabled={reading}
        >
          {t('uploadId')}
        </Button>
        <Button
          size="small"
          variant="outlined"
          startIcon={<PhotoCameraIcon />}
          onClick={openCamera}
          disabled={reading}
        >
          {t('useCamera')}
        </Button>
        <input
          ref={fileRef}
          type="file"
          accept={ACCEPT}
          hidden
          onChange={(event) => {
            const file = event.target.files && event.target.files[0];
            event.target.value = '';
            submitFile(file);
          }}
        />
      </Stack>
      {previewUrl ? (
        <Box
          component="img"
          src={previewUrl}
          alt={t('idPreviewAlt')}
          sx={{ mt: 1, maxHeight: 140, maxWidth: '100%', borderRadius: 1 }}
        />
      ) : null}
      {reading ? (
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1 }}>
          <CircularProgress size={18} />
          <Typography variant="body2">{t('readingDocument')}</Typography>
        </Stack>
      ) : null}
      {message && !reading ? (
        <Alert severity={severity} sx={{ mt: 1 }} onClose={() => setMessage('')}>
          {message}
        </Alert>
      ) : null}

      <Dialog open={cameraOpen} onClose={stopCamera} maxWidth="sm" fullWidth>
        <DialogTitle>{t('useCamera')}</DialogTitle>
        <DialogContent>
          <Box
            component="video"
            ref={videoRef}
            autoPlay
            playsInline
            muted
            sx={{ width: '100%', borderRadius: 1, bgcolor: 'black' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={stopCamera}>{t('idCloseCamera')}</Button>
          <Button variant="contained" onClick={captureStill}>{t('idCapture')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
