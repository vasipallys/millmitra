import { Button, ButtonGroup } from '@mui/material';

const PreviewModeToggle = ({ mode, onChange }) => (
  <ButtonGroup variant="outlined" size="small" aria-label="Preview data source">
    <Button
      variant={mode === 'actual' ? 'contained' : 'outlined'}
      onClick={() => onChange('actual')}
    >
      View actual
    </Button>
    <Button
      variant={mode === 'sample' ? 'contained' : 'outlined'}
      onClick={() => onChange('sample')}
    >
      View sample
    </Button>
  </ButtonGroup>
);

export default PreviewModeToggle;
