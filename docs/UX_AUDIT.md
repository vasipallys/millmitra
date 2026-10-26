# UX audit (Phases applied)

Walked routes in `frontend/src/App.jsx` against code and a signed-in desktop pass (admin). Role matrices come from `access_control` + Playwright role specs. Full 6-role × en/te × 1366/390 screenshot matrix was **not** archived in-repo (shots stay out of git). Mobile checks use the 390 Playwright smoke.

## Cross-cutting issues (found → fixed)

| Issue | Where | Fix |
|---|---|---|
| Flat 16-item sidebar, no grouping | Sidebar | Daily / Ops / Sales / Quality / Admin / Settings / Preview groups |
| No global search | Navbar | Command palette, Ctrl+K |
| No first-run path | Dashboard | Getting started checklist, DB-persisted |
| Comfort / large type missing | Settings | Comfort mode preference |
| Icon-only help missing | Headers | HelpTips with visible “Help” on md+ |
| Colour-only status chips | Users, IIoT | `StatusChip` (icon + text) |
| INR / dates ad hoc | Dashboard, Sales | `formatINR` / `formatQty` |
| Quality header hardcoded English | QualityControl | `PageHeader` + i18n subtitle |
| Tables without search / mobile cards | Users | `DataTable` |
| Deactivate user with no confirm | Users | `ConfirmDialog` |
| Touch targets < 44px | Buttons / nav | Theme `minHeight: 44`, drawer items 44 |
| Dialogs cramped on phone | MUI Dialog | Full-bleed paper under 600px |
| Mobile: sidebar-only nav | App | Bottom nav + More opens drawer |
| Horizontal scroll 156px at 390 | Navbar + persistent drawer | Short title on xs, hide chips, temporary drawer below md |
| Unsaved form-builder leave | FormBuilder | `useUnsavedGuard` |
| Missing page chrome on Quality | QualityControl | `PageShell` + `PageHeader` |

## Per route (after fix)

| Route | Purpose in 3s | Primary action | Header | Empty/load/error | Notes |
|---|---|---|---|---|---|
| Login | Sign in | Login | Special | Error alert | Password tab first; demo list remains |
| Dashboard | What to do next | Suggested step | Yes + help | Loading / error | Getting started + formatters |
| Mill flow | One mill day | Start / next | Yes + help | Existing wizard | Unchanged Formik steps |
| Farmers | People and paddy | Register farmer | Yes + help | Query error | Formik dialogs kept |
| Inventory | Stock | Add stock | Yes + help | Existing | |
| Production | Batches | Start batch | Yes + help | Empty CTAs | |
| Quality | Tests | Tabs | Yes + help | Existing | English header removed |
| Sales | Orders | New order | Yes + help | Empty CTA | INR formatter |
| Customers | Buyers | Add customer | Yes + help | Existing | |
| Finance | Invoice / pay | Create invoice | Yes + help | Existing | |
| Settings | Mill + you | Save | Yes + help | Alerts | Comfort mode |
| Users | Accounts | Create user | Yes + help | DataTable empty | Confirm deactivate |
| Access | Who may open what | Save matrix | Yes + help | Existing | |
| Lookups | Dropdown lists | Add value | Yes + help | Existing | |
| IIoT | Machines | Manual save | Yes + help | Empty rows | StatusChip |
| Form builder | Extra fields | Save | Yes + help | Empty fields | Unsaved guard |
| Dynamic forms | Extra records | Save | Yes + help | Empty records | |
| Dashboard builder | Widgets | Save | Yes | Loading | |
| Preview pages | Not mill-of-record | — | Mixed | Demo banners | Not restyled |

## Leftovers closed (this pass)

- **Inner tables → DataTable** on Sales orders, Finance invoices, Inventory movements, Farmers (list + procurements + contracts), Production batches, Quality tests, Customers, Access matrix, Financial Intelligence schedules, GST activity/calendar, Analytics insights, Analytics Reporting reports. Lookups / Users / IIoT were already migrated. Inventory stock stays card grid (not a table). Notifications is a list, not tabular. Sales has no payments table; Finance has no separate transactions/GST tables (GST lives on Compliance).
- **Preview pages** (Analytics, Financial Intelligence, GST, Analytics Reporting) now use `PageShell` + `PageHeader` + `pageKey` help + `StatusChip` + shared formatters. Sample-vs-actual / time-range toggles are unchanged.
- **Toasts**: `ToastProvider` default titles go through `t('toastSuccess'|'toastError'|'toastWarning'|'toastInfo')`. `useToastNotifications` strips English titles/messages from `TOAST_MESSAGES` so locale defaults win.
- **axe** now loops every authenticated `App.jsx` route as admin at 1366 and 390, plus login, plus operator (allowed + denied). RequireAccess denied page has an `h1`. Coverage: login + 22 admin routes × 2 viewports + 13 operator routes = **58 page scans**. First full-route run found serious/critical on inventory, production, analytics, FI, GST, reporting, notifications, and users (progressbars without names, unlabeled icon buttons, warning/info chip contrast, list/listitem markup, nested notification controls, unlabeled role selects). After fixes: **0 serious/critical**. Prior pass only scanned login + 4 app pages.
- **390 overflow** is asserted on every admin route (`< 8px`). Migrated tables expose `data-testid="data-table-cards"` on mobile.
