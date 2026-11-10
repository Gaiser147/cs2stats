# cs2stats

Personal CS2 stats from the [Leetify Public CS API](https://api-public-docs.cs-prod.leetify.com/).

## Scripts

| Command | What it does |
| --- | --- |
| `node leetify-stats.mjs <SteamID64 or profile URL>` | Profile overview: ranks (Premier, FACEIT, Competitive), Leetify ratings, aim and utility stats, last 10 matches. |
| `python3 leetify_analyze.py fetch [SteamID64]` | Downloads profile, match history and details of new matches to `data/leetify/<SteamID64>/`. |
| `python3 demo_analyze.py auto` | Fully automatic: updates the Leetify match list, fetches the demo of every matchmaking match from the last 30 days that has no demo stats yet, analyses it and pushes. |
| `python3 demo_analyze.py sync --push` | Analyses every new CS2 demo in the replays folder with [demoparser2](https://github.com/LaihoE/demoparser), writes the stats to `data/demos/` and pushes them to GitHub. |
| `python3 demo_analyze.py analyze <demo.dem>` | Analyses one demo (any path), also again if it was analysed before. |
| `python3 demo_analyze.py report` | One line per analysed demo: score, K/D, ADR, KAST, rating, crosshair angle, time to damage, counter-strafing. |
| `python3 leetify_analyze.py report [SteamID64] [all\|matches\|summary]` | Match-by-match analysis comparing you with your team and the lobby (ADR, rating rank, aim, preaim, utility, trades), plus totals by mode, map, result and trend. |

The SteamID64 defaults to `76561198382673172`. Optional: put `LEETIFY_API_KEY=...` in `.env` (git-ignored) for higher rate limits; get a key at [leetify.com/app/developer](https://leetify.com/app/developer).

Leetify sends ratings as fractions (0.0512); the scripts multiply them by 100 to match leetify.com (+5.12).

## Demo analysis

Setup once: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, then run the script with `.venv/bin/python demo_analyze.py ...`.
Demos come from CS2 (Watch → Your Matches → download); they land in `~/.local/share/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays/`, which `sync` reads by default. The `.dem` files themselves are not committed.

### Automatic download

`auto` turns each Leetify match's share code into match ID, outcome ID and token, asks the CS2 game coordinator for the replay link through the running Steam client with [boiler-writter](https://github.com/akiver/boiler-writter) (from the CS Demo Manager author, downloaded to `tools/boiler/` on first use), downloads the `.dem.bz2` from Valve's replay server to `~/.cache/cs2stats/demos/` and analyses it. Requirements: Steam running and logged in, **CS2 closed** (only one program per account can talk to the game coordinator; `auto` waits for the next run while CS2 is open). Valve keeps demos for about a month; matches whose demo is gone are remembered in `~/.cache/cs2stats/auto_state.json` and skipped.

Run it every 2 hours with a systemd user timer:

```
mkdir -p ~/.config/systemd/user && cp systemd/cs2stats.* ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now cs2stats.timer
journalctl --user -u cs2stats.service    # log of the runs
```

Per demo, `data/demos/<demo name>/` holds:

| File | Content |
| --- | --- |
| `match.json` | Map, score, link to the Leetify match (decoded from the share code), per-round summary (winner, reason, team equipment, buy type) and per-player totals for all players: K/D/A, ADR, KAST, HLTV 1.0 rating and an approximation of 2.0, multi-kills, opening duels, trade kills and traded deaths, clutches by 1vX, survival, kill details (wallbang, smoke, blind, distance), aim, utility, damage taken and team damage, economy, bomb, T/CT split, per-weapon kills and accuracy. |
| `rounds.csv` | One row per player and round: side, equipment value, money, kills, damage, KAST, opening, trade, clutch, survival time, utility value held on death. |
| `kills.csv` | Every kill with killer and victim positions and callouts, time into the round, weapon and flags. |
| `damage.csv` | Every damage event with attacker and victim positions and callouts; `damage` is capped at the victim's remaining health (ADR matches Leetify). |
| `shots.csv` | Every gun shot: position and callout, horizontal speed, counter-strafed (below 34 % of the weapon's max speed), position in the burst, hit and head hit. |
| `engagements.csv` | Every time a player sees an enemy after 0.5 s unseen: both positions and callouts, distance, crosshair angle off the enemy's head (total, horizontal, vertical), time to first shot and to first damage. |
| `grenades.csv` | Every grenade detonation with position; flashes with enemies and teammates blinded (≥ 1.1 s). |
| `positions.csv.gz` | Movement: every alive player every 0.5 s of live round time with position, view direction (yaw), health, weapon and callout. |

`match.json` also lists per player the callouts of their kills and deaths (`places`, deaths split by side).

### Positions on the radar

Positions are game coordinates. `data/maps/overviews.json` holds each map's radar transform, read from the game files with `python3 demo_analyze.py maps` (numbers only; the radar images are Valve's and are not in this repo). On a 1024×1024 radar image: `pixel_x = (x - pos_x) / scale`, `pixel_y = (pos_y - y) / scale`. Maps with `vertical_sections` (Nuke, Vertigo) have a second radar for the lower level, chosen by z. Wingman maps with a `_2v2` entry (e.g. `de_overpass_2v2`) use that one.

`data/demos/index.json` lists all analysed demos with the tracked player's main numbers.

Aim definitions differ from Leetify: a sighting starts when the server marks the enemy as spotted by the player (the radar spot, which needs the enemy in view), so crosshair angle and time to damage come out lower than Leetify's preaim and reaction time. Compare them across your own demos, not with Leetify numbers. Kills match Leetify in every match; deaths in 224 of 228 player rows (bomb deaths count, "world" suicides after the round do not); ADR within 1.5. Assists are the game's own and can differ from Leetify's by one; flash assists are counted separately.

## Data

`data/leetify/<SteamID64>/` holds the raw API responses: `profile.json`, `history.json` and one file per match in `matches/` with the stats of all players in that match.

Data Provided by Leetify. [View on Leetify](https://leetify.com/app/profile/76561198382673172)
