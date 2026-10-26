# MillMitra UX guidelines

One pattern set for every signed-in mill screen. Do not invent a second header, table, or toast.

## Page

- Wrap with `PageShell`.
- `PageHeader` has an `h1` title, one-line subtitle (“what you do here”), primary action on the right, and a `pageKey` so the **?** popover can load tips.
- Nested work uses the existing mill-flow wizard, not a second chrome.

## Forms

- Visible label on every field. Required fields use the MUI asterisk plus `requiredField` for assistive text (`FormField`).
- Validate on blur and on submit. Inline error under the field.
- Dialog actions: **Cancel** left, primary right. Sticky on small screens. First field autofocus. Enter submits a one-step form.
- `useUnsavedGuard` on builders that can lose work.

## Tables

- Use `DataTable`: search, skeleton, empty state + CTA, row action menu, card layout below `md`.

## Status

- `StatusChip` is icon **and** text. Never colour alone. Map statuses in `StatusChip.jsx`.

## Feedback

- Existing `ToastProvider` (`useToast`) for success/error/info.
- `ConfirmDialog` for turn-off / delete / irreversible actions. Plain words.

## Numbers and dates

- `formatINR`, `formatQty`, `formatDate`, `formatNumber` from `frontend/src/utils/format.js`. Indian grouping. `dd MMM yyyy`.

## Navigation

- Sidebar groups: Daily work / Inventory and production / Sales and money / Quality and compliance / Admin / Settings / Preview.
- Role-filtered. Active item uses colour **and** `aria-current`.
- Mobile: bottom nav (Dashboard, Mill flow, Farmers, Inventory, More).
- **Find a page** (`Ctrl+K` / search icon) jumps using the same paths as the assistant.

## First-run and help

- Dashboard **Getting started** checklist (farmer → buy → mill → sell). Dismiss and ticks persist on `PUT /api/user/preferences`.
- Per-page **?** tips (`HelpTips` + `PAGE_TIPS`).

## Comfort mode

- Settings → Comfort mode. Larger type and spacing. Stored as `comfort_mode` on the user and `millmitra.comfort` locally.

## Accessibility

- Buttons and icon buttons: 44px minimum.
- Focus visible (existing theme outline).
- Dialogs go edge-to-edge below 600px.
- Status and nav never rely on colour alone.
