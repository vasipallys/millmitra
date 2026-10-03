import { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  FormControl,
  FormControlLabel,
  Grid,
  FormHelperText,
  InputLabel,
  MenuItem,
  Radio,
  RadioGroup,
  Select,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
} from '@mui/material';
import { useQuery } from 'react-query';
import { farmerService } from '../services/farmerService';
import { inventoryService } from '../services/inventoryService';
import { productionService } from '../services/productionService';
import { salesAPI } from '../services/api';
import { financeService } from '../services/financeService';
import { getApiErrorMessage } from '../utils/apiError';
import { PageHeader, PageLoading, PageShell } from '../components/common/PageChrome';
import { useI18n } from '../i18n/I18nContext';
import {
  isOpenBatch,
  isPlannedBatch,
  isUnpaidInvoice,
  remainingPaddyKg,
  suggestMillStep,
  unwrapList,
  productStockKg,
} from '../utils/millFlowSuggestion';

const STEP_KEYS = ['stepReceive', 'stepBatch', 'stepQuality', 'stepSell', 'stepPay'];

const WALK_IN = 'walk_in';
const NONE = 'none';

const SELECT_MENU_PROPS = {
  disablePortal: false,
  disableAutoFocusItem: true,
  PaperProps: { sx: { maxHeight: 280 } },
};

const PADDY_VARIETIES = [
  { value: 'basmati', label: 'Basmati' },
  { value: 'jasmine', label: 'Jasmine' },
  { value: 'long_grain', label: 'Long Grain' },
  { value: 'short_grain', label: 'Short Grain' },
];

const today = () => new Date().toISOString().slice(0, 10);

const emptyContext = () => ({
  farmer: null,
  paddy: null,
  batch: null,
  quality: null,
  customer: null,
  order: null,
  invoice: null,
  payment: null,
});

function lotRemaining(lot) {
  return Number(lot?.remaining_quantity ?? lot?.quantity ?? 0) || 0;
}

function receiveMissingFields({ farmerMode, newFarmer, paddyForm }) {
  const missing = [];
  if (!paddyForm.variety) missing.push('variety');
  if (!Number.isFinite(Number(paddyForm.quantity)) || Number(paddyForm.quantity) <= 0) {
    missing.push('quantity (kg > 0)');
  }
  if (!Number.isFinite(Number(paddyForm.purchase_price)) || Number(paddyForm.purchase_price) <= 0) {
    missing.push('price (₹/kg > 0)');
  }
  if (!String(paddyForm.storage_location || '').trim()) missing.push('storage location');
  if (farmerMode === 'new') {
    if (!newFarmer.name.trim()) missing.push('farmer name');
    if (!newFarmer.phone.trim()) missing.push('farmer phone');
    if (!newFarmer.village.trim()) missing.push('village');
    if (!newFarmer.district.trim()) missing.push('district');
    if (!newFarmer.state.trim()) missing.push('state');
  }
  return missing;
}

const MillFlow = () => {
  const { t } = useI18n();
  const stepLabels = STEP_KEYS.map((key) => t(key));
  const [phase, setPhase] = useState('home');
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [context, setContext] = useState(emptyContext);
  const [farmerMode, setFarmerMode] = useState('existing');
  const [farmerId, setFarmerId] = useState(WALK_IN);
  const [newFarmer, setNewFarmer] = useState({
    name: '', phone: '', village: '', district: '', state: '',
  });
  const [paddyForm, setPaddyForm] = useState({
    variety: 'basmati', quantity: '', purchase_price: '', storage_location: '', moisture_content: '',
  });
  const [batchForm, setBatchForm] = useState({
    paddy_stock_id: NONE, input_quantity: '', quality_grade: 'A',
  });
  const [qualityForm, setQualityForm] = useState({
    moisture_content: '', broken_percentage: '', foreign_matter: '',
  });
  const [completeForm, setCompleteForm] = useState({
    rice_output: '', broken_rice_output: '', bran_output: '', husk_output: '',
  });
  const [customerMode, setCustomerMode] = useState('existing');
  const [customerId, setCustomerId] = useState(NONE);
  const [newCustomer, setNewCustomer] = useState({ name: '', phone: '' });
  const [orderForm, setOrderForm] = useState({
    description: 'Basmati Rice', quantity: '', unit_price: '', order_date: today(),
  });
  const [invoiceForm, setInvoiceForm] = useState({
    description: 'Basmati Rice', quantity: '', unit_price: '',
  });
  const [paymentForm, setPaymentForm] = useState({
    amount: '', payment_method: 'cash', payment_date: today(),
  });

  const farmersQuery = useQuery('mill-flow-farmers', () => farmerService.getFarmers({}), { retry: false });
  const paddyQuery = useQuery('mill-flow-paddy', () => inventoryService.getPaddyStock(), { retry: false });
  const productQuery = useQuery('mill-flow-products', () => inventoryService.getProductStock(), { retry: false });
  const batchesQuery = useQuery('mill-flow-batches', () => productionService.getBatches(), { retry: false });
  const invoicesQuery = useQuery('mill-flow-invoices', () => financeService.getInvoices({ limit: 50 }), { retry: false });
  const customersQuery = useQuery(
    'mill-flow-customers',
    async () => (await salesAPI.getCustomers({ per_page: 100 })).data,
    { retry: false }
  );

  const farmers = unwrapList(farmersQuery.data, ['farmers', 'items']);
  const paddyLots = unwrapList(paddyQuery.data, ['stock', 'paddy_stock', 'items']);
  const products = unwrapList(productQuery.data, ['stock', 'products', 'items']);
  const batches = unwrapList(batchesQuery.data, ['batches', 'items']);
  const invoices = unwrapList(invoicesQuery.data, ['invoices', 'items']);
  const customers = unwrapList(customersQuery.data, ['customers', 'items']);

  const snapshotLoading = farmersQuery.isLoading || paddyQuery.isLoading || batchesQuery.isLoading
    || productQuery.isLoading || invoicesQuery.isLoading;

  const suggestion = useMemo(
    () => suggestMillStep({ paddyLots, batches, products, invoices }),
    [paddyLots, batches, products, invoices]
  );

  const availableLots = paddyLots.filter((lot) => lotRemaining(lot) > 0);
  const unpaidInvoices = invoices.filter(isUnpaidInvoice);
  const openBatch = batches.find(isOpenBatch) || context.batch;
  const plannedBatch = batches.find(isPlannedBatch);

  useEffect(() => {
    if (context.paddy && (!batchForm.paddy_stock_id || batchForm.paddy_stock_id === NONE)) {
      setBatchForm((prev) => ({
        ...prev,
        paddy_stock_id: String(context.paddy.id || prev.paddy_stock_id),
        input_quantity: prev.input_quantity || String(lotRemaining(context.paddy) || paddyForm.quantity || ''),
      }));
    }
  }, [context.paddy, batchForm.paddy_stock_id, paddyForm.quantity]);

  useEffect(() => {
    const variety = context.paddy?.variety || context.batch?.paddy_variety || paddyForm.variety;
    const varietyLabel = PADDY_VARIETIES.find((item) => item.value === variety)?.label || variety || 'Basmati';
    const description = `${String(varietyLabel).replace(/ rice$/i, '')} Rice`;
    setOrderForm((prev) => {
      if (prev.description && prev.quantity) return prev;
      return {
        ...prev,
        description: prev.description || description,
        quantity: prev.quantity || completeForm.rice_output || prev.quantity,
      };
    });
    setInvoiceForm((prev) => {
      if (prev.description && prev.quantity && prev.unit_price) return prev;
      return {
        ...prev,
        description: prev.description || description,
        quantity: prev.quantity || completeForm.rice_output || prev.quantity,
      };
    });
  }, [context.paddy, context.batch, paddyForm.variety, completeForm.rice_output]);

  const refreshLists = async () => {
    await Promise.all([
      farmersQuery.refetch(),
      paddyQuery.refetch(),
      productQuery.refetch(),
      batchesQuery.refetch(),
      invoicesQuery.refetch(),
      customersQuery.refetch(),
    ]);
  };

  const beginWizard = (step = suggestion.step) => {
    setError('');
    setActiveStep(step);
    setPhase('wizard');
    if (step >= 1 && availableLots[0] && !context.paddy) {
      const lot = availableLots[0];
      setContext((prev) => ({ ...prev, paddy: lot }));
      setBatchForm((prev) => ({
        ...prev,
        paddy_stock_id: String(lot.id),
        input_quantity: String(lotRemaining(lot)),
      }));
    }
    if (step >= 2 && openBatch) {
      setContext((prev) => ({ ...prev, batch: openBatch }));
    } else if (step === 1 && plannedBatch) {
      setContext((prev) => ({ ...prev, batch: plannedBatch }));
    }
    if (step === 4 && unpaidInvoices[0]) {
      setContext((prev) => ({ ...prev, invoice: unpaidInvoices[0] }));
      setPaymentForm((prev) => ({
        ...prev,
        amount: String(unpaidInvoices[0].total_amount || unpaidInvoices[0].outstanding_amount || ''),
      }));
    }
    if (customers[0] && (!customerId || customerId === NONE)) {
      setCustomerId(String(customers[0].id));
    }
  };

  const goBack = () => {
    setError('');
    if (activeStep === 0) {
      setPhase('home');
      return;
    }
    setActiveStep((step) => step - 1);
  };

  const runStep = async () => {
    setError('');
    setBusy(true);
    try {
      if (activeStep === 0) await savePaddy();
      else if (activeStep === 1) await saveBatch();
      else if (activeStep === 2) await saveQualityAndComplete();
      else if (activeStep === 3) await saveSale();
      else if (activeStep === 4) await saveInvoiceAndPay();
      await refreshLists();
      if (activeStep < STEP_KEYS.length - 1) {
        setActiveStep((step) => step + 1);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not save this step. Fix the fields and try again.'));
    } finally {
      setBusy(false);
    }
  };

  const savePaddy = async () => {
    const missing = receiveMissingFields({ farmerMode, newFarmer, paddyForm });
    if (missing.length) {
      throw new Error(`Fill required fields: ${missing.join(', ')}`);
    }
    const quantity = Number(paddyForm.quantity);
    const price = Number(paddyForm.purchase_price);

    let farmer = null;
    if (farmerMode === 'new') {
      const created = await farmerService.registerFarmer(newFarmer);
      farmer = created.farmer || created;
    } else if (farmerId && farmerId !== WALK_IN && farmerId !== NONE) {
      farmer = farmers.find((item) => String(item.id) === String(farmerId)) || { id: Number(farmerId) };
    }

    const payload = {
      variety: paddyForm.variety,
      quantity,
      purchase_price: price,
      storage_location: paddyForm.storage_location.trim(),
      moisture_content: paddyForm.moisture_content === '' ? undefined : Number(paddyForm.moisture_content),
    };
    if (farmer?.id) payload.farmer_id = farmer.id;

    const stock = await inventoryService.addPaddyStock(payload);
    const lot = stock.stock || stock.paddy || stock;
    setContext((prev) => ({ ...prev, farmer, paddy: lot }));
    setBatchForm((prev) => ({
      ...prev,
      paddy_stock_id: String(lot.id || prev.paddy_stock_id),
      input_quantity: String(quantity),
    }));
  };

  const saveBatch = async () => {
    if (context.batch && isOpenBatch(context.batch)) return;
    if (context.batch && isPlannedBatch(context.batch)) {
      const started = await productionService.startBatch(context.batch.id);
      setContext((prev) => ({ ...prev, batch: started.batch || started }));
      return;
    }
    const quantity = Number(batchForm.input_quantity);
    if (!batchForm.paddy_stock_id || batchForm.paddy_stock_id === NONE) throw new Error('Select a paddy lot');
    if (!Number.isFinite(quantity) || quantity <= 0) throw new Error('Batch quantity must be greater than 0');
    const lot = availableLots.find((item) => String(item.id) === String(batchForm.paddy_stock_id)) || context.paddy;
    const created = await productionService.createBatch({
      paddy_stock_id: Number(batchForm.paddy_stock_id),
      paddy_variety: lot?.variety || paddyForm.variety,
      input_quantity: quantity,
      quality_grade: batchForm.quality_grade,
    });
    const batch = created.batch || created;
    const started = await productionService.startBatch(batch.id);
    setContext((prev) => ({ ...prev, paddy: lot, batch: started.batch || started }));
  };

  const saveQualityAndComplete = async () => {
    const batch = context.batch || openBatch;
    if (!batch?.id) throw new Error('Start a batch before recording quality or output');
    const rice = Number(completeForm.rice_output);
    if (!Number.isFinite(rice) || rice <= 0) throw new Error('Rice output kg must be greater than 0 so product stock can increase');

    let quality = context.quality;
    const hasQuality = ['moisture_content', 'broken_percentage', 'foreign_matter']
      .some((key) => qualityForm[key] !== '');
    if (hasQuality) {
      quality = await productionService.createQualityTest({
        batch_id: batch.id,
        test_parameters: {
          moisture_content: qualityForm.moisture_content === '' ? undefined : Number(qualityForm.moisture_content),
          broken_percentage: qualityForm.broken_percentage === '' ? undefined : Number(qualityForm.broken_percentage),
          foreign_matter: qualityForm.foreign_matter === '' ? undefined : Number(qualityForm.foreign_matter),
        },
      });
    }
    const completed = await productionService.completeBatch(batch.id, {
      rice_output: rice,
      output_quantity: rice,
      broken_rice_output: Number(completeForm.broken_rice_output || 0),
      bran_output: Number(completeForm.bran_output || 0),
      husk_output: Number(completeForm.husk_output || 0),
    });
    setContext((prev) => ({ ...prev, quality, batch: completed.batch || completed }));
    setOrderForm((prev) => ({ ...prev, quantity: prev.quantity || String(rice) }));
    setInvoiceForm((prev) => ({ ...prev, quantity: prev.quantity || String(rice) }));
  };

  const skipQualityOnly = () => {
    setQualityForm({ moisture_content: '', broken_percentage: '', foreign_matter: '' });
    setError('');
  };

  const saveSale = async () => {
    let customer = context.customer;
    if (customerMode === 'new') {
      if (!newCustomer.name.trim() || !newCustomer.phone.trim()) throw new Error('Customer name and phone are required');
      const created = await salesAPI.createCustomer(newCustomer);
      customer = created.data?.customer || created.data || created.customer || created;
    } else {
      if (!customerId || customerId === NONE) throw new Error('Select a customer or switch to New customer');
      customer = customers.find((item) => String(item.id) === String(customerId)) || { id: Number(customerId) };
    }
    const quantity = Number(orderForm.quantity);
    const unitPrice = Number(orderForm.unit_price);
    if (!orderForm.description.trim()) throw new Error('Order item description is required');
    if (!Number.isFinite(quantity) || quantity <= 0 || !Number.isFinite(unitPrice) || unitPrice <= 0) {
      throw new Error('Order quantity and unit price must be greater than 0');
    }
    const createdOrder = await salesAPI.createOrder({
      customer_id: Number(customer.id),
      order_date: orderForm.order_date,
      items: [{
        description: orderForm.description.trim(),
        variety: orderForm.description.trim(),
        quantity,
        unit_price: unitPrice,
      }],
    });
    const order = createdOrder.data?.order || createdOrder.order || createdOrder.data || createdOrder;
    setContext((prev) => ({ ...prev, customer, order }));
    setInvoiceForm({
      description: orderForm.description.trim(),
      quantity: String(quantity),
      unit_price: String(unitPrice),
    });
  };

  const saveInvoiceAndPay = async () => {
    let invoice = context.invoice;
    const customer = context.customer || customers.find((item) => String(item.id) === String(customerId));
    if (!invoice) {
      if (!customer?.id) throw new Error('Customer is required for the invoice');
      const quantity = Number(invoiceForm.quantity);
      const unitPrice = Number(invoiceForm.unit_price);
      if (!invoiceForm.description.trim()) throw new Error('Invoice line description is required');
      if (!Number.isFinite(quantity) || quantity <= 0 || !Number.isFinite(unitPrice) || unitPrice <= 0) {
        throw new Error('Invoice quantity and unit price must be greater than 0');
      }
      const created = await financeService.createInvoice({
        customer_id: Number(customer.id),
        invoice_date: today(),
        items: [{
          description: invoiceForm.description.trim(),
          quantity,
          unit_price: unitPrice,
          product_category: 'processed_rice',
        }],
      });
      invoice = created.invoice || created;
      setContext((prev) => ({ ...prev, invoice }));
    }
    const amount = Number(paymentForm.amount || invoice.total_amount);
    if (!Number.isFinite(amount) || amount <= 0) throw new Error('Payment amount must be greater than 0');
    const payment = await financeService.recordPayment({
      invoice_id: invoice.id,
      customer_id: invoice.customer_id || customer?.id,
      amount,
      payment_method: paymentForm.payment_method,
      payment_date: paymentForm.payment_date,
      payment_type: amount >= Number(invoice.total_amount || amount) ? 'full' : 'partial',
    });
    setContext((prev) => ({ ...prev, invoice, payment: payment.payment || payment }));
    setPaymentForm((prev) => ({ ...prev, amount: String(amount) }));
  };

  const primaryLabel = () => {
    if (busy) return t('saving');
    if (activeStep === 0) return t('savePaddy');
    if (activeStep === 1) return t('startBatch');
    if (activeStep === 2) return t('completeBatch');
    if (activeStep === 3) return t('saveOrder');
    if (context.invoice) return t('recordPayment');
    return t('invoiceAndPay');
  };

  if (snapshotLoading && phase === 'home') {
    return (
      <PageShell>
        <PageLoading label="Reading mill records…" />
      </PageShell>
    );
  }

  return (
    <PageShell>
      <PageHeader
        title={t('millFlowTitle')}
        subtitle={t('millFlowSubtitle')}
        actions={
          phase === 'wizard' ? (
            <Button aria-label="Back to mill flow start" onClick={() => { setPhase('home'); setError(''); }}>
              {t('millFlowStartPage')}
            </Button>
          ) : null
        }
      />

      {phase === 'home' && (
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="overline" color="text.secondary">Suggested next step</Typography>
                <Typography variant="h5" sx={{ mt: 0.5 }}>{suggestion.title}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 2 }}>
                  {suggestion.reason}
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  <Button
                    variant="contained"
                    aria-label={`Start suggested step: ${suggestion.title}`}
                    onClick={() => beginWizard(suggestion.step)}
                  >
                    Continue suggested step
                  </Button>
                  <Button
                    variant="outlined"
                    aria-label="Start mill flow from receive paddy"
                    onClick={() => beginWizard(0)}
                  >
                    Start from receive paddy
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard label="Paddy remaining" value={`${remainingPaddyKg(paddyLots).toLocaleString('en-IN')} kg`} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard label="Open batches" value={batches.filter(isOpenBatch).length} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard label="Product stock" value={`${productStockKg(products).toLocaleString('en-IN')} kg`} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryCard label="Unpaid invoices" value={unpaidInvoices.length} />
          </Grid>
        </Grid>
      )}

      {phase === 'wizard' && (
        <Card sx={{ overflow: 'visible' }}>
          <CardContent sx={{ overflow: 'visible' }}>
            <Box sx={{ overflowX: 'auto', pb: 1 }}>
              <Stepper activeStep={activeStep} alternativeLabel sx={{ minWidth: 520 }}>
                {stepLabels.map((label) => (
                  <Step key={label}>
                    <StepLabel>{label}</StepLabel>
                  </Step>
                ))}
              </Stepper>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError('')} role="alert">
                {error}
              </Alert>
            )}

            <Box sx={{ mt: 3, maxWidth: 720 }}>
              {activeStep === 0 && (
                <ReceiveStep
                  farmerMode={farmerMode}
                  setFarmerMode={setFarmerMode}
                  farmerId={farmerId}
                  setFarmerId={setFarmerId}
                  farmers={farmers}
                  newFarmer={newFarmer}
                  setNewFarmer={setNewFarmer}
                  paddyForm={paddyForm}
                  setPaddyForm={setPaddyForm}
                />
              )}
              {activeStep === 1 && (
                <BatchStep
                  lots={availableLots}
                  batchForm={batchForm}
                  setBatchForm={setBatchForm}
                  existing={context.batch}
                />
              )}
              {activeStep === 2 && (
                <CompleteStep
                  batch={context.batch || openBatch}
                  qualityForm={qualityForm}
                  setQualityForm={setQualityForm}
                  completeForm={completeForm}
                  setCompleteForm={setCompleteForm}
                  onSkipQuality={skipQualityOnly}
                />
              )}
              {activeStep === 3 && (
                <SellStep
                  customerMode={customerMode}
                  setCustomerMode={setCustomerMode}
                  customerId={customerId}
                  setCustomerId={setCustomerId}
                  customers={customers}
                  newCustomer={newCustomer}
                  setNewCustomer={setNewCustomer}
                  orderForm={orderForm}
                  setOrderForm={setOrderForm}
                />
              )}
              {activeStep === 4 && (
                <PayStep
                  invoice={context.invoice}
                  customer={context.customer}
                  invoiceForm={invoiceForm}
                  setInvoiceForm={setInvoiceForm}
                  paymentForm={paymentForm}
                  setPaymentForm={setPaymentForm}
                  unpaidInvoices={unpaidInvoices}
                  onPickInvoice={(invoice) => {
                    setContext((prev) => ({ ...prev, invoice }));
                    setPaymentForm((prev) => ({
                      ...prev,
                      amount: String(invoice.total_amount || ''),
                    }));
                  }}
                />
              )}
            </Box>

            {context.payment && activeStep === 4 && (
              <Alert severity="success" sx={{ mt: 2 }}>
                Payment recorded. You can open Finance or Dashboard to confirm the mill books.
              </Alert>
            )}

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 3 }}>
              <Button aria-label="Go to previous mill flow step" onClick={goBack} disabled={busy}>
                {t('back')}
              </Button>
              {!(context.payment && activeStep === 4) && (
                <Button
                  variant="contained"
                  aria-label={primaryLabel()}
                  onClick={runStep}
                  disabled={busy}
                >
                  {primaryLabel()}
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>
      )}
    </PageShell>
  );
};

const SummaryCard = ({ label, value }) => (
  <Card>
    <CardContent>
      <Typography variant="body2" color="text.secondary">{label}</Typography>
      <Typography variant="h5">{value}</Typography>
    </CardContent>
  </Card>
);

const ReceiveStep = ({
  farmerMode, setFarmerMode, farmerId, setFarmerId, farmers, newFarmer, setNewFarmer, paddyForm, setPaddyForm,
}) => {
  const missing = receiveMissingFields({ farmerMode, newFarmer, paddyForm });
  return (
    <Box>
    <Typography variant="h6" gutterBottom>1. Receive paddy</Typography>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      Keep Existing farmer and Walk-in / later, or switch to New farmer. Then fill variety, quantity, price, and location.
    </Typography>
    <FormControl component="fieldset" sx={{ mb: 2 }}>
      <RadioGroup
        row
        value={farmerMode}
        onChange={(event) => setFarmerMode(event.target.value)}
      >
        <FormControlLabel value="existing" control={<Radio />} label="Existing farmer" />
        <FormControlLabel value="new" control={<Radio />} label="New farmer" />
      </RadioGroup>
    </FormControl>
    <Grid container spacing={2}>
      {farmerMode === 'existing' ? (
        <Grid item xs={12}>
          <FormControl fullWidth>
            <InputLabel id="mill-flow-farmer-label">Farmer</InputLabel>
            <Select
              labelId="mill-flow-farmer-label"
              label="Farmer"
              value={farmerId || WALK_IN}
              onChange={(event) => setFarmerId(event.target.value)}
              MenuProps={SELECT_MENU_PROPS}
            >
              <MenuItem value={WALK_IN}>Walk-in / later</MenuItem>
              {farmers.map((farmer) => (
                <MenuItem key={farmer.id} value={String(farmer.id)}>
                  {farmer.name} {farmer.phone ? `· ${farmer.phone}` : ''}
                </MenuItem>
              ))}
            </Select>
            <FormHelperText>
              Walk-in / later files the lot without a farmer id. The mill walk-in farmer is used on save.
            </FormHelperText>
          </FormControl>
        </Grid>
      ) : (
        <>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth required label="Farmer name" value={newFarmer.name} onChange={(e) => setNewFarmer({ ...newFarmer, name: e.target.value })} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth required label="Phone" value={newFarmer.phone} onChange={(e) => setNewFarmer({ ...newFarmer, phone: e.target.value })} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth required label="Village" value={newFarmer.village} onChange={(e) => setNewFarmer({ ...newFarmer, village: e.target.value })} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth required label="District" value={newFarmer.district} onChange={(e) => setNewFarmer({ ...newFarmer, district: e.target.value })} />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField fullWidth required label="State" value={newFarmer.state} onChange={(e) => setNewFarmer({ ...newFarmer, state: e.target.value })} />
          </Grid>
        </>
      )}
      <Grid item xs={12} sm={6}>
        <FormControl fullWidth required>
          <InputLabel id="mill-flow-variety-label">Variety</InputLabel>
          <Select
            labelId="mill-flow-variety-label"
            label="Variety"
            value={paddyForm.variety}
            onChange={(e) => setPaddyForm({ ...paddyForm, variety: e.target.value })}
            MenuProps={SELECT_MENU_PROPS}
          >
            {PADDY_VARIETIES.map((item) => (
              <MenuItem key={item.value} value={item.value}>{item.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField fullWidth required type="number" label="Quantity (kg)" value={paddyForm.quantity} onChange={(e) => setPaddyForm({ ...paddyForm, quantity: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField fullWidth required type="number" label="Price (₹/kg)" value={paddyForm.purchase_price} onChange={(e) => setPaddyForm({ ...paddyForm, purchase_price: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField fullWidth required label="Storage location" value={paddyForm.storage_location} onChange={(e) => setPaddyForm({ ...paddyForm, storage_location: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField fullWidth type="number" label="Moisture % (optional)" value={paddyForm.moisture_content} onChange={(e) => setPaddyForm({ ...paddyForm, moisture_content: e.target.value })} />
      </Grid>
    </Grid>
      {missing.length > 0 && (
        <Alert severity="info" sx={{ mt: 2 }} role="status">
          Still needed: {missing.join(', ')}
        </Alert>
      )}
    </Box>
  );
};

const BatchStep = ({ lots, batchForm, setBatchForm, existing }) => (
  <Box>
    <Typography variant="h6" gutterBottom>2. Start a batch</Typography>
    {existing && (
      <Alert severity="info" sx={{ mb: 2 }}>
        Using batch {existing.batch_number || existing.id} ({existing.status}). Starting deducts paddy for a planned batch.
      </Alert>
    )}
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      Choose the paddy lot. Starting the batch deducts remaining kg. This step cannot skip stock rules.
    </Typography>
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <FormControl fullWidth required>
          <InputLabel id="mill-flow-lot-label">Paddy lot</InputLabel>
          <Select
            labelId="mill-flow-lot-label"
            label="Paddy lot"
            value={batchForm.paddy_stock_id || NONE}
            onChange={(e) => setBatchForm({ ...batchForm, paddy_stock_id: e.target.value })}
            MenuProps={SELECT_MENU_PROPS}
          >
            <MenuItem value={NONE}>Select a paddy lot</MenuItem>
            {lots.map((lot) => (
              <MenuItem key={lot.id} value={String(lot.id)}>
                {lot.variety} · {lotRemaining(lot)} kg · {lot.warehouse_id || lot.storage_location || lot.stock_id}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          required
          type="number"
          label="Input quantity (kg)"
          value={batchForm.input_quantity}
          onChange={(e) => setBatchForm({ ...batchForm, input_quantity: e.target.value })}
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <FormControl fullWidth>
          <InputLabel id="mill-flow-grade-label">Grade</InputLabel>
          <Select
            labelId="mill-flow-grade-label"
            label="Grade"
            value={batchForm.quality_grade}
            onChange={(e) => setBatchForm({ ...batchForm, quality_grade: e.target.value })}
            MenuProps={SELECT_MENU_PROPS}
          >
            <MenuItem value="A">Grade A</MenuItem>
            <MenuItem value="B">Grade B</MenuItem>
            <MenuItem value="C">Grade C</MenuItem>
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  </Box>
);

const CompleteStep = ({ batch, qualityForm, setQualityForm, completeForm, setCompleteForm, onSkipQuality }) => (
  <Box>
    <Typography variant="h6" gutterBottom>3. Quality and complete</Typography>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
      Quality test is optional. Rice output kg is required so product stock increases.
    </Typography>
    {batch && <Chip sx={{ mb: 2 }} label={`Batch ${batch.batch_number || batch.id}`} />}
    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
      <Button aria-label="Skip quality test" onClick={onSkipQuality}>Skip quality test</Button>
    </Box>
    <Grid container spacing={2}>
      <Grid item xs={12} sm={4}>
        <TextField fullWidth type="number" label="Moisture %" value={qualityForm.moisture_content} onChange={(e) => setQualityForm({ ...qualityForm, moisture_content: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={4}>
        <TextField fullWidth type="number" label="Broken %" value={qualityForm.broken_percentage} onChange={(e) => setQualityForm({ ...qualityForm, broken_percentage: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={4}>
        <TextField fullWidth type="number" label="Foreign matter %" value={qualityForm.foreign_matter} onChange={(e) => setQualityForm({ ...qualityForm, foreign_matter: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField fullWidth required type="number" label="Rice output (kg)" value={completeForm.rice_output} onChange={(e) => setCompleteForm({ ...completeForm, rice_output: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField fullWidth type="number" label="Broken rice (kg)" value={completeForm.broken_rice_output} onChange={(e) => setCompleteForm({ ...completeForm, broken_rice_output: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField fullWidth type="number" label="Bran (kg)" value={completeForm.bran_output} onChange={(e) => setCompleteForm({ ...completeForm, bran_output: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField fullWidth type="number" label="Husk (kg)" value={completeForm.husk_output} onChange={(e) => setCompleteForm({ ...completeForm, husk_output: e.target.value })} />
      </Grid>
    </Grid>
  </Box>
);

const SellStep = ({
  customerMode, setCustomerMode, customerId, setCustomerId, customers, newCustomer, setNewCustomer, orderForm, setOrderForm,
}) => (
  <Box>
    <Typography variant="h6" gutterBottom>4. Sell</Typography>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      Select or create a customer, then save a sales order.
    </Typography>
    <FormControl component="fieldset" sx={{ mb: 2 }}>
      <RadioGroup row value={customerMode} onChange={(e) => setCustomerMode(e.target.value)}>
        <FormControlLabel value="existing" control={<Radio />} label="Existing customer" />
        <FormControlLabel value="new" control={<Radio />} label="New customer" />
      </RadioGroup>
    </FormControl>
    <Grid container spacing={2}>
      {customerMode === 'existing' ? (
        <Grid item xs={12}>
          <FormControl fullWidth required>
            <InputLabel id="mill-flow-customer-label">Customer</InputLabel>
            <Select
              labelId="mill-flow-customer-label"
              label="Customer"
              value={customerId || NONE}
              onChange={(e) => setCustomerId(e.target.value)}
              MenuProps={SELECT_MENU_PROPS}
            >
              <MenuItem value={NONE}>Select a customer</MenuItem>
              {customers.map((customer) => (
                <MenuItem key={customer.id} value={String(customer.id)}>
                  {customer.name} {customer.phone ? `· ${customer.phone}` : ''}
                </MenuItem>
              ))}
            </Select>
            {!customers.length && (
              <FormHelperText>No customers yet. Switch to New customer.</FormHelperText>
            )}
          </FormControl>
        </Grid>
      ) : (
        <>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth required label="Customer name" value={newCustomer.name} onChange={(e) => setNewCustomer({ ...newCustomer, name: e.target.value })} />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField fullWidth required label="Phone" value={newCustomer.phone} onChange={(e) => setNewCustomer({ ...newCustomer, phone: e.target.value })} />
          </Grid>
        </>
      )}
      <Grid item xs={12}>
        <TextField fullWidth required label="Item / variety" value={orderForm.description} onChange={(e) => setOrderForm({ ...orderForm, description: e.target.value })} helperText="Use wording that matches product stock if you will invoice next" />
      </Grid>
      <Grid item xs={12} sm={4}>
        <TextField fullWidth required type="number" label="Quantity (kg)" value={orderForm.quantity} onChange={(e) => setOrderForm({ ...orderForm, quantity: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={4}>
        <TextField fullWidth required type="number" label="Unit price (₹/kg)" value={orderForm.unit_price} onChange={(e) => setOrderForm({ ...orderForm, unit_price: e.target.value })} />
      </Grid>
      <Grid item xs={12} sm={4}>
        <TextField fullWidth type="date" label="Order date" InputLabelProps={{ shrink: true }} value={orderForm.order_date} onChange={(e) => setOrderForm({ ...orderForm, order_date: e.target.value })} />
      </Grid>
    </Grid>
  </Box>
);

const PayStep = ({
  invoice, customer, invoiceForm, setInvoiceForm, paymentForm, setPaymentForm, unpaidInvoices, onPickInvoice,
}) => (
  <Box>
    <Typography variant="h6" gutterBottom>5. Invoice and payment</Typography>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
      Invoice lines must match product stock. Payment amount must be greater than 0.
    </Typography>
    {invoice ? (
      <Alert severity="info" sx={{ mb: 2 }}>
        Invoice {invoice.invoice_number || invoice.id} · ₹{Number(invoice.total_amount || 0).toLocaleString('en-IN')}
        {customer?.name ? ` · ${customer.name}` : ''}
      </Alert>
    ) : (
      <Grid container spacing={2} sx={{ mb: 2 }}>
        {unpaidInvoices.length > 0 && (
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel id="mill-flow-unpaid-label">Or pick an unpaid invoice</InputLabel>
              <Select
                labelId="mill-flow-unpaid-label"
                label="Or pick an unpaid invoice"
                value={invoice?.id ? String(invoice.id) : NONE}
                onChange={(e) => {
                  const found = unpaidInvoices.find((item) => String(item.id) === String(e.target.value));
                  if (found) onPickInvoice(found);
                }}
                MenuProps={SELECT_MENU_PROPS}
              >
                <MenuItem value={NONE}>Create a new invoice below</MenuItem>
                {unpaidInvoices.map((item) => (
                  <MenuItem key={item.id} value={String(item.id)}>
                    {item.invoice_number || item.id} · ₹{Number(item.total_amount || 0).toLocaleString('en-IN')}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        )}
        <Grid item xs={12}>
          <TextField fullWidth required label="Invoice line" value={invoiceForm.description} onChange={(e) => setInvoiceForm({ ...invoiceForm, description: e.target.value })} />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField fullWidth required type="number" label="Quantity (kg)" value={invoiceForm.quantity} onChange={(e) => setInvoiceForm({ ...invoiceForm, quantity: e.target.value })} />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField fullWidth required type="number" label="Unit price (₹/kg)" value={invoiceForm.unit_price} onChange={(e) => setInvoiceForm({ ...invoiceForm, unit_price: e.target.value })} />
        </Grid>
      </Grid>
    )}
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          required
          type="number"
          label="Payment amount (₹)"
          value={paymentForm.amount}
          onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })}
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <FormControl fullWidth>
          <InputLabel id="mill-flow-pay-method-label">Payment method</InputLabel>
          <Select
            labelId="mill-flow-pay-method-label"
            label="Payment method"
            value={paymentForm.payment_method}
            onChange={(e) => setPaymentForm({ ...paymentForm, payment_method: e.target.value })}
            MenuProps={SELECT_MENU_PROPS}
          >
            <MenuItem value="cash">Cash</MenuItem>
            <MenuItem value="upi">UPI</MenuItem>
            <MenuItem value="bank_transfer">Bank transfer</MenuItem>
            <MenuItem value="cheque">Cheque</MenuItem>
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  </Box>
);

export default MillFlow;
