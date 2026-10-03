import { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, FormControl, InputLabel, Select,
  MenuItem, Box, Typography, Chip, Alert
} from '@mui/material';
import { customerService } from '../services/customerService';
import { useI18n } from '../i18n/I18nContext';

const InteractionDialog = ({ open, onClose, customer, onSubmit, loading }) => {
  const { t, statusLabel } = useI18n();
  const [formData, setFormData] = useState({
    interaction_type: 'call',
    subject: '',
    description: '',
    priority: 'medium',
    status: 'open',
    follow_up_required: false,
    follow_up_date: ''
  });

  const [aiAnalysis, setAiAnalysis] = useState(null);

  const handleChange = (field) => (e) => {
    const value = e.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Trigger AI analysis when description changes
    if (field === 'description' && value.length > 20) {
      analyzeInteraction(value);
    }
  };

  const analyzeInteraction = async (description) => {
    try {
      const analysis = await customerService.analyzeFeedback({
        feedback: description,
        customer_id: customer?.id
      });
      setAiAnalysis(analysis);
    } catch (error) {
      console.error('Failed to analyze interaction:', error);
    }
  };

  const [submitError, setSubmitError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.subject || !formData.description) {
      setSubmitError('Subject and notes are required');
      return;
    }
    setSubmitError('');
    onSubmit({
      customerId: customer?.id,
      ...formData,
      ai_analysis: aiAnalysis
    });
  };

  const getSentimentColor = (score) => {
    if (score > 0.3) return 'success';
    if (score < -0.3) return 'error';
    return 'warning';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {t('addInteraction')}
        {customer && (
          <Typography variant="subtitle2" color="text.secondary">
            {t('customer')}: {customer.name}
          </Typography>
        )}
      </DialogTitle>
      
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {submitError && <Alert severity="error">{submitError}</Alert>}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>{t('interactionType')}</InputLabel>
              <Select
                value={formData.interaction_type}
                onChange={handleChange('interaction_type')}
                required
              >
                <MenuItem value="call">{t('phoneCall')}</MenuItem>
                <MenuItem value="email">{t('email')}</MenuItem>
                <MenuItem value="meeting">{t('meeting')}</MenuItem>
                <MenuItem value="complaint">{t('complaint')}</MenuItem>
                <MenuItem value="inquiry">{t('inquiry')}</MenuItem>
                <MenuItem value="feedback">{t('feedback')}</MenuItem>
                <MenuItem value="support">{t('supportRequest')}</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label={t('subject')}
              value={formData.subject}
              onChange={handleChange('subject')}
              required
            />

            <TextField
              fullWidth
              label={t('description')}
              value={formData.description}
              onChange={handleChange('description')}
              multiline
              rows={4}
              required
              helperText="Describe the interaction details. AI will analyze sentiment and urgency."
            />

            {/* AI Analysis Results */}
            {aiAnalysis && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  AI Analysis Results
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <Chip
                    label={`Sentiment: ${aiAnalysis.sentiment_label}`}
                    color={getSentimentColor(aiAnalysis.sentiment_score)}
                    size="small"
                  />
                  {aiAnalysis.action_required && (
                    <Chip
                      label={t('actionRequired')}
                      color="error"
                      size="small"
                    />
                  )}
                </Box>
                {aiAnalysis.key_themes && (
                  <Typography variant="body2">
                    Key themes: {aiAnalysis.key_themes.join(', ')}
                  </Typography>
                )}
              </Alert>
            )}

            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>{t('priority')}</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={handleChange('priority')}
                >
                  <MenuItem value="low">{t('priorityLow')}</MenuItem>
                  <MenuItem value="medium">{t('priorityMedium')}</MenuItem>
                  <MenuItem value="high">{t('priorityHigh')}</MenuItem>
                  <MenuItem value="urgent">{t('priorityUrgent')}</MenuItem>
                </Select>
              </FormControl>

              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>{t('status')}</InputLabel>
                <Select
                  value={formData.status}
                  onChange={handleChange('status')}
                >
                  <MenuItem value="open">{statusLabel('open')}</MenuItem>
                  <MenuItem value="in_progress">{statusLabel('in_progress')}</MenuItem>
                  <MenuItem value="resolved">{statusLabel('resolved')}</MenuItem>
                  <MenuItem value="closed">{statusLabel('closed')}</MenuItem>
                </Select>
              </FormControl>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FormControl>
                <InputLabel>{t('followUpRequired')}</InputLabel>
                <Select
                  value={formData.follow_up_required}
                  onChange={handleChange('follow_up_required')}
                >
                  <MenuItem value={false}>{t('no')}</MenuItem>
                  <MenuItem value={true}>{t('yes')}</MenuItem>
                </Select>
              </FormControl>

              {formData.follow_up_required && (
                <TextField
                  type="datetime-local"
                  label={t('followUpDate')}
                  value={formData.follow_up_date}
                  onChange={handleChange('follow_up_date')}
                  InputLabelProps={{ shrink: true }}
                />
              )}
            </Box>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose}>{t('cancel')}</Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !formData.subject || !formData.description}
          >
            {loading ? t('creating') : t('createInteraction')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default InteractionDialog;