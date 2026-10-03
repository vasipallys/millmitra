import { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button, FormControl, InputLabel, Select,
  MenuItem, Box, Typography, Chip, Alert
} from '@mui/material';
import { customerService } from '../services/customerService';

const InteractionDialog = ({ open, onClose, customer, onSubmit, loading }) => {
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
        Add Customer Interaction
        {customer && (
          <Typography variant="subtitle2" color="text.secondary">
            Customer: {customer.name}
          </Typography>
        )}
      </DialogTitle>
      
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {submitError && <Alert severity="error">{submitError}</Alert>}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Interaction Type</InputLabel>
              <Select
                value={formData.interaction_type}
                onChange={handleChange('interaction_type')}
                required
              >
                <MenuItem value="call">Phone Call</MenuItem>
                <MenuItem value="email">Email</MenuItem>
                <MenuItem value="meeting">In-Person Meeting</MenuItem>
                <MenuItem value="complaint">Complaint</MenuItem>
                <MenuItem value="inquiry">General Inquiry</MenuItem>
                <MenuItem value="feedback">Feedback</MenuItem>
                <MenuItem value="support">Support Request</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Subject"
              value={formData.subject}
              onChange={handleChange('subject')}
              required
            />

            <TextField
              fullWidth
              label="Description"
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
                      label="Action Required"
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
                <InputLabel>Priority</InputLabel>
                <Select
                  value={formData.priority}
                  onChange={handleChange('priority')}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>

              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={handleChange('status')}
                >
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="resolved">Resolved</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <FormControl>
                <InputLabel>Follow-up Required</InputLabel>
                <Select
                  value={formData.follow_up_required}
                  onChange={handleChange('follow_up_required')}
                >
                  <MenuItem value={false}>No</MenuItem>
                  <MenuItem value={true}>Yes</MenuItem>
                </Select>
              </FormControl>

              {formData.follow_up_required && (
                <TextField
                  type="datetime-local"
                  label="Follow-up Date"
                  value={formData.follow_up_date}
                  onChange={handleChange('follow_up_date')}
                  InputLabelProps={{ shrink: true }}
                />
              )}
            </Box>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose}>Cancel</Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !formData.subject || !formData.description}
          >
            {loading ? 'Creating...' : 'Create Interaction'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default InteractionDialog;