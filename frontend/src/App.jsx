import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import VoiceInterface from './components/VoiceInterface';
import PWAInstallPrompt from './components/PWAInstallPrompt';

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

// Services
import { authService } from './services/authService';

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
    },
  },
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const userData = await authService.getCurrentUser();
        setUser(userData);
        setIsAuthenticated(true);
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
          justifyContent="center"
          alignItems="center"
          minHeight="100vh"
          bgcolor="background.default"
        >
          <div>Loading...</div>
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
          />
          
          {/* Page Content */}
          <Box sx={{
            flexGrow: 1,
            p: 0, // Remove padding to eliminate gaps
            bgcolor: 'background.default',
            overflow: 'hidden' // Prevent any overflow issues
          }}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/login" element={<Login />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/farmers/*" element={<Farmers />} />
              <Route path="/inventory/*" element={<Inventory />} />
              <Route path="/production/*" element={<Production />} />
              <Route path="/sales/*" element={<Sales />} />
              <Route path="/finance/*" element={<Finance />} />
              <Route path="/customers/*" element={<Customers />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/quality-control" element={<QualityControl />} />
              <Route path="/financial-intelligence" element={<FinancialIntelligence />} />
              <Route path="/compliance-gst" element={<ComplianceGST />} />
              <Route path="/analytics" element={<AnalyticsReporting />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Box>
        </Box>
        
        {/* Voice Interface */}
        <VoiceInterface />

        {/* PWA Install Prompt */}
        <PWAInstallPrompt />
      </Box>
    </ThemeProvider>
  );
}

export default App;
