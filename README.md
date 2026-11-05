# cs2stats

Personal CS2 stats from the [Leetify Public CS API](https://api-public-docs.cs-prod.leetify.com/).

## Scripts

| Command | What it does |
| --- | --- |
| `node leetify-stats.mjs <SteamID64 or profile URL>` | Profile overview: ranks (Premier, FACEIT, Competitive), Leetify ratings, aim and utility stats, last 10 matches. |
| `python3 leetify_analyze.py fetch [SteamID64]` | Downloads profile, match history and details of new matches to `data/leetify/<SteamID64>/`. |
| `python3 leetify_analyze.py report [SteamID64] [all\|matches\|summary]` | Match-by-match analysis comparing you with your team and the lobby (ADR, rating rank, aim, preaim, utility, trades), plus totals by mode, map, result and trend. |

The SteamID64 defaults to `76561198382673172`. Optional: put `LEETIFY_API_KEY=...` in `.env` (git-ignored) for higher rate limits; get a key at [leetify.com/app/developer](https://leetify.com/app/developer).

Leetify sends ratings as fractions (0.0512); the scripts multiply them by 100 to match leetify.com (+5.12).

## Data

`data/leetify/<SteamID64>/` holds the raw API responses: `profile.json`, `history.json` and one file per match in `matches/` with the stats of all players in that match.

Data Provided by Leetify. [View on Leetify](https://leetify.com/app/profile/76561198382673172)
