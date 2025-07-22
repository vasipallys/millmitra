import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Receipt,
  Assessment,
  CheckCircle,
  Warning,
  Error,
  AccountBalance,
  Description,
  Schedule,
  Security,
  ExpandMore,
  GetApp,
  Upload,
  Calculate,
  Gavel,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const ComplianceGST = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [dashboardData, setDashboardData] = useState(null);
  const [complianceStatus, setComplianceStatus] = useState(null);
  const [gstCalculator, setGstCalculator] = useState({
    amount: '',
    product_category: 'processed_rice',
    transaction_type: 'sale'
  });
  const [gstResult, setGstResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showInvoiceDialog, setShowInvoiceDialog] = useState(false);
  const [invoiceForm, setInvoiceForm] = useState({
    customer_id: '',
    items: [{ description: '', quantity: 1, unit_price: 0, product_category: 'processed_rice' }],
    invoice_date: new Date().toISOString().split('T')[0],
    due_date: '',
    payment_terms: 'Net 30'
  });

  // Mock data for demonstration
  const mockComplianceData = {
    overall_status: 'good',
    compliance_score: 87.5,
    checks: [
      {
        category: 'GST Compliance',
        score: 95,
        status: 'compliant',
        issues: []
      },
      {
        category: 'FSSAI Compliance',
        score: 85,
        status: 'compliant',
        issues: ['License expiring in 45 days']
      },
      {
        category: 'Pollution Control',
        score: 90,
        status: 'compliant',
        issues: []
      },
      {
        category: 'Labor Compliance',
        score: 80,
        status: 'compliant',
        issues: ['PF registration pending for 2 employees']
      }
    ],
    alerts: [
      {
        type: 'warning',
        category: 'license_renewal',
        title: 'FSSAI License Renewal',
        message: 'FSSAI license expires in 45 days'
      }
    ]
  };

  const mockGSTData = {
    monthly_summary: {
      total_sales: 1250000,
      total_gst_collected: 62500,
      gstr1_filed: true,
      gstr3b_filed: true,
      due_dates: {
        gstr1: '11-02-2024',
        gstr3b: '20-02-2024'
      }
    },
    tax_breakdown: [
      { name: '5% GST', value: 62500, color: '#4CAF50' },
      { name: '12% GST', value: 0, color: '#FF9800' },
      { name: '18% GST', value: 0, color: '#F44336' },
      { name: '28% GST', value: 0, color: '#9C27B0' }
    ]
  };

  const complianceCalendar = [
    { date: '11-02-2024', task: 'GSTR-1 Filing', status: 'pending', priority: 'high' },
    { date: '20-02-2024', task: 'GSTR-3B Filing', status: 'pending', priority: 'high' },
    { date: '31-03-2024', task: 'Annual Return', status: 'upcoming', priority: 'medium' },
    { date: '15-04-2024', task: 'TDS Return Q4', status: 'upcoming', priority: 'medium' }
  ];

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Simulate API calls
      setTimeout(() => {
        setDashboardData(mockGSTData);
        setComplianceStatus(mockComplianceData);
        setLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setLoading(false);
    }
  };

  const calculateGST = async () => {
    try {
      const response = await fetch('/api/compliance/gst/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(gstCalculator)
      });

      const result = await response.json();

      if (result.success) {
        setGstResult(result);
      } else {
        alert('GST calculation failed: ' + result.error);
      }
    } catch (error) {
      alert('Network error during GST calculation');
    }
  };

  const generateGSTInvoice = async () => {
    try {
      const response = await fetch('/api/compliance/invoice/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(invoiceForm)
      });

      const result = await response.json();

      if (result.success) {
        alert('GST Invoice generated successfully!');
        setShowInvoiceDialog(false);
        setInvoiceForm({
          customer_id: '',
          items: [{ description: '', quantity: 1, unit_price: 0, product_category: 'processed_rice' }],
          invoice_date: new Date().toISOString().split('T')[0],
          due_date: '',
          payment_terms: 'Net 30'
        });
      } else {
        alert('Invoice generation failed: ' + result.error);
      }
    } catch (error) {
      alert('Network error during invoice generation');
    }
  };

  const addInvoiceItem = () => {
    setInvoiceForm({
      ...invoiceForm,
      items: [...invoiceForm.items, { description: '', quantity: 1, unit_price: 0, product_category: 'processed_rice' }]
    });
  };

  const updateInvoiceItem = (index, field, value) => {
    const updatedItems = [...invoiceForm.items];
    updatedItems[index][field] = value;
    setInvoiceForm({ ...invoiceForm, items: updatedItems });
  };

  const getComplianceColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 75) return 'info';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'compliant': return <CheckCircle color="success" />;
      case 'non_compliant': return <Error color="error" />;
      case 'pending': return <Warning color="warning" />;
      default: return <Warning color="warning" />;
    }
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Compliance Data...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Compliance & GST Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Automated regulatory compliance and tax management
        </Typography>
      </Box>

      {/* Alerts */}
      {complianceStatus?.alerts?.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {complianceStatus.alerts.map((alert, index) => (
            <Alert 
              key={index} 
              severity={alert.type} 
              sx={{ mb: 1 }}
              action={
                <Button color="inherit" size="small">
                  Action Required
                </Button>
              }
            >
              <strong>{alert.title}:</strong> {alert.message}
            </Alert>
          ))}
        </Box>
      )}

      {/* Compliance Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab icon={<Assessment />} label="Dashboard" />
          <Tab icon={<Receipt />} label="GST Management" />
          <Tab icon={<Security />} label="Compliance Status" />
          <Tab icon={<Schedule />} label="Calendar" />
          <Tab icon={<Calculate />} label="GST Calculator" />
        </Tabs>
      </Paper>

      {/* Dashboard Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          {/* Compliance Score Card */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" color="primary.main">
                    {complianceStatus?.compliance_score}
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    Compliance Score
                  </Typography>
                  <Chip 
                    label={complianceStatus?.overall_status?.toUpperCase()} 
                    color={getComplianceColor(complianceStatus?.compliance_score)} 
                    sx={{ mt: 1 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* GST Summary Card */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Monthly GST Summary
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Total Sales
                  </Typography>
                  <Typography variant="h5">
                    ₹{dashboardData?.monthly_summary?.total_sales?.toLocaleString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    GST Collected
                  </Typography>
                  <Typography variant="h5" color="success.main">
                    ₹{dashboardData?.monthly_summary?.total_gst_collected?.toLocaleString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Filing Status Card */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Filing Status
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {getStatusIcon(dashboardData?.monthly_summary?.gstr1_filed ? 'compliant' : 'pending')}
                  <Typography variant="body1" sx={{ ml: 1 }}>
                    GSTR-1: {dashboardData?.monthly_summary?.gstr1_filed ? 'Filed' : 'Pending'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {getStatusIcon(dashboardData?.monthly_summary?.gstr3b_filed ? 'compliant' : 'pending')}
                  <Typography variant="body1" sx={{ ml: 1 }}>
                    GSTR-3B: {dashboardData?.monthly_summary?.gstr3b_filed ? 'Filed' : 'Pending'}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Compliance Areas */}
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Compliance Areas
                </Typography>
                {complianceStatus?.checks?.map((check, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body1" fontWeight="medium">
                        {check.category}
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {check.score}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={check.score} 
                      sx={{ height: 8, borderRadius: 4 }}
                      color={getComplianceColor(check.score)}
                    />
                    {check.issues?.length > 0 && (
                      <Typography variant="body2" color="warning.main" sx={{ mt: 0.5 }}>
                        Issues: {check.issues.join(', ')}
                      </Typography>
                    )}
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Tax Breakdown */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Tax Breakdown
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={dashboardData?.tax_breakdown}
                      cx="50%"
                      cy="50%"
                      outerRadius={60}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => value > 0 ? `${name}: ₹${value.toLocaleString()}` : ''}
                    >
                      {dashboardData?.tax_breakdown?.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `₹${value.toLocaleString()}`} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* GST Management Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  GST Returns
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<Description />}
                    sx={{ mr: 2, mb: 1 }}
                  >
                    Generate GSTR-1
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<Description />}
                    sx={{ mb: 1 }}
                  >
                    Generate GSTR-3B
                  </Button>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Next due dates:
                </Typography>
                <Typography variant="body2">
                  GSTR-1: {dashboardData?.monthly_summary?.due_dates?.gstr1}
                </Typography>
                <Typography variant="body2">
                  GSTR-3B: {dashboardData?.monthly_summary?.due_dates?.gstr3b}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Invoice Management
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Receipt />}
                  onClick={() => setShowInvoiceDialog(true)}
                  sx={{ mb: 2 }}
                >
                  Generate GST Invoice
                </Button>
                <Typography variant="body2" color="text.secondary">
                  Create GST-compliant invoices with automatic tax calculations
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent GST Activities
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Activity</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Amount</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>15-01-2024</TableCell>
                        <TableCell>GSTR-1 Filed</TableCell>
                        <TableCell>
                          <Chip label="Completed" color="success" size="small" />
                        </TableCell>
                        <TableCell>₹62,500</TableCell>
                        <TableCell>
                          <Button size="small" startIcon={<GetApp />}>
                            Download
                          </Button>
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>20-01-2024</TableCell>
                        <TableCell>GSTR-3B Filed</TableCell>
                        <TableCell>
                          <Chip label="Completed" color="success" size="small" />
                        </TableCell>
                        <TableCell>₹58,000</TableCell>
                        <TableCell>
                          <Button size="small" startIcon={<GetApp />}>
                            Download
                          </Button>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Compliance Status Tab */}
      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          {complianceStatus?.checks?.map((check, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getStatusIcon(check.status)}
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      {check.category}
                    </Typography>
                    <Box sx={{ flexGrow: 1 }} />
                    <Chip 
                      label={`${check.score}%`} 
                      color={getComplianceColor(check.score)} 
                    />
                  </Box>
                  
                  <LinearProgress 
                    variant="determinate" 
                    value={check.score} 
                    sx={{ mb: 2, height: 8, borderRadius: 4 }}
                    color={getComplianceColor(check.score)}
                  />
                  
                  {check.issues?.length > 0 ? (
                    <Box>
                      <Typography variant="subtitle2" color="warning.main" gutterBottom>
                        Issues to Address:
                      </Typography>
                      {check.issues.map((issue, issueIndex) => (
                        <Typography key={issueIndex} variant="body2" color="text.secondary">
                          • {issue}
                        </Typography>
                      ))}
                    </Box>
                  ) : (
                    <Typography variant="body2" color="success.main">
                      ✓ All requirements met
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Calendar Tab */}
      <TabPanel value={activeTab} index={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Compliance Calendar
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Due Date</TableCell>
                    <TableCell>Task</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {complianceCalendar.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>{item.date}</TableCell>
                      <TableCell>{item.task}</TableCell>
                      <TableCell>
                        <Chip 
                          label={item.status} 
                          color={item.status === 'pending' ? 'warning' : 'info'} 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={item.priority} 
                          color={item.priority === 'high' ? 'error' : 'warning'} 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined">
                          View Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </TabPanel>

      {/* GST Calculator Tab */}
      <TabPanel value={activeTab} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  GST Calculator
                </Typography>
                
                <TextField
                  fullWidth
                  label="Amount"
                  type="number"
                  value={gstCalculator.amount}
                  onChange={(e) => setGstCalculator({ ...gstCalculator, amount: e.target.value })}
                  margin="normal"
                />
                
                <TextField
                  fullWidth
                  select
                  label="Product Category"
                  value={gstCalculator.product_category}
                  onChange={(e) => setGstCalculator({ ...gstCalculator, product_category: e.target.value })}
                  margin="normal"
                >
                  <MenuItem value="raw_rice">Raw Rice</MenuItem>
                  <MenuItem value="processed_rice">Processed Rice</MenuItem>
                  <MenuItem value="premium_rice">Premium Rice</MenuItem>
                  <MenuItem value="broken_rice">Broken Rice</MenuItem>
                  <MenuItem value="rice_bran">Rice Bran</MenuItem>
                  <MenuItem value="paddy">Paddy</MenuItem>
                </TextField>
                
                <TextField
                  fullWidth
                  select
                  label="Transaction Type"
                  value={gstCalculator.transaction_type}
                  onChange={(e) => setGstCalculator({ ...gstCalculator, transaction_type: e.target.value })}
                  margin="normal"
                >
                  <MenuItem value="sale">Sale</MenuItem>
                  <MenuItem value="purchase">Purchase</MenuItem>
                </TextField>
                
                <Button
                  variant="contained"
                  onClick={calculateGST}
                  startIcon={<Calculate />}
                  sx={{ mt: 2 }}
                  fullWidth
                >
                  Calculate GST
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {gstResult && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    GST Calculation Result
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Base Amount
                    </Typography>
                    <Typography variant="h6">
                      ₹{gstResult.base_amount?.toLocaleString()}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      GST Rate
                    </Typography>
                    <Typography variant="h6">
                      {gstResult.gst_rate}%
                    </Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      CGST
                    </Typography>
                    <Typography variant="body1">
                      ₹{gstResult.cgst?.toLocaleString()}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      SGST
                    </Typography>
                    <Typography variant="body1">
                      ₹{gstResult.sgst?.toLocaleString()}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Total GST
                    </Typography>
                    <Typography variant="h6" color="primary.main">
                      ₹{gstResult.gst_amount?.toLocaleString()}
                    </Typography>
                  </Box>
                  
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Total Amount
                    </Typography>
                    <Typography variant="h5" color="success.main">
                      ₹{gstResult.total_amount?.toLocaleString()}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* GST Invoice Dialog */}
      <Dialog open={showInvoiceDialog} onClose={() => setShowInvoiceDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Generate GST Invoice</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Customer ID"
            value={invoiceForm.customer_id}
            onChange={(e) => setInvoiceForm({ ...invoiceForm, customer_id: e.target.value })}
            margin="normal"
            type="number"
          />
          
          <TextField
            fullWidth
            label="Invoice Date"
            type="date"
            value={invoiceForm.invoice_date}
            onChange={(e) => setInvoiceForm({ ...invoiceForm, invoice_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          
          <TextField
            fullWidth
            label="Due Date"
            type="date"
            value={invoiceForm.due_date}
            onChange={(e) => setInvoiceForm({ ...invoiceForm, due_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            Invoice Items
          </Typography>
          
          {invoiceForm.items.map((item, index) => (
            <Box key={index} sx={{ border: '1px solid #ddd', p: 2, mb: 2, borderRadius: 1 }}>
              <TextField
                fullWidth
                label="Description"
                value={item.description}
                onChange={(e) => updateInvoiceItem(index, 'description', e.target.value)}
                margin="normal"
              />
              
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Quantity"
                    type="number"
                    value={item.quantity}
                    onChange={(e) => updateInvoiceItem(index, 'quantity', parseFloat(e.target.value))}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Unit Price"
                    type="number"
                    value={item.unit_price}
                    onChange={(e) => updateInvoiceItem(index, 'unit_price', parseFloat(e.target.value))}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    select
                    label="Category"
                    value={item.product_category}
                    onChange={(e) => updateInvoiceItem(index, 'product_category', e.target.value)}
                    margin="normal"
                  >
                    <MenuItem value="processed_rice">Processed Rice</MenuItem>
                    <MenuItem value="premium_rice">Premium Rice</MenuItem>
                    <MenuItem value="broken_rice">Broken Rice</MenuItem>
                  </TextField>
                </Grid>
              </Grid>
            </Box>
          ))}
          
          <Button onClick={addInvoiceItem} variant="outlined" sx={{ mt: 1 }}>
            Add Item
          </Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowInvoiceDialog(false)}>Cancel</Button>
          <Button onClick={generateGSTInvoice} variant="contained">
            Generate Invoice
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ComplianceGST;
