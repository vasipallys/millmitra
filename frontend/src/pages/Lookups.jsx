import { useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { PageHeader, PageLoading, PageShell } from '../components/common/PageChrome';
import { lookupService, optionLabel } from '../services/lookupService';
import { getApiErrorMessage } from '../utils/apiError';
import { useI18n } from '../i18n/I18nContext';

const emptyForm = (group) => ({
  group_key: group || 'product_type',
  value: '',
  label_en: '',
  label_hi: '',
  label_te: '',
  sort_order: 0,
});

export default function Lookups() {
  const { t, locale } = useI18n();
  const queryClient = useQueryClient();
  const [group, setGroup] = useState('product_type');
  const [form, setForm] = useState(emptyForm('product_type'));
  const [editing, setEditing] = useState(null);
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const adminQuery = useQuery(['lookups-admin'], () => lookupService.listAdmin(), { retry: false });
  const groups = adminQuery.data?.groups || [];
  const rows = useMemo(
    () => (adminQuery.data?.options || []).filter((item) => item.group_key === group),
    [adminQuery.data, group]
  );

  const refresh = () => {
    queryClient.invalidateQueries('lookups-admin');
    queryClient.invalidateQueries('lookups');
  };

  const createMutation = useMutation((payload) => lookupService.create(payload), {
    onSuccess: () => {
      setMessage(t('lookupSaved'));
      setError('');
      setOpen(false);
      refresh();
    },
    onError: (err) => setError(getApiErrorMessage(err, t('lookupSaveError'))),
  });

  const updateMutation = useMutation(
    ({ id, payload }) => lookupService.update(id, payload),
    {
      onSuccess: () => {
        setMessage(t('lookupSaved'));
        setError('');
        setOpen(false);
        refresh();
      },
      onError: (err) => setError(getApiErrorMessage(err, t('lookupSaveError'))),
    }
  );

  const toggleMutation = useMutation(
    ({ id, active }) => (active ? lookupService.activate(id) : lookupService.deactivate(id)),
    {
      onSuccess: () => {
        setMessage(t('lookupSaved'));
        setError('');
        refresh();
      },
      onError: (err) => setError(getApiErrorMessage(err, t('lookupSaveError'))),
    }
  );

  if (adminQuery.isLoading) {
    return <PageShell><PageLoading label={t('lookupsTitle')} /></PageShell>;
  }

  const groupLocked = groups.find((item) => item.key === group)?.locked;

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm(group));
    setOpen(true);
  };

  const openEdit = (row) => {
    setEditing(row);
    setForm({
      group_key: row.group_key,
      value: row.value,
      label_en: row.label_en || row.labels?.en || '',
      label_hi: row.label_hi || row.labels?.hi || '',
      label_te: row.label_te || row.labels?.te || '',
      sort_order: row.sort_order || 0,
    });
    setOpen(true);
  };

  const submit = () => {
    const payload = {
      group_key: form.group_key,
      value: form.value,
      label_en: form.label_en,
      label_hi: form.label_hi,
      label_te: form.label_te,
      sort_order: Number(form.sort_order) || 0,
    };
    if (editing) {
      updateMutation.mutate({ id: editing.id, payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  return (
    <PageShell>
      <PageHeader
        title={t('lookupsTitle')}
        subtitle={t('lookupsSubtitle')}
        actions={(
          <Button variant="contained" onClick={openCreate} disabled={groupLocked}>
            {t('lookupAdd')}
          </Button>
        )}
      />
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {message && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setMessage('')}>{message}</Alert>}
      {adminQuery.isError && (
        <Alert severity="error" sx={{ mb: 2 }}>{getApiErrorMessage(adminQuery.error, t('lookupLoadError'))}</Alert>
      )}
      <TextField
        select
        label={t('lookupGroup')}
        value={group}
        onChange={(event) => setGroup(event.target.value)}
        sx={{ mb: 2, minWidth: 280 }}
      >
        {groups.map((item) => (
          <MenuItem key={item.key} value={item.key}>
            {t(`lookup_group_${item.key}`) === `lookup_group_${item.key}` ? item.key : t(`lookup_group_${item.key}`)}
          </MenuItem>
        ))}
      </TextField>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('lookupLabel')}</TableCell>
            <TableCell>{t('lookupValue')}</TableCell>
            <TableCell>{t('active')}</TableCell>
            <TableCell>{t('lookupSort')}</TableCell>
            <TableCell />
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id}>
              <TableCell>{optionLabel(row, locale)}</TableCell>
              <TableCell>{row.value}</TableCell>
              <TableCell>
                <Chip
                  size="small"
                  color={row.is_active ? 'success' : 'default'}
                  label={row.is_active ? t('active') : t('lookupInactive')}
                />
                {row.is_locked ? <Chip size="small" sx={{ ml: 1 }} label={t('lookupLocked')} /> : null}
              </TableCell>
              <TableCell>{row.sort_order}</TableCell>
              <TableCell>
                <Stack direction="row" spacing={1}>
                  <Button size="small" onClick={() => openEdit(row)}>{t('lookupEdit')}</Button>
                  {!row.is_locked && (
                    <Button
                      size="small"
                      onClick={() => toggleMutation.mutate({ id: row.id, active: !row.is_active })}
                    >
                      {row.is_active ? t('lookupDeactivate') : t('lookupActivate')}
                    </Button>
                  )}
                </Stack>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? t('lookupEdit') : t('lookupAdd')}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label={t('lookupValue')}
              value={form.value}
              onChange={(event) => setForm({ ...form, value: event.target.value })}
              disabled={Boolean(editing?.is_locked)}
            />
            <TextField
              label={t('lookupLabelEn')}
              value={form.label_en}
              onChange={(event) => setForm({ ...form, label_en: event.target.value })}
            />
            <TextField
              label={t('lookupLabelHi')}
              value={form.label_hi}
              onChange={(event) => setForm({ ...form, label_hi: event.target.value })}
            />
            <TextField
              label={t('lookupLabelTe')}
              value={form.label_te}
              onChange={(event) => setForm({ ...form, label_te: event.target.value })}
            />
            <TextField
              label={t('lookupSort')}
              type="number"
              value={form.sort_order}
              onChange={(event) => setForm({ ...form, sort_order: event.target.value })}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>{t('cancel')}</Button>
          <Button variant="contained" onClick={submit} disabled={createMutation.isLoading || updateMutation.isLoading}>
            {t('save')}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
