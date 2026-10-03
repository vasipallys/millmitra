import { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Select, MenuItem, FormControl, InputLabel, Alert, LinearProgress,
  Tabs, Tab, IconButton, Tooltip, Paper, Avatar, Divider
} from '@mui/material';
import {
  Add, Person, Business, Phone, Email, TrendingUp,
  Assignment, Chat, ShoppingCart, Analytics, Search,
  FilterList, Refresh, Star, Warning
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { customerService } from '../services/customerService';
import { useI18n } from '../i18n/I18nContext';
import CustomerCard from '../components/CustomerCard';
import CustomerDetails from '../components/CustomerDetails';
import OrderHistory from '../components/OrderHistory';
import CustomerAnalytics from '../components/CustomerAnalytics';
import InteractionDialog from '../components/InteractionDialog';
import { getApiErrorMessage } from '../utils/apiError';
import { PageHeader, PageShell, QueryErrorAlert } from '../components/common/PageChrome';

const Customers = () => {
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState(0);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [addCustomerOpen, setAddCustomerOpen] = useState(false);
  const [interactionOpen, setInteractionOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [segmentFilter, setSegmentFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const queryClient = useQueryClient();

  // Fetch customers data
  const { data: customersData, isLoading: customersLoading, isError: customersError, error: customersErr, refetch: refetchCustomers } = useQuery(
    ['customers', searchTerm, segmentFilter, statusFilter],
    () => customerService.getCustomers({ search: searchTerm, segment: segmentFilter, status: statusFilter }),
    { refetchInterval: 60000 }
  );

  const { data: analytics } = useQuery(
    'customer-analytics',
    () => customerService.getCustomerAnalytics(),
    { refetchInterval: 300000 }
  );

  const { data: segments } = useQuery(
    'customer-segments',
    () => customerService.getCustomerSegments(),
    { refetchInterval: 300000 }
  );

  // Mutations
  const [actionError, setActionError] = useState('');

  const createCustomerMutation = useMutation(customerService.createCustomer, {
    onSuccess: () => {
      queryClient.invalidateQueries('customers');
      setAddCustomerOpen(false);
      setActionError('');
    },
    onError: (error) => setActionError(getApiErrorMessage(error, 'Could not add customer'))
  });

  const createInteractionMutation = useMutation(customerService.createInteraction, {
    onSuccess: () => {
      queryClient.invalidateQueries(['customer-details', selectedCustomer?.id]);
      setInteractionOpen(false);
      setActionError('');
    },
    onError: (error) => setActionError(getApiErrorMessage(error, 'Could not save interaction')),
  });

  const handleCreateCustomer = (customerData) => {
    setActionError('');
    createCustomerMutation.mutate(customerData);
  };

  const handleCreateInteraction = (interactionData) => {
    createInteractionMutation.mutate({
      customerId: selectedCustomer.id,
      ...interactionData
    });
  };

  const getSegmentColor = (segment) => {
    const colors = {
      premium: 'success',
      regular: 'primary',
      budget: 'warning',
      inactive: 'default'
    };
    return colors[segment] || 'default';
  };

  const getChurnRiskColor = (score) => {
    if (score >= 0.7) return 'error';
    if (score >= 0.4) return 'warning';
    return 'success';
  };

  return (
    <PageShell>
      <PageHeader
        title={t('customersTitle')}
        subtitle={t('customersSubtitle')}
        actions={
          <>
            <Button variant="outlined" startIcon={<Analytics />} onClick={() => setActiveTab(3)}>
              Analytics
            </Button>
            <Button variant="contained" startIcon={<Add />} onClick={() => setAddCustomerOpen(true)}>
              {t('addCustomer')}
            </Button>
          </>
        }
      />
      {customersError && <QueryErrorAlert error={customersErr} onRetry={refetchCustomers} entity="customers" />}
      {actionError && <QueryErrorAlert error={new Error(actionError)} entity="customer action" />}
      {customersLoading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Quick Stats */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Customers
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {customersData?.total || 0}
                  </Typography>
                </Box>
                <Person color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Customers
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {customersData?.customers?.filter(c => c.status === 'active').length || 0}
                  </Typography>
                </Box>
                <TrendingUp color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    High Value Customers
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {customersData?.customers?.filter(c => c.customer_segment === 'premium').length || 0}
                  </Typography>
                </Box>
                <Star color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    At Risk Customers
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="error.main">
                    {customersData?.customers?.filter(c => c.churn_risk_score >= 0.7).length || 0}
                  </Typography>
                </Box>
                <Warning color="error" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search customers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Segment</InputLabel>
                <Select
                  value={segmentFilter}
                  onChange={(e) => setSegmentFilter(e.target.value)}
                >
                  <MenuItem value="">All Segments</MenuItem>
                  <MenuItem value="premium">Premium</MenuItem>
                  <MenuItem value="regular">Regular</MenuItem>
                  <MenuItem value="budget">Budget</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                  <MenuItem value="blocked">Blocked</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => {
                  setSearchTerm('');
                  setSegmentFilter('');
                  setStatusFilter('');
                }}
              >
                Clear
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label={t('customerList')} />
          <Tab label={t('customerDetails')} disabled={!selectedCustomer} />
          <Tab label={t('orders')} />
          <Tab label={t('analytics')} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {customersData?.customers?.map((customer) => (
            <Grid item xs={12} md={6} lg={4} key={customer.id}>
              <CustomerCard
                customer={customer}
                onSelect={() => {
                  setSelectedCustomer(customer);
                  setActiveTab(1);
                }}
                onInteraction={() => {
                  setSelectedCustomer(customer);
                  setInteractionOpen(true);
                }}
                onViewOrders={() => {
                  setSelectedCustomer(customer);
                  setActiveTab(2);
                }}
              />
            </Grid>
          ))}
          {customersData?.customers?.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Person sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  {t('noCustomersYet')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('noCustomersHint')}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setAddCustomerOpen(true)}
                  sx={{ mt: 2 }}
                >
                  {t('addFirstCustomer')}
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {activeTab === 1 && selectedCustomer && (
        <CustomerDetails
          customerId={selectedCustomer.id}
          onInteraction={() => setInteractionOpen(true)}
        />
      )}

      {activeTab === 2 && (
        <OrderHistory
          customerId={selectedCustomer?.id}
          showAllOrders={!selectedCustomer}
        />
      )}

      {activeTab === 3 && (
        <CustomerAnalytics analytics={analytics} />
      )}

      {/* Add Customer Dialog */}
      <Dialog
        open={addCustomerOpen}
        onClose={() => setAddCustomerOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{t('addNewCustomer')}</DialogTitle>
        <DialogContent>
          {actionError && <Alert severity="error" sx={{ mt: 1 }}>{actionError}</Alert>}
          <AddCustomerForm
            onSubmit={handleCreateCustomer}
            loading={createCustomerMutation.isLoading}
            onCancel={() => setAddCustomerOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Interaction Dialog */}
      <InteractionDialog
        open={interactionOpen}
        onClose={() => setInteractionOpen(false)}
        customer={selectedCustomer}
        onSubmit={handleCreateInteraction}
        loading={createInteractionMutation.isLoading}
      />

      {/* AI Insights Panel */}
      {customersData?.ai_insights && (
        <Card sx={{ mt: 3, bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              AI Insights
            </Typography>
            <Grid container spacing={2}>
              {customersData.ai_insights.recommendations?.map((insight, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Alert severity="info" sx={{ mb: 1 }}>
                    {insight}
                  </Alert>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}
    </PageShell>
  );
};

// Add Customer Form Component
const emptyCustomerForm = () => ({
  name: '',
  company_name: '',
  customer_type: 'individual',
  phone: '',
  email: '',
  address: '',
  city: '',
  state: '',
  pincode: '',
  gst_number: '',
  credit_limit: 0,
  payment_terms: 'cash',
  preferred_products: []
});

const AddCustomerForm = ({ onSubmit, loading, onCancel }) => {
  const { t } = useI18n();
  const [formData, setFormData] = useState(emptyCustomerForm);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (field) => (e) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={t('customerName')}
            value={formData.name}
            onChange={handleChange('name')}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={t('companyName')}
            value={formData.company_name}
            onChange={handleChange('company_name')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>{t('customerType')}</InputLabel>
            <Select
              value={formData.customer_type}
              onChange={handleChange('customer_type')}
            >
              <MenuItem value="individual">{t('typeIndividual')}</MenuItem>
              <MenuItem value="business">{t('typeBusiness')}</MenuItem>
              <MenuItem value="distributor">{t('typeDistributor')}</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={t('phone')}
            value={formData.phone}
            onChange={handleChange('phone')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={t('email')}
            type="email"
            value={formData.email}
            onChange={handleChange('email')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={t('gstNumber')}
            value={formData.gst_number}
            onChange={handleChange('gst_number')}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label={t('address')}
            multiline
            rows={2}
            value={formData.address}
            onChange={handleChange('address')}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label={t('city')}
            value={formData.city}
            onChange={handleChange('city')}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label={t('state')}
            value={formData.state}
            onChange={handleChange('state')}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label={t('pincode')}
            value={formData.pincode}
            onChange={handleChange('pincode')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={t('creditLimitPlain')}
            type="number"
            value={formData.credit_limit}
            onChange={handleChange('credit_limit')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>{t('paymentTerms')}</InputLabel>
            <Select
              value={formData.payment_terms}
              onChange={handleChange('payment_terms')}
            >
              <MenuItem value="cash">{t('payCash')}</MenuItem>
              <MenuItem value="credit_7">{t('credit7')}</MenuItem>
              <MenuItem value="credit_15">{t('credit15')}</MenuItem>
              <MenuItem value="credit_30">{t('credit30')}</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button type="button" onClick={onCancel} disabled={loading}>
          {t('cancel')}
        </Button>
        <Button type="button" onClick={() => setFormData(emptyCustomerForm())} disabled={loading}>
          {t('reset')}
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={loading || !formData.name}
        >
          {loading ? t('creating') : t('createCustomer')}
        </Button>
      </Box>
    </form>
  );
};

export default Customers;
