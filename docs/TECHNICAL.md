# MillMitra — Technical document

For engineers working in `D:\GenAi\millmitra`. This matches the product as implemented: React/Vite office UI and Flask/SQLAlchemy mill API.

Related: [User Guide](USER_GUIDE.md), [Business document](BUSINESS.md).

---

## 1. Stack

| Layer | Technology |
| --- | --- |
| Frontend | React 18, Vite 4, Material UI 5, React Router 6, React Query 3, Axios |
| Backend | Python 3.13 (supported), Flask 3.0.3, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, Flask-Migrate |
| Database | SQLite file `rice_mill_erp.db` by default; PostgreSQL via `DATABASE_URL` and `psycopg[binary]` |
| Cache / sessions | Redis optional; login and sessions fall back to the database |
| Auth | JWT access token (`identity` is `str(user.id)`); password via Werkzeug hashes |

Optional folder `ai-services/` (FastAPI, port 8000) is **not required** for farmer, inventory, production, sales, finance, or dashboard.

TensorFlow is **not** a core dependency and is **not** imported by mill routes.

---

## 2. Repo layout

```
millmitra/
├── backend/
│   ├── app.py                 # create_app, CORS, blueprints, /api/health
│   ├── config.py              # env + persistent SECRET_KEY
│   ├── extensions.py          # db, jwt, migrate
│   ├── utils.py               # current_user / current_user_id
│   ├── migrate_db.py          # create_all + default users
│   ├── requirements.txt       # core ERP (3.13 / Windows)
│   ├── requirements-ml.txt    # optional extras
│   ├── models/                # package used at runtime
│   ├── models.py              # legacy re-export file (do not treat as source of truth)
│   ├── routes/                # Flask blueprints
│   ├── services/              # dashboard, session, quality helpers
│   ├── ai/                    # optional NLP/vision modules (guarded imports)
│   └── instance/              # gitignored; .secret_key lives here
├── frontend/
│   ├── src/App.jsx            # auth gate + routes
│   ├── src/pages/             # screens
│   ├── src/services/api.js    # Axios client
│   ├── src/services/*Service.js
│   └── package.json           # lint + build (no unit-test script)
├── docs/
│   ├── USER_GUIDE.md
│   ├── BUSINESS.md
│   └── TECHNICAL.md
├── ai-services/               # optional; not needed for core ERP
└── README.md
```

---

## 3. How to run

Use **this** repo’s venv. A common mistake is activating `D:\GenAi\ricemill\backend\venv` while the cwd is millmitra.

### Backend (Windows)

```powershell
cd D:\GenAi\millmitra\backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
# Optional vision/NLP extras only:
# .\venv\Scripts\python.exe -m pip install -r requirements-ml.txt
copy .env.example .env
.\venv\Scripts\python.exe migrate_db.py
.\venv\Scripts\python.exe app.py
```

Server: `http://localhost:5000`. Liveness: `GET /api/health`. Readiness: `GET /api/ready`.

Do **not** bind port 5000 with system Python (`C:\Python313\python.exe app.py`). That process keeps stale modules. After role/dashboard/login changes, stop Flask and start again with the venv executable.

Default DB: SQLite `sqlite:///rice_mill_erp.db`. Set `DATABASE_URL` for PostgreSQL.

Demo users are ensured on **startup** (`services/demo_users.py`) if missing — passwords of existing rows are not reset: `admin/admin123`, `manager/manager123`, `operator/operator123`, `quality/quality123`, `sales/sales123`, `accountant/accountant123` (emails `@ricemill.com`). Role defaults live in `services/access_control.py` and table `role_permissions`.

### Frontend

```powershell
cd D:\GenAi\millmitra\frontend
npm install
npm run dev
```

Vite prefers port **3000**. If that port is taken, it binds the next free port and prints the URL. Do not pin HMR to another port. `npm run dev` does **not** register `public/sw.js` (`isDevRuntime()` in `usePWA.js` / `pwaRuntime.js`).

i18n: React context + `src/i18n/translations.js` (en / hi / te). Locale key `millmitra.language`.

Axios `baseURL` is `import.meta.env.VITE_API_URL` or `http://localhost:5000/api`.

### Docker

`backend/Dockerfile`, `frontend/Dockerfile`, and `ai-services/Dockerfile` exist. There is **no** `docker-compose.yml` at the MillMitra repo root (a nested `rice-mill-ai/` folder has its own compose). Local development is the venv + `npm run dev` path above.

---

## 4. Architecture

```
Browser (React pages)
    │  Authorization: Bearer <JWT>
    ▼
Flask app (backend/app.py)
    ├── JWT + session middleware
    ├── Blueprints under /api/...
    ├── SQLAlchemy models (models/)
    └── Services (dashboard_service, session_manager, …)
            │
            ▼
     SQLite or PostgreSQL
     Redis (optional)
```

- **Routes** validate JWT (most mutating and live GETs), load `current_user()`, talk to models.
- **Access guard** (`services/access_control.py`, `register_access_guard`) maps `/api/...` prefixes to permission keys and returns **403** when the stored matrix (or defaults) deny the call. Quality may write quality-test paths; other production writes are denied for `quality_control`.
- **Unused “AI service” routes** (many inventory/customer extras) return empty stubs so they do not 500.
- **Frontend** pages call `src/services/*.js` or `api.js`. React Query wraps list loads. `queryFn` must be an arrow so React Query context is not sent as HTTP params.

---

## 5. Auth, CORS, secrets

### JWT

- Login: `POST /api/auth/login` with `username` (username, email, or phone) and `password`.
- Token identity is **`str(user.id)`**. Always resolve users with `utils.current_user()` / `current_user_id()` (int), never `User.query.get(get_jwt_identity())` with the raw string.
- Access expiry: 8 hours on the login call; config default `JWT_ACCESS_TOKEN_EXPIRES` is 24 hours if unset on other tokens.
- `GET /api/auth/me` confirms the token.
- `POST /api/auth/logout` invalidates the optional session token; JWT is discarded client-side.

Frontend: token in `localStorage.token`. Axios attaches it. On HTTP 401 (except login/me/logout/OTP), token is cleared; full-page redirect to `/login` is skipped for those auth URLs.

Session store (`session_manager`): Redis if `SESSION_REDIS_URL` works; else `user_sessions` table. Session create failure must not fail login (rollback + JWT still issued).

### Secrets

If `SECRET_KEY` is unset, `config.py` writes a hex key to `backend/instance/.secret_key` (gitignored) and reuses it across process restarts. `JWT_SECRET_KEY` defaults to the same value. First start after this behavior was added logs everyone out once; later restarts keep tokens.

Do not commit `.env` or `instance/.secret_key`.

### CORS

Allowed origins: `http://localhost:<any port>` and `http://127.0.0.1:<any port>` only. Local Vite on 3000/3001/3002 works. There is no `*` default.

---

## 6. Live API surface

Prefix `/api` unless noted. JWT required except login, username suggest, OTP verify, and health.

### Auth (`/api/auth`)

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/login` | Password; returns `access_token`, `user` (includes `role`, `permissions`), optional `session_token`. Voice/biometric methods on this route return **501** |
| GET | `/me` | Current user + `permissions` |
| POST | `/logout` | End DB/Redis session |
| POST | `/verify-otp` | OTP check if login asked for 2FA |
| POST | `/suggest-username` | Exists for registration-style hints; **Login does not treat these as sign-in accounts** |
| POST | `/voice-login` | Experimental |

### Dashboard (`/api/dashboard`)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/overview` | Summary cards (production, quality, inventory value, pending orders, active farmers) |
| GET | `/widgets` | Role-based widgets from live tables |
| GET | `/insights` | Insight list (may be empty) |
| GET | `/alerts` | Operational alerts |
| GET | `/metrics/production` | Daily production series |
| GET | `/metrics/quality` | Quality series |
| GET | `/metrics/inventory` | Inventory metrics |
| GET | `/metrics/financial` | Financial metrics |
| GET | `/predictions` | Stub/optional |
| POST | `/customize` | Persist widget prefs on the user |

### Farmers (`/api/farmer`)

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/register` | Create farmer (name, phone, village, district, state required) |
| GET | `/list` | List farmers |
| GET | `/<id>` | Farmer detail |
| PUT | `/<id>` | Submit edit request (not always an immediate in-place edit) |
| PUT | `/<id>/verify` | Verify (admin/manager) |
| GET/POST | `/contracts` | List / create contracts |
| PUT | `/contracts/<id>` | Update contract |
| GET/POST | `/procurements` | List / record purchases |
| GET | `/edit-requests` | Pending profile edits |
| POST | `/edit-requests/<id>/approve` | Approve |
| POST | `/edit-requests/<id>/reject` | Reject |
| GET | `/analytics/overview` | Farmer totals |
| POST | `/payments` | Farmer payout (reduces `outstanding_amount`); no dedicated mill-office button |

### Inventory (`/api/inventory`)

Live UI uses these (not `/paddy-stock` stubs):

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/paddy` | List / add paddy lots |
| PUT | `/paddy/<id>` | Update lot |
| GET/POST | `/products` | List / add product lots |
| PUT | `/products/<id>` | Update lot |
| GET | `/analytics` | Overview / valuation helpers |
| GET | `/valuation` | Stock value |
| GET | `/alerts/low-stock` | Low remaining qty |
| GET | `/movements` | Persisted `stock_movements` (what the Inventory UI lists) |
| POST | `/transactions` | Apply in/out/transfer and persist a `StockMovement` |
| GET | `/transactions` | Older list via `inventory_service` (not the live movement table) |

Many other `/inventory/*` paths exist as stubs for unused AI screens. Do not document them as mill APIs.

### Production (`/api/production`)

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/batches` | List / create (**planned**) |
| GET | `/batches/<id>` | Detail + quality tests |
| POST | `/batches/<id>/start` | planned/paused → in_progress; deduct paddy on first start |
| POST | `/batches/<id>/pause` | → paused |
| POST | `/batches/<id>/resume` | → in_progress |
| POST | `/batches/<id>/complete` | → completed; rice_output > 0 adds product stock |
| GET/POST | `/quality-tests` | List / create tests |
| GET | `/current-status` | Active/planned counts |
| GET | `/dashboard` | Production dashboard payload |
| GET | `/analytics` | Yield / batch summaries |

Statuses: `planned`, `in_progress`, `paused`, `completed` (also `started` accepted on complete).

### Sales (`/api/sales`)

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/customers` | List / create (also used from Sales New Order) |
| GET | `/customers/<id>` | Detail |
| GET/POST | `/orders` | List / create (`customer_id` required; items JSON) |
| PUT | `/orders/<id>/status` | Update status |
| GET | `/analytics` | Revenue / order counts |
| GET | `/dashboard` | Sales dashboard |

`GET /quotations` and `GET /leads` return empty lists. `POST` and status updates return **501** (`not enabled`). The Sales page does not offer them.

### Customers (`/api/customers`)

Live: `GET/POST /`, `GET/PUT /<id>` for CRM. Nested interactions/segments/campaigns are largely stubs.

### Finance (`/api/finance`)

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/invoices` | List / create; create deducts matching product stock |
| POST | `/payments` | Record payment; optional invoice → status `paid` |
| GET | `/financial-summary` | Revenue, expenses, profit, AR |
| GET | `/summary` | Alias of financial-summary |
| GET | `/cash-flow` | From invoices/payments |
| GET | `/accounts-receivable` | Unpaid invoices |
| GET | `/aging-report` | AR aging buckets |

`POST /accounts` and `/journal-entries` hit stubs.

### User / settings

Blueprint has **no** `/api` prefix on the blueprint; paths are absolute:

| Method | Path | Purpose |
| --- | --- | --- |
| GET/PUT | `/api/user/profile` | JWT profile |
| POST | `/api/user/change-password` | Verify current password |
| PUT | `/api/user/preferences` | JSON prefs |
| GET/PUT | `/api/user/mill-settings` | Mill business settings on `User.preferences` |
| GET | `/api/user/activity` | AuthLog rows |
| GET | `/api/user/sessions` | Active UserSession rows |
| DELETE | `/api/user/delete-session/<id>` | Deactivate own session |
| POST | `/api/user/enable-2fa` / `disable-2fa` | 501, not configured |

### Users and access (`/api`, admin / `users` permission)

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/users` | List users |
| POST | `/users` | Create user (username, password, role) |
| PATCH | `/users/<id>` | Change role or `is_active` (cannot deactivate self) |
| GET | `/access` | Permission matrix |
| PUT | `/access` | Toggle `{ role, permission, allowed }` |

### Health

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Liveness: process is up. Does not check the database. |
| GET | `/api/ready` | Readiness: `SELECT 1` against the configured DB. `503` if the DB is down. |

Requests log `method`, `path`, `status`, `duration_ms`, and `request_id` (no passwords or tokens). Unexpected 500s return `{ success: false, message, error_id }` and log the traceback.

Registered but **not** mill-of-record: biometric, quality-vision, financial-intelligence, compliance/gst, analytics/reporting, supply-chain, logistics, compliance, quality (standards), session extras. Preview UI may call them; they must not be treated as source of truth.

---

## 7. Data model overview

Runtime models live under `backend/models/`.

```
User ──┬── Farmer (created_by)
       ├── PaddyStock (farmer_id, remaining_quantity)
       ├── ProductStock (variety, quantity)
       ├── StockMovement (stock_kind, stock_id, movement_type, quantity)
       ├── ProductionBatch (paddy_stock_id, paddy_input_quantity, rice_output, status)
       ├── QualityTest (batch_id)
       ├── Customer
       ├── SalesOrder (customer_id, items JSON)
       ├── Invoice (customer_id, items JSON, status)
       └── Payment
```

Also: `FarmerContract`, `PaddyProcurement`, `FarmerEditRequest`, `AuthLog`, `UserSession`.

Invoice and sales order lines are **JSON**, not line tables. Product stock match on invoice create is by product name / variety string.

`backend/models.py` re-exports a subset. Prefer `from models.inventory import …` / package `__init__`. Having both the package and `models.py` is debt (see §10).

---

## 8. Frontend routing and API client

`App.jsx` blocks the shell until `authService.getCurrentUser()` succeeds (or no token). Unauthenticated users only see `Login`.

| Path | Page | Live? |
| --- | --- | --- |
| `/dashboard` | Dashboard | Yes |
| `/mill-flow` | MillFlow | Yes (reuses farmer/inventory/production/sales/finance APIs) |
| `/farmers/*` | Farmers | Yes |
| `/inventory/*` | Inventory | Yes |
| `/production/*` | Production | Yes |
| `/sales/*` | Sales | Yes (orders) |
| `/finance/*` | Finance | Yes |
| `/customers/*` | Customers | Yes |
| `/settings` | Settings | Yes (localStorage + mill-settings) |
| `/users` | Users | Admin only |
| `/access` | Access | Admin only |
| `/analytics` | Analytics | Preview; **live mill records by default** (`usePreviewMode`, `View sample`) |
| `/quality-control` | QualityControl | Preview; live default; official tests stay on Production |
| `/financial-intelligence` | FinancialIntelligence | Preview; live default |
| `/compliance-gst` | ComplianceGST | Preview; live default; does not file GST |
| `/analytics-reporting` | AnalyticsReporting | Preview, not in sidebar |
| `/notifications` | Notifications | In-app list |

Sidebar: core items first (filtered by `user.permissions`); Preview group without a Sample-only chip. `RequireAccess` shows a denied panel on a forbidden URL.

Clients:

- `src/services/api.js` — Axios + `productionAPI`, `inventoryAPI`, `salesAPI`
- `authService.js`, `inventoryService.js`, `financeService.js`, `dashboardService.js`, farmer/customer services

401 interceptor must not redirect during login.

---

## 9. How to verify

From `frontend`:

```powershell
npm run lint    # eslint src
npm run build   # vite production bundle
```

From `backend` (venv activated):

```powershell
python -c "from app import create_app; create_app(); print('ok')"
```

There is no reliable `frontend` unit-test script. Many files under `toberemoved/` and `docs/toberemoved/` are not the active suite. `backend/test_models.py` assumes PostgreSQL `information_schema` and is a poor SQLite check.

---

## 10. Known technical debt

- **`models.py` vs `models/`** — runtime uses the package; the file is a leftover re-export.
- **Stub routes** — inventory AI, customer campaigns, finance journal, quotations/leads. Safe empties, not features.
- **Preview screens** — same pages; default to mill records; `View sample` is opt-in (`sessionStorage` `millmitra.previewMode.<page>`).
- **Optional ML** — `requirements-ml.txt`; `enhanced_nlp` / OpenCV imports are guarded so the app starts without them.
- **JSON line items** — hard to query; invoice stock match is stringly typed.
- **Role UI** — sidebar and route guard hide by permission; server `before_request` enforces the matrix. Farmer verify remains admin/manager. Admin can change the stored matrix.
- **Partial payment** sets invoice `paid`.
- **Dual schema names** — routes use `paddy_input_quantity` / `rice_output` / `business_name`; older services used other names. Live routes follow the models.
- **Kitchen-sink root `requirements.txt`** — do not `pip install` that file on 3.13; use `backend/requirements.txt`.
- **`migrate_db.py` imports a subset of models** — it creates `User`, farmer/inventory/production/sales/finance tables it imported, and default users. `Invoice` lives in `models/financial.py` and `StockMovement` is not imported there. After a wipe-and-recreate, start the Flask app once (`create_app` imports those models) or add the missing imports before relying on invoices/movements.
- **GET `/inventory/transactions`** still goes through the older inventory service; the UI uses **GET `/movements`**.

---

## 11. Claims omitted on purpose

Not implemented as described in older README/API lists: JWT refresh endpoint, encryption at rest, production HTTPS, barcode scanning, FAISS-as-required, TensorFlow, working 2FA enrollment, GST filing, `npm test`. User list/create/role and the access matrix **are** implemented (`/api/users`, `/api/access`).

Dashboard `GET /api/dashboard/overview` for manager uses role helpers in `dashboard_service.py`. A Flask process started before that change still 500s until restart.
