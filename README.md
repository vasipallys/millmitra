# MillMitra

Rice mill operations software: farmers and paddy intake, godown stock, milling batches, customers, sales orders, invoices, and payments. The office UI is React (Vite). The mill API is Flask + SQLAlchemy. Default local database is SQLite.

This is the same app you may see labeled **Smart Mill**, **Rice Mill Management System**, or **Rice Mill AI**.

**Start here**

| Audience | Document |
| --- | --- |
| Operators and office staff | [docs/USER_GUIDE.md](docs/USER_GUIDE.md) |
| Owners and managers (process, live vs preview) | [docs/BUSINESS.md](docs/BUSINESS.md) |
| Engineers (stack, APIs, data model, debt) | [docs/TECHNICAL.md](docs/TECHNICAL.md) |

Live mill-of-record screens: Dashboard, Farmers, Inventory, Production, Sales (orders), Finance, Customers, Settings. Sidebar **Preview** items (Analytics, Quality Control, Financial Intelligence, Compliance & GST) are sample UIs — do not treat them as official numbers.

---

## How to start (local)

You need **both** processes. The UI calls `http://localhost:5000/api`.

Use this repo’s venv only. Activating `D:\GenAi\ricemill\backend\venv` while working in millmitra will install packages in the wrong place.

### Backend

Python 3.13 on Windows is supported. Core ERP does **not** need TensorFlow.

```powershell
cd D:\GenAi\millmitra\backend
python -m venv venv
.\venv\Scripts\activate
python -c "import sys; print(sys.executable)"
# Must be ...\millmitra\backend\venv\Scripts\python.exe
python -m pip install -r requirements.txt
# Optional vision/NLP extras only:
# python -m pip install -r requirements-ml.txt
copy .env.example .env
python migrate_db.py
python app.py
```

- API: http://localhost:5000
- Liveness: http://localhost:5000/api/health
- Readiness (DB): http://localhost:5000/api/ready
- Database: SQLite `rice_mill_erp.db` unless you set `DATABASE_URL` (PostgreSQL via `psycopg[binary]`)
- If `SECRET_KEY` / `JWT_SECRET_KEY` are unset, Flask writes a key to `backend/instance/.secret_key` (gitignored) so tokens survive restarts

Do **not** `pip install` the kitchen-sink `requirements.txt` at the repo root on Python 3.13.

After `migrate_db.py`, these accounts exist if they were not already created:

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `admin123` | admin |
| `manager` | `manager123` | manager |
| `operator` | `operator123` | operator |

Emails such as `admin@ricemill.com` also work. Change these passwords on a real mill PC.

`migrate_db.py` drops and recreates tables it imported. Start `python app.py` once afterward so models such as `Invoice` and `StockMovement` are registered. Details: [docs/TECHNICAL.md](docs/TECHNICAL.md).

### Frontend

```powershell
cd D:\GenAi\millmitra\frontend
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:3000). If 3000 is taken, Vite uses the next free port — use that URL. Axios default is `http://localhost:5000/api` (`VITE_API_URL` overrides). CORS allows only `http://localhost:<port>` and `http://127.0.0.1:<port>`.

### Daily start

1. `backend`: activate `venv`, then `python app.py`
2. `frontend`: `npm run dev`
3. Log in on the **Password** tab (Voice / Biometric are experimental)

An optional FastAPI folder `ai-services/` (port 8000) is **not** required for farmer, stock, batch, sales, invoice, or payment work.

### Docker

`backend/Dockerfile`, `frontend/Dockerfile`, and `ai-services/Dockerfile` exist. There is no `docker-compose.yml` at this repo root. Prefer the manual start above.

---

## What is implemented

| Area | What staff actually do |
| --- | --- |
| Farmers | Register Farmer, contracts, Record Procurement, Approve/Verify (admin/manager), edit requests |
| Inventory | Add New Stock (paddy or product), Stock Movement, valuation, low-stock |
| Production | New Batch → Start Batch → Pause/Resume → Quality Test → Mark Complete |
| Sales | New Order (customer, variety, qty, price) |
| Finance | Create Invoice (deducts matching product stock), Record Payment |
| Dashboard / Settings | Live cards/widgets; mill settings saved to the user plus the browser |

Not mill-of-record: GST filing, quotations/leads, computer-vision grading, voice login, 2FA enrollment, double-entry books.

---

## Stack (short)

- Frontend: React 18, Vite 4, Material UI 5, React Query, Axios
- Backend: Flask 3.0.3, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS
- Auth: JWT (`identity` is `str(user.id)`); resolve users with `utils.current_user()`
- Cache: Redis optional; sessions fall back to the database

Repo layout, live API table, and data model: [docs/TECHNICAL.md](docs/TECHNICAL.md).

---

## Configuration

Useful env vars (see `backend/.env.example`):

```bash
DATABASE_URL=sqlite:///rice_mill_erp.db
# DATABASE_URL=postgresql://user:password@localhost:5432/rice_mill_erp
SECRET_KEY=          # optional; persisted under backend/instance/ if unset
JWT_SECRET_KEY=      # optional; defaults to SECRET_KEY
REDIS_URL=           # optional
FLASK_DEBUG=True
```

PostgreSQL is optional. Redis is optional.

---

## Verify (engineers)

```powershell
cd frontend
npm run lint
npm run build
```

```powershell
cd backend
# venv active
python -c "from app import create_app; create_app(); print('ok')"
```

There is no `npm test` script. Do not treat `backend/test_models.py` as a SQLite suite.

---

## Security notes

- JWT access tokens; login does not expose a working refresh endpoint
- CORS is localhost / 127.0.0.1 only
- Do not commit `.env` or `backend/instance/.secret_key`
- Input validation exists on mill writes; this is not a hardened production checklist (no claim of encryption at rest or bundled HTTPS)
