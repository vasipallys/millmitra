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
import RegisterFarmerDialog from '../components/farmer/RegisterFarmerDialog';
import FarmerEditRequestsDialog from '../components/farmer/FarmerEditRequestsDialog';
import CreateContractDialog from '../components/farmer/CreateContractDialog';
import RecordProcurementDialog from '../components/farmer/RecordProcurementDialog';

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
  const [selectedFarmerForRequests, setSelectedFarmerForRequests] = useState(null);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Check if user is authenticated
  const isAuthenticated = !!localStorage.getItem('token');

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
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Queries
  const { data: farmersData, isLoading: farmersLoading, error: farmersError } = useQuery(
    ['farmers', searchTerm],
    () => farmerService.getFarmers({ search: searchTerm }),
    {
      refetchInterval: 300000,
      enabled: isAuthenticated,
      onSuccess: (data) => {
        console.log('Farmers data received:', data);
        if (data?.farmers?.length > 0) {
          console.log('Sample farmer data:', data.farmers[0]);
        }
      },
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
      onSuccess: (data) => {
        console.log('Analytics data received:', data);
        if (data?.analytics) {
          console.log('Analytics metrics:', data.analytics);
        }
      },
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
      enabled: isAuthenticated
    }
  );

  const { data: contractsData, isLoading: contractsLoading, error: contractsError } = useQuery(
    'all-contracts',
    () => farmerService.getContracts({ status: 'all' }),
    {
      refetchInterval: 300000,
      enabled: isAuthenticated,
      onSuccess: (data) => {
        console.log('Contracts data received:', data);
        if (data?.contracts?.length > 0) {
          console.log('Sample contract data:', data.contracts[0]);
        }
      },
      onError: (error) => {
        console.error('Contracts fetch error:', error);
      }
    }
  );

  // Mutations
  const registerFarmerMutation = useMutation(farmerService.registerFarmer, {
    onSuccess: () => {
      queryClient.invalidateQueries('farmers');
      setRegisterDialogOpen(false);
    },
    onError: (error) => {
      console.error('Farmer registration error:', error);
    }
  });

  // Handle farmer registration with proper promise handling
  const handleFarmerRegistration = async (farmerData) => {
    try {
      const result = await farmerService.registerFarmer(farmerData);
      queryClient.invalidateQueries('farmers');
      setRegisterDialogOpen(false);
      return result;
    } catch (error) {
      console.error('Farmer registration error:', error);
      throw error;
    }
  };

  const createContractMutation = useMutation(farmerService.createContract, {
    onSuccess: () => {
      queryClient.invalidateQueries(['farmers', 'farmer-analytics']);
      setContractDialogOpen(false);
    }
  });

  const recordProcurementMutation = useMutation(farmerService.recordProcurement, {
    onSuccess: () => {
      queryClient.invalidateQueries(['farmers', 'farmer-analytics']);
      setProcurementDialogOpen(false);
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
          alert('Changes applied successfully (auto-approved)');
        } else if (data.requires_approval) {
          alert('Edit request submitted for approval. Changes will be applied after verification.');
        }
      },
      onError: (error) => {
        console.error('Update farmer error:', error);
        alert('Error submitting edit request: ' + (error.response?.data?.message || error.message));
      }
    }
  );

  const approveFarmerMutation = useMutation(
    ({ farmerId, updateData }) => farmerService.updateFarmer(farmerId, updateData),
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

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Farmer Management
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<PersonAdd />}
            onClick={() => setRegisterDialogOpen(true)}
            sx={{ mr: 2 }}
          >
            Register Farmer
          </Button>
          <Button
            variant="outlined"
            startIcon={<Assignment />}
            onClick={() => setContractDialogOpen(true)}
            sx={{ mr: 2 }}
          >
            Create Contract
          </Button>
          <Button
            variant="outlined"
            startIcon={<Agriculture />}
            onClick={() => setProcurementDialogOpen(true)}
            sx={{ mr: 2 }}
          >
            Record Procurement
          </Button>
          <Button
            variant="outlined"
            startIcon={<PendingActions />}
            onClick={() => setEditRequestsDialogOpen(true)}
            color="warning"
          >
            Edit Requests
          </Button>
        </Box>
      </Box>

      {/* Analytics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PersonAdd color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Farmers
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
                    Active Contracts
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
                    Total Procurement (Qt)
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
                    Total Payments
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
          <Tab label="All Farmers" />
          <Tab label="Recent Procurements" />
          <Tab label="Contract Management" />
          <Tab label="Analytics" />
        </Tabs>
      </Box>

      {/* Farmers List Tab */}
      <TabPanel value={tabValue} index={0}>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search farmers by name, code, or phone..."
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
              All Farmers ({farmersData?.farmers?.length || 0})
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
                  Error loading farmers: {farmersError.message}
                </Typography>
              </Box>
            ) : farmersData?.farmers?.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Farmer Code</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Phone</TableCell>
                      <TableCell>Village</TableCell>
                      <TableCell>Land Area</TableCell>
                      <TableCell>Quality Rating</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Verification</TableCell>
                      <TableCell>Actions</TableCell>
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
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            size="small"
                            onClick={() => handleViewFarmer(farmer)}
                            color="primary"
                            title="View Details"
                          >
                            <Visibility />
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => handleEditFarmer(farmer)}
                            color="secondary"
                            title="Edit Farmer"
                          >
                            <Assignment />
                          </IconButton>
                          {!farmer.is_verified && (
                            <IconButton
                              size="small"
                              onClick={() => handleApproveFarmer(farmer)}
                              color="success"
                              title="Approve/Verify"
                            >
                              <Payment />
                            </IconButton>
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
                      <TableCell>Date</TableCell>
                      <TableCell>Farmer</TableCell>
                      <TableCell>Variety</TableCell>
                      <TableCell>Quantity (kg)</TableCell>
                      <TableCell>Price/Unit</TableCell>
                      <TableCell>Total Amount</TableCell>
                      <TableCell>Quality</TableCell>
                      <TableCell>Status</TableCell>
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
                      <TableCell>Contract ID</TableCell>
                      <TableCell>Farmer</TableCell>
                      <TableCell>Crop Type</TableCell>
                      <TableCell>Season</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Base Price</TableCell>
                      <TableCell>Start Date</TableCell>
                      <TableCell>End Date</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
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
                    <Typography variant="body2">Active Farmers</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {analyticsLoading ? '...' : (analytics?.analytics?.active_farmers || analytics?.analytics?.total_farmers || 0)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Total Procurement</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {analyticsLoading ? '...' : `${(analytics?.analytics?.total_procurement || 0) / 100} Qt`}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Active Contracts</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {analyticsLoading ? '...' : (analytics?.analytics?.active_contracts || 0)}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Total Payments</Typography>
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
        onSubmit={handleFarmerRegistration}
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
            <Typography variant="h6">Farmer Details</Typography>
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
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
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
        <DialogTitle>Edit Farmer Information</DialogTitle>
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
                    label="Reason for Edit"
                    value={editFormData.edit_reason || ''}
                    onChange={(e) => handleEditFormChange('edit_reason', e.target.value)}
                    placeholder="Please provide a reason for this edit..."
                    multiline
                    rows={2}
                    margin="normal"
                    helperText="This information will be reviewed by administrators"
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
                    label="Full Name"
                    value={editFormData.name || ''}
                    onChange={(e) => handleEditFormChange('name', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    value={editFormData.phone || ''}
                    onChange={(e) => handleEditFormChange('phone', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    type="email"
                    value={editFormData.email || ''}
                    onChange={(e) => handleEditFormChange('email', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Farmer Code"
                    defaultValue={selectedFarmer.farmer_code}
                    margin="normal"
                    disabled
                    helperText="Farmer code cannot be changed"
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
                    label="Village"
                    value={editFormData.village || ''}
                    onChange={(e) => handleEditFormChange('village', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="District"
                    value={editFormData.district || ''}
                    onChange={(e) => handleEditFormChange('district', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="State"
                    value={editFormData.state || ''}
                    onChange={(e) => handleEditFormChange('state', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Pincode"
                    defaultValue={selectedFarmer.pincode || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Address"
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
                    label="Aadhar Number"
                    defaultValue={selectedFarmer.aadhar_number || ''}
                    margin="normal"
                    inputProps={{ maxLength: 12 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="PAN Number"
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
                    label="Land Area (acres)"
                    type="number"
                    defaultValue={selectedFarmer.land_area || ''}
                    margin="normal"
                    inputProps={{ min: 0, step: 0.1 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Farming Experience (years)"
                    type="number"
                    defaultValue={selectedFarmer.farming_experience || ''}
                    margin="normal"
                    inputProps={{ min: 0 }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    select
                    label="Farming Type"
                    defaultValue={selectedFarmer.farming_type || 'conventional'}
                    margin="normal"
                  >
                    <MenuItem value="organic">Organic</MenuItem>
                    <MenuItem value="conventional">Conventional</MenuItem>
                    <MenuItem value="mixed">Mixed</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    select
                    label="Irrigation Type"
                    defaultValue={selectedFarmer.irrigation_type || 'bore_well'}
                    margin="normal"
                  >
                    <MenuItem value="bore_well">Bore Well</MenuItem>
                    <MenuItem value="canal">Canal</MenuItem>
                    <MenuItem value="rain_fed">Rain Fed</MenuItem>
                    <MenuItem value="mixed">Mixed</MenuItem>
                  </TextField>
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
                    label="Bank Account Number"
                    defaultValue={selectedFarmer.bank_account || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="IFSC Code"
                    defaultValue={selectedFarmer.ifsc_code || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Bank Name"
                    defaultValue={selectedFarmer.bank_name || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Branch Name"
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
                  <TextField
                    fullWidth
                    select
                    label="Payment Terms"
                    defaultValue={selectedFarmer.payment_terms || 'immediate'}
                    margin="normal"
                  >
                    <MenuItem value="immediate">Immediate</MenuItem>
                    <MenuItem value="15_days">15 Days</MenuItem>
                    <MenuItem value="30_days">30 Days</MenuItem>
                    <MenuItem value="45_days">45 Days</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Credit Limit (₹)"
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
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
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
        <DialogTitle>Farmer Approval</DialogTitle>
        <DialogContent>
          {selectedFarmer && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                Approve Farmer: {selectedFarmer.name}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Farmer Code: {selectedFarmer.farmer_code}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Phone: {selectedFarmer.phone}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Village: {selectedFarmer.village}
              </Typography>

              <Alert severity="info" sx={{ mt: 2 }}>
                Approving this farmer will:
                <ul>
                  <li>Mark them as verified</li>
                  <li>Enable them for contracts and procurements</li>
                  <li>Send confirmation notification</li>
                </ul>
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApprovalDialogOpen(false)}>Cancel</Button>
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
          <Button onClick={() => setContractViewDialogOpen(false)}>Close</Button>
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
        <DialogTitle>Edit Contract</DialogTitle>
        <DialogContent>
          {selectedContract && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Quantity Committed (kg)"
                    type="number"
                    defaultValue={selectedContract.quantity_committed || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Base Price (₹/kg)"
                    type="number"
                    defaultValue={selectedContract.base_price || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Quality Bonus (₹)"
                    type="number"
                    defaultValue={selectedContract.quality_bonus || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Advance Amount (₹)"
                    type="number"
                    defaultValue={selectedContract.advance_amount || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Terms & Conditions"
                    multiline
                    rows={3}
                    defaultValue={selectedContract.terms_conditions || ''}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Special Instructions"
                    multiline
                    rows={2}
                    defaultValue={selectedContract.special_instructions || ''}
                    margin="normal"
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContractEditDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              // TODO: Implement actual contract edit functionality
              console.log('Save contract changes');
              setContractEditDialogOpen(false);
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
        <DialogTitle>Update Contract Status</DialogTitle>
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
          <Button onClick={() => setContractStatusDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Farmer Edit Requests Dialog */}
      <FarmerEditRequestsDialog
        open={editRequestsDialogOpen}
        onClose={() => setEditRequestsDialogOpen(false)}
        farmerId={selectedFarmerForRequests?.id}
      />
    </Box>
  );
};

export default Farmers;