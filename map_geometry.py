#!/usr/bin/env python3
"""Floor plans for the debrief from the maps' navigation meshes.

Downloads navs.zip from an awpy-data release (https://github.com/pnxenopoulos/awpy-data, the nav meshes
the awpy project publishes), reads the walkable polygons of each map and writes them to
data/maps/geometry/<map>.json: one polygon per nav area, corners as integer game units, plus the mean
height. Only coordinates are kept; no radar image, texture or other artwork.

Usage:
  python3 map_geometry.py            # latest release, all de_ and cs_ maps that have a radar transform
  python3 map_geometry.py 2000942    # a specific awpy-data release

Standard library only. The geometry changes only when Valve edits a map, so run it after map updates.
"""
import io
import json
import math
import os
import struct
import sys
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = "pnxenopoulos/awpy-data"
FALLBACK_VERSION = "2000942"
OUT = os.path.join(ROOT, "data", "maps", "geometry")


def latest_version():
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/releases/latest",
                                     headers={"User-Agent": "cs2stats", "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["tag_name"]
    except Exception as e:  # rate limit or no API access: fall back to a known release
        print(f"latest release unknown ({e}), using {FALLBACK_VERSION}")
        return FALLBACK_VERSION


def _corner_table(b):
    """Offset and size of the corner table: the first run of plausible float triples after the header."""
    def plausible(off, n):
        for k in range(min(n, 50)):
            v = struct.unpack_from("<fff", b, off + k * 12)
            if not all(math.isfinite(t) and abs(t) < 40000 for t in v):
                return False
        return True
    for off in range(16, 4000):
        n = struct.unpack_from("<I", b, off)[0]
        if 50 < n < 500000 and off + 4 + n * 12 < len(b) and plausible(off + 4, n):
            return off, n
    raise ValueError("no corner table found")


def parse_nav(b):
    """Polygons of a CS2 .nav file (versions 35 and 36): shared corner table, then polygons as corner indices."""
    magic, version = struct.unpack_from("<II", b, 0)
    if magic != 0xFEEDFACE:
        raise ValueError("not a nav file")
    off, n = _corner_table(b)
    corners = [struct.unpack_from("<fff", b, off + 4 + k * 12) for k in range(n)]
    p = off + 4 + n * 12
    count = struct.unpack_from("<I", b, p)[0]
    p += 4
    polys = []
    for _ in range(count):
        cn = b[p]
        p += 1
        idx = struct.unpack_from(f"<{cn}I", b, p)
        p += 4 * cn + 4          # corner indices, then one unknown field per polygon
        if any(i >= n for i in idx):
            raise ValueError("corner index out of range")
        polys.append([corners[i] for i in idx])
    return version, polys


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else latest_version()
    url = f"https://github.com/{REPO}/releases/download/{version}/navs.zip"
    print("downloading", url)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "cs2stats"}), timeout=120) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    overviews = json.load(open(os.path.join(ROOT, "data", "maps", "overviews.json"), encoding="utf-8"))["maps"]
    os.makedirs(OUT, exist_ok=True)
    for name in sorted(z.namelist()):
        map_name = os.path.splitext(os.path.basename(name))[0]
        if not name.endswith(".nav") or map_name not in overviews or not map_name.startswith(("de_", "cs_")) or map_name.endswith("_night"):
            continue
        try:
            nav_version, polys = parse_nav(z.read(name))
        except ValueError as e:
            print(f"  {map_name}: skipped ({e})")
            continue
        out = {
            "map": map_name, "source": f"nav mesh, awpy-data release {version} (nav version {nav_version})",
            "polys": [[c for x, y, _ in p for c in (round(x), round(y))] for p in polys],
            "z": [round(sum(c[2] for c in p) / len(p)) for p in polys],
        }
        with open(os.path.join(OUT, map_name + ".json"), "w", encoding="utf-8") as f:
            json.dump(out, f, separators=(",", ":"))
        print(f"  {map_name}: {len(polys)} areas")


if __name__ == "__main__":
    main()
