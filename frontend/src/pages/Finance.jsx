import React, { useState, useEffect } from 'react';
import {
  Grid, Card, CardContent, Typography, Box, Button,
  Paper, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  TrendingUp, TrendingDown, AccountBalance, Receipt,
  Payment, Assessment, Add
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { financeService } from '../services/financeService';
import CreateInvoiceDialog from '../components/finance/CreateInvoiceDialog';
import RecordPaymentDialog from '../components/finance/RecordPaymentDialog';
import CashFlowChart from '../components/finance/CashFlowChart';
import { getApiErrorMessage } from '../utils/apiError';
import { PageHeader, PageShell, QueryErrorAlert } from '../components/common/PageChrome';
import StatusChip from '../components/common/StatusChip';
import DataTable from '../components/common/DataTable';
import { formatDate, formatINR } from '../utils/format';
import { useI18n } from '../i18n/I18nContext';
import { useAssistantOpen } from '../assistant/AssistantBridge';

const Finance = () => {
  const { t } = useI18n();
  const [createInvoiceOpen, setCreateInvoiceOpen] = useState(false);
  useAssistantOpen('create-invoice', () => setCreateInvoiceOpen(true));
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

  const formatCurrency = (amount) => formatINR(amount);

  return (
    <PageShell>
      <PageHeader
        title={t('financeTitle')}
        subtitle={t('financeSubtitle')}
        pageKey="finance"
        actions={
          <>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => { setActionError(''); setCreateInvoiceOpen(true); }}
            >
              {t('createInvoice')}
            </Button>
            <Button
              variant="outlined"
              startIcon={<Payment />}
              onClick={() => { setActionError(''); setRecordPaymentOpen(true); }}
            >
              {t('recordPayment')}
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
              <DataTable
                testId="finance-invoices"
                rows={recentInvoices?.invoices || []}
                searchKeys={['invoice_number', 'customer_name', 'status']}
                emptyTitle={t('noInvoicesYet')}
                emptyDescription={t('noInvoicesHint')}
                emptyAction={(
                  <Button variant="contained" startIcon={<Add />} onClick={() => setCreateInvoiceOpen(true)}>
                    {t('createInvoice')}
                  </Button>
                )}
                columns={[
                  { field: 'invoice_number', label: t('invoiceNo') },
                  { field: 'customer_name', label: t('customers'), render: (invoice) => invoice.customer?.name || invoice.customer_name || '—' },
                  { field: 'invoice_date', label: t('date'), render: (invoice) => formatDate(invoice.invoice_date) },
                  { field: 'due_date', label: t('dueDate'), render: (invoice) => formatDate(invoice.due_date) },
                  { field: 'total_amount', label: t('amount'), render: (invoice) => formatCurrency(invoice.total_amount) },
                  { field: 'status', label: t('status'), render: (invoice) => <StatusChip status={invoice.status} /> },
                ]}
                rowActions={[
                  { label: t('view'), onClick: (invoice) => setSelectedInvoice(invoice) },
                ]}
              />
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
          <Button onClick={() => setSelectedInvoice(null)}>{t('close')}</Button>
          <Button
            variant="contained"
            onClick={() => {
              setRecordPaymentOpen(true);
            }}
          >
            {t('recordPayment')}
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