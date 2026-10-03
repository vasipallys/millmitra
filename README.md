# MillMitra

Rice mill operations software: farmers and paddy intake, godown stock, milling batches, customers, sales orders, invoices, and payments. Office UI is React (Vite). Mill API is Flask + SQLAlchemy. Default local database is SQLite.

Same app you may see labeled **Smart Mill**, **Rice Mill Management System**, or **Rice Mill AI**.

**Start here**

| Audience | Document |
| --- | --- |
| Operators and office staff | [docs/USER_GUIDE.md](docs/USER_GUIDE.md) |
| Owners and managers | [docs/BUSINESS.md](docs/BUSINESS.md) |
| Engineers | [docs/TECHNICAL.md](docs/TECHNICAL.md) |

**Where to start after login:** sidebar **Mill flow** (`/mill-flow`) — guided receive → mill → sell → pay, with a suggested next step from mill records. Or open Dashboard.

---

## How to start (local)

You need **both** processes. The UI calls `http://localhost:5000/api`.

Use **this** repo’s venv only: `D:\GenAi\millmitra\backend\venv`. Do **not** activate `ricemill\backend\venv`. Do **not** run `python app.py` with system Python (`C:\Python313\…`) on port 5000 — that process keeps old code in memory.

Python 3.13 is supported. Core ERP does **not** need TensorFlow. Use `backend/requirements.txt`, not the kitchen-sink file at the repo root.

### Backend (first time)

```powershell
cd D:\GenAi\millmitra\backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.\venv\Scripts\python.exe migrate_db.py
.\venv\Scripts\python.exe app.py
```

### Backend (daily)

```powershell
cd D:\GenAi\millmitra\backend
.\venv\Scripts\python.exe app.py
```

- API: http://localhost:5000
- Liveness: `GET http://localhost:5000/api/health`
- Readiness: `GET http://localhost:5000/api/ready`
- Database: SQLite `rice_mill_erp.db` unless `DATABASE_URL` is set
- After code changes (roles, dashboard, login), **stop** the old Flask window and start again with the venv command above

`python app.py` after `activate` is fine **only if** `python -c "import sys; print(sys.executable)"` prints `...\millmitra\backend\venv\Scripts\python.exe`.

### Frontend

```powershell
cd D:\GenAi\millmitra\frontend
npm install
npm run dev
```

Open the URL Vite prints (often http://localhost:3000). If 3000 is taken, use the next free port Vite prints. The service worker is **not** registered in `npm run dev`.

### Daily start

1. Backend: `cd backend` then `.\venv\Scripts\python.exe app.py`
2. Frontend: `cd frontend` then `npm run dev`
3. Log in on the **Password** tab (Voice / Biometric are experimental and return 501)

Optional `ai-services/` on port 8000 is **not** required for mill work.

---

## Demo logins

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

English, Hindi, and Telugu. Switcher on the **login** card and in the **navbar**. Stored in this browser as `localStorage` key `millmitra.language`.

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

---

## Verify (engineers)

```powershell
cd frontend
npm run lint
npm run build
```

```powershell
cd backend
.\venv\Scripts\python.exe -c "from app import create_app; create_app(); print('ok')"
```

---

## Security notes

- JWT access tokens; login does not expose a working refresh endpoint
- CORS is localhost / 127.0.0.1 only
- Do not commit `.env` or `backend/instance/.secret_key`
- Do not log passwords
