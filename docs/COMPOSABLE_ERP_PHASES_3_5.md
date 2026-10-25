# COMPOSABLE ERP — Phases 3–5 (what was built)

**Repo:** `D:\GenAi\millmitra`  
**Depends on:** [PHASE1](COMPOSABLE_ERP_PHASE1.md), [PHASE2](COMPOSABLE_ERP_PHASE2.md)

Flask + SQLAlchemy and React/Vite/MUI were **kept**. Review pass tightened isolation, tokens, validation, RTL, i18n keys, Kafka adapter, dynamic `/forms/:entity`, and Tailwind coexist mode.

Restart Flask after pulling this work so `/api/metadata` and `/api/iiot` exist.

---

## Built

- Kernel plugins: farmers, inventory, metadata, iiot. URLs `/api/farmer` and `/api/inventory` unchanged.
- Metadata + custom fields + form layouts + dashboard layouts + standalone `metadata_records`.
- IIoT ingest (device token, constant-time compare), manual entry, discrepancies, IndexedDB outbox with dedupe/retry.
- Kafka adapter (`KAFKA_BOOTSTRAP_SERVERS`) lazy-imports `kafka-python-ng` / `kafka`. Unit-tested with a fake producer. **Not integration-tested without a broker.**
- MUI RTL via `@emotion/cache` + `stylis-plugin-rtl` when locale is `ur`.
- Tailwind coexist: `tw-` prefix, **preflight off**, imported only on new composable pages. Existing mill pages are not restyled.
- Dynamic forms at `/forms/:entity`.

## Env vars

| Variable | Default | Effect |
|---|---|---|
| `MQTT_BROKER_URL` | unset | MQTT subscriber only if set |
| `IOT_DEMO_TOKEN` | `demo-device-token` | Seeded dryer token (never listed in GET /devices) |
| `IOT_RECONCILE_TOLERANCE` | `0.5` | Opens a discrepancy |
| `IOT_RECONCILE_WINDOW_MINUTES` | `60` | Compare window |
| `REDIS_URL` | unset | Optional Redis Streams bus |
| `KAFKA_BOOTSTRAP_SERVERS` | unset | Optional Kafka adapter |
| `Tenant.db_url` | empty | Optional per-tenant engine |

Scripts:

- `backend/scripts/postgres_rls.sql` — not applied on SQLite
- `backend/scripts/timescaledb_telemetry.sql` — not applied on SQLite
- `backend/scripts/check_tenant_db.py` — Postgres smoke; **not run here** (no Postgres)
- `backend/scripts/simulate_telemetry.py`

## Permissions

| Key | Who (default) | Routes |
|---|---|---|
| `metadata` | admin, manager | Form builder / field / entity writes |
| `iiot` | admin, manager, operator | IIoT page, manual; ingest is device token not JWT |
| `reconciliation` | admin, manager | Resolve discrepancy |

GET form/fields/values/records and PUT values / POST records / dashboard-layout are JWT-authenticated and tenant-scoped; they do not require the metadata admin key so operators can save custom fields and `/forms/:entity` records.

## Not verified here

- Live Kafka broker publish
- Live Timescale `create_hypertable`
- Live Postgres RLS against two DB roles (`check_tenant_db.py` not executed)
- Per-tenant **Postgres** engines (two **SQLite** URLs are tested)
- Pixel-identical screenshot archive from before Tailwind existed — MUI font/body probe is in `e2e/dashboard-mui-stable.spec.js`
