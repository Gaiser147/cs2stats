---
name: Zattocat Debrief
description: A personal CS2 debrief drawn in marker on one pivoting coach's whiteboard, paged one gesture at a time.
colors:
  room: "#e3e7e8"
  board: "#f2f4f3"
  ink: "#1c1e23"
  ink-2: "#444952"
  marker-blue: "#1f4fbf"
  marker-red: "#d62f2a"
  marker-red-text: "#b5221d"
  rule-grey: "#9aa0a6"
  grab-grey: "#a4aab0"
  magnet-orange: "#e8862a"
  magnet-graphite: "#3a3d43"
  magnet-tan: "#b08a58"
  board-core: "#e9ecec"
  aluminium: "#d3d8dc"
  stand-dark: "#2a2c30"
  floor: "#d2d7d8"
  wall-white: "#f6f7f7"
  flash-white: "#ffffff"
  selection: "#f5c48f"
typography:
  display:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "clamp(54px, 16vw, 110px)"
    fontWeight: 400
    lineHeight: 1
  headline:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "clamp(30px, 7vw, 46px)"
    fontWeight: 400
    lineHeight: 1.1
  title:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "clamp(22px, 6vw, 30px)"
    fontWeight: 400
    lineHeight: 1.12
  title-desktop:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "clamp(28px, 2.6vw, 40px)"
    fontWeight: 400
    lineHeight: 1.12
  drill-title:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "23px"
    fontWeight: 400
    lineHeight: 1.15
  annotation:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1
  hint:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "19px"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Archivo, Helvetica Neue, Segoe UI, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  body-desktop:
    fontFamily: "Archivo, Helvetica Neue, Segoe UI, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Archivo, Helvetica Neue, Segoe UI, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "tnum"
  button:
    fontFamily: "Archivo, Helvetica Neue, Segoe UI, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    lineHeight: 1.5
rounded:
  hairline: "3px"
  focus: "4px"
  figure: "6px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "8px"
  md: "12px"
  gutter: "22px"
  section: "26px"
  cap-top: "34px"
  lg: "48px"
components:
  caption:
    backgroundColor: "{colors.room}"
    textColor: "{colors.ink-2}"
    typography: "{typography.body}"
    padding: "34px 22px 26px"
  caption-title:
    textColor: "{colors.ink}"
    typography: "{typography.title}"
  caption-desktop:
    backgroundColor: "{colors.room}"
    typography: "{typography.body-desktop}"
    padding: "40px 48px 40px 28px"
    width: "min(38vw, 460px)"
  swipe-hint:
    textColor: "{colors.ink}"
    typography: "{typography.hint}"
    padding: "0 22px"
  drills-sheet:
    backgroundColor: "{colors.room}"
    textColor: "{colors.ink-2}"
    padding: "34px 22px 48px"
    width: "760px"
  drill:
    textColor: "{colors.ink-2}"
    typography: "{typography.body}"
    padding: "18px 0 0"
  sheet-back:
    textColor: "{colors.ink-2}"
    typography: "{typography.button}"
    padding: "4px 0"
  skip-button:
    backgroundColor: "{colors.board}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    padding: "10px 16px"
  flash-overlay:
    backgroundColor: "{colors.flash-white}"
    textColor: "{colors.ink}"
    typography: "{typography.display}"
    padding: "24px"
  board-label:
    textColor: "{colors.ink}"
    typography: "{typography.annotation}"
  board-label-lobby:
    textColor: "{colors.marker-blue}"
    typography: "{typography.annotation}"
  board-label-fix:
    textColor: "{colors.marker-red-text}"
    typography: "{typography.annotation}"
  footer-code:
    backgroundColor: "{colors.board}"
    rounded: "{rounded.hairline}"
    padding: "2px 6px"
---

# Design System: Zattocat Debrief

## Overview

**Creative North Star: "The Coach's Tactic Board"**

The whole page is one physical object: a double-sided white melamine whiteboard in an aluminium frame on a rolling stand with a marker tray, lit by bright, even room light in a pale grey room. There is no scrolling document and no chrome. Each gesture turns the board to its next page, the new face is written stroke by stroke in dry-erase marker, magnets land, walls and original CT/T figures rise, and only then does the caption appear. Lessons are drawn, explained and wiped; faint eraser ghosting of the previous page stays on the surface.

Three marker inks carry all meaning: black for structure, blue dashed for the lobby, red for the player's own number that has to move. Two voices write on it: a marker hand (Permanent Marker) for everything written on the board, captions and the one giant number per chapter, and a sturdy grotesk (Archivo) for reading text and small print. Density is low: one lesson, one number, one sketch per page.

The system rejects the dark stats dashboard of KPI tiles and neon charts. Every mark encodes a measured value of the owner against their own lobbies; illustrations never pretend to be data, so every map is labelled a sketch.

**Key Characteristics:**
- One pivoting whiteboard, paged one gesture at a time; the page itself never scrolls.
- A fixed transition sequence: turn or camera move, marker writing, magnets and figures, caption last.
- Three-ink grammar: black structure, blue dashed lobby, red for the player's value to fix.
- Data marks are marker marks (tallies, hatched boxes, checks and crosses, rings, arrows), never painted dots.
- Portrait board on phones, landscape board on desktop; caption below or beside.
- Same facts survive without motion and without WebGL.

## Colors

A cool, near-neutral room and board with three dry-erase inks and three magnet colours; colour is meaning, never decoration.

### Primary
- **Fix Red** (marker-red): the red marker. The giant chapter number, the player's aim ray, the cross for "last 5" when the target is missed, lost duels on the T side, the arrow pointer on the utility ruler, the flee path in the molotov scene, the rank-4 and rank-5 hatched boxes.
- **Fix Red Text** (marker-red-text): the same red darkened for legible text: "du" labels, values below the lobby, and `.fix` emphasis in captions.

### Secondary
- **Lobby Blue** (marker-blue): the lobby, always. Dashed lines and ticks for lobby values, lobby numbers in the hand, `.lobby` spans in captions, links in the drills footer.

### Tertiary (magnets and 3D materials)
- **Magnet Orange** (magnet-orange): the magnet base under the player's own figure. The only orange in the system.
- **Magnet Graphite** (magnet-graphite): the CT opponent's magnet; also the dark-grey dashed sightlines and the CT's door line drawn on the board.
- **Magnet Tan** (magnet-tan): a teammate's magnet (the entry in the duel drill), the T-cloth colour.
- **Board Core** (board-core), **Aluminium** (aluminium), **Stand Dark** (stand-dark), **Floor** (floor), **Wall White** (wall-white): the 3D world. Melamine core, frame and posts, knobs, wheels and grenade metal, the floor under the stand, and the white blocks that rise as walls (outlined with ink tubes).

### Neutral
- **Room Light** (room): page and scene background, fog colour, caption and sheet backgrounds.
- **Board White** (board): the drawing surface of both faces; also the fill of skip buttons and inline code.
- **Marker Black** (ink): structure strokes, walls, headings and body emphasis, focus ring.
- **Faded Ink** (ink-2): caption and drill body text, small Archivo print on the board.
- **Rule Grey** (rule-grey): thin ruled lines under table rows on the board and the dashed footer divider.
- **Grab Grey** (grab-grey): the drills-sheet grab handle.
- **Flash White** (flash-white): the full-screen flash white-out only.
- **Highlighter** (selection): text selection only.

The canvas palette `C` mirrors the CSS custom properties exactly: `ink`, `ink2`, `blue`, `red`, `redT`, `board`, `rule`.

### Named Rules
**The Three Inks Rule.** Black is structure, blue dashed is the lobby, red is the player's own value that has to move. A colour never changes meaning between pages.

**The Lobby Is Blue Rule.** Every lobby value, on the board or in a caption, is Lobby Blue; every comparison is the player against their own lobbies, never pros or global averages.

**The Orange Is You Rule.** Orange appears only as the magnet under the player's figure. Graphite marks the CT opponent, tan a teammate.

## Typography

**Display Font:** Permanent Marker (with Marker Felt, Segoe Print, Bradley Hand, cursive)
**Body Font:** Archivo, variable width and weight 400–800 (with Helvetica Neue, Segoe UI, Arial, sans-serif)

**Character:** The marker hand is the coach writing on the board: headings, annotations, the giant number and every label in the scene. Archivo is the steady reading voice for sentences, small print and controls. The two never swap roles.

### Hierarchy
- **Display** (400, clamp(54px, 16vw, 110px), 1): the "Flash!" white-out only.
- **Headline** (400, clamp(30px, 7vw, 46px), 1.1): the drills-sheet heading.
- **Title** (400, clamp(22px, 6vw, 30px), 1.12; desktop clamp(28px, 2.6vw, 40px)): the caption heading per state, max 22ch, balanced.
- **Drill title** (400, 23px, 1.15): each drill on the sheet.
- **Hint** (400, 19px): the swipe hint text, max 24ch.
- **Annotation** (400, 17px, 1; count 30px in red): the DOM labels in the first-person view ("Kopf", "Lobby", "dein Start", the shrinking degree count).
- **Body** (400, 16px, 1.5; 17px beside the board on desktop): caption and drill text, max 48ch in captions and 60ch on the sheet; `b` at 700.
- **Label** (400, 14px, tabular figures): drill status lines, the "tap again" line, footer.
- **Button** (600, 15px): the back link and the keyboard skip buttons.

### Board type ramp (canvas, in board units; landscape / portrait)
- Giant chapter number: hand 110–120 / 46–74, Fix Red.
- Board title: hand 84 / 60 (name), 52 / 34 (Debrief, blue).
- Page heading: hand 40–64 / 24–40.
- Row labels and values: hand 20–44 / 15–36.
- Small print and axis ticks: Archivo 15–19 / 10.5–13.5, Faded Ink; "Skizze" notes Archivo 600.

### Named Rules
**The Two Voices Rule.** Marker hand for what is written on the board and its headings; Archivo for anything read as a sentence. No third family.

**The One Giant Number Rule.** Each data chapter carries exactly one giant marker number, the player's value, in Fix Red.

## Layout

The page is a fixed full-viewport WebGL scene (`overflow: hidden`, `touch-action: none`) with a pointer-transparent overlay for captions, labels and the hint. There is no document flow except the drills sheet and the no-WebGL fallback.

**Paged navigation.** One wheel gesture, swipe or key moves exactly one page. Wheel deltas accumulate past a 40 threshold; after a step the wheel locks until a 220 ms quiet gap, and wheel input during a transition is ignored. Touch (vertical swipe over 40px that beats the horizontal component) and keys (ArrowDown, PageDown, Space, Enter forward; ArrowUp, PageUp back) queue one pending step that fires 60 ms after the transition ends. A tap under 10px or a click on a grenade page replays its effect; a click on the title page advances. After the last state the drills sheet slides up; scrolling up at its top, swiping down over 60px, Escape or the back link close it.

**Board format.**
- Phone, portrait (width not more than 1.05× height): board 1.0 × 1.45 m, canvas 360 logical px wide, texture 1400px.
- Desktop, landscape (width over 1.05× height; CSS `min-aspect-ratio: 21/20`): board 1.8 × 1.2 m, canvas 840 logical px, texture 2048px.

**Fit boxes.** Each camera pose is binary-searched so the board corners (and on desktop face views the stand feet) land inside a viewport box given as [left, right, top, bottom] fractions:
- Face and top views: desktop [.04, .6, .06, .94], phone [.035, .965, .035, .66].
- Side views: desktop [.06, .6, .06, .94] including the whole board; phone [.06, .94, .1, .54] (preaim) and [.06, .94, .1, .56] (duel), a close three-quarter view.
- Grenade view: desktop [.06, .6, .06, .94], phone [.04, .96, .06, .66].
- First-person view: fov 68 on phone, offset upward; fov 58 on desktop, offset left.

**Captions.** On phone the caption sits below the board, bottom-anchored with 34px top / 22px side / 26px bottom padding (safe-area aware) over a gradient that fades the room colour in. On desktop it is a column on the right, min(38vw, 460px) wide, vertically centred, padded 40px 48px 40px 28px, over a leftward gradient (room colour from 80%). The swipe hint takes the same slot.

**Map writing at the near edge.** On phone, all writing on map pages (giant number, legend, "Skizze" note) sits along the board's near edge (bottom of the portrait board) so the close side cameras never show it; the view tag lives in the top corner as a lone ringed letter. On desktop map writing sits in the left third, map art offset right (`fx` 0.25–0.28).

**Spacing rhythm.** 6 / 8 / 12px inner gaps, 22px gutters, 26px between drills, 34px caption top, 48px sheet bottom. The sheet column caps at 760px.

## Elevation & Depth

Depth is real 3D, not CSS layering. A hemisphere light (white over #c4c9ca, 1.65) and one directional sun (1.15, from above-left-front) cast PCF soft shadows (1024px map, radius 5, bias −0.0005, normalBias 0.015). Room-coloured fog follows the camera (near = distance + 1.6, far = distance + 9). The board faces use an emissive shader that holds bare melamine at Board White under any angle while ink stays dark.

Shadows switch with posture: while the board stands upright, the core and frame cast shadows and the faces do not receive them; once the board lies flat (|cos θ| < 0.5) the frame stops casting and the faces receive the shadows of walls, figures and magnets.

### Shadow Vocabulary
- **Drills sheet lift** (`box-shadow: 0 -10px 30px rgba(28, 30, 35, .18)`): the sheet sliding over the board.
- **Flat page** (`box-shadow: 0 6px 18px rgba(28, 30, 35, .18)`): board images in the no-WebGL fallback.
- **Caption fade** (room-colour gradient): captions sit on a gradient of the room colour, never a card.

### Named Rules
**The Lying Flat Rule.** Faces receive shadows only while lying flat; upright, the board is lit evenly so marker writing never carries a shadow band.

## Shapes

The board is a crisp rectangle with a 30mm aluminium rail; walls are white blocks with ink-tube outlines; magnets are round discs. Everything drawn is a marker stroke: seeded wobble along the path (about 1.3px amplitude, one jitter point per 24px), round caps and joins, 2.2–5px widths. Interface radii are minimal: 3px for code and the grab handle, 4px for the focus ring, 6px for fallback images, full pill only for skip buttons. Rules on the sheet are 2.5px solid ink above each drill and a 1.5px dashed rule-grey line above the footer.

## Components

### Board page (signature)
Each state draws a page recorded as marker operations: strokes (`s`), dashed lines (`d`), text (`t`) and fills (`f`). The recording replays as drawing.
- **Strokes** unroll along their length (L/650 s, 0.05–0.4 s each); dashed lines extend; text reveals left to right with a clip wipe (0.03 s per character, 0.08–0.4 s); fills fade. Each op starts at 45% of the previous one's duration, so writing overlaps like a hand. A page takes 1–2.1 s.
- **Ghosting:** the previous page on a face remains at 1.6% opacity, blurred 6px, plus 16 faint eraser smears seeded per page.
- **View tags:** a ringed hand letter (A, B, C) with an Archivo 600 name below; on phone only the ringed letter.

### Marker mark vocabulary
- **Tallies:** groups of four strokes and a diagonal fifth for counts (flashes: player in ink, one lobby player in blue).
- **Hatched boxes:** one box per match in the rank histogram ("1 Kästchen = 1 Match"); ranks 4 and 5 in red.
- **Checks and crosses:** opening duels rounded to ten; checks in ink for won, crosses for lost (red on T side, faded ink on CT).
- **Plan tracks:** an arrow pointing to "besser", a blue dashed tick for the lobby target, a ring for all matches, a cross for the last 5 (red when the target is missed), and a check beside a reached target.
- **Ruler pointer:** a red marker arrow points down at the player's value on the utility ruler; a blue dashed tick marks the lobby.
- **Ranges:** angle fan in 13% red fill with a red arc; a bracket over dry matches.
- **Magnets:** 3D discs remain only under figures: orange for you, graphite for the CT opponent, tan for a teammate. In the flat fallback the figure positions are drawn as marker rings instead.

### Grenade pages
On the flat board, the player's T throws along an arc; each effect has its own caption with the data.
- **Flash:** a burst sprite, then a full-screen white-out with "Flash!" in display hand and the instruction in Archivo, holding about 2.7 s.
- **HE:** a short hard flash (0.08 s up, 0.22 s down), a pale pressure ring and rising soot; the CT shakes.
- **Molotov:** a carpet of flickering flame tongues, a scorch mark and a red dashed flee path along which the CT runs out.
- **Smoke:** a cloud that grows over 1.5 s while the graphite CT sightline to the door fades out.
- A tap or click replays the effect; the caption says how ("Tippe" on touch, "Klicke" otherwise).

### Caption
- **Style:** hand title over Archivo body, no container; room-colour gradient behind.
- **Emphasis:** `b` in ink 700; `.fix` in Fix Red Text 700; `.lobby` in Lobby Blue 600.
- **Behaviour:** fades out in 0.25 s when a transition starts and fades in last, over 0.4 s, after the writing and magnets. Announced politely to screen readers.

### Swipe hint
A hand-drawn marker arrow (4.6px stroke) above hint text, replacing any start button. On touch it points up with "Wischen, um die Tafel zu drehen"; on fine pointers it points down with "Scrollen oder Pfeiltaste, um die Tafel zu drehen". Appears 2 s after load on the title only, nudges 12px every 1.8 s, and is clickable to advance.

### Drills sheet
Room-coloured sheet over the board with a grab handle, an underlined Archivo 600 back link, a hand headline, four drills separated by 2.5px ink rules, each with hand title, Archivo text and a tabular status line ("geschafft" in ink 700), then a dashed-rule footer with data stand, the Leetify attribution and link, and the rebuild commands in inline code.

### Navigation
No visible navigation. Keyboard users get two skip buttons (previous/next page), off-screen until focused, then a 2px ink pill on board white. Focus everywhere is a 2px ink outline, offset 3px, radius 4px.

### State table
| # | Angle θ | Face | Page | Camera | Adds |
|---|---|---|---|---|---|
| 0 | 0 | front | title | face | intro ease-in, title written |
| 1 | π/2 | back | map1 (preaim) | top | magnets |
| 2 | π/2 | back | map1 | side | wall, figures, 3D aim/lobby rays |
| 3 | π/2 | back | map1 | ego | crosshair flick, own figure hidden |
| 4 | π | back | aimH (crosshair height vs. side, demos) | face | figure to scale, offset boxes |
| 5 | 2π | front | gut (mechanics vs. lobby, demos) | face | |
| 6 | 3π | back | util1 (utility on death, flashes) | face | |
| 7 | 4π | front | util2 (grenades per match) | face | |
| 8–11 | 7π/2 | front | utilmap | util | flash, HE, molotov, smoke |
| 12 | 9π/2 | back | deaths0 (most-played map) | top | measured deaths, opening deaths, kills |
| 13 | 11π/2 | front | deaths1 (second map) | top | |
| 14 | 13π/2 | back | map2 (opening duel) | top | magnets |
| 15 | 13π/2 | back | map2 | side | walls, you, entry, CT |
| 16 | 6π | front | erg (ADR, rank, KAST) | face | |
| 17 | 7π | back | plan (four tracks to targets) | face | |
| then | | | drills sheet | | slides up |

Angles are derived, not listed: each page names its face and whether the board lies flat, and the pivot takes the nearest matching angle (forward on a tie). Without demo data the demo pages drop out and the sequence falls back to the original 14 states. Transitions between a flat and an upright page that are not the top view route the camera through that map's top view, with the rotation in the matching half.

### Motion grammar
- Board turn 1.35 s; same-page camera move 0.45 s; other camera moves 1.05 s; in-out cubic.
- Writing starts at 70% of a turn or 25% of a camera move and runs 1–2.1 s.
- Magnets, walls and figures rise over 0.9 s (out cubic) after the writing; leaving, they collapse in 0.4 s.
- Caption fades in last (0.4 s).
- Intro: camera eases in over 2.2 s while the title writes from 0.6 s.
- First-person flick: from 0.4 s, 1.3 s, crosshair travels the preaim angle onto the head while the red count runs to 0,0°.
- Drills sheet 0.7 s on cubic-bezier(.16, 1, .3, 1).

### Fallbacks
- **Reduced motion:** no turns, camera moves, writing, intro, flick, hint nudge, white-out or sheet slide; pages, magnets and figures appear complete, and grenade pages show their end state.
- **No WebGL (or no three.js):** the page becomes a normal scrolling document of flat board canvases (one per page, drawn complete, positions as rings), each followed by its captions, then the drills sheet inline.

## Do's and Don'ts

### Do:
- **Do** move exactly one page per gesture, and keep the order: turn or camera move, marker writing, magnets and figures, caption last.
- **Do** encode every value as a marker mark (stroke, dashed line, tally, hatched box, check, cross, ring, arrow) in the three inks.
- **Do** write "Skizze" on every scenario page; those positions are illustrative and not measured.
- **Do** keep death maps measured: red marker crosses for deaths, a red ring around a cross for a lost opening duel, small ink rings for kills, a light floor fill with an ink-2 outline traced from player movement, callout names in bold sans with a board-coloured halo. No radar images.
- **Do** keep all map writing at the board's near edge on phone so side cameras stay clean.
- **Do** compare only the owner's stats with lobby averages, and keep "Data Provided by Leetify" with the "View on Leetify" link.
- **Do** give every effect page its own caption with the data, and let a tap or click replay it.
- **Do** keep the same facts reachable with reduced motion and without WebGL.

### Don't:
- **Don't** turn the debrief into a dark stats dashboard of KPI tiles and neon charts.
- **Don't** use painted dots as data marks on the board; 3D magnets belong under figures only.
- **Don't** use red for lobby values or blue for the player; colours never change meaning.
- **Don't** show other players' names or Steam IDs.
- **Don't** use or redistribute Valve assets (character models, maps, logos); figures are original CT/T-style models and maps are labelled sketches.
- **Don't** add top bars, menus or start buttons; the board and the swipe hint carry the page.
