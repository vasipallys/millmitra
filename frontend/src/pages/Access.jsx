import { useState } from 'react';
import { Alert, Checkbox } from '@mui/material';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { PageHeader, PageLoading, PageShell } from '../components/common/PageChrome';
import DataTable from '../components/common/DataTable';
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
  const rows = roles.map((role) => ({ id: role, role, ...matrix[role] }));

  return (
    <PageShell>
      <PageHeader title={t('accessTitle')} subtitle={t('accessSubtitle')} pageKey="access" />
      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      <DataTable
        testId="access-matrix"
        rows={rows}
        searchKeys={['role']}
        emptyTitle={t('noRows')}
        columns={[
          { field: 'role', label: t('role'), render: (row) => roleLabel(row.role) },
          ...permissions.map((perm) => ({
            field: perm,
            label: t(`perm_${perm}`) === `perm_${perm}` ? perm : t(`perm_${perm}`),
            render: (row) => (
              <Checkbox
                checked={Boolean(matrix[row.role]?.[perm])}
                onChange={(event) => saveMutation.mutate({
                  role: row.role,
                  permission: perm,
                  allowed: event.target.checked,
                })}
                inputProps={{ 'aria-label': `${row.role} ${perm}` }}
              />
            ),
          })),
        ]}
      />
    </PageShell>
  );
}
