# MillMitra

Rice mill operations software: farmers and paddy intake, godown stock, milling batches, customers, sales orders, invoices, and payments. Office UI is React (Vite). Mill API is Flask + SQLAlchemy. Default local database is SQLite.

Same app you may see labeled **Smart Mill**, **Rice Mill Management System**, or **Rice Mill AI**.

**Start here**

| Audience | Document |
| --- | --- |
| Operators and office staff | [docs/USER_GUIDE.md](docs/USER_GUIDE.md) |
| Owners and managers | [docs/BUSINESS.md](docs/BUSINESS.md) — mill-day scenarios and Playwright map: [docs/BUSINESS_SCENARIOS.md](docs/BUSINESS_SCENARIOS.md) |
| Engineers | [docs/TECHNICAL.md](docs/TECHNICAL.md) |
| UX patterns | [docs/UX_GUIDELINES.md](docs/UX_GUIDELINES.md), audit notes: [docs/UX_AUDIT.md](docs/UX_AUDIT.md) |
| Composable ERP | [docs/COMPOSABLE_ERP_PHASE1.md](docs/COMPOSABLE_ERP_PHASE1.md), [PHASE2](docs/COMPOSABLE_ERP_PHASE2.md), [Phases 3–5](docs/COMPOSABLE_ERP_PHASES_3_5.md) |

**Where to start after login:** sidebar **Mill flow** (`/mill-flow`) — guided receive → mill → sell → pay, with a suggested next step from mill records. Or open Dashboard.

---

## Setup, install, and run

You need **both** processes. The UI calls `http://localhost:5000/api`.

Use **this** repo’s venv only: `D:\GenAi\millmitra\backend\venv`. Do **not** activate `ricemill\backend\venv`. Do **not** run `python app.py` with system Python (`C:\Python313\…`) on port 5000 — that process keeps old code in memory.

Python 3.13 is supported. Core ERP does **not** need TensorFlow. Install `backend/requirements.txt`. Do not install `ai-services/requirements.txt` or anything under `toberemoved/` for mill ERP.

### Prerequisites

| Need | Notes |
| --- | --- |
| Python **3.13** | `py -3.13 --version`. TensorFlow 2.13–2.15 have no cp313 wheels — do not pin `tensorflow<2.16`. |
| Node.js **18+** | `node -v`. Vite 4 / Playwright 1.63. |
| Git | Clone this repo. |
| Tesseract OCR (optional) | Farmer ID photos. UB Mannheim build; often `C:\Program Files\Tesseract-OCR\tesseract.exe` on PATH. App starts without it. |
| PostgreSQL (optional) | Only if `DATABASE_URL` is `postgresql://…`. Install `psycopg[binary]` from `requirements-optional.txt`. |
| Mosquitto (optional) | MQTT subscriber starts only when `MQTT_BROKER_URL` is set. |
| Redis (optional) | Sessions/cache/event bus. App starts without it. |
| Kafka (optional) | `KAFKA_BOOTSTRAP_SERVERS`; lazy `kafka-python-ng`. App starts without it. |
| Phoenix (optional) | Local OTLP UI on port 6006. `arize-phoenix==20.19.0` from the optional file. |

Optional folder `ai-services/` on port 8000 is **not** required for mill work.

### Clone

```powershell
git clone <this-repo-url> millmitra
cd millmitra
```

Linux / macOS: same `git clone` / `cd`.

### Backend venv and install

**Windows (PowerShell)**

```powershell
cd D:\GenAi\millmitra\backend
py -3.13 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
# Optional (Redis, MQTT, OCR, Postgres):
.\venv\Scripts\python.exe -m pip install -r requirements-optional.txt
# Tests:
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\venv\Scripts\python.exe migrate_db.py
```

**Linux / macOS**

```bash
cd backend
python3.13 -m venv venv
./venv/bin/python -m pip install --upgrade pip
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python -m pip install -r requirements-optional.txt   # optional
./venv/bin/python -m pip install -r requirements-dev.txt        # tests
cp .env.example .env
./venv/bin/python migrate_db.py
```

Uncomment groups in `requirements-optional.txt` for Kafka (`kafka-python-ng`), Phoenix (`arize-phoenix==20.19.0`), or ML. TensorFlow belongs on Python ≤ 3.12 only.

`python app.py` after `activate` is fine **only if** `python -c "import sys; print(sys.executable)"` prints `...\millmitra\backend\venv\Scripts\python.exe` (or `backend/venv/bin/python` on Unix).

### Environment variables

Copy `backend/.env.example` → `backend/.env` and `frontend/.env.example` → `frontend/.env` (Vite reads `VITE_*` at **dev-server start**). Flask loads `backend/.env` via `python-dotenv`.

If `SECRET_KEY` is unset, `config.py` writes a hex key to `backend/instance/.secret_key` (gitignored) and reuses it so JWTs survive restarts. Leave it unset locally. Do not commit `.env`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///rice_mill_erp.db` | SQLite file under `backend/` (or `backend/instance/` once migrated). **Do not** leave a Postgres URL with placeholder creds. |
| `SECRET_KEY` | persisted file | Flask secret. Set a long random value in production. |
| `JWT_SECRET_KEY` | same as `SECRET_KEY` | JWT signing key. Changing it logs everyone out. |
| `XAI_API_KEY` | unset | Grok / farmer ID extract. Alias: `GROK_API_KEY`. Optional. |
| `OTEL_ENABLED` | `true` | Backend tracing + `/api/telemetry` proxy. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://127.0.0.1:6006` | Phoenix UI/OTLP HTTP (traces at `/v1/traces`). Jaeger/collector: `http://127.0.0.1:4318`. |
| `OTEL_SERVICE_NAME` | `millmitra-api` | API resource name. |
| `MQTT_BROKER_URL` | unset | MQTT subscriber only if set (`mqtt://127.0.0.1:1883`). |
| `REDIS_URL` | unset | Optional Redis. App starts without it. |
| `SESSION_REDIS_URL` | `redis://localhost:6379/1` | Session store; falls back to the database if Redis is down. |
| `KAFKA_BOOTSTRAP_SERVERS` | unset | Optional Kafka adapter (`localhost:9092`). |
| `IOT_DEMO_TOKEN` | `demo-device-token` | Seeded dryer ingest token (never listed in GET /devices). |
| `IOT_RECONCILE_TOLERANCE` | `0.5` | Opens a discrepancy when mill vs device disagree. |
| `IOT_RECONCILE_WINDOW_MINUTES` | `60` | Compare window. |
| `VITE_API_URL` | `http://localhost:5000/api` | Axios base URL (frontend `.env`). |
| `VITE_OTEL_ENABLED` | `true` | Browser tracer. |

Turn tracing off: `OTEL_ENABLED=false` and `VITE_OTEL_ENABLED=false`.

### Run the API

**Windows (daily)**

```powershell
cd D:\GenAi\millmitra\backend
.\venv\Scripts\python.exe app.py
```

**Linux / macOS**

```bash
cd backend
./venv/bin/python app.py
```

- API: http://localhost:5000
- Liveness: `GET http://localhost:5000/api/health`
- Readiness: `GET http://localhost:5000/api/ready`
- After code changes (roles, dashboard, login), **stop** the old Flask window and start again with the venv command above

### Frontend install and run

Prefer `npm ci` (uses `package-lock.json`). Use `npm install` only if the lockfile is missing.

**Windows**

```powershell
cd D:\GenAi\millmitra\frontend
npm ci
npx playwright install chromium
npm run dev
```

**Linux / macOS**

```bash
cd frontend
npm ci
npx playwright install chromium
npm run dev
```

Scripts: `dev` (Vite :3000), `build`, `preview`, `lint`, `test:e2e`.

Open the URL Vite prints (often http://localhost:3000). If 3000 is taken, use the next free port Vite prints. The service worker is **not** registered in `npm run dev`.

### Daily start

1. Backend: `cd backend` then `.\venv\Scripts\python.exe app.py`
2. Frontend: `cd frontend` then `npm run dev`
3. Log in on the **Password** tab (Voice / Biometric are experimental and return 501)

### URLs

| What | URL |
| --- | --- |
| Office UI | http://localhost:3000 |
| Mill API | http://localhost:5000 |
| Health | http://localhost:5000/api/health |
| Phoenix (optional) | http://127.0.0.1:6006 |

### Demo logins

Seeded on app startup if missing (passwords of existing users are **not** reset):

| Username | Password | Role | Typical access |
| --- | --- | --- | --- |
| `admin` | `admin123` | admin | All modules, **Users**, **Access** |
| `manager` | `manager123` | manager | Operations + finance; no user admin |
| `operator` | `operator123` | operator | Mill flow, farmers, inventory, production |
| `quality` | `quality123` | quality_control | Production view + quality tests, Quality Control |
| `sales` | `sales123` | sales | Customers, sales orders, invoices |
| `accountant` | `accountant123` | accountant | Finance, invoices, payments; customers read |

Emails such as `admin@ricemill.com` also work. Change these passwords on a real mill PC.

After a restart with this venv, those demo accounts still sign into mill slug **`default`**. The JWT includes that mill’s `tenant_id`.

The **server** enforces the permission matrix. The sidebar hides items the role cannot use. A forbidden URL shows “You don’t have access.” Admin pages: **Users** (`/users`) and **Access** (`/access`).

### Tests

Backend tests use SQLite. Override `DATABASE_URL` so they never hit a leftover Postgres URL in `.env`. Disable OTEL so a down collector cannot slow the suite.

```powershell
cd D:\GenAi\millmitra\backend
$env:DATABASE_URL = "sqlite:///:memory:"
$env:OTEL_ENABLED = "false"
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Linux / macOS:

```bash
cd backend
DATABASE_URL=sqlite:///:memory: OTEL_ENABLED=false ./venv/bin/python -m unittest discover -s tests -p "test_*.py"
```

Frontend:

```powershell
cd D:\GenAi\millmitra\frontend
npm run lint
npm run build
```

Playwright (`npm run test:e2e`) **requires the real UI and API to be up**. `e2e/global-setup.js` fetches `http://127.0.0.1:3000` and `http://127.0.0.1:5000/api/health` and fails fast if either is down or is some other process. Do not start a second Vite/Flask if those ports are already MillMitra. Chromium: `npx playwright install chromium`.

```powershell
cd D:\GenAi\millmitra\frontend
npm run test:e2e
```

If Vite bound 3001 because 3000 was taken: `$env:PLAYWRIGHT_BASE_URL = "http://127.0.0.1:3001"`.

### IIoT simulator

HTTP ingest, no Mosquitto required:

```powershell
cd D:\GenAi\millmitra\backend
.\venv\Scripts\python.exe scripts\simulate_telemetry.py
```

### Phoenix (optional tracing)

Browser spans (`millmitra-web`) and Flask spans (`millmitra-api`) share one W3C `traceparent`. The UI does **not** call Phoenix (CORS). It posts OTLP to `POST /api/telemetry/v1/traces`; Flask forwards to the collector.

```powershell
# millmitra venv already has arize-phoenix 20.19.0. New venv: uncomment it in requirements-optional.txt
cd D:\GenAi\millmitra\backend
.\venv\Scripts\phoenix.exe serve
```

Open http://127.0.0.1:6006. Restart Flask and Vite. Sign in as `admin` / `admin123`. In Phoenix look for a `millmitra-web` HTTP span for `/auth/login` whose child is `millmitra-api` `POST /api/auth/login`. A down collector must not 500 login.

More in [docs/TECHNICAL.md](docs/TECHNICAL.md#11-opentelemetry).

### Troubleshooting

| Symptom | What to do |
| --- | --- |
| Port 3000 in use | Vite binds the next free port (`strictPort: false`). Open the URL it prints. Do not pin `server.hmr.port` — that caused `ERR_SERVER_ALREADY_LISTEN`. Playwright: set `PLAYWRIGHT_BASE_URL`. |
| Stale Flask on system Python | `Get-Process python` / `netstat -ano \| findstr :5000`. Stop the process whose path is `C:\Python313\python.exe`. Start with `.\venv\Scripts\python.exe app.py`. Confirm `python -c "import sys; print(sys.executable)"`. |
| `DATABASE_URL` Postgres with bad creds | Flask fails on connect. Set `DATABASE_URL=sqlite:///rice_mill_erp.db` in `backend/.env` (the example file now defaults to SQLite). Postgres needs a real server **and** `pip install -r requirements-optional.txt`. |
| TensorFlow on 3.13 | Not used. Do not `pip install tensorflow<2.16`. Core `requirements.txt` does not include it. Use Python 3.12 only if you truly need TF. |
| Vite HMR dead / overlay | Restart **only** `npm run dev`. Do not start a second Vite if :3000 is already this app. `npm run build` writes `frontend/dist/` and can knock over a Vite that is watching `dist`. |
| Login 401 after restart | `SECRET_KEY` changed (new `.env` placeholder vs `instance/.secret_key`). Keep one stable secret. |
| Playwright global-setup timeout | UI or API not reachable. Start both, or point `PLAYWRIGHT_BASE_URL` at the Vite URL. |
| OTEL noise / slow login | `OTEL_ENABLED=false` and `VITE_OTEL_ENABLED=false`. Phoenix 12.x with FastAPI 0.100 crashes — use 20.19.0. |
| `pip` conflict protobuf / OTEL | Core pins `protobuf==5.29.6` with OTEL API/SDK **1.45.0**. Do not mix in OTEL 1.32.1 from old docs. |

---

## Tenants (more than one mill)

A **tenant** is one mill / organization. All mills share **one** SQLite file (`backend/instance/rice_mill_erp.db`). Farmers, stock, lookups, invoices, and the Access matrix are **not** shared between mills.

The first mill is created on startup as slug `default`. There is **no** “Add mill” screen. Create a mill with `POST /api/tenants`. Staff with two memberships switch from the **mill name chip** in the navbar.

Operator steps (create, join, switch, backup): [USER_GUIDE — Add a mill](docs/USER_GUIDE.md#46-add-a-mill-tenant) and [Switch mill](docs/USER_GUIDE.md#47-switch-mill).  
API tables and who can create: [TECHNICAL.md](docs/TECHNICAL.md#tenants-apitenants).  
Architecture only: [docs/SAAS_ARCHITECTURE.md](docs/SAAS_ARCHITECTURE.md).

**Create a second mill (PowerShell, mill API on port 5000)**

```powershell
# New mill + new owner account (no token required)
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5000/api/tenants `
  -ContentType 'application/json' `
  -Body '{"name":"Mill B","slug":"mill-b","username":"adminb","password":"adminb123","email":"adminb@ricemill.com"}'

# Or, while signed in, attach this user as admin of the new mill
$login = Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5000/api/auth/login `
  -ContentType 'application/json' `
  -Body '{"username":"admin","password":"admin123","method":"password"}'
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5000/api/tenants `
  -ContentType 'application/json' `
  -Headers @{ Authorization = "Bearer $($login.access_token)" } `
  -Body '{"name":"Mill B","slug":"mill-b"}'
```

Then sign in as `adminb` / `adminb123`, or click the mill name in the top bar if your account now belongs to two mills.

Settings **Data & Backup** copies the **whole** database file (every mill), not one tenant.

---

## Language

English, Hindi, Telugu, and Urdu. Switcher on the **login** card and in the **navbar**. Stored in this browser as `localStorage` key `millmitra.language`. Urdu sets `document.dir=rtl`.

---

## What staff actually do

| Area | Live work |
| --- | --- |
| Mill flow | Guided paddy → batch → quality/complete → sell → invoice/pay. **Walk-in / later** files paddy without a farmer id |
| Farmers | Register, contracts, procurement, Approve/Verify (admin/manager) |
| Inventory | Add stock, movements, valuation |
| Production | New / start / pause / resume / quality test / complete |
| Sales | New Order (live order book) |
| Finance | Create Invoice, Record Payment |
| Dashboard / Settings | Live cards; mill settings |
| Preview group | Analytics, Quality Control, Financial Intelligence, Compliance & GST — **mill records by default**; use **View sample** only for demonstration |

Not mill-of-record: GST filing, quotations/leads, computer-vision grading, voice login, 2FA enrollment, double-entry books.

---

## Stack (short)

- Frontend: React 18, Vite 4, Material UI 5, React Query, Axios
- Backend: Flask 3.0.3, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS
- Auth: JWT (`identity` is `str(user.id)`); `utils.current_user()`
- Roles: stored matrix `role_permissions` (defaults if no row)
- Cache: Redis optional
- Tracing: OpenTelemetry → Phoenix or any OTLP HTTP collector
- Python deps: `backend/requirements.txt` (core), `requirements-optional.txt`, `requirements-dev.txt`

---

## Composable ERP (kernel, metadata, IIoT)

MillMitra now has a plugin kernel plus metadata and IIoT modules. Flask + MUI are unchanged. See:

- [docs/COMPOSABLE_ERP_PHASE1.md](docs/COMPOSABLE_ERP_PHASE1.md) — gap assessment
- [docs/COMPOSABLE_ERP_PHASE2.md](docs/COMPOSABLE_ERP_PHASE2.md) — locked stack
- [docs/COMPOSABLE_ERP_PHASES_3_5.md](docs/COMPOSABLE_ERP_PHASES_3_5.md) — what was built, env vars, simulator, remaining limits

Sidebar **IIoT** (`/iiot`) is for device readings and manual entry. **Form builder** (`/form-builder`) is admin/metadata. **Dashboard builder** (`/dashboard-builder`) saves widget layout. **Dynamic forms** (`/forms/:entity`) is tenant-scoped record entry (existing mill forms stay Formik). Restart Flask after pulling these changes so `/api/iiot` and `/api/metadata` exist.

Language **اردو** sets `document.dir=rtl` and switches the MUI Emotion RTL cache so Sidebar/Navbar mirror. Optional Kafka: set `KAFKA_BOOTSTRAP_SERVERS` (lazy `kafka-python-ng`; app starts without it).

UX: grouped sidebar, Ctrl+K find-a-page, Getting started on the Dashboard, Comfort mode in Settings, shared tables/status/formatters. See [docs/UX_GUIDELINES.md](docs/UX_GUIDELINES.md) and [docs/UX_AUDIT.md](docs/UX_AUDIT.md).

---

## Security notes

- JWT access tokens; login does not expose a working refresh endpoint
- CORS is localhost / 127.0.0.1 only
- Do not commit `.env` or `backend/instance/.secret_key`
- Do not log passwords
