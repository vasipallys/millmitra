-- Postgres RLS policies for shared-schema mill tables.
-- Do NOT run against SQLite. Apply only after migrating to Postgres.
-- Session GUC: SET LOCAL app.tenant_id = '<tenant uuid>';

-- Example for one table. Repeat the ENABLE + POLICY pattern for each tenant-owned table.

ALTER TABLE farmers ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS farmers_tenant_isolation ON farmers;
CREATE POLICY farmers_tenant_isolation ON farmers
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

ALTER TABLE lookup_options ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS lookup_options_tenant_isolation ON lookup_options;
CREATE POLICY lookup_options_tenant_isolation ON lookup_options
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

ALTER TABLE custom_field_values ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS custom_field_values_tenant_isolation ON custom_field_values;
CREATE POLICY custom_field_values_tenant_isolation ON custom_field_values
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

ALTER TABLE machine_telemetry ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS machine_telemetry_tenant_isolation ON machine_telemetry;
CREATE POLICY machine_telemetry_tenant_isolation ON machine_telemetry
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

ALTER TABLE iiot_devices ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS iiot_devices_tenant_isolation ON iiot_devices;
CREATE POLICY iiot_devices_tenant_isolation ON iiot_devices
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));

ALTER TABLE iiot_discrepancies ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS iiot_discrepancies_tenant_isolation ON iiot_discrepancies;
CREATE POLICY iiot_discrepancies_tenant_isolation ON iiot_discrepancies
    USING (tenant_id = current_setting('app.tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true));
