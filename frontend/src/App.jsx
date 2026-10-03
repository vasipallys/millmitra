import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, CircularProgress, Typography } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import PWAInstallPrompt from './components/PWAInstallPrompt';
import { AssistantProvider } from './assistant/AssistantBridge';
import AssistantOverlay from './assistant/AssistantOverlay';
import ToastProvider from './components/common/ToastProvider';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Farmers from './pages/Farmers';
import Inventory from './pages/Inventory';
import Production from './pages/Production';
import Sales from './pages/Sales';
import Finance from './pages/Finance';
import Customers from './pages/Customers';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';
import Notifications from './pages/Notifications';
import QualityControl from './pages/QualityControl';
import FinancialIntelligence from './pages/FinancialIntelligence';
import ComplianceGST from './pages/ComplianceGST';
import AnalyticsReporting from './pages/AnalyticsReporting';
import MillFlow from './pages/MillFlow';
import Users from './pages/Users';
import Access from './pages/Access';
import Lookups from './pages/Lookups';
import RequireAccess from './components/RequireAccess';
import { permissionForPath } from './utils/permissions';

// Services
import { authService } from './services/authService';
import { recordNavigation } from './telemetry';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2E7D32', // Green for rice/agriculture theme
      light: '#4CAF50',
      dark: '#1B5E20',
    },
    secondary: {
      main: '#FF9800', // Orange for accent
      light: '#FFB74D',
      dark: '#F57C00',
    },
    background: {
      default: '#F5F5F5',
      paper: '#FFFFFF',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
      defaultProps: {
        disableElevation: true,
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          '&:focus-visible': {
            outline: '2px solid #2E7D32',
            outlineOffset: 2,
          },
        },
      },
    },
    MuiDialog: {
      defaultProps: {
        fullWidth: true,
      },
    },
    MuiTooltip: {
      defaultProps: {
        enterDelay: 400,
      },
    },
  },
});

// Create QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function Guard({ user, children }) {
  const location = useLocation();
  return (
    <RequireAccess user={user} permission={permissionForPath(location.pathname)}>
      {children}
    </RequireAccess>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AppContent />
      </ToastProvider>
    </QueryClientProvider>
  );
}

function AppContent() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [user, setUser] = useState(null);
  const location = useLocation();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  useEffect(() => {
    recordNavigation(location.pathname);
  }, [location.pathname]);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const userData = await authService.getCurrentUser();
        if (userData) {
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          setUser(null);
          setIsAuthenticated(false);
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  if (loading) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box
          display="flex"
          flexDirection="column"
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          bgcolor="background.default"
          gap={2}
          role="status"
          aria-live="polite"
        >
          <CircularProgress />
          <Typography variant="body2" color="text.secondary">
            Opening MillMitra…
          </Typography>
        </Box>
      </ThemeProvider>
    );
  }

  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Login onLogin={handleLogin} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AssistantProvider>
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        {/* Sidebar */}
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          user={user}
        />

        {/* Main Content */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0, // Prevent flex item from overflowing
          }}
        >
          {/* Top Navigation */}
          <Navbar 
            onMenuClick={toggleSidebar}
            onLogout={handleLogout}
            user={user}
            onUserChange={setUser}
          />
          
          {/* Page Content */}
          <Box sx={{
            flexGrow: 1,
            p: 0,
            bgcolor: 'background.default',
            overflow: 'auto',
            minWidth: 0
          }}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Guard user={user}><Dashboard /></Guard>} />
              <Route path="/mill-flow" element={<Guard user={user}><MillFlow /></Guard>} />
              <Route path="/farmers/*" element={<Guard user={user}><Farmers /></Guard>} />
              <Route path="/inventory/*" element={<Guard user={user}><Inventory /></Guard>} />
              <Route path="/production/*" element={<Guard user={user}><Production /></Guard>} />
              <Route path="/sales/*" element={<Guard user={user}><Sales /></Guard>} />
              <Route path="/finance/*" element={<Guard user={user}><Finance /></Guard>} />
              <Route path="/customers/*" element={<Guard user={user}><Customers /></Guard>} />
              <Route path="/analytics" element={<Guard user={user}><Analytics /></Guard>} />
              <Route path="/quality-control" element={<Guard user={user}><QualityControl /></Guard>} />
              <Route path="/financial-intelligence" element={<Guard user={user}><FinancialIntelligence /></Guard>} />
              <Route path="/compliance-gst" element={<Guard user={user}><ComplianceGST /></Guard>} />
              <Route path="/analytics-reporting" element={<Guard user={user}><AnalyticsReporting /></Guard>} />
              <Route path="/notifications" element={<Guard user={user}><Notifications /></Guard>} />
              <Route path="/settings" element={<Guard user={user}><Settings /></Guard>} />
              <Route path="/users" element={<Guard user={user}><Users currentUser={user} /></Guard>} />
              <Route path="/access" element={<Guard user={user}><Access /></Guard>} />
              <Route path="/lookups" element={<Guard user={user}><Lookups /></Guard>} />
            </Routes>
          </Box>
        </Box>
        
        <AssistantOverlay />
        <PWAInstallPrompt />
      </Box>
      </AssistantProvider>
    </ThemeProvider>
  );
}

export default App;
