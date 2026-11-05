---
name: Zattocat Debrief
description: A personal CS2 debrief drawn in marker on one pivoting coach's whiteboard.
colors:
  room: "#e3e7e8"
  board: "#f2f4f3"
  ink: "#1c1e23"
  ink-2: "#444952"
  marker-blue: "#1f4fbf"
  marker-red: "#d62f2a"
  marker-red-text: "#b5221d"
  magnet-orange: "#e8862a"
  magnet-orange-deep: "#b9661a"
  magnet-graphite: "#3a3d43"
  rule-grey: "#9aa0a6"
  floor: "#d2d7d8"
  aluminium: "#d3d8dc"
  selection: "#f5c48f"
typography:
  display:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "clamp(30px, 7vw, 46px)"
    fontWeight: 400
    lineHeight: 1.1
  headline:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "clamp(22px, 6vw, 30px)"
    fontWeight: 400
    lineHeight: 1.12
  headline-desktop:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "clamp(28px, 2.6vw, 40px)"
    fontWeight: 400
    lineHeight: 1.12
  title:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "23px"
    fontWeight: 400
    lineHeight: 1.15
  annotation:
    fontFamily: "Permanent Marker, Marker Felt, Segoe Print, Bradley Hand, cursive"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1
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
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1
rounded:
  code: "3px"
  focus: "4px"
  flat-page: "6px"
  pill: "999px"
spacing:
  hair: "6px"
  xs: "8px"
  sm: "12px"
  md: "22px"
  lg: "26px"
  xl: "40px"
  xxl: "56px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.board}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    padding: "12px 22px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.pill}"
    padding: "12px 22px"
  caption:
    backgroundColor: "{colors.room}"
    textColor: "{colors.ink-2}"
    typography: "{typography.body}"
    padding: "40px 22px 26px"
  drill:
    textColor: "{colors.ink-2}"
    typography: "{typography.body}"
    padding: "18px 0 0"
  footer-code:
    backgroundColor: "{colors.board}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.code}"
    padding: "2px 6px"
---

# Design System: Zattocat Debrief

## Overview

**Creative North Star: "The Coach's Tactic Board"**

The whole page is one physical object: a double-sided white melamine whiteboard in an aluminium frame on a rolling stand with a marker tray and eraser, lit by bright, cool room light. Scrolling pivots the board around its horizontal axis. Every lesson is drawn on a face in dry-erase marker, explained in a plain caption beside or below it, then the board turns and the next face arrives freshly written, carrying a faint eraser ghost of what was there before. When the board tips flat, its back is a map sketch, and the magnets on it rise into small original CT/T-style figures standing at eye height to scale.

Density is low: one giant marker number per chapter, a handful of strokes, a two-to-four-line caption. Colour is functional, not decorative: black structures, blue dashed means the lobby, red marks the thing to fix. The page refuses the dark stats dashboard of KPI tiles and neon charts; there is no chrome, no top bar, no menu, and the graphics carry the page.

**Key Characteristics:**
- One pivoting whiteboard is the only stage; there are no cards, panels or tiles.
- Marker hand for annotations and big numbers, a sturdy grotesk for anything read as sentences.
- A three-ink code: black for structure, blue dashed for the lobby, red for the one thing to fix.
- Magnets as the player tokens: orange is you, graphite is the opponent, white is a teammate, an outlined ring is "all matches".
- Bright, light room; depth comes from real 3D light and soft shadow, never from UI elevation.

## Colors

A light, cool-grey room with a near-white board, three marker inks, and one warm magnet orange.

### Primary
- **Fix Red** (marker-red): the red marker. Draws the measured quantity the chapter asks the player to fix: the giant chapter number, the player's aim ray and angle arc, the bar to their utility value, the "not here" cross. Also the red marker cap in the tray and the red ray in 3D.
- **Fix Red, Text** (marker-red-text): the darker red for red text at reading and annotation sizes (caption `fix` figures, "du" labels, unmet latest values on the plan), where the stroke red would be too light.

### Secondary
- **Lobby Blue** (marker-blue): the blue marker. Always the lobby comparison: dashed lines, the dashed lobby ray and dashed ring, lobby tallies, lobby labels and caption values, and links.

### Tertiary
- **Magnet Orange** (magnet-orange): the "you" magnet and the base ring of the player's figure. Rendered as a lit radial gradient from a highlight (#ffbe7a) through the orange to the deep tone.
- **Magnet Orange, Deep** (magnet-orange-deep): the magnet's shadow side and the dashed outline of the ghost ring ("all matches").

### Neutral
- **Room Light** (room): page background, 3D scene background and fog, caption scrim.
- **Melamine** (board): the board face every page is drawn on, the primary button's text, footer code chips.
- **Marker Black** (ink): structural strokes (walls, axes, rules, arrows), marker headings, body emphasis, button border and primary fill, focus ring.
- **Faded Ink** (ink-2): Archivo reading text in captions, drills and footer; small sans annotations on the board.
- **Graphite Magnet** (magnet-graphite): opponent magnets and figure bases, the opponent's dashed line on the trade map.
- **Rule Grey** (rule-grey): thin row rules on the title page and the dashed footer divider.
- **Floor** (floor) and **Aluminium** (aluminium): 3D-only materials for the floor plane and the frame, posts, tray and bar.
- **Highlighter** (selection): text selection only.

### Named Rules
**The Three Inks Rule.** Black structures, blue dashed is the lobby, red is the thing to fix. No other marker colours exist on the board, and blue is never used for the player.

**The Rationed Red Rule.** Red marks only the measured value the chapter asks the player to change, and the strokes that draw that value. On the plan page it marks each latest value that has not reached its lobby target. It is never decoration, never a heading colour, never a second highlighted stat in the same caption.

**The Magnet Code Rule.** Orange magnet is you, graphite is the opponent, white with a black outline is a teammate, a dashed deep-orange outline ring is "all matches". The code holds on the canvas, in 3D figure bases, and in counting rows (filled orange for won, graphite for lost; ranks 4 and 5 orange).

## Typography

**Display Font:** Permanent Marker (with Marker Felt, Segoe Print, Bradley Hand, cursive)
**Body Font:** Archivo (variable, wdth 62-125, wght 400-800; with Helvetica Neue, Segoe UI, Arial, sans-serif)

**Character:** The marker is the coach's hand: it writes headings, annotations and the one giant number. Archivo is the explanation underneath: sturdy, neutral, built for full sentences in German.

### Hierarchy
- **Display** (400, clamp(30px, 7vw, 46px), 1.1): the heading of the drill section after the board.
- **Headline** (400, clamp(22px, 6vw, 30px), 1.12; desktop clamp(28px, 2.6vw, 40px)): caption titles, balanced, max 22ch. Viewpoint chapters are lettered "A · Draufsicht", "B · Seitenansicht", "C · Ego-Sicht".
- **Title** (400, 23px, 1.15): drill names.
- **Annotation** (400, 17px, 1): marker labels floating over the 3D scene ("Kopf", "Lobby", "dein Start"); the live degree counter is 30px in Fix Red.
- **Body** (400, 16px, 1.5; desktop captions 17px): captions (max 48ch) and drill text (max 60ch); emphasis is Archivo 700 in ink, lobby values Archivo 600 in Lobby Blue, fix values Archivo 700 in Fix Red Text.
- **Label** (400, 14px, tabular numerals): drill progress lines and footer.
- **Board number** (canvas only, marker): the chapter's one giant number, 110-120px on the landscape board, 52-74px on the portrait board, in Fix Red. Board sans annotations run 11-19px in Faded Ink.

### Named Rules
**The Two Hands Rule.** If it is read as a sentence, it is Archivo. If it is written on or over the board, a heading, or a number to remember, it is Permanent Marker. Marker headings are always weight 400.

**The One Big Number Rule.** Each board page carries exactly one giant marker number, the chapter's measured value.

## Layout

The page is a fixed full-viewport WebGL canvas behind a scroll track. Scroll position maps to a board state: one state per 1.1 viewport heights, ten states (title, three views of the aim map, utility, utility per match, two views of the trade map, damage, plan), with a short overscroll tail. After the track, an ordinary reading section holds the drills and footer, max width 760px, sliding over the scene with a room-coloured top fade.

**Orientation.** Landscape is `width > 1.05 × height` (CSS `min-aspect-ratio: 21/20`, the same threshold in script). Phones get a portrait board (1.0 × 1.45 m, drawn on a 360-unit canvas, 1400px texture); desktop gets a landscape board (1.8 × 1.2 m, 840-unit canvas, 2048px texture). Pages are composed separately for each orientation, not scaled.

**Fit boxes.** Every camera pose is solved by binary search so the board (or the figures) fits a normalised screen box. Phone face and top views: x 0.035-0.965, y 0.035-0.66, leaving the lower third to the caption. Desktop face and top: x 0.04-0.60, y 0.06-0.94, leaving the right side to the caption, and the stand's feet are kept in frame. Side views: phone x 0.06-0.94, y 0.12-0.64; desktop x 0.10-0.60, y 0.12-0.88. First person: field of view 68° phone, 58° desktop, offset to the same free area.

**Captions.** Phone: pinned to the bottom, full width, padding 40px top and 22px sides (safe-area aware), on a room-coloured gradient scrim. Desktop: a right-hand column, width min(38vw, 460px), vertically centred, 48px right padding, scrim fading leftward from 78%.

**Spacing rhythm.** 8px caption gap (12px on desktop), 22px side gutters, 26px between drills, 40px and 56px for section padding.

## Elevation & Depth

Depth is physical, not interface. The scene has a hemisphere light (white over #c4c9ca, 1.65) and one soft directional key light from upper left (1.15, PCF soft shadows, radius 5). The board, frame, stand, tray, markers, eraser, walls and figures cast real shadows on the floor and on the board when it lies flat; the board stops casting while it lies flat. Fog in the room colour starts 1.6 m behind the camera target, so the background dissolves into the page colour.

The board faces glow slightly (emissive 0.5) only where the melamine is bare, so marker ink keeps its full colour under the light.

### Shadow Vocabulary
- **Magnet drop** (canvas, rgba(28,30,35,.28) disc offset 0.6 / 1.8px): under every drawn magnet.
- **Flat page** (`box-shadow: 0 6px 18px rgba(28,30,35,.18)`): the board images in the no-WebGL fallback.
- **Reading lip** (`box-shadow: 0 -18px 30px` room colour): the drill section fading over the scene.

### Named Rules
**The Room Is The Elevation Rule.** No HTML element floats on a card or shadow. Captions sit on a scrim in the room colour; anything that needs depth is a 3D object lit by the room.

## Shapes

Circles and pills: magnets, figure bases and buttons are round (pill radius on buttons). Marker strokes are round-capped and round-jointed, with a seeded wobble (about 1.3 units over 24-unit segments) so lines look hand-drawn but render identically on every load. Walls and wall outlines are drawn with sharp corners. The view letter sits in a hand-drawn hexagon. Small radii only for code chips (3px), the focus ring (4px) and the fallback page images (6px).

## Components

### Buttons
Start buttons, ink on room, round and plain.
- **Shape:** full pill (999px), 2px ink border.
- **Primary** ("Debrief starten"): ink fill, Melamine text, Archivo 700 16px, 12px × 22px.
- **Ghost** ("Zum Plan"): transparent with ink border and ink text.
- **Hover / Focus:** lift 2px over 0.2s on the house ease, back to rest on press; focus is a 2px ink outline offset 3px. No transition under reduced motion.
- **Behaviour:** they sit under the board on phones (centred, with the one-line intro above) and in the caption column on desktop (15vh from the bottom). They fade out over the first 8% of a state's scroll and stop receiving pointer events and screen-reader attention at half opacity. "Debrief starten" scrolls to state 1, "Zum Plan" to the plan state.

### Captions
One per board state (none on the title state): a marker headline and one Archivo paragraph whose numbers use the ink code (bold ink, Lobby Blue 600, Fix Red Text 700). A caption fades in and rises 10px over 6% of a state's scroll and fades out the same way, so only one is visible at a time.

### Drills
After the board: a heavy 2.5px ink rule on top, marker title, Archivo instructions, and a tabular 14px progress line ("Alle Matches … · letzte 5: … · Ziel (Lobby) … · geschafft"). The footer is separated by a 1.5px dashed Rule Grey line and carries the Leetify attribution.

### The Board (signature)
The pivoting double-sided board. Each state sets an angle, a face and a page:

| State | Angle | Face | Page | Camera |
|---|---|---|---|---|
| 0 | 0 | front | title | face |
| 1 | π/2 | back | aim map | top |
| 2 | π/2 | back | aim map | side |
| 3 | π/2 | back | aim map | first person |
| 4 | 0 | front | utility on death and flashes | face |
| 5 | π | back | utility per match | face |
| 6 | 3π/2 | front | trade map | top |
| 7 | 3π/2 | front | trade map | side |
| 8 | π | back | damage cost | face |
| 9 | 2π | front | plan | face |

The face that is not visible is repainted with the next page it will show, so every turn arrives freshly written. Leaving a side or first-person view for a face view routes the camera through the top view.

### Board marker conventions
- Solid black: walls, axes, rules, the true line to the enemy, arrows, the done tick.
- Solid red, heavier (4-5 units): the player's value as a stroke (aim ray, utility bar), with a 13% red fan for an angle.
- Dashed blue (7/6 dash, 3 units): the lobby value; tallies and labels for the lobby in blue.
- Tally marks in groups of five for counts.
- Magnet sizes: 11 units on maps, 7.5-13 in rows; legends pair magnet, ghost ring and dashed blue tick ("letzte 5", "alle", "Lobby = Ziel").
- Every map page states in sans on the board that it is a sketch and positions are not measured.

### Figures
Original low-poly CT/T-style figures built from primitives: T in sand and brown (cloth #b08a58), CT in slate (cloth #4a586e) with a helmet, eye height 1.63 m, on a magnet base ringed in the Magnet Code colour. In 3D the rays repeat the ink code: red tube for your aim, thin black tube to the enemy, dashed blue tube for the lobby, and a dashed black head-height line on the wall.

### Motion grammar
- **House ease:** cubic-bezier(.16, 1, .3, 1) for HTML transitions; smoothstep for everything in the scene.
- **Intro ease-in:** on load the camera starts 55% further out and slightly offset and eases in over 2.2s; the title then writes on after 0.7s.
- **Scroll damping:** progress follows scroll by 12% per frame. Within each state the first 30% holds still and the change happens over the next 60%.
- **Board pivot:** the board rotates about its horizontal axis between state angles, always continuing in one direction (0 → 2π over the page).
- **Figures rising:** walls grow from 2% to full height and figures scale up from the magnets over half a state as the board tips flat.
- **First-person flick:** the view turns from the player's average aim error onto the enemy's head over 0.3 state, the red degree counter running down to zero, with a red crosshair, a dashed blue lobby ring and a red "dein Start" cross.
- **Marker reveal sweep:** a freshly written face reveals its ink in a diagonal sweep from top-left over 1.1s, triggered when the face turns towards the camera.
- **Eraser ghosting:** the previous page stays under the new one at 1.6% opacity with a 6px blur.

### Fallbacks
- **Reduced motion:** scroll snaps to whole states, no damping, no intro, no reveal sweep, captions switch instead of fading, buttons jump instead of smooth-scrolling. Every fact stays.
- **No WebGL** (or three.js missing): the scene, track and overlay are hidden and every page is painted once onto a flat canvas with magnets, shown as a column of figures (max 760px) with the captions of every state that uses that page underneath.

## Do's and Don'ts

### Do:
- **Do** draw every lesson on the one board; a new idea is a new page and a turn, not a new panel.
- **Do** keep the ink code: black structure, blue dashed lobby, red only for the value to fix.
- **Do** use the magnet code: orange you, graphite opponent, white teammate, dashed outline ring for all matches.
- **Do** set one giant marker number per page and explain it in an Archivo caption.
- **Do** label every map scene on the board as a sketch whose positions are not measured.
- **Do** compose separate portrait and landscape pages and fit the camera to the free screen box rather than scaling one layout.
- **Do** keep reduced-motion and no-WebGL paths showing the same facts as the animated page.

### Don't:
- **Don't** build a dark dashboard of KPI tiles and neon charts.
- **Don't** add top bars, menus or other interface chrome.
- **Don't** use Valve game assets (character models, maps, logos); figures and map sketches are original.
- **Don't** imply measured positions: no death spots or standing positions presented as data.
- **Don't** use red for a heading, decoration or a second emphasis in the same caption.
- **Don't** set reading sentences in Permanent Marker.
- **Don't** put HTML content on cards or shadows; depth belongs to the lit 3D room.
