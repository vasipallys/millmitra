import React, { useEffect, useState } from 'react';
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
} from '@mui/material';
import {
  Receipt,
  Assessment,
  CheckCircle,
  Warning,
  Error,
  Description,
  Schedule,
  Security,
  GetApp,
  Calculate,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import DemoBanner from '../components/DemoBanner';
import { useI18n } from '../i18n/I18nContext';
import LookupSelect from '../components/common/LookupSelect';
import PreviewModeToggle from '../components/PreviewModeToggle';
import { usePreviewMode } from '../hooks/usePreviewMode';
import { financeService } from '../services/financeService';
import api from '../services/api';
import { farmerService } from '../services/farmerService';
import { getApiErrorMessage } from '../utils/apiError';
import {
  actualComplianceStatus,
  gstActivitiesFromInvoices,
  gstDashboardFromInvoices,
  procurementsToGstr2bRows,
  statutoryGstCalendar,
  unwrapList,
} from '../utils/previewLiveData';
import {
  CALENDAR_TASKS,
  GST_CATEGORIES,
  buildInvoiceText,
  computeGst,
  downloadText,
  formatInr,
  invoicesToGstr1Rows,
  sampleGstr1Rows,
  sampleGstr2bRows,
  sampleGstr3bSummary,
  toCsv,
} from '../utils/gstPreview';

const mockComplianceData = {
  overall_status: 'good',
  compliance_score: 87.5,
  checks: [
    { category: 'GST Compliance', score: 95, status: 'compliant', issues: [] },
    { category: 'FSSAI Compliance', score: 85, status: 'compliant', issues: ['License expiring in 45 days'] },
    { category: 'Pollution Control', score: 90, status: 'compliant', issues: [] },
    { category: 'Labor Compliance', score: 80, status: 'compliant', issues: ['PF registration pending for 2 employees'] },
  ],
  alerts: [
    {
      type: 'warning',
      category: 'license_renewal',
      title: 'FSSAI License Renewal',
      message: 'FSSAI license expires in 45 days',
      nextStep: 'This is a preview reminder. Renew on the FSSAI portal; MillMitra does not file licences.',
    },
  ],
};

const mockGSTData = {
  monthly_summary: {
    total_sales: 1250000,
    total_gst_collected: 62500,
    gstr1_filed: true,
    gstr3b_filed: true,
    due_dates: { gstr1: '11-02-2024', gstr3b: '20-02-2024' },
  },
  tax_breakdown: [
    { name: '5% GST', value: 62500, color: '#4CAF50' },
    { name: '12% GST', value: 0, color: '#FF9800' },
    { name: '18% GST', value: 0, color: '#F44336' },
    { name: '28% GST', value: 0, color: '#9C27B0' },
  ],
};

const complianceCalendar = [
  { date: '11-02-2024', task: 'GSTR-1 Filing', status: 'pending', priority: 'high' },
  { date: '20-02-2024', task: 'GSTR-3B Filing', status: 'pending', priority: 'high' },
  { date: '31-03-2024', task: 'Annual Return', status: 'upcoming', priority: 'medium' },
  { date: '15-04-2024', task: 'TDS Return Q4', status: 'upcoming', priority: 'medium' },
];

const gstActivities = [
  { date: '15-01-2024', activity: 'GSTR-1 Filed', status: 'Completed', amount: 62500, form: 'GSTR-1' },
  { date: '20-01-2024', activity: 'GSTR-3B Filed', status: 'Completed', amount: 58000, form: 'GSTR-3B' },
];

const emptyInvoiceForm = {
  customer_id: '',
  items: [{ description: '', quantity: 1, unit_price: 0, product_category: 'processed_rice' }],
  invoice_date: new Date().toISOString().split('T')[0],
  due_date: '',
  payment_terms: 'Net 30',
};

const TabPanel = ({ children, value, index }) => (
  <div hidden={value !== index} role="tabpanel">
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const ComplianceGST = () => {
  const { t } = useI18n();
  const { mode, setMode, isSample } = usePreviewMode('compliance-gst');
  const [activeTab, setActiveTab] = useState(0);
  const [invoiceRows, setInvoiceRows] = useState([]);
  const [activityRows, setActivityRows] = useState([]);
  const [calendarRows, setCalendarRows] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [complianceStatus, setComplianceStatus] = useState(null);
  const [gstCalculator, setGstCalculator] = useState({
    amount: '',
    product_category: 'processed_rice',
    transaction_type: 'sale',
    supply: 'intra',
  });
  const [amountError, setAmountError] = useState('');
  const [gstResult, setGstResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pageMessage, setPageMessage] = useState(null);
  const [showInvoiceDialog, setShowInvoiceDialog] = useState(false);
  const [invoiceForm, setInvoiceForm] = useState(emptyInvoiceForm);
  const [invoiceError, setInvoiceError] = useState('');
  const [calendarItem, setCalendarItem] = useState(null);
  const [alertItem, setAlertItem] = useState(null);
  const [statusItem, setStatusItem] = useState(null);
  const [busyAction, setBusyAction] = useState('');

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      if (isSample) {
        setDashboardData(mockGSTData);
        setComplianceStatus(mockComplianceData);
        setActivityRows(gstActivities);
        setCalendarRows(complianceCalendar);
        setInvoiceRows(sampleGstr1Rows());
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const [data, filingsRes] = await Promise.all([
          financeService.getInvoices({ limit: 50 }),
          api.get('/compliance/gst/filings').catch(() => ({ data: { filings: [] } })),
        ]);
        if (cancelled) return;
        const invoices = unwrapList(data, ['invoices', 'items']);
        const filings = filingsRes?.data?.filings || [];
        setInvoiceRows(invoicesToGstr1Rows(invoices));
        setDashboardData(gstDashboardFromInvoices(invoices));
        setComplianceStatus(actualComplianceStatus(invoices));
        setActivityRows([
          ...filings.map((row) => ({
            date: row.date || (row.recorded_at || '').slice(0, 10),
            activity: row.activity || `${row.form} recorded in MillMitra`,
            status: 'Recorded locally',
            amount: row.amount,
            form: row.form,
          })),
          ...gstActivitiesFromInvoices(invoices),
        ]);
        const recordedForms = new Set(filings.map((row) => row.form));
        setCalendarRows(statutoryGstCalendar().map((item) => (
          recordedForms.has(item.task) || recordedForms.has(CALENDAR_TASKS[item.task]?.form)
            ? { ...item, status: 'recorded' }
            : item
        )));
      } catch (error) {
        if (!cancelled) {
          setInvoiceRows([]);
          setDashboardData(gstDashboardFromInvoices([]));
          setComplianceStatus(actualComplianceStatus([]));
          setActivityRows([]);
          setCalendarRows(statutoryGstCalendar());
          setPageMessage({ severity: 'warning', text: getApiErrorMessage(error, t('couldNotLoadInvoices')) });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [isSample]);

  const showMessage = (severity, text) => {
    setPageMessage({ severity, text });
  };

  const calculateGST = () => {
    const amount = Number(gstCalculator.amount);
    if (!gstCalculator.amount || !Number.isFinite(amount) || amount <= 0) {
      setAmountError('Amount is required and must be greater than 0');
      setGstResult(null);
      return;
    }
    setAmountError('');
    const result = computeGst(gstCalculator);
    if (!result.success) {
      setAmountError(result.message);
      setGstResult(null);
      return;
    }
    setGstResult(result);
    showMessage('success', t('gstCalcToast', {
      rate: result.gst_rate,
      supply: result.igst > 0 ? t('interState') : t('intraState'),
    }));
  };

  const loadInvoiceRows = async () => {
    if (isSample) {
      return { rows: sampleGstr1Rows(), source: 'sample rows on this preview page' };
    }
    if (invoiceRows.length) {
      return { rows: invoiceRows, source: 'live invoices from Finance' };
    }
    try {
      const data = await financeService.getInvoices({ limit: 50 });
      const invoices = data?.invoices || data?.items || [];
      const rows = invoicesToGstr1Rows(invoices);
      return { rows, source: rows.length ? 'live invoices from Finance' : 'no invoices yet' };
    } catch (error) {
      return {
        rows: [],
        source: getApiErrorMessage(error, 'Finance invoices unavailable'),
      };
    }
  };

  const generateReturn = async (kind) => {
    setBusyAction(kind);
    try {
      const stamp = new Date().toISOString().slice(0, 10);
      if (kind === 'GSTR-2B') {
        if (isSample) {
          const rows = sampleGstr2bRows();
          downloadText(`gstr-2b-preview-${stamp}.csv`, toCsv(rows), 'text/csv;charset=utf-8');
          showMessage('success', t('gstr2bSampleDl'));
          return;
        }
        try {
          const data = await farmerService.getProcurements({ limit: 50 });
          const rows = procurementsToGstr2bRows(unwrapList(data, ['procurements', 'items']));
          if (!rows.length) {
            downloadText(`gstr-2b-preview-${stamp}.csv`, 'sr,invoice_number,invoice_date,supplier,taxable_value,gst_amount,total,status\n', 'text/csv;charset=utf-8');
            showMessage('info', t('gstr2bEmptyDl'));
            return;
          }
          downloadText(`gstr-2b-preview-${stamp}.csv`, toCsv(rows), 'text/csv;charset=utf-8');
          showMessage('success', t('gstr2bLiveDl'));
        } catch (error) {
          showMessage('error', getApiErrorMessage(error, t('couldNotLoadProcurements')));
        }
        return;
      }
      const { rows, source } = await loadInvoiceRows();
      if (kind === 'GSTR-3B') {
        downloadText(`gstr-3b-preview-${stamp}.csv`, toCsv(sampleGstr3bSummary(rows)), 'text/csv;charset=utf-8');
        showMessage('success', t('gstr3bDl', { source }));
        return;
      }
      downloadText(`gstr-1-preview-${stamp}.csv`, toCsv(rows), 'text/csv;charset=utf-8');
      showMessage('success', t('gstr1Dl', { source }));
    } catch (error) {
      showMessage('error', getApiErrorMessage(error, t('couldNotGeneratePreview')));
    } finally {
      setBusyAction('');
    }
  };

  const downloadActivity = (row) => {
    const payload = {
      form: row.form,
      activity: row.activity,
      date: row.date,
      status: row.status,
      amount: row.amount,
      note: 'Preview activity row from Compliance & GST. Not a filed return.',
    };
    downloadText(
      `${row.form.toLowerCase()}-${row.date.replace(/-/g, '')}.json`,
      JSON.stringify(payload, null, 2),
      'application/json;charset=utf-8'
    );
    showMessage('success', t('downloadedActivity', { activity: row.activity }));
  };

  const generateGSTInvoice = () => {
    if (!invoiceForm.customer_id) {
      setInvoiceError('Customer ID is required');
      return;
    }
    const lines = invoiceForm.items.map((item) => {
      const taxable = Number(item.quantity || 0) * Number(item.unit_price || 0);
      const gst = computeGst({
        amount: taxable,
        product_category: item.product_category,
        transaction_type: 'sale',
        supply: 'intra',
      });
      return {
        ...item,
        taxable: gst.success ? gst.base_amount : 0,
        gst_rate: gst.success ? gst.gst_rate : 0,
        gst_amount: gst.success ? gst.gst_amount : 0,
        total: gst.success ? gst.total_amount : 0,
        category_label: gst.category_label,
      };
    });
    const valid = lines.some((line) => line.taxable > 0 && (line.description || line.category_label));
    if (!valid) {
      setInvoiceError('Add at least one line with description, quantity, and unit price greater than 0');
      return;
    }
    setInvoiceError('');
    const stamp = invoiceForm.invoice_date || new Date().toISOString().slice(0, 10);
    downloadText(`gst-invoice-preview-${stamp}.txt`, buildInvoiceText(invoiceForm, lines));
    setShowInvoiceDialog(false);
    setInvoiceForm(emptyInvoiceForm);
    showMessage('success', t('gstInvoiceDl'));
  };

  const addInvoiceItem = () => {
    setInvoiceForm({
      ...invoiceForm,
      items: [...invoiceForm.items, { description: '', quantity: 1, unit_price: 0, product_category: 'processed_rice' }],
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
      <DemoBanner title={t('complianceGst')} mode={mode} />
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Compliance & GST Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            GST totals from Finance invoices at preview rates. MillMitra does not file GST.
          </Typography>
        </Box>
        <PreviewModeToggle mode={mode} onChange={setMode} />
      </Box>

      {pageMessage && (
        <Alert severity={pageMessage.severity} sx={{ mb: 2 }} onClose={() => setPageMessage(null)} role="status">
          {pageMessage.text}
        </Alert>
      )}

      {complianceStatus?.alerts?.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {complianceStatus.alerts.map((item, index) => (
            <Alert
              key={index}
              severity={item.type}
              sx={{ mb: 1 }}
              action={
                <Button color="inherit" size="small" onClick={() => setAlertItem(item)}>
                  Action Required
                </Button>
              }
            >
              <strong>{item.title}:</strong> {item.message}
            </Alert>
          ))}
        </Box>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
        >
          <Tab icon={<Assessment />} label={t('dashboard')} />
          <Tab icon={<Receipt />} label={t('gstManagement')} />
          <Tab icon={<Security />} label={t('complianceStatus')} />
          <Tab icon={<Schedule />} label={t('calendar')} />
          <Tab icon={<Calculate />} label={t('gstCalculator')} />
        </Tabs>
      </Paper>

      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" color="primary.main">
                    {complianceStatus?.compliance_score != null
                      ? complianceStatus.compliance_score
                      : (dashboardData?.monthly_summary?.invoice_count ?? 0)}
                  </Typography>
                  <Typography variant="h6" color="text.secondary">
                    {complianceStatus?.compliance_score != null ? 'Compliance Score' : 'Invoices in preview'}
                  </Typography>
                  <Chip
                    label={(complianceStatus?.overall_status || 'preview').toUpperCase()}
                    color={complianceStatus?.compliance_score != null ? getComplianceColor(complianceStatus.compliance_score) : 'info'}
                    sx={{ mt: 1 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Monthly GST Summary</Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Total Sales</Typography>
                  <Typography variant="h5">
                    ₹{dashboardData?.monthly_summary?.total_sales?.toLocaleString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">GST Collected</Typography>
                  <Typography variant="h5" color="success.main">
                    ₹{dashboardData?.monthly_summary?.total_gst_collected?.toLocaleString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Filing Status</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {getStatusIcon(isSample && dashboardData?.monthly_summary?.gstr1_filed ? 'compliant' : 'pending')}
                  <Typography variant="body1" sx={{ ml: 1 }}>
                    GSTR-1: {isSample && dashboardData?.monthly_summary?.gstr1_filed ? 'Sample: Filed' : 'Not filed in MillMitra'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {getStatusIcon(isSample && dashboardData?.monthly_summary?.gstr3b_filed ? 'compliant' : 'pending')}
                  <Typography variant="body1" sx={{ ml: 1 }}>
                    GSTR-3B: {isSample && dashboardData?.monthly_summary?.gstr3b_filed ? 'Sample: Filed' : 'Not filed in MillMitra'}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Compliance Areas</Typography>
                {complianceStatus?.checks?.map((check, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, gap: 1, flexWrap: 'wrap' }}>
                      <Typography variant="body1" fontWeight="medium">{check.category}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {check.score != null && <Typography variant="body1" fontWeight="bold">{check.score}%</Typography>}
                        <Button size="small" onClick={() => setStatusItem(check)}>View details</Button>
                      </Box>
                    </Box>
                    {check.score != null && (
                    <LinearProgress
                      variant="determinate"
                      value={check.score}
                      sx={{ height: 8, borderRadius: 4 }}
                      color={getComplianceColor(check.score)}
                    />
                    )}
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

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Tax Breakdown</Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={dashboardData?.tax_breakdown}
                      cx="50%"
                      cy="50%"
                      outerRadius={60}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => (value > 0 ? `${name}: ₹${value.toLocaleString()}` : '')}
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

      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>GST Returns</Typography>
                <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  <Button
                    variant="contained"
                    startIcon={<Description />}
                    onClick={() => generateReturn('GSTR-1')}
                    disabled={Boolean(busyAction)}
                  >
                    {busyAction === 'GSTR-1' ? t('preparing') : t('generateGstr1')}
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<Description />}
                    onClick={() => generateReturn('GSTR-2B')}
                    disabled={Boolean(busyAction)}
                  >
                    {busyAction === 'GSTR-2B' ? t('preparing') : t('generateGstr2b')}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Description />}
                    onClick={() => generateReturn('GSTR-3B')}
                    disabled={Boolean(busyAction)}
                  >
                    {busyAction === 'GSTR-3B' ? t('preparing') : t('generateGstr3b')}
                  </Button>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Downloads a CSV preview. View actual uses Finance invoices (and procurements for GSTR-2B). View sample uses demonstration rows.
                </Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>
                  GSTR-1 due: {dashboardData?.monthly_summary?.due_dates?.gstr1}
                </Typography>
                <Typography variant="body2">
                  GSTR-3B due: {dashboardData?.monthly_summary?.due_dates?.gstr3b}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Invoice Management</Typography>
                <Button
                  variant="contained"
                  startIcon={<Receipt />}
                  onClick={() => {
                    setInvoiceError('');
                    setShowInvoiceDialog(true);
                  }}
                  sx={{ mb: 2 }}
                >
                  {t('generateGstInvoice')}
                </Button>
                <Typography variant="body2" color="text.secondary">
                  Opens a form and downloads a preview invoice. Does not file GST or post to Finance.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>Recent GST Activities</Typography>
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
                      {!activityRows.length && (
                        <TableRow>
                          <TableCell colSpan={5}>
                            <Typography variant="body2" color="text.secondary">No invoice GST activity yet.</Typography>
                          </TableCell>
                        </TableRow>
                      )}
                      {activityRows.map((row, index) => (
                        <TableRow key={`${row.form}-${row.activity}-${index}`}>
                          <TableCell>{row.date}</TableCell>
                          <TableCell>{row.activity}</TableCell>
                          <TableCell>
                            <Chip label={row.status} color="success" size="small" />
                          </TableCell>
                          <TableCell>{formatInr(row.amount)}</TableCell>
                          <TableCell>
                            <Button size="small" startIcon={<GetApp />} onClick={() => downloadActivity(row)}>
                              Download
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          {complianceStatus?.checks?.map((check, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {getStatusIcon(check.status)}
                    <Typography variant="h6" sx={{ ml: 1 }}>{check.category}</Typography>
                    <Box sx={{ flexGrow: 1 }} />
                    {check.score != null && (
                      <Chip label={`${check.score}%`} color={getComplianceColor(check.score)} />
                    )}
                  </Box>
                  {check.score != null && (
                  <LinearProgress
                    variant="determinate"
                    value={check.score}
                    sx={{ mb: 2, height: 8, borderRadius: 4 }}
                    color={getComplianceColor(check.score)}
                  />
                  )}
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
                      All listed preview checks are clear
                    </Typography>
                  )}
                  <Button size="small" sx={{ mt: 1 }} onClick={() => setStatusItem(check)}>
                    View details
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Compliance Calendar</Typography>
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
                  {calendarRows.map((item) => (
                    <TableRow key={item.task}>
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
                        <Button size="small" variant="outlined" onClick={() => setCalendarItem(item)}>
                          {t('viewDetails')}
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

      <TabPanel value={activeTab} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>{t('gstCalculator')}</Typography>
                <TextField
                  fullWidth
                  label={t('gstAmount')}
                  type="number"
                  value={gstCalculator.amount}
                  onChange={(e) => {
                    setGstCalculator({ ...gstCalculator, amount: e.target.value });
                    if (amountError) setAmountError('');
                  }}
                  margin="normal"
                  required
                  error={Boolean(amountError)}
                  helperText={amountError || t('gstAmountHelp')}
                  inputProps={{ min: 0, step: 'any' }}
                />
                <LookupSelect
                  group="gst_product_category"
                  label={t('productCategory')}
                  value={gstCalculator.product_category}
                  onChange={(e) => setGstCalculator({ ...gstCalculator, product_category: e.target.value })}
                  sx={{ mt: 2 }}
                />
                <LookupSelect
                  group="gst_transaction_type"
                  label={t('transactionType')}
                  value={gstCalculator.transaction_type}
                  onChange={(e) => setGstCalculator({ ...gstCalculator, transaction_type: e.target.value })}
                  sx={{ mt: 2 }}
                />
                <LookupSelect
                  group="gst_supply"
                  label={t('supply')}
                  value={gstCalculator.supply}
                  onChange={(e) => setGstCalculator({ ...gstCalculator, supply: e.target.value })}
                  helperText={t('supplyHelp')}
                  sx={{ mt: 2 }}
                />
                <Button
                  variant="contained"
                  onClick={calculateGST}
                  startIcon={<Calculate />}
                  sx={{ mt: 2 }}
                  fullWidth
                >
                  {t('calculateGst')}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            {gstResult ? (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>{t('gstCalcResult')}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {gstResult.category_label} · HSN {gstResult.hsn} · {gstResult.igst > 0 ? t('interState') : t('intraState')}
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">{t('taxableValue')}</Typography>
                    <Typography variant="h6">{formatInr(gstResult.base_amount)}</Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">{t('gstRate')}</Typography>
                    <Typography variant="h6">{gstResult.gst_rate}%</Typography>
                  </Box>
                  {gstResult.igst > 0 ? (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">{t('igst')}</Typography>
                      <Typography variant="body1">{formatInr(gstResult.igst)}</Typography>
                    </Box>
                  ) : (
                    <>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">{t('cgst')}</Typography>
                        <Typography variant="body1">{formatInr(gstResult.cgst)}</Typography>
                      </Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">{t('sgst')}</Typography>
                        <Typography variant="body1">{formatInr(gstResult.sgst)}</Typography>
                      </Box>
                    </>
                  )}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">{t('totalGst')}</Typography>
                    <Typography variant="h6" color="primary.main">{formatInr(gstResult.gst_amount)}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">{t('totalAmount')}</Typography>
                    <Typography variant="h5" color="success.main">{formatInr(gstResult.total_amount)}</Typography>
                  </Box>
                </CardContent>
              </Card>
            ) : (
              <Alert severity="info">{t('gstCalcHelp')}</Alert>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      <Dialog
        open={Boolean(calendarItem)}
        onClose={() => setCalendarItem(null)}
        maxWidth="sm"
        fullWidth
        aria-labelledby="calendar-detail-title"
      >
        <DialogTitle id="calendar-detail-title">{calendarItem?.task}</DialogTitle>
        <DialogContent>
          {calendarItem && (
            <Box sx={{ pt: 1 }}>
              <Typography variant="body2" color="text.secondary">Due date</Typography>
              <Typography sx={{ mb: 1 }}>{calendarItem.date}</Typography>
              <Typography variant="body2" color="text.secondary">Status</Typography>
              <Typography sx={{ mb: 1 }}>{calendarItem.status}</Typography>
              <Typography variant="body2" color="text.secondary">Priority</Typography>
              <Typography sx={{ mb: 1 }}>{calendarItem.priority}</Typography>
              <Typography variant="body2" color="text.secondary">Form</Typography>
              <Typography sx={{ mb: 1 }}>{CALENDAR_TASKS[calendarItem.task]?.form || calendarItem.task}</Typography>
              <Typography variant="body2" color="text.secondary">What this filing is</Typography>
              <Typography sx={{ mb: 1 }}>
                {CALENDAR_TASKS[calendarItem.task]?.meaning || 'A scheduled compliance task on this preview calendar.'}
              </Typography>
              <Typography variant="body2" color="text.secondary">Typical due rule</Typography>
              <Typography>
                {CALENDAR_TASKS[calendarItem.task]?.typicalDue || 'Confirm the due date on the GST portal.'}
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                {isSample
                  ? 'Dates on this calendar are sample. MillMitra does not file this return.'
                  : 'Typical statutory due dates for a checklist only. MillMitra does not file this return.'}
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          {!isSample && (
            <Button
              disabled={busyAction === 'record-filing'}
              onClick={async () => {
                setBusyAction('record-filing');
                try {
                  await api.post('/compliance/gst/filings', {
                    form: calendarItem.task,
                    due_date: calendarItem.date,
                    notes: 'Recorded in MillMitra. Not a GSTN filing receipt.',
                  });
                  setCalendarRows((prev) => prev.map((row) => (
                    row.task === calendarItem.task ? { ...row, status: 'recorded' } : row
                  )));
                  setActivityRows((prev) => [{
                    date: new Date().toISOString().slice(0, 10),
                    activity: `${calendarItem.task} recorded in MillMitra`,
                    status: 'Recorded locally',
                    amount: 0,
                    form: calendarItem.task,
                  }, ...prev]);
                  showMessage('success', t('gstSavedChecklist'));
                  setCalendarItem(null);
                } catch (error) {
                  showMessage('error', getApiErrorMessage(error, t('couldNotSaveChecklist')));
                } finally {
                  setBusyAction('');
                }
              }}
            >
              Record in MillMitra
            </Button>
          )}
          <Button onClick={() => setCalendarItem(null)}>{t('close')}</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(alertItem)}
        onClose={() => setAlertItem(null)}
        maxWidth="sm"
        fullWidth
        aria-labelledby="alert-detail-title"
      >
        <DialogTitle id="alert-detail-title">{alertItem?.title}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 1 }}>{alertItem?.message}</Typography>
          <Typography sx={{ mt: 2 }}>{alertItem?.nextStep}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAlertItem(null)}>{t('close')}</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={Boolean(statusItem)}
        onClose={() => setStatusItem(null)}
        maxWidth="sm"
        fullWidth
        aria-labelledby="status-detail-title"
      >
        <DialogTitle id="status-detail-title">{statusItem?.category}</DialogTitle>
        <DialogContent>
          {statusItem && (
            <Box sx={{ pt: 1 }}>
              {statusItem.score != null && <Typography>Score: {statusItem.score}%</Typography>}
              <Typography>Status: {statusItem.status}</Typography>
              <Typography sx={{ mt: 1 }}>
                {statusItem.issues?.length
                  ? `Issues: ${statusItem.issues.join(', ')}`
                  : 'No issues listed on this preview check.'}
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                {isSample ? t('gstSampleStatus') : t('gstLiveStatus')}
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStatusItem(null)}>{t('close')}</Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={showInvoiceDialog}
        onClose={() => setShowInvoiceDialog(false)}
        maxWidth="md"
        fullWidth
        aria-labelledby="gst-invoice-title"
      >
        <DialogTitle id="gst-invoice-title">{t('generateGstInvoice')}</DialogTitle>
        <DialogContent>
          {invoiceError && <Alert severity="error" sx={{ mt: 1 }} role="alert">{invoiceError}</Alert>}
          <TextField
            fullWidth
            label={t('customerId')}
            value={invoiceForm.customer_id}
            onChange={(e) => setInvoiceForm({ ...invoiceForm, customer_id: e.target.value })}
            margin="normal"
            required
            helperText={t('customerIdPreviewHelp')}
          />
          <TextField
            fullWidth
            label={t('invoiceDate')}
            type="date"
            value={invoiceForm.invoice_date}
            onChange={(e) => setInvoiceForm({ ...invoiceForm, invoice_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            fullWidth
            label={t('dueDate')}
            type="date"
            value={invoiceForm.due_date}
            onChange={(e) => setInvoiceForm({ ...invoiceForm, due_date: e.target.value })}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>{t('invoiceItems')}</Typography>
          {invoiceForm.items.map((item, index) => (
            <Box key={index} sx={{ border: '1px solid #ddd', p: 2, mb: 2, borderRadius: 1 }}>
              <TextField
                fullWidth
                label={t('lineDescription')}
                value={item.description}
                onChange={(e) => updateInvoiceItem(index, 'description', e.target.value)}
                margin="normal"
                helperText={t('gstInvoiceHelp')}
              />
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label={t('quantity')}
                    type="number"
                    value={item.quantity}
                    onChange={(e) => updateInvoiceItem(index, 'quantity', parseFloat(e.target.value) || 0)}
                    margin="normal"
                    inputProps={{ min: 0, step: 'any' }}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label={t('unitPrice')}
                    type="number"
                    value={item.unit_price}
                    onChange={(e) => updateInvoiceItem(index, 'unit_price', parseFloat(e.target.value) || 0)}
                    margin="normal"
                    inputProps={{ min: 0, step: 'any' }}
                  />
                </Grid>
                <Grid item xs={4}>
                  <LookupSelect
                    group="gst_product_category"
                    label={t('category')}
                    value={item.product_category}
                    onChange={(e) => updateInvoiceItem(index, 'product_category', e.target.value)}
                    sx={{ mt: 2 }}
                  />
                </Grid>
              </Grid>
            </Box>
          ))}
          <Button onClick={addInvoiceItem} variant="outlined" sx={{ mt: 1 }}>{t('addItem')}</Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowInvoiceDialog(false)}>{t('cancel')}</Button>
          <Button onClick={generateGSTInvoice} variant="contained">{t('generateInvoice')}</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ComplianceGST;
