import { useEffect, useMemo, useRef, useState } from 'react';
import {
  Box,
  Fab,
  IconButton,
  Paper,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import SendIcon from '@mui/icons-material/Send';
import ImageOutlinedIcon from '@mui/icons-material/ImageOutlined';
import { useLocation } from 'react-router-dom';
import { useI18n } from '../i18n/I18nContext';
import { farmerService } from '../services/farmerService';
import { describeAssistantError, localAssistantFallback, sendAssistantMessage } from './assistantApi';
import { useAssistant } from './AssistantBridge';

const SPEECH_LANG = { en: 'en-IN', hi: 'hi-IN', te: 'te-IN' };
const IMAGE_TYPES = /^image\/(jpeg|jpg|png|webp)$/i;

function speechEngine() {
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

function wantsFarmerHelp(text, pathname) {
  return /farmer|register|id card|aadhaar|आधार|किसान|రైతు/i.test(text || '')
    || String(pathname || '').startsWith('/farmers');
}

function fieldSummary(fields) {
  return Object.entries(fields || {})
    .filter(([, value]) => value !== '' && value != null)
    .map(([key, value]) => `${key}: ${value}`)
    .join(', ');
}

export default function AssistantOverlay() {
  const { t, locale } = useI18n();
  const location = useLocation();
  const { applyActions } = useAssistant();
  const panelRef = useRef(null);
  const inputRef = useRef(null);
  const fabRef = useRef(null);
  const fileRef = useRef(null);
  const recognitionRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [transcript, setTranscript] = useState('');
  const [listening, setListening] = useState(false);
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState([]);
  const SpeechRecognition = useMemo(speechEngine, []);

  useEffect(() => {
    if (!open) return undefined;
    const timer = window.setTimeout(() => inputRef.current?.focus(), 40);
    return () => window.clearTimeout(timer);
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (event) => {
      if (event.key === 'Escape') {
        event.stopPropagation();
        setOpen(false);
        window.setTimeout(() => fabRef.current?.focus(), 0);
      }
    };
    window.addEventListener('keydown', onKey, true);
    return () => window.removeEventListener('keydown', onKey, true);
  }, [open]);

  useEffect(() => () => {
    recognitionRef.current?.stop?.();
  }, []);

  const pushMessage = (role, text) => {
    const body = String(text || '').trim();
    if (!body) return;
    setMessages((prev) => [...prev.slice(-40), { role, text: body, at: Date.now() }]);
  };

  const runMessage = async (text, extraReply) => {
    const message = String(text || '').trim();
    if (!message && !extraReply) return;
    if (message) pushMessage('user', message);
    setBusy(true);
    try {
      const result = await sendAssistantMessage({
        message: message || extraReply || '',
        route: location.pathname,
        language: locale,
      });
      const applied = await applyActions(result.actions);
      let reply = result.reply || t('assistantEmpty');
      if (applied.filled.length) {
        reply = `${reply} ${t('assistantFilled')}`;
      }
      if (applied.missing.length) {
        reply = `${reply} ${t('assistantOpenRegisterFirst')}`;
      }
      if (extraReply) {
        reply = `${extraReply} ${reply}`.trim();
      }
      pushMessage('assistant', reply);
    } catch (err) {
      const local = localAssistantFallback(message);
      if (local.actions.length) {
        const applied = await applyActions(local.actions);
        let reply = local.reply || t('assistantEmpty');
        if (applied.filled.length) reply = `${reply} ${t('assistantFilled')}`;
        if (applied.missing.length) reply = `${reply} ${t('assistantOpenRegisterFirst')}`;
        pushMessage('assistant', reply);
      } else {
        pushMessage('assistant', err?.assistantMessage || describeAssistantError(err) || t('assistantError'));
      }
    } finally {
      setBusy(false);
    }
  };

  const handleSend = () => {
    if (busy) return;
    const text = draft.trim();
    if (!text) return;
    setDraft('');
    setTranscript('');
    runMessage(text);
  };

  const toggleMic = () => {
    if (!SpeechRecognition) return;
    if (listening) {
      recognitionRef.current?.stop?.();
      setListening(false);
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = SPEECH_LANG[locale] || 'en-IN';
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.onresult = (event) => {
      let spoken = '';
      for (let i = 0; i < event.results.length; i += 1) {
        spoken += event.results[i][0]?.transcript || '';
      }
      setTranscript(spoken);
      setDraft(spoken);
    };
    recognition.onerror = () => {
      setListening(false);
    };
    recognition.onend = () => {
      setListening(false);
    };
    recognitionRef.current = recognition;
    setListening(true);
    recognition.start();
  };

  const handleAttach = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    if (!IMAGE_TYPES.test(file.type) && !/\.(jpe?g|png|webp)$/i.test(file.name || '')) {
      pushMessage('assistant', t('assistantImageType'));
      return;
    }
    if (!wantsFarmerHelp(draft, location.pathname)) {
      pushMessage('assistant', t('assistantOpenRegisterFirst'));
      return;
    }
    setBusy(true);
    pushMessage('user', t('assistantImageAttached'));
    try {
      const result = await farmerService.extractId(file);
      const fields = result?.fields || result?.extracted || {};
      const applied = await applyActions([
        { type: 'navigate', path: '/farmers' },
        { type: 'open', target: 'register-farmer' },
        { type: 'fill', target: 'register-farmer', fields },
      ]);
      const summary = fieldSummary(fields);
      if (applied.filled.length && summary) {
        pushMessage('assistant', `${t('assistantImageOk')} ${summary}. ${t('assistantFilled')}`);
      } else if (applied.missing.length) {
        pushMessage('assistant', t('assistantOpenRegisterFirst'));
      } else {
        pushMessage('assistant', result?.notes || t('assistantImageFail'));
      }
    } catch (err) {
      pushMessage('assistant', err?.userMessage || describeAssistantError(err) || t('assistantImageFail'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <Tooltip title={t('assistantOpen')}>
        <Fab
          ref={fabRef}
          color="primary"
          aria-label={t('assistantOpen')}
          aria-expanded={open}
          aria-controls="millmitra-assistant-panel"
          onClick={() => setOpen((prev) => !prev)}
          sx={{
            position: 'fixed',
            right: 20,
            bottom: 20,
            zIndex: 1200,
          }}
        >
          <ChatIcon />
        </Fab>
      </Tooltip>

      {open && (
        <Paper
          id="millmitra-assistant-panel"
          ref={panelRef}
          role="dialog"
          aria-modal="false"
          aria-labelledby="millmitra-assistant-title"
          tabIndex={-1}
          elevation={8}
          sx={{
            position: 'fixed',
            right: 20,
            bottom: 88,
            width: { xs: 'calc(100vw - 32px)', sm: 400 },
            maxWidth: 400,
            maxHeight: 'min(72vh, 640px)',
            zIndex: 1250,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              px: 2,
              py: 1.25,
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <Box sx={{ flexGrow: 1, minWidth: 0 }}>
              <Typography id="millmitra-assistant-title" variant="subtitle1">
                {t('assistantTitle')}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.9 }}>
                {t('assistantSubtitle')}
              </Typography>
            </Box>
            <IconButton
              color="inherit"
              aria-label={t('assistantClose')}
              onClick={() => {
                setOpen(false);
                window.setTimeout(() => fabRef.current?.focus(), 0);
              }}
            >
              <CloseIcon />
            </IconButton>
          </Box>

          <Stack spacing={1} sx={{ p: 1.5, overflowY: 'auto', flexGrow: 1 }}>
            {messages.length === 0 && (
              <Typography variant="body2" color="text.secondary">
                {t('assistantWelcome')}
              </Typography>
            )}
            {messages.map((item) => (
              <Box
                key={`${item.role}-${item.at}`}
                sx={{
                  alignSelf: item.role === 'user' ? 'flex-end' : 'flex-start',
                  bgcolor: item.role === 'user' ? 'primary.light' : 'grey.100',
                  color: item.role === 'user' ? 'primary.contrastText' : 'text.primary',
                  px: 1.25,
                  py: 0.75,
                  borderRadius: 1.5,
                  maxWidth: '92%',
                }}
              >
                <Typography variant="body2">{item.text}</Typography>
              </Box>
            ))}
            {listening && transcript && (
              <Typography variant="caption" color="text.secondary">
                {t('assistantTranscript')}: {transcript}
              </Typography>
            )}
            {!SpeechRecognition && (
              <Typography variant="caption" color="text.secondary">
                {t('assistantVoiceUnsupported')}
              </Typography>
            )}
          </Stack>

          <Box sx={{ p: 1.5, borderTop: '1px solid', borderColor: 'divider' }}>
            <Stack direction="row" spacing={1} alignItems="flex-end">
              <TextField
                inputRef={inputRef}
                fullWidth
                size="small"
                multiline
                maxRows={4}
                value={draft}
                disabled={busy}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    handleSend();
                  }
                }}
                label={t('assistantPlaceholder')}
                inputProps={{ 'aria-label': t('assistantPlaceholder') }}
              />
              <input
                ref={fileRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                hidden
                onChange={handleAttach}
              />
              <Tooltip title={t('assistantAttach')}>
                <span>
                  <IconButton
                    aria-label={t('assistantAttach')}
                    disabled={busy}
                    onClick={() => fileRef.current?.click()}
                  >
                    <ImageOutlinedIcon />
                  </IconButton>
                </span>
              </Tooltip>
              {SpeechRecognition && (
                <Tooltip title={listening ? t('assistantStopMic') : t('assistantMic')}>
                  <IconButton
                    aria-label={listening ? t('assistantStopMic') : t('assistantMic')}
                    color={listening ? 'error' : 'default'}
                    disabled={busy}
                    onClick={toggleMic}
                  >
                    {listening ? <MicOffIcon /> : <MicIcon />}
                  </IconButton>
                </Tooltip>
              )}
              <Tooltip title={t('assistantSend')}>
                <span>
                  <IconButton
                    color="primary"
                    aria-label={t('assistantSend')}
                    disabled={busy || !draft.trim()}
                    onClick={handleSend}
                  >
                    <SendIcon />
                  </IconButton>
                </span>
              </Tooltip>
            </Stack>
          </Box>
        </Paper>
      )}
    </>
  );
}
