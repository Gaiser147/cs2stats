# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Single-file HTML page published as a claude.ai Artifact. External scripts only from the Artifact CDN allowlist (cdnjs, jsDelivr, unpkg); no runtime fetch to other hosts, so the page cannot call the Leetify API itself. Data is baked into the page at build time from `data/leetify/<SteamID64>/` (fetched by `leetify_analyze.py fetch`).

## Users

Primary: Zattocat (SteamID64 76561198382673172), a CS2 player in Competitive and Premier (Premier rating 8,274 as of 2026-11-04) who wants to find out what to practise to improve. Secondary: friends and teammates the owner shares the page with. Mostly viewed on a phone, in portrait.

## Product Purpose

A personal CS2 debrief built from Leetify match data. It shows which few weaknesses cost the most rounds, grounded in the player's own numbers compared with their own lobbies, and turns them into a short training plan. Success: the player knows the two or three things to work on and can see in later updates whether those numbers moved.

## Positioning

Leetify and similar sites show every stat on dashboards. This debrief picks only the numbers that explain the player's results and compares them with the other nine players in the same matches, not with pros or global averages.

## Operating Context

Read on a phone between sessions or before playing; sometimes shown to friends. Grows over time: after new matches, `python3 leetify_analyze.py fetch` updates the data and the page is rebuilt and republished at the same URL.

## Capabilities and Constraints

- Data per match for all ten players: rating, ADR, K/D/A, accuracy (enemy spotted, head, spray), preaim in degrees, reaction time, counter-strafing, utility thrown, utility value held on death, flashes (enemies/teammates blinded, flash-to-kill), trades (chances, attempts, successes), multi-kills, rounds survived. Profile: Premier, Competitive per map, Leetify sub-ratings (aim, positioning, utility, clutch, opening), CT/T opening duel rates.
- No round-by-round data, no positions, no demos: the page must not show where a player stood or died as if it were measured.
- Small sample (17 matches as of 2026-11-04, several cut short); claims must be worded as tendencies.
- Leetify attribution required ("Data Provided by Leetify", "View on Leetify" link).
- Shared page shows only the owner's stats and lobby averages, never other players' names or Steam IDs.

## Brand Commitments

German UI copy. No Valve game assets (character models, maps, logos) are extracted or redistributed; player figures are original CT/T-style models built for this page. Minimal interface: no top bars or menus, the graphics carry the page.

## Evidence on Hand

`data/leetify/76561198382673172/` (profile.json, history.json, 17 match files). Analysis logic in `leetify_analyze.py`. No screenshots, demos or video of the player.

## Product Principles

- Only numbers that change what the player practises; everything else stays out.
- Compare with the player's own lobbies, not with pros.
- Every visual encodes a measured value; illustrations never imply data that does not exist.
- Each weakness ends in a concrete drill and a target the next update can check.
