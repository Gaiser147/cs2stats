# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Single-file HTML page published as a claude.ai Artifact. External scripts only from the Artifact CDN allowlist (cdnjs, jsDelivr, unpkg); web fonts from Google Fonts, which the Artifact allows for stylesheets; no runtime fetch to other hosts, so the page cannot call the Leetify API itself. Data is baked into the page at build time from `data/leetify/<SteamID64>/` (fetched by `leetify_analyze.py fetch`).

## Users

Primary: Zattocat (SteamID64 76561198382673172), a CS2 player in Competitive and Premier (Premier rating 7,540 as of 2026-11-10) who wants to find out what to practise to improve. Secondary: friends and teammates the owner shares the page with. Mostly viewed on a phone, in portrait.

## Product Purpose

A personal CS2 debrief built from Leetify match data. It shows which few weaknesses cost the most rounds, grounded in the player's own numbers compared with their own lobbies, and turns them into a short training plan. Success: the player knows the two or three things to work on and can see in later updates whether those numbers moved.

## Positioning

Leetify and similar sites show every stat on dashboards. This debrief picks only the numbers that explain the player's results and compares them with the other nine players in the same matches, not with pros or global averages.

## Operating Context

Read on a phone between sessions or before playing; sometimes shown to friends. Grows over time: after new matches, `python3 leetify_analyze.py fetch` updates the data and the page is rebuilt and republished at the same URL.

## Capabilities and Constraints

- Data per match for all ten players: rating, ADR, K/D/A, accuracy (enemy spotted, head, spray), preaim in degrees, reaction time, counter-strafing, utility thrown, utility value held on death, flashes (enemies/teammates blinded, flash-to-kill), trades (chances, attempts, successes), multi-kills, rounds survived. Profile: Premier, Competitive per map, Leetify sub-ratings (aim, positioning, utility, clutch, opening), CT/T opening duel rates.
- Demos (own parser, `demo_analyze.py`, 5v5 since 2026-10-17): positions of every kill, death, shot and sighting, movement every 0.5 s, crosshair offset split into horizontal and vertical, time to damage, counter-strafing, opening duels per side, KAST. Only these pages show measured positions (death maps); the scenario sketches stay labelled "Skizze".
- Demo aim numbers use a tighter sighting definition than Leetify's preaim and reaction time; they are only compared with the lobby of the same demos.
- Floor plans on map pages come from each map's navigation mesh (walkable polygons with height, via the awpy-data releases, stored as coordinates in `data/maps/geometry/`). No Valve radar images or textures.
- What the page shows is decided by the data at build time: chapters (Fadenkreuz, Granaten, erstes Duell) appear only when the player is clearly behind the lobby and in order of the gap; grenade replays only for the grenade types that lag; the two most relevant maps (often and recently played, lost on) get map pages, every other map appears in an overview.
- Small sample (43 Leetify matches and 18 5v5 demos as of 2026-11-10); claims must be worded as tendencies.
- Leetify attribution required ("Data Provided by Leetify", "View on Leetify" link).
- Shared page shows only the owner's stats and lobby averages, never other players' names or Steam IDs.

## Brand Commitments

German UI copy. No Valve artwork (character models, radar images, textures, logos) is extracted or redistributed; map floor plans are drawn from nav-mesh coordinates only; player figures are original CT/T-style models built for this page. Minimal interface: no top bars or menus, the graphics carry the page.

## Evidence on Hand

`data/leetify/76561198382673172/` (profile.json, history.json, one file per match) and `data/demos/` (per-demo CSVs and positions). Analysis logic in `leetify_analyze.py`, `demo_analyze.py` and `debrief_demos.py`. No screenshots or video of the player.

## Product Principles

- Only numbers that change what the player practises; everything else stays out.
- Compare with the player's own lobbies, not with pros.
- Every visual encodes a measured value; illustrations never imply data that does not exist.
- Each weakness ends in a concrete drill and a target the next update can check.
