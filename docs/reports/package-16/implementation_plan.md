# Package 16 — Frontend / Stitch UI Implementation Plan

**Author:** Architecture & UX Design Lead  
**Status:** Planning — Final Revision (Approved in Principle)  
**Target Executor:** Gemini 3.1 Pro High  
**Date:** 2026-08-28

---

## 1. Current State Assessment

### 1.1 What Exists

The current P16 frontend is a minimal React + TypeScript + Vite application in `frontend/` with:

- **2 pages:** Dashboard (`Dashboard.tsx`) and CaseDetail (`CaseDetail.tsx`)
- **2 API integrations:** `GET /api/recovery-cases` and `GET /api/recovery-cases/{case_id}/timeline`
- **1 health check:** `GET /api/health`
- **Build tooling:** Vite 8.2, React 19, TypeScript 6, TailwindCSS v4 with `@tailwindcss/postcss`
- **Dependencies:** `react-router-dom`, `lucide-react`, `clsx`, `tailwind-merge`
- **Stitch project:** ID `17638431777656320869` with 1 generated Case Detail screen

### 1.2 What Is Good (Preserve)

1. **Build toolchain works:** `npm run build` compiles with zero TS errors
2. **Vite proxy configured:** `/api` → `http://127.0.0.1:8000` with path rewrite
3. **React Router wired:** Client-side routing between Dashboard and CaseDetail
4. **TailwindCSS v4 configured:** `@import "tailwindcss"` + `@theme` block pattern
5. **Backend test suite preserved:** 154 tests still pass

### 1.3 What Is Broken (Must Fix)

| # | Defect | Severity |
|---|--------|----------|
| 1 | **Hardcoded mock data** in CaseDetail: root cause analysis, policy decision, execution status are all static strings identical for every case | CRITICAL |
| 2 | **Dead "Execute Intervention" button** — no `onClick` handler, no API call | CRITICAL |
| 3 | **Hardcoded Recovery Rate** of 68.4% — not computed from data or API | CRITICAL |
| 4 | **Dead sidebar links** — "Recovery Cases" and "Settings" are `href="#"` | HIGH |
| 5 | **No mobile navigation** — sidebar is `hidden md:flex` with no hamburger/drawer | HIGH |
| 6 | **Wrong currency formatting** — hardcoded `$` prefix for all currencies including INR | HIGH |
| 7 | **No error handling** — `Promise.all` in CaseDetail has no `.catch()`, hangs on failure | HIGH |
| 8 | **No API client abstraction** — raw `fetch()` scattered in `useEffect` hooks | MEDIUM |
| 9 | **Tailwind v3/v4 config conflict** — legacy `tailwind.config.js` coexists with v4 `@theme` | MEDIUM |
| 10 | **Missing font imports** — `Inter` and `JetBrains Mono` not loaded via CDN or local files | MEDIUM |
| 11 | **Leftover Vite boilerplate** — `App.css` has 185 lines of unused starter CSS | LOW |
| 12 | **`<title>frontend</title>`** instead of `<title>RecoverAI</title>` | LOW |
| 13 | **`any[]` type** for timeline events — no TypeScript safety | MEDIUM |
| 14 | **No frontend tests** — zero component or integration tests | MEDIUM |
| 15 | **DESIGN.md is skeletal** — 10 lines, no actual design tokens or component specs | HIGH |

### 1.4 Visual Direction Rejection

The current dark navy aesthetic (`#0F172A` background, `#1E293B` surfaces, `#007AFF` primary) produces a generic cybersecurity/SOC dashboard feel. The user has explicitly rejected this as "AI slop." The redesign must adopt a warm, premium, financially trustworthy visual language.

---

## 2. Architecture Constraints

### 2.1 What P16 MAY Change

- All files under `frontend/`
- `DESIGN.md` in repository root
- `docs/reports/package-16/*` artifacts
- `docs/checkpoints/package-16.md`

### 2.2 What P16 MUST NOT Change

- Any file under `recoverai/` (backend source)
- Any file under `tests/` (backend tests)
- Any file under `docs/` except `docs/reports/package-16/` and `docs/checkpoints/package-16.md`
- `pyproject.toml`, `uv.lock`
- n8n workflows, deployment configs
- P15 API endpoints or contracts

### 2.3 Backend API Is Frozen

P15 exposes exactly 6 endpoints. P16 must work within these boundaries. If the UI needs data that P15 does not provide, it must be flagged explicitly (see §15) rather than silently inventing endpoints.

### 2.4 Financial Authority Rules

- Frontend NEVER decides that an action is safe
- Frontend NEVER bypasses P05 (State Machine), P07 (Policy), P08 (Razorpay), P09 (Verification)
- Frontend NEVER contains secrets (Razorpay keys, LLM keys, webhook secrets, DB credentials)
- `UNKNOWN` NEVER looks like `SUCCESS`
- `RECOVERED` requires backend verification — green styling is reserved for verified outcomes

---

## 3. UX/Product Goals

### 3.1 Emotional Tone

The application should communicate:

| Feeling | How |
|---------|-----|
| **Calm** | Warm neutral backgrounds, generous whitespace, unhurried typography, reduced card density |
| **Clarity** | Editorial hierarchy, intentional composition, progressive disclosure, fewer persistent borders |
| **Confidence** | Large, precise financial numbers, verified badges, deterministic policy display |
| **Financial trust** | Professional typography, restrained color, premium rather than template-like SaaS styling |
| **Intelligence** | Subtle AI indicators, evidence-based recommendations, clear reasoning |
| **Progress** | Recovery journey visualization, meaningful motion |
| **Recovery** | Clear outcome visualization based exclusively on verified data |
| **Human decision-making** | Explicit approval flows, clear "why" for every recommendation |

### 3.2 What the User Should Quickly Answer

1. **What money is at risk?** → Dashboard hero metric
2. **What requires my attention?** → Dashboard open cases panel
3. **Why is this case at risk?** → Case detail: cause + evidence
4. **What does RecoverAI recommend?** → AI recommendation section
5. **Why is that recommendation allowed?** → Policy decision with rule badges
6. **What has already happened?** → Audit timeline
7. **Has the money actually been recovered?** → Verification state with evidence (per case)
8. **What do I need to do?** → Workflow handoff notices

---

## 4. Information Architecture

### 4.1 Navigation Structure

```
RecoverAI

PRIMARY
  Overview (Dashboard)          /
  Recovery Cases (List)         /cases
  Case Detail                   /cases/:id

SECONDARY (MVP stretch — show as disabled/coming-soon if not wired)
  Activity / Audit              /activity
  System Health                 /system

ALWAYS VISIBLE
  System status indicator (top bar)
  TEST MODE badge (top bar)
```

### 4.2 Navigation Rationale

The spec (`docs/ui_ux.md` §9) lists 8 navigation items. For a realistic MVP with 6 API endpoints, we implement the 3 primary routes with real data. Secondary routes can show empty/coming-soon states. We do NOT create fake pages with hardcoded data.

---

## 5. Complete User Journeys

### 5.1 Primary Journey: Revenue Recovery Overview → Case Resolution

```
User opens RecoverAI
  → Dashboard loads with real metrics
  → Sees revenue at risk, active cases (Unavailable metrics shown gracefully)
  → Notices "Open Recovery Cases" summary
  → Clicks a case row
  → Case Detail loads with real case data + timeline
  → Reads amount at risk, workflow state
  → Scrolls through timeline to understand what happened
  → Sees AI recommendation (from timeline events)
  → Sees policy decision (from timeline events)
  → Sees execution state and verification outcome
  → Returns to dashboard
```

### 5.2 Secondary Journey: Case List Filtering

```
User navigates to Recovery Cases list
  → Sees all cases with status badges
  → Scans amount, status, date columns
  → Clicks a case to drill into detail
```

### 5.3 Error Journey: API Unavailable

```
User opens RecoverAI
  → Dashboard shows skeleton loading
  → API call fails
  → Error state appears with "Unable to load recovery data" message
  → Retry button offered
  → System status indicator shows degraded
```

---

## 6. Screen Inventory

### 6.1 Required Screens/States

| Screen | Route | Data Source | States |
|--------|-------|-------------|--------|
| Dashboard | `/` | `GET /recovery-cases`, `GET /health` | loading, data, empty, error |
| Recovery Cases List | `/cases` | `GET /recovery-cases` | loading, data, empty, error |
| Case Detail | `/cases/:id` | `GET /recovery-cases/:id`, `GET /recovery-cases/:id/timeline` | loading, data, not-found, error |
| Activity (stretch) | `/activity` | — | coming-soon |
| System Health (stretch) | `/system` | `GET /health` | loading, data, error |

### 6.2 Shared States (Every Data-Driven Component)

- **Loading:** Skeleton placeholder matching content shape
- **Empty:** Descriptive message explaining what the section shows
- **Error:** Friendly message + retry button, never raw stack trace
- **Data:** Real content from P15 API

---

## 7. Stitch MCP Execution Plan

### 7.1 Strategy

Create a NEW Stitch project with the warm/light design system, generate 3 core screens as high-fidelity references, then translate the design tokens and layout principles into production React components.

**Critical Generation Sequence:**
1. Create design system
2. Generate Case Detail desktop (the product-defining experience)
3. Generate Dashboard desktop
4. Generate Dashboard mobile

### 7.2 Step-by-Step Stitch Workflow

**Step 1: Create Project**
```
Tool: create_project
Args: { "title": "RecoverAI v2 — Warm Premium" }
Purpose: Fresh project, not polluted by the old dark-navy designs
```

**Step 2: Create Design System**
```
Tool: create_design_system
Args: {
  "projectId": "<new_project_id>",
  "designSystem": {
    "displayName": "RecoverAI Warm Premium",
    "theme": {
      "colorMode": "LIGHT",
      "headlineFont": "PLUS_JAKARTA_SANS",
      "bodyFont": "INTER",
      "labelFont": "JETBRAINS_MONO",
      "roundness": "ROUND_EIGHT",
      "customColor": "#2563EB",
      "colorVariant": "TONAL_SPOT",
      "overridePrimaryColor": "#2563EB",
      "overrideSecondaryColor": "#F5F0EB",
      "overrideTertiaryColor": "#059669",
      "overrideNeutralColor": "#57534E",
      "designMd": "<see DESIGN.md content below>"
    }
  }
}
Purpose: Establish the warm light palette, typography, and roundness as the design system.
```

**Step 3: Generate Case Detail Screen (Desktop)**
```
Tool: generate_screen_from_text
Args: {
  "projectId": "<new_project_id>",
  "designSystem": "<design_system_asset_id>",
  "deviceType": "DESKTOP",
  "modelId": "GEMINI_3_1_PRO",
  "prompt": "RecoverAI — Recovery Case Detail page. Light warm cream background. Back arrow + Case ID 'REC-—' + Status badge 'VERIFYING' (amber). Hero section: '₹— at risk' large prominent number. Recovery journey stepper: DETECTED → ASSESSED → POLICY → EXECUTING → VERIFYING (current step highlighted).
  Layout: Editorial, reduced density, generous whitespace.
  LEFT COLUMN - 'Case Summary': Failure type, customer context, payment method, recovery window. 'AI Recommendation' section: 'CREATE_PAYMENT_LINK' action, evidence chips.
  RIGHT COLUMN - 'Policy Decision': 'APPROVED' with green badge, reason codes as subtle pills. 'Execution': action status 'VERIFICATION_PENDING'. 'Workflow Handoff' notice showing where execution is managed. No fake 'Execute' buttons.
  BOTTOM - 'Timeline' vertical stepper with nodes for each audit event showing timestamp, actor, and description.
  Warm, professional, premium financial feel. Use placeholder text like 'Sample Case' and '₹—' for financial values to ensure design is uncoupled from realistic data."
}
```

**Step 4: Generate Dashboard Screen (Desktop)**
```
Tool: generate_screen_from_text
Args: {
  "projectId": "<new_project_id>",
  "designSystem": "<design_system_asset_id>",
  "deviceType": "DESKTOP",
  "modelId": "GEMINI_3_1_PRO",
  "prompt": "RecoverAI — AI Revenue Recovery Dashboard. Light warm cream/ivory background (#FAFAF7). Professional financial operations interface. Top bar with logo 'RecoverAI', system status pill, and 'TEST MODE' badge. Left sidebar with compact navigation. Main content area shows:
  1. Hero metrics row: 'Open Revenue at Risk ₹—' (large, prominent), 'Active Cases —'. Include two muted, visually secondary placeholder states for 'Verified Recovered' and 'Recovery Rate' showing a graceful 'Data Unavailable' state so they do not dominate the real KPIs.
  2. Two-column section below: Left column 'Open Recovery Cases' summary panel describing active cases in the recovery pipeline. Right column 'System Health' showing a single unified 'System Operational' state.
  3. Full-width 'Recent Recovery Cases' table with columns: Case, Customer, Amount at Risk, Status (colored pills), Last Updated.
  Design Rules: Reduced card density. Generous whitespace. Editorial hierarchy. Fewer persistent borders. Selective use of surfaces. Large financial figures. Premium, calm, trustworthy. No dark navy. IMPORTANT: Use neutral placeholders like '—' for all metrics to emphasize they are design-only."
}
```

**Step 5: Generate Mobile Dashboard**
```
Tool: generate_screen_from_text
Args: {
  "projectId": "<new_project_id>",
  "designSystem": "<design_system_asset_id>",
  "deviceType": "MOBILE",
  "modelId": "GEMINI_3_1_PRO",
  "prompt": "RecoverAI mobile dashboard. Same warm premium design rules: reduced density, generous whitespace. Top bar with hamburger menu icon, 'RecoverAI' logo, single system status dot. Stacked vertical layout: Hero metrics (Active Cases, Revenue at Risk). Open Recovery Cases summary. Recent cases as compact card list. Touch-friendly 44px minimum tap targets. Use '—' for all data values."
}
```

**Step 6: Get Generated Screens**
```
Tool: get_screen (for each generated screen)
Purpose: Extract the HTML code and design tokens from each screen
```

**Step 7: Apply Design System for Consistency**
```
Tool: apply_design_system
Purpose: Ensure all screens share the same design tokens
```

### 7.3 Design Token Extraction & Implementation Rule

**CRITICAL RULE:** The final React implementation MUST never copy placeholder business values (like `₹—`, `Sample Case`, or `—`) from the Stitch code as live data. The design is purely a structural reference; all values must be populated by the React components mapping to the API.

---

## 8. Visual Design System

### 8.1 Visual Quality Mandates

- **Reduced card density:** Do not wrap every single section in a bordered box.
- **Generous whitespace:** Use padding to group elements logically rather than lines and boxes.
- **Editorial hierarchy:** Typography size and weight should establish order of importance.
- **Fewer persistent borders:** Rely on layout and subtle background tints instead of hard borders.
- **Selective surfaces:** Only use elevated surfaces (`bg-white` over `#FAFAF7`) for primary interactive areas or critical focal points.
- **Large financial figures:** Revenue numbers must be visually dominant.
- **Progressive disclosure:** Hide non-essential audit data until requested (e.g., collapsible timeline details).
- **Intentional composition:** The layout must purposefully direct the eye, not just dump data into a grid.
- **Premium styling:** Avoid default SaaS template looks; aim for bespoke financial software.
- **Meaningful motion:** See Section 12.

### 8.2 Color Palette

**Foundation — Warm Neutral Light**

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg` | `#FAFAF7` | Page background (warm off-white) |
| `--color-surface` | `#FFFFFF` | Core focal panels (use selectively) |
| `--color-surface-secondary` | `#F5F0EB` | Subtle secondary backgrounds |
| `--color-border` | `#E7E0D8` | Rare structural dividers |
| `--color-border-subtle` | `#F0EBE4` | Very subtle separators |

**Text Hierarchy**

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-text-primary` | `#1C1917` | Headings, primary content (stone-900) |
| `--color-text-secondary` | `#57534E` | Body text, descriptions (stone-600) |
| `--color-text-muted` | `#A8A29E` | Metadata, timestamps, labels (stone-400) |

**Semantic Colors**

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-success` | `#059669` | Verified recovery, healthy status (emerald-600) |
| `--color-success-bg` | `#ECFDF5` | Success background tint |
| `--color-warning` | `#D97706` | Attention, pending, unknown (amber-600) |
| `--color-warning-bg` | `#FFFBEB` | Warning background tint |
| `--color-danger` | `#DC2626` | Failure, blocked, error (red-600) |
| `--color-danger-bg` | `#FEF2F2` | Danger background tint |
| `--color-info` | `#2563EB` | AI recommendation, informational (blue-600) |
| `--color-info-bg` | `#EFF6FF` | Info background tint |
| `--color-neutral` | `#78716C` | Inactive, unknown states (stone-500) |
| `--color-neutral-bg` | `#F5F5F4` | Neutral background tint |

**Brand Accent**

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-primary` | `#2563EB` | Primary actions, links, active nav (blue-600) |
| `--color-primary-hover` | `#1D4ED8` | Primary hover state |
| `--color-primary-bg` | `#EFF6FF` | Primary background tint |

### 8.3 Typography & Resilience

Keep Plus Jakarta Sans / Inter / JetBrains Mono as the preferred design fonts, but **require robust system fallbacks** in the Tailwind configuration so that the UI remains premium if external font loading fails.

| Level | Font Stack | Size | Weight | Line Height | Usage |
|-------|------------|------|--------|-------------|-------|
| Display | `'Plus Jakarta Sans', system-ui, sans-serif` | 36px | 700 | 1.1 | Hero financial figures |
| H1 | `'Plus Jakarta Sans', system-ui, sans-serif` | 28px | 700 | 1.2 | Page titles |
| H2 | `'Plus Jakarta Sans', system-ui, sans-serif` | 22px | 600 | 1.3 | Section headings |
| Body | `'Inter', system-ui, sans-serif` | 15px | 400 | 1.6 | Prose, descriptions |
| Label | `'Inter', system-ui, sans-serif` | 12px | 500 | 1.3 | Metadata, headers |
| Mono | `'JetBrains Mono', ui-monospace, monospace` | 14px | 500 | 1.4 | Financial amounts, IDs |

### 8.4 Spacing Scale & Border Radius

Base unit: 4px. Use Tailwind's default spacing scale (`p-1` = 4px, `p-2` = 8px, etc.). Highlighted panels use `12px` (`rounded-xl`), buttons use `8px` (`rounded-lg`).

---

## 9. Component Architecture

### 9.1 Directory Structure

```
frontend/src/
├── main.tsx
├── App.tsx
├── index.css                    # Tailwind + @theme tokens
├── api/
│   └── client.ts                # Centralized typed API client
├── types/
│   └── domain.ts                # TypeScript interfaces matching P15 responses
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx          # Sidebar + TopBar + Main content area
│   │   ├── Sidebar.tsx           # Desktop sidebar navigation
│   │   ├── TopBar.tsx            # Top bar with logo, status, test mode badge
│   │   ├── MobileNav.tsx         # Mobile hamburger drawer
│   │   └── PageHeader.tsx        # Page title + subtitle + optional actions
│   ├── data-display/
│   │   ├── MetricCard.tsx        # KPI display (value, label)
│   │   ├── UnavailableMetric.tsx # Graceful UI for missing data (visually secondary)
│   │   ├── DataTable.tsx         # Reusable sortable table
│   │   └── Timeline.tsx          # Vertical timeline for audit events
│   ├── status/
│   │   ├── StatusBadge.tsx       # Colored pill for workflow/action states
│   │   ├── SystemStatus.tsx      # Unified health indicator dot + label
│   │   └── TestModeBadge.tsx     # "TEST MODE" / "RAZORPAY TEST" badge
│   ├── financial/
│   │   ├── MoneyValue.tsx        # Formatted currency display (₹ / $ / EUR)
│   │   └── RecoveryJourney.tsx   # Horizontal stepper showing case lifecycle
│   ├── feedback/
│   │   ├── LoadingSkeleton.tsx   # Skeleton placeholder shapes
│   │   ├── EmptyState.tsx        # Icon + message for empty data
│   │   └── ErrorState.tsx        # Error message + retry button
│   └── case/
│       ├── CaseSummary.tsx       # Case header with amount, status, dates
│       ├── TimelineEvent.tsx     # Single timeline node
│       └── AttentionPanel.tsx    # "Open Recovery Cases" summary
├── pages/
│   ├── Dashboard.tsx
│   ├── CaseList.tsx              # Recovery Cases list (separate from Dashboard)
│   ├── CaseDetail.tsx
│   └── SystemHealth.tsx          # Stretch: basic health page
└── hooks/
    ├── useApi.ts                 # Generic fetch hook with loading/error states
    └── useCases.ts               # Case-specific data fetching
```

### 9.2 Data Provenance Rule

**Explicit Rule:** Every displayed business value must map directly to:
1. A real P15 response field, or
2. A documented timeline event field.

No inferred, guessed, or approximated production data is allowed.

---

## 10. Dashboard Design

### 10.1 Layout Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│ TopBar: [RecoverAI Logo]            [TEST MODE] [● System OK]  │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                      │
│ Sidebar  │  PageHeader: "Overview"                              │
│          │  Subtitle: "Revenue recovery operations"             │
│ Overview │                                                      │
│ Cases    │  Open Revenue at Risk      Active Cases              │
│ Activity │  ₹<from-API>               <from-API>                │
│ System   │                                                      │
│          │  [Verified Recovered: Data Unavailable] (Muted)      │
│          │  [Recovery Rate: Data Unavailable] (Muted)           │
│          │                                                      │
│          │  Open Recovery Cases                                 │
│          │  Currently tracking <from-API> active cases in       │
│          │  the recovery pipeline.                              │
│          │                                                      │
│          │  Recent Recovery Cases                               │
│          │  Case    Amount     Status        Updated    →       │
│          │  ...     ₹...       ● Verifying   2m ago              │
│          │                                                      │
└──────────┴──────────────────────────────────────────────────────┘
```

### 10.2 Hero Metrics — Data Derivation

| Metric | Derivation |
|--------|------------|
| Open Revenue at Risk | `sum(case.amount_minor)` for cases where `status === 'OPEN'`, divided by 100 |
| Active Cases | `count` where `status === 'OPEN'` |
| **Verified Recovered** | **NOT AVAILABLE** from P15 API → Visually secondary `UnavailableMetric` |
| **Recovery Rate** | **NOT AVAILABLE** from P15 API → Visually secondary `UnavailableMetric` |

Unavailable metrics must be visually subordinated so the dashboard is not dominated by missing data.

### 10.3 Open Cases Panel

Scan cases for `OPEN` status. Provide a truthful "Open Recovery Cases" summary describing active cases in the pipeline. Do NOT imply every OPEN case requires operator attention unless supported by actual data. Do NOT hallucinate specific workflow counts.

### 10.4 System Health

Use `GET /health` to display a single system-level status. Display one unified status. Do NOT fabricate specific provider health checks.

---

## 11. Case Detail Design

### 11.1 Information Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Cases                                                 │
│                                                                  │
│ Case <case_id>                                   ● VERIFYING    │
│ Created <date>                                                  │
│                                                                  │
│              ₹<amount> at risk                                   │
│                                                                  │
│  DETECTED → ASSESSED → POLICY → EXECUTING → VERIFYING           │
│     ✓          ✓          ✓         ✓          ●                 │
│                                                                  │
│  Case Summary                                                    │
│  Status: OPEN | Currency: INR | Verifications: 2                 │
│                                                                  │
│  Recovery Decision                                               │
│  AI Recommendation                                               │
│  (from timeline events)                                          │
│                                                                  │
│  Policy Decision                                                 │
│  (from timeline events)                                          │
│                                                                  │
│  Workflow / Execution Handoff                                    │
│  Execution managed by n8n orchestrator.                          │
│                                                                  │
│  Timeline (Collapsible)                                          │
│  ● CASE_CREATED          System       Aug 28, 10:00             │
│  ● RISK_ASSESSMENT       ML Model     Aug 28, 10:01             │
└─────────────────────────────────────────────────────────────────┘
```

### 11.2 Recovery Journey Stepper

Map `workflow_state` (derived from the latest timeline event's `new_state`) to a horizontal stepper:

| Stage | Workflow States | Visual |
|-------|----------------|--------|
| Detected | DETECTED | ✓ completed (if past) |
| Assessed | ENRICHING, ASSESSED | ✓ completed |
| Policy | PLANNING, POLICY_REVIEW, WAITING_APPROVAL | ✓ completed |
| Executing | EXECUTING | ✓ completed or ● active |
| Verifying | VERIFYING | ● active or ✓ completed |
| Resolved | CLOSED | ✓ or outcome badge |
| Unknown | UNKNOWN | ⚠ warning indicator |

### 11.3 Case Summary & Recovery Decision

Display fields directly from `GET /recovery-cases/{case_id}` and `GET /recovery-cases/{case_id}/timeline`. Use REAL data from the timeline instead of hardcoded strings.

### 11.4 Status Visual Language

1. **"Payment Link Created" ≠ "Revenue Recovered"** — `ACTION_EXECUTING` uses blue/info; only `VERIFICATION_COMPLETED` with `VERIFIED_SUCCESS` uses green/success
2. **UNKNOWN gets amber/warning with explicit text**
3. **Green is ONLY for verified success**

---

## 12. Motion / Interaction Design

### 12.1 Premium, Restrained Interactions

Add **only 2–3 restrained premium interactions**. No decorative 3D scenes or excessive animation.

| Interaction | Purpose | Styling |
|-------------|---------|---------|
| **Recovery Journey progress animation** | Celebrate step completion | Subtle fill transition or checkmark reveal (300ms spring) |
| **Opportunity-card depth/elevation** | Indicate interactivity | Subtle shadow/elevation change on hover (150ms ease) |
| **Restrained VERIFIED_SUCCESS transition** | Emphasize positive outcome | Gentle fade-in of the green success state on the case page |

### 12.2 Reduced Motion

All animations must respect `prefers-reduced-motion: reduce`:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 13. Responsive Strategy

### 13.1 Breakpoints

| Name | Width | Layout |
|------|-------|--------|
| Mobile | < 640px | Single column, hamburger nav, stacked content |
| Tablet | 640px–1024px | Single column main, collapsible sidebar |
| Desktop | > 1024px | Sidebar + main content area |

### 13.2 Component Behavior by Breakpoint

- **Navigation:** Hamburger drawer (mobile) → Collapsed icon (tablet) → Full sidebar (desktop)
- **Table:** Card list (mobile) → Compact table (tablet) → Full table (desktop)
- **Touch targets:** Minimum 44×44px on all touch devices.

---

## 14. Accessibility Strategy

- **Semantic HTML:** `<nav>`, `<main>`, strict heading hierarchy.
- **Keyboard Support:** Focus rings, Tab navigation, Escape to close.
- **Contrast:** Ensure all text meets WCAG AA contrast.
- **Status Communication:** Never use color alone; include icons/labels.

---

## 15. API Integration Mapping & GAP Analysis

### 15.1 Available Endpoints → UI Features

| UI Feature | Endpoint | Fields Used |
|------------|----------|-------------|
| Dashboard metrics (Open/At-Risk) | `GET /recovery-cases` | Compute from `amount_minor`, `status`, `currency` |
| System health indicator | `GET /health` | `status` field |
| Cases table | `GET /recovery-cases` | All fields from `cases` array |
| Case detail header | `GET /recovery-cases/{id}` | `case_id`, `amount_minor`, `currency`, `status`, `created_at` |
| Case timeline | `GET /recovery-cases/{id}/timeline` | Full `events` array |

### 15.2 API Gaps — AUTHORITATIVE TRUTH BOUNDARY

> [!CAUTION]
> For every metric below: NOT AVAILABLE → do not fabricate → provide graceful visually-secondary UI treatment.

| Gap # | UI Feature | Missing From P15 API | Mandatory UI Treatment |
|-------|------------|-----------------------|-------------------------|
| GAP-1 | `workflow_state` counts | Case list only returns `OPEN`/`CLOSED` | Dashboard must show "Open Recovery Cases". Do NOT fabricate workflow state counts. |
| GAP-2 | Verified Recovered Revenue | Not in case list response. | Show distinct, muted `UnavailableMetric` treatment. Do NOT invent this number. |
| GAP-3 | Recovery Rate | Requires recovered total vs at risk. | Show distinct, muted `UnavailableMetric` treatment. Do NOT invent this percentage. |
| GAP-4 | Provider-specific Health | `/health` returns singular status | Show unified "System Operational". Do NOT fabricate specific health. |

### 15.3 MCP Frontend Usage Rules

The frontend must primarily use standard P15 REST endpoints. `POST /mcp/execute` is not a general-purpose frontend business API.

---

## 16. Loading / Empty / Error / Unknown States

- **Loading:** Skeleton shapes without borders.
- **Empty:** Descriptive text and icon (e.g., "No recovery cases yet").
- **Error:** Friendly message + retry button (e.g., "Unable to load data").
- **Unknown State:** Amber/warning indicator with text explaining automatic duplicate execution is blocked.

---

## 17. Human Approval UX

### 17.1 Handoff Display

The browser cannot directly approve or execute a financial action without an explicit backend mutation endpoint, which does not exist in P15. Present a workflow handoff notice transparently:

```
🔔 Human Approval Required

Recommendation: CREATE_PAYMENT_LINK for ₹<amount>
Evidence: Root cause indicates correctable customer failure
Policy Explanation: Amount exceeds auto-approval threshold.

Workflow Handoff: Approval and execution orchestration is managed externally via n8n.
```

Do NOT create a fake "Execute" or "Approve" button in the browser.

---

## 18. Security Constraints

- No Razorpay/LLM API keys, webhook secrets, or DB credentials in frontend.
- Do not bypass policy engine or execute financial operations directly.
- Base URL via `VITE_API_BASE_URL` (default empty string for same-origin proxy).

---

## 19. Testing Strategy

### 19.1 Frontend Tests

Add Vitest + React Testing Library.

**Critical Integration Test:**
Add one integration-style frontend test covering the core journey:
- Dashboard → select case → Case Detail → real timeline rendering

Additional component tests:
- `StatusBadge.test.tsx`, `MoneyValue.test.tsx`, `UnavailableMetric.test.tsx`, `ErrorState.test.tsx`.

---

## 20. Acceptance Criteria

P16 is NOT complete merely because `npm run build` passes.

### 20.1 Strict Truth Boundary Checks

- [ ] **No fake recovered revenue.** Must use graceful, visually secondary unavailable UI.
- [ ] **No fake recovery rate.** Must use graceful, visually secondary unavailable UI.
- [ ] **No fake provider-specific health.** Must only use unified system status.
- [ ] **No fake attention counts.** Must only summarize known OPEN cases.
- [ ] **No fake approval controls.** Must present workflow handoff notice instead of dead buttons.
- [ ] **Data Provenance Rule upheld:** All displayed business values map exactly to P15 endpoints or timeline events.

### 20.2 Visual & Interaction Quality

- [ ] Warm light palette implemented (no dark navy).
- [ ] Reduced density, generous whitespace, editorial hierarchy.
- [ ] Status badges use correct semantic colors (UNKNOWN ≠ SUCCESS).
- [ ] Robust font fallbacks configured.
- [ ] Meaningful motion applied (recovery progress, depth on hover, verified transition).

### 20.3 Build Quality

- [ ] Core journey integration test exists and passes.
- [ ] `npm run build` succeeds with zero errors.
- [ ] `uv run pytest` continues to pass (154 tests — backend unchanged).
- [ ] No TypeScript `any` types in domain interfaces.

---

## 21. Implementation Sequence

### Phase 1: Foundation
1. Clean up existing frontend.
2. Create `DESIGN.md` with full design token specification.
3. Update `index.css` with warm palette and font fallbacks.
4. Add font imports to `index.html`.
5. Create typed API client.

### Phase 2: Stitch Design Generation
6. Create new Stitch project.
7. Create design system.
8. Generate **Case Detail (Desktop)**.
9. Generate **Dashboard (Desktop)**.
10. Generate **Dashboard (Mobile)**.
*Ensure all prompts use neutral placeholders (e.g. `—`) so the generated React never copies placeholder business values as live data.*

### Phase 3: Core Components
11. Build layout, status, financial, data, and feedback components (including `UnavailableMetric` and restrained animations).

### Phase 4: Pages
12. Rebuild Dashboard (Wire to computed aggregates, Open Cases summary, Cases table).
13. Create CaseList page.
14. Rebuild CaseDetail (Wire to real API data + timeline event parsing).

### Phase 5: Polish & Verify
15. Add Vitest + core journey integration test.
16. Responsive & Accessibility pass.
17. Motion implementation (respecting reduced-motion).
18. Final build verification (`npm run build`, `uv run pytest`).

### Phase 6: Documentation
19. Update `DESIGN.md`.
20. Create P16 artifacts (implementation_report.md, verification.md, walkthrough.md, package-16.md checkpoint).
