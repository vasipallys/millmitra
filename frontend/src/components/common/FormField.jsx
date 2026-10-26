import { FormHelperText, TextField } from '@mui/material';
import { useI18n } from '../../i18n/I18nContext';

export default function FormField({
  label,
  required = false,
  help,
  error,
  value,
  onChange,
  onBlur,
  ...rest
}) {
  const { t } = useI18n();
  const shownError = Boolean(error);
  return (
    <>
      <TextField
        fullWidth
        margin="normal"
        label={label}
        required={required}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        error={shownError}
        helperText={shownError ? error : help}
        inputProps={{
          'aria-required': required || undefined,
          'aria-invalid': shownError || undefined,
        }}
        {...rest}
      />
      {required && (
        <FormHelperText sx={{
          position: 'absolute',
          width: 1,
          height: 1,
          overflow: 'hidden',
          clip: 'rect(0 0 0 0)',
        }}
        >
          {t('requiredField')}
        </FormHelperText>
      )}
    </>
  );
}
