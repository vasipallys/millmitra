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
    inventoryService.getInventoryOverview,
    { refetchInterval: 120000 }
  );

  const { data: reorderAlerts } = useQuery(
    'reorder-alerts',
    inventoryService.getReorderAlerts,
    { refetchInterval: 300000 }
  );

  const { data: valuation } = useQuery(
    'inventory-valuation',
    inventoryService.getInventoryValuation,
    { refetchInterval: 300000 }
  );

  // Mutations
  const addStockMutation = useMutation(
    (data) => stockType === 'paddy' 
      ? inventoryService.addPaddyStock(data)
      : inventoryService.addProductStock(data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries([`${stockType}-stock`, 'inventory-overview']);
        setAddStockOpen(false);
      }
    }
  );

  const createMovementMutation = useMutation(inventoryService.createStockMovement, {
    onSuccess: () => {
      queryClient.invalidateQueries(['paddy-stock', 'product-stock', 'inventory-overview']);
      setMovementDialogOpen(false);
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
    const numAmount = Number(amount);
    if (isNaN(numAmount) || numAmount === null || numAmount === undefined) {
      return '₹0';
    }
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(numAmount);
  };

  // Transform backend data to StockCard expected format
  const transformStockData = (stock, type) => {
    if (!stock) return stock;

    if (type === 'paddy') {
      return {
        ...stock,
        product_name: stock.variety,
        current_stock: stock.remaining_quantity || stock.quantity,
        reorder_level: 100, // Default reorder level for paddy
        max_stock: (stock.quantity || 0) * 1.5, // 150% of current as max
        unit_price: stock.purchase_price,
        unit: 'kg',
        last_updated: stock.updated_at || stock.created_at,
        category: 'paddy',
        storage_location: stock.warehouse_id
      };
    } else if (type === 'product') {
      return {
        ...stock,
        current_stock: stock.quantity,
        reorder_level: stock.reorder_point || stock.minimum_stock_level || 50,
        max_stock: stock.maximum_stock_level || (stock.quantity || 0) * 2,
        unit_price: stock.market_price || stock.unit_cost,
        unit: 'kg',
        last_updated: stock.updated_at || stock.created_at,
        category: stock.product_type,
        storage_location: stock.storage_location || stock.warehouse_id
      };
    }

    return stock;
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
                    {valuation ? formatCurrency(valuation.total_valuation || valuation.total_value) : '₹0'}
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
                    {valuation ? formatCurrency(valuation.paddy_valuation || valuation.paddy_value) : '₹0'}
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
                    {valuation ? formatCurrency(valuation.product_valuation || valuation.product_value) : '₹0'}
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
                stock={transformStockData(stock, 'paddy')}
                type="paddy"
                onUpdate={() => queryClient.invalidateQueries('paddy-stock')}
                onReorder={(stock) => {
                  console.log('Reorder requested for:', stock);
                  // TODO: Implement reorder functionality
                  alert(`Reorder request for ${stock?.variety || stock?.product_name || 'Unknown Product'}`);
                }}
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
                stock={transformStockData(stock, 'product')}
                type="product"
                onUpdate={() => queryClient.invalidateQueries('product-stock')}
                onReorder={(stock) => {
                  console.log('Reorder requested for:', stock);
                  // TODO: Implement reorder functionality
                  alert(`Reorder request for ${stock?.variety || stock?.product_name || 'Unknown Product'}`);
                }}
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
        <InventoryAnalytics />
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

const AddStockDialog = ({ open, onClose, stockType, onStockTypeChange, onSubmit, loading }) => {
  const [formData, setFormData] = useState({
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

  const handleSubmit = () => {
    // Transform data based on stock type
    const submitData = { ...formData };

    if (stockType === 'product') {
      // For product stock, rename 'variety' to 'product_type'
      submitData.product_type = submitData.variety;
      delete submitData.variety;
    }

    onSubmit(submitData);
  };

  const resetForm = () => {
    setFormData({
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
  };

  useEffect(() => {
    if (!open) resetForm();
  }, [open]);

  // Reset variety when stock type changes
  useEffect(() => {
    console.log('Stock type changed to:', stockType);
    setFormData(prev => ({
      ...prev,
      variety: ''
    }));
  }, [stockType]);

  // Debug form data changes
  useEffect(() => {
    console.log('Form data updated:', formData);
  }, [formData]);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Add New Stock</DialogTitle>
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel id="stock-type-select-label">Stock Type</InputLabel>
              <Select
                labelId="stock-type-select-label"
                label="Stock Type"
                value={stockType}
                onChange={(e) => onStockTypeChange(e.target.value)}
              >
                <MenuItem value="paddy">Paddy Stock</MenuItem>
                <MenuItem value="product">Product Stock</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id={`variety-select-label-${stockType}`}>
                {stockType === 'paddy' ? 'Paddy Variety' : 'Product Type'}
              </InputLabel>
              <Select
                labelId={`variety-select-label-${stockType}`}
                id={`variety-select-${stockType}`}
                label={stockType === 'paddy' ? 'Paddy Variety' : 'Product Type'}
                value={formData.variety || ''}
                onChange={(event) => {
                  const selectedValue = event.target.value;
                  console.log('Variety selected:', selectedValue, 'Stock type:', stockType);
                  setFormData(prevData => ({
                    ...prevData,
                    variety: selectedValue
                  }));
                }}
                displayEmpty
                MenuProps={{
                  PaperProps: {
                    style: {
                      maxHeight: 300,
                      zIndex: 9999
                    }
                  }
                }}
                onClick={() => console.log('Select clicked')}
                onOpen={() => console.log('Select opened')}
                onClose={() => console.log('Select closed')}
              >
                <MenuItem value="" disabled>
                  <em>Select {stockType === 'paddy' ? 'Paddy Variety' : 'Product Type'}</em>
                </MenuItem>
                {stockType === 'paddy' ? (
                  [
                    <MenuItem key="basmati_1121" value="basmati_1121" onClick={() => console.log('Clicked: basmati_1121')}>Basmati 1121</MenuItem>,
                    <MenuItem key="pusa_basmati" value="pusa_basmati" onClick={() => console.log('Clicked: pusa_basmati')}>Pusa Basmati</MenuItem>,
                    <MenuItem key="ir64" value="ir64" onClick={() => console.log('Clicked: ir64')}>IR64</MenuItem>,
                    <MenuItem key="swarna" value="swarna" onClick={() => console.log('Clicked: swarna')}>Swarna</MenuItem>,
                    <MenuItem key="sona_masuri" value="sona_masuri" onClick={() => console.log('Clicked: sona_masuri')}>Sona Masuri</MenuItem>,
                    <MenuItem key="pr106" value="pr106" onClick={() => console.log('Clicked: pr106')}>PR106</MenuItem>,
                    <MenuItem key="pr121" value="pr121" onClick={() => console.log('Clicked: pr121')}>PR121</MenuItem>,
                    <MenuItem key="sharbati" value="sharbati" onClick={() => console.log('Clicked: sharbati')}>Sharbati</MenuItem>,
                    <MenuItem key="sugandha" value="sugandha" onClick={() => console.log('Clicked: sugandha')}>Sugandha</MenuItem>,
                    <MenuItem key="kranti" value="kranti" onClick={() => console.log('Clicked: kranti')}>Kranti</MenuItem>
                  ]
                ) : (
                  [
                    <MenuItem key="basmati_rice" value="basmati_rice" onClick={() => console.log('Clicked: basmati_rice')}>Basmati Rice</MenuItem>,
                    <MenuItem key="sona_masuri_rice" value="sona_masuri_rice" onClick={() => console.log('Clicked: sona_masuri_rice')}>Sona Masuri Rice</MenuItem>,
                    <MenuItem key="ir64_rice" value="ir64_rice" onClick={() => console.log('Clicked: ir64_rice')}>IR64 Rice</MenuItem>,
                    <MenuItem key="swarna_rice" value="swarna_rice" onClick={() => console.log('Clicked: swarna_rice')}>Swarna Rice</MenuItem>,
                    <MenuItem key="parboiled_rice" value="parboiled_rice" onClick={() => console.log('Clicked: parboiled_rice')}>Parboiled Rice</MenuItem>,
                    <MenuItem key="brown_rice" value="brown_rice" onClick={() => console.log('Clicked: brown_rice')}>Brown Rice</MenuItem>,
                    <MenuItem key="broken_rice" value="broken_rice" onClick={() => console.log('Clicked: broken_rice')}>Broken Rice</MenuItem>,
                    <MenuItem key="rice_bran" value="rice_bran" onClick={() => console.log('Clicked: rice_bran')}>Rice Bran</MenuItem>,
                    <MenuItem key="rice_husk" value="rice_husk" onClick={() => console.log('Clicked: rice_husk')}>Rice Husk</MenuItem>
                  ]
                )}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Quantity (kg)"
              type="number"
              value={formData.quantity}
              onChange={(e) => setFormData({...formData, quantity: e.target.value})}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={stockType === 'paddy' ? 'Purchase Price (₹/kg)' : 'Selling Price (₹/kg)'}
              type="number"
              value={formData.purchase_price}
              onChange={(e) => setFormData({...formData, purchase_price: e.target.value})}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel id="quality-grade-select-label">Quality Grade</InputLabel>
              <Select
                labelId="quality-grade-select-label"
                label="Quality Grade"
                value={formData.quality_grade}
                onChange={(e) => setFormData({...formData, quality_grade: e.target.value})}
              >
                <MenuItem value="A">Grade A</MenuItem>
                <MenuItem value="B">Grade B</MenuItem>
                <MenuItem value="C">Grade C</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Storage Location"
              value={formData.storage_location}
              onChange={(e) => setFormData({...formData, storage_location: e.target.value})}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Moisture Content (%)"
              type="number"
              value={formData.moisture_content}
              onChange={(e) => setFormData({...formData, moisture_content: e.target.value})}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
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