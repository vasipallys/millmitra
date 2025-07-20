import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, IconButton, Dialog, TextField, InputAdornment, Tabs, Tab
} from '@mui/material';
import {
  PersonAdd, Search, Visibility, Assignment, Payment,
  TrendingUp, Agriculture, AccountBalance
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { farmerService } from '../services/farmerService';
import RegisterFarmerDialog from '../components/farmer/RegisterFarmerDialog';
import CreateContractDialog from '../components/farmer/CreateContractDialog';
import RecordProcurementDialog from '../components/farmer/RecordProcurementDialog';

const Farmers = () => {
  const [tabValue, setTabValue] = useState(0);
  const [registerDialogOpen, setRegisterDialogOpen] = useState(false);
  const [contractDialogOpen, setContractDialogOpen] = useState(false);
  const [procurementDialogOpen, setProcurementDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFarmer, setSelectedFarmer] = useState(null);
  const queryClient = useQueryClient();

  // Queries
  const { data: farmersData } = useQuery(
    ['farmers', searchTerm],
    () => farmerService.getFarmers({ search: searchTerm }),
    { refetchInterval: 300000 }
  );

  const { data: analytics } = useQuery(
    'farmer-analytics',
    farmerService.getFarmerAnalytics,
    { refetchInterval: 300000 }
  );

  // Mutations
  const registerFarmerMutation = useMutation(farmerService.registerFarmer, {
    onSuccess: () => {
      queryClient.invalidateQueries('farmers');
      setRegisterDialogOpen(false);
    }
  });

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

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'suspended': return 'error';
      default: return 'default';
    }
  };

  const getVerificationColor = (status) => {
    switch (status) {
      case 'verified': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
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
          >
            Record Procurement
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
                    {analytics?.total_farmers || 0}
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
                    {analytics?.active_contracts || 0}
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
                    {analytics?.total_procurement || 0}
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
                    {analytics?.total_payments ? formatCurrency(analytics.total_payments) : '₹0'}
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
                  {farmersData?.farmers?.map((farmer) => (
                    <TableRow key={farmer.id}>
                      <TableCell>{farmer.farmer_code}</TableCell>
                      <TableCell>{farmer.name}</TableCell>
                      <TableCell>{farmer.phone}</TableCell>
                      <TableCell>{farmer.village}</TableCell>
                      <TableCell>{farmer.total_land_area || 'N/A'} acres</TableCell>
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
                          label={farmer.status}
                          color={getStatusColor(farmer.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={farmer.verification_status}
                          color={getVerificationColor(farmer.verification_status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton
                          size="small"
                          onClick={() => setSelectedFarmer(farmer)}
                        >
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
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
            {/* Procurement list component would go here */}
          </CardContent>
        </Card>
      </TabPanel>

      {/* Contract Management Tab */}
      <TabPanel value={tabValue} index={2}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom