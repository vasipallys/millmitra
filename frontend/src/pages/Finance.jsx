import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Paper, Chip, IconButton, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  TrendingUp, TrendingDown, AccountBalance, Receipt,
  Payment, Assessment, Add, Visibility
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { financeService } from '../services/financeService';
import CreateInvoiceDialog from '../components/finance/CreateInvoiceDialog';
import RecordPaymentDialog from '../components/finance/RecordPaymentDialog';
import CashFlowChart from '../components/finance/CashFlowChart';
import { getApiErrorMessage } from '../utils/apiError';
import { PageEmpty, PageHeader, PageShell, QueryErrorAlert } from '../components/common/PageChrome';

const Finance = () => {
  const [createInvoiceOpen, setCreateInvoiceOpen] = useState(false);
  const [recordPaymentOpen, setRecordPaymentOpen] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const queryClient = useQueryClient();

  // Queries
  const { data: summary, isError: summaryError, error: summaryErr, refetch: refetchSummary } = useQuery(
    'financial-summary',
    () => financeService.getFinancialSummary(30),
    { refetchInterval: 300000 }
  );

  const { data: cashFlow } = useQuery(
    'cash-flow',
    () => financeService.getCashFlow('monthly'),
    { refetchInterval: 300000 }
  );

  const { data: accountsReceivable } = useQuery(
    'accounts-receivable',
    () => financeService.getAccountsReceivable(),
    { refetchInterval: 300000 }
  );

  const { data: recentInvoices, isError: invoicesError, error: invoicesErr, refetch: refetchInvoices } = useQuery(
    'recent-invoices',
    () => financeService.getInvoices({ limit: 10 })
  );

  // Mutations
  const [actionError, setActionError] = useState('');

  const createInvoiceMutation = useMutation(financeService.createInvoice, {
    onSuccess: () => {
      queryClient.invalidateQueries('financial-summary');
      queryClient.invalidateQueries('recent-invoices');
      queryClient.invalidateQueries('accounts-receivable');
      queryClient.invalidateQueries('cash-flow');
      setCreateInvoiceOpen(false);
      setActionError('');
    },
    onError: (error) => {
      setActionError(getApiErrorMessage(error, 'Could not create invoice'));
    }
  });

  const recordPaymentMutation = useMutation(financeService.recordPayment, {
    onSuccess: () => {
      queryClient.invalidateQueries('financial-summary');
      queryClient.invalidateQueries('accounts-receivable');
      queryClient.invalidateQueries('cash-flow');
      queryClient.invalidateQueries('recent-invoices');
      setRecordPaymentOpen(false);
      setActionError('');
    },
    onError: (error) => {
      setActionError(getApiErrorMessage(error, 'Could not record payment'));
    }
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'success';
      case 'pending': return 'warning';
      case 'overdue': return 'error';
      case 'partial': return 'info';
      default: return 'default';
    }
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
        title="Financial Management"
        subtitle="Invoices and payments you entered. Line descriptions must match product stock."
        actions={
          <>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => { setActionError(''); setCreateInvoiceOpen(true); }}
            >
              Create Invoice
            </Button>
            <Button
              variant="outlined"
              startIcon={<Payment />}
              onClick={() => { setActionError(''); setRecordPaymentOpen(true); }}
            >
              Record Payment
            </Button>
          </>
        }
      />
      {summaryError && <QueryErrorAlert error={summaryErr} onRetry={refetchSummary} entity="finance summary" />}
      {invoicesError && <QueryErrorAlert error={invoicesErr} onRetry={refetchInvoices} entity="invoices" />}
      {actionError && <QueryErrorAlert error={new Error(actionError)} entity="finance action" />}

      {/* Financial Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Revenue
                  </Typography>
                  <Typography variant="h5">
                    {summary ? formatCurrency(summary.total_revenue) : '₹0'}
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
                <TrendingDown color="error" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Expenses
                  </Typography>
                  <Typography variant="h5">
                    {summary ? formatCurrency(summary.total_expenses) : '₹0'}
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
                <AccountBalance color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Net Profit
                  </Typography>
                  <Typography variant="h5" color={summary?.net_profit >= 0 ? 'success.main' : 'error.main'}>
                    {summary ? formatCurrency(summary.net_profit) : '₹0'}
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
                <Receipt color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Outstanding Receivables
                  </Typography>
                  <Typography variant="h5">
                    {summary ? formatCurrency(summary.outstanding_receivables) : '₹0'}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Cash Flow Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cash Flow Analysis
              </Typography>
              {Array.isArray(cashFlow) && cashFlow.length > 0 && <CashFlowChart data={cashFlow} />}
              {Array.isArray(cashFlow) && cashFlow.length === 0 && (
                <Typography color="textSecondary">No cash-flow months yet.</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Accounts Receivable Summary */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Accounts Receivable
              </Typography>
              {accountsReceivable && (
                <Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Total Outstanding
                    </Typography>
                    <Typography variant="h6">
                      {formatCurrency(accountsReceivable.total_outstanding)}
                    </Typography>
                  </Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="textSecondary">
                      Overdue Amount
                    </Typography>
                    <Typography variant="h6" color="error">
                      {formatCurrency(accountsReceivable.total_overdue)}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Overdue Invoices
                    </Typography>
                    <Typography variant="h6">
                      {accountsReceivable.overdue_count}
                    </Typography>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Invoices */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Invoices
              </Typography>
              {!recentInvoices?.invoices?.length && (
                <PageEmpty
                  title="No invoices yet"
                  description="Create Invoice to bill a customer. Product line wording must match Inventory."
                  action={
                    <Button variant="contained" startIcon={<Add />} onClick={() => setCreateInvoiceOpen(true)}>
                      Create Invoice
                    </Button>
                  }
                />
              )}
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Invoice #</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Due Date</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(recentInvoices?.invoices || []).map((invoice) => (
                      <TableRow key={invoice.id}>
                        <TableCell>{invoice.invoice_number}</TableCell>
                        <TableCell>{invoice.customer?.name || invoice.customer_name || '—'}</TableCell>
                        <TableCell>{new Date(invoice.invoice_date).toLocaleDateString()}</TableCell>
                        <TableCell>{new Date(invoice.due_date).toLocaleDateString()}</TableCell>
                        <TableCell>{formatCurrency(invoice.total_amount)}</TableCell>
                        <TableCell>
                          <Chip
                            label={invoice.status}
                            color={getStatusColor(invoice.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <IconButton
                            size="small"
                            aria-label={`View invoice ${invoice.invoice_number}`}
                            onClick={() => setSelectedInvoice(invoice)}
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
        </Grid>
      </Grid>

      {/* Dialogs */}
      <CreateInvoiceDialog
        open={createInvoiceOpen}
        onClose={() => setCreateInvoiceOpen(false)}
        onSubmit={(data) => createInvoiceMutation.mutate(data)}
        loading={createInvoiceMutation.isLoading}
      />

      <Dialog
        open={Boolean(selectedInvoice)}
        onClose={() => setSelectedInvoice(null)}
        maxWidth="sm"
        fullWidth
        aria-labelledby="invoice-detail-title"
      >
        <DialogTitle id="invoice-detail-title">
          Invoice {selectedInvoice?.invoice_number}
        </DialogTitle>
        <DialogContent>
          {selectedInvoice && (
            <Box sx={{ pt: 1 }}>
              <Typography>Customer: {selectedInvoice.customer?.name || selectedInvoice.customer_name || selectedInvoice.customer_id || '—'}</Typography>
              <Typography>Date: {selectedInvoice.invoice_date ? new Date(selectedInvoice.invoice_date).toLocaleDateString() : '—'}</Typography>
              <Typography>Due: {selectedInvoice.due_date ? new Date(selectedInvoice.due_date).toLocaleDateString() : '—'}</Typography>
              <Typography>Amount: {formatCurrency(selectedInvoice.total_amount)}</Typography>
              <Typography>Status: {selectedInvoice.status || '—'}</Typography>
              <Typography sx={{ mt: 1 }} variant="body2" color="text.secondary">
                Line items must match product stock names when the invoice was created.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedInvoice(null)}>Close</Button>
          <Button
            variant="contained"
            onClick={() => {
              setRecordPaymentOpen(true);
            }}
          >
            Record Payment
          </Button>
        </DialogActions>
      </Dialog>

      <RecordPaymentDialog
        open={recordPaymentOpen}
        onClose={() => setRecordPaymentOpen(false)}
        onSubmit={(data) => recordPaymentMutation.mutate(data)}
        loading={recordPaymentMutation.isLoading}
        invoice={selectedInvoice}
      />
    </PageShell>
  );
};

export default Finance;