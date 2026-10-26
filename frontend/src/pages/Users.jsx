import { useState } from 'react';
import {
  Alert,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Select,
  TextField,
} from '@mui/material';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { PageHeader, PageLoading, PageShell } from '../components/common/PageChrome';
import DataTable from '../components/common/DataTable';
import StatusChip from '../components/common/StatusChip';
import ConfirmDialog from '../components/common/ConfirmDialog';
import { userAdminService } from '../services/userAdminService';
import { getApiErrorMessage } from '../utils/apiError';
import { useI18n } from '../i18n/I18nContext';

const ROLES = ['admin', 'manager', 'operator', 'quality_control', 'sales', 'accountant'];

export default function Users({ currentUser }) {
  const { t, roleLabel } = useI18n();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ username: '', password: '', role: 'operator' });
  const [error, setError] = useState('');
  const [confirmUser, setConfirmUser] = useState(null);

  const usersQuery = useQuery('admin-users', () => userAdminService.listUsers(), { retry: false });
  const users = usersQuery.data?.users || [];

  const createMutation = useMutation((payload) => userAdminService.createUser(payload), {
    onSuccess: () => {
      queryClient.invalidateQueries('admin-users');
      setOpen(false);
      setForm({ username: '', password: '', role: 'operator' });
      setError('');
    },
    onError: (err) => setError(getApiErrorMessage(err, t('couldNotCreateUser'))),
  });

  const patchMutation = useMutation(
    ({ id, payload }) => userAdminService.updateUser(id, payload),
    {
      onSuccess: () => queryClient.invalidateQueries('admin-users'),
      onError: (err) => setError(getApiErrorMessage(err, t('couldNotUpdateUser'))),
    }
  );

  if (usersQuery.isLoading) {
    return <PageShell><PageLoading label={t('usersTitle')} /></PageShell>;
  }

  return (
    <PageShell>
      <PageHeader
        title={t('usersTitle')}
        subtitle={t('usersSubtitle')}
        pageKey="users"
        actions={(
          <Button variant="contained" onClick={() => setOpen(true)}>{t('createUser')}</Button>
        )}
      />
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      <DataTable
        rows={users}
        searchKeys={['username', 'first_name', 'role']}
        emptyTitle={t('noRows')}
        columns={[
          { field: 'username', label: t('username'), render: (user) => `${user.username}${user.first_name ? ` · ${user.first_name}` : ''}` },
          {
            field: 'role',
            label: t('role'),
            render: (user) => (
              <Select
                size="small"
                value={user.role}
                inputProps={{ 'aria-label': `${t('role')} ${user.username}` }}
                onChange={(event) => patchMutation.mutate({ id: user.id, payload: { role: event.target.value } })}
              >
                {ROLES.map((role) => (
                  <MenuItem key={role} value={role}>{roleLabel(role)}</MenuItem>
                ))}
              </Select>
            ),
          },
          {
            field: 'is_active',
            label: t('active'),
            render: (user) => <StatusChip status={user.is_active ? 'active' : 'inactive'} />,
          },
        ]}
        rowActions={[
          {
            label: (row) => (row?.is_active ? t('deactivate') : t('activate')),
            disabled: (row) => row?.id === currentUser?.id && row?.is_active,
            onClick: (row) => setConfirmUser(row),
          },
        ]}
      />
      <ConfirmDialog
        open={Boolean(confirmUser)}
        title={t('pleaseConfirm')}
        message={confirmUser?.is_active ? t('confirmDeactivateUser') : t('confirmActivateUser')}
        danger={Boolean(confirmUser?.is_active)}
        onCancel={() => setConfirmUser(null)}
        onConfirm={() => {
          patchMutation.mutate({
            id: confirmUser.id,
            payload: { is_active: !confirmUser.is_active },
          });
          setConfirmUser(null);
        }}
      />

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>{t('createUser')}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            margin="normal"
            label={t('username')}
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />
          <TextField
            fullWidth
            margin="normal"
            type="password"
            label={t('password')}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <Select
            fullWidth
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
            sx={{ mt: 2 }}
          >
            {ROLES.map((role) => (
              <MenuItem key={role} value={role}>{roleLabel(role)}</MenuItem>
            ))}
          </Select>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>{t('cancel')}</Button>
          <Button
            variant="contained"
            onClick={() => createMutation.mutate(form)}
            disabled={!form.username || !form.password}
          >
            {t('save')}
          </Button>
        </DialogActions>
      </Dialog>
    </PageShell>
  );
}
