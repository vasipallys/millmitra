import { Alert } from '@mui/material';

const DemoBanner = ({ title = 'Preview' }) => (
  <Alert severity="info" sx={{ mb: 3 }}>
    {title} uses sample data for demonstration. Live mill records are on Dashboard,
    Farmers, Inventory, Production, Sales, Finance, Customers, and Settings.
  </Alert>
);

export default DemoBanner;
