---
name: Wealify
description: AI Financial Guardian — professional financial analysis interface
colors:
  primary: "#FF6B1A"
  primary-light: "#FFF1E8"
  primary-hover: "#E55A0F"
  destructive: "#DC2626"
  destructive-light: "#FEE2E2"
  destructive-foreground: "#FFFFFF"
  warning: "#D97706"
  warning-light: "#FFFBEB"
  success: "#16A34A"
  success-light: "#DCFCE7"
  neutral-bg: "#FFFFFF"
  neutral-surface: "#F9FAFB"
  neutral-muted: "#F3F4F6"
  neutral-border: "#E5E7EB"
  neutral-muted-foreground: "#6B7280"
  neutral-foreground: "#111827"
  neutral-secondary-foreground: "#374151"
typography:
  display:
    fontFamily: "Oswald, Bebas Neue, Impact, sans-serif"
    fontSize: "clamp(2.5rem, 6vw, 5rem)"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.02em"
  headline:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "1.875rem"
    fontWeight: 700
    lineHeight: 1.2
  title:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "DM Sans, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    letterSpacing: "0.05em"
    textTransform: "uppercase"
rounded:
  sm: "0.375rem"
  md: "0.5rem"
  lg: "0.75rem"
  full: "9999px"
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
  2xl: "3rem"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: "0.5rem 1rem"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.neutral-foreground}"
    border: "1px solid {colors.neutral-border}"
    rounded: "{rounded.md}"
    padding: "0.5rem 1rem"
  button-secondary-hover:
    borderColor: "{colors.primary}"
    textColor: "{colors.primary}"
  card:
    backgroundColor: "{colors.neutral-bg}"
    rounded: "{rounded.lg}"
    boxShadow: "0 1px 3px 0 rgb(0 0 0 / 0.1)"
    padding: "1.5rem"
  input:
    backgroundColor: "{colors.neutral-bg}"
    border: "1px solid {colors.neutral-border}"
    rounded: "{rounded.md}"
    padding: "0.75rem 1rem"
  input-focus:
    borderColor: "{colors.primary}"
    ringColor: "{colors.primary}"
  chip:
    backgroundColor: "{colors.primary-light}"
    textColor: "{colors.primary}"
    rounded: "{rounded.full}"
    padding: "0.125rem 0.625rem"
    fontSize: "0.75rem"
    fontWeight: 600
---

# Design System: Wealify

## Overview

**Creative North Star: "The Financial Analyst"**

Wealify's interface embodies the calm authority of a seasoned financial analyst — a professional who has seen thousands of statements, knows exactly what to look for, and communicates findings with precision and clarity. Every element earns its place on the screen. The design is structured, scanable, and trustworthy: data-dense without being cluttered, warm without being casual. It feels like the interface a CFO would trust, not a consumer fintech gimmick.

**The orange IS the brand.** Not a highlight color or an alert color — it is the dominant personality. It leads headings, fills primary actions, encodes brand identity across charts and containers. Blue exists only as a data/semantic secondary (online status, informational tones).

**Key Characteristics:**
- Orange-dominant palette with warm neutrals; no cold blue as primary
- Structured 2-column dashboard layout; clean data hierarchy
- Cards with subtle shadows; tonal depth through layering, not gradients
- DM Sans for body, Bebas Neue for display/headlines — analytical pairing
- Dashed upload zones as a recurring visual motif for the "document upload" workflow
- Emoji used sparingly as status icons — functional, not decorative
- Vietnamese-first labels with English secondary

## Colors

The palette is warm-neutral with an orange-dominant brand identity. Warm grays (not cool grays) ground the system. Orange is the primary action and brand color. Semantic colors (success, destructive, warning) use conventional hues.

### Primary

- **Wealify Orange** (`#FF6B1A`): Primary brand color. Buttons, active states, selected tabs, highlights, decorative accents, hover indicators. The dominant personality of the system.
- **Orange Hover** (`#E55A0F`): Hover and pressed states for all orange elements.
- **Orange Light** (`#FFF1E8`): Chip backgrounds, subtle tinted containers, data visualization fills.

### Neutral

- **Pure White** (`#FFFFFF`): Primary surface color for all cards, containers, inputs, and the main background.
- **Warm Surface** (`#F9FAFB`): Secondary surface for alternating rows, subtle containers, tab backgrounds.
- **Muted Surface** (`#F3F4F6`): Tertiary surface for nested containers, secondary backgrounds.
- **Border** (`#E5E7EB`): Default borders on cards, inputs, dividers.
- **Muted Text** (`#6B7280`): Secondary labels, placeholder text, captions, timestamps.
- **Body Text** (`#111827`): Primary text color for all headings and body copy.
- **Secondary Text** (`#374151`): Supporting text that is not muted but not primary.

### Semantic

- **Success / Green** (`#16A34A` / `#DCFCE7`): Income, positive amounts, online status indicators, success states.
- **Destructive / Red** (`#DC2626` / `#FEE2E2`): Errors, negative amounts, destructive actions, delete states.
- **Warning / Amber** (`#D97706` / `#FFFBEB`): Anomalies, flagged transactions, caution states.

### Named Rules

**The Brand Voice Rule.** Orange (`#FF6B1A`) appears on at least one dominant element per major screen section — a heading, a button, a chip, a highlight. It is never decoratively absent. Its rarity IS the point only for data alerts; for brand expression, it leads.

## Typography

**Display Font:** Oswald (with Bebas Neue/Impact fallback) — used for large section headings and the logo mark only. Oswald has the bold, condensed character of Bebas Neue while supporting Vietnamese glyphs (`Ả Ạ Ấ Ầ Ệ Ể Ộ Ủ Ứ Ỳ`).

**Body Font:** DM Sans (with system-ui fallback) — the complete type system. Clean, geometric, readable at all sizes. Excellent for financial data and UI labels.

**Character:** Professional and analytical. The Oswald/DM Sans pairing recalls financial terminals and editorial data journalism — serious without being cold, structured without being rigid.

### Hierarchy

- **Display** (Oswald, 600 weight, clamp 2.5–5rem, line-height 1, tracked): Major section headings, hero headlines. Only used sparingly — never for body or UI.
- **Headline** (DM Sans, 700 weight, 1.875rem, line-height 1.2): Card titles, section labels, primary headings within cards.
- **Title** (DM Sans, 600 weight, 1.25rem, line-height 1.3): Sub-headings, component labels, secondary headings.
- **Body** (DM Sans, 400 weight, 0.875rem, line-height 1.6): All prose, descriptions, chat messages, table content. Max line length ~75ch.
- **Label** (DM Sans, 500 weight, 0.75rem, letter-spacing 0.05em, uppercase): All UI labels, badges, tabs, metadata, timestamps, chip text.

### Named Rules

**The Label Rule.** Every interactive or navigational element has a text label. Icons alone are not sufficient — each icon is paired with a visible label or tooltip. Exception: emoji status indicators in transaction chips.

## Layout

**Grid Model:** Dashboard uses a 2-column layout on large screens (`lg:grid-cols-2`). Cards stack vertically within columns. The 3 upload zones sit in a 3-column grid above the main content. Responsive breakpoint collapses to single column on mobile.

**Container:** Standard `container mx-auto` with `px-4` horizontal padding. Max content width ~1280px.

**Spacing Rhythm:** 8px base unit. Primary spacing tokens: 4, 8, 12, 16, 24, 32, 48px. Cards use 24px internal padding. Section gaps use 24px. Component gaps use 16px.

**Density:** Medium density. Generous but not spacious — designed for data review, not marketing. Cards are compact enough that 4 stats fit across a row on desktop.

**Responsive:** Mobile-first with `sm`, `md`, `lg` breakpoints. Navigation collapses to icon-only on mobile. Dashboard columns stack. Upload grid goes 1-column on mobile, 3-column on desktop.

## Elevation & Depth

The system uses **shadow + tonal layering** — no ambient shadows, no glows. Depth is structural: elements that sit above other content cast a shadow. Elements at the same level share the same background tone.

### Shadow Vocabulary

- **Card Shadow** (`box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)`): Default card elevation. Every white card on white background has this shadow.
- **Subtle Shadow** (used on sticky header): `box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.05)`. Lighter weight for header/nav.

### Named Rules

**The Flat-By-Default Rule.** Cards, containers, and inputs are flat at rest. Shadows appear only on elements that visually float above a same-toned surface. The white background is the ground plane; cards float above it.

**The Border-Before-Shadow Rule.** When a card or container needs visual separation from its surroundings, a border is preferred over a shadow if the separation is subtle. Cards use both border (when adjacent to other cards) and shadow (when floating over the page background).

## Shapes

**Corner Strategy:** `0.5rem` (8px) as the default corner radius. Buttons, cards, inputs, chips all use this. Larger containers can use `0.75rem` (12px). The radius is consistent across all components — no mixing of `rounded-sm` with `rounded-lg` in the same context.

**Border Strategy:** Light gray borders (`#E5E7EB`) for input containers, card dividers, and secondary containers. Orange borders (`#FF6B1A`) for focus states and selected/active states.

**Dashed Zones:** Upload dropzones use `border-2 border-dashed` — a distinctive recurring form motif that signals "drop something here" and distinguishes the upload workflow visually.

**Clipping:** No clipping masks. No diagonal cuts. The form language is orthogonal and clean.

## Components

### Buttons

- **Shape:** 8px radius (`rounded-md`), no border by default.
- **Primary (orange):** Orange background (`#FF6B1A`), white text, 12px 24px padding. Hover darkens to `#E55A0F`. Used for: main CTAs, upload triggers, send actions.
- **Ghost / Secondary:** Transparent background, gray border, dark text. Hover border turns orange, text turns orange. Used for: secondary actions, cancel, settings.
- **Icon Buttons:** Square-ish padding, centered icon. Used in chat send button, close buttons.
- **States:** Disabled = 50% opacity, no pointer events. Loading = spinner replaces icon, button disabled.

### Cards

- **Corner Style:** 12px radius (`rounded-lg`).
- **Background:** Pure white (`#FFFFFF`) on the gray page background.
- **Shadow:** Default card shadow (see Elevation section). No border by default.
- **Internal Padding:** 24px on all sides.
- **Border Bottom:** Card headers use a bottom border to separate title from content.

### Input Fields

- **Style:** White background, 1px gray border, 8px radius.
- **Focus:** Orange border + orange ring (`ring-2 ring-orange-500 ring-offset-1`).
- **Placeholder:** Gray text (`#9CA3AF`), lowercase, normal weight.
- **Textarea:** Same styling, min-height 80px, resize vertical only.
- **Drag Zone (upload):** Dashed 2px border, slightly tinted background on hover/drag, blue border color change on active drag.

### Navigation / Header

- **Style:** White background, bottom border, sticky positioning. Logo + title on left, actions on right.
- **Typography:** Logo = bold 20px, subtitle = muted 12px. Nav links = 14px medium weight.
- **Tab Bar (Dashboard):** Pill-shaped tab group, gray background container, white active tab, subtle shadow on active.

### Transaction List Item

- **Layout:** Flex row — left (icon + metadata), right (amount + mask). Bottom border divider.
- **Type Chip:** Colored background chip (green/red/gray/amber) with type label. Used consistently across all transaction views.
- **Status Indicators:** Emoji (`⚠️`) used inline for flagged transactions. Colored dot indicators for transaction type.
- **Alert Reason:** Subtle tinted container below the main row when an anomaly is detected.

### Chat Interface

- **Container:** White card with header, scrollable message area, fixed input footer.
- **Message Bubbles:** Rounded-2xl (18px) corners. User = orange background (right-aligned). Assistant = light gray background (left-aligned).
- **Avatar:** Circular, 32px. User = orange with white icon. Assistant = gray with bot icon.
- **Input:** Textarea that auto-grows, send button right-aligned.
- **Status:** Online indicator = green dot with pulse animation.

### Chips / Badges

- **Default Chip:** Orange light background, orange text, full pill shape, small 500-weight text.
- **Semantic Chips:** Green/Red/Amber background-light variants for transaction type labels.
- **Active Tab:** White background with shadow, orange text.
- **Recurring Badge:** Orange-tinted chip, consistent across all transaction views.

### File Upload Cards

- **Layout:** Centered content, dashed border, icon + title + accepted formats label.
- **Drag State:** Blue border on drag-over (current implementation; brand-consistent upgrade would be orange).
- **File Selected State:** File name shown with remove button, upload CTA below.
- **Loading State:** Spinner replaces upload icon, "Processing..." label.

## Do's and Don'ts

### Do:

- **Do** use orange as the primary action color on every screen. Every page needs at least one orange CTA.
- **Do** use Bebas Neue for section headings and hero text. It is the brand's display voice.
- **Do** use DM Sans for all body text, labels, and UI elements.
- **Do** use card shadows consistently — every white card floating on the page background should have the card shadow.
- **Do** use rounded-md (8px) as the default corner radius across all components.
- **Do** use dashed borders for upload dropzones — this is a recurring, intentional visual motif.
- **Do** mask card numbers to `**** XXXX` format. Never show full card numbers.
- **Do** use Vietnamese labels in the UI with English as secondary.

### Don't:

- **Don't** use blue as a primary action color. The existing blue in `globals.css` (`hsl(221.2 83.2% 53.3%)`) is the incumbent anti-pattern to replace.
- **Don't** use gradients as background fills. The system is flat with tonal layering only.
- **Don't** use emoji for anything other than functional status indicators (✅ ✅ ✅ in transaction chips).
- **Don't** use Inter font in new implementations. Migrate to DM Sans.
- **Don't** use shadows as decoration. A shadow always means the element floats above something.
- **Don't** show real card numbers, CVV, or full account numbers. Mask everything.
- **Don't** send alerts without user confirmation — this is a product constraint, not a visual one, but it informs empty/pending state design.
