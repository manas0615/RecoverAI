# RecoverAI Design System
**Version:** 2.0 (Warm Premium)  
**Status:** Approved & Implemented (Package 16)

## 1. Overview
The RecoverAI frontend utilizes a "Warm Premium" visual direction designed to communicate calm, clarity, and financial trust. This replaces the legacy dark-navy "SOC dashboard" aesthetic with an editorial layout featuring reduced card density and generous whitespace.

## 2. Stitch MCP Design References
The following high-fidelity design references were generated via Stitch MCP to establish the structural composition and visual rules.

**The single canonical Stitch project used for P16:**
- **Project ID:** `1051231661397186252` (Title: RecoverAI v2 — Warm Premium)
- **Design System Asset:** `assets/15122457507156157995`

**Generated Screens:**
- Case Detail (Desktop)
- Dashboard (Desktop)
- Dashboard (Mobile)
- Recovery Cases List (Desktop)
- Recovery Cases List (Mobile)
- Case Detail — WAITING_APPROVAL / ESCALATED
- Case Detail — UNKNOWN
- Case Detail — VERIFIED_SUCCESS

*Note: The generated Stitch screens used neutral placeholders (e.g. `₹—`) to separate structural design from live production data.*

## 3. Core Principles
1. **Reduced Density:** Fewer persistent borders, selective use of elevated surfaces.
2. **Editorial Hierarchy:** Typography establishes order of importance.
3. **Data Provenance:** The UI never fabricates missing metrics; it degrades gracefully.
4. **Verified Success:** Green styling is strictly reserved for verified revenue recovery. All UNKNOWN or ESCALATED states utilize warning/amber treatments.
5. **Touch-First Accessibility:** All interactive elements on mobile adhere to a 44x44px minimum tap target.

## 4. Design Tokens (Tailwind v4 @theme)

### 4.1 Typography
- **Display (Hero numbers):** `Plus Jakarta Sans`, system-ui, sans-serif
- **Body & Labels:** `Inter`, system-ui, sans-serif
- **Mono (Financials/IDs):** `JetBrains Mono`, ui-monospace, monospace

### 4.2 Color Palette

**Foundation**
- `bg`: `#FAFAF7` (Warm off-white)
- `surface`: `#FFFFFF`
- `surface-secondary`: `#F5F0EB`
- `border`: `#E7E0D8`
- `border-subtle`: `#F0EBE4`

**Text**
- `text-primary`: `#1C1917` (Stone 900)
- `text-secondary`: `#57534E` (Stone 600)
- `text-muted`: `#A8A29E` (Stone 400)

**Semantic States**
- `success`: `#059669` (Emerald 600) | bg: `#ECFDF5`
- `warning`: `#D97706` (Amber 600) | bg: `#FFFBEB`
- `danger`: `#DC2626` (Red 600) | bg: `#FEF2F2`
- `info`: `#2563EB` (Blue 600) | bg: `#EFF6FF`
- `neutral`: `#78716C` (Stone 500) | bg: `#F5F5F4`

**Brand**
- `primary`: `#2563EB`

### 4.3 Motion
Restrained interactions respecting `prefers-reduced-motion`:
- Skeleton shimmer (`1.5s linear`)
- Hover elevation (`150ms transition-shadow`)
- Fade-in page transitions (`300ms ease-out`)
