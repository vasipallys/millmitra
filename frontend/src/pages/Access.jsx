import { useState } from 'react';
import { Alert, Checkbox, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { PageHeader, PageLoading, PageShell } from '../components/common/PageChrome';
import { userAdminService } from '../services/userAdminService';
import { getApiErrorMessage } from '../utils/apiError';
import { useI18n } from '../i18n/I18nContext';

export default function Access() {
  const { t, roleLabel } = useI18n();
  const queryClient = useQueryClient();
  const [error, setError] = useState('');
  const matrixQuery = useQuery('access-matrix', () => userAdminService.getAccess(), { retry: false });
  const saveMutation = useMutation(
    (payload) => userAdminService.saveAccess(payload),
    {
      onSuccess: () => queryClient.invalidateQueries('access-matrix'),
      onError: (err) => setError(getApiErrorMessage(err, t('couldNotSaveAccess'))),
    }
  );

  if (matrixQuery.isLoading) {
    return <PageShell><PageLoading label={t('accessTitle')} /></PageShell>;
  }

  const roles = matrixQuery.data?.roles || [];
  const permissions = matrixQuery.data?.permissions || [];
  const matrix = matrixQuery.data?.matrix || {};

  return (
    <PageShell>
      <PageHeader title={t('accessTitle')} subtitle={t('accessSubtitle')} />
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>{t('role')}</TableCell>
            {permissions.map((perm) => (
              <TableCell key={perm} align="center">{t(`perm_${perm}`) === `perm_${perm}` ? perm : t(`perm_${perm}`)}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {roles.map((role) => (
            <TableRow key={role}>
              <TableCell>{roleLabel(role)}</TableCell>
              {permissions.map((perm) => (
                <TableCell key={`${role}-${perm}`} align="center">
                  <Checkbox
                    checked={Boolean(matrix[role]?.[perm])}
                    onChange={(event) => saveMutation.mutate({
                      role,
                      permission: perm,
                      allowed: event.target.checked,
                    })}
                    inputProps={{ 'aria-label': `${role} ${perm}` }}
                  />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </PageShell>
  );
}
