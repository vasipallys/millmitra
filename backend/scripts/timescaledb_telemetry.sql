-- TimescaleDB hypertable for machine_telemetry.
-- Requires Postgres + Timescale. SQLite stores the same rows without this.

CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT create_hypertable(
    'machine_telemetry',
    'time',
    if_not_exists => TRUE
);

CREATE INDEX IF NOT EXISTS ix_machine_telemetry_tenant_device_metric_time
    ON machine_telemetry (tenant_id, device_id, metric, time DESC);
