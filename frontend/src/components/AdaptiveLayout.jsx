import React, { useState, useEffect, useContext, createContext } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Chip,
  Switch,
  FormControlLabel,
  Menu,
  MenuItem,
  Alert
} from '@mui/material';
import {
  DashboardCustomize as CustomizeIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  SwapVert as ReorderIcon,
  Settings as SettingsIcon,
  AutoAwesome as AIIcon
} from '@mui/icons-material';

// Context for adaptive layout
const AdaptiveLayoutContext = createContext();

export const useAdaptiveLayout = () => {
  const context = useContext(AdaptiveLayoutContext);
  if (!context) {
    throw new Error('useAdaptiveLayout must be used within AdaptiveLayoutProvider');
  }
  return context;
};

// User behavior tracking
class UserBehaviorTracker {
  constructor() {
    this.interactions = JSON.parse(localStorage.getItem('userInteractions') || '{}');
    this.sessionStart = Date.now();
    this.currentSession = [];
  }

  trackInteraction(component, action, metadata = {}) {
    const interaction = {
      component,
      action,
      timestamp: Date.now(),
      timeOfDay: new Date().getHours(),
      dayOfWeek: new Date().getDay(),
      metadata
    };

    this.currentSession.push(interaction);
    
    // Update persistent storage
    const key = `${component}_${action}`;
    if (!this.interactions[key]) {
      this.interactions[key] = {
        count: 0,
        lastUsed: null,
        timePatterns: {},
        dayPatterns: {}
      };
    }

    this.interactions[key].count++;
    this.interactions[key].lastUsed = Date.now();
    
    // Track time patterns
    const hour = interaction.timeOfDay;
    this.interactions[key].timePatterns[hour] = (this.interactions[key].timePatterns[hour] || 0) + 1;
    
    // Track day patterns
    const day = interaction.dayOfWeek;
    this.interactions[key].dayPatterns[day] = (this.interactions[key].dayPatterns[day] || 0) + 1;

    this.saveInteractions();
  }

  getComponentPriority(component) {
    const interactions = this.interactions[component] || { count: 0, lastUsed: 0 };
    const recency = Date.now() - (interactions.lastUsed || 0);
    const frequency = interactions.count;
    
    // Calculate priority score (higher = more important)
    const recencyScore = Math.max(0, 100 - (recency / (1000 * 60 * 60 * 24))); // Decay over days
    const frequencyScore = Math.min(100, frequency * 5); // Cap at 100
    
    return (recencyScore * 0.3) + (frequencyScore * 0.7);
  }

  getTimeBasedRecommendations() {
    const currentHour = new Date().getHours();
    const currentDay = new Date().getDay();
    
    const recommendations = [];
    
    Object.entries(this.interactions).forEach(([key, data]) => {
      const hourUsage = data.timePatterns[currentHour] || 0;
      const dayUsage = data.dayPatterns[currentDay] || 0;
      
      if (hourUsage > 2 || dayUsage > 5) {
        recommendations.push({
          component: key.split('_')[0],
          score: hourUsage + dayUsage,
          reason: `Frequently used at this time`
        });
      }
    });

    return recommendations.sort((a, b) => b.score - a.score);
  }

  saveInteractions() {
    localStorage.setItem('userInteractions', JSON.stringify(this.interactions));
  }

  getSessionSummary() {
    return {
      duration: Date.now() - this.sessionStart,
      interactions: this.currentSession.length,
      topComponents: this.currentSession
        .reduce((acc, interaction) => {
          acc[interaction.component] = (acc[interaction.component] || 0) + 1;
          return acc;
        }, {})
    };
  }
}

// Layout configuration based on user role and behavior
const getLayoutConfig = (userRole, userBehavior, timeOfDay) => {
  const baseLayouts = {
    admin: {
      priority: ['dashboard', 'analytics', 'finance', 'production', 'farmers', 'customers'],
      defaultVisible: ['dashboard', 'analytics', 'finance', 'production'],
      timeBasedAdjustments: {
        morning: ['production', 'quality', 'farmers'],
        afternoon: ['sales', 'customers', 'finance'],
        evening: ['analytics', 'reports', 'planning']
      }
    },
    manager: {
      priority: ['production', 'quality', 'inventory', 'dashboard', 'analytics'],
      defaultVisible: ['production', 'quality', 'inventory', 'dashboard'],
      timeBasedAdjustments: {
        morning: ['production', 'quality', 'inventory'],
        afternoon: ['sales', 'customers'],
        evening: ['analytics', 'reports']
      }
    },
    operator: {
      priority: ['production', 'quality', 'inventory', 'farmers'],
      defaultVisible: ['production', 'quality', 'inventory'],
      timeBasedAdjustments: {
        morning: ['production', 'farmers'],
        afternoon: ['quality', 'inventory'],
        evening: ['reports']
      }
    },
    accountant: {
      priority: ['finance', 'customers', 'analytics', 'dashboard'],
      defaultVisible: ['finance', 'customers', 'analytics'],
      timeBasedAdjustments: {
        morning: ['finance', 'payments'],
        afternoon: ['customers', 'invoicing'],
        evening: ['reports', 'analytics']
      }
    }
  };

  const config = baseLayouts[userRole] || baseLayouts.operator;
  
  // Adjust based on user behavior
  if (userBehavior) {
    const behaviorPriorities = Object.keys(userBehavior.interactions)
      .map(key => key.split('_')[0])
      .filter((component, index, arr) => arr.indexOf(component) === index)
      .sort((a, b) => userBehavior.getComponentPriority(b) - userBehavior.getComponentPriority(a));
    
    // Merge behavior-based priorities with role-based priorities
    config.priority = [...new Set([...behaviorPriorities, ...config.priority])];
  }

  return config;
};

// Adaptive Widget Component
const AdaptiveWidget = ({ 
  id, 
  title, 
  children, 
  priority = 0, 
  isVisible = true, 
  onVisibilityChange,
  onInteraction,
  size = 'medium'
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const handleInteraction = (action, metadata = {}) => {
    if (onInteraction) {
      onInteraction(id, action, metadata);
    }
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
    handleInteraction('menu_opened');
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const toggleVisibility = () => {
    const newVisibility = !isVisible;
    if (onVisibilityChange) {
      onVisibilityChange(id, newVisibility);
    }
    handleInteraction('visibility_toggled', { visible: newVisibility });
  };

  const sizeMap = {
    small: { xs: 12, sm: 6, md: 4 },
    medium: { xs: 12, sm: 6, md: 6 },
    large: { xs: 12, sm: 12, md: 8 },
    full: { xs: 12, sm: 12, md: 12 }
  };

  if (!isVisible) return null;

  return (
    <Grid item {...sizeMap[size]}>
      <Paper
        elevation={isHovered ? 4 : 2}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={() => handleInteraction('clicked')}
        sx={{
          p: 2,
          height: '100%',
          position: 'relative',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          border: priority > 80 ? '2px solid' : 'none',
          borderColor: 'primary.main',
          '&:hover': {
            transform: 'translateY(-2px)'
          }
        }}
      >
        {/* Widget Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6" component="h3">
            {title}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {priority > 80 && (
              <Tooltip title="High priority based on your usage">
                <Chip 
                  icon={<AIIcon />} 
                  label="AI Recommended" 
                  size="small" 
                  color="primary" 
                  variant="outlined"
                />
              </Tooltip>
            )}
            
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleMenuOpen(e);
              }}
              sx={{ opacity: isHovered ? 1 : 0.3 }}
            >
              <SettingsIcon fontSize="small" />
            </IconButton>
          </Box>
        </Box>

        {/* Widget Content */}
        <Box onClick={() => handleInteraction('content_interacted')}>
          {children}
        </Box>

        {/* Widget Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          onClick={(e) => e.stopPropagation()}
        >
          <MenuItem onClick={toggleVisibility}>
            {isVisible ? <VisibilityOffIcon /> : <VisibilityIcon />}
            <Typography sx={{ ml: 1 }}>
              {isVisible ? 'Hide Widget' : 'Show Widget'}
            </Typography>
          </MenuItem>
          <MenuItem onClick={() => {
            handleInteraction('refresh_requested');
            handleMenuClose();
          }}>
            <ReorderIcon />
            <Typography sx={{ ml: 1 }}>Refresh Data</Typography>
          </MenuItem>
        </Menu>
      </Paper>
    </Grid>
  );
};

// Main Adaptive Layout Provider
export const AdaptiveLayoutProvider = ({ children, userRole = 'operator' }) => {
  const [behaviorTracker] = useState(() => new UserBehaviorTracker());
  const [layoutConfig, setLayoutConfig] = useState(() => 
    getLayoutConfig(userRole, behaviorTracker, new Date().getHours())
  );
  const [widgetVisibility, setWidgetVisibility] = useState(() => {
    const saved = localStorage.getItem('widgetVisibility');
    return saved ? JSON.parse(saved) : {};
  });
  const [adaptiveMode, setAdaptiveMode] = useState(
    localStorage.getItem('adaptiveMode') !== 'false'
  );
  const [recommendations, setRecommendations] = useState([]);

  // Update layout based on time and behavior
  useEffect(() => {
    const updateLayout = () => {
      const newConfig = getLayoutConfig(userRole, behaviorTracker, new Date().getHours());
      setLayoutConfig(newConfig);
      
      if (adaptiveMode) {
        const newRecommendations = behaviorTracker.getTimeBasedRecommendations();
        setRecommendations(newRecommendations);
      }
    };

    // Update every hour
    const interval = setInterval(updateLayout, 60 * 60 * 1000);
    updateLayout(); // Initial update

    return () => clearInterval(interval);
  }, [userRole, adaptiveMode]);

  const trackInteraction = (component, action, metadata) => {
    behaviorTracker.trackInteraction(component, action, metadata);
    
    // Update layout if significant interaction
    if (['clicked', 'content_interacted'].includes(action)) {
      const newConfig = getLayoutConfig(userRole, behaviorTracker, new Date().getHours());
      setLayoutConfig(newConfig);
    }
  };

  const handleWidgetVisibilityChange = (widgetId, isVisible) => {
    const newVisibility = { ...widgetVisibility, [widgetId]: isVisible };
    setWidgetVisibility(newVisibility);
    localStorage.setItem('widgetVisibility', JSON.stringify(newVisibility));
  };

  const toggleAdaptiveMode = () => {
    const newMode = !adaptiveMode;
    setAdaptiveMode(newMode);
    localStorage.setItem('adaptiveMode', newMode.toString());
  };

  const getWidgetPriority = (widgetId) => {
    return behaviorTracker.getComponentPriority(widgetId);
  };

  const isWidgetVisible = (widgetId) => {
    return widgetVisibility[widgetId] !== false; // Default to visible
  };

  const contextValue = {
    layoutConfig,
    trackInteraction,
    handleWidgetVisibilityChange,
    getWidgetPriority,
    isWidgetVisible,
    adaptiveMode,
    toggleAdaptiveMode,
    recommendations,
    behaviorTracker,
    AdaptiveWidget
  };

  return (
    <AdaptiveLayoutContext.Provider value={contextValue}>
      <Box>
        {/* Adaptive Mode Controls */}
        <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={adaptiveMode}
                onChange={toggleAdaptiveMode}
                color="primary"
              />
            }
            label="AI Adaptive Layout"
          />
          
          {adaptiveMode && recommendations.length > 0 && (
            <Alert severity="info" sx={{ flexGrow: 1 }}>
              <Typography variant="body2">
                AI suggests prioritizing: {recommendations.slice(0, 3).map(r => r.component).join(', ')}
              </Typography>
            </Alert>
          )}
        </Box>

        {children}
      </Box>
    </AdaptiveLayoutContext.Provider>
  );
};

// Hook for easy access to adaptive widget component
export const useAdaptiveWidget = () => {
  const { AdaptiveWidget, trackInteraction, getWidgetPriority, isWidgetVisible, handleWidgetVisibilityChange } = useAdaptiveLayout();
  
  return {
    AdaptiveWidget,
    trackInteraction,
    getWidgetPriority,
    isWidgetVisible,
    handleWidgetVisibilityChange
  };
};

export default AdaptiveLayoutProvider;
