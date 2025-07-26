import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Alert,
  Fade,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid
} from '@mui/material';
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  VolumeUp as VolumeUpIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';

const VoiceCommandCenter = ({ onCommandExecuted }) => {
  const [isActive, setIsActive] = useState(false);
  const [commandHistory, setCommandHistory] = useState([]);
  const [currentCommand, setCurrentCommand] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [voiceSettings, setVoiceSettings] = useState({
    language: 'en-US',
    sensitivity: 'medium',
    confirmCommands: true,
    voiceFeedback: true
  });

  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    isSupported,
    error
  } = useVoiceRecognition();

  // Voice command patterns and their handlers
  const commandPatterns = {
    navigation: {
      patterns: [
        /go to (dashboard|home)/i,
        /open (farmers?|inventory|production|sales|finance|customers?)/i,
        /show me (.*)/i,
        /navigate to (.*)/i
      ],
      handler: handleNavigationCommand
    },
    data_entry: {
      patterns: [
        /add new (farmer|customer|batch|transaction)/i,
        /create (.*)/i,
        /record (.*)/i,
        /enter (.*)/i
      ],
      handler: handleDataEntryCommand
    },
    queries: {
      patterns: [
        /what is (.*)/i,
        /how much (.*)/i,
        /show me (.*)/i,
        /tell me about (.*)/i,
        /status of (.*)/i
      ],
      handler: handleQueryCommand
    },
    actions: {
      patterns: [
        /start (.*)/i,
        /stop (.*)/i,
        /update (.*)/i,
        /delete (.*)/i,
        /approve (.*)/i,
        /reject (.*)/i
      ],
      handler: handleActionCommand
    },
    system: {
      patterns: [
        /help/i,
        /what can you do/i,
        /voice commands/i,
        /cancel/i,
        /stop listening/i
      ],
      handler: handleSystemCommand
    }
  };

  // Update current command when transcript changes
  useEffect(() => {
    if (transcript && transcript !== currentCommand) {
      setCurrentCommand(transcript);
    }
  }, [transcript]);

  // Process command when listening stops
  useEffect(() => {
    if (!isListening && currentCommand && isActive) {
      processCommand(currentCommand);
    }
  }, [isListening, currentCommand, isActive]);

  const toggleVoiceCommands = () => {
    if (isActive) {
      setIsActive(false);
      if (isListening) {
        stopListening();
      }
      setCurrentCommand('');
    } else {
      setIsActive(true);
      startListening();
    }
  };

  const processCommand = async (command) => {
    if (!command.trim()) return;

    setIsProcessing(true);
    const commandEntry = {
      id: Date.now(),
      command: command,
      timestamp: new Date().toLocaleTimeString(),
      status: 'processing'
    };

    setCommandHistory(prev => [commandEntry, ...prev.slice(0, 9)]);

    try {
      // Find matching pattern and execute handler
      let handled = false;
      
      for (const [category, config] of Object.entries(commandPatterns)) {
        for (const pattern of config.patterns) {
          const match = command.match(pattern);
          if (match) {
            const result = await config.handler(command, match);
            
            // Update command history
            setCommandHistory(prev => 
              prev.map(cmd => 
                cmd.id === commandEntry.id 
                  ? { ...cmd, status: result.success ? 'success' : 'error', result: result.message }
                  : cmd
              )
            );

            // Show feedback
            setFeedback({
              type: result.success ? 'success' : 'error',
              message: result.message
            });

            // Voice feedback
            if (voiceSettings.voiceFeedback && result.success) {
              speakResponse(result.message);
            }

            // Execute callback
            if (onCommandExecuted) {
              onCommandExecuted(result);
            }

            handled = true;
            break;
          }
        }
        if (handled) break;
      }

      if (!handled) {
        // Try natural language processing
        const nlResult = await processNaturalLanguageCommand(command);
        
        setCommandHistory(prev => 
          prev.map(cmd => 
            cmd.id === commandEntry.id 
              ? { ...cmd, status: nlResult.success ? 'success' : 'error', result: nlResult.message }
              : cmd
          )
        );

        setFeedback({
          type: nlResult.success ? 'success' : 'warning',
          message: nlResult.message
        });
      }

    } catch (error) {
      console.error('Command processing error:', error);
      
      setCommandHistory(prev => 
        prev.map(cmd => 
          cmd.id === commandEntry.id 
            ? { ...cmd, status: 'error', result: 'Command processing failed' }
            : cmd
        )
      );

      setFeedback({
        type: 'error',
        message: 'Sorry, I couldn\'t process that command. Please try again.'
      });
    } finally {
      setIsProcessing(false);
      setCurrentCommand('');
      
      // Auto-clear feedback after 5 seconds
      setTimeout(() => setFeedback(null), 5000);
      
      // Continue listening if still active
      if (isActive) {
        setTimeout(() => startListening(), 1000);
      }
    }
  };

  // Command handlers
  async function handleNavigationCommand(command, match) {
    const target = match[1]?.toLowerCase();
    
    const navigationMap = {
      'dashboard': '/dashboard',
      'home': '/dashboard',
      'farmers': '/farmers',
      'farmer': '/farmers',
      'inventory': '/inventory',
      'production': '/production',
      'sales': '/sales',
      'finance': '/finance',
      'customers': '/customers',
      'customer': '/customers'
    };

    if (navigationMap[target]) {
      // Navigate using React Router
      window.location.hash = navigationMap[target];
      return {
        success: true,
        message: `Navigating to ${target}`
      };
    } else {
      return {
        success: false,
        message: `I don't know how to navigate to ${target}`
      };
    }
  }

  async function handleDataEntryCommand(command, match) {
    const entityType = match[1]?.toLowerCase();
    
    const entityMap = {
      'farmer': 'farmer',
      'customer': 'customer',
      'batch': 'production',
      'transaction': 'finance'
    };

    if (entityMap[entityType]) {
      return {
        success: true,
        message: `Opening new ${entityType} form`,
        action: 'open_form',
        entity: entityType
      };
    } else {
      return {
        success: false,
        message: `I don't know how to create a ${entityType}`
      };
    }
  }

  async function handleQueryCommand(command, match) {
    // Send to natural language processor
    try {
      const response = await fetch('/api/ai/natural-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ query: command })
      });

      if (response.ok) {
        const data = await response.json();
        return {
          success: true,
          message: data.response || 'Query processed successfully',
          data: data
        };
      } else {
        throw new Error('Query processing failed');
      }
    } catch (error) {
      return {
        success: false,
        message: 'I couldn\'t process that query right now'
      };
    }
  }

  async function handleActionCommand(command, match) {
    const action = match[0]?.toLowerCase();
    const target = match[1]?.toLowerCase();

    // Mock action handling - in real implementation, this would call appropriate APIs
    const actions = ['start', 'stop', 'update', 'delete', 'approve', 'reject'];
    
    if (actions.some(a => command.toLowerCase().includes(a))) {
      return {
        success: true,
        message: `${action} ${target} - command received`,
        action: action,
        target: target
      };
    } else {
      return {
        success: false,
        message: 'I didn\'t understand that action'
      };
    }
  }

  async function handleSystemCommand(command, match) {
    const cmd = command.toLowerCase();
    
    if (cmd.includes('help') || cmd.includes('what can you do')) {
      return {
        success: true,
        message: 'I can help you navigate, enter data, query information, and perform actions. Try saying "go to dashboard", "add new farmer", or "what is today\'s production".'
      };
    } else if (cmd.includes('cancel') || cmd.includes('stop listening')) {
      setIsActive(false);
      stopListening();
      return {
        success: true,
        message: 'Voice commands stopped'
      };
    } else {
      return {
        success: true,
        message: 'System command processed'
      };
    }
  }

  async function processNaturalLanguageCommand(command) {
    // Fallback for unmatched commands
    return {
      success: false,
      message: `I didn't understand "${command}". Try saying "help" for available commands.`
    };
  }

  const speakResponse = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'processing':
        return <CircularProgress size={20} />;
      default:
        return <PlayIcon />;
    }
  };

  if (!isSupported) {
    return (
      <Alert severity="warning">
        Voice commands are not supported in this browser. Please use Chrome, Firefox, or Safari.
      </Alert>
    );
  }

  return (
    <Box sx={{ width: '100%', maxWidth: 600, mx: 'auto' }}>
      {/* Main Control Panel */}
      <Card elevation={3} sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              Voice Command Center
            </Typography>
            <IconButton onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <IconButton
              onClick={toggleVoiceCommands}
              color={isActive ? "secondary" : "default"}
              size="large"
              sx={{
                bgcolor: isActive ? 'secondary.light' : 'grey.100',
                '&:hover': {
                  bgcolor: isActive ? 'secondary.main' : 'grey.200'
                }
              }}
            >
              {isListening ? <MicOffIcon /> : <MicIcon />}
            </IconButton>

            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="body1" color={isActive ? 'secondary.main' : 'text.secondary'}>
                {isActive 
                  ? (isListening ? 'Listening...' : 'Voice commands active - Click mic to speak')
                  : 'Voice commands inactive'
                }
              </Typography>
              
              {currentCommand && (
                <Typography variant="body2" color="primary" sx={{ mt: 0.5 }}>
                  "{currentCommand}"
                </Typography>
              )}
            </Box>

            {isProcessing && <CircularProgress size={24} />}
          </Box>

          {/* Status Chips */}
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              label={isActive ? "Active" : "Inactive"}
              color={isActive ? "success" : "default"}
              size="small"
            />
            <Chip
              label={`Language: ${voiceSettings.language}`}
              variant="outlined"
              size="small"
            />
            <Chip
              label={`Sensitivity: ${voiceSettings.sensitivity}`}
              variant="outlined"
              size="small"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Feedback */}
      {feedback && (
        <Fade in={!!feedback}>
          <Alert 
            severity={feedback.type} 
            sx={{ mb: 2 }}
            onClose={() => setFeedback(null)}
          >
            {feedback.message}
          </Alert>
        </Fade>
      )}

      {/* Command History */}
      {commandHistory.length > 0 && (
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Commands
            </Typography>
            <List dense>
              {commandHistory.map((cmd) => (
                <ListItem key={cmd.id}>
                  <ListItemIcon>
                    {getStatusIcon(cmd.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={cmd.command}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {cmd.timestamp}
                        </Typography>
                        {cmd.result && (
                          <Typography variant="caption" color="text.secondary">
                            {cmd.result}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Voice Command Settings</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Available Commands:
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText 
                    primary="Navigation" 
                    secondary="'Go to dashboard', 'Open farmers', 'Show me inventory'" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Data Entry" 
                    secondary="'Add new farmer', 'Create customer', 'Record transaction'" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Queries" 
                    secondary="'What is production status?', 'Show me today's performance'" 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="System" 
                    secondary="'Help', 'Stop listening', 'What can you do?'" 
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default VoiceCommandCenter;
