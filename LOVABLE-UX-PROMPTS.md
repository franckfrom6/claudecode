# Lift Link Studio - Lovable UX/UI Prompts

> Audit complet et liste de prompts pour améliorer le design, l'UX/UI et le responsive de la plateforme Lift Link Studio (app pour coachs sportifs et athlètes).

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
| **Phase 1** | #1, #2, #3 | Mobile utilisable |
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
