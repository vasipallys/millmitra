import { useMemo, useState } from 'react';
import {
  Box, Card, CardContent, IconButton, Menu, MenuItem, Skeleton, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, TextField, Typography,
} from '@mui/material';
import MoreVert from '@mui/icons-material/MoreVert';
import { useI18n } from '../../i18n/I18nContext';
import { PageEmpty } from './PageChrome';

export default function DataTable({
  columns = [],
  rows = [],
  loading = false,
  searchKeys = [],
  emptyTitle,
  emptyDescription,
  emptyAction,
  rowActions,
  getRowId = (row, index) => row.id ?? index,
  testId,
}) {
  const { t } = useI18n();
  const [query, setQuery] = useState('');
  const [menu, setMenu] = useState({ anchor: null, row: null });

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return rows;
    return rows.filter((row) => {
      const keys = searchKeys.length ? searchKeys : columns.map((col) => col.field);
      return keys.some((key) => String(row[key] ?? '').toLowerCase().includes(needle));
    });
  }, [rows, query, searchKeys, columns]);

  if (loading) {
    return (
      <Box role="status" aria-live="polite">
        {[0, 1, 2].map((item) => (
          <Skeleton key={item} height={48} sx={{ mb: 1 }} />
        ))}
      </Box>
    );
  }

  if (!rows.length) {
    return (
      <PageEmpty
        title={emptyTitle || t('noRows')}
        description={emptyDescription}
        action={emptyAction}
      />
    );
  }

  return (
    <Box data-testid={testId}>
      <TextField
        size="small"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        label={t('searchTable')}
        sx={{ mb: 2, minWidth: { xs: '100%', sm: 260 } }}
      />
      <TableContainer sx={{ display: { xs: 'none', md: 'block' }, overflowX: 'auto' }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {columns.map((col) => (
                <TableCell key={col.field || col.label}>{col.label}</TableCell>
              ))}
              {rowActions && <TableCell align="right">{t('moreActions')}</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.map((row, index) => (
              <TableRow key={getRowId(row, index)} hover>
                {columns.map((col) => (
                  <TableCell key={col.field || col.label}>
                    {col.render ? col.render(row) : row[col.field]}
                  </TableCell>
                ))}
                {rowActions && (
                  <TableCell align="right">
                    <IconButton
                      aria-label={t('moreActions')}
                      onClick={(event) => setMenu({ anchor: event.currentTarget, row })}
                      sx={{ minWidth: 44, minHeight: 44 }}
                    >
                      <MoreVert />
                    </IconButton>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box data-testid="data-table-cards" sx={{ display: { xs: 'flex', md: 'none' }, flexDirection: 'column', gap: 1 }}>
        {filtered.map((row, index) => (
          <Card key={`card-${getRowId(row, index)}`} variant="outlined">
            <CardContent>
              {columns.map((col) => (
                <Box key={col.field || col.label} sx={{ mb: 0.75 }}>
                  <Typography component="div" variant="caption" color="text.secondary">{col.label}</Typography>
                  <Typography component="div" variant="body2">
                    {col.render ? col.render(row) : (row[col.field] ?? '—')}
                  </Typography>
                </Box>
              ))}
              {rowActions && (
                <IconButton
                  aria-label={t('moreActions')}
                  onClick={(event) => setMenu({ anchor: event.currentTarget, row })}
                >
                  <MoreVert />
                </IconButton>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>

      {!filtered.length && (
        <Typography color="text.secondary" sx={{ mt: 1 }}>{t('noRowsMatch')}</Typography>
      )}

      <Menu
        open={Boolean(menu.anchor)}
        anchorEl={menu.anchor}
        onClose={() => setMenu({ anchor: null, row: null })}
      >
        {(rowActions || []).map((action) => (
          <MenuItem
            key={typeof action.label === 'function' ? action.id || 'action' : action.label}
            disabled={action.disabled?.(menu.row)}
            onClick={() => {
              action.onClick?.(menu.row);
              setMenu({ anchor: null, row: null });
            }}
          >
            {typeof action.label === 'function' ? action.label(menu.row) : action.label}
          </MenuItem>
        ))}
      </Menu>
    </Box>
  );
}
