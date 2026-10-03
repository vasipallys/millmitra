import { Alert } from '@mui/material';

const DemoBanner = ({ title = 'Preview', mode = 'actual' }) => (
  <Alert severity={mode === 'sample' ? 'warning' : 'info'} sx={{ mb: 3 }}>
    {mode === 'sample'
      ? `${title} is showing sample data for demonstration. Switch to View actual for mill records.`
      : `${title} figures come from mill records on Dashboard, Farmers, Inventory, Production, Sales, and Finance. Use View sample only when you need a demonstration.`}
  </Alert>
);

export default DemoBanner;
