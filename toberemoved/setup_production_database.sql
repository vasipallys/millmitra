-- Rice Mill ERP Production Database Setup
-- Run these commands as PostgreSQL superuser

-- Create database user
CREATE USER rice_mill_user WITH PASSWORD 'osTXGqPoL_PjhPiq5flFKA';

-- Create database
CREATE DATABASE rice_mill_erp_prod OWNER rice_mill_user;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE rice_mill_erp_prod TO rice_mill_user;

-- Connect to the database and grant schema permissions
\c rice_mill_erp_prod;
GRANT ALL ON SCHEMA public TO rice_mill_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rice_mill_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO rice_mill_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO rice_mill_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO rice_mill_user;
