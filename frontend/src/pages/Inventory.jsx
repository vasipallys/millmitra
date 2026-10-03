import { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Select, MenuItem, FormControl, InputLabel, Alert, LinearProgress,
  Tabs, Tab, IconButton, Tooltip, Paper
} from '@mui/material';
import {
  Add, Inventory as InventoryIcon, TrendingDown, Warning, Assessment,
  LocalShipping, Store, Analytics, Refresh
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { inventoryService } from '../services/inventoryService';
import { useToastNotifications } from '../hooks/useToastNotifications';
import ValidationErrorDisplay, { useValidation } from '../components/common/ValidationErrorDisplay';
import StockCard from '../components/StockCard';
import ReorderAlerts from '../components/ReorderAlerts';
import InventoryAnalytics from '../components/InventoryAnalytics';
import StockMovementDialog from '../components/StockMovementDialog';

const Inventory = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [addStockOpen, setAddStockOpen] = useState(false);
  const [stockType, setStockType] = useState('paddy');
  const [movementDialogOpen, setMovementDialogOpen] = useState(false);
  const queryClient = useQueryClient();
  const toast = useToastNotifications();

  // Fetch inventory data
  const { data: paddyStock, isLoading: paddyLoading } = useQuery(
    'paddy-stock',
    () => inventoryService.getPaddyStock(),
    { refetchInterval: 60000 }
  );

  const { data: productStock, isLoading: productLoading } = useQuery(
    'product-stock',
    () => inventoryService.getProductStock(),
    { refetchInterval: 60000 }
  );

  const { data: overview } = useQuery(
    'inventory-overview',
    () => inventoryService.getInventoryOverview(),
    { refetchInterval: 120000 }
  );

  const { data: reorderAlerts } = useQuery(
    'reorder-alerts',
    () => inventoryService.getReorderAlerts(),
    { refetchInterval: 300000 }
  );

  const { data: valuation } = useQuery(
    'inventory-valuation',
    () => inventoryService.getInventoryValuation(),
    { refetchInterval: 300000 }
  );

  // Mutations
  const addStockMutation = useMutation(
    (data) => {
      console.log('Adding stock with data:', data);
      return stockType === 'paddy'
        ? inventoryService.addPaddyStock(data)
        : inventoryService.addProductStock(data);
    },
    {
      onSuccess: (result, variables) => {
        console.log('Stock added successfully:', result);
        queryClient.invalidateQueries('paddy-stock');
        queryClient.invalidateQueries('product-stock');
        queryClient.invalidateQueries('inventory-overview');
        setAddStockOpen(false);

        // Show success toast
        const itemName = variables.variety || variables.product_name || 'Item';
        const quantity = variables.quantity || 0;
        toast.inventory.stockAdded(itemName, quantity);
      },
      onError: (error) => {
        console.error('Failed to add stock:', error);
        toast.inventory.error('Add Stock', error.response?.data?.message || error.message);
      }
    }
  );

  const createMovementMutation = useMutation(inventoryService.createStockMovement, {
    onSuccess: () => {
      queryClient.invalidateQueries('paddy-stock');
      queryClient.invalidateQueries('product-stock');
      queryClient.invalidateQueries('inventory-overview');
      queryClient.invalidateQueries('stock-movements');
      setMovementDialogOpen(false);
      toast.inventory.movementRecorded('stock', 'inventory', '');
    },
    onError: (error) => {
      toast.inventory.error('Stock Movement', error.response?.data?.message || error.message);
    }
  });

  const handleAddStock = (stockData) => {
    addStockMutation.mutate(stockData);
  };

  const handleCreateMovement = (movementData) => {
    createMovementMutation.mutate(movementData);
  };

  const getStockStatusColor = (quantity, threshold = 100) => {
    if (quantity <= threshold * 0.2) return 'error';
    if (quantity <= threshold * 0.5) return 'warning';
    return 'success';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Inventory Management
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<LocalShipping />}
            onClick={() => setMovementDialogOpen(true)}
            sx={{ mr: 2 }}
          >
            Stock Movement
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddStockOpen(true)}
          >
            Add Stock
          </Button>
        </Box>
      </Box>

      {/* Reorder Alerts */}
      {reorderAlerts?.alerts?.length > 0 && (
        <ReorderAlerts alerts={reorderAlerts.alerts} />
      )}

      {/* Overview Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Valuation
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {valuation ? formatCurrency(valuation.total_valuation) : '₹0'}
                  </Typography>
                </Box>
                <Store color="primary" sx={{ fontSize: 40 }} />
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
                    Paddy Stock Value
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {valuation ? formatCurrency(valuation.paddy_valuation) : '₹0'}
                  </Typography>
                </Box>
                <InventoryIcon color="success" sx={{ fontSize: 40 }} />
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
                    Product Stock Value
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {valuation ? formatCurrency(valuation.product_valuation) : '₹0'}
                  </Typography>
                </Box>
                <Store color="info" sx={{ fontSize: 40 }} />
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
                    Low Stock Items
                  </Typography>
                  <Typography variant="h5" fontWeight="bold" color="warning.main">
                    {reorderAlerts?.alerts?.length || 0}
                  </Typography>
                </Box>
                <Warning color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Paddy Stock" />
          <Tab label="Product Stock" />
          <Tab label="Stock Movements" />
          <Tab label="Analytics" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {paddyStock?.stocks?.map((stock) => (
            <Grid item xs={12} md={6} lg={4} key={stock.id}>
              <StockCard
                stock={stock}
                type="paddy"
                onUpdate={() => queryClient.invalidateQueries('paddy-stock')}
              />
            </Grid>
          ))}
          {paddyStock?.stocks?.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <InventoryIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  No paddy stock available
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => {
                    setStockType('paddy');
                    setAddStockOpen(true);
                  }}
                  sx={{ mt: 2 }}
                >
                  Add Paddy Stock
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          {productStock?.stocks?.map((stock) => (
            <Grid item xs={12} md={6} lg={4} key={stock.id}>
              <StockCard
                stock={stock}
                type="product"
                onUpdate={() => queryClient.invalidateQueries('product-stock')}
              />
            </Grid>
          ))}
          {productStock?.stocks?.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Store sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  No product stock available
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => {
                    setStockType('product');
                    setAddStockOpen(true);
                  }}
                  sx={{ mt: 2 }}
                >
                  Add Product Stock
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {activeTab === 2 && (
        <StockMovementsTab />
      )}

      {activeTab === 3 && (
        <InventoryAnalytics data={overview} />
      )}

      {/* Add Stock Dialog */}
      <AddStockDialog
        open={addStockOpen}
        onClose={() => setAddStockOpen(false)}
        stockType={stockType}
        onStockTypeChange={setStockType}
        onSubmit={handleAddStock}
        loading={addStockMutation.isLoading}
      />

      {/* Stock Movement Dialog */}
      <StockMovementDialog
        open={movementDialogOpen}
        onClose={() => setMovementDialogOpen(false)}
        onSubmit={handleCreateMovement}
        loading={createMovementMutation.isLoading}
      />
    </Box>
  );
};

const PADDY_VARIETIES = [
  { value: 'basmati', label: 'Basmati' },
  { value: 'jasmine', label: 'Jasmine' },
  { value: 'long_grain', label: 'Long Grain' },
  { value: 'short_grain', label: 'Short Grain' },
];

const PRODUCT_TYPES = [
  { value: 'basmati_rice', label: 'Basmati Rice' },
  { value: 'jasmine_rice', label: 'Jasmine Rice' },
  { value: 'long_grain_rice', label: 'Long Grain Rice' },
  { value: 'short_grain_rice', label: 'Short Grain Rice' },
];

const QUALITY_GRADES = [
  { value: 'A', label: 'Grade A' },
  { value: 'B', label: 'Grade B' },
  { value: 'C', label: 'Grade C' },
];

const SELECT_MENU_PROPS = {
  disablePortal: true,
  disableAutoFocusItem: true,
  PaperProps: { sx: { maxHeight: 240 } },
};

const emptyStockForm = () => ({
  variety: '',
  quantity: '',
  purchase_price: '',
  quality_grade: 'A',
  moisture_content: '',
  storage_location: '',
  supplier_id: '',
  harvest_date: '',
  expiry_date: '',
  notes: ''
});

const AddStockDialog = ({ open, onClose, stockType, onStockTypeChange, onSubmit, loading }) => {
  const [formData, setFormData] = useState(emptyStockForm);
  const validation = useValidation();
  const varietyOptions = stockType === 'paddy' ? PADDY_VARIETIES : PRODUCT_TYPES;

  const validateField = (fieldName, value) => {
    switch (fieldName) {
      case 'variety':
        if (!value) {
          validation.addError('Variety', `${stockType === 'paddy' ? 'Paddy variety' : 'Product type'} is required`, 'Please select a variety from the dropdown');
        } else {
          validation.removeError('Variety');
        }
        break;
      case 'quantity':
        if (value === '' || value === null || Number(value) <= 0) {
          validation.addError('Quantity', 'Quantity must be greater than 0', 'Enter the quantity in kilograms (kg)');
        } else {
          validation.removeError('Quantity');
          if (Number(value) > 100000) {
            validation.addWarning('Quantity', 'Large quantity detected', 'Please verify this is the correct amount');
          } else {
            validation.removeWarning('Quantity');
          }
        }
        break;
      case 'purchase_price':
        if (value === '' || value === null || Number(value) <= 0) {
          validation.addError('Price', `${stockType === 'paddy' ? 'Purchase price' : 'Selling price'} must be greater than 0`, 'Enter the price per kilogram in rupees');
        } else {
          validation.removeError('Price');
          if (Number(value) > 1000) {
            validation.addWarning('Price', 'High price detected', 'Please verify this is the correct price per kg');
          } else {
            validation.removeWarning('Price');
          }
        }
        break;
      case 'storage_location':
        if (!value || String(value).trim().length < 2) {
          validation.addError('Storage Location', 'Storage location is required', 'Enter the warehouse or storage area name');
        } else {
          validation.removeError('Storage Location');
        }
        break;
      case 'moisture_content':
        if (value !== '' && value !== null && (Number(value) < 0 || Number(value) > 100)) {
          validation.addError('Moisture Content', 'Moisture content must be between 0 and 100%', 'Enter a valid moisture percentage');
        } else {
          validation.removeError('Moisture Content');
          if (stockType === 'paddy' && value !== '' && Number(value) > 14) {
            validation.addWarning('Moisture Content', 'High moisture content detected', 'Moisture above 14% may require additional drying');
          } else {
            validation.removeWarning('Moisture Content');
          }
        }
        break;
      default:
        break;
    }
  };

  const updateField = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    validateField(field, value);
  };

  const handleStockTypeChange = (nextType) => {
    onStockTypeChange(nextType);
    setFormData((prev) => ({ ...prev, variety: '' }));
    validation.removeError('Variety');
  };

  const handleSubmit = () => {
    const next = formData;
    validateField('variety', next.variety);
    validateField('quantity', next.quantity);
    validateField('purchase_price', next.purchase_price);
    validateField('storage_location', next.storage_location);
    validateField('moisture_content', next.moisture_content);

    const quantityOk = next.quantity !== '' && Number(next.quantity) > 0;
    const priceOk = next.purchase_price !== '' && Number(next.purchase_price) > 0;
    const locationOk = next.storage_location && String(next.storage_location).trim().length >= 2;
    const moistureOk = next.moisture_content === '' || next.moisture_content === null
      || (Number(next.moisture_content) >= 0 && Number(next.moisture_content) <= 100);
    if (!next.variety || !quantityOk || !priceOk || !locationOk || !moistureOk) {
      return;
    }

    onSubmit(next);
  };

  useEffect(() => {
    if (!open) {
      setFormData(emptyStockForm());
      validation.clearAll();
    }
  }, [open]);

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      disableRestoreFocus
    >
      <DialogTitle>Add New Stock</DialogTitle>
      <DialogContent sx={{ overflow: 'visible' }}>
        <ValidationErrorDisplay
          errors={validation.errors}
          warnings={validation.warnings}
          title="Stock Entry Validation"
          onClose={() => validation.clearAll()}
        />

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel id="stock-type-label">Stock Type</InputLabel>
              <Select
                labelId="stock-type-label"
                label="Stock Type"
                value={stockType}
                onChange={(e) => handleStockTypeChange(e.target.value)}
                MenuProps={SELECT_MENU_PROPS}
              >
                <MenuItem value="paddy">Paddy Stock</MenuItem>
                <MenuItem value="product">Product Stock</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="stock-variety-label">
                {stockType === 'paddy' ? 'Paddy Variety' : 'Product Type'}
              </InputLabel>
              <Select
                labelId="stock-variety-label"
                label={stockType === 'paddy' ? 'Paddy Variety' : 'Product Type'}
                value={formData.variety}
                onChange={(e) => updateField('variety', e.target.value)}
                MenuProps={SELECT_MENU_PROPS}
              >
                {varietyOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Quantity (kg)"
              type="number"
              inputProps={{ min: 0, step: 'any' }}
              value={formData.quantity}
              onChange={(e) => updateField('quantity', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={stockType === 'paddy' ? 'Purchase Price (₹/kg)' : 'Selling Price (₹/kg)'}
              type="number"
              inputProps={{ min: 0, step: 'any' }}
              value={formData.purchase_price}
              onChange={(e) => updateField('purchase_price', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="quality-grade-label">Quality Grade</InputLabel>
              <Select
                labelId="quality-grade-label"
                label="Quality Grade"
                value={formData.quality_grade}
                onChange={(e) => updateField('quality_grade', e.target.value)}
                MenuProps={SELECT_MENU_PROPS}
              >
                {QUALITY_GRADES.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Storage Location"
              value={formData.storage_location}
              onChange={(e) => updateField('storage_location', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Moisture Content (%)"
              type="number"
              inputProps={{ min: 0, max: 100, step: 'any' }}
              value={formData.moisture_content}
              onChange={(e) => updateField('moisture_content', e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => updateField('notes', e.target.value)}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? 'Adding...' : 'Add Stock'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const StockMovementsTab = () => {
  const { data: movements, isLoading } = useQuery(
    'stock-movements',
    () => inventoryService.getStockMovements(),
    { refetchInterval: 60000 }
  );

  if (isLoading) return <LinearProgress />;

  return (
    <Card>
      <CardContent>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Reference</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Value</TableCell>
                <TableCell>Notes</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(!movements?.movements || movements.movements.length === 0) && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography color="text.secondary" sx={{ py: 3 }}>
                      No stock movements recorded yet
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
              {movements?.movements?.map((movement) => (
                <TableRow key={movement.id}>
                  <TableCell>
                    {new Date(movement.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={movement.movement_type}
                      color={movement.movement_type === 'in' ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{movement.reference_type}</TableCell>
                  <TableCell>{movement.quantity} kg</TableCell>
                  <TableCell>
                    {movement.total_value ? `₹${movement.total_value.toFixed(2)}` : '-'}
                  </TableCell>
                  <TableCell>{movement.notes || '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
};

export default Inventory;