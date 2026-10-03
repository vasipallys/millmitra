import { useQuery } from 'react-query';
import { lookupService, optionLabel } from '../services/lookupService';
import { useI18n } from '../i18n/I18nContext';

export function useLookup(groupKey) {
  const { locale } = useI18n();
  const query = useQuery(
    ['lookups', groupKey],
    () => lookupService.listActive(groupKey),
    {
      enabled: Boolean(groupKey),
      staleTime: 30 * 1000,
      retry: 1,
    }
  );
  const options = query.data?.options || [];
  return {
    options,
    isLoading: query.isLoading,
    isError: Boolean(query.isError),
    refetch: query.refetch,
    labelOf: (option) => optionLabel(option, locale),
  };
}

export default useLookup;
