import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  useTheme
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Legend
} from 'recharts';

const CashFlowChart = ({ data = [], chartType = 'line', title = 'Cash Flow Analysis' }) => {
  const theme = useTheme();

  // Default data if none provided
  const defaultData = [
    { date: '2024-01-01', inflow: 150000, outflow: 120000, netFlow: 30000 },
    { date: '2024-01-02', inflow: 180000, outflow: 140000, netFlow: 40000 },
    { date: '2024-01-03', inflow: 160000, outflow: 130000, netFlow: 30000 },
    { date: '2024-01-04', inflow: 200000, outflow: 150000, netFlow: 50000 },
    { date: '2024-01-05', inflow: 170000, outflow: 135000, netFlow: 35000 },
    { date: '2024-01-06', inflow: 190000, outflow: 145000, netFlow: 45000 },
    { date: '2024-01-07', inflow: 220000, outflow: 160000, netFlow: 60000 },
  ];

  const chartData = Array.isArray(data) ? data : defaultData;

  const formatCurrency = (value) => {
    return `₹${(value / 1000).toFixed(0)}K`;
  };

  const formatTooltipValue = (value, name) => {
    const formattedValue = `₹${value.toLocaleString()}`;
    const nameMap = {
      inflow: 'Cash Inflow',
      outflow: 'Cash Outflow',
      netFlow: 'Net Cash Flow'
    };
    return [formattedValue, nameMap[name] || name];
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            bgcolor: 'background.paper',
            p: 2,
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            boxShadow: 2
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            {new Date(label).toLocaleDateString()}
          </Typography>
          {payload.map((entry, index) => (
            <Typography
              key={index}
              variant="body2"
              sx={{ color: entry.color }}
            >
              {formatTooltipValue(entry.value, entry.dataKey)[1]}: {formatTooltipValue(entry.value, entry.dataKey)[0]}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 }
    };

    switch (chartType) {
      case 'area':
        return (
          <AreaChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis tickFormatter={formatCurrency} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Area
              type="monotone"
              dataKey="inflow"
              stackId="1"
              stroke={theme.palette.success.main}
              fill={theme.palette.success.main}
              fillOpacity={0.6}
              name="Cash Inflow"
            />
            <Area
              type="monotone"
              dataKey="outflow"
              stackId="2"
              stroke={theme.palette.error.main}
              fill={theme.palette.error.main}
              fillOpacity={0.6}
              name="Cash Outflow"
            />
          </AreaChart>
        );

      case 'bar':
        return (
          <BarChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis tickFormatter={formatCurrency} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="inflow" fill={theme.palette.success.main} name="Cash Inflow" />
            <Bar dataKey="outflow" fill={theme.palette.error.main} name="Cash Outflow" />
            <Bar dataKey="netFlow" fill={theme.palette.primary.main} name="Net Cash Flow" />
          </BarChart>
        );

      default: // line chart
        return (
          <LineChart {...commonProps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis tickFormatter={formatCurrency} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="inflow"
              stroke={theme.palette.success.main}
              strokeWidth={2}
              dot={{ fill: theme.palette.success.main, strokeWidth: 2, r: 4 }}
              name="Cash Inflow"
            />
            <Line
              type="monotone"
              dataKey="outflow"
              stroke={theme.palette.error.main}
              strokeWidth={2}
              dot={{ fill: theme.palette.error.main, strokeWidth: 2, r: 4 }}
              name="Cash Outflow"
            />
            <Line
              type="monotone"
              dataKey="netFlow"
              stroke={theme.palette.primary.main}
              strokeWidth={3}
              dot={{ fill: theme.palette.primary.main, strokeWidth: 2, r: 5 }}
              name="Net Cash Flow"
            />
          </LineChart>
        );
    }
  };

  // Calculate summary statistics
  const totalInflow = chartData.reduce((sum, item) => sum + item.inflow, 0);
  const totalOutflow = chartData.reduce((sum, item) => sum + item.outflow, 0);
  const netCashFlow = totalInflow - totalOutflow;
  const avgDailyInflow = totalInflow / chartData.length;
  const avgDailyOutflow = totalOutflow / chartData.length;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        
        {/* Summary Statistics */}
        <Box sx={{ display: 'flex', gap: 3, mb: 3, flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Total Inflow
            </Typography>
            <Typography variant="h6" color="success.main">
              ₹{totalInflow.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Total Outflow
            </Typography>
            <Typography variant="h6" color="error.main">
              ₹{totalOutflow.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Net Cash Flow
            </Typography>
            <Typography 
              variant="h6" 
              color={netCashFlow >= 0 ? 'success.main' : 'error.main'}
            >
              ₹{netCashFlow.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Avg Daily Inflow
            </Typography>
            <Typography variant="body1">
              ₹{avgDailyInflow.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Avg Daily Outflow
            </Typography>
            <Typography variant="body1">
              ₹{avgDailyOutflow.toLocaleString()}
            </Typography>
          </Box>
        </Box>

        {/* Chart */}
        <Box sx={{ height: 400, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            {renderChart()}
          </ResponsiveContainer>
        </Box>

        {/* Additional Insights */}
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Cash Flow Insights
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • {netCashFlow >= 0 ? 'Positive' : 'Negative'} net cash flow of ₹{Math.abs(netCashFlow).toLocaleString()}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • Average daily cash generation: ₹{(netCashFlow / chartData.length).toLocaleString()}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            • Cash flow trend: {netCashFlow >= 0 ? 'Healthy' : 'Needs attention'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default CashFlowChart;
