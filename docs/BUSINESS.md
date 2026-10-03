# MillMitra — Business document

For mill owners, managers, and operators. This describes MillMitra as it works today: the mill process it records, who uses which screens, and what is live versus preview.

Related reading: [User Guide](USER_GUIDE.md) (click-by-click), [Technical document](TECHNICAL.md) (engineers).

---

## 1. What MillMitra is

MillMitra is a rice mill operations application. It is one place of record for:

- Farmers who supply paddy
- Paddy in the godown and milled product stock
- Milling batches (create, start, pause/resume, quality test, complete)
- Customers and sales orders
- Invoices and payments
- A live operations dashboard and mill settings

In the product you will also see **Smart Mill** (left sidebar), **Rice Mill Management System** (top bar), and **Rice Mill AI** (login). Those names are the same application.

MillMitra is **not** a GST filing portal, a mill machine controller, or audited accounts software. Staff still weigh grain, run machines, and keep statutory books. The app records those operations so stock and money stay visible.

---

## 2. The business problem

A typical rice mill already does this work on paper, WhatsApp, and spreadsheets:

1. Buy paddy at the gate from farmers (or walk-in lots).
2. Store it, mill it, grade it, and bag rice.
3. Sell to traders or distributors and collect payment.

Without one system, remaining paddy, rice output, and outstanding bills drift apart. MillMitra’s job is to keep that chain consistent: **paddy in → batch out → rice stock → order/invoice → payment**.

---

## 3. Who uses it

Anyone with a login can open every sidebar item. A few actions are role-gated (for example **Approve/Verify** on a farmer).

| Role at the mill | Typical MillMitra use | Role stored on the account |
| --- | --- | --- |
| Owner / mill manager | Dashboard, farmer verification, stock and money review | `admin` or `manager` |
| Gate / office staff | Register farmer, record procurement, add stock, customers, invoices, payments | `admin`, `manager`, or `operator` |
| Floor operator | New batch, Start Batch, Pause/Resume, Mark Complete | `operator` |
| Lab / quality | **Quality Test** on a production batch (not the Preview Quality Control page) | any login; use Production |
| Sales / accounts | Customers, **Sales → New Order**, Finance invoices and payments | any login |

After `python migrate_db.py`, these accounts exist if they were not already created:

| Username | Typical password | Role |
| --- | --- | --- |
| `admin` | `admin123` | admin |
| `manager` | `manager123` | manager |
| `operator` | `operator123` | operator |

You can also sign in with the matching email (for example `admin@ricemill.com`). Change these passwords on a real mill PC.

---

## 4. End-to-end mill process

This is the live chain. Each step names the screen and the main button.

```
Farmer (or walk-in lot)
        │
        ▼
Paddy stock (Inventory)
        │
        ▼
Production batch  →  Quality Test (on the batch)
        │
        ▼
Product stock (milled rice)
        │
        ├──► Sales → New Order  (order book)
        │
        └──► Finance → Create Invoice  →  Record Payment
                              │
                              ▼
                         Dashboard
```

### 4.1 Farmer procurement

**Farmers → Register Farmer** when the supplier is new. Required on the server even if a step looks optional: **name**, **phone**, **village**, **district**, **state**. The mill assigns a farmer code from the district (for example Nalgonda → `NAL0001`).

**Farmers → Create Contract** is a season commitment (crop, **kharif** / **rabi**, year, quantity kg, base price ₹/kg, dates). It does not by itself add stock.

**Farmers → Record Procurement** is a purchase from a registered farmer: variety, date, quantity, price, moisture, storage. Use this when the paddy came from that farmer.

Managers and admins can **Approve/Verify** a farmer. Operators who click it may see **Insufficient permissions to verify farmers**.

**Edit Requests** reviews proposed changes to a farmer profile (approve / reject).

### 4.2 Paddy inventory

If the lot is walk-in (no farmer), **Inventory → Add Stock → Stock Type: Paddy Stock**. The mill files it against an internal “Direct / Walk-in Purchase” farmer so batches can still draw from it.

Fields: **Paddy Variety** (Basmati, Jasmine, Long Grain, Short Grain), **Quantity (kg)** > 0, **Purchase Price (₹/kg)** > 0, **Quality Grade** (Grade A / B / C), **Storage Location**, optional moisture and notes.

**Inventory** cards: **Total Valuation**, **Paddy Stock Value**, **Product Stock Value**, **Low Stock Items**. Tabs: **Paddy Stock**, **Product Stock**, **Stock Movements**, **Analytics**.

### 4.3 Stock movements

**Inventory → Stock Movement** records **in**, **out**, or **transfer** against a lot (lot type, lot ID from the stock card, quantity, reason). Outbound movements reduce remaining paddy or product quantity. Use this for godown shifts or issues that are not a full invoice.

### 4.4 Milling / production batches

**Production → New Batch**. Variety must match paddy with enough **remaining** kg. New batches are **planned** and do **not** consume paddy yet.

**All Batches → Start Batch** (play icon) on a **planned** row: deducts paddy (oldest matching lot / the lot tied to the batch) and sets status **in_progress**.

Lifecycle you should expect: **planned → in_progress → completed**. **paused** is supported: on **All Batches**, **Pause Batch** (stop icon) while in progress, **Resume Batch** while paused. Pause does not cancel the batch or put paddy back.

**Mark Complete** on the same row: enter rice / by-product kg. Rice output > 0 increases **Product Stock** for that variety.

### 4.5 Quality (live)

Record lab numbers on the **batch**, not on the Preview Quality Control page.

From **All Batches** (in_progress or paused) use the **Quality Test** icon: steps **Test Setup**, **Measurements**, **Review & Submit**. Moisture %, broken %, foreign matter, chalky kernels, grain size, conditions, tester name.

### 4.6 Product stock

Created or increased when a batch completes with rice output, or via **Add Stock → Product Stock**. Varieties: Basmati Rice, Jasmine Rice, Long Grain Rice, Short Grain Rice (stored as variety keys such as `basmati` / `basmati_rice` depending on the form).

### 4.7 Customers and sales orders

**Customers → Add Customer**: **Customer Name** and **Phone** required. Types include Individual, Business, Distributor. Optional GST, address, credit limit, payment terms.

**Sales → New Order** opens **Create New Order**: **Customer**, **Order Date**, **Item / variety**, **Quantity (kg)**, **Unit price (₹/kg)**. Orders are stored as **pending** and appear on Sales and on **Customers → Orders**.

Quotations and leads are **not** offered as working screens.

### 4.8 Invoices and payments

**Finance → Create Invoice**: customer ID (the number from Customers), dates, payment terms, line items. Line **description** must match a product name/variety in Inventory or the invoice is rejected (stock cannot be deducted). Tax defaults to about 5% if you do not enter a figure. Invoice numbers look like `INV000001`.

**Finance → Record Payment**: amount > 0, method (Cash, Bank Transfer, Cheque, UPI, Card, Online), date, reference. If you enter an invoice ID, that invoice is marked **paid** (including when the amount is partial — confirm the amount before save).

Cards **Total Revenue**, **Total Expenses**, **Net Profit**, **Outstanding Receivables** come from invoices and payments you entered, not sample totals. This is still not a statutory ledger.

### 4.9 Dashboard

**Smart Dashboard** after login. Cards: **Production** (kg), **Quality Score** (%), **Inventory Value** (₹), **Pending Orders**, **Active Farmers**. Widgets (current batch, production chart, inventory alerts, and more by role) use live mill data when records exist. Empty mills show zeros.

---

## 5. Day-in-the-life workflows

### Gate morning (office + godown)

1. Log in at the office app (**Password** tab). Land on **Smart Dashboard**.
2. New supplier: **Farmers → Register Farmer** (include village, district, state).
3. Purchase: **Record Procurement**, or **Inventory → Add Stock** for walk-in paddy.
4. Confirm the lot on **Inventory → Paddy Stock**.

### Floor (milling)

1. Confirm remaining kg of that variety.
2. **Production → New Batch** → **Create Batch**.
3. **All Batches → Start Batch**.
4. If the line stops: **All Batches → Pause Batch**; later **Resume Batch**.
5. Lab: **Quality Test** on that batch row.
6. After the run: **Mark Complete** with rice kg. Check **Inventory → Product Stock**.

### Office afternoon (sell and collect)

1. New buyer: **Customers → Add Customer**.
2. Optional order book: **Sales → New Order**.
3. Bill: **Finance → Create Invoice** (description matches product stock).
4. When money arrives: **Record Payment**.
5. **Logout** on a shared PC (avatar → **Logout**).

Skip Preview sidebar items for operational numbers.

---

## 6. What is live vs preview / sample

The sidebar splits **core** items from a **Preview** group (chip **Sample**).

| Screen / feature | Status | Use for mill-of-record? |
| --- | --- | --- |
| Dashboard | Live metrics and widgets | Yes, after you have data |
| Farmers (register, list, contracts, procurement, verify, edit requests) | Live | Yes |
| Inventory (paddy, products, add stock, movements, valuation, low stock) | Live | Yes |
| Production (batch create/start/pause/resume/complete, quality tests, analytics tab) | Live | Yes |
| Sales → New Order and order list | Live | Yes (order book) |
| Customers (add, list, orders) | Live | Yes |
| Finance (invoices, payments, summary, aging) | Live | Yes (operational, not statutory) |
| Settings (business info, save) | Live (browser + server mill-settings) | Yes for mill name/GST/address you type |
| Analytics (sidebar) | Preview / sample charts | No |
| Quality Control (sidebar) | Preview camera / sample tests | No — use Production Quality Test |
| Financial Intelligence | Preview | No — use Finance |
| Compliance & GST | Preview; does not file GST | No |
| Analytics reporting (`/analytics-reporting`) | Not in sidebar; treat as sample unless you confirm figures | No by default |
| Quotations / leads | Not enabled (API returns not implemented) | No |
| Voice and Biometric login tabs | Experimental | No — use **Password** |
| Voice microphone / floating voice control | Optional, not required | No |
| 2FA enable in Settings | Not available (server returns not configured) | No |

---

## 7. Data they enter and decisions they make

### Decisions

- Accept a farmer (verify) or keep them unverified.
- Buy against a contract or as a spot / walk-in lot.
- Which variety and how many kg to mill today (must fit remaining paddy).
- Pause vs complete a batch.
- Whether a lab test is needed before completing.
- Sell via **New Order** only, or also raise a **Create Invoice** (invoice is what deducts product stock).
- Mark an invoice paid when recording a payment.

### Typical validation (what the forms and server enforce)

| Data | Rule |
| --- | --- |
| Farmer name | At least 2 characters |
| Phone | 10 digits |
| Aadhar | 12 digits if entered |
| PAN / IFSC | Format-checked if entered (`SBIN0001234`-style IFSC) |
| Village, district, state | Required to register a farmer |
| Land area | Greater than 0 acres on the farmer form |
| Stock / procurement / batch / payment quantities and prices | Greater than 0 |
| Moisture (procurement) | 0–30% typical server check; stock form 0–100, warning above 14% for paddy |
| Variety | Pick the same dropdown value for stock and batches (`basmati`, not a free-typed local name) |
| Invoice line description | Must match product name/variety or stock deduct fails |
| Customer | Name and phone required |

Quantities are **kg**. Money is **₹**.

---

## 8. Limitations operators must know

- **Not GST software.** Preview Compliance & GST does not file returns. Keep the CA / GST portal.
- **Not a full general ledger.** No working chart-of-accounts UI. Finance is invoices, payments, and simple summaries.
- **Invoice stock is strict.** Wrong line wording means the invoice is refused. Use the Inventory product name/variety.
- **Partial payment** against an invoice ID still marks that invoice **paid**.
- **Pause Batch** does not reverse paddy already deducted. There is no separate Stop/cancel that returns grain to the lot.
- **Older databases** may miss farmer/contract columns; lists often still work.
- **Login Voice / Biometric** are not for daily use.
- **AI banners** (typo suggestions, insights) are optional; empty or wrong ones do not block save/load.
- **Sidebar does not hide by role.** Training matters more than the menu list.
- Change default passwords if this mill is in real use.

---

## 9. What this document does not claim

The following appear in older marketing or unused routes and are **not** mill-of-record features: e-signatures, barcode/QR scanning, GPS fleet tracking, double-entry bookkeeping, computer-vision grading as the official grade, predictive maintenance, TensorFlow/ML scoring, automated GST, quotations, leads, or equipment control.

For click-level steps and error messages, use [USER_GUIDE.md](USER_GUIDE.md).
