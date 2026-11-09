#!/usr/bin/env python3
"""CS2 demo analysis with demoparser2: stats for every player, round by round and tick by tick.

Goes beyond the Leetify API: per round (economy, side, KAST, clutches, opening duels, trades),
per kill (positions, distance, wallbang/smoke/blind), per shot (speed when firing, burst index,
hit or miss) and per engagement (time to damage and crosshair placement from the moment an
enemy becomes visible).

Usage:
  python3 demo_analyze.py sync   [--push] [--steamid ID] [DEMO_OR_DIR ...]
      Analyse every demo not analysed yet (default: the CS2 replays folder), then with --push
      commit data/demos/ and push it to GitHub.
  python3 demo_analyze.py analyze DEMO [--steamid ID] [--force]   # one demo, even if done before
  python3 demo_analyze.py report  [--steamid ID]                  # summary of all analysed demos
  python3 demo_analyze.py push                                    # commit + push data/demos/

Output per demo in data/demos/<demo name>/:
  match.json        metadata, score, per-player stats (all players), per-round summary
  rounds.csv        one row per player and round (side, equipment, kills, damage, KAST, clutch ...)
  kills.csv         every kill with positions of killer and victim
  damage.csv        every damage event (health damage capped at remaining health)
  shots.csv         every gun shot: speed, counter-strafed, burst index, hit, head hit
  engagements.csv   every time a player saw an enemy: time to damage, crosshair angle off target
  grenades.csv      every grenade detonation with position, flashes with enemies/teammates blinded
data/demos/index.json lists all analysed demos with the main numbers of the tracked player.

Requires: pip install demoparser2 pandas (see requirements.txt).
"""
import argparse
import datetime as dt
import json
import math
import os
import subprocess
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
from demoparser2 import DemoParser

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "data", "demos")
DEFAULT_STEAM64 = "76561198382673172"
REPLAYS = os.path.expanduser(
    "~/.local/share/Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/replays")
TICK = 64
TRADE_WINDOW = 5 * TICK          # a death counts as traded if the killer dies within 5 s
BURST_GAP = 16                   # shots less than 0.25 s apart belong to the same burst
SPOT_GAP = 32                    # an enemy must be unseen for 0.5 s before a new sighting counts
ENGAGE_WINDOW = 3 * TICK         # damage within 3 s of a sighting counts for time to damage
EYE, EYE_DUCK = 64.0, 46.0

GRENADES = {"weapon_flashbang": "flash", "weapon_hegrenade": "he", "weapon_smokegrenade": "smoke",
            "weapon_molotov": "molotov", "weapon_incgrenade": "molotov", "weapon_decoy": "decoy"}
UTIL_HURT = {"hegrenade", "inferno", "molotov", "incgrenade", "flashbang", "smokegrenade", "decoy"}
UTIL_VALUE = {"Flashbang": 200, "Smoke Grenade": 300, "High Explosive Grenade": 300,
              "Molotov": 400, "Incendiary Grenade": 500, "Decoy Grenade": 50}
# Maximum running speed per weapon (units/s); a shot counts as counter-strafed below 34 % of it,
# the speed at which CS2 guns reach full standing accuracy.
MAX_SPEED = {"ak47": 215, "m4a1": 225, "m4a1_silencer": 225, "famas": 220, "galilar": 215,
             "aug": 220, "sg556": 210, "awp": 200, "ssg08": 230, "scar20": 215, "g3sg1": 215,
             "deagle": 230, "revolver": 220, "glock": 240, "usp_silencer": 240, "hkp2000": 240,
             "p250": 240, "fiveseven": 240, "tec9": 240, "cz75a": 240, "elite": 240,
             "mac10": 240, "mp9": 240, "mp7": 220, "mp5sd": 235, "ump45": 230, "p90": 230,
             "bizon": 240, "nova": 220, "xm1014": 215, "mag7": 225, "sawedoff": 210,
             "m249": 195, "negev": 150}
SHOTGUNS = {"nova", "xm1014", "mag7", "sawedoff"}
SNIPERS = {"awp", "ssg08", "scar20", "g3sg1"}


def is_gun(weapon):
    w = weapon.removeprefix("weapon_")
    return bool(w) and w not in {g.removeprefix("weapon_") for g in GRENADES} and w not in UTIL_HURT \
        and "knife" not in w and "bayonet" not in w and w not in {"c4", "taser", "world"}


def r(v, digits=1):
    if v is None or (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
        return None
    return round(float(v), digits)


def ratio(a, b, digits=3):
    return r(a / b, digits) if b else None


# ---------- share codes (link demos to Leetify matches) ----------

SHARE_ALPHABET = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefhijkmnopqrstuvwxyz23456789"


def sharecode_ids(code):
    n = 0
    for ch in reversed(code.removeprefix("CSGO-").replace("-", "")):
        n = n * 57 + SHARE_ALPHABET.index(ch)
    b = n.to_bytes(18, "big")
    return {int.from_bytes(b[0:8], "little"), int.from_bytes(b[8:16], "little")}


def find_leetify_match(match_id, steam64):
    path = os.path.join(ROOT, "data", "leetify", steam64, "history.json")
    if not match_id or not os.path.exists(path):
        return None
    for m in json.load(open(path, encoding="utf-8")):
        code = m.get("data_source_match_id") or ""
        if code.startswith("CSGO-"):
            try:
                if match_id in sharecode_ids(code):
                    return {"id": m["id"], "share_code": code, "finished_at": m.get("finished_at"),
                            "data_source": m.get("data_source")}
            except ValueError:
                pass
    return None


# ---------- parsing ----------

def sid(v):
    try:
        return str(int(v)) if v is not None and not (isinstance(v, float) and math.isnan(v)) and int(v) else None
    except (TypeError, ValueError):
        return None


def norm_ids(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].map(sid)
    return df


def analyze(demo_path, steam64):
    p = DemoParser(demo_path)
    header = p.parse_header()
    ev = lambda name, **kw: pd.DataFrame(p.parse_event(name, **kw))
    names = set(p.list_game_events())

    # --- rounds ---
    starts = [int(t) for name in ("round_announce_match_start", "begin_new_match") if name in names
              for t in ev(name)["tick"]]
    match_start = max(starts) if starts else 0
    rend = ev("round_end")
    rend = rend[rend.tick > match_start].drop_duplicates("round", keep="last").sort_values("tick")
    rend = rend[rend.winner.isin(["T", "CT"])].reset_index(drop=True)
    freeze = sorted(int(t) for t in ev("round_freeze_end")["tick"] if t > match_start)
    buyend = sorted(int(t) for t in ev("buytime_ended")["tick"]) if "buytime_ended" in names else []
    rounds = []
    prev_end = match_start
    for i, row in rend.iterrows():
        end = int(row.tick)
        fz = next((t for t in freeze if prev_end < t < end), prev_end + 1)
        be = next((t for t in buyend if fz <= t < end), fz)
        rounds.append({"round": i + 1, "start": prev_end, "freeze_end": fz, "buy_end": be, "end": end,
                       "winner": 2 if row.winner == "T" else 3, "reason": row.reason})
        prev_end = end
    if not rounds:
        raise RuntimeError("no completed rounds found")
    round_ends = np.array([x["end"] for x in rounds])

    def round_of(tick):
        i = int(np.searchsorted(round_ends, tick, side="left"))
        return i + 1 if i < len(rounds) and tick > rounds[i]["start"] else None

    # --- ticks (every tick, every player) ---
    ticks = pd.DataFrame(p.parse_ticks(["X", "Y", "Z", "pitch", "yaw", "is_alive", "team_num", "ducking",
                                        "approximate_spotted_by", "health"]))
    ticks = norm_ids(ticks, ["steamid"])
    ticks = ticks[ticks.steamid.notna() & ticks.team_num.isin([2, 3])]
    names_by_id = ticks.groupby("steamid")["name"].last().to_dict()
    per = {s: g.set_index("tick").sort_index() for s, g in ticks.groupby("steamid")}

    def at(steamid, tick, col):
        g = per.get(steamid)
        if g is None:
            return None
        idx = g.index.searchsorted(tick, side="right") - 1
        return g[col].iloc[idx] if idx >= 0 else None

    # side, equipment and money per player and round
    ft = [x["freeze_end"] for x in rounds] + [x["buy_end"] for x in rounds]
    snap = norm_ids(pd.DataFrame(p.parse_ticks(["team_num", "current_equip_value", "balance",
                                                "round_start_equip_value", "is_alive"], ticks=sorted(set(ft)))),
                    ["steamid"])
    snap = snap[snap.team_num.isin([2, 3])].set_index(["tick", "steamid"])
    side = {}         # (round, steamid) -> team_num
    equip = {}        # (round, steamid) -> (equip at buy end, money at round start)
    for x in rounds:
        for s in names_by_id:
            k = (x["freeze_end"], s)
            if k in snap.index:
                side[(x["round"], s)] = int(snap.loc[k, "team_num"])
                kb = (x["buy_end"], s)
                eq = snap.loc[kb] if kb in snap.index else snap.loc[k]
                equip[(x["round"], s)] = (int(eq["current_equip_value"]),
                                          int(snap.loc[k, "balance"] + snap.loc[k, "round_start_equip_value"]))

    # --- kills ---
    kills = ev("player_death", player=["X", "Y", "Z", "team_num"])
    kills = norm_ids(kills, ["attacker_steamid", "user_steamid", "assister_steamid"])
    kills["round"] = kills.tick.map(round_of)
    kills = kills[kills["round"].notna()].sort_values("tick").reset_index(drop=True)
    kills["round"] = kills["round"].astype(int)
    kills["team_kill"] = (kills.attacker_team_num == kills.user_team_num) & kills.attacker_steamid.notna() \
        & (kills.attacker_steamid != kills.user_steamid)
    kills["suicide"] = kills.attacker_steamid.isna() | (kills.attacker_steamid == kills.user_steamid)
    kills["enemy_kill"] = ~kills.team_kill & ~kills.suicide
    kills["time_in_round"] = [(t - rounds[rd - 1]["freeze_end"]) / TICK for t, rd in zip(kills.tick, kills["round"])]
    # trades
    kills["traded"] = False
    kills["trade_kill"] = False
    for i, k in kills[kills.enemy_kill].iterrows():
        later = kills[(kills.tick > k.tick) & (kills.tick <= k.tick + TRADE_WINDOW) & kills.enemy_kill
                      & (kills.user_steamid == k.attacker_steamid)]
        if len(later):
            kills.loc[i, "traded"] = True
            kills.loc[later.index[0], "trade_kill"] = True
    first = kills[kills.enemy_kill].groupby("round").head(1)
    kills["opening"] = kills.index.isin(first.index)

    # --- damage ---
    hurt = ev("player_hurt", player=["team_num"])
    hurt = norm_ids(hurt, ["attacker_steamid", "user_steamid"])
    hurt["round"] = hurt.tick.map(round_of)
    hurt = hurt[hurt["round"].notna()].sort_values("tick").reset_index(drop=True)
    hurt["round"] = hurt["round"].astype(int)
    hp = {}
    real = []
    for row in hurt.itertuples():
        key = (row.round, row.user_steamid)
        before = hp.get(key, 100)
        real.append(min(row.dmg_health, before))
        hp[key] = row.health
    hurt["damage"] = real
    hurt["enemy"] = hurt.attacker_steamid.notna() & (hurt.attacker_steamid != hurt.user_steamid) \
        & (hurt.attacker_team_num != hurt.user_team_num)
    hurt["team_damage"] = hurt.attacker_steamid.notna() & (hurt.attacker_steamid != hurt.user_steamid) \
        & (hurt.attacker_team_num == hurt.user_team_num)
    hurt["utility"] = hurt.weapon.isin(UTIL_HURT)

    # --- shots ---
    fire = ev("weapon_fire")
    fire = norm_ids(fire, ["user_steamid"])
    fire["round"] = fire.tick.map(round_of)
    fire = fire[fire["round"].notna() & fire.user_steamid.notna()].copy()
    fire["round"] = fire["round"].astype(int)
    thrown = fire[fire.weapon.isin(GRENADES)].copy()
    thrown["type"] = thrown.weapon.map(GRENADES)
    shots = fire[fire.weapon.map(is_gun)].sort_values(["user_steamid", "tick"]).copy()
    shots["weapon"] = shots.weapon.str.removeprefix("weapon_")
    gun_hits = hurt[hurt.enemy & ~hurt.utility & hurt.weapon.map(lambda w: is_gun(w))]
    hit_ticks = set(zip(gun_hits.attacker_steamid, gun_hits.tick))
    head_ticks = set(zip(gun_hits[gun_hits.hitgroup == "head"].attacker_steamid,
                         gun_hits[gun_hits.hitgroup == "head"].tick))
    shots["hit"] = [(s, t) in hit_ticks or (s, t - 1) in hit_ticks for s, t in zip(shots.user_steamid, shots.tick)]
    shots["head"] = [(s, t) in head_ticks or (s, t - 1) in head_ticks for s, t in zip(shots.user_steamid, shots.tick)]
    burst, speed, scoped = [], [], []
    last = {}
    for row in shots.itertuples():
        prev = last.get(row.user_steamid)
        n = prev[1] + 1 if prev and row.tick - prev[0] <= BURST_GAP and prev[2] == row.round else 0
        last[row.user_steamid] = (row.tick, n, row.round)
        burst.append(n)
        g = per.get(row.user_steamid)
        v = None
        if g is not None:
            i = g.index.searchsorted(row.tick, side="right") - 1
            if i >= 2:
                a, b = g.iloc[i - 2], g.iloc[i]
                dtk = g.index[i] - g.index[i - 2]
                if 0 < dtk <= 4:
                    v = math.hypot(b.X - a.X, b.Y - a.Y) * TICK / dtk
        speed.append(v)
    shots["burst_index"] = burst
    shots["speed"] = speed
    shots["max_speed"] = shots.weapon.map(lambda w: MAX_SPEED.get(w, 230))
    shots["counter_strafed"] = pd.Series([None if pd.isna(v) else bool(v <= 0.34 * m)
                                          for v, m in zip(shots.speed, shots.max_speed)],
                                         index=shots.index, dtype=object)

    # --- engagements: from first sighting of an enemy to first damage ---
    engagements = []
    hurt_by_pair = defaultdict(list)
    for row in hurt[hurt.enemy].itertuples():
        hurt_by_pair[(row.attacker_steamid, row.user_steamid)].append(row.tick)
    shots_by_player = {s: g.tick.values for s, g in shots.groupby("user_steamid")}
    live = np.zeros(int(ticks.tick.max()) + 2, dtype=bool)
    for x in rounds:
        live[x["freeze_end"]:x["end"] + 1] = True
    for victim, g in per.items():
        alive_v = g.is_alive.values.astype(bool)
        tick_idx = g.index.values
        spotted = g.approximate_spotted_by.values
        for shooter, gs in per.items():
            if shooter == victim:
                continue
            sh_int = int(shooter)
            seen = np.array([lst is not None and sh_int in lst for lst in spotted], dtype=bool)
            seen &= alive_v & live[tick_idx]
            if not seen.any():
                continue
            last_seen = -10 ** 9
            for j in np.flatnonzero(seen):
                t = int(tick_idx[j])
                new = t - last_seen > SPOT_GAP
                last_seen = t
                if not new:
                    continue
                rd = round_of(t)
                if rd is None or side.get((rd, shooter)) == side.get((rd, victim)):
                    continue
                si = gs.index.searchsorted(t, side="right") - 1
                if si < 0 or not gs.is_alive.iloc[si]:
                    continue
                a, v = gs.iloc[si], g.iloc[j]
                eye = np.array([a.X, a.Y, a.Z + (EYE_DUCK if a.ducking else EYE)])
                head = np.array([v.X, v.Y, v.Z + (EYE_DUCK if v.ducking else EYE)])
                to = head - eye
                dist = float(np.linalg.norm(to))
                if dist < 1:
                    continue
                pitch, yaw = math.radians(a.pitch), math.radians(a.yaw)
                look = np.array([math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), -math.sin(pitch)])
                angle = math.degrees(math.acos(max(-1.0, min(1.0, float(look @ to) / dist))))
                want_yaw = math.degrees(math.atan2(to[1], to[0]))
                want_pitch = -math.degrees(math.atan2(to[2], math.hypot(to[0], to[1])))
                dyaw = abs((a.yaw - want_yaw + 180) % 360 - 180)
                dpitch = abs(a.pitch - want_pitch)
                dmg = [h for h in hurt_by_pair.get((shooter, victim), []) if t <= h <= t + ENGAGE_WINDOW]
                st_ = shots_by_player.get(shooter, np.array([]))
                shot = st_[(st_ >= t) & (st_ <= t + ENGAGE_WINDOW)]
                engagements.append({
                    "round": rd, "tick": t, "steamid": shooter, "enemy_steamid": victim,
                    "distance": r(dist), "crosshair_angle": r(angle, 2), "yaw_off": r(dyaw, 2),
                    "pitch_off": r(dpitch, 2),
                    "time_to_damage_ms": r((dmg[0] - t) * 1000 / TICK, 0) if dmg else None,
                    "time_to_shot_ms": r((shot[0] - t) * 1000 / TICK, 0) if len(shot) else None,
                })
    engagements = pd.DataFrame(engagements, columns=["round", "tick", "steamid", "enemy_steamid", "distance",
                                                     "crosshair_angle", "yaw_off", "pitch_off",
                                                     "time_to_damage_ms", "time_to_shot_ms"])

    # --- grenades and flashes ---
    blind = ev("player_blind", player=["team_num"])
    blind = norm_ids(blind, ["attacker_steamid", "user_steamid"])
    blind["round"] = blind.tick.map(round_of)
    blind = blind[blind["round"].notna() & blind.attacker_steamid.notna()]
    blind["enemy"] = blind.attacker_team_num != blind.user_team_num
    blind["self"] = blind.attacker_steamid == blind.user_steamid
    gren_rows = []
    for evname, typ in (("flashbang_detonate", "flash"), ("hegrenade_detonate", "he"),
                        ("smokegrenade_detonate", "smoke"), ("inferno_startburn", "molotov"),
                        ("decoy_started", "decoy")):
        if evname not in names:
            continue
        e = norm_ids(ev(evname), ["user_steamid"])
        for row in e.itertuples():
            rd = round_of(row.tick)
            if rd is None or not row.user_steamid:
                continue
            item = {"round": rd, "tick": int(row.tick), "steamid": row.user_steamid, "type": typ,
                    "x": r(row.x), "y": r(row.y), "z": r(row.z)}
            if typ == "flash":
                b = blind[(blind.attacker_steamid == row.user_steamid) & (blind.tick >= row.tick)
                          & (blind.tick <= row.tick + 2) & ~blind.self]
                item["enemies_blinded"] = int((b.enemy & (b.blind_duration >= 1.1)).sum())
                item["enemy_blind_s"] = r(b[b.enemy].blind_duration.sum(), 2)
                item["teammates_blinded"] = int((~b.enemy & (b.blind_duration >= 1.1)).sum())
            gren_rows.append(item)
    grenades = pd.DataFrame(gren_rows)

    # unused utility at death
    inv_ticks = sorted({int(t) - 1 for t in kills.tick})
    inv = norm_ids(pd.DataFrame(p.parse_ticks(["inventory"], ticks=inv_ticks)), ["steamid"]) if inv_ticks else None
    util_on_death = {}
    if inv is not None:
        inv = inv.set_index(["tick", "steamid"])
        for row in kills.itertuples():
            k = (int(row.tick) - 1, row.user_steamid)
            if k in inv.index:
                util_on_death[row.Index] = sum(UTIL_VALUE.get(i, 0) for i in (inv.loc[k, "inventory"] or []))
    kills["utility_on_death"] = [util_on_death.get(i, 0) for i in kills.index]

    # bomb
    plants = norm_ids(ev("bomb_planted"), ["user_steamid"]) if "bomb_planted" in names else pd.DataFrame()
    defuses = norm_ids(ev("bomb_defused"), ["user_steamid"]) if "bomb_defused" in names else pd.DataFrame()

    # --- per player and round ---
    players = sorted(names_by_id)
    rows = []
    clutch_rows = []
    for x in rounds:
        rd = x["round"]
        alive = {s: side[(rd, s)] for s in players if (rd, s) in side}
        rk = kills[kills["round"] == rd]
        # clutches: a player alone against at least one enemy
        clutch = {}
        for k in rk.itertuples():
            alive.pop(k.user_steamid, None)
            for team in (2, 3):
                mine = [s for s, t in alive.items() if t == team]
                enemies = [s for s, t in alive.items() if t != team]
                if len(mine) == 1 and enemies and mine[0] not in clutch:
                    clutch[mine[0]] = len(enemies)
        for s, n in clutch.items():
            clutch_rows.append({"round": rd, "steamid": s, "vs": n, "won": x["winner"] == side[(rd, s)]})
        for s in players:
            if (rd, s) not in side:
                continue
            team = side[(rd, s)]
            mk = rk[(rk.attacker_steamid == s) & rk.enemy_kill]
            died = rk[rk.user_steamid == s]
            assists = rk[(rk.assister_steamid == s) & rk.enemy_kill & (rk.attacker_steamid != s)]
            dmg = hurt[(hurt["round"] == rd) & (hurt.attacker_steamid == s) & hurt.enemy]
            death_tick = int(died.tick.iloc[0]) if len(died) else None
            traded = bool(len(died) and died.traded.iloc[0])
            kast = bool(len(mk) or len(assists) or not len(died) or traded)
            eq = equip.get((rd, s), (None, None))
            rows.append({
                "round": rd, "steamid": s, "name": names_by_id[s], "side": "T" if team == 2 else "CT",
                "won": x["winner"] == team, "equip_value": eq[0], "money_start": eq[1],
                "kills": len(mk), "headshots": int(mk.headshot.sum()), "assists": len(assists),
                "flash_assists": int((assists.assistedflash == True).sum()),
                "died": bool(len(died)), "traded_death": traded,
                "trade_kills": int(mk.trade_kill.sum()), "damage": int(dmg.damage.sum()),
                "utility_damage": int(dmg[dmg.utility].damage.sum()),
                "opening_kill": bool(mk.opening.any()), "opening_death": bool(len(died) and died.opening.iloc[0]),
                "kast": kast, "clutch_vs": clutch.get(s), "clutch_won": (x["winner"] == team) if s in clutch else None,
                "survival_s": r(((death_tick or x["end"]) - x["freeze_end"]) / TICK),
                "utility_on_death": int(died.utility_on_death.iloc[0]) if len(died) else None,
            })
    prounds = pd.DataFrame(rows)

    # team economy per round
    for x in rounds:
        for team in (2, 3):
            vals = [equip[(x["round"], s)][0] for s in players
                    if side.get((x["round"], s)) == team and (x["round"], s) in equip]
            avg = sum(vals) / len(vals) if vals else 0
            x["T_equip" if team == 2 else "CT_equip"] = int(avg)
        x["winner"] = "T" if x["winner"] == 2 else "CT"
    halves = []
    for x in rounds:
        sides = tuple(side.get((x["round"], s)) for s in players)
        if not halves or halves[-1] != sides:
            halves.append(sides)
            x["pistol"] = True
        else:
            x["pistol"] = False
    for x in rounds:
        for t in ("T", "CT"):
            v = x[f"{t}_equip"]
            x[f"{t}_buy"] = "pistol" if x["pistol"] else "eco" if v < 1500 else "force" if v < 3800 else "full"

    # --- per player totals ---
    stats = {}
    n_rounds = len(rounds)
    for s in players:
        pr = prounds[prounds.steamid == s]
        nr = len(pr)
        if not nr:
            continue
        K, D, A = int(pr.kills.sum()), int(pr.died.sum()), int(pr.assists.sum())
        mk = kills[(kills.attacker_steamid == s) & kills.enemy_kill]
        multi = pr.kills.value_counts().to_dict()
        kpr, dpr, apr = K / nr, D / nr, A / nr
        adr = pr.damage.sum() / nr
        kast = pr.kast.mean() * 100
        surv = (nr - D) / nr
        rmk = sum(multi.get(i, 0) * i * i for i in range(1, 6)) / nr
        rating1 = (kpr / 0.679 + 0.7 * surv / 0.317 + rmk / 1.277) / 2.7
        impact = 2.13 * kpr + 0.42 * apr - 0.41
        rating2 = 0.0073 * kast + 0.3591 * kpr - 0.5329 * dpr + 0.2372 * impact + 0.0032 * adr + 0.1587
        sh = shots[shots.user_steamid == s]
        rifle = sh[~sh.weapon.isin(SHOTGUNS)]
        first_sh = rifle[rifle.burst_index == 0]
        spray = rifle[rifle.burst_index >= 3]
        cs = rifle[rifle.counter_strafed.notna()]
        cs_first = first_sh[first_sh.counter_strafed.notna()]
        en = engagements[engagements.steamid == s]
        en_dmg = en[en.time_to_damage_ms.notna()]
        gr = grenades[grenades.steamid == s] if len(grenades) else pd.DataFrame()
        fl = gr[gr.type == "flash"] if len(gr) else pd.DataFrame()
        bl = blind[(blind.attacker_steamid == s) & ~blind.self]
        th = thrown[thrown.user_steamid == s]
        dmg = hurt[(hurt.attacker_steamid == s)]
        cl = [c for c in clutch_rows if c["steamid"] == s]
        sides = {}
        for sd in ("T", "CT"):
            q = pr[pr.side == sd]
            if len(q):
                sides[sd] = {"rounds": len(q), "won": int(q.won.sum()), "kills": int(q.kills.sum()),
                             "deaths": int(q.died.sum()), "adr": r(q.damage.mean()),
                             "kast": r(q.kast.mean() * 100),
                             "opening_kills": int(q.opening_kill.sum()),
                             "opening_deaths": int(q.opening_death.sum())}
        by_weapon = {}
        for w, g in mk.groupby("weapon"):
            ws = sh[sh.weapon == w]
            by_weapon[w] = {"kills": len(g), "headshots": int(g.headshot.sum()), "shots": len(ws),
                            "hits": int(ws.hit.sum()), "accuracy": ratio(ws.hit.sum(), len(ws))}
        team_end = side.get((n_rounds, s))
        stats[s] = {
            "name": names_by_id[s], "rounds": nr,
            "rounds_won": int(pr.won.sum()),
            "kills": K, "deaths": D, "assists": A, "kd": ratio(K, D, 2),
            "adr": r(adr), "kast": r(kast), "hs_pct": r(mk.headshot.mean() * 100) if K else None,
            "rating_hltv1": r(rating1, 2), "rating_hltv2_approx": r(rating2, 2), "impact": r(impact, 2),
            "multikills": {f"{i}k": int(multi.get(i, 0)) for i in range(2, 6)},
            "opening": {"kills": int(pr.opening_kill.sum()), "deaths": int(pr.opening_death.sum()),
                        "attempts": int(pr.opening_kill.sum() + pr.opening_death.sum())},
            "trades": {"trade_kills": int(pr.trade_kills.sum()), "traded_deaths": int(pr.traded_death.sum()),
                       "deaths_not_traded": int((pr.died & ~pr.traded_death).sum())},
            "clutches": {"attempts": len(cl), "won": sum(c["won"] for c in cl),
                         "by_vs": {f"1v{n}": {"attempts": sum(1 for c in cl if c["vs"] == n),
                                              "won": sum(1 for c in cl if c["vs"] == n and c["won"])}
                                   for n in sorted({c["vs"] for c in cl})}},
            "survival": {"rounds_survived": nr - D, "avg_time_alive_s": r(pr.survival_s.mean())},
            "kills_detail": {
                "wallbang": int((mk.penetrated > 0).sum()), "through_smoke": int(mk.thrusmoke.sum()),
                "while_blind": int(mk.attackerblind.sum()), "noscope": int(mk.noscope.sum()),
                "in_air": int(mk.attackerinair.sum()), "avg_distance": r(mk.distance.mean()),
                "avg_time_in_round_s": r(mk.time_in_round.mean())},
            "aim": {
                "shots": len(sh), "hits": int(sh.hit.sum()), "accuracy": ratio(sh.hit.sum(), len(sh)),
                "head_accuracy": ratio(sh["head"].sum(), sh.hit.sum()),
                "first_shot_accuracy": ratio(first_sh.hit.sum(), len(first_sh)),
                "spray_accuracy": ratio(spray.hit.sum(), len(spray)),
                "counter_strafe_pct": r(cs.counter_strafed.astype(bool).mean() * 100) if len(cs) else None,
                "counter_strafe_first_shot_pct": r(cs_first.counter_strafed.astype(bool).mean() * 100)
                if len(cs_first) else None,
                "avg_speed_first_shot": r(first_sh.speed.mean()),
                "engagements": len(en),
                "crosshair_angle_median": r(en.crosshair_angle.median(), 2),
                "crosshair_yaw_median": r(en.yaw_off.median(), 2),
                "crosshair_pitch_median": r(en.pitch_off.median(), 2),
                "time_to_damage_median_ms": r(en_dmg.time_to_damage_ms.median(), 0),
                "time_to_shot_median_ms": r(en.time_to_shot_ms.median(), 0),
                "engagements_damaged_pct": r(len(en_dmg) / len(en) * 100) if len(en) else None},
            "utility": {
                "thrown": {t: int((th.type == t).sum()) for t in ("flash", "smoke", "he", "molotov", "decoy")},
                "damage": int(dmg[dmg.enemy & dmg.utility].damage.sum()),
                "he_damage": int(dmg[dmg.enemy & (dmg.weapon == "hegrenade")].damage.sum()),
                "fire_damage": int(dmg[dmg.enemy & dmg.weapon.isin(["inferno", "molotov", "incgrenade"])].damage.sum()),
                "enemies_flashed": int((bl.enemy & (bl.blind_duration >= 1.1)).sum()),
                "enemy_blind_time_s": r(bl[bl.enemy].blind_duration.sum(), 2),
                "teammates_flashed": int((~bl.enemy & (bl.blind_duration >= 1.1)).sum()),
                "flash_assists": int(pr.flash_assists.sum()),
                "enemies_per_flash": ratio((bl.enemy & (bl.blind_duration >= 1.1)).sum(), len(fl), 2),
                "avg_utility_value_on_death": r(pr.utility_on_death.dropna().mean(), 0)},
            "damage": {"total": int(pr.damage.sum()),
                       "team_damage": int(hurt[(hurt.attacker_steamid == s) & hurt.team_damage].damage.sum()),
                       "taken": int(hurt[(hurt.user_steamid == s) & hurt.enemy].damage.sum())},
            "economy": {"avg_equip_value": r(pr.equip_value.mean(), 0)},
            "bomb": {"plants": int((plants.user_steamid == s).sum()) if len(plants) else 0,
                     "defuses": int((defuses.user_steamid == s).sum()) if len(defuses) else 0},
            "sides": sides,
            "weapons": by_weapon,
            "final_team": "T" if team_end == 2 else "CT" if team_end == 3 else None,
        }

    # score
    last_round = rounds[-1]["round"]
    final = {}
    for s, st_ in stats.items():
        final[s] = st_["rounds_won"]
    me = stats.get(steam64)
    base = os.path.basename(demo_path)
    match_id = None
    parts = base.split("_")
    if base.startswith("match730_") and len(parts) > 1 and parts[1].isdigit():
        match_id = int(parts[1])
    meta = {
        "demo": base, "map": header.get("map_name"), "server": header.get("server_name"),
        "patch": header.get("patch_version"), "match_id": str(match_id) if match_id else None,
        "demo_mtime": dt.datetime.fromtimestamp(os.path.getmtime(demo_path), dt.timezone.utc).isoformat(timespec="seconds"),
        "rounds": n_rounds, "players": len(stats),
        "mode": {4: "wingman", 10: "5v5"}.get(len(stats), f"{len(stats)} players"),
        "leetify": find_leetify_match(match_id, steam64),
        "analysed_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "tool": f"demo_analyze.py (demoparser2)",
    }
    if me:
        my_team = me["final_team"]
        won = me["rounds_won"]
        meta["tracked_player"] = steam64
        meta["score"] = {"own": won, "enemy": n_rounds - won,
                         "result": "win" if won > n_rounds - won else "loss" if won < n_rounds - won else "draw"}

    # tables for output
    kills_out = kills.rename(columns={"user_steamid": "victim_steamid", "user_name": "victim_name",
                                      "user_X": "victim_x", "user_Y": "victim_y", "user_Z": "victim_z",
                                      "attacker_X": "attacker_x", "attacker_Y": "attacker_y", "attacker_Z": "attacker_z",
                                      "attacker_team_num": "attacker_team", "user_team_num": "victim_team"})
    kills_out = kills_out[["round", "tick", "time_in_round", "attacker_steamid", "attacker_name", "attacker_team",
                           "victim_steamid", "victim_name", "victim_team", "assister_steamid", "weapon", "headshot",
                           "penetrated", "thrusmoke", "attackerblind", "noscope", "attackerinair", "assistedflash",
                           "distance", "attacker_x", "attacker_y", "attacker_z", "victim_x", "victim_y", "victim_z",
                           "opening", "trade_kill", "traded", "team_kill", "utility_on_death"]]
    damage_out = hurt.rename(columns={"user_steamid": "victim_steamid", "health": "health_after"})[
        ["round", "tick", "attacker_steamid", "victim_steamid", "weapon", "hitgroup", "dmg_health", "damage",
         "dmg_armor", "health_after", "enemy", "team_damage", "utility"]]
    shots_out = shots.rename(columns={"user_steamid": "steamid"})[
        ["round", "tick", "steamid", "weapon", "speed", "max_speed", "counter_strafed", "burst_index", "hit", "head"]]
    return {
        "meta": meta, "players": stats, "rounds": rounds, "clutches": clutch_rows,
        "tables": {"rounds": prounds, "kills": kills_out, "damage": damage_out, "shots": shots_out,
                   "engagements": engagements, "grenades": grenades},
    }


# ---------- output ----------

def demo_id(path):
    return os.path.splitext(os.path.basename(path))[0]


def save(result, path):
    d = os.path.join(OUT, demo_id(path))
    os.makedirs(d, exist_ok=True)
    for name, df in result["tables"].items():
        df = df.copy()
        for c in df.columns:
            if df[c].dtype == float:
                df[c] = df[c].round(2)
        df.to_csv(os.path.join(d, f"{name}.csv"), index=False)
    doc = {k: v for k, v in result.items() if k != "tables"}
    with open(os.path.join(d, "match.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    return d


def update_index(steam64):
    items = []
    for name in sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []:
        f = os.path.join(OUT, name, "match.json")
        if not os.path.exists(f):
            continue
        m = json.load(open(f, encoding="utf-8"))
        me = m["players"].get(steam64) or {}
        items.append({"demo": name, "map": m["meta"]["map"], "mode": m["meta"]["mode"],
                      "rounds": m["meta"]["rounds"], "date": (m["meta"].get("leetify") or {}).get("finished_at")
                      or m["meta"]["demo_mtime"], "score": m["meta"].get("score"),
                      "leetify_id": (m["meta"].get("leetify") or {}).get("id"),
                      "rating_hltv1": me.get("rating_hltv1"), "adr": me.get("adr"), "kast": me.get("kast"),
                      "kills": me.get("kills"), "deaths": me.get("deaths"),
                      "crosshair_angle_median": (me.get("aim") or {}).get("crosshair_angle_median"),
                      "time_to_damage_median_ms": (me.get("aim") or {}).get("time_to_damage_median_ms"),
                      "counter_strafe_pct": (me.get("aim") or {}).get("counter_strafe_pct")})
    items.sort(key=lambda x: x["date"] or "")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"steamid": steam64, "matches": items}, f, ensure_ascii=False, indent=1)
    return items


def collect(paths):
    out = []
    for p in paths or [REPLAYS]:
        p = os.path.expanduser(p)
        if os.path.isdir(p):
            out += [os.path.join(p, f) for f in sorted(os.listdir(p)) if f.endswith(".dem")]
        elif p.endswith(".dem") and os.path.exists(p):
            out.append(p)
        else:
            print(f"skip (not a .dem file or folder): {p}", file=sys.stderr)
    return out


def print_summary(result, steam64):
    m, me = result["meta"], result["players"].get(steam64)
    score = m.get("score") or {}
    print(f"{m['map']} {m['mode']} {m['rounds']} rounds  {score.get('own', '?')}:{score.get('enemy', '?')} "
          f"{score.get('result', '')}")
    if not me:
        print("  tracked player not in this demo")
        return
    a, u = me["aim"], me["utility"]
    print(f"  {me['name']}: {me['kills']}-{me['deaths']}-{me['assists']}  ADR {me['adr']}  KAST {me['kast']}%  "
          f"HLTV1 {me['rating_hltv1']}  HS {me['hs_pct']}%")
    print(f"  aim: crosshair {a['crosshair_angle_median']}°  time to damage {a['time_to_damage_median_ms']} ms  "
          f"counter-strafe {a['counter_strafe_pct']}%  first shot {a['first_shot_accuracy']}  "
          f"spray {a['spray_accuracy']}")
    print(f"  openings {me['opening']['kills']}/{me['opening']['attempts']}  "
          f"clutches {me['clutches']['won']}/{me['clutches']['attempts']}  "
          f"untraded deaths {me['trades']['deaths_not_traded']}  utility dmg {u['damage']}  "
          f"enemies flashed {u['enemies_flashed']}")


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], check=True, capture_output=True, text=True).stdout


def push(message):
    git("add", "data/demos")
    if not git("diff", "--cached", "--name-only").strip():
        print("nothing new to push")
        return
    git("commit", "-m", message)
    git("pull", "--rebase", "--autostash")
    git("push")
    print("pushed:", git("log", "-1", "--format=%h %s").strip())


def report(steam64):
    items = update_index(steam64)
    if not items:
        print("no analysed demos in data/demos/")
        return
    for it in items:
        sc = it["score"] or {}
        print(f"{(it['date'] or '')[:10]}  {it['map']:<12} {it['mode']:<8} {sc.get('own', '?'):>2}:{sc.get('enemy', '?'):<2} "
              f"K/D {it['kills']}/{it['deaths']}  ADR {it['adr']}  KAST {it['kast']}  HLTV1 {it['rating_hltv1']}  "
              f"crosshair {it['crosshair_angle_median']}°  TTD {it['time_to_damage_median_ms']} ms  "
              f"strafe {it['counter_strafe_pct']}%")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["sync", "analyze", "report", "push"])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--steamid", default=DEFAULT_STEAM64)
    ap.add_argument("--push", action="store_true", help="commit and push data/demos/ after sync")
    ap.add_argument("--force", action="store_true", help="re-analyse demos that were analysed before")
    a = ap.parse_args()

    if a.command == "report":
        return report(a.steamid)
    if a.command == "push":
        update_index(a.steamid)
        return push("Demo stats: update")
    demos = collect(a.paths)
    if a.command == "analyze" and not demos:
        ap.error("no demo given")
    done = []
    for path in demos:
        if not (a.force or a.command == "analyze") and os.path.exists(os.path.join(OUT, demo_id(path), "match.json")):
            continue
        print(f"analysing {os.path.basename(path)} ...")
        try:
            res = analyze(path, a.steamid)
        except Exception as e:  # keep going with the other demos
            print(f"  failed: {e}", file=sys.stderr)
            continue
        save(res, path)
        print_summary(res, a.steamid)
        done.append(res["meta"])
    update_index(a.steamid)
    if not done:
        print("no new demos")
    if a.push:
        label = ", ".join(f"{m['map']} {(m.get('leetify') or {}).get('finished_at', m['demo_mtime'])[:10]}" for m in done)
        push(f"Demo stats: {label}" if done else "Demo stats: update index")


if __name__ == "__main__":
    main()
