import React, { useState, useEffect, createContext, useContext } from 'react';
import {
  Box,
  Collapse,
  Typography,
  Button,
  IconButton,
  Tooltip,
  Chip,
  Card,
  CardContent,
  CardActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  LinearProgress,
  Badge
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  School as LearnIcon,
  Star as ExpertIcon,
  TrendingUp as ProgressIcon,
  Lightbulb as TipIcon,
  CheckCircle as CompletedIcon,
  Lock as LockedIcon,
  AutoAwesome as AIIcon
} from '@mui/icons-material';

// Context for progressive disclosure
const ProgressiveDisclosureContext = createContext();

export const useProgressiveDisclosure = () => {
  const context = useContext(ProgressiveDisclosureContext);
  if (!context) {
    throw new Error('useProgressiveDisclosure must be used within ProgressiveDisclosureProvider');
  }
  return context;
};

// User expertise tracking
class ExpertiseTracker {
  constructor() {
    this.expertise = JSON.parse(localStorage.getItem('userExpertise') || '{}');
    this.completedFeatures = JSON.parse(localStorage.getItem('completedFeatures') || '[]');
    this.featureUsage = JSON.parse(localStorage.getItem('featureUsage') || '{}');
  }

  // Calculate expertise level for a feature area (0-100)
  getExpertiseLevel(area) {
    const usage = this.featureUsage[area] || { count: 0, complexity: 0, success: 0 };
    const baseScore = Math.min(usage.count * 2, 50); // Usage frequency (max 50)
    const complexityScore = Math.min(usage.complexity * 10, 30); // Complexity handling (max 30)
    const successScore = Math.min(usage.success * 20, 20); // Success rate (max 20)
    
    return Math.min(baseScore + complexityScore + successScore, 100);
  }

  // Record feature usage
  recordUsage(area, complexity = 1, success = true) {
    if (!this.featureUsage[area]) {
      this.featureUsage[area] = { count: 0, complexity: 0, success: 0, totalAttempts: 0 };
    }

    this.featureUsage[area].count++;
    this.featureUsage[area].complexity = Math.max(this.featureUsage[area].complexity, complexity);
    this.featureUsage[area].totalAttempts++;
    
    if (success) {
      this.featureUsage[area].success++;
    }

    this.saveData();
  }

  // Mark feature as completed
  completeFeature(featureId) {
    if (!this.completedFeatures.includes(featureId)) {
      this.completedFeatures.push(featureId);
      this.saveData();
    }
  }

  // Check if feature is unlocked based on prerequisites
  isFeatureUnlocked(feature) {
    if (!feature.prerequisites) return true;
    
    return feature.prerequisites.every(prereq => {
      if (prereq.type === 'expertise') {
        return this.getExpertiseLevel(prereq.area) >= prereq.level;
      } else if (prereq.type === 'feature') {
        return this.completedFeatures.includes(prereq.featureId);
      } else if (prereq.type === 'usage') {
        const usage = this.featureUsage[prereq.area] || { count: 0 };
        return usage.count >= prereq.count;
      }
      return false;
    });
  }

  // Get recommended next features
  getRecommendedFeatures(allFeatures) {
    return allFeatures
      .filter(feature => 
        !this.completedFeatures.includes(feature.id) && 
        this.isFeatureUnlocked(feature)
      )
      .sort((a, b) => {
        // Prioritize by difficulty and relevance
        const aScore = (a.difficulty || 1) + (this.getExpertiseLevel(a.area) / 10);
        const bScore = (b.difficulty || 1) + (this.getExpertiseLevel(b.area) / 10);
        return aScore - bScore;
      })
      .slice(0, 3);
  }

  saveData() {
    localStorage.setItem('userExpertise', JSON.stringify(this.expertise));
    localStorage.setItem('completedFeatures', JSON.stringify(this.completedFeatures));
    localStorage.setItem('featureUsage', JSON.stringify(this.featureUsage));
  }
}

// Feature definition structure
const featureDefinitions = {
  'basic-navigation': {
    id: 'basic-navigation',
    title: 'Basic Navigation',
    area: 'general',
    difficulty: 1,
    description: 'Learn to navigate between different sections',
    steps: [
      'Click on Dashboard to view overview',
      'Navigate to Farmers section',
      'Explore the sidebar menu'
    ]
  },
  'farmer-management': {
    id: 'farmer-management',
    title: 'Farmer Management',
    area: 'farmers',
    difficulty: 2,
    description: 'Manage farmer information and contracts',
    prerequisites: [
      { type: 'feature', featureId: 'basic-navigation' }
    ],
    steps: [
      'Add a new farmer',
      'Update farmer information',
      'View farmer analytics'
    ]
  },
  'advanced-analytics': {
    id: 'advanced-analytics',
    title: 'Advanced Analytics',
    area: 'analytics',
    difficulty: 4,
    description: 'Use advanced analytics and AI insights',
    prerequisites: [
      { type: 'expertise', area: 'general', level: 30 },
      { type: 'usage', area: 'farmers', count: 5 }
    ],
    steps: [
      'Access analytics dashboard',
      'Create custom reports',
      'Use AI insights'
    ]
  },
  'voice-commands': {
    id: 'voice-commands',
    title: 'Voice Commands',
    area: 'ai',
    difficulty: 3,
    description: 'Use voice commands for hands-free operation',
    prerequisites: [
      { type: 'expertise', area: 'general', level: 20 }
    ],
    steps: [
      'Enable voice commands',
      'Try basic voice navigation',
      'Use voice for data entry'
    ]
  }
};

// Progressive Feature Component
const ProgressiveFeature = ({ 
  feature, 
  isUnlocked, 
  isCompleted, 
  onComplete, 
  onStartLearning,
  children 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isLearning, setIsLearning] = useState(false);

  const handleStartLearning = () => {
    setIsLearning(true);
    setIsExpanded(true);
    if (onStartLearning) {
      onStartLearning(feature.id);
    }
  };

  const handleStepComplete = () => {
    if (currentStep < feature.steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setIsLearning(false);
      if (onComplete) {
        onComplete(feature.id);
      }
    }
  };

  const getDifficultyColor = (difficulty) => {
    if (difficulty <= 2) return 'success';
    if (difficulty <= 3) return 'warning';
    return 'error';
  };

  const getDifficultyLabel = (difficulty) => {
    if (difficulty <= 2) return 'Beginner';
    if (difficulty <= 3) return 'Intermediate';
    return 'Advanced';
  };

  return (
    <Card 
      sx={{ 
        mb: 2, 
        opacity: isUnlocked ? 1 : 0.6,
        border: isCompleted ? '2px solid' : 'none',
        borderColor: 'success.main'
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">
              {feature.title}
            </Typography>
            
            {isCompleted && <CompletedIcon color="success" />}
            {!isUnlocked && <LockedIcon color="disabled" />}
          </Box>

          <Box sx={{ display: 'flex', gap: 1 }}>
            <Chip
              label={getDifficultyLabel(feature.difficulty)}
              color={getDifficultyColor(feature.difficulty)}
              size="small"
            />
            
            <IconButton
              onClick={() => setIsExpanded(!isExpanded)}
              disabled={!isUnlocked}
            >
              {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" paragraph>
          {feature.description}
        </Typography>

        {/* Prerequisites */}
        {feature.prerequisites && !isUnlocked && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Prerequisites: Complete basic navigation and gain more experience
            </Typography>
          </Alert>
        )}

        <Collapse in={isExpanded}>
          {isLearning ? (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Learning Progress
              </Typography>
              
              <Stepper activeStep={currentStep} orientation="vertical">
                {feature.steps.map((step, index) => (
                  <Step key={index}>
                    <StepLabel>
                      {step}
                    </StepLabel>
                    <StepContent>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" paragraph>
                          {step}
                        </Typography>
                        <Button
                          variant="contained"
                          onClick={handleStepComplete}
                          size="small"
                        >
                          {index === feature.steps.length - 1 ? 'Complete' : 'Next Step'}
                        </Button>
                      </Box>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              {children}
            </Box>
          )}
        </Collapse>
      </CardContent>

      {isUnlocked && !isCompleted && !isLearning && (
        <CardActions>
          <Button
            startIcon={<LearnIcon />}
            onClick={handleStartLearning}
            variant="outlined"
          >
            Start Learning
          </Button>
        </CardActions>
      )}
    </Card>
  );
};

// Expertise Level Display
const ExpertiseDisplay = ({ area, level, onImprove }) => {
  const getExpertiseLabel = (level) => {
    if (level < 20) return 'Beginner';
    if (level < 50) return 'Intermediate';
    if (level < 80) return 'Advanced';
    return 'Expert';
  };

  const getExpertiseColor = (level) => {
    if (level < 20) return 'error';
    if (level < 50) return 'warning';
    if (level < 80) return 'info';
    return 'success';
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            {area.charAt(0).toUpperCase() + area.slice(1)} Expertise
          </Typography>
          <Chip
            icon={level >= 80 ? <ExpertIcon /> : <ProgressIcon />}
            label={getExpertiseLabel(level)}
            color={getExpertiseColor(level)}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <LinearProgress
            variant="determinate"
            value={level}
            color={getExpertiseColor(level)}
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {level}% mastery
          </Typography>
        </Box>

        {level < 100 && (
          <Button
            startIcon={<TipIcon />}
            onClick={() => onImprove && onImprove(area)}
            variant="outlined"
            size="small"
          >
            Get Tips to Improve
          </Button>
        )}
      </CardContent>
    </Card>
  );
};

// Main Progressive Disclosure Provider
export const ProgressiveDisclosureProvider = ({ children }) => {
  const [expertiseTracker] = useState(() => new ExpertiseTracker());
  const [recommendedFeatures, setRecommendedFeatures] = useState([]);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    // Check if user is new (no completed features)
    if (expertiseTracker.completedFeatures.length === 0) {
      setShowOnboarding(true);
    }

    // Update recommended features
    const features = Object.values(featureDefinitions);
    const recommended = expertiseTracker.getRecommendedFeatures(features);
    setRecommendedFeatures(recommended);
  }, []);

  const recordFeatureUsage = (area, complexity = 1, success = true) => {
    expertiseTracker.recordUsage(area, complexity, success);
    
    // Update recommendations
    const features = Object.values(featureDefinitions);
    const recommended = expertiseTracker.getRecommendedFeatures(features);
    setRecommendedFeatures(recommended);
  };

  const completeFeature = (featureId) => {
    expertiseTracker.completeFeature(featureId);
    
    // Update recommendations
    const features = Object.values(featureDefinitions);
    const recommended = expertiseTracker.getRecommendedFeatures(features);
    setRecommendedFeatures(recommended);
  };

  const getExpertiseLevel = (area) => {
    return expertiseTracker.getExpertiseLevel(area);
  };

  const isFeatureUnlocked = (featureId) => {
    const feature = featureDefinitions[featureId];
    return feature ? expertiseTracker.isFeatureUnlocked(feature) : false;
  };

  const isFeatureCompleted = (featureId) => {
    return expertiseTracker.completedFeatures.includes(featureId);
  };

  const contextValue = {
    recordFeatureUsage,
    completeFeature,
    getExpertiseLevel,
    isFeatureUnlocked,
    isFeatureCompleted,
    recommendedFeatures,
    showOnboarding,
    setShowOnboarding,
    expertiseTracker,
    ProgressiveFeature,
    ExpertiseDisplay
  };

  return (
    <ProgressiveDisclosureContext.Provider value={contextValue}>
      {children}
    </ProgressiveDisclosureContext.Provider>
  );
};

// Learning Center Component
export const LearningCenter = () => {
  const {
    recommendedFeatures,
    completeFeature,
    getExpertiseLevel,
    isFeatureUnlocked,
    isFeatureCompleted,
    ProgressiveFeature,
    ExpertiseDisplay
  } = useProgressiveDisclosure();

  const expertiseAreas = ['general', 'farmers', 'production', 'analytics', 'ai'];

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Learning Center
      </Typography>

      {/* Expertise Overview */}
      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        Your Expertise
      </Typography>
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        {expertiseAreas.map(area => (
          <Box key={area} sx={{ minWidth: 300, flex: 1 }}>
            <ExpertiseDisplay
              area={area}
              level={getExpertiseLevel(area)}
            />
          </Box>
        ))}
      </Box>

      {/* Recommended Features */}
      {recommendedFeatures.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Recommended for You
          </Typography>
          
          {recommendedFeatures.map(feature => (
            <ProgressiveFeature
              key={feature.id}
              feature={feature}
              isUnlocked={isFeatureUnlocked(feature.id)}
              isCompleted={isFeatureCompleted(feature.id)}
              onComplete={completeFeature}
            >
              <Typography variant="body2">
                This feature will help you become more efficient in {feature.area}.
              </Typography>
            </ProgressiveFeature>
          ))}
        </Box>
      )}

      {/* All Features */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          All Features
        </Typography>
        
        {Object.values(featureDefinitions).map(feature => (
          <ProgressiveFeature
            key={feature.id}
            feature={feature}
            isUnlocked={isFeatureUnlocked(feature.id)}
            isCompleted={isFeatureCompleted(feature.id)}
            onComplete={completeFeature}
          >
            <Typography variant="body2">
              Master this feature to unlock advanced capabilities.
            </Typography>
          </ProgressiveFeature>
        ))}
      </Box>
    </Box>
  );
};

export default ProgressiveDisclosureProvider;
