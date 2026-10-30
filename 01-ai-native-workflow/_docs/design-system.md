# Design System — Shared Household Chores Tool

## Visual Identity & Principles

- **Mobile-first & PWA-ready**: Designed for quick thumb-reach interactions on smartphones and clean responsive desktop layout.
- **Warm & Friendly Household Aesthetic**: Clean, modern indigo primary theme (`#4f46e5`), soft surfaces (`#f8fafc`), crisp card elevations, and rounded touch targets.
- **Immediate Status Clarity**: High-visibility semantic color-coding for chore statuses (`Pending`, `Done`, `Overdue`, `Verified`).

---

## Color Palette

| Token | Hex | Usage |
|---|---|---|
| `primary` | `#4f46e5` | Primary buttons, brand header, active tabs |
| `primary-hover` | `#4338ca` | Button hover & active states |
| `primary-light` | `#eef2ff` | Light badge background, active navigation pill |
| `surface` | `#ffffff` | Card backgrounds, modals, input backgrounds |
| `background` | `#f8fafc` | Page background |
| `text-main` | `#0f172a` | Main headings, table data, primary body text |
| `text-muted` | `#64748b` | Subheadings, dates, helper text, empty states |
| `border` | `#e2e8f0` | Dividers, card borders, table row borders |
| `success` | `#10b981` | Completed chore badge, mark-complete buttons |
| `success-light` | `#ecfdf5` | Verified badge background, success alerts |
| `warning` | `#f59e0b` | Unverified completion badge, attention warnings |
| `warning-light` | `#fffbeb` | Unverified badge background |
| `danger` | `#ef4444` | Overdue badge, delete action buttons |
| `danger-light` | `#fef2f2` | Overdue badge background, error callouts |
| `info` | `#3b82f6` | Verify action buttons, informational pills |

---

## Typography

- **Font Family**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- **Headings**:
  - `h1`: `1.875rem` (30px), bold (`700`), tight line-height (`1.2`)
  - `h2`: `1.5rem` (24px), semi-bold (`600`), line-height (`1.3`)
  - `h3`: `1.125rem` (18px), semi-bold (`600`)
- **Body**: `1rem` (16px), regular (`400`), line-height (`1.5`)
- **Small / Meta**: `0.875rem` (14px), line-height (`1.4`)

---

## Components

### 1. Navigation Header
- Fixed/sticky or clean top bar with household logo / icon, active links, user profile pill, and logout.
- Accent border at bottom (`1px solid #e2e8f0`).

### 2. Cards
- White background (`#ffffff`), rounded corners (`12px` / `0.75rem`), subtle border (`1px solid #e2e8f0`), soft shadow (`0 1px 3px rgba(0,0,0,0.05)`).
- Generous padding (`1.5rem`).

### 3. Buttons
- Base: `0.5rem 1rem` padding, rounded corners (`8px`), font weight `500`, smooth transition (`0.15s ease`).
- `.btn-primary`: Indigo background, white text.
- `.btn-success`: Emerald background, white text (used for "Mark Complete").
- `.btn-info`: Blue background, white text (used for "Verify").
- `.btn-danger`: Red text or subtle light red button with red text.
- `.btn-secondary`: Outlined or light gray button.

### 4. Status Badges
- Pill shape (`border-radius: 9999px`), `font-weight: 600`, `font-size: 0.8125rem`, `padding: 0.25rem 0.75rem`.
- `Done ✓ (verified)`: Green text (`#047857`) on emerald light background (`#ecfdf5`).
- `Done (unverified)`: Amber text (`#b45309`) on amber light background (`#fffbeb`).
- `Pending`: Slate text (`#475569`) on gray background (`#f1f5f9`).
- `Overdue`: Red text (`#b91c1c`) on rose light background (`#fef2f2`).

### 5. Tables
- Border-collapse with `100%` width.
- Headers with subtle background (`#f8fafc`), uppercase small text (`0.75rem`), letter spacing (`0.05em`).
- Padding `0.75rem 1rem`, rows separated by light divider (`1px solid #f1f5f9`).
- Row hover effect (`#f8fafc`).
- Horizontal scrolling container on small screens.

### 6. Forms
- Inputs with `padding: 0.625rem 0.875rem`, border `1px solid #cbd5e1`, rounded `8px`, transition on focus (`border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,0.15)`).
- Labels in semi-bold text with subtle margin bottom.
- Help text in muted slate (`#64748b`).
