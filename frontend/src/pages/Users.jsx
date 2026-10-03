import { useState } from 'react';
import {
  Alert,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
} from '@mui/material';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { PageHeader, PageLoading, PageShell } from '../components/common/PageChrome';
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
        actions={(
          <Button variant="contained" onClick={() => setOpen(true)}>{t('createUser')}</Button>
        )}
      />
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('username')}</TableCell>
            <TableCell>{t('role')}</TableCell>
            <TableCell>{t('active')}</TableCell>
            <TableCell />
          </TableRow>
        </TableHead>
        <TableBody>
          {users.map((user) => (
            <TableRow key={user.id}>
              <TableCell>{user.username}{user.first_name ? ` · ${user.first_name}` : ''}</TableCell>
              <TableCell>
                <Select
                  size="small"
                  value={user.role}
                  onChange={(event) => patchMutation.mutate({ id: user.id, payload: { role: event.target.value } })}
                >
                  {ROLES.map((role) => (
                    <MenuItem key={role} value={role}>{roleLabel(role)}</MenuItem>
                  ))}
                </Select>
              </TableCell>
              <TableCell>
                <Chip size="small" label={user.is_active ? t('active') : t('inactive')} color={user.is_active ? 'success' : 'default'} />
              </TableCell>
              <TableCell>
                <Button
                  size="small"
                  disabled={user.id === currentUser?.id && user.is_active}
                  onClick={() => patchMutation.mutate({
                    id: user.id,
                    payload: { is_active: !user.is_active },
                  })}
                >
                  {user.is_active ? t('deactivate') : t('activate')}
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

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
