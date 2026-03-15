# Lift Link Studio - Lovable UX/UI Prompts

> Audit complet et liste de prompts pour améliorer le design, l'UX/UI et le responsive de la plateforme Lift Link Studio (app pour coachs sportifs et athlètes).

---

## URGENT — Fix EnhancedExerciseCard Simple Mode (collapsed state)

**Problème** : En mode Simple, les cards exercices sont cassées sur mobile — noms sur 3 lignes, tags empilés verticalement, boutons qui compressent le contenu.

#### Prompt 0 — Fix Exercise Cards Simple Mode

```
Redesign the EnhancedExerciseCard component in Simple mode (non-expanded/collapsed state) to be clean and compact on mobile. Currently it looks broken: exercise names wrap on 3 lines, tags (sets, reps, rest) stack vertically under the icon, and action buttons compress the content area.

Here's the new layout for the collapsed card header (Simple mode):

LINE 1: Exercise name on a single line (truncated with ellipsis if too long), with a small completion checkmark or chevron on the far right.

LINE 2: All tags (sets count, reps range, rest time) displayed inline as a single readable string like "4s · 6-8 reps · 2'30 rest" in text-xs text-muted-foreground — NOT as separate badge chips. This is simpler and takes one line instead of wrapping.

LINE 3 (optional): Only show action buttons (swap, skip, coach instructions) when the card is the active exercise. For non-active cards, hide all action buttons to save space.

Remove the dumbbell/timer icon from the collapsed state in Simple mode — it adds visual noise without value. The exercise name is enough.

Keep the card compact: max height of ~56px for inactive cards (name + inline tags only). Active card can be taller with action buttons shown.

The expanded state (when chevron is clicked) remains unchanged — show the set grid, video, timer etc. as before.

Make sure Advanced mode is NOT affected by these changes — it should keep the current badge/tag layout with tempo and RPE badges.

Specific CSS fixes needed:
- Exercise name: use "text-sm font-semibold truncate" with the parent having "min-w-0 flex-1" so truncation actually works
- Tags line: replace the flex-wrap badge layout with a simple text span in Simple mode: "{sets}s · {repsMin === repsMax ? repsMin : repsMin+'-'+repsMax} reps · {formattedRest}"
- Card padding: p-3 is fine but reduce gap between icon area and text from gap-3 to gap-2
- Action buttons: wrap in {isActive && (...)} for Simple mode so they only show on the current exercise
- Chevron: always visible, aligned to the right edge

The goal is that on a 375px screen, an athlete should see 5-6 exercise cards without scrolling, each showing the exercise name and key params at a glance. Think of the Hevy app exercise list: clean, scannable, one line per exercise when collapsed.
```

---

## CODE REVIEW #2 — Problèmes critiques (Mars 2026)

### Findings

| # | Sévérité | Problème | Fichiers |
|---|----------|----------|----------|
| 1 | CRITIQUE | Bottom nav **pas fixe** — participe au flux flex, peut disparaître au scroll | StudentLayout.tsx:74, CoachLayout.tsx:78, AdminLayout.tsx:120 |
| 2 | CRITIQUE | **Aucun bottom padding** sur `<main>` — contenu masqué derrière la nav mobile | Les 3 layouts, balise `<main>` |
| 3 | CRITIQUE | Classe `safe-area-bottom` **n'existe pas** dans Tailwind — iPhone à encoche cassé | Les 3 layouts, bottom nav |
| 4 | HAUT | Pages Support standalone (`/support`, `/support/help`, `/support/ticket/:id`) — **pas de bottom nav, pas de retour app** | App.tsx routes, SupportPage, KBLayout |
| 5 | HAUT | Coach bottom nav items `py-1 px-1.5` — zones de tap **~36px** au lieu de 44px | CoachLayout.tsx:82, AdminLayout.tsx:127 |
| 6 | HAUT | Dropdown "Plus" peu discoverable — items cachés derrière un menu overflow | CoachLayout.tsx:90-105, AdminLayout.tsx:136-151 |
| 7 | MOYEN | KBArticle sans breadcrumb — l'utilisateur est perdu dans les articles | KBArticle.tsx |
| 8 | MOYEN | Z-index conflits : OnboardingTooltip z-60 > Dialog z-50, AISidebar z-50 = Dialog z-50 | OnboardingTooltip.tsx:51, AISidebar.tsx:98 |
| 9 | MOYEN | `vh` au lieu de `dvh` dans modals — contenu inaccessible avec barre d'adresse mobile | SessionBuilderModal.tsx:215, FreeSessionCreator.tsx:167 |
| 10 | MOYEN | AISidebarToggle `bottom-20` — peut chevaucher la bottom nav sur petits écrans | AISidebarToggle.tsx:20 |

---

### Prompt N1 — Fix Bottom Nav: Truly Fixed + Safe Area (URGENT)

```
CRITICAL FIX: The mobile bottom navigation bar in all 3 layout files (StudentLayout.tsx, CoachLayout.tsx, AdminLayout.tsx) is NOT truly fixed — it sits inside a flex column and participates in normal document flow. On long pages, content scrolls behind it or the nav can shift.

Fix ALL 3 layouts with this exact approach:

1. Make the bottom nav truly fixed:
   - Add "fixed bottom-0 left-0 right-0" to the <nav> element on mobile
   - Add "z-30" to ensure it stays above page content but below modals (z-50)
   - Add "bg-background/95 backdrop-blur-md" for a polished glass effect when content scrolls underneath

2. Add proper safe-area-inset for notched iPhones:
   - Remove the non-existent "safe-area-bottom" class
   - Add inline style: style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
   - OR add this to the global CSS: .safe-area-bottom { padding-bottom: env(safe-area-inset-bottom, 0px); }
   - Also add to tailwind.config.ts a custom utility if preferred

3. Add bottom padding to the <main> content area to prevent content from being hidden behind the fixed nav:
   - Change <main> className to include "pb-20 md:pb-0" (80px on mobile to account for nav height ~64px + breathing room, 0 on desktop since sidebar is used)

4. Fix touch targets on bottom nav items:
   - StudentLayout: already has min-h-[44px] — GOOD
   - CoachLayout: change "py-1 px-1.5" to "py-1.5 px-2 min-h-[44px] min-w-[44px] justify-center" on all nav items AND the MoreHorizontal dropdown trigger
   - AdminLayout: same fix as CoachLayout

5. Add a subtle top border shadow to the fixed nav: "shadow-[0_-1px_3px_rgba(0,0,0,0.1)]" for visual separation

Apply these changes to ALL 3 files: StudentLayout.tsx, CoachLayout.tsx, AdminLayout.tsx. Do NOT change the desktop sidebar behavior — only the mobile bottom nav.
```

---

### Prompt N2 — Fix Support Pages: Add Navigation Back to App

```
The Support pages (/support, /support/help, /support/new, /support/ticket/:ticketId, /aide) render OUTSIDE of StudentLayout/CoachLayout. This means they have NO bottom navigation bar and NO way to return to the main app except browser back button.

Fix this by adding a persistent header bar to ALL support-related pages:

1. Create a SupportHeader component that shows:
   - Left: Back arrow button that navigates to the user's home page (use the auth context to determine role — /student for athletes, /coach for coaches, /admin for admins)
   - Center: "Support" or "Help Center" title
   - Right: UserMenu component for profile/logout access

2. Add this SupportHeader to:
   - SupportPage.tsx (the main /support page)
   - KBLayout.tsx (the /support/help knowledge base)
   - TicketForm (the /support/new page)
   - TicketDetail (the /support/ticket/:ticketId page)

3. On KBLayout specifically, add breadcrumbs inside KBArticle:
   - Show: "Help Center > [Category Name] > [Article Title]"
   - "Help Center" links back to /support/help
   - Category links to the category section in the sidebar
   - Current article is non-clickable text

4. On TicketDetail, the existing back button navigates to /support — this is correct, keep it.

5. Style the header consistently with the main app headers: "flex items-center justify-between p-3 border-b border-border bg-background sticky top-0 z-30"

This ensures users are NEVER trapped on support pages without a way to navigate back to the main application.
```

---

### Prompt N3 — Fix Viewport Height & Z-Index Issues

```
Fix viewport height and z-index stacking issues across the app:

VIEWPORT HEIGHT FIXES:
1. SessionBuilderModal.tsx: Change h-[92vh] to h-[92dvh] with fallback h-[92vh] (use className="h-[92vh] h-[92dvh]" — browsers that support dvh will use it, others fall back to vh)
2. FreeSessionCreator.tsx: Change h-[90vh] to h-[90dvh] with same fallback pattern
3. CoachExercises.tsx: Change max-h-[80vh] to max-h-[80dvh]
4. AdminKB.tsx: Change max-h-[85vh] to max-h-[85dvh]
5. AdminSupport.tsx: Change max-h-[80vh] to max-h-[80dvh]
6. KBLayout.tsx sidebar: Change h-[calc(100vh-3.5rem)] to h-[calc(100dvh-3.5rem)]

This prevents content from being cut off when mobile browsers show/hide the address bar.

Z-INDEX STACKING FIXES:
1. OnboardingTooltip.tsx: Change z-[60] to z-[45] — tooltips should appear BELOW modals (z-50), not above
2. AISidebar.tsx backdrop: Change z-50 to z-[55] — AI sidebar should appear ABOVE regular dialogs since it's a persistent panel
3. AISidebar.tsx content panel: Change z-50 to z-[55] to match backdrop
4. AISidebarToggle.tsx: Change bottom-20 to bottom-24 (96px) to properly clear the mobile bottom nav which is ~64px + safe area

Establish this z-index scale as a reference:
- z-10: Sticky headers within page content
- z-20: Floating action buttons
- z-30: Fixed bottom nav, fixed headers
- z-40: Dropdowns, popovers, tooltips
- z-50: Modal dialogs, sheets, drawers
- z-55: AI Sidebar (persistent panel)
- z-100: Toasts/notifications (already correct)
```

---

### Prompt N4 — Every Page Must Have Back Navigation

```
Add consistent back navigation to EVERY page in the app so users can ALWAYS navigate backwards without relying on the browser back button.

COACH DETAIL PAGES (already have back buttons — verify and standardize):
- StudentDetail: Has back button → /coach/students ✓
- CoachProgramDetail: Has back button → parent student ✓
- ProgramEditor: Has back button → parent ✓
- StudentBilan: Has back button (navigate(-1)) ✓

ADD BREADCRUMBS to coach detail pages:
- StudentDetail: "Students > [Student Name]"
- CoachProgramDetail: "Students > [Student Name] > [Program Name]"
- ProgramEditor: "Students > [Student Name] > New Program" or "Edit [Program Name]"
- StudentBilan: "Students > [Student Name] > Bilan AI"

Create a reusable Breadcrumb component:
- Props: items: { label: string, to?: string }[]
- Render: Items separated by ">" chevron icons
- Last item is current page (no link, bold text)
- On mobile (< md): Show only back arrow + current page name (collapse intermediate levels)
- Style: text-sm text-muted-foreground, links are hover:text-foreground
- Place it at the top of each page, before the main content

STUDENT PAGES (add contextual navigation):
- StudentNutrition: Has back button → /student ✓
- LiveSession: Has sticky back/quit button ✓
- AthleteProgramEditor: Has back button ✓

These are already good, but add the same Breadcrumb component for consistency:
- LiveSession: "Week > [Session Name]" (back arrow only on mobile)
- StudentNutrition: "Profile > Nutrition"

LANDING/AUTH PAGES (no changes needed — these are standalone entry points).
```

---

### Prompt N5 — Optimize Every Clickable Element

```
Perform a comprehensive pass on EVERY interactive element in the app to ensure optimal click/tap experience:

1. MINIMUM TAP TARGET SIZE — 44x44px on ALL clickable elements:
   - All icon-only buttons must be min-w-[44px] min-h-[44px] (use padding to expand hit area if visual size should stay small)
   - All text buttons must have min-h-[44px] with adequate horizontal padding
   - All nav items must have min-h-[44px]
   - All dropdown triggers must have min-h-[44px]

2. VISUAL FEEDBACK on every clickable element:
   - Buttons: Add active:scale-[0.97] transition-transform for press feedback
   - Cards/list items: Add active:bg-accent/50 for tap feedback
   - Icon buttons: Add hover:bg-secondary active:bg-secondary/80
   - Links: Add hover:text-foreground transition-colors
   - Ensure ALL elements have cursor-pointer when clickable

3. SPACING between adjacent tap targets:
   - Minimum 8px gap between any two clickable elements
   - In the bottom nav, ensure items have at least 8px between them
   - In exercise card action buttons (swap, skip, chevron), add gap-2 minimum
   - In form rows with multiple buttons, add gap-2 minimum

4. DISABLED STATES — make them visually clear:
   - All disabled buttons: opacity-50 cursor-not-allowed (not just opacity-40)
   - All disabled inputs: bg-muted/50 text-muted-foreground cursor-not-allowed
   - Never allow click events on disabled elements (check all onClick handlers)

5. FOCUS STATES for keyboard/accessibility:
   - Add focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 to ALL interactive elements
   - This is critical for accessibility and also helps with tablet users using external keyboards

6. SPECIFIC COMPONENTS to fix:
   - CircularRestTimer: +/- buttons from 32px to 48px
   - EnhancedExerciseCard duration steppers: from h-4 (16px) to h-8 (32px) minimum, with 44px tap area via padding
   - LiveExerciseList drag handles: from w-3.5 (14px) to w-6 (24px) with min-h-[44px] tap area
   - WeeklyCheckinForm soreness buttons: from 32px to 44px
   - CoachLayout/AdminLayout "More" dropdown trigger: ensure 44px tap area
   - UserMenu trigger: ensure 44px tap area
```

---

### Prompt N6 — Sticky Headers on Every Page

```
Add persistent sticky headers to all main pages so users always know where they are and can navigate. The header should NEVER scroll away.

LAYOUT-LEVEL CHANGES:
1. In StudentLayout, CoachLayout, AdminLayout: The mobile header is already in flow but NOT sticky. Make it sticky:
   - Add "sticky top-0 z-30 bg-background/95 backdrop-blur-md" to the mobile <header> element
   - This ensures the logo + user menu are always visible

2. On desktop, the sidebar is already fixed — no changes needed.

PAGE-LEVEL STICKY HEADERS:
For pages that have their own title/action bar, make those sticky too:

3. StudentWeek: The week selector (day tabs) should be sticky below the main header:
   - Wrap the week navigation in a sticky container: "sticky top-[57px] z-20 bg-background/95 backdrop-blur-md py-2 -mx-4 px-4"
   - This ensures the day selector is always visible while scrolling through sessions

4. CoachStudents: The search/filter bar should be sticky:
   - Wrap the search input and filters in: "sticky top-[57px] z-20 bg-background/95 backdrop-blur-md py-2 -mx-4 px-4"

5. CoachExercises: The search bar and category filter should be sticky:
   - Same sticky pattern as CoachStudents

6. LiveSession: The session header (elapsed time, progress) is already sticky — verify it uses proper z-index (z-20) and backdrop-blur

7. StudentProfile: The tab navigation (info/nutrition/notifications) should be sticky:
   - Wrap tabs in: "sticky top-[57px] z-20 bg-background py-2"

IMPORTANT: All sticky elements should use backdrop-blur-md and bg-background/95 for a polished glass effect. The stacking should be:
- z-30: Main layout header + bottom nav (fixed)
- z-20: Page-level sticky headers (sticky)
- z-10: In-page sticky elements (if any)
```

---

## Architecture existante

- **Stack** : React + Tailwind + shadcn/ui + Supabase
- **Breakpoint mobile** : 768px
- **Thème** : Violet #6C5CE7, glassmorphism, dark mode complet
- **Mode d'affichage** : Simple (Essential) vs Advanced (Pro) — persisté en DB
  - **Simple** : Sets/reps/poids, timer linéaire, calories uniquement, 4 dernières sessions
  - **Avancé** : Tempo, RPE, volume, macros détaillés, historique complet, timer circulaire, body evolution

---

## Audit - Faiblesses identifiées

| Catégorie | Problème |
|-----------|----------|
| Touch targets | 16-32px vs 44px recommandé (steppers, timer, soreness buttons) |
| Navigation | Pas de breadcrumbs, dropdown "More" peu discoverable |
| Formulaires | Pas de validation visible, pas d'états d'erreur, pas de floating labels |
| Animations | Swipe instantané (pas de transition), pas de célébrations |
| Accessibilité | ARIA manquants, pas de focus-visible, progress bars sans role |
| Responsive | Grilles fixes cassées sous 375px, emojis qui débordent |
| Mode toggle | Petit bouton peu discoverable, pas d'explication au switch |

---

## Prompts Lovable par priorité

### PRIORITE 1 — Mobile & Responsive

#### Prompt 1 — Navigation mobile modernisée

```
Redesign the mobile bottom navigation bar to follow iOS/Android native patterns. Replace the current "More" dropdown with a scrollable horizontal tab bar showing all items. Add a floating action button (FAB) for the primary action (start session for athletes, create program for coaches). Use spring animations on tab switches. Add haptic feedback patterns. The active tab should have a filled icon + label, inactive tabs icon-only. Add a subtle blur backdrop to the nav bar. Ensure all touch targets are minimum 48x48px with 8px spacing between them.
```

#### Prompt 2 — Responsive sous 375px

```
Fix all responsive layouts for screens under 375px (iPhone SE). The emoji rating buttons (5 in a row) in WeeklyCheckinForm and SessionFeedbackWizard must wrap to 3+2 layout on small screens. The exercise set grid in EnhancedExerciseCard must stack weight and reps inputs vertically below 375px instead of the fixed 5-column grid. All cards must have minimum padding of 12px. Add horizontal scroll-snap for week selectors and program tabs. Test and fix every form and card layout at 320px width.
```

#### Prompt 3 — Touch targets & zones de tap

```
Increase all interactive touch targets to minimum 44x44px across the entire app. Specifically: CircularRestTimer control buttons (+/- and play/pause) from 32px to 48px, duration steppers in EnhancedExerciseCard from 16px to 40px, soreness location buttons in WeeklyCheckinForm from 32px to 44px, grip handles in LiveExerciseList from 14px to 24px width with a 44px hit area. Add minimum 8px gap between all adjacent touch targets. Use padding to increase tap zones without changing visual size where needed.
```

---

### PRIORITE 2 — Expérience athlète premium (simple + avancé)

#### Prompt 4 — Live Session immersive (respecte simple/avancé)

```
Redesign the LiveSession page as a full-screen immersive workout experience inspired by Hevy and Strong apps. In Simple mode: keep a clean, distraction-free interface — large weight/reps inputs (48px height), a linear rest timer with progress bar, and a clear "Next exercise" preview at the bottom. No tempo, no RPE, no progression timeline — just sets to complete with a big checkmark button. In Advanced mode: add the circular rest timer with gradient stroke and pulsing glow, show tempo/RPE tags on each exercise, display previous session comparison arrows next to inputs, show the progression timeline button, and add substitution notices. Both modes: add a persistent top bar (elapsed time, total volume, sets completed ratio), swipe-left-to-complete-set gesture with spring animation, confetti + vibration on session completion, and dark theme during workout. The transition between modes should be seamless — toggling mid-session should animate elements in/out smoothly without losing workout state.
```

#### Prompt 5 — Dashboard athlète (respecte simple/avancé)

```
Redesign the StudentWeek and student dashboard inspired by Strava and Whoop. In Simple mode: show a clean weekly view with a horizontal scrollable day timeline centered on today. Each day card shows only: session name, duration estimate, completion checkmark. The WeeklySummaryCard shows 2-column grid (sessions done, check-in status). The WaterTracker shows just current intake vs goal in ml. StrengthProgressChart shows only last 4 sessions with max weight line. In Advanced mode: expand the WeeklySummaryCard to 4 columns + total volume card. WaterTracker adds percentage display and 7-day history mini-chart. StrengthProgressChart shows all data points with a max-weight/volume toggle. Add weekly load sparklines. Add body evolution section and progress photos on the Progress page. Both modes: add an activity ring at the top showing weekly training completion, a "Today's Focus" hero card for the next session with one-tap start, smooth page transitions between days. The mode toggle (Zap/Target icon) should be prominently placed in the header and animate content blocks in/out when switched.
```

#### Prompt 6 — Dashboard coach (respecte le mode des athlètes)

```
Redesign the CoachDashboard with a modern layout inspired by Linear/Notion. Important: each student card must visually indicate whether that student is in Simple or Advanced display mode (show a small Zap icon for advanced, Target icon for simple). This helps coaches understand what their athletes see. In the student detail view, the coach should see ALL data (advanced view) regardless of the student's mode, but with a visual banner showing "This athlete uses Simple mode — they don't see: tempo, RPE, volume charts, body evolution". On CoachExercises page, show full descriptions always (don't truncate for coaches). Add Kanban columns: "Needs Attention", "In Progress", "On Track", "Inactive". Add command palette (Cmd+K), notification badges, collapsible sidebar with pinned students.
```

#### Prompt 7 — Micro-interactions (adapté simple/avancé)

```
Add delightful micro-interactions throughout the app, adapted to the display mode. In Simple mode: keep animations minimal and functional — a gentle checkmark scale-bounce on set completion, a brief toast on exercise completion, a celebration screen with confetti on session end. Simple mode should feel calm and focused. In Advanced mode: richer animations — set completion shows checkmark + comparison arrow animation (green slide-up for improvement, red for regression), RPE badge pulses when selected, tempo countdown visualizes each phase (eccentric/pause/concentric). Volume counting-up effect on session recap. PR detection with gold star burst animation. Circular rest timer pulses and glows when time is up. 7-day water chart bars animate in sequence. Both modes: spring animations on card expand/collapse, scale-press (0.97) on button touch, smooth mode toggle transition animating content blocks in/out.
```

#### Prompt 7b — Mode toggle UX amélioré

```
Redesign the Simple/Advanced mode toggle (DisplayModeToggle) to be more discoverable and informative. Replace the small icon+text button with a segmented control (pill-shaped toggle) showing "Essential" and "Pro" labels with their respective icons (Target and Zap). Place it prominently in the app header on both mobile and desktop. When switching modes, show a brief overlay explaining what changed: "Pro mode enabled — you now see: RPE tracking, tempo, volume analytics, body stats, detailed nutrition macros" or "Essential mode — streamlined view for focused training". Animate all affected content blocks: elements exclusive to Advanced mode should slide-in from the right with a stagger delay when enabling Pro, and fade-out when switching to Essential. Add a first-time tooltip explaining the feature: "Switch between Essential (clean & simple) and Pro (detailed analytics) anytime". Persist the choice to the database as already implemented.
```

---

### PRIORITE 3 — Formulaires & Onboarding

#### Prompt 8 — Formulaires modernes

```
Upgrade all form inputs across the app to modern patterns. Add floating labels that animate up when focused (like Material Design). Add inline validation with red border + error message appearing with a slide-down animation. Show a green checkmark when a field is valid. For numeric inputs (sets, reps, weight), use large stepper buttons (+/-) instead of raw number inputs on mobile. Add inputMode="numeric" to all number fields for proper mobile keyboard. Add a progress bar at the top of multi-step forms (WeeklyCheckinForm, SessionFeedbackWizard) showing "Step 2 of 4". Add auto-focus to the next empty field after completing one.
```

#### Prompt 9 — Onboarding athlète (inspiré Freeletics/Fitbod)

```
Create a premium onboarding flow for new athletes inspired by Freeletics and Fitbod. After signup, show a 4-step wizard: 1) Profile photo + name with large avatar upload area, 2) Training goal selection with illustrated cards (muscle gain, fat loss, strength, endurance), 3) Experience level with visual slider (beginner/intermediate/advanced) and body illustration, 4) Schedule preference with interactive weekly calendar grid. Each step should animate in from the right with a spring transition. Add a skip button but show a completion percentage to encourage finishing. End with a personalized "Your plan is ready" celebration screen.
```

#### Prompt 10 — Landing page premium (inspiré Arc/Linear)

```
Redesign the landing page with a premium dark aesthetic inspired by Arc browser and Linear websites. Replace the current hero with a full-viewport hero featuring: an animated gradient mesh background (purple to blue), a large bold headline with text-reveal animation on scroll, a floating 3D mockup of the app on mobile. Add scroll-triggered section reveals with parallax effects. Feature section should use bento grid layout (like Apple) with interactive hover cards that tilt in 3D. Pricing section should use glass-morphism cards with a glowing border on the recommended plan. Add smooth scroll-linked progress indicator in the nav bar. Add a "trusted by" section with coach avatar carousel.
```

---

### PRIORITE 4 — Navigation & Architecture

#### Prompt 11 — Breadcrumbs & navigation contextuelle

```
Add a breadcrumb navigation system to all detail pages in the coach and student interfaces. Show the full path like: Dashboard > Student Name > Program Name > Week 3. Each breadcrumb should be clickable to navigate back to that level. On mobile, collapse intermediate levels and show only parent + current page with a back arrow. Add a slide-in page transition animation when navigating deeper (slide from right) and when going back (slide from left). Add a command palette (Ctrl+K / Cmd+K) accessible from anywhere for quick search of students, programs, exercises.
```

#### Prompt 12 — Sidebar coach repensée

```
Redesign the coach desktop sidebar with a modern collapsible layout inspired by Discord/Slack. Add a "Favorites" section at the top with pinned students (drag to pin). Add student avatars with online/active status indicators (green dot). Group navigation items into sections: "Overview" (dashboard, calendar), "Clients" (students list, recommendations), "Programs" (templates, exercises), "AI Tools" (bilan, adaptation). Add a mini-mode (icon-only, 60px wide) that expands on hover. Show unread notification count badges next to relevant sections. Add a search bar at the top of the sidebar.
```

---

### PRIORITE 5 — Composants spécifiques

#### Prompt 13 — Rest timer gamifié

```
Redesign the CircularRestTimer component as a gamified experience. Make the circle larger (200px diameter) with a thick gradient stroke (purple to blue). Add a pulsing glow effect when timer is running. When rest is complete, animate the circle filling with green and show a "GO!" text with a bounce animation. Add +15s / -15s quick-adjust buttons as large pill-shaped buttons below the timer. Add a motivational message that changes each rest period ("Almost there!", "Stay focused", "Breathe deep"). Show the upcoming exercise name and target sets below the timer for mental preparation. Add a sound effect toggle with a speaker icon.
```

#### Prompt 14 — Progress charts premium (inspiré Apple Health)

```
Redesign the StrengthProgressChart and all data visualizations inspired by Apple Health. Use smooth curved lines instead of straight connections. Add an interactive tooltip that follows touch/cursor showing exact values. Add a date range selector (1W, 1M, 3M, 6M, 1Y, ALL) as pill-shaped tabs. Show personal records as gold star markers on the chart. Add a subtle gradient fill below the line. For the WeeklySummaryCard, use circular progress rings (like Apple Watch) instead of flat progress bars. Add animated number counting when cards appear in viewport. Use a consistent chart color palette across all visualizations. Remember: in Simple mode, only show last 4 sessions and max weight only. In Advanced mode, show all data with volume toggle.
```

#### Prompt 15 — Session recap & partage social

```
Redesign the SessionRecap component as a shareable workout summary card. Create a beautiful card layout with: gradient background matching the session type, large stats (duration, volume, sets, PRs) with animated counting numbers, exercise list with completion checkmarks, personal records highlighted in gold. Add a "Share to Instagram Stories" button that generates a 1080x1920 image of the recap card with the app branding. Add "Share with Coach" button. Add a streak counter ("5 sessions this week!"). The card should appear with a slide-up animation and confetti on first render. Add coach feedback section below where the coach's comment appears with typing animation.
```

---

### PRIORITE 6 — Accessibilité & Performance

#### Prompt 16 — Accessibilité WCAG AA

```
Perform a full accessibility pass on the entire application. Add aria-labels to all icon-only buttons (move up/down, delete, expand/collapse). Add role="progressbar" with aria-valuenow and aria-valuemax to WaterTracker and all progress indicators. Add visible focus-visible rings (2px solid blue, 2px offset) to all interactive elements. Replace emoji-only labels with emoji + text labels (show text on hover/focus). Add proper aria-live regions for dynamic content (rest timer completion, set validation, toast notifications). Ensure all color combinations meet WCAG AA contrast ratio (4.5:1 for text, 3:1 for large text). Add skip-to-content link. Test full keyboard navigation flow.
```

#### Prompt 17 — Skeleton loading & états vides

```
Add polished loading and empty states across the entire app. Replace all Loader2 spinners with skeleton loading screens that match the actual content layout (card skeletons for student list, chart skeletons for progress page, form skeletons for editors). Add meaningful empty states with illustrations: "No students yet" with an illustration and CTA to invite, "No sessions this week" with a CTA to create one, "No progress data" with an explanation of how to start tracking. Add pull-to-refresh on mobile for all list views. Add optimistic UI updates (show changes immediately, revert on error). Add a subtle shimmer animation to all skeleton loaders.
```

---

### BONUS — Design System

#### Prompt 18 — Design system unifié

```
Create a unified design system with consistent spacing, typography, and component patterns. Define 4 spacing scales only: compact (4px), default (8px), relaxed (16px), spacious (24px). Standardize all card padding to 16px mobile / 20px desktop. Standardize all section gaps to 24px. Create 3 card variants: "flat" (bg only), "elevated" (shadow), "glass" (blur + border). Standardize badge sizes to only 2 variants: small (text-xs px-2 py-0.5) and default (text-sm px-2.5 py-1). Ensure all buttons use the same border-radius (8px). Add a consistent hover state to all cards (translateY(-2px) + shadow increase with 200ms transition). Standardize icon sizes to 16px (inline), 20px (button), 24px (section header).
```

---

## Ordre d'exécution recommandé

| Phase | Prompts | Impact |
|-------|---------|--------|
| **Phase 0 — URGENT** | #0, #N1, #N3 | Fix cards Simple mode + bottom nav fixe + viewport/z-index |
| **Phase 0b — NAV** | #N2, #N4, #N6 | Support pages navigation + breadcrumbs + sticky headers |
| **Phase 0c — CLICK** | #N5, #3 | Touch targets 44px + espacement + feedback visuel |
| **Phase 1** | #1, #2 | Navigation mobile modernisée + responsive 375px |
| **Phase 2** | #4, #5, #7b | Expérience athlète premium + mode toggle |
| **Phase 3** | #6, #7, #8 | Expérience coach + formulaires + animations |
| **Phase 4** | #10, #9 | Acquisition (landing + onboarding) |
| **Phase 5** | #13, #14, #15 | Composants polish |
| **Phase 6** | #16, #17, #18 | Accessibilité & cohérence |
| **Phase 7** | #11, #12 | Navigation avancée |

---

## Référence : Simple vs Advanced mode

| Composant | Simple | Advanced (ajouté) |
|-----------|--------|-------------------|
| EnhancedExerciseCard | Sets/reps/poids, timer linéaire | + Tempo, RPE, comparaison session précédente, timer circulaire |
| WeeklySummaryCard | 2 colonnes (sessions, check-in) | + 4 colonnes + volume total |
| WaterTracker | ml uniquement | + Pourcentage + historique 7 jours |
| StrengthProgressChart | 4 dernières sessions, poids max | + Toutes les sessions + toggle volume |
| DailyNutritionLog | Barre calories seule | + 3 barres macros (P/G/L) |
| StudentProgress | Chart force basique | + Body evolution + photos |
| StudentProfile | Total calories centré | + Donut macros |
| SessionBuilderParams | Groupes musculaires basiques | + Groupes isolés avancés |
| NotificationSettings | Rappels on/off | + Heure précise, intervalles, plages horaires |
| LiveSession | Session épurée | + Timeline progression, substitutions |
| CoachExercises | Description tronquée | + Description complète + badge composé/isolation |
