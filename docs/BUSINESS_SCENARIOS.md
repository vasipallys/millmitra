# MillMitra — Business scenarios and Playwright coverage

This document maps **who does what** in the live mill product to expected results, forbidden outcomes, and the Playwright specs under `frontend/e2e`. It is written from the product as it works today (shared-schema tenants, JWT `tenant_id`, demo mill slug `default`).

Related: [BUSINESS.md](BUSINESS.md) (what the mill is), [USER_GUIDE.md](USER_GUIDE.md) (click-by-click), [TECHNICAL.md](TECHNICAL.md) (API).

Run the suite (UI on `:3000`, API on `:5000`, do not start a second server if those ports are already taken):

```powershell
cd D:\GenAi\millmitra\frontend
npm run test:e2e
```

Override URLs with `PLAYWRIGHT_BASE_URL` (default `http://127.0.0.1:3000`) and `PLAYWRIGHT_API_URL` (default `http://127.0.0.1:5000`). Tests fail fast if either process is down.

Demo accounts stay on the **default** mill: `admin/admin123`, `manager/manager123`, `operator/operator123`, `quality/quality123`, `sales/sales123`, `accountant/accountant123`. Specs prefix new storage notes with `pw-` and **do not delete** the database.

---

## Mill-day narrative (receive → mill → sell → pay)

This is the office story the product is built around. Playwright automates the **safe prefix** (login, access, dashboard next action, walk-in receive paddy, inventory dropdowns, language, notifications, farmer validation, sales visibility, logout). Later steps stay documented so staff and testers share one script.

| Time | Who | Goal | Product steps | Expected result | Must never happen |
| --- | --- | --- | --- | --- | --- |
| Gate, morning | Operator or manager | Identify the supplier | **Farmers → Register Farmer**, or Mill flow **Walk-in / later** | Farmer exists or the mill walk-in farmer is used on save | Do not invent a farmer from another mill; do not store the ID photo; do not treat a 12-digit Aadhaar as a phone |
| Gate, morning | Operator | Weigh and file paddy | **Mill flow → Start from receive paddy**: Walk-in, variety from lookup, kg, ₹/kg, storage `pw-…` → **Save paddy and continue** | New paddy lot on this mill; wizard moves to **Start batch** | Do not write stock to another tenant; do not crash the wizard |
| Floor | Operator / quality | Mill the lot | Mill flow **Start batch** (or **Production → New Batch**), start, optional quality test, mark complete with rice kg | Open batch, then product stock increases | Quality must not complete finance steps; operator must not record invoice payments |
| Office, afternoon | Sales | Book the sale | **Sales → New Order** (or Mill flow sell step) for a customer on this mill | Order appears on Sales | Operator must not open Sales to create orders |
| Office, afternoon | Accountant / manager / admin | Bill and collect | **Finance → Create Invoice**, then **Record Payment** | Invoice and payment on this mill | Operator must not pay invoices; do not apply cash to another mill’s invoice |
| Close | Any signed-in user | Leave a shared PC | Avatar → **Logout** | Login screen; token cleared | Do not leave a working session on the shared browser |

E2E that covers the automated prefix: `mill-flow.spec.js` (receive), `farmer.spec.js` (register dialog), `inventory.spec.js` (Add Stock lookups), `sales.spec.js` + `access.spec.js` (who may sell or see Finance), `logout.spec.js`.

---

## Scenario catalog

### 1. Sign in and reject a wrong password

- **Who:** Any mill user (tested as `admin`).
- **Goal:** Open the mill on the Password tab; keep strangers out.
- **Steps:** Open the UI → Password tab → username + password → **Login**. Repeat with a wrong password.
- **Expected:** Correct demo password reaches the signed-in shell (dashboard next-action). Wrong password shows **Username or password is not recognized** (or the same phrase in the current language). Voice / Biometric tabs stay experimental and are not required.
- **Must never happen:** A 500 on login because Phoenix is down; leaking the password in the URL or console as a success path; treating a 401 as a generic crash.
- **Playwright:** `e2e/login.spec.js`

### 2. Role walls (operator vs admin)

- **Who:** `operator` vs `admin`.
- **Goal:** Floor staff work Farmers / Inventory / Mill flow; only admin maintains Users and Dropdown lists.
- **Steps:** Sign in as operator → inspect sidebar → open `/finance` directly. Sign in as admin → confirm **Users** and **Dropdown lists**.
- **Expected:** Operator sidebar has Farmers and hides **Finance**, **Users**, and **Dropdown lists**. Direct `/finance` shows **You don't have access**. Admin sees Users and Dropdown lists.
- **Must never happen:** Operator paying invoices or editing the Access matrix; UI hiding a link but the page still loading live finance data for that role.
- **Playwright:** `e2e/access.spec.js`

### 3. Dashboard next action

- **Who:** Operator (also works for admin/manager).
- **Goal:** Know the next mill job without hunting menus.
- **Steps:** Sign in → **Smart Dashboard**.
- **Expected:** A **Next step** card with one of **Register farmer**, **Add stock**, or **Open Mill flow** (empty mill vs mill that already has lots).
- **Must never happen:** Fake production numbers presented as live when the mill is empty; a next-action button that 404s.
- **Playwright:** `e2e/dashboard.spec.js`

### 4. Mill flow — walk-in receive paddy

- **Who:** Operator (has `mill_flow` + `inventory` + `farmers`).
- **Goal:** File a walk-in paddy lot and continue the guided day.
- **Steps:** `/mill-flow` → **Start from receive paddy** → farmer **Walk-in / later** (`walk_in`) → first real **Variety** lookup option → quantity, price, storage `pw-…` → **Save paddy and continue**.
- **Expected:** No crash. Wizard shows **2. Start batch**, or a clear field error if the API rejects the lot. Stock notes/locations use the `pw-` prefix so reruns are identifiable.
- **Must never happen:** Selecting an empty farmer value that blocks the dropdown; writing the lot onto another tenant; advancing the operator into **Create invoice / Record payment**.
- **Playwright:** `e2e/mill-flow.spec.js`  
  Later mill-day steps (batch → quality → sell → invoice) are in the narrative table above; they are not fully automated so operator tests never attempt payments.

### 5. Inventory Add Stock lookups

- **Who:** Operator or manager.
- **Goal:** Add godown stock using admin-configured lists, not hardcoded types.
- **Steps:** **Inventory → Add Stock** → switch **Stock type** to product when that option exists → open **Product type** (or paddy variety if the mill only has paddy).
- **Expected:** After load, the type dropdown has at least one API option. Empty-after-load shows the admin helper, not a silent blank control.
- **Must never happen:** Saving stock with a type the lookup API did not return; cross-tenant lookup values.
- **Playwright:** `e2e/inventory.spec.js`

### 6. Language — Telugu then English

- **Who:** Any signed-in user (tested as operator).
- **Goal:** Office staff can work in Telugu without changing stored role keys or API payloads.
- **Steps:** Navbar **Language → తెలుగు** → confirm sidebar **రైతులు** or **డాష్బోర్డ్** → switch back to **English** → **Farmers**.
- **Expected:** Visible nav labels change. Rice variety names and typed data may stay as stored.
- **Must never happen:** Language switch changing farmer IDs, permissions, or tenant; untranslated crash.
- **Playwright:** `e2e/language.spec.js`

### 7. Notifications bell

- **Who:** Any signed-in user.
- **Goal:** See in-app notices without breaking the shell.
- **Steps:** Navbar bell (**Notifications**).
- **Expected:** Panel opens (list, empty state, or search). No page error.
- **Must never happen:** Unauthenticated sample cards (fake PB001 / Basmati) presented as this mill’s live feed; a thrown exception that blanks the app.
- **Playwright:** `e2e/notifications.spec.js`

### 8. Register farmer — validation (no Grok dependency)

- **Who:** Operator or manager (`farmers`).
- **Goal:** Open registration and see required-field rules before save.
- **Steps:** **Farmers → Register Farmer**. If **Next** is enabled on an empty step, click it; otherwise the dialog already shows step-0 errors. Optional: upload a 1×1 PNG. Do not require Grok or Tesseract to fill fields.
- **Expected:** **Register New Farmer** dialog. Validation such as **Registration Form Validation** / **Name is required…**. Upload may show **Filled using Grok**, **Filled using Tesseract**, or “no details could be read” — empty OCR must not fail the suite. The picture is not stored.
- **Must never happen:** Treating a 12-digit Aadhaar as phone; auto-submitting the farmer from OCR; logging the ID image or Aadhaar.
- **Playwright:** `e2e/farmer.spec.js`

### 9. Sales visibility

- **Who:** `sales` vs `operator`.
- **Goal:** Sales books orders; floor staff do not.
- **Steps:** Sign in as sales → `/sales`. Sign in as operator → sidebar and `/sales`.
- **Expected:** Sales sees **Sales Management**. Operator has no Sales nav item; `/sales` shows **You don't have access**.
- **Must never happen:** Operator creating orders or seeing another mill’s customers through a guessable URL.
- **Playwright:** `e2e/sales.spec.js`

### 10. Logout

- **Who:** Shared-PC users (tested as operator after a form login).
- **Goal:** End the session.
- **Steps:** Avatar → **Logout**.
- **Expected:** **Sign in to MillMitra** and the **Login** button. Dashboard is gone.
- **Must never happen:** A still-valid token in `localStorage` that reopens the mill on refresh without a password.
- **Playwright:** `e2e/logout.spec.js`

---

## Roles at a glance (default mill)

| Role | Typical screens | Must not do |
| --- | --- | --- |
| Admin | All core + Users, Access, Dropdown lists | Must not share the admin password on the floor PC |
| Manager | Core mill + finance/sales as granted; not Users/lookups by default | Must not edit another mill’s Access matrix |
| Operator | Dashboard, Mill flow, Farmers, Inventory, Production, Settings | Finance invoices/payments, Users, Sales orders |
| Quality | Production / quality | Sell or pay |
| Sales | Sales, customers | Operator floor intake is not required |
| Accountant | Finance, customers | Creating mill users |

Cross-tenant rule for every scenario: records (farmers, stock, lookups, invoices, role permissions) stay on the signed-in mill. People (usernames) are global; a **membership** chooses the mill and role. The Playwright suite stays on `default` and never switches tenant.

---

## Spec index

| Spec | Scenarios |
| --- | --- |
| `frontend/e2e/login.spec.js` | 1 |
| `frontend/e2e/access.spec.js` | 2 |
| `frontend/e2e/dashboard.spec.js` | 3 |
| `frontend/e2e/mill-flow.spec.js` | 4 (receive prefix of the mill-day) |
| `frontend/e2e/inventory.spec.js` | 5 |
| `frontend/e2e/language.spec.js` | 6 |
| `frontend/e2e/notifications.spec.js` | 7 |
| `frontend/e2e/farmer.spec.js` | 8 |
| `frontend/e2e/sales.spec.js` | 9 |
| `frontend/e2e/logout.spec.js` | 10 |
| `frontend/e2e/helpers/auth.js` | Login helper / API session (no secrets beyond demo accounts) |
| `frontend/e2e/global-setup.js` | Fail fast if UI or API is down |
