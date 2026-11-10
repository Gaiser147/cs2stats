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
GRID = 128            # cells across the 1024 px radar space
MAP_MIN_DEATHS = 25   # a map gets its own death map from this many deaths on
MAX_MAPS = 2


def _wavg(pairs):
    """Round-weighted mean of (value, rounds) pairs; None values are skipped."""
    pairs = [(v, w) for v, w in pairs if v is not None]
    tot = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / tot if tot else None


def _place(name):
    """'BombsiteA' -> 'Bombsite A', 'SnipersNest' -> 'Snipers Nest'."""
    return re.sub(r"(?<=[a-z])(?=[A-Z0-9])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name or "").strip()


# ---------- floor plan ----------

def _close(g, n):
    def morph(src, want):
        out = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                block = [src[a][b] for a in range(max(0, i - 1), min(n, i + 2)) for b in range(max(0, j - 1), min(n, j + 2))]
                out[i][j] = 1 if (any(block) if want else all(block)) else 0
        return out
    return morph(morph(g, True), False)


def _loops(g, n):
    """Boundary loops of filled cells along grid lines, filled side on the left (outer CCW in y-down)."""
    edges = {}
    filled = lambda i, j: 0 <= i < n and 0 <= j < n and g[i][j]
    for i in range(n):
        for j in range(n):
            if not g[i][j]:
                continue
            # vertices are (x, y) = (col, row); walk so the filled cell stays on one side
            if not filled(i - 1, j): edges.setdefault((j + 1, i), []).append((j, i))
            if not filled(i + 1, j): edges.setdefault((j, i + 1), []).append((j + 1, i + 1))
            if not filled(i, j - 1): edges.setdefault((j, i), []).append((j, i + 1))
            if not filled(i, j + 1): edges.setdefault((j + 1, i + 1), []).append((j + 1, i))
    loops = []
    while edges:
        start = next(iter(edges))
        loop, v = [start], start
        while True:
            nxt = edges[v].pop()
            if not edges[v]:
                del edges[v]
            if nxt == start:
                break
            loop.append(nxt)
            v = nxt
            if v not in edges:
                break
        loops.append(loop)
    return loops


def _area(loop):
    return abs(sum(loop[k][0] * loop[k - 1][1] - loop[k - 1][0] * loop[k][1] for k in range(len(loop)))) / 2


def _simplify(pts, tol):
    """Douglas-Peucker on an open polyline."""
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    ln = (dx * dx + dy * dy) ** .5 or 1e-9
    best, idx = -1, 0
    for k in range(1, len(pts) - 1):
        d = abs(dy * pts[k][0] - dx * pts[k][1] + x1 * y0 - y1 * x0) / ln
        if d > best:
            best, idx = d, k
    if best <= tol:
        return [pts[0], pts[-1]]
    return _simplify(pts[:idx + 1], tol)[:-1] + _simplify(pts[idx:], tol)


def _simplify_loop(loop, tol):
    far = max(range(len(loop)), key=lambda k: (loop[k][0] - loop[0][0]) ** 2 + (loop[k][1] - loop[0][1]) ** 2)
    a = _simplify(loop[:far + 1], tol)
    b = _simplify(loop[far:] + [loop[0]], tol)
    return a[:-1] + b[:-1]


def _floor(map_name, ov, demos):
    n, cnt, places = GRID, [[0] * GRID for _ in range(GRID)], {}
    lower = (ov.get("vertical_sections") or {}).get("lower")
    for d in demos:
        path = os.path.join(DEMOS, d, "positions.csv.gz")
        if not os.path.exists(path):
            continue
        with gzip.open(path, "rt", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                x, y, z = float(r["x"]), float(r["y"]), float(r["z"])
                if lower and z < lower["z_max"]:
                    continue
                px, py = (x - ov["pos_x"]) / ov["scale"], (ov["pos_y"] - y) / ov["scale"]
                i, j = int(py / 1024 * n), int(px / 1024 * n)
                if 0 <= i < n and 0 <= j < n:
                    cnt[i][j] += 1
                    if r.get("place"):
                        s = places.setdefault(r["place"], [0.0, 0.0, 0])
                        s[0] += px / 1024 * n; s[1] += py / 1024 * n; s[2] += 1
    g = _close([[1 if c else 0 for c in row] for row in cnt], n)
    loops = [lp for lp in _loops(g, n) if _area(lp) >= 6]
    loops = [_simplify_loop(lp, .85) for lp in loops]
    loops = [lp for lp in loops if len(lp) >= 3]
    xs = [p[0] for lp in loops for p in lp]
    ys = [p[1] for lp in loops for p in lp]
    box = (min(xs), min(ys), max(xs), max(ys))
    centroids = {k: (v[0] / v[2], v[1] / v[2]) for k, v in places.items() if v[2] >= 20}
    return loops, box, centroids


# ---------- digest ----------

def digest(steam64):
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
                    kills_by_map.setdefault(m["map"], []).append((float(r["attacker_x"]), float(r["attacker_y"]), float(r["attacker_z"])))
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

    ranked = sorted(deaths_by_map.items(), key=lambda kv: -len(kv[1]))
    for map_name, deaths in ranked[:MAX_MAPS]:
        ov = ov_all.get(map_name)
        if len(deaths) < MAP_MIN_DEATHS or not ov:
            continue
        demos = [m["demo"] for m in index if m["map"] == map_name]
        loops, (bx0, by0, bx1, by1), centroids = _floor(map_name, ov, demos)
        lower = (ov.get("vertical_sections") or {}).get("lower")
        pad = 2
        span = max(bx1 - bx0, by1 - by0) + 2 * pad
        ox, oy = (bx0 + bx1) / 2 - span / 2, (by0 + by1) / 2 - span / 2
        norm = lambda gx, gy: [round((gx - ox) / span * 1000), round((gy - oy) / span * 1000)]
        to_grid = lambda x, y: ((x - ov["pos_x"]) / ov["scale"] / 1024 * GRID, (ov["pos_y"] - y) / ov["scale"] / 1024 * GRID)
        dpts, counts = [], {}
        for x, y, z, s, op, place in deaths:
            if lower and z < lower["z_max"]:
                continue
            dpts.append(norm(*to_grid(x, y)) + [1 if s == "CT" else 0, 1 if op else 0])
            c = counts.setdefault(place, {"T": 0, "CT": 0})
            if s in c:
                c[s] += 1
        kpts = [norm(*to_grid(x, y)) for x, y, z in kills_by_map.get(map_name, []) if not (lower and z < lower["z_max"])]
        top = sorted(counts.items(), key=lambda kv: -(kv[1]["T"] + kv[1]["CT"]))
        labels = [{"name": _place(p), "t": c["T"], "ct": c["CT"], "at": norm(*centroids[p])} for p, c in top if p in centroids][:4]
        out["maps"].append({
            "map": map_name, "name": map_name.split("_", 1)[-1].capitalize(), "rounds": rounds_by_map.get(map_name, 0),
            "matches": sum(1 for m in five if m["map"] == map_name),
            "floor": [[norm(x, y) for x, y in lp] for lp in loops],
            "deaths": dpts, "kills": kpts, "labels": labels,
        })
    return out


if __name__ == "__main__":
    import sys
    d = digest(sys.argv[1] if len(sys.argv) > 1 else "76561198382673172")
    maps = d.pop("maps")
    print(json.dumps({k: v for k, v in d.items() if k != "per_demo"}, indent=1))
    for m in maps:
        print(m["name"], m["matches"], "matches", len(m["deaths"]), "deaths", len(m["kills"]), "kills",
              len(m["floor"]), "loops", sum(len(l) for l in m["floor"]), "pts", m["labels"])
