import { useState, useEffect } from 'react';
import {
  Card, CardContent, CardHeader, Typography, Box,
  IconButton, Menu, MenuItem, CircularProgress
} from '@mui/material';
import { MoreVert, Refresh } from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useQuery } from 'react-query';
import api from '../services/api';

const SmartWidget = ({ widget }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  // Fetch widget data if it has an endpoint
  const { data: widgetData, isLoading } = useQuery(
    [`widget-${widget.id}`, refreshKey],
    () => {
      if (!widget.data?.endpoint) {
        return Promise.resolve(null);
      }
      return api.get(widget.data.endpoint).then(res => res.data);
    },
    {
      enabled: !!widget.data?.endpoint,
      refetchInterval: widget.refresh_interval || 60000
    }
  );

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    handleMenuClose();
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height="200px">
          <CircularProgress />
        </Box>
      );
    }

    switch (widget.type) {
      case 'chart':
        return renderChart();
      case 'metric':
        return renderMetric();
      case 'list':
        return renderList();
      case 'alert':
        return renderAlert();
      default:
        return <Typography>Widget type not supported</Typography>;
    }
  };

  const renderChart = () => {
    if (!widgetData) return null;

    const chartType = widget.data?.chart_type || 'line';
    const data = widgetData.daily_production || widgetData.quality_trends || [];

    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="output" stroke="#2E7D32" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'area':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="score" stroke="#4CAF50" fill="#4CAF50" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        );
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="efficiency" fill="#FFA726" />
            </BarChart>
          </ResponsiveContainer>
        );
      default:
        return <Typography>Chart type not supported</Typography>;
    }
  };

  const renderMetric = () => {
    return (
      <Box textAlign="center" py={4}>
        <Typography variant="h3" color="primary" fontWeight="bold">
          {widget.data?.value || 'N/A'}
        </Typography>
        <Typography variant="body1" color="textSecondary">
          {widget.data?.subtitle}
        </Typography>
      </Box>
    );
  };

  const renderList = () => {
    const items = widgetData?.items || widget.data?.items || [];
    
    return (
      <Box>
        {items.map((item, index) => (
          <Box key={index} py={1} borderBottom="1px solid #eee">
            <Typography variant="body2" fontWeight="medium">
              {item.title}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              {item.description}
            </Typography>
          </Box>
        ))}
      </Box>
    );
  };

  const renderAlert = () => {
    return (
      <Box>
        <Typography variant="body1" color="warning.main">
          {widget.data?.message}
        </Typography>
        {widget.data?.action && (
          <Typography variant="body2" color="textSecondary" mt={1}>
            Action: {widget.data.action}
          </Typography>
        )}
      </Box>
    );
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardHeader
        title={widget.title}
        action={
          <IconButton onClick={handleMenuOpen}>
            <MoreVert />
          </IconButton>
        }
        titleTypographyProps={{ variant: 'h6', fontWeight: 'medium' }}
      />
      <CardContent sx={{ pt: 0 }}>
        {renderContent()}
      </CardContent>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleRefresh}>
          <Refresh fontSize="small" sx={{ mr: 1 }} />
          Refresh
        </MenuItem>
      </Menu>
    </Card>
  );
};

export default SmartWidget;