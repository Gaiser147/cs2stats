"""Demo digest for the debrief: aim mechanics, opening duels and death maps from data/demos/.

Standard library only. Only the tracked player's own events and anonymous lobby aggregates leave this
module; other players' names and Steam IDs stay in the repo data and never reach the page.

Floor plans are traced from where all players walked (positions.csv.gz, every 0.5 s): the occupied cells
of a grid over the radar space, closed and outlined. No radar image or other game asset is used.
"""
import csv
import glob
import gzip
import json
import os
import re
import statistics as st

ROOT = os.path.dirname(os.path.abspath(__file__))
DEMOS = os.path.join(ROOT, "data", "demos")
MAP_MIN_DEATHS = 20   # a focus map needs at least this many of your deaths in the demos
FOCUS_MAPS = 2        # deep-dive pages; every other map only appears in the overview
GEOMETRY = os.path.join(ROOT, "data", "maps", "geometry")
BAND = 40             # height bands of the floor shading, in game units


def _wavg(pairs):
    """Round-weighted mean of (value, rounds) pairs; None values are skipped."""
    pairs = [(v, w) for v, w in pairs if v is not None]
    tot = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / tot if tot else None


def _place(name):
    """'BombsiteA' -> 'Bombsite A', 'SnipersNest' -> 'Snipers Nest'."""
    return re.sub(r"(?<=[a-z])(?=[A-Z0-9])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name or "").strip()


def _short(map_name):
    return map_name.split("_", 1)[-1]


# ---------- map view: nav-mesh floor plan, places, your deaths and kills ----------

def _samples(ov, demos):
    """Place statistics from everyone's movement: per place the mean radar position and height, and per
    (4 px cell, 64-unit height step) the most common place, to tag floor polygons with their callout."""
    places, cells = {}, {}
    for d in demos:
        path = os.path.join(DEMOS, d, "positions.csv.gz")
        if not os.path.exists(path):
            continue
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if not r.get("place"):
                    continue
                x, y, z = float(r["x"]), float(r["y"]), float(r["z"])
                px, py = (x - ov["pos_x"]) / ov["scale"], (ov["pos_y"] - y) / ov["scale"]
                s = places.setdefault(r["place"], [0.0, 0.0, 0.0, 0])
                s[0] += px; s[1] += py; s[2] += z; s[3] += 1
                c = cells.setdefault((int(px // 4), int(py // 4), int(z // 64)), {})
                c[r["place"]] = c.get(r["place"], 0) + 1
    centroids = {k: (v[0] / v[3], v[1] / v[3], v[2] / v[3], v[3]) for k, v in places.items() if v[3] >= 20}
    return centroids, cells


def _poly_place(cells, px, py, z):
    best = {}
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for k, v in cells.get((int(px // 4) + dx, int(py // 4) + dy, int(z // 64) + dz), {}).items():
                    best[k] = best.get(k, 0) + v * (3 if dx == dy == dz == 0 else 1)
    return max(best, key=best.get) if best else None


def map_view(map_name, ov, demos, deaths, kills):
    path = os.path.join(GEOMETRY, map_name + ".json")
    if not os.path.exists(path):
        return None
    geo = json.load(open(path, encoding="utf-8"))
    to_px = lambda x, y: ((x - ov["pos_x"]) / ov["scale"], (ov["pos_y"] - y) / ov["scale"])
    polys = [[to_px(p[k], p[k + 1]) for k in range(0, len(p), 2)] for p in geo["polys"]]
    zs = geo["z"]
    lower = (ov.get("vertical_sections") or {}).get("lower")
    split = lower["z_max"] if lower else None
    level = lambda z: 1 if split is not None and z < split else 0
    centroids, cells = _samples(ov, demos)

    # panels: one, or for maps with two radar levels (Nuke) the upper and the lower level side by side or stacked
    groups = {}
    for i, z in enumerate(zs):
        groups.setdefault(level(z), []).append(i)
    keys = sorted(groups)
    boxes = {}
    for k in keys:
        xs = [x for i in groups[k] for x, _ in polys[i]]
        ys = [y for i in groups[k] for _, y in polys[i]]
        boxes[k] = (min(xs), min(ys), max(xs), max(ys))
    pad = 30
    layout = {}
    if len(keys) == 1:
        layout[keys[0]] = (pad, pad, 1000 - 2 * pad, 1000 - 2 * pad)
    else:
        w = [boxes[k][2] - boxes[k][0] for k in keys]
        h = [boxes[k][3] - boxes[k][1] for k in keys]
        side = min((1000 - 3 * pad) / sum(w), (1000 - 2 * pad) / max(h))
        stack = min((1000 - 2 * pad) / max(w), (1000 - 3 * pad) / sum(h))
        if side >= stack:
            x = pad
            for k, wk in zip(keys, w):
                layout[k] = (x, pad, wk * side, 1000 - 2 * pad); x += wk * side + pad
        else:
            y = pad
            for k, hk in zip(keys, h):
                layout[k] = (pad, y, 1000 - 2 * pad, hk * stack); y += hk * stack + pad
    tf = {}
    for k in keys:
        bx0, by0, bx1, by1 = boxes[k]
        rx, ry, rw, rh = layout[k]
        sc = min(rw / (bx1 - bx0), rh / (by1 - by0))
        ox, oy = rx + (rw - (bx1 - bx0) * sc) / 2, ry + (rh - (by1 - by0) * sc) / 2
        tf[k] = (bx0, by0, sc, ox, oy)
    def norm(px, py, k):
        bx0, by0, sc, ox, oy = tf[k]
        return [round(ox + (px - bx0) * sc), round(oy + (py - by0) * sc)]

    z0 = min(zs)
    zspan = max(max(zs) - z0, 1)
    panels = []
    for k in keys:
        bands = {}
        sites = {"A": [], "B": []}
        for i in sorted(groups[k], key=lambda i: zs[i]):
            flat = [c for x, y in polys[i] for c in norm(x, y, k)]
            bands.setdefault(int((zs[i] - z0) // BAND), []).append(flat)
            cx = sum(x for x, _ in polys[i]) / len(polys[i])
            cy = sum(y for _, y in polys[i]) / len(polys[i])
            pl = _poly_place(cells, cx, cy, zs[i])
            if pl in ("BombsiteA", "BombsiteB"):
                sites[pl[-1]].append(flat)
        panels.append({
            "name": ("unten" if k else "oben") if len(keys) > 1 else "",
            "rect": [round(v) for v in layout[k]],
            "bands": [{"t": round(min(1, (b * BAND + BAND / 2) / zspan), 3), "polys": v} for b, v in sorted(bands.items())],
            "sites": {s: v for s, v in sites.items() if v},
        })

    names = sorted(centroids)
    places = []
    for p in names:
        px, py, z, n = centroids[p]
        places.append({"name": _place(p), "key": p, "at": norm(px, py, level(z)) + [level(z)], "n": n})
    pidx = lambda p: names.index(p) if p in centroids else -1
    dpts = [norm(*to_px(x, y), level(z)) + [1 if s == "CT" else 0, 1 if op else 0, pidx(place)] for x, y, z, s, op, place in deaths]
    kpts = [norm(*to_px(x, y), level(z)) + [pidx(place)] for x, y, z, place in kills]
    return {"panels": panels, "places": places, "deaths": dpts, "kills": kpts}


# ---------- which maps matter ----------

def map_relevance(rows, deaths_by_map):
    """Rank the maps from the Leetify history: played often and recently, and lost on.
    relevance = share of recent rounds (each older match counts 10 % less) x (1 + ADR deficit / 20) x (1.5 - win rate)."""
    five = sorted([r for r in rows or [] if r.get("n_lobby", 0) >= 10 and r.get("rounds", 0) >= 5], key=lambda r: r["date"])
    stats = {}
    for age, r in enumerate(reversed(five)):
        s = stats.setdefault(r["map"], {"matches": 0, "rounds": 0, "w": 0, "l": 0, "adr": 0.0, "l_adr": 0.0, "rating": 0.0, "fresh": 0.0, "last": r["date"]})
        s["matches"] += 1; s["rounds"] += r["rounds"]
        s["w"] += r["res"] == "W"; s["l"] += r["res"] == "L"
        s["adr"] += r["adr"] * r["rounds"]; s["l_adr"] += r["l_adr"] * r["rounds"]; s["rating"] += r["rating"]
        s["fresh"] += r["rounds"] * 0.9 ** age
    tot = sum(s["fresh"] for s in stats.values()) or 1
    out = []
    for m, s in stats.items():
        adr, ladr = s["adr"] / s["rounds"], s["l_adr"] / s["rounds"]
        wr = s["w"] / s["matches"]
        rel = s["fresh"] / tot * (1 + max(0, ladr - adr) / 20) * (1.5 - wr)
        out.append({"map": m, "name": m.capitalize(), "matches": s["matches"], "rounds": s["rounds"], "w": s["w"], "l": s["l"],
                    "adr": round(adr, 1), "l_adr": round(ladr, 1), "rating": round(s["rating"] / s["matches"], 2),
                    "last": s["last"], "relevance": round(rel, 4),
                    "demo_deaths": len(deaths_by_map.get(m, []))})
    return sorted(out, key=lambda x: -x["relevance"])


# ---------- digest ----------

def digest(steam64, rows=None):
    idx_path = os.path.join(DEMOS, "index.json")
    if not os.path.exists(idx_path):
        return None
    index = [m for m in json.load(open(idx_path, encoding="utf-8"))["matches"]]
    five = sorted([m for m in index if m.get("mode") == "5v5" and m.get("rounds", 0) >= 5], key=lambda m: m["date"])
    if not five:
        return None
    ov_all = json.load(open(os.path.join(ROOT, "data", "maps", "overviews.json"), encoding="utf-8"))["maps"]

    aim_keys = {"angle": "crosshair_angle_median", "yaw": "crosshair_yaw_median", "pitch": "crosshair_pitch_median",
                "ttd": "time_to_damage_median_ms", "cs": "counter_strafe_pct", "fsa": "first_shot_accuracy", "head": "head_accuracy"}
    me = {k: [] for k in aim_keys}; lob = {k: [] for k in aim_keys}
    me["kast"], lob["kast"] = [], []
    opening = {"me": {"T": [0, 0], "CT": [0, 0]}, "lobby": {"T": [0, 0], "CT": [0, 0]}}
    per_demo, dist, rounds_total = [], [], 0
    deaths_by_map, kills_by_map, rounds_by_map = {}, {}, {}
    for m in five:
        folder = os.path.join(DEMOS, m["demo"])
        match = json.load(open(os.path.join(folder, "match.json"), encoding="utf-8"))
        rounds_total += m["rounds"]
        rounds_by_map[m["map"]] = rounds_by_map.get(m["map"], 0) + m["rounds"]
        for sid, p in match["players"].items():
            tgt, a, w = (me if sid == steam64 else lob), p.get("aim") or {}, p["rounds"]
            for k, src in aim_keys.items():
                tgt[k].append((a.get(src), w))
            tgt["kast"].append((p.get("kast"), w))
        side = {}
        with open(os.path.join(folder, "rounds.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                side[(r["round"], r["steamid"])] = r["side"]
        own_open = {"T": [0, 0], "CT": [0, 0]}
        with open(os.path.join(folder, "kills.csv"), encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["team_kill"] == "True":
                    continue
                if r["opening"] == "True":
                    for sid, won in ((r["attacker_steamid"], 1), (r["victim_steamid"], 0)):
                        s = side.get((r["round"], sid))
                        if s in ("T", "CT"):
                            bucket = opening["me" if sid == steam64 else "lobby"][s]
                            bucket[0] += won; bucket[1] += 1
                            if sid == steam64:
                                own_open[s][0] += won; own_open[s][1] += 1
                if r["victim_steamid"] == steam64 and r["victim_x"]:
                    deaths_by_map.setdefault(m["map"], []).append(
                        (float(r["victim_x"]), float(r["victim_y"]), float(r["victim_z"]), side.get((r["round"], steam64)), r["opening"] == "True", r["victim_place"]))
                if r["attacker_steamid"] == steam64 and r["attacker_x"]:
                    kills_by_map.setdefault(m["map"], []).append((float(r["attacker_x"]), float(r["attacker_y"]), float(r["attacker_z"]), r["attacker_place"]))
        with open(os.path.join(folder, "engagements.csv"), encoding="utf-8") as f:
            pitch = []
            for r in csv.DictReader(f):
                if r["steamid"] == steam64 and r["distance"]:
                    dist.append(float(r["distance"]))
                    if r["pitch_off"]:
                        pitch.append(float(r["pitch_off"]))
        per_demo.append({"date": m["date"][:10], "map": m["map"], "rounds": m["rounds"],
                         "pitch": round(st.median(pitch), 2) if pitch else None, "open_ct": own_open["CT"], "open_t": own_open["T"]})

    out = {
        "n": len(five), "rounds": rounds_total, "first": five[0]["date"][:10], "last": five[-1]["date"][:10],
        "me": {k: round(_wavg(v), 4) if _wavg(v) is not None else None for k, v in me.items()},
        "lobby": {k: round(_wavg(v), 4) if _wavg(v) is not None else None for k, v in lob.items()},
        "opening": opening,
        "dist_m": round(st.median(dist) * 0.0254, 1) if dist else None,   # 1 game unit = 1 inch
        "per_demo": per_demo,
        "maps": [],
    }

    # maps: rank all from the Leetify history, deep-dive the most relevant ones that have demo deaths and a floor plan
    by_short = {_short(k): k for k in deaths_by_map}
    ranking = map_relevance(rows, {_short(k): v for k, v in deaths_by_map.items()})
    if not ranking:   # no Leetify rows: fall back to the maps you died on most in the demos
        ranking = [{"map": _short(k), "name": _short(k).capitalize(), "relevance": len(v), "demo_deaths": len(v)} for k, v in deaths_by_map.items()]
        ranking.sort(key=lambda x: -x["relevance"])
    for entry in ranking:
        full = by_short.get(entry["map"])
        entry["focus"] = False
        if len(out["maps"]) >= FOCUS_MAPS or not full or entry["demo_deaths"] < MAP_MIN_DEATHS or full not in ov_all:
            continue
        demos = [m["demo"] for m in index if m["map"] == full]
        view = map_view(full, ov_all[full], demos, deaths_by_map[full], kills_by_map.get(full, []))
        if not view:
            continue
        entry["focus"] = True
        out["maps"].append({"map": full, "name": entry["name"], "rounds": rounds_by_map.get(full, 0),
                            "matches": sum(1 for m in five if m["map"] == full), **view})
    out["ranking"] = ranking
    return out


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ROOT)
    import leetify_analyze
    sid = sys.argv[1] if len(sys.argv) > 1 else "76561198382673172"
    d = digest(sid, leetify_analyze.build_rows(sid))
    for r in d["ranking"]:
        print(f"{r['name']:10s} rel {r['relevance']:.3f}  {r.get('matches', '-')} matches  ADR {r.get('adr', '-')} vs {r.get('l_adr', '-')}  demo deaths {r['demo_deaths']}  {'FOCUS' if r['focus'] else ''}")
    for m in d["maps"]:
        print(m["name"], len(m["panels"]), "panels", sum(len(b["polys"]) for p in m["panels"] for b in p["bands"]), "polys",
              {k: len(v) for p in m["panels"] for k, v in p["sites"].items()}, len(m["deaths"]), "deaths", len(m["places"]), "places",
              len(json.dumps(m)) // 1024, "KB")
