# MusicVault design spec

Status: locked, v1.1 (November 2026)
Owner: Anjelo Go

This is the source of truth for how MusicVault looks and reads. Build every screen from the tokens and the shared components in `frontend/components/ui/`. If something you need isn't here, open a PR that changes this file first and tag the owner. Don't add one-off colors, fonts, shadows or restyled copies of shared components inside feature code.

The Figma file is a visual reference: https://www.figma.com/design/dzEQijDD31lbZxZibGwBKb (pages "Splash" and "UI Components"). When Figma and this doc disagree, this doc wins.

## 1. What it should feel like

- Inviting, roomy, closer to onboarding than to an admin panel. Big type, generous padding, one main action per area.
- Written like a guide. The interface talks to the person in plain language and tells them what happens next.
- One bold thing per screen. Everything around it stays quiet.
- Real content. Real album art, real song names, real numbers. No lorem ipsum, no fake stats.

Never use: gradients, blur or glassmorphism, glows, drop shadows, all-caps labels, small eyebrow labels above headings, numbered markers (01 / 02) unless the content is an actual sequence, arrows appended to button text, emoji as decoration.

## 2. Color

Only these seven colors exist. Use the Tailwind tokens, never hex values in components.

| Token | Hex | Use |
|---|---|---|
| `olive` | #282F13 | Text, primary buttons, dark surfaces, active nav |
| `blush` | #F6C6CD | Splash background, text on olive, hover fills, tracks |
| `orchid` | #D59ADA | Accent on olive, insight surfaces, avatars, selected slider |
| `green` | #397E20 | Positive state (kept, saved, done), progress fill, button hover |
| `canvas` | #FCE9EC | App page background |
| `paper` | #FFF9F9 | Cards and fields inside the app |
| `red` | #B3261E | Error state only: field border, focus ring and message text. Never fills or decoration |

Text levels on light backgrounds: olive (primary), olive at 70% (secondary), olive at 45% (placeholder and disabled). On olive backgrounds use blush at the same three levels.

Allowed text pairs: olive on blush, canvas, paper or orchid. Blush on olive. Blush on green only for hover states, icons, and text 18px semibold or larger. Never olive on green and never blush on blush. Red on paper and red on canvas are allowed. Red is never used on blush, the contrast fails.

Borders: 1.5px olive at 14% (fields, sidebar), 25% (secondary buttons, unselected chips). Dashed 2px olive at 22% only for "coming soon" or drop areas.

Layer tints, an allowed color at reduced opacity, are fine for the LoadingStack's depth layers.

## 3. Type

One family: Bricolage Grotesque, weights 400, 500, 600. No other fonts.

| Role | Size / line height | Weight | Tracking |
|---|---|---|---|
| Splash display | 80 / 0.98 | 600 | -3.5% |
| Page title (h1) | 44 / 1.05 | 600 | -3% |
| Section title (h2) | 28 / 1.15 | 600 | -1.5% |
| Card title | 22 to 24 / 1.2 | 600 | -1.5% |
| Body large | 18 / 1.5 | 400 | 0 |
| Body | 16 to 17 / 1.5 | 400 | 0 |
| Label, button | 16 to 17 | 500 | 0 |
| Small | 15 / 1.45 | 400 or 500 | 0 |
| Caption | 13 | 400 | 0 |

Headings use `text-wrap: balance`. Running text stays under about 65 characters wide. Nothing in a headline gets a special color, italic or weight on a single word. On phones, page titles drop to 32px.

## 4. Spacing and layout

4px base. Use this scale only: 4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 56, 64, 80, 96, 112, 128.

- Gap between page sections: 28. Grid gap between cards: 24.
- Card padding: 28 (default), 40 (large).
- App shell: 260px sidebar from 860px up, bottom tab bar below that. Main content max width 1120px. Side gutter clamps from 16px (phone) to 56px. The sidebar collapses from 260px to 76px via the edge handle or the `[` key, remembered in a cookie.
- Splash: 64px side padding on desktop, 16px on phones.
- Lay out with flex or grid gaps, not margins between siblings.
- No horizontal scroll at 390px wide, ever.

## 5. Shape

| Thing | Radius |
|---|---|
| Pills (chips, tags, small buttons inside cards) | full |
| Buttons | 10 (sm), 14 (md), 12 (lg) |
| Small artwork (rows, tray) | 12 |
| Rows, fields | 18 to 20 |
| Large artwork | 20 |
| Cards and panels | 28 to 32 |

Depth comes from fill color, not shadows. Cards on canvas use paper. Emphasis cards use olive or orchid.

## 6. Icons

24px grid, 2px stroke, round caps and joins, `currentColor`. Use the set in `components/ui/icons.tsx`. Add new icons to that file in the same style. No icon fonts and no filled icon sets, except the play triangle and the filled heart for "saved".

## 7. Motion

| Change | Duration |
|---|---|
| Hover and color changes | 200ms |
| Focus ring offset | 150ms |
| Press feedback | 150ms |
| Toggles, swaps and reveals | 200 to 250ms |
| Position changes (nav pill, sidebar width, progress fill) | 250ms |

- One easing curve everywhere, cubic-bezier(0.22, 1, 0.36, 1), the "mv" ease: an ease-out feel that never overshoots. No bounce.
- Only for state changes: hover, toggles, saving, a card leaving the swipe deck. No scroll-triggered entrances, no staggered fade-ins, nothing animates on page load.
- Press feedback scales the control down: buttons to 0.98, icon buttons to 0.94, chips to 0.97, all over 150ms. Disabled controls don't hover or press.
- Focus rings: color, width and style appear instantly on focus. Only the offset animates, 0 to 3px (2px on fields), over 150ms.
- Sliding nav pill: one olive pill slides to the active nav item over 250ms, link text color follows over 200ms.
- Sidebar collapse: 260px to 76px over 250ms.
- The error shake is the one allowed oscillation: a single damped horizontal shake, 250ms, fired only when an error appears after mount, never on page load, off under reduced motion.
- Looping indicators (the LoadingStack mark, a button's border trace) aren't transitions, so the 250ms cap doesn't apply to them. Under reduced motion they stop and show a still frame.
- Respect `prefers-reduced-motion`: drop the movement, keep the state change.

## 8. Shared components

Live in `frontend/components/ui/`. Use them as they are. If a variant is missing, add it there in a PR, don't fork the styles in feature code. Preview everything at `/ui`.

| Component | Use it for |
|---|---|
| `Button` | Every action. Primary once per area, secondary and quiet for the rest. Use `loading`, `progress` and `loadingLabel` for in-progress states |
| `IconButton` | Round actions with no label text (play, pass, keep). Always pass `label` |
| `Chip` | Toggleable choices (moods, pass reasons) |
| `Tag` | Static descriptors (genres, "Acoustic") |
| `SearchField` | Any search input |
| `Surface` | Every card or panel |
| `ProgressBar` | Setup progress, round progress, preview playback |
| `LoadingStack` | Unknown waits on a region or page. For buttons, use the `Button` `loading` prop instead: a border trace while the wait is unknown, a border progress ring only when real progress is reported. Never fake a percentage |
| `Avatar` | People |
| `PageHeader` | The top of every app page |
| icons | All iconography |

Feature components (recommendation card, swipe deck, checklist, insights) are built by the dashboard team out of these pieces and live with their feature, not in `components/ui/`.

## 9. Writing

- Sentence case everywhere, including buttons and nav.
- Talk to the person: "your vault", "songs you love".
- Buttons say what happens: "Save to vault", then the confirmation says "Saved". Keep the same verb through a flow.
- Name things the way listeners do: songs, artists, vault, swipe. Not tracks metadata, entities, sync jobs.
- Empty states invite an action ("Your vault is empty" plus "Pick three songs"). Errors say what happened and what to do, without apologizing.
- No exclamation marks in UI copy. No em dashes.
- Numbers: "88K listeners", "2B plays", "1 of 4 done".

## 10. Imagery

- Inside the app, artwork comes from Spotify (album covers). Don't crop covers to anything but a square.
- Stock photography is for the splash page only.
- Every image has real alt text: "Porch Light by Hollis Reed, album cover", not "image".

## 11. Accessibility

- Every interactive element has a visible focus ring: 2px olive, 2 to 3px offset. On olive surfaces use blush.
- Tap targets are at least 44px. The sidebar edge handle is 44px wide and reachable by keyboard.
- Toggles use `aria-pressed`, the current nav item uses `aria-current="page"`, icon-only buttons have an `aria-label`.
- One h1 per page, from `PageHeader`.

## 12. Changing this spec

Open a PR that edits this file, explain why, and tag the owner. CODEOWNERS requires the owner's review for this file, `frontend/components/ui/` and `frontend/app/globals.css`. Bump the version at the top when a change lands.
