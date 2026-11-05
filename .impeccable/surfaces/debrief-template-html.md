---
version: 1
slug: "debrief-template-html"
primary_target: "debrief/template.html"
related_targets: []
---

# Surface brief: CS2 debrief (debrief/template.html)

Scope: single-page scroll debrief, published as a claude.ai Artifact, rebuilt from repo data after each `leetify_analyze.py fetch`. Mode: experience.
Audience: Zattocat first, friends/teammates second; phone portrait first.
Job: see the few weaknesses that cost rounds, compared with own lobbies, and leave with drills and targets; on later updates, see whether those numbers moved.
Content: Preaim (hero), damage/survival, utility on death + flashes, T-side openings + trade success, maps/modes in brief, training plan with progress vs targets. German copy. Leetify attribution.
Constraints: no other players' names; no claims about positions or death spots (no round data); small-sample wording; must run smoothly on phones; reduced-motion fallback renders the same facts statically.

## Direction contract

THESIS: The debrief is the coach's tactic board: one whiteboard where each lesson is drawn in marker, explained, then wiped for the next. It refuses the dark stats dashboard of KPI tiles and neon charts.

OWN-WORLD: White melamine board under bright room light with faint eraser ghosting, an aluminium frame rail with a marker tray, dry-erase strokes in black (structure), blue dashed (lobby) and red solid (the one thing to fix per chapter, rationed), round magnets: orange for you, graphite for opponents. Marker hand for annotations and one giant number per chapter; a sturdy grotesk for reading text. Views lettered A Draufsicht, B Seitenansicht, C Ego-Sicht.

STORY: The visitor sees their preaim drawn as an angle, watches it become a 3D duel, then gets damage, utility and duel lessons the same way, believes them because every line is their own number against their own lobbies, and leaves with four drills and targets.

FIRST VIEWPORT: Phone 390x844, no chrome. A real double-sided whiteboard on a rolling stand with a marker tray; on load the camera eases in until the board fills the width and the title is written on it stroke by stroke in marker (name, match count, Premier, winrate). Below the board a hand-drawn arrow with "Wischen, um die Tafel zu drehen" (pointing down with "Scrollen oder Pfeiltaste" on desktop); no buttons.

FORM: Tactic board, candidate 4 of 7, assigned by roll; user-pinned refinement: the page is one physical pivoting whiteboard paged one gesture at a time. Signature interaction: each swipe, scroll gesture or key turns the board to the next page and plays a fixed sequence (turn, marker drawing stroke by stroke, magnets landing and walls and original CT/T figures rising, caption last); the preaim map goes top, three-quarter side, first person with the crosshair flick; grenade pages animate flash (white-out with the instruction), HE, molotov and smoke on the flat board. seed:6b2f7829c7029bfa

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
