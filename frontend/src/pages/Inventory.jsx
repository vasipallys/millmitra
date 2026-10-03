import { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  Alert, LinearProgress,
  Tabs, Tab, IconButton, Tooltip, Paper
} from '@mui/material';
import {
  Add, Inventory as InventoryIcon, TrendingDown, Warning, Assessment,
  LocalShipping, Store, Analytics, Refresh
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { inventoryService } from '../services/inventoryService';
import { useToastNotifications } from '../hooks/useToastNotifications';
import { useI18n } from '../i18n/I18nContext';
import ValidationErrorDisplay, { useValidation } from '../components/common/ValidationErrorDisplay';
import StockCard from '../components/StockCard';
import ReorderAlerts from '../components/ReorderAlerts';
import InventoryAnalytics from '../components/InventoryAnalytics';
import StockMovementDialog from '../components/StockMovementDialog';
import { PageHeader, PageShell, QueryErrorAlert } from '../components/common/PageChrome';
import LookupSelect from '../components/common/LookupSelect';

const normalizeStock = (stock, type) => ({
  ...stock,
  type,
  product_name: stock.product_name || stock.variety || 'Stock',
  current_stock: stock.remaining_quantity ?? stock.quantity ?? 0,
  unit: stock.unit || 'kg',
  unit_price: stock.purchase_price || stock.market_price || stock.unit_cost || 0,
  storage_location: stock.storage_location || stock.warehouse_id || '',
  last_updated: stock.updated_at || stock.created_at || stock.purchase_date,
  category: stock.product_type || stock.category || type,
  reorder_level: stock.reorder_level || 100,
  max_stock: stock.max_stock || 10000,
});

const Inventory = () => {
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState(0);
  const [addStockOpen, setAddStockOpen] = useState(false);
  const [stockType, setStockType] = useState('paddy');
  const [movementDialogOpen, setMovementDialogOpen] = useState(false);
  const [movementStock, setMovementStock] = useState(null);
  const [movementType, setMovementType] = useState('in');
  const [selectedStock, setSelectedStock] = useState(null);
  const [stockDetailOpen, setStockDetailOpen] = useState(false);
  const [stockEditOpen, setStockEditOpen] = useState(false);
  const [editForm, setEditForm] = useState({ quantity: '', storage_location: '' });
  const [stockActionError, setStockActionError] = useState('');
  const queryClient = useQueryClient();
  const toast = useToastNotifications();

  // Fetch inventory data
  const { data: paddyStock, isLoading: paddyLoading, isError: paddyError, error: paddyErr, refetch: refetchPaddy } = useQuery(
    'paddy-stock',
    () => inventoryService.getPaddyStock(),
    { refetchInterval: 60000 }
  );

  const { data: productStock, isLoading: productLoading, isError: productError, error: productErr, refetch: refetchProduct } = useQuery(
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
        const message = error.userMessage || error.response?.data?.message || error.message;
        setStockActionError(message);
        toast.inventory.error('Add Stock', message);
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
      setMovementStock(null);
      toast.inventory.movementRecorded('stock', 'inventory', '');
    },
    onError: (error) => {
      const message = error.userMessage || error.response?.data?.message || error.message;
      setStockActionError(message);
      toast.inventory.error('Stock Movement', message);
    }
  });

  const updateStockMutation = useMutation(
    ({ stock, data }) => (
      stock.type === 'paddy'
        ? inventoryService.updatePaddyStock(stock.id, data)
        : inventoryService.updateProductStock(stock.id, data)
    ),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('paddy-stock');
        queryClient.invalidateQueries('product-stock');
        queryClient.invalidateQueries('inventory-overview');
        setStockEditOpen(false);
        setStockActionError('');
      },
      onError: (error) => {
        setStockActionError(error.userMessage || error.response?.data?.message || error.message);
      }
    }
  );

  const handleAddStock = (stockData) => {
    setStockActionError('');
    addStockMutation.mutate(stockData);
  };

  const handleCreateMovement = (movementData) => {
    setStockActionError('');
    createMovementMutation.mutate(movementData);
  };

  const stockCardHandlers = (type) => ({
    onAddStock: (stock) => {
      setStockType(type);
      setAddStockOpen(true);
      setStockActionError('');
    },
    onRemoveStock: (stock) => {
      setMovementStock(normalizeStock(stock, type));
      setMovementType('out');
      setMovementDialogOpen(true);
      setStockActionError('');
    },
    onEditStock: (stock) => {
      const normalized = normalizeStock(stock, type);
      setSelectedStock(normalized);
      setEditForm({
        quantity: normalized.current_stock,
        storage_location: normalized.storage_location,
      });
      setStockEditOpen(true);
      setStockActionError('');
    },
    onViewDetails: (stock) => {
      setSelectedStock(normalizeStock(stock, type));
      setStockDetailOpen(true);
    },
    onReorder: (stock) => {
      setStockType(type);
      setAddStockOpen(true);
      setStockActionError('');
    },
  });

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
    <PageShell>
      <PageHeader
        title={t('inventoryTitle')}
        subtitle={t('inventorySubtitle')}
        actions={
          <>
            <Button
              variant="outlined"
              startIcon={<LocalShipping />}
              onClick={() => {
                setMovementStock(null);
                setMovementType('in');
                setStockActionError('');
                setMovementDialogOpen(true);
              }}
            >
              Stock Movement
            </Button>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setAddStockOpen(true)}
            >
              {t('addStock')}
            </Button>
          </>
        }
      />
      {paddyError && <QueryErrorAlert error={paddyErr} onRetry={refetchPaddy} entity="paddy stock" />}
      {productError && <QueryErrorAlert error={productErr} onRetry={refetchProduct} entity="product stock" />}
      {stockActionError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setStockActionError('')}>
          {stockActionError}
        </Alert>
      )}
      {(paddyLoading || productLoading) && <LinearProgress sx={{ mb: 2 }} />}

      {/* Reorder Alerts */}
      {reorderAlerts?.alerts?.length > 0 && (
        <ReorderAlerts
          sourceAlerts={reorderAlerts.alerts}
          onReorder={async () => {
            setStockType('product');
            setAddStockOpen(true);
          }}
        />
      )}

      {/* Overview Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
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
        <Grid item xs={12} sm={6} md={3}>
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
        <Grid item xs={12} sm={6} md={3}>
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
        <Grid item xs={12} sm={6} md={3}>
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
          <Tab label={t('paddyStock')} />
          <Tab label={t('productStock')} />
          <Tab label={t('stockMovements')} />
          <Tab label={t('analytics')} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          {paddyStock?.stocks?.map((stock) => (
            <Grid item xs={12} md={6} lg={4} key={stock.id}>
              <StockCard
                stock={normalizeStock(stock, 'paddy')}
                type="paddy"
                onUpdate={() => queryClient.invalidateQueries('paddy-stock')}
                {...stockCardHandlers('paddy')}
              />
            </Grid>
          ))}
          {paddyStock?.stocks?.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <InventoryIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  {t('noPaddyLots')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('noPaddyLotsHint')}
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
                stock={normalizeStock(stock, 'product')}
                type="product"
                onUpdate={() => queryClient.invalidateQueries('product-stock')}
                {...stockCardHandlers('product')}
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
        error={addStockMutation.isError ? stockActionError : ''}
      />

      {/* Stock Movement Dialog */}
      <StockMovementDialog
        open={movementDialogOpen}
        onClose={() => setMovementDialogOpen(false)}
        onSubmit={handleCreateMovement}
        loading={createMovementMutation.isLoading}
        stockItem={movementStock}
        movementType={movementType}
      />

      <Dialog open={stockDetailOpen} onClose={() => setStockDetailOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedStock?.product_name || t('stockDetails')}</DialogTitle>
        <DialogContent>
          {selectedStock && (
            <Box sx={{ pt: 1 }}>
              <Typography>Quantity: {selectedStock.current_stock} {selectedStock.unit}</Typography>
              <Typography>{t('location')}: {selectedStock.storage_location || '—'}</Typography>
              <Typography>{t('grade')}: {selectedStock.quality_grade || selectedStock.grade || '—'}</Typography>
              <Typography>{t('unitPriceSlash', { price: selectedStock.unit_price || 0 })}</Typography>
              <Typography>{t('lotId')}: {selectedStock.id}</Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStockDetailOpen(false)}>{t('close')}</Button>
          <Button
            variant="contained"
            onClick={() => {
              setStockDetailOpen(false);
              if (selectedStock) {
                setEditForm({
                  quantity: selectedStock.current_stock,
                  storage_location: selectedStock.storage_location,
                });
                setStockEditOpen(true);
              }
            }}
          >
            {t('edit')}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={stockEditOpen} onClose={() => !updateStockMutation.isLoading && setStockEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('editNamed', { name: selectedStock?.product_name || t('stockWord') })}</DialogTitle>
        <DialogContent>
          {stockActionError && stockEditOpen && (
            <Alert severity="error" sx={{ mt: 1 }}>{stockActionError}</Alert>
          )}
          <TextField
            fullWidth
            margin="normal"
            label={t('quantityKg')}
            type="number"
            value={editForm.quantity}
            onChange={(e) => setEditForm((prev) => ({ ...prev, quantity: e.target.value }))}
          />
          <TextField
            fullWidth
            margin="normal"
            label={t('storageLocation')}
            value={editForm.storage_location}
            onChange={(e) => setEditForm((prev) => ({ ...prev, storage_location: e.target.value }))}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStockEditOpen(false)} disabled={updateStockMutation.isLoading}>{t('cancel')}</Button>
          <Button
            variant="contained"
            disabled={updateStockMutation.isLoading}
            onClick={() => {
              const quantity = parseFloat(editForm.quantity);
              if (!Number.isFinite(quantity) || quantity < 0) {
                setStockActionError(t('qtyMustBeNonneg'));
                return;
              }
              setStockActionError('');
              updateStockMutation.mutate({
                stock: selectedStock,
                data: {
                  quantity,
                  storage_location: editForm.storage_location,
                },
              });
            }}
          >
            {updateStockMutation.isLoading ? t('saving') : t('save')}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
};

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

const AddStockDialog = ({ open, onClose, stockType, onStockTypeChange, onSubmit, loading, error }) => {
  const { t } = useI18n();
  const [formData, setFormData] = useState(emptyStockForm);
  const validation = useValidation();
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
      <DialogTitle>{t('addNewStock')}</DialogTitle>
      <DialogContent sx={{ overflow: 'visible' }}>
        {error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}
        <ValidationErrorDisplay
          errors={validation.errors}
          warnings={validation.warnings}
          title={t('stockEntryValidation')}
          onClose={() => validation.clearAll()}
        />

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <LookupSelect
              group="stock_type"
              label={t('stockType')}
              value={stockType}
              onChange={(e) => handleStockTypeChange(e.target.value)}
              MenuProps={SELECT_MENU_PROPS}
              includeValue={stockType}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <LookupSelect
              group={stockType === 'paddy' ? 'paddy_variety' : 'product_type'}
              label={stockType === 'paddy' ? t('paddyVariety') : t('productType')}
              value={formData.variety}
              onChange={(e) => updateField('variety', e.target.value)}
              MenuProps={SELECT_MENU_PROPS}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              required
              label={t('quantityKg')}
              type="number"
              inputProps={{ min: 0, step: 'any' }}
              value={formData.quantity}
              onChange={(e) => updateField('quantity', e.target.value)}
              helperText={t('qtyHelper')}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              required
              label={stockType === 'paddy' ? t('purchasePrice') : t('sellingPrice')}
              type="number"
              inputProps={{ min: 0, step: 'any' }}
              value={formData.purchase_price}
              onChange={(e) => updateField('purchase_price', e.target.value)}
              helperText={t('priceHelper')}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <LookupSelect
              group="quality_grade"
              label={t('qualityGrade')}
              value={formData.quality_grade}
              onChange={(e) => updateField('quality_grade', e.target.value)}
              MenuProps={SELECT_MENU_PROPS}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              required
              label={t('storageLocation')}
              value={formData.storage_location}
              onChange={(e) => updateField('storage_location', e.target.value)}
              helperText={t('locationHelper')}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label={t('moisture')}
              type="number"
              inputProps={{ min: 0, max: 100, step: 'any' }}
              value={formData.moisture_content}
              onChange={(e) => updateField('moisture_content', e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label={t('notes')}
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => updateField('notes', e.target.value)}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('cancel')}</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? t('saving') : (stockType === 'paddy' ? t('savePaddyLot') : t('saveProductLot'))}
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