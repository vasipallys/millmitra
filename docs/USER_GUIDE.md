# MillMitra User Guide

**Rice mill operations, from paddy intake to customer billing**

This guide is for mill operators, managers, and office staff. It describes MillMitra as it works today: screens, buttons, and workflows you can actually use. Features that look present but are sample-only or incomplete are called out in the relevant section and again in [Known limitations](#20-known-limitations).

---

## Contents

1. [What MillMitra is](#1-what-millmitra-is)
2. [Who it is for](#2-who-it-is-for)
3. [How to start and open the app](#3-how-to-start-and-open-the-app)
4. [Login, session, and logout](#4-login-session-and-logout)
5. [Finding your way around](#5-finding-your-way-around)
6. [Roles and permissions](#6-roles-and-permissions)
7. [Dashboard](#7-dashboard)
7a. [Mill flow](#7a-mill-flow)
8. [Farmers](#8-farmers)
9. [Inventory](#9-inventory)
10. [Production batches](#10-production-batches)
11. [Quality tests](#11-quality-tests)
12. [Customers](#12-customers)
13. [Sales](#13-sales)
14. [Finance: invoices and payments](#14-finance-invoices-and-payments)
15. [Analytics](#15-analytics)
16. [Other screens](#16-other-screens)
17. [Common tasks](#17-common-tasks)
18. [Field meanings and validation](#18-field-meanings-and-validation)
19. [Typical mill day](#19-typical-mill-day)
20. [Known limitations](#20-known-limitations)
21. [Troubleshooting](#21-troubleshooting)
22. [Glossary](#22-glossary)

---

## 1. What MillMitra is

MillMitra is a rice mill management application. It helps a mill keep one place of record for:

- Farmers who supply paddy
- Paddy and finished-product stock
- Milling batches (create, start, test quality, complete)
- Customers
- Invoices and payments
- A live operations dashboard

In the product you will also see the names **Smart Mill** (left sidebar) and **Rice Mill Management System** / **Rice Mill AI** (top bar and login). Those are the same application.

MillMitra is **not** a replacement for statutory GST filing software, and it is **not** a fully automated mill controller. You still weigh grain, run machines, and issue physical bills as your mill already does. The app records those operations and keeps stock and money in view.

---

## 2. Who it is for

| Role you have at the mill | How you typically use MillMitra |
| --- | --- |
| Mill operator | Start and follow production batches, record quality tests, check paddy availability |
| Mill manager | Approve farmers, watch dashboard numbers, review stock and efficiency |
| Office / accounts staff | Register farmers, add stock, create customers, raise invoices, record payments |
| Sales staff | Maintain customers; use **Sales → New Order** for the live order book |
| Quality staff | Record lab-style tests on a batch from **Production**; the **Quality Control** menu is demonstration-only |

The sidebar only shows modules your role may use. The mill server also blocks forbidden saves. Farmer **Approve/Verify** still needs **admin** or **manager**.

---

## 3. How to start and open the app

You need **both** the office website (frontend) and the mill server (backend) running. The website talks to the server at `http://localhost:5000`. If only the website is running, login and every save will fail.

Typical addresses after a successful start:

- Office app: [http://localhost:3000](http://localhost:3000) (preferred). If that port is already used by another program, Vite prints a different URL such as [http://localhost:3001](http://localhost:3001) — use the address shown in the terminal.
- Mill server: [http://localhost:5000](http://localhost:5000)

An optional AI service on port 8000 is **not required** for day-to-day farmer, stock, batch, customer, invoice, or payment work.

### 3.1 First-time setup (Windows)

Do this once on the mill PC, or whenever you set up a new machine.

**A. Mill server (backend)**

1. Open a terminal in the project folder `D:\GenAi\millmitra`.
2. Go into the backend folder:

   ```powershell
   cd D:\GenAi\millmitra\backend
   python -m venv venv
   .\venv\Scripts\activate
   python -c "import sys; print(sys.executable)"
   # Must print ...\millmitra\backend\venv\Scripts\python.exe
   # If it prints ricemill\backend\venv, deactivate and activate this venv again.
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` if you do not already have an `.env` file, and set the database connection if your mill uses PostgreSQL. A local SQLite file is used when no database URL is set.
4. Create tables and the first users:

   ```powershell
   .\venv\Scripts\python.exe migrate_db.py
   ```

   App startup also creates any **missing** demo users (including quality, sales, accountant) without resetting existing passwords.

5. Start the server **with the millmitra venv**, not system Python:

   ```powershell
   .\venv\Scripts\python.exe app.py
   ```

   Leave this window open. The server listens on port **5000**. If something else already answers on 5000 (especially `C:\Python313\python.exe app.py`), stop that window first — it serves old code. Confirm liveness at [http://localhost:5000/api/health](http://localhost:5000/api/health).

**B. Office app (frontend)**

1. Open a **second** terminal.
2. Install and start:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

3. Open the URL Vite prints (usually [http://localhost:3000](http://localhost:3000)).

### 3.2 Daily start (already installed)

1. Start the mill server: `cd D:\GenAi\millmitra\backend` then `.\venv\Scripts\python.exe app.py`.
2. Start the office app: `cd D:\GenAi\millmitra\frontend` then `npm run dev`.
3. Open the URL Vite printed and log in on the **Password** tab. Pick English, Hindi, or Telugu on the login card if you want.

### 3.3 Docker (optional)

Project documentation describes `docker-compose up -d` and then `docker-compose exec backend python migrate_db.py`. Use that only if your mill’s installation actually includes Docker Compose for this project. If `docker-compose` is not available in the MillMitra folder, use the manual steps above.

### 3.4 First users

If the database was initialized with the bundled setup script, these accounts exist:

| Username | Typical password | Role shown in the app |
| --- | --- | --- |
| `admin` | `admin123` | admin |
| `manager` | `manager123` | manager |
| `operator` | `operator123` | operator |
| `quality` | `quality123` | quality_control |
| `sales` | `sales123` | sales |
| `accountant` | `accountant123` | accountant |

You can also log in with the matching email (for example `admin@ricemill.com`). **Change these passwords** after first login if this mill is in real use. If login fails with these names, ask whoever set up the mill PC which accounts were created.

### 3.5 Roles, access, and language

Each person has **one role**. The mill server checks that role on save and on finance/user reads — hiding a sidebar item is not the only lock.

| Persona | Username | Can open | Cannot |
| --- | --- | --- | --- |
| Mill owner | `admin` | All modules, **Users**, **Access** | — |
| Mill manager | `manager` | Operations and finance | Users / Access |
| Floor operator | `operator` | Dashboard, Mill flow, farmers, inventory, production, own settings | Finance, sales, user admin |
| Quality | `quality` | Dashboard, production (view + quality tests), Quality Control | Sales, finance, user admin, starting unrelated writes |
| Sales | `sales` | Customers, sales orders, invoices | Production start, user admin |
| Accountant | `accountant` | Finance, invoices, payments, dashboard; customers read | Batch start, user admin |

**Users** (`/users`) and **Access** (`/access`) are admin-only. Access shows a permission grid (dashboard, mill_flow, farmers, inventory, production, quality, sales, customers, finance, settings, users, preview). Toggles save to the mill database and apply on the next API call.

**Language:** English, Hindi, and Telugu. Use the language control on the login card and in the top bar. The choice is stored in this browser (`localStorage`) and updates login, sidebar, Mill flow steps/buttons, dashboard title, Users, Access, and common actions (Save, Cancel, Back).

---

## 4. Login, session, and logout

### 4.1 Sign in with password (use this)

1. Open the office app. You should see **Rice Mill AI** and **Sign in to MillMitra**.
2. Stay on the **Password** tab. The login card lists the real demo accounts (admin, manager, operator, quality, sales, accountant). It does **not** invent extra usernames from a suggestion API.
3. Enter **Username / Email / Phone** and **Password**.
4. Click **Login**. A wrong pair shows **Username or password is not recognized**.

On success you land on **Smart Dashboard**. Your name and **role** appear in the top bar and in the sidebar. The language control is on the login card and in the navbar (`localStorage` key `millmitra.language`).

### 4.2 Other login tabs (not reliable)

The login card also has **Voice** and **Biometric** tabs.

- **Voice** asks you to say “Login as [your username]” or “I am [your username]” and shows **Click to speak**.
- **Biometric** asks for a username and a **Biometric Login** button.

Treat these as experimental. Use **Password** for daily work. If a two-step code (OTP) screen appears, enter the code you were sent; a wrong code shows **Invalid OTP**.

### 4.3 Session

After login, MillMitra stores your session in the browser. You can close a tab and come back to [http://localhost:3000](http://localhost:3000) without typing the password again, as long as the session is still valid.

You do **not** need to log in on every page. The left menu stays available until you log out or the session expires.

### 4.4 Log out

1. Click your avatar in the top-right of **Rice Mill Management System**.
2. Click **Logout**.

You return to the login screen. Always log out on a shared office PC.

The same menu also has **Profile** and **Settings**. **Settings** opens the Settings page described later.

### 4.5 If login or the session fails

| What you see | What it usually means | What to do |
| --- | --- | --- |
| Error on the login card after **Login** | Wrong username/password, inactive account, or mill server not running | Check spelling; confirm `python app.py` is running on port 5000 |
| Browser jumps back to login while you work | Session expired or was rejected (HTTP 401) | Log in again |
| Pages load empty, or saves fail with network errors | Frontend is up, backend is not | Start the mill server, then refresh |
| “Loading...” that never finishes on Farmers | Auth check could not confirm you | Log out and log in again |

The app clears the saved session and sends you to login when the server says you are no longer authorized.

---

## 5. Finding your way around

After login you have:

- **Left sidebar** branded **Smart Mill** — main modules
- **Top bar** titled **Rice Mill Management System** — menu button, **role** chip, **language**, microphone, notifications bell, avatar
- **Main area** — the page for the module you selected

The sidebar **hides** items your role cannot use. Opening a hidden path shows **You don’t have access**. The mill server also rejects forbidden saves (for example an operator creating a finance invoice).

| Sidebar label | Opens | What it is for | Who typically sees it |
| --- | --- | --- | --- |
| Dashboard | `/dashboard` | Live mill snapshot | Most roles |
| Mill flow | `/mill-flow` | Guided receive → mill → sell → pay | admin, manager, operator |
| Farmers | `/farmers` | Farmer register, contracts, procurement | admin, manager, operator |
| Inventory | `/inventory` | Paddy and product stock | admin, manager, operator |
| Production | `/production` | Milling batches | admin, manager, operator, quality |
| Sales | `/sales` | Live order book (**New Order**) | admin, manager, sales |
| Finance | `/finance` | Invoices and payments | admin, manager, sales, accountant |
| Customers | `/customers` | Buyer records and their orders | admin, manager, sales, accountant (read) |
| Settings | `/settings` | Mill / own profile settings | Most roles |
| Users | `/users` | Create accounts, change role, activate | admin only |
| Access | `/access` | Permission matrix per role | admin only |
| Analytics | `/analytics` | Preview group — mill records by default | roles with `preview` |
| Quality Control | `/quality-control` | Camera / tests page (live records default) | roles with `quality` |
| Financial Intelligence | `/financial-intelligence` | Preview finance view | roles with `preview` |
| Compliance & GST | `/compliance-gst` | Preview GST view; does not file | roles with `preview` |

The bell icon opens notifications. A full notifications page also exists at `/notifications`. A reporting page exists at `/analytics-reporting` but is **not** listed in the sidebar.

On a phone-width screen, use the top-left menu icon to open or close the sidebar.

A voice microphone in the top bar and a floating voice control may appear. They are optional. They are not required for any workflow in this guide.

---

## 6. Roles and permissions

Your role is shown under your username in the sidebar and in the avatar menu.

| Role | Intended use | Enforced today |
| --- | --- | --- |
| **admin** | Mill owner | All modules; **Users** and **Access**; farmer verify |
| **manager** | Operations + finance | All except user admin; farmer verify |
| **operator** | Floor | Mill flow, farmers, inventory, production; no finance / sales / users |
| **quality_control** | Lab | Production view + quality tests, Quality Control page; no sales/finance/users |
| **sales** | Office sales | Customers, orders, invoices; no production start / users |
| **accountant** | Books | Finance and dashboard; customers read; no batch start / users |

Admin **Users** (`/users`): list, create (username, password, role), change role, activate/deactivate (not yourself). Admin **Access** (`/access`): toggle permissions; saved in `role_permissions`. Farmer **Approve/Verify** still needs admin or manager.

---

## 7. Dashboard

**Smart Dashboard** is the home page.

### What you can do

- Read the metric cards: **Production** (kg), **Quality Score** (%), **Inventory Value** (₹), **Pending Orders**, **Active Farmers**.
- Open any alerts listed in the alerts panel.
- Click the refresh icon to reload.
- Click the gear icon to open **Customize Dashboard** (widget selection). This is optional.

Numbers refresh on their own every few seconds to a few minutes. If a card shows `0`, that module may still be empty (no batches, no stock, no farmers yet).

Insights or “AI” banners only appear when the server actually returns them. If you see none, daily work is unaffected.

---

## 7a. Mill flow

**Mill flow** (sidebar: **Mill flow** / **Run the mill**) is a guided path at `/mill-flow`. Use it when you want the main mill chain on fewer screens, especially on an empty mill.

The start page is labeled **Suggested next step** and **Guided from your mill records**. It is not an AI model. It reads live paddy, batches, product stock, and invoices, then picks one step:

| Mill records | Suggested step |
| --- | --- |
| No paddy and no open batch | Receive paddy |
| Paddy on hand, or a planned batch, and nothing in progress | Start a batch |
| Batch in progress or paused | Quality & complete |
| Product stock and no unpaid invoice | Sell |
| Unpaid invoice | Invoice & pay |

Five steps, one at a time, with **Back** and a save button. If the server rejects a save, you stay on that step and see an inline error.

1. **Receive paddy** — **Existing farmer** with **Walk-in / later** (no farmer id; the mill walk-in farmer is used), a listed farmer, or **New farmer** (name, phone, village, district, state). Then variety, kg > 0, ₹/kg > 0, storage location. Saves through Inventory paddy stock.
2. **Start batch** — pick the lot (prefilled) and kg. Creates the batch and starts it, which deducts paddy.
3. **Quality & complete** — optional moisture / broken / foreign matter (**Skip quality test** is allowed). Rice output kg is required and increases product stock.
4. **Sell** — select or create a customer (name + phone), then a sales order.
5. **Invoice & pay** — invoice lines from the order; then a payment amount. Invoice wording must still match product stock.

You can still use Farmers, Inventory, Production, Sales, and Finance for the same work. Mill flow does not replace those pages.

---

## 8. Farmers

Open **Farmers**. The page title is **Farmer Management**.

Top buttons:

- **Register Farmer**
- **Create Contract**
- **Record Procurement**
- **Edit Requests**

Tabs:

- **All Farmers**
- **Recent Procurements**
- **Contract Management**
- **Analytics**

Summary cards at the top show totals such as **Total Farmers** when the server provides them.

### 8.1 Register a farmer

Use this before you buy paddy from a new supplier.

1. Click **Register Farmer**.
2. Complete the four steps: **Basic Information**, **Contact Details**, **Farm Details**, **Bank Details**.
3. Click through with **Next**, then submit at the last step.

**Fill these even if a field looks optional on screen.** The mill server will reject the registration without **village**, **district**, and **state**.

| Step | Fields | Rules |
| --- | --- | --- |
| Basic Information | Name, Father’s name, Phone, Alternate phone, Email | Name at least 2 characters; phone exactly 10 digits; valid email |
| Contact Details | Aadhar, PAN, Village, District, State, Pincode | Aadhar exactly 12 digits; PAN like `ABCDE1234F` if entered; **village, district, state required by the server** |
| Farm Details | Total land area, Irrigated area, Farming experience, Primary crop | Land area must be greater than 0 (acres) |
| Bank Details | Account number, IFSC, Bank name, Notes | Account at least 8 characters; IFSC like `SBIN0001234` |

After a successful save, the farmer appears on **All Farmers** with a generated farmer code (based on district). Use the search box: *Search farmers by name, code, or phone...*

**Example:** Ramesh of Nalgonda, phone `9876543210`, Aadhar 12 digits, 4 acres, account `123456789012`, IFSC `SBIN0001234`, village **Miryalaguda**, district **Nalgonda**, state **Telangana**.

Managers and admins can use **Approve/Verify** on a farmer row when the mill requires verification.

### 8.2 Create a contract

A contract is a season-wise commitment: how much paddy the farmer will supply, at what base price.

1. Click **Create Contract**.
2. Choose an **active** farmer.
3. Fill crop, season, year, quantity, prices, and dates.
4. Submit.

| Field | Meaning | Rules |
| --- | --- | --- |
| Farmer | Must already be registered | Required |
| Crop type | Default **Basmati Rice** | Required |
| Season | **kharif** or **rabi** | Required |
| Year | Contract year | 2020–2030 |
| Quantity committed | kg the farmer agrees to supply | Greater than 0 |
| Base price | ₹ per kg | Greater than 0 |
| Quality bonus / Advance amount | Optional extras | — |
| Contract start / end date | Validity period | Both required |
| Advance payment method | Default **bank_transfer** | — |

Open **Contract Management** to review existing contracts.

If opening a farmer’s detail page fails on an older mill database (missing contract columns), you can still use the list, register, and contract buttons; ask the installer to update the database when convenient. See [Troubleshooting](#21-troubleshooting).

### 8.3 Record procurement (buy paddy from a farmer)

This records a purchase from a farmer. It is the farmer-side counterpart of adding paddy into the mill.

1. Click **Record Procurement**.
2. Select the farmer (and a contract if they have an active one).
3. Enter crop, variety, date, quantity, prices, moisture, and storage.
4. Submit.

| Field | Meaning | Rules |
| --- | --- | --- |
| Farmer | Who delivered the paddy | Required |
| Contract | Optional link to a season contract | Optional |
| Crop type | Default **Basmati Rice** | Required |
| Paddy variety | Variety delivered | Required |
| Procurement date | Delivery date | Required |
| Quantity | kg purchased | Greater than 0 |
| Price per unit / Base price | ₹ per kg | Greater than 0 |
| Moisture content | % moisture | 0–30, required |
| Quality grade | Default **A** | — |
| Storage location | Default **Main Warehouse** | Required |
| Vehicle / driver / notes | Gate details | Optional |

**Recent Procurements** lists recent purchases.

### 8.4 Edit requests

Click **Edit Requests** to review farmer-profile change requests. Approve or reject from that dialog. Use a **manager** or **admin** account when the mill requires approval.

---

## 9. Inventory

Open **Inventory**. The page title is **Inventory Management**.

Top buttons:

- **Stock Movement**
- **Add Stock**

Cards:

- **Total Valuation**
- **Paddy Stock Value**
- **Product Stock Value**
- **Low Stock Items**

Tabs:

- **Paddy Stock**
- **Product Stock**
- **Stock Movements**
- **Analytics**

Paddy is unmilled grain. Product stock is milled rice (and related finished goods).

### 9.1 Add paddy or product stock

This is the fastest way to put grain or rice on the books when you are not using **Record Procurement**.

1. Click **Add Stock**.
2. Choose **Stock Type**: **Paddy Stock** or **Product Stock**.
3. Fill the form and click **Add Stock**.

| Field | Paddy | Product |
| --- | --- | --- |
| Variety / type | Basmati, Jasmine, Long Grain, Short Grain | Basmati Rice, Jasmine Rice, Long Grain Rice, Short Grain Rice |
| Quantity (kg) | Required, greater than 0 | Same |
| Purchase Price (₹/kg) | Required, greater than 0 | Shown as **Selling Price (₹/kg)** |
| Quality Grade | A / B / C (default A) | Same |
| Storage Location | Required (warehouse name) | Same |
| Moisture Content (%) | 0–100; warning above 14% for paddy | Optional |
| Notes | Optional | Optional |

A quantity above 100,000 kg or a price above ₹1,000/kg shows a warning so you can double-check the figures. You can still save after checking.

**Example:** Add 5,000 kg Basmati paddy at ₹28/kg into **Godown 1**, moisture 12%, grade A.

If you add paddy without selecting a farmer, the mill files it as a walk-in / direct purchase so the batch can still draw from that stock.

Empty paddy tab shows **No paddy stock available** and **Add Paddy Stock**.

### 9.2 Stock movement

**Stock Movement** records stock in, stock out, or transfer (from / to location, quantity, reference number, reason). Use it when grain is shifted between godowns or issued out without a full sales invoice.

### 9.3 Using stock for milling

Production draws **paddy** of the matching variety, oldest lots first. If a variety has no remaining quantity, **New Batch** will fail until you add or procure that variety.

When a batch **starts**, that paddy quantity is deducted. When a batch **completes** with a rice output greater than zero, **product** stock increases.

---

## 10. Production batches

Open **Production**. The page title is **Production Management**.

Top button: **New Batch**.

Status cards (when the server reports them):

- **Active Batches**
- **In Progress**
- **Planned**
- **Machines in Use**

Tabs:

- **Active Batches**
- **All Batches**
- **Analytics**

Batch life cycle you should expect:

**Planned → In Progress → Completed**  
(Paused is supported by the mill server; see notes below.)

### 10.1 Create a batch

You must have **paddy stock** of the chosen variety with enough remaining quantity.

1. Click **New Batch**.
2. Fill **Create New Production Batch**.
3. Click **Create Batch**.

| Field | Meaning | Typical values |
| --- | --- | --- |
| Paddy Variety | Must match stock | basmati, jasmine, long_grain, short_grain |
| Input Quantity (kg) | Paddy to mill | e.g. 1000 |
| Quality Grade | Input grade | Grade A / B / C |
| Planned Start Time | Optional schedule | Date and time |
| Special Instructions | Floor notes | Optional |

The mill assigns a batch number such as `B20260920001` (date + sequence). New batches start as **planned**. They do **not** consume paddy until you start them.

If you see a message about insufficient paddy, add stock or reduce **Input Quantity (kg)**.

### 10.2 Start a batch

Starting deducts paddy from inventory and sets status to **in_progress**.

1. Open the **All Batches** tab.
2. On a **planned** row, click the play icon (**Start Batch**).

You cannot start a batch that is already completed, and you cannot start if that lot no longer has enough remaining paddy.

### 10.3 Pause and resume

On **Active Batches**, the ⋮ menu on a card can show **Pause Batch**, **Resume Batch**, or **Stop Batch**.

- **Resume Batch** uses the same start action as **Start Batch** and works for a batch that is already **paused**.
- **Pause Batch** / **Stop Batch** may appear but are not always saved. If pause does not stick, leave the batch **in_progress** and complete it when milling is finished.

### 10.4 Complete a batch

Completing marks the batch done and, when rice output is recorded as more than 0 kg, adds rice to **Product Stock**.

On **Active Batches**, open the card menu (⋮). **Mark Complete** appears only when the card shows the batch at 100% of its target quantity. If you never see **Mark Complete**, the batch can remain **in_progress** on screen even after the mill run is finished — see [Known limitations](#20-known-limitations).

**All Batches** is the reliable place to **start** a planned batch and to open **Quality Test**. It does not include a complete button.

### 10.5 View a batch

On **All Batches**, click the view (eye) icon. **Batch Details** shows variety, status, input/output kg, efficiency, and planned/actual times.

Efficiency is rice output as a percentage of paddy input, once the batch is completed.

### 10.6 Production analytics

The **Analytics** tab on Production shows mill-run summaries when batches exist (counts, input, output, yield). Empty mills show zeros.

---

## 11. Quality tests

Record lab measurements against a **production batch**. This is the working quality workflow.

### From All Batches

1. Find a batch with status **in_progress**.
2. Click the quality / assessment icon (**Quality Test**).

### From Active Batches

1. Open the card menu (⋮).
2. Click **Quality Test** (shown for **in_progress** or **completed** batches).

### Filling the test

The dialog uses three steps: **Test Setup**, **Measurements**, **Review & Submit**.

| Area | What you enter |
| --- | --- |
| Test type | Comprehensive Test, Moisture Content Only, Physical Properties, Visual Inspection, Custom Test |
| Measurements | Moisture %, broken %, foreign matter, chalky kernels, grain length/width, colour uniformity |
| Conditions | Temperature, humidity, equipment (Moisture Meter #1 / #2, Grain Analyzer, Color Sorter, Manual Inspection) |
| Tester name / notes | Who tested, remarks |

Click through the steps and submit. The test is stored against that batch.

**Do not confuse this with the sidebar item Quality Control.** That page is a camera demo with sample charts. Real tests belong here, on the batch.

---

## 12. Customers

Open **Customers**. The page title is **Customer Management**.

Top buttons: **Analytics** (jumps to the Analytics tab) and **Add Customer**.

Cards include **Total Customers** and **Active Customers**.

Tabs:

- **Customer List**
- **Customer Details** (enabled after you select a customer)
- **Orders**
- **Analytics**

### 12.1 Add a customer

1. Click **Add Customer**.
2. Fill the form. **Customer Name** and **Phone** are required by the mill server.
3. Save.

| Field | Meaning |
| --- | --- |
| Customer Name | Person or firm display name (**required**) |
| Company Name | Trading name; stored with the customer |
| Customer Type | Individual, Business, or Distributor |
| Phone | **Required** |
| Email, GST Number | Optional but useful for invoices |
| Address, City, State, Pincode | Delivery / billing address |
| Credit Limit | Maximum outstanding you allow (₹) |
| Payment terms | Default **cash** |

**Example:** Customer Name `Lakshmi Traders`, Company Name `Lakshmi Traders Pvt`, type **distributor**, phone `9988776655`, GST if they have one, credit limit `200000`.

Search and filters on the list help by name, segment, or status.

### 12.2 Customer details, orders, interactions

Select a customer to open **Customer Details**. Use **Orders** for that buyer’s sales orders (live data from the mill server). Interactions (calls/visits) can be logged from the customer tools when those dialogs are offered.

Customer **Analytics** on this page depends on the server; if the charts are empty, the customer list and orders still work.

---

## 13. Sales

Open **Sales**. The page title is **Sales Management**.

**Treat this screen as live mill orders.** Use **New Order** to save a customer, variety, quantity, and price. Charts only appear after you have orders.

Quotations and leads are not offered in this screen.

**What to use instead**

| You want to… | Use |
| --- | --- |
| Create a sales order | **Sales** → **New Order** |
| Add a buyer | **Customers** → **Add Customer** |
| See a buyer’s orders | **Customers** → **Orders** or **Sales** |
| Bill a buyer | **Finance** → **Create Invoice** (deducts matching product stock) |
| Record money received | **Finance** → **Record Payment** |

There is no working Quotations or Leads screen in the menu. Those functions are not enabled in this deployment.

---

## 14. Finance: invoices and payments

Open **Finance**. The page title is **Financial Management**.

Top buttons:

- **Create Invoice**
- **Record Payment**

Cards:

- **Total Revenue**
- **Total Expenses**
- **Net Profit**
- **Outstanding Receivables**

The recent invoices table lists invoices you actually created. Summary cards and cash-flow use those invoices and payments (not sample totals). They are still not a replacement for audited accounts.

### 14.1 Create an invoice

You need the customer’s ID (from **Customers**; it is the customer number in the system).

1. Click **Create Invoice**.
2. Fill **Create New Invoice**.
3. Add line items (description, quantity, unit price).
4. Save.

| Field | Meaning |
| --- | --- |
| Customer ID | Number of the customer (**required**) |
| Invoice Date | Bill date |
| Due Date | When payment is expected |
| Payment Terms | Net 15 / Net 30 / Net 45 / Net 60 / Due on Receipt |
| Item description | Must match a product name/variety in Inventory so stock can be deducted |
| Quantity and Unit price | kg or bags × ₹ |
| Notes | Optional |

The mill assigns an invoice number such as `INV000001`. Tax is applied in the background (about 5% if you do not enter a tax figure). Totals are quantity × unit price, plus tax.

**Example:** Customer ID `3`, one line “Basmati Rice — 500 kg” at ₹80/kg, terms **Net 30**.

### 14.2 Record a payment

1. Click **Record Payment**.
2. Enter invoice (if known), amount, method, date, and reference.
3. Save.

| Field | Meaning |
| --- | --- |
| Invoice | Optional; if set, that invoice is marked **paid** |
| Amount | Must be greater than 0 |
| Payment type | Full or partial |
| Payment method | Cash, Bank Transfer, Cheque, UPI, Card Payment, Online Payment |
| Payment date | When money was received |
| Reference number | UTR, cheque number, UPI ref |
| Notes | Optional |

**Example:** ₹40,000 by **UPI**, reference `UPI123456`, against invoice `INV000001`.

If you enter an invoice ID, that invoice’s status becomes **paid** even for a partial amount. Confirm the amount matches the bill before saving.

---

## 15. Analytics

### 15.1 Sidebar → Analytics

**Analytics** in the left menu is a **sample** business-intelligence page (charts and “AI insights” that load from demonstration data). Do not take those numbers as this mill’s actual results.

### 15.2 Analytics that follow real work

Use these when you want figures tied to what you entered:

- **Dashboard** metric cards
- **Inventory** → **Analytics** tab (stock-related)
- **Production** → **Analytics** tab (batches, yield)
- **Farmers** → **Analytics** tab
- **Customers** → **Analytics** tab

### 15.3 Analytics reporting URL

`/analytics-reporting` is a reporting layout that is **not** in the sidebar. If you open it, treat charts as you would any other reporting screen: confirm they match batches, stock, and invoices you know are real.

---

## 16. Other screens

### 16.1 Quality Control (sidebar)

Title: **AI Quality Control**. Tabs: **Live Analysis**, **Dashboard**, **Test Results**.

This is a **demonstration** of camera-based grading (sample scores, sample tests). It does not replace batch **Quality Test** on **Production**.

### 16.2 Financial Intelligence

Sample cash-flow and “health score” views. For real invoices and payments use **Finance**.

### 16.3 Compliance & GST

Sample GST / compliance dashboard. It does not file GST returns and is not the mill’s official tax register. Keep using your CA / GST portal.

### 16.4 Settings

Title includes mill **Business Info**, **Notifications**, **AI Features**, **Security**, **Data & Backup**.

You can type company name, GST number, address, and similar fields and click **Save Settings**. Values are stored on this computer and, when you are signed in, on the mill server.

### 16.5 Notifications

The bell lists in-app notices. You can open the full **Notifications** page from the top bar flow. Categories may include farmers, payments, quality, inventory, and production, depending on what the mill has generated.

---

## 17. Common tasks

### Run the mill from one screen

1. Sidebar **Mill flow**.
2. Read **Suggested next step**, or click **Start from receive paddy**.
3. Complete the five steps (receive → start batch → quality/complete → sell → invoice & pay). Quality can be skipped; stock deduction cannot.

### Add paddy stock (godown receipt)

1. **Inventory** → **Add Stock**.
2. Stock Type **Paddy Stock**.
3. Variety, quantity kg, purchase price ₹/kg, grade, **Storage Location**, moisture.
4. **Add Stock**.
5. Confirm the lot on **Paddy Stock**.

*Alternative:* **Farmers** → **Record Procurement** when the paddy came from a registered farmer.

### Mill a batch

1. Confirm paddy of that variety on **Inventory** → **Paddy Stock**.
2. **Production** → **New Batch** → variety, input kg, grade → **Create Batch**.
3. **All Batches** → play icon **Start Batch** on the **planned** row.
4. When the run is underway, use **Quality Test** if the lab checks a sample. **Pause Batch** / **Resume Batch** from **All Batches** if the line stops.
5. When milling is finished, **Mark Complete** and enter rice / by-product kg. Rice output is added to product stock.

### Bill a customer

1. **Customers** → **Add Customer** if they are new (name + phone).
2. Note the customer’s ID.
3. **Finance** → **Create Invoice** → customer ID, lines, dates → save.
4. Find the new row in recent invoices (number like `INV000001`).

### Record a customer payment

1. **Finance** → **Record Payment**.
2. Amount, method (Cash / UPI / Bank Transfer / …), date, reference.
3. Enter the invoice ID if you are closing that bill.
4. Save.

Do **not** use sample Sales figures — **Sales → New Order** now saves a real mill order.

---

## 18. Field meanings and validation

### 18.1 Grades and varieties

| Term in the app | Meaning on the mill floor |
| --- | --- |
| Grade A / B / C | Quality band for paddy or rice (A is best in this app) |
| Basmati / Jasmine / Long Grain / Short Grain | Variety keys used for **both** stock and batches — pick the same spelling throughout |
| Moisture % | Water in the grain. Paddy above ~14% may need drying (the stock form warns you) |
| Broken % | Broken kernels in a sample |
| Foreign matter | Stones, straw, other seeds |
| Efficiency / yield | Rice out ÷ paddy in, as a percentage after a batch completes |

### 18.2 Money and quantity

- Quantities are in **kg** unless a field says otherwise.
- Money is **Indian rupees (₹)**.
- Phone numbers are **10 digits**, no spaces or `+91`.
- Aadhar is **12 digits**.
- IFSC looks like `SBIN0001234` (four letters, zero, then six letters/digits).

### 18.3 Messages you may see

| Message (or similar) | Cause | Fix |
| --- | --- | --- |
| Name is required / Phone number must be 10 digits | Farmer or customer form | Correct the field |
| Aadhar number must be exactly 12 digits | Farmer contact step | Digits only |
| Invalid IFSC code format | Bank step | Recheck IFSC |
| Village / district / state missing (server error) | Farmer register | Fill all three location fields |
| Quantity must be greater than 0 | Stock, contract, or procurement | Enter kg > 0 |
| Moisture content cannot exceed 30% | Procurement | Check the meter reading |
| Insufficient paddy stock… | New batch or start | Add paddy of that variety or reduce input kg |
| Batch cannot be started from status “…” | Start clicked on a finished or already running batch | Use a **planned** (or paused) batch |
| Batch is not in progress | Complete clicked too early | Start the batch first |
| Amount must be greater than 0 | Payment | Enter a positive amount |
| Name and phone are required | Customer | Fill both |
| Insufficient permissions to verify farmers | Operator tried Approve/Verify | Use manager or admin |
| Invalid OTP | Two-step login | Re-enter the code or use password login |

---

## 19. Typical mill day

A practical sequence that matches the live screens:

1. **Log in** with password at [http://localhost:3000](http://localhost:3000).
2. Glance at **Smart Dashboard** (stock value, active farmers, production).
3. Gate arrival: **Register Farmer** if new, then **Record Procurement**, **or** **Inventory** → **Add Stock** for walk-in paddy.
4. Floor: **Production** → **New Batch** → **Start Batch** on **All Batches**.
5. Lab: **Quality Test** on that batch.
6. Office: **Add Customer** if needed → **Create Invoice** → **Record Payment** when money comes in.
7. **Logout** on the shared PC.

For official numbers stay on Dashboard, Mill flow, Inventory, Production, Sales, and Finance. Preview pages default to **mill records**; use **View sample** only when you want a demonstration.

---

## 20. Known limitations

These are current product limits, written the way office staff will meet them.

| Area | What you will notice | What to do |
| --- | --- | --- |
| **Quotations / leads** | Not offered as working screens. | Ignore; they are not enabled. |
| **Quality Control menu** | Camera / test page; mill records by default, **View sample** optional. | Record official lab tests from **Production** → **Quality Test**. |
| **Analytics**, **Financial Intelligence**, **Compliance & GST** | Preview group; **live mill records by default**. **View sample** is demonstration only. Compliance does not file GST. | Use Dashboard, Inventory, Production, Sales, and Finance for operational work. |
| **Pause / Stop batch** | Pause saves. Stop also pauses the batch (it does not cancel or reverse paddy already deducted). | Resume from the batch card or All Batches. |
| **Invoice stock** | Invoice lines deduct matching **product** stock. If the description does not match a product lot, the invoice is rejected. | Use the Inventory product name/variety on the line. |
| **Voice / Biometric login** | Often fails or is incomplete. | Use the **Password** tab. |
| **Older mill database** | Opening some farmer details or contracts can fail if extra columns were never added. | Lists and new registers often still work; ask for a database update if contract/advance fields error. |
| **Voice / experimental extras** | Voice login and biometric return “not implemented” / 501. Contract “optimization” and dashboard insights may be empty. | Use **Password**. Day-to-day save/load does not depend on insights. |

---

## 21. Troubleshooting

**Cannot open http://localhost:3000, or `npm run dev` says the port is in use**  
Port 3000 is the preferred office-app port. Another program on this PC may already be using it (that is not MillMitra). Start the frontend anyway (`npm run dev` in `frontend`); Vite will move to the next free port and print the URL. Use that address — do not stop the other program unless you know it is an old MillMitra window.

**Login never succeeds / “Network Error”**  
Start the backend (`.\venv\Scripts\python.exe app.py` in `backend`). If login still fails against old behaviour, stop the process on port 5000 and start again with that venv command. Confirm [http://localhost:5000/api/health](http://localhost:5000/api/health).

**Kicked to login in the middle of work**  
Session expired. Log in again. Avoid two different accounts in the same browser.

**Farmer will not save**  
Check 10-digit phone, email, 12-digit Aadhar, land area > 0, bank IFSC, **and village, district, state**.

**Batch will not create or start**  
Add paddy of the **same variety** with remaining kg ≥ input quantity. Varieties are case-style specific (`basmati`, not a free-typed local name).

**Invoice saved but dashboard finance cards look unchanged**  
Expected. Use the invoices table.

**Customer saved but Sales still looks empty**
Open **Sales → New Order** and pick that customer. Sales lists live orders, not a sample buyer list.

**Numbers look stuck at zero**  
Enter at least one farmer, one paddy lot, and one batch, then refresh. Empty mill = zeros.

**Page is blank after a server restart**  
Refresh the browser. If you still see login, sign in again.

---

## 22. Glossary

| Term | Meaning in MillMitra |
| --- | --- |
| **Paddy** | Unmilled rice grain as received from farmers |
| **Product stock** | Milled rice (and similar finished goods) ready to sell |
| **Variety** | Grain type: Basmati, Jasmine, Long Grain, Short Grain |
| **Grade** | Quality band A, B, or C |
| **Procurement** | Purchase of paddy from a farmer |
| **Contract** | Season agreement (kharif/rabi) for quantity and price |
| **Kharif / Rabi** | Monsoon and winter crop seasons |
| **Batch / production batch** | One milling run with a batch number (for example `B20260920001`) |
| **Planned** | Batch created, paddy not yet consumed |
| **In progress** | Batch started; paddy deducted |
| **Paused** | Batch stopped temporarily (if the mill recorded it) |
| **Completed** | Batch finished; rice may have been added to product stock |
| **Input quantity** | kg of paddy fed to the mill |
| **Output / rice output** | kg of rice recovered |
| **Efficiency / yield** | Output ÷ input × 100 |
| **Moisture content** | Water in grain, percent |
| **Broken grains / broken %** | Damaged kernels in a sample |
| **Foreign matter** | Non-grain material in a sample |
| **Godown / storage location** | Warehouse or bin name |
| **Walk-in / direct** | Paddy added without a farmer ID |
| **Customer ID** | Internal number needed on **Create Invoice** |
| **Invoice** | Bill to a customer (`INV000001` style) |
| **Payment** | Money recorded against a customer or invoice (`PAY…` style) |
| **Net 30** | Pay within 30 days of invoice date |
| **Outstanding receivables** | Unpaid customer bills from invoices you created |
| **GST number** | Customer or mill GSTIN, for your records |
| **Aadhar / PAN / IFSC** | Farmer KYC and bank identifiers |
| **Advance** | Money paid to a farmer on a contract |
| **Base price** | ₹/kg before quality bonus |
| **Quality test** | Lab measurements stored on a batch |
| **Smart Dashboard** | Home overview after login |
| **Smart Mill** | Sidebar name for this application |

---

*This guide matches the MillMitra screens and mill-server behaviour as of the current application build. If a button label on your PC differs slightly, follow the on-screen name and the workflow in the matching section above.*
