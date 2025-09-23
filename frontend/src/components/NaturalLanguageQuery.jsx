import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  Chip,
  CircularProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Fade,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Psychology as AIIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useVoiceRecognition } from '../hooks/useVoiceRecognition';

const NaturalLanguageQuery = ({ onQueryResult }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef(null);

  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    isSupported
  } = useVoiceRecognition();

  // Predefined query suggestions
  const querySuggestions = [
    "Why is production low today?",
    "Show me today's performance",
    "What are the quality issues?",
    "Which customers need attention?",
    "How is our cash flow?",
    "What maintenance is due?",
    "Show me best performing areas",
    "What are the compliance alerts?",
    "Which farmers delivered today?",
    "What's the profit margin this week?"
  ];

  // Update query when voice transcript changes
  useEffect(() => {
    if (transcript) {
      setQuery(transcript);
    }
  }, [transcript]);

  // Filter suggestions based on current query
  useEffect(() => {
    if (query.length > 2) {
      const filtered = querySuggestions.filter(suggestion =>
        suggestion.toLowerCase().includes(query.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 5));
      setShowSuggestions(true);
    } else {
      setSuggestions(querySuggestions.slice(0, 5));
      setShowSuggestions(query.length === 0);
    }
  }, [query]);

  const handleSubmit = async (e) => {
    if (e && typeof e.preventDefault === "function") {
      e.preventDefault();
    }
    const queryText = query.trim();
    if (!queryText) return;

    setIsLoading(true);
    setResult(null);
    setError(null);
    setShowSuggestions(false);

    try {
      // Call the real AI services endpoint
      const response = await fetch('http://localhost:8000/process-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: queryText,
          context: {
            user_id: localStorage.getItem('user_id'),
            timestamp: new Date().toISOString(),
            active_batches: 3,
            current_date: new Date().toISOString().split('T')[0]
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data.response);
        if (onQueryResult) {
          onQueryResult(data.response);
        }
      } else {
        // Fallback to mock response for demo
        const mockResponse = generateMockResponse(queryText);
        setResult(mockResponse);
        if (onQueryResult) {
          onQueryResult(mockResponse);
        }
      }
    } catch (error) {
      console.error('Query error:', error);
      setError('Failed to process query. Please try again.');
      // Fallback to mock response
      const mockResponse = generateMockResponse(queryText);
      setResult(mockResponse);
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockResponse = (queryText) => {
    const queryLower = queryText.toLowerCase();
    
    if (queryLower.includes('production') && queryLower.includes('low')) {
      return {
        type: 'analysis',
        response: "Production is currently at 87% efficiency. Main factors affecting output: 1) Mill #2 needs maintenance (reducing capacity by 15%), 2) Moisture content in current paddy batch is higher than optimal (13.8% vs target 13.2%), 3) Two operators are on leave today.",
        actionable_items: [
          'Schedule Mill #2 maintenance tonight',
          'Adjust paddy drying parameters',
          'Consider overtime for remaining operators'
        ],
        metrics: {
          current_efficiency: '87%',
          target_efficiency: '95%',
          impact_factors: ['Maintenance needed', 'High moisture', 'Staff shortage']
        }
      };
    } else if (queryLower.includes('today') || queryLower.includes('performance')) {
      return {
        type: 'daily_summary',
        response: "Today's Performance Summary: Production: 2,500kg (87% of target), Quality Grade: A+, Revenue: ₹3,75,000, New Orders: 8, Customer Satisfaction: 4.6/5. Key highlights: Completed large order for ABC Traders, received quality certification renewal.",
        metrics: {
          production: '2,500 kg',
          efficiency: '87%',
          revenue: '₹3,75,000',
          orders: 8,
          satisfaction: '4.6/5',
          quality_grade: 'A+'
        }
      };
    } else if (queryLower.includes('quality')) {
      return {
        type: 'quality_analysis',
        response: "Quality Status: Overall grade A+ with 99.2% pass rate. Minor issues detected: 2.1% broken grains (target <2%), moisture slightly high at 13.4% (target 13.2%). Recommendation: Adjust milling speed and improve drying process.",
        metrics: {
          overall_grade: 'A+',
          pass_rate: '99.2%',
          broken_grains: '2.1%',
          moisture_content: '13.4%',
          foreign_matter: '0.8%'
        }
      };
    } else {
      return {
        type: 'general',
        response: `I understand you're asking about "${queryText}". Let me analyze the current data and provide insights. Based on our current operations, here's what I found relevant to your query.`,
        suggestions: [
          'Try asking about specific metrics like production or quality',
          'Ask about today\'s performance or recent trends',
          'Inquire about specific areas like customer satisfaction or inventory'
        ]
      };
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSubmit();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    handleSubmit(suggestion);
  };

  const toggleVoiceInput = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const getResultIcon = (type) => {
    switch (type) {
      case 'analysis':
        return <TrendingUpIcon color="primary" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'success':
        return <CheckCircleIcon color="success" />;
      default:
        return <AIIcon color="primary" />;
    }
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto', p: 2 }}>
      {/* Query Input */}
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AIIcon color="primary" />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Ask Rice Mill AI
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
          <TextField
            ref={inputRef}
            fullWidth
            variant="outlined"
            placeholder="Ask me anything about your rice mill operations..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => setShowSuggestions(true)}
            sx={{ mr: 1 }}
          />
          
          {isSupported && (
            <Tooltip title={isListening ? "Stop voice input" : "Start voice input"}>
              <IconButton
                onClick={toggleVoiceInput}
                color={isListening ? "secondary" : "default"}
                sx={{ mr: 1 }}
              >
                {isListening ? <MicOffIcon /> : <MicIcon />}
              </IconButton>
            </Tooltip>
          )}
          
          <IconButton
            onClick={() => handleSubmit()}
            disabled={isLoading || !query.trim()}
            color="primary"
          >
            {isLoading ? <CircularProgress size={24} /> : <SearchIcon />}
          </IconButton>
        </Box>

        {/* Voice Status */}
        {isListening && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <CircularProgress size={16} />
            <Typography variant="caption" color="secondary">
              Listening... Speak your question
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <Fade in={showSuggestions}>
          <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Try asking:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {suggestions.map((suggestion, index) => (
                <Chip
                  key={index}
                  label={suggestion}
                  onClick={() => handleSuggestionClick(suggestion)}
                  variant="outlined"
                  size="small"
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Paper>
        </Fade>
      )}

      {/* Results */}
      {result && (
        <Fade in={!!result}>
          <Card elevation={3}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                {getResultIcon(result.type)}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  AI Analysis
                </Typography>
              </Box>
              
              <Typography variant="body1" paragraph>
                {result.response}
              </Typography>

              {/* Metrics */}
              {result.metrics && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Key Metrics:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {Object.entries(result.metrics).map(([key, value]) => (
                      <Chip
                        key={key}
                        label={`${key.replace(/_/g, ' ')}: ${value}`}
                        variant="filled"
                        size="small"
                        color="primary"
                      />
                    ))}
                  </Box>
                </Box>
              )}

              {/* Actionable Items */}
              {result.actionable_items && result.actionable_items.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Recommended Actions:
                  </Typography>
                  <List dense>
                    {result.actionable_items.map((item, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemText
                          primary={item}
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {/* Suggestions */}
              {result.suggestions && result.suggestions.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Suggestions:
                  </Typography>
                  <List dense>
                    {result.suggestions.map((suggestion, index) => (
                      <ListItem key={index} sx={{ py: 0.5 }}>
                        <ListItemText
                          primary={suggestion}
                          primaryTypographyProps={{ variant: 'body2', color: 'text.secondary' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </CardContent>
          </Card>
        </Fade>
      )}
    </Box>
  );
};

export default NaturalLanguageQuery;
