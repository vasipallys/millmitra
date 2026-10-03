import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Dialog, TextField, InputAdornment, Tabs, Tab,
  DialogTitle, DialogContent, DialogActions, Alert, MenuItem
} from '@mui/material';
import {
  PersonAdd, Search, Visibility, Assignment, Payment,
  TrendingUp, Agriculture, AccountBalance, Refresh,
  VerifiedUser, PendingActions
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { farmerService } from '../services/farmerService';
import { useToastNotifications } from '../hooks/useToastNotifications';
import RegisterFarmerDialog from '../components/farmer/RegisterFarmerDialog';
import FarmerEditRequestsDialog from '../components/farmer/FarmerEditRequestsDialog';
import CreateContractDialog from '../components/farmer/CreateContractDialog';
import RecordProcurementDialog from '../components/farmer/RecordProcurementDialog';
import { getApiErrorMessage } from '../utils/apiError';
import { PageHeader, PageShell, QueryErrorAlert } from '../components/common/PageChrome';
import { useI18n } from '../i18n/I18nContext';
import LookupSelect from '../components/common/LookupSelect';

const Farmers = () => {
  const [tabValue, setTabValue] = useState(0);
  const [registerDialogOpen, setRegisterDialogOpen] = useState(false);
  const [contractDialogOpen, setContractDialogOpen] = useState(false);
  const [procurementDialogOpen, setProcurementDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFarmer, setSelectedFarmer] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({});
  const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
  const [contractViewDialogOpen, setContractViewDialogOpen] = useState(false);
  const [contractEditDialogOpen, setContractEditDialogOpen] = useState(false);
  const [contractStatusDialogOpen, setContractStatusDialogOpen] = useState(false);
  const [selectedContract, setSelectedContract] = useState(null);
  const [editRequestsDialogOpen, setEditRequestsDialogOpen] = useState(false);
  const [contractEditForm, setContractEditForm] = useState({
    quantity_committed: '',
    base_price: '',
    quality_bonus: '',
    advance_amount: '',
    terms_conditions: '',
    special_instructions: '',
  });
  const [contractEditError, setContractEditError] = useState('');
  const [selectedFarmerForRequests, setSelectedFarmerForRequests] = useState(null);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const toast = useToastNotifications();
  const { t } = useI18n();

  // Check if user is authenticated
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setAuthChecked(true);
  }, []);

  // Utility function to format currency
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  // Redirect to login if not authenticated
  useEffect(() => {
    if (authChecked && !isAuthenticated) {
      navigate('/login');
    }
  }, [authChecked, isAuthenticated, navigate]);

  // Queries
  const { data: farmersData, isLoading: farmersLoading, error: farmersError } = useQuery(
    ['farmers', searchTerm],
    () => farmerService.getFarmers({ search: searchTerm }),
    {
      refetchInterval: 300000,
      enabled: isAuthenticated,
      retry: false,
      onError: (error) => {
        console.error('Farmers fetch error:', error);
      }
    }
  );

  const { data: analytics, isLoading: analyticsLoading, error: analyticsError } = useQuery(
    'farmer-analytics',
    () => farmerService.getFarmerAnalytics('monthly', null),
    {
      refetchInterval: 300000,
      enabled: isAuthenticated,
      retry: false,
      onError: (error) => {
        console.error('Analytics fetch error:', error);
      }
    }
  );

  const { data: procurementsData } = useQuery(
    'recent-procurements',
    () => farmerService.getProcurements({ limit: 10, sort: 'recent' }),
    {
      refetchInterval: 300000,
      enabled: isAuthenticated,
      retry: false
    }
  );

  const { data: contractsData, isLoading: contractsLoading, error: contractsError } = useQuery(
    'all-contracts',
    () => farmerService.getContracts({ status: 'all' }),
    {
      refetchInterval: 300000,
      enabled: isAuthenticated,
      retry: false,
      onError: (error) => {
        console.error('Contracts fetch error:', error);
      }
    }
  );

  // Mutations
  const registerFarmerMutation = useMutation(farmerService.registerFarmer, {
    onSuccess: (data) => {
      queryClient.invalidateQueries('farmers');
      setRegisterDialogOpen(false);
      toast.farmer.created(data.farmer?.name || 'New Farmer');
    },
    onError: (error) => {
      toast.farmer.error('Create', error.response?.data?.message || error.message);
    }
  });

  const createContractMutation = useMutation(farmerService.createContract, {
    onSuccess: (data) => {
      queryClient.invalidateQueries(['farmers', 'farmer-analytics']);
      setContractDialogOpen(false);
      toast.showSuccess(`Contract ${data.contract?.contract_number || 'created'} successfully`, {
        module: 'farmer',
        action: 'Create Contract'
      });
    },
    onError: (error) => {
      toast.showError(`Failed to create contract: ${error.response?.data?.message || error.message}`, {
        module: 'farmer',
        action: 'Create Contract'
      });
    }
  });

  const recordProcurementMutation = useMutation(farmerService.recordProcurement, {
    onSuccess: (data) => {
      queryClient.invalidateQueries(['farmers', 'farmer-analytics']);
      setProcurementDialogOpen(false);
      toast.showSuccess(`Procurement recorded: ${data.procurement?.quantity || 'N/A'} kg`, {
        module: 'farmer',
        action: 'Record Procurement'
      });
    },
    onError: (error) => {
      toast.showError(`Failed to record procurement: ${error.response?.data?.message || error.message}`, {
        module: 'farmer',
        action: 'Record Procurement'
      });
    }
  });

  const updateFarmerMutation = useMutation(
    ({ farmerId, farmerData }) => farmerService.updateFarmer(farmerId, farmerData),
    {
      onSuccess: (data) => {
        queryClient.invalidateQueries(['farmers', 'farmer-analytics']);
        setEditDialogOpen(false);
        setSelectedFarmer(null);
        setEditFormData({});

        // Show appropriate message based on verification status
        if (data.auto_approved) {
          toast.farmer.updated(selectedFarmer?.name || 'Farmer', 'Auto-approved changes');
        } else if (data.requires_approval) {
          toast.farmer.editRequestSubmitted(selectedFarmer?.name || 'Farmer', data.changes || {});
        } else {
          toast.farmer.updated(selectedFarmer?.name || 'Farmer');
        }
      },
      onError: (error) => {
        console.error('Update farmer error:', error);
        toast.farmer.error('Update', error.response?.data?.message || error.message);
      }
    }
  );

  const approveFarmerMutation = useMutation(
    ({ farmerId, updateData }) => farmerService.verifyFarmer(farmerId, updateData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['farmers']);
        setApprovalDialogOpen(false);
      }
    }
  );

  const updateContractMutation = useMutation(
    ({ contractId, updateData }) => farmerService.updateContract(contractId, updateData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['all-contracts']);
        setContractEditDialogOpen(false);
        setContractStatusDialogOpen(false);
        setContractEditError('');
      },
      onError: (error) => {
        setContractEditError(getApiErrorMessage(error, 'Could not update contract'));
      }
    }
  );

  const getStatusColor = (isActive) => {
    return isActive ? 'success' : 'default';
  };

  const getVerificationColor = (isVerified) => {
    return isVerified ? 'success' : 'warning';
  };

  const getStatusLabel = (isActive) => {
    return isActive ? 'Active' : 'Inactive';
  };

  const getVerificationLabel = (isVerified) => {
    return isVerified ? 'Verified' : 'Pending';
  };

  // Action handlers
  const handleViewFarmer = (farmer) => {
    setSelectedFarmer(farmer);
    setViewDialogOpen(true);
  };

  const handleEditFarmer = (farmer) => {
    setSelectedFarmer(farmer);
    setEditFormData({
      name: farmer.name || '',
      phone: farmer.phone || '',
      email: farmer.email || '',
      village: farmer.village || '',
      district: farmer.district || '',
      state: farmer.state || '',
      pincode: farmer.pincode || '',
      address: farmer.address || '',
      aadhar_number: farmer.aadhar_number || '',
      pan_number: farmer.pan_number || '',
      land_area: farmer.land_area || '',
      farming_experience: farmer.farming_experience || '',
      farming_type: farmer.farming_type || 'conventional',
      irrigation_type: farmer.irrigation_type || 'bore_well',
      bank_account: farmer.bank_account || '',
      ifsc_code: farmer.ifsc_code || '',
      bank_name: farmer.bank_name || '',
      branch_name: farmer.branch_name || '',
      payment_terms: farmer.payment_terms || 'immediate',
      credit_limit: farmer.credit_limit || ''
    });
    setEditDialogOpen(true);
  };

  const handleSaveEditFarmer = () => {
    if (selectedFarmer && editFormData) {
      // Add edit reason to the form data
      const dataWithReason = {
        ...editFormData,
        edit_reason: editFormData.edit_reason || 'Information update'
      };

      updateFarmerMutation.mutate({
        farmerId: selectedFarmer.id,
        farmerData: dataWithReason
      });
    }
  };

  const handleEditFormChange = (field, value) => {
    setEditFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleApproveFarmer = (farmer) => {
    setSelectedFarmer(farmer);
    setApprovalDialogOpen(true);
  };

  const handleUpdateFarmerStatus = (farmerId, updates) => {
    approveFarmerMutation.mutate({ farmerId, updateData: updates });
  };

  // Contract action handlers
  const handleViewContract = (contract) => {
    setSelectedContract(contract);
    setContractViewDialogOpen(true);
  };

  const handleEditContract = (contract) => {
    setSelectedContract(contract);
    setContractEditError('');
    setContractEditForm({
      quantity_committed: contract.quantity_committed || '',
      base_price: contract.base_price || '',
      quality_bonus: contract.quality_bonus || '',
      advance_amount: contract.advance_amount || '',
      terms_conditions: contract.terms_conditions || '',
      special_instructions: contract.special_instructions || '',
    });
    setContractEditDialogOpen(true);
  };

  const handleUpdateContractStatus = (contract) => {
    setSelectedContract(contract);
    setContractStatusDialogOpen(true);
  };

  const handleContractStatusUpdate = (contractId, newStatus) => {
    updateContractMutation.mutate({
      contractId,
      updateData: {
        status: newStatus,
        updated_at: new Date().toISOString()
      }
    });
  };

  const getContractStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'info';
      case 'cancelled': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  // Show loading during authentication check
  if (!authChecked) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Typography>{t('loading')}</Typography>
      </Box>
    );
  }

  return (
    <PageShell>
      <PageHeader
        title={t('farmerManagement')}
        subtitle={t('farmerSubtitle')}
        actions={
          <>
            <Button variant="contained" startIcon={<PersonAdd />} onClick={() => setRegisterDialogOpen(true)}>
              {t('registerFarmer')}
            </Button>
            <Button variant="outlined" startIcon={<Assignment />} onClick={() => setContractDialogOpen(true)}>
              {t('createContract')}
            </Button>
            <Button variant="outlined" startIcon={<Agriculture />} onClick={() => setProcurementDialogOpen(true)}>
              {t('recordProcurement')}
            </Button>
            <Button variant="outlined" startIcon={<PendingActions />} onClick={() => setEditRequestsDialogOpen(true)} color="warning">
              {t('editRequests')}
            </Button>
          </>
        }
      />
      {farmersError && <QueryErrorAlert error={farmersError} entity="farmers" />}

      {/* Analytics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PersonAdd color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    {t('totalFarmers')}
                  </Typography>
                  <Typography variant="h5">
                    {analyticsLoading ? '...' : (analytics?.analytics?.total_farmers || 0)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Assignment color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    {t('activeContracts')}
                  </Typography>
                  <Typography variant="h5">
                    {analyticsLoading ? '...' : (analytics?.analytics?.active_contracts || 0)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Agriculture color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    {t('totalProcurementQt')}
                  </Typography>
                  <Typography variant="h5">
                    {analyticsLoading ? '...' : (analytics?.analytics?.total_procurement ? `${(analytics.analytics.total_procurement / 100).toFixed(1)}` : '0')}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <AccountBalance color="info" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    {t('totalPayments')}
                  </Typography>
                  <Typography variant="h5">
                    {analyticsLoading ? '...' : (analytics?.analytics?.total_payments ? formatCurrency(analytics.analytics.total_payments) : '₹0')}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label={t('allFarmers')} />
          <Tab label={t('recentProcurements')} />
          <Tab label={t('contractManagement')} />
          <Tab label={t('analytics')} />
        </Tabs>
      </Box>

      {/* Farmers List Tab */}
      <TabPanel value={tabValue} index={0}>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder={t('searchFarmers')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {t('allFarmers')} ({farmersData?.farmers?.length || 0})
            </Typography>
            {farmersLoading ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  Loading farmers...
                </Typography>
              </Box>
            ) : farmersError ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="error">
                  {getApiErrorMessage(farmersError, 'Could not load farmers')}
                </Typography>
              </Box>
            ) : farmersData?.farmers?.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('farmerCode')}</TableCell>
                      <TableCell>{t('name')}</TableCell>
                      <TableCell>{t('phone')}</TableCell>
                      <TableCell>{t('village')}</TableCell>
                      <TableCell>{t('landArea')}</TableCell>
                      <TableCell>{t('qualityRating')}</TableCell>
                      <TableCell>{t('status')}</TableCell>
                      <TableCell>{t('verification')}</TableCell>
                      <TableCell>{t('actions')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {farmersData.farmers.map((farmer) => (
                    <TableRow key={farmer.id}>
                      <TableCell>{farmer.farmer_code}</TableCell>
                      <TableCell>{farmer.name}</TableCell>
                      <TableCell>{farmer.phone}</TableCell>
                      <TableCell>{farmer.village}</TableCell>
                      <TableCell>{farmer.land_area || 'N/A'} acres</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2">
                            {farmer.quality_rating?.toFixed(1) || '0.0'}
                          </Typography>
                          <TrendingUp 
                            fontSize="small" 
                            color={farmer.quality_rating > 3.5 ? 'success' : 'warning'}
                            sx={{ ml: 1 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusLabel(farmer.is_active)}
                          color={getStatusColor(farmer.is_active)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getVerificationLabel(farmer.is_verified)}
                          color={getVerificationColor(farmer.is_verified)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                          <Button size="small" startIcon={<Visibility />} onClick={() => handleViewFarmer(farmer)} sx={{ minHeight: 40 }}>
                            View
                          </Button>
                          <Button size="small" startIcon={<Assignment />} onClick={() => handleEditFarmer(farmer)} sx={{ minHeight: 40 }}>
                            Edit
                          </Button>
                          {!farmer.is_verified && (
                            <Button size="small" color="success" startIcon={<Payment />} onClick={() => handleApproveFarmer(farmer)} sx={{ minHeight: 40 }}>
                              Verify
                            </Button>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <PersonAdd sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No Farmers Found
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {searchTerm ? 'No farmers match your search criteria' : 'Start by registering your first farmer'}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<PersonAdd />}
                  onClick={() => setRegisterDialogOpen(true)}
                >
                  Register First Farmer
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Recent Procurements Tab */}
      <TabPanel value={tabValue} index={1}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Procurements
            </Typography>
            {procurementsData?.procurements?.length > 0 ? (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('date')}</TableCell>
                      <TableCell>{t('farmers')}</TableCell>
                      <TableCell>{t('variety')}</TableCell>
                      <TableCell>{t('quantityKg')}</TableCell>
                      <TableCell>{t('pricePerUnit')}</TableCell>
                      <TableCell>{t('totalAmount')}</TableCell>
                      <TableCell>{t('quality')}</TableCell>
                      <TableCell>{t('status')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {procurementsData.procurements.map((procurement) => (
                      <TableRow key={procurement.id}>
                        <TableCell>
                          {new Date(procurement.procurement_date).toLocaleDateString()}
                        </TableCell>
                        <TableCell>{procurement.farmer_name}</TableCell>
                        <TableCell>{procurement.variety}</TableCell>
                        <TableCell>{procurement.quantity}</TableCell>
                        <TableCell>{formatCurrency(procurement.price_per_unit)}</TableCell>
                        <TableCell>{formatCurrency(procurement.total_amount)}</TableCell>
                        <TableCell>
                          <Chip
                            label={procurement.quality_grade || 'A'}
                            color="success"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={procurement.status || 'Completed'}
                            color="success"
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Agriculture sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No Procurements Yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Start recording paddy procurements to see them here
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Agriculture />}
                  onClick={() => setProcurementDialogOpen(true)}
                >
                  Record First Procurement
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Contract Management Tab */}
      <TabPanel value={tabValue} index={2}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Contract Management
            </Typography>
            {contractsLoading ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  Loading contracts...
                </Typography>
              </Box>
            ) : contractsError ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="error">
                  Error loading contracts: {contractsError.message}
                </Typography>
              </Box>
            ) : contractsData?.contracts?.length > 0 ? (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('contractId')}</TableCell>
                      <TableCell>{t('farmers')}</TableCell>
                      <TableCell>{t('cropType')}</TableCell>
                      <TableCell>{t('season')}</TableCell>
                      <TableCell>{t('quantity')}</TableCell>
                      <TableCell>{t('basePrice')}</TableCell>
                      <TableCell>{t('startDate')}</TableCell>
                      <TableCell>{t('endDate')}</TableCell>
                      <TableCell>{t('status')}</TableCell>
                      <TableCell>{t('actions')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {contractsData.contracts.map((contract) => (
                      <TableRow key={contract.id}>
                        <TableCell>{contract.contract_number || `C-${contract.id}`}</TableCell>
                        <TableCell>{contract.farmer_name || 'Unknown'}</TableCell>
                        <TableCell>{contract.crop_type || contract.variety || 'Rice'}</TableCell>
                        <TableCell>
                          <Chip
                            label={contract.season || contract.contract_type || 'Kharif'}
                            color="primary"
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{contract.quantity_committed || 0} kg</TableCell>
                        <TableCell>{formatCurrency(contract.base_price || contract.price_per_kg || 0)}</TableCell>
                        <TableCell>
                          {contract.contract_start_date ?
                            new Date(contract.contract_start_date).toLocaleDateString() :
                            (contract.start_date ? new Date(contract.start_date).toLocaleDateString() : 'N/A')
                          }
                        </TableCell>
                        <TableCell>
                          {contract.contract_end_date ?
                            new Date(contract.contract_end_date).toLocaleDateString() :
                            (contract.end_date ? new Date(contract.end_date).toLocaleDateString() : 'N/A')
                          }
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={contract.status}
                            color={getContractStatusColor(contract.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton
                              size="small"
                              onClick={() => handleViewContract(contract)}
                              color="primary"
                              title="View Contract Details"
                            >
                              <Visibility />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => handleEditContract(contract)}
                              color="secondary"
                              title="Edit Contract"
                            >
                              <Assignment />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => handleUpdateContractStatus(contract)}
                              color="info"
                              title="Update Status"
                            >
                              <TrendingUp />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Assignment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No Contracts Yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Create farmer contracts to manage procurement agreements
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Assignment />}
                  onClick={() => setContractDialogOpen(true)}
                >
                  Create First Contract
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Analytics Tab */}
      <TabPanel value={tabValue} index={3}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">
            Analytics & Insights
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => {
              queryClient.invalidateQueries('farmer-analytics');
            }}
            disabled={analyticsLoading}
          >
            {analyticsLoading ? 'Refreshing...' : 'Refresh Data'}
          </Button>
        </Box>
        <Grid container spacing={3}>
          {/* Performance Metrics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Metrics
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{t('activeFarmers')}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {analyticsLoading ? '...' : (analytics?.analytics?.active_farmers || analytics?.analytics?.total_farmers || 0)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{t('totalProcurement')}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {analyticsLoading ? '...' : `${(analytics?.analytics?.total_procurement || 0) / 100} Qt`}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{t('activeContracts')}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {analyticsLoading ? '...' : (analytics?.analytics?.active_contracts || 0)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{t('totalPayments')}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {analyticsLoading ? '...' : (analytics?.analytics?.total_payments ? formatCurrency(analytics.analytics.total_payments) : '₹0')}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {analyticsLoading ? (
                    <Typography variant="body2" color="text.secondary">
                      Loading recent activity...
                    </Typography>
                  ) : analytics?.recent_activity ? (
                    <>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">New Farmers</Typography>
                        <Typography variant="body2" fontWeight="bold" color="primary">
                          +{analytics.recent_activity.new_farmers || 0}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">New Contracts</Typography>
                        <Typography variant="body2" fontWeight="bold" color="success.main">
                          +{analytics.recent_activity.new_contracts || 0}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">New Procurements</Typography>
                        <Typography variant="body2" fontWeight="bold" color="warning.main">
                          +{analytics.recent_activity.new_procurements || 0}
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                        Last {analytics.recent_activity.period || '30 days'}
                      </Typography>
                    </>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No recent activity data available
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Quality Trends */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quality & Performance Trends
                </Typography>
                {analyticsLoading ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      Loading analytics data...
                    </Typography>
                  </Box>
                ) : analytics?.analytics ? (
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="primary" gutterBottom>
                          {analytics.analytics.avg_quality_rating?.toFixed(1) || '0.0'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Average Quality Rating
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="success.main" gutterBottom>
                          {analytics.analytics.avg_land_area?.toFixed(1) || '0.0'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Average Land Area (Acres)
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <Typography variant="h4" color="warning.main" gutterBottom>
                          {analytics.analytics.total_procurement_records || 0}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Total Procurement Records
                        </Typography>
                      </Box>
                    </Grid>

                    {/* AI Insights */}
                    {analytics.ai_analytics?.insights && (
                      <Grid item xs={12}>
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="h6" gutterBottom>
                            AI Insights
                          </Typography>
                          {analytics.ai_analytics.insights.map((insight, index) => (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              <TrendingUp sx={{ mr: 1, color: 'primary.main', fontSize: 20 }} />
                              <Typography variant="body2">
                                {insight}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </Grid>
                    )}

                    {/* Recommendations */}
                    {analytics.ai_analytics?.recommendations && (
                      <Grid item xs={12}>
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="h6" gutterBottom>
                            Recommendations
                          </Typography>
                          {analytics.ai_analytics.recommendations.map((recommendation, index) => (
                            <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              <Assignment sx={{ mr: 1, color: 'success.main', fontSize: 20 }} />
                              <Typography variant="body2">
                                {recommendation}
                              </Typography>
                            </Box>
                          ))}
                        </Box>
                      </Grid>
                    )}
                  </Grid>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <TrendingUp sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      No Analytics Data Available
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Analytics will be displayed once data is available
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Dialogs */}
      <RegisterFarmerDialog
        open={registerDialogOpen}
        onClose={() => setRegisterDialogOpen(false)}
        onSubmit={registerFarmerMutation.mutate}
        loading={registerFarmerMutation.isLoading}
      />

      <CreateContractDialog
        open={contractDialogOpen}
        onClose={() => setContractDialogOpen(false)}
        onSubmit={createContractMutation.mutate}
        loading={createContractMutation.isLoading}
      />

      <RecordProcurementDialog
        open={procurementDialogOpen}
        onClose={() => setProcurementDialogOpen(false)}
        onSubmit={recordProcurementMutation.mutate}
        loading={recordProcurementMutation.isLoading}
      />

      {/* View Farmer Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">{t('farmerDetails')}</Typography>
            <IconButton onClick={() => setViewDialogOpen(false)}>
              <Search />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedFarmer && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Basic Information</Typography>
                    <Typography><strong>Farmer Code:</strong> {selectedFarmer.farmer_code}</Typography>
                    <Typography><strong>Name:</strong> {selectedFarmer.name}</Typography>
                    <Typography><strong>Phone:</strong> {selectedFarmer.phone}</Typography>
                    <Typography><strong>Email:</strong> {selectedFarmer.email || 'N/A'}</Typography>
                    <Typography><strong>Village:</strong> {selectedFarmer.village}</Typography>
                    <Typography><strong>District:</strong> {selectedFarmer.district}</Typography>
                    <Typography><strong>State:</strong> {selectedFarmer.state}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Farming Information</Typography>
                    <Typography><strong>Land Area:</strong> {selectedFarmer.land_area || 'N/A'} acres</Typography>
                    <Typography><strong>Farming Experience:</strong> {selectedFarmer.farming_experience || 'N/A'} years</Typography>
                    <Typography><strong>Farming Type:</strong> {selectedFarmer.farming_type || 'N/A'}</Typography>
                    <Typography><strong>Quality Rating:</strong> {selectedFarmer.quality_rating?.toFixed(1) || '0.0'}/5.0</Typography>
                    <Typography><strong>Total Transactions:</strong> {selectedFarmer.total_transactions || 0}</Typography>
                    <Typography><strong>Total Quantity Supplied:</strong> {selectedFarmer.total_quantity_supplied || 0} kg</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Status & Verification</Typography>
                    <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                      <Chip
                        label={getStatusLabel(selectedFarmer.is_active)}
                        color={getStatusColor(selectedFarmer.is_active)}
                      />
                      <Chip
                        label={getVerificationLabel(selectedFarmer.is_verified)}
                        color={getVerificationColor(selectedFarmer.is_verified)}
                      />
                    </Box>
                    <Typography><strong>Created:</strong> {new Date(selectedFarmer.created_at).toLocaleDateString()}</Typography>
                    <Typography><strong>Last Updated:</strong> {new Date(selectedFarmer.updated_at).toLocaleDateString()}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>{t('close')}</Button>
          <Button
            variant="contained"
            onClick={() => {
              setViewDialogOpen(false);
              handleEditFarmer(selectedFarmer);
            }}
          >
            Edit Farmer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Farmer Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>{t('editFarmer')}</DialogTitle>
        <DialogContent>
          {selectedFarmer && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={3}>
                {/* Edit Reason */}
                <Grid item xs={12}>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Changes to farmer information require verification and approval.
                  </Alert>
                  <TextField
                    fullWidth
                    label={t('reasonForEdit')}
                    value={editFormData.edit_reason || ''}
                    onChange={(e) => handleEditFormChange('edit_reason', e.target.value)}
                    placeholder={t('reasonForEditPh')}
                    multiline
                    rows={2}
                    margin="normal"
                    helperText={t('reasonReviewHint')}
                  />
                </Grid>

                {/* Basic Information */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom color="primary">
                    Basic Information
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('fullName')}
                    value={editFormData.name || ''}
                    onChange={(e) => handleEditFormChange('name', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('phoneNumber')}
                    value={editFormData.phone || ''}
                    onChange={(e) => handleEditFormChange('phone', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('email')}
                    type="email"
                    value={editFormData.email || ''}
                    onChange={(e) => handleEditFormChange('email', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('farmerCode')}
                    defaultValue={selectedFarmer.farmer_code}
                    margin="normal"
                    disabled
                    helperText={t('farmerCodeReadonly')}
                  />
                </Grid>

                {/* Address Information */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom color="primary" sx={{ mt: 2 }}>
                    Address Information
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('village')}
                    value={editFormData.village || ''}
                    onChange={(e) => handleEditFormChange('village', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('district')}
                    value={editFormData.district || ''}
                    onChange={(e) => handleEditFormChange('district', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('state')}
                    value={editFormData.state || ''}
                    onChange={(e) => handleEditFormChange('state', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('pincode')}
                    defaultValue={selectedFarmer.pincode || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label={t('address')}
                    multiline
                    rows={2}
                    defaultValue={selectedFarmer.address || ''}
                    margin="normal"
                  />
                </Grid>

                {/* Identity Information */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom color="primary" sx={{ mt: 2 }}>
                    Identity Information
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('aadharNumber')}
                    defaultValue={selectedFarmer.aadhar_number || ''}
                    margin="normal"
                    inputProps={{ maxLength: 12 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('panNumber')}
                    defaultValue={selectedFarmer.pan_number || ''}
                    margin="normal"
                    inputProps={{ maxLength: 10 }}
                  />
                </Grid>

                {/* Farming Information */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom color="primary" sx={{ mt: 2 }}>
                    Farming Information
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('totalLandAcres')}
                    type="number"
                    defaultValue={selectedFarmer.land_area || ''}
                    margin="normal"
                    inputProps={{ min: 0, step: 0.1 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('farmingYears')}
                    type="number"
                    defaultValue={selectedFarmer.farming_experience || ''}
                    margin="normal"
                    inputProps={{ min: 0 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <LookupSelect
                    group="farming_type"
                    label={t('farmingType')}
                    value={editFormData.farming_type || selectedFarmer.farming_type || 'conventional'}
                    onChange={(e) => handleEditFormChange('farming_type', e.target.value)}
                    sx={{ mt: 2 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <LookupSelect
                    group="irrigation_type"
                    label={t('irrigationType')}
                    value={editFormData.irrigation_type || selectedFarmer.irrigation_type || 'bore_well'}
                    onChange={(e) => handleEditFormChange('irrigation_type', e.target.value)}
                    sx={{ mt: 2 }}
                  />
                </Grid>

                {/* Banking Information */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom color="primary" sx={{ mt: 2 }}>
                    Banking Information
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('bankAccount')}
                    defaultValue={selectedFarmer.bank_account || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('ifscCode')}
                    defaultValue={selectedFarmer.ifsc_code || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('bankName')}
                    defaultValue={selectedFarmer.bank_name || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('branchName')}
                    defaultValue={selectedFarmer.branch_name || ''}
                    margin="normal"
                  />
                </Grid>

                {/* Business Information */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom color="primary" sx={{ mt: 2 }}>
                    Business Information
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <LookupSelect
                    group="payment_terms"
                    label={t('paymentTerms')}
                    value={editFormData.payment_terms || selectedFarmer.payment_terms || 'immediate'}
                    onChange={(e) => handleEditFormChange('payment_terms', e.target.value)}
                    sx={{ mt: 2 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('creditLimit')}
                    type="number"
                    defaultValue={selectedFarmer.credit_limit || ''}
                    margin="normal"
                    inputProps={{ min: 0 }}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>{t('cancel')}</Button>
          <Button
            variant="contained"
            onClick={handleSaveEditFarmer}
            disabled={updateFarmerMutation.isLoading}
          >
            {updateFarmerMutation.isLoading ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Approval Dialog */}
      <Dialog
        open={approvalDialogOpen}
        onClose={() => setApprovalDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{t('farmerApproval')}</DialogTitle>
        <DialogContent>
          {selectedFarmer && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                {t('farmerApproval')}: {selectedFarmer.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {t('farmerCode')}: {selectedFarmer.farmer_code}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {t('phone')}: {selectedFarmer.phone}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {t('village')}: {selectedFarmer.village}
              </Typography>

              <Alert severity="info" sx={{ mt: 2 }}>
                {t('approveWill')}
                <ul>
                  <li>{t('approveVerified')}</li>
                  <li>{t('approveContracts')}</li>
                  <li>{t('approveNotify')}</li>
                </ul>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialogOpen(false)}>{t('cancel')}</Button>
          <Button
            variant="contained"
            color="success"
            onClick={() => {
              if (selectedFarmer) {
                handleUpdateFarmerStatus(selectedFarmer.id, {
                  is_verified: true,
                  verification_date: new Date().toISOString()
                });
              }
            }}
            disabled={approveFarmerMutation.isLoading}
          >
            {approveFarmerMutation.isLoading ? 'Approving...' : 'Approve Farmer'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Contract View Dialog */}
      <Dialog
        open={contractViewDialogOpen}
        onClose={() => setContractViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Contract Details</Typography>
            <IconButton onClick={() => setContractViewDialogOpen(false)}>
              <Search />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedContract && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Contract Information</Typography>
                    <Typography><strong>Contract ID:</strong> {selectedContract.contract_number || `C-${selectedContract.id}`}</Typography>
                    <Typography><strong>Farmer:</strong> {selectedContract.farmer_name}</Typography>
                    <Typography><strong>Crop Type:</strong> {selectedContract.crop_type}</Typography>
                    <Typography><strong>Season:</strong> {selectedContract.season}</Typography>
                    <Typography><strong>Year:</strong> {selectedContract.year}</Typography>
                    <Box sx={{ mt: 2 }}>
                      <Chip
                        label={selectedContract.status}
                        color={getContractStatusColor(selectedContract.status)}
                        size="small"
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Financial Details</Typography>
                    <Typography><strong>Quantity Committed:</strong> {selectedContract.quantity_committed} kg</Typography>
                    <Typography><strong>Base Price:</strong> {formatCurrency(selectedContract.base_price)}</Typography>
                    <Typography><strong>Quality Bonus:</strong> {formatCurrency(selectedContract.quality_bonus || 0)}</Typography>
                    <Typography><strong>Advance Amount:</strong> {formatCurrency(selectedContract.advance_amount || 0)}</Typography>
                    <Typography><strong>Total Value:</strong> {formatCurrency((selectedContract.quantity_committed || 0) * (selectedContract.base_price || 0))}</Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>Timeline & Terms</Typography>
                    <Typography><strong>Start Date:</strong> {new Date(selectedContract.contract_start_date).toLocaleDateString()}</Typography>
                    <Typography><strong>End Date:</strong> {new Date(selectedContract.contract_end_date).toLocaleDateString()}</Typography>
                    <Typography><strong>Payment Terms:</strong> {selectedContract.payment_terms || 'Standard'}</Typography>
                    {selectedContract.terms_conditions && (
                      <Typography><strong>Terms & Conditions:</strong> {selectedContract.terms_conditions}</Typography>
                    )}
                    {selectedContract.special_instructions && (
                      <Typography><strong>Special Instructions:</strong> {selectedContract.special_instructions}</Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContractViewDialogOpen(false)}>{t('close')}</Button>
          <Button
            variant="contained"
            onClick={() => {
              setContractViewDialogOpen(false);
              handleEditContract(selectedContract);
            }}
          >
            Edit Contract
          </Button>
        </DialogActions>
      </Dialog>

      {/* Contract Edit Dialog */}
      <Dialog
        open={contractEditDialogOpen}
        onClose={() => setContractEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{t('editContract')}</DialogTitle>
        <DialogContent>
          {contractEditError && <Alert severity="error" sx={{ mt: 1 }}>{contractEditError}</Alert>}
          {selectedContract && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('qtyCommittedKg')}
                    type="number"
                    value={contractEditForm.quantity_committed}
                    onChange={(e) => setContractEditForm({ ...contractEditForm, quantity_committed: e.target.value })}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('basePriceKg')}
                    type="number"
                    value={contractEditForm.base_price}
                    onChange={(e) => setContractEditForm({ ...contractEditForm, base_price: e.target.value })}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('qualityBonusRs')}
                    type="number"
                    value={contractEditForm.quality_bonus}
                    onChange={(e) => setContractEditForm({ ...contractEditForm, quality_bonus: e.target.value })}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label={t('advanceAmount')}
                    type="number"
                    value={contractEditForm.advance_amount}
                    onChange={(e) => setContractEditForm({ ...contractEditForm, advance_amount: e.target.value })}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label={t('termsConditions')}
                    multiline
                    rows={3}
                    value={contractEditForm.terms_conditions}
                    onChange={(e) => setContractEditForm({ ...contractEditForm, terms_conditions: e.target.value })}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label={t('specialInstructions')}
                    multiline
                    rows={2}
                    value={contractEditForm.special_instructions}
                    onChange={(e) => setContractEditForm({ ...contractEditForm, special_instructions: e.target.value })}
                    margin="normal"
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContractEditDialogOpen(false)}>{t('cancel')}</Button>
          <Button
            variant="contained"
            onClick={() => {
              const qty = parseFloat(contractEditForm.quantity_committed);
              const price = parseFloat(contractEditForm.base_price);
              if (!Number.isFinite(qty) || qty <= 0 || !Number.isFinite(price) || price <= 0) {
                setContractEditError('Quantity and base price must be greater than 0');
                return;
              }
              setContractEditError('');
              updateContractMutation.mutate({
                contractId: selectedContract.id,
                updateData: {
                  quantity_committed: qty,
                  base_price: price,
                  quality_bonus: parseFloat(contractEditForm.quality_bonus) || 0,
                  advance_amount: parseFloat(contractEditForm.advance_amount) || 0,
                  terms_conditions: contractEditForm.terms_conditions,
                  special_instructions: contractEditForm.special_instructions,
                }
              });
            }}
            disabled={updateContractMutation.isLoading}
          >
            {updateContractMutation.isLoading ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Contract Status Update Dialog */}
      <Dialog
        open={contractStatusDialogOpen}
        onClose={() => setContractStatusDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{t('updateContractStatus')}</DialogTitle>
        <DialogContent>
          {selectedContract && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Contract: {selectedContract.contract_number || `C-${selectedContract.id}`}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Farmer: {selectedContract.farmer_name}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Current Status:
                </Typography>
                <Chip label={selectedContract.status} color={getContractStatusColor(selectedContract.status)} size="small" />
              </Box>

              <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
                Select New Status:
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant={selectedContract.status === 'active' ? 'contained' : 'outlined'}
                  color="success"
                  onClick={() => handleContractStatusUpdate(selectedContract.id, 'active')}
                  disabled={selectedContract.status === 'active' || updateContractMutation.isLoading}
                >
                  Mark as Active
                </Button>
                <Button
                  variant={selectedContract.status === 'completed' ? 'contained' : 'outlined'}
                  color="info"
                  onClick={() => handleContractStatusUpdate(selectedContract.id, 'completed')}
                  disabled={selectedContract.status === 'completed' || updateContractMutation.isLoading}
                >
                  Mark as Completed
                </Button>
                <Button
                  variant={selectedContract.status === 'cancelled' ? 'contained' : 'outlined'}
                  color="error"
                  onClick={() => handleContractStatusUpdate(selectedContract.id, 'cancelled')}
                  disabled={selectedContract.status === 'cancelled' || updateContractMutation.isLoading}
                >
                  Mark as Cancelled
                </Button>
              </Box>

              {updateContractMutation.isLoading && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  Updating contract status...
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContractStatusDialogOpen(false)}>{t('close')}</Button>
        </DialogActions>
      </Dialog>

      {/* Farmer Edit Requests Dialog */}
      <FarmerEditRequestsDialog
        open={editRequestsDialogOpen}
        onClose={() => setEditRequestsDialogOpen(false)}
        farmerId={selectedFarmerForRequests?.id}
      />
    </PageShell>
  );
};

export default Farmers;