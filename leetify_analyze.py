#!/usr/bin/env python3
"""Match-by-match CS2 analysis from the Leetify Public CS API.

Compares one player with their team and the rest of the lobby in every match:
rating, ADR, aim (accuracy, preaim, reaction time), utility and trades.

Usage:
  python3 leetify_analyze.py fetch  [STEAM64]   # download profile, match list and new match details
  python3 leetify_analyze.py report [STEAM64] [all|matches|summary]
  python3 leetify_analyze.py debrief [STEAM64]  # bake the data into debrief/index.html

Data is stored in data/leetify/<steam64>/. LEETIFY_API_KEY (environment or .env) is optional
and only raises the rate limit (https://leetify.com/app/developer).
Data Provided by Leetify - https://leetify.com
"""
import json
import os
import statistics as st
import sys
import time
import urllib.error
import urllib.request

API = "https://api-public.cs-prod.leetify.com"
ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STEAM64 = "76561198382673172"


# ---------- fetching ----------

def api_key():
    if os.environ.get("LEETIFY_API_KEY"):
        return os.environ["LEETIFY_API_KEY"]
    env = os.path.join(ROOT, ".env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.startswith("LEETIFY_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def get(path):
    headers = {"User-Agent": "cs2stats"}
    key = api_key()
    if key:
        headers["_leetify_key"] = key
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + path, headers=headers), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise


def data_dir(steam64):
    return os.path.join(ROOT, "data", "leetify", steam64)


def save(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")


def fetch(steam64):
    d = data_dir(steam64)
    save(os.path.join(d, "profile.json"), get(f"/v3/profile?steam64_id={steam64}"))
    history = get(f"/v3/profile/matches?steam64_id={steam64}")
    save(os.path.join(d, "history.json"), history)
    new = 0
    for m in history:
        path = os.path.join(d, "matches", f"{m['id']}.json")
        if os.path.exists(path):
            continue
        save(path, get(f"/v2/matches/{m['id']}"))
        new += 1
        time.sleep(1.5)
    print(f"{len(history)} matches in history, {new} new match details saved to {os.path.relpath(d, ROOT)}")


# ---------- analysis ----------

def g(p, k, default=0.0):
    v = p.get(k)
    return default if v is None else v


def adr(p):
    return g(p, "total_damage") / max(g(p, "rounds_count", 1), 1)


def util_per_round(p):
    thrown = sum(g(p, k) for k in ("flashbang_thrown", "he_thrown", "smoke_thrown", "molotov_thrown"))
    return thrown / max(g(p, "rounds_count", 1), 1)


def rank_of(players, key, steam64):
    order = sorted(players, key=key, reverse=True)
    return [p["steam64_id"] for p in order].index(steam64) + 1


def build_rows(steam64):
    folder = os.path.join(data_dir(steam64), "matches")
    if not os.path.isdir(folder):
        sys.exit(f"No data for {steam64}. Run: python3 leetify_analyze.py fetch {steam64}")
    matches = [json.load(open(os.path.join(folder, f), encoding="utf-8")) for f in os.listdir(folder) if f.endswith(".json")]
    matches.sort(key=lambda m: m["finished_at"])
    rows = []
    for m in matches:
        me = next((p for p in m["stats"] if p["steam64_id"] == steam64), None)
        if me is None:
            continue
        lobby = m["stats"]
        others = [p for p in lobby if p["steam64_id"] != steam64]
        team = [p for p in lobby if p["initial_team_number"] == me["initial_team_number"]]
        scores = {t["team_number"]: t["score"] for t in m["team_scores"]}
        my_s = scores.get(me["initial_team_number"], 0)
        op_s = max((v for k, v in scores.items() if k != me["initial_team_number"]), default=0)

        def lavg(fn):
            return st.mean(fn(p) for p in others) if others else 0.0

        rows.append(dict(
            date=m["finished_at"][:10],
            mode={"matchmaking": "premier", "matchmaking_competitive": "competitive", "matchmaking_wingman": "wingman"}.get(m["data_source"], m["data_source"]),
            map=m["map_name"].replace("de_", "").replace("cs_", ""),
            res="W" if my_s > op_s else "L" if my_s < op_s else "T", score=f"{my_s}-{op_s}",
            rounds=g(me, "rounds_count"), n_lobby=len(lobby), team_n=len(team),
            k=g(me, "total_kills"), d=g(me, "total_deaths"), a=g(me, "total_assists"),
            adr=adr(me), hs=g(me, "total_hs_kills") / max(g(me, "total_kills"), 1),
            rating=g(me, "leetify_rating") * 100, ct=g(me, "ct_leetify_rating") * 100, t=g(me, "t_leetify_rating") * 100,
            rk_lobby=rank_of(lobby, lambda p: g(p, "leetify_rating"), steam64),
            rk_team=rank_of(team, lambda p: g(p, "leetify_rating"), steam64),
            rk_adr=rank_of(lobby, adr, steam64),
            survived=g(me, "rounds_survived_percentage"),
            mk=sum(g(me, f"multi{i}k") for i in range(2, 6)),
            acc_spot=g(me, "accuracy_enemy_spotted"), acc_head=g(me, "accuracy_head"), spray=g(me, "spray_accuracy"),
            preaim=g(me, "preaim"), rt=g(me, "reaction_time") * 1000, cs=g(me, "counter_strafing_shots_good_ratio"),
            l_adr=lavg(adr), l_spot=lavg(lambda p: g(p, "accuracy_enemy_spotted")), l_head=lavg(lambda p: g(p, "accuracy_head")),
            l_preaim=lavg(lambda p: g(p, "preaim")), l_rt=lavg(lambda p: g(p, "reaction_time")) * 1000,
            fl=g(me, "flashbang_thrown"), fl_foe=g(me, "flashbang_hit_foe"), fl_friend=g(me, "flashbang_hit_friend"),
            fl_kill=g(me, "flashbang_leading_to_kill"), he=g(me, "he_thrown"), smoke=g(me, "smoke_thrown"), molly=g(me, "molotov_thrown"),
            util_pr=util_per_round(me), l_util_pr=lavg(util_per_round),
            uod=g(me, "utility_on_death_avg"), l_uod=lavg(lambda p: g(p, "utility_on_death_avg")),
            tk_opp=g(me, "trade_kill_opportunities"), tk_att=g(me, "trade_kill_attempts"), tk_ok=g(me, "trade_kills_succeed"),
            td_opp=g(me, "traded_death_opportunities"), td_ok=g(me, "traded_deaths_succeed"),
            ff=g(me, "shots_hit_friend"),
            # lobby (the other players in the match): per-round averages and summed counts for rates
            l_surv=lavg(lambda p: g(p, "rounds_survived_percentage")),
            l_fl_pr=lavg(lambda p: g(p, "flashbang_thrown") / max(g(p, "rounds_count", 1), 1)),
            l_fl_sum=sum(g(p, "flashbang_thrown") for p in others),
            l_fl_foe_sum=sum(g(p, "flashbang_hit_foe") for p in others),
            l_fl_friend_sum=sum(g(p, "flashbang_hit_friend") for p in others),
            l_tk_att_sum=sum(g(p, "trade_kill_attempts") for p in others),
            l_tk_ok_sum=sum(g(p, "trade_kills_succeed") for p in others),
        ))
    return rows


def f(v, n=1):
    return f"{v:.{n}f}"


def pc(v):
    return f"{v * 100:.0f}%"


def print_matches(rows):
    print("PER MATCH (rating x100 like leetify.com; rkL/rkT = rank by Leetify rating in lobby/team; lADR = lobby average without you)")
    print(f"{'date':10} {'mode':11} {'map':8} {'res':3} {'score':6} {'K-D-A':9} {'ADR':>5} {'lADR':>5} {'HS%':>4} {'rating':>7} {'CT':>6} {'T':>6} {'rkL':>5} {'rkT':>4} {'rkADR':>5} {'surv':>5} {'2k+':>3}")
    for r in rows:
        kda = f"{r['k']}-{r['d']}-{r['a']}"
        print(f"{r['date']:10} {r['mode']:11} {r['map']:8} {r['res']:3} {r['score']:6} {kda:9} {f(r['adr']):>5} {f(r['l_adr']):>5} {pc(r['hs']):>4} "
              f"{r['rating']:>+7.2f} {r['ct']:>+6.1f} {r['t']:>+6.1f} {str(r['rk_lobby']) + '/' + str(r['n_lobby']):>5} {str(r['rk_team']) + '/' + str(r['team_n']):>4} {r['rk_adr']:>5} {pc(r['survived']):>5} {r['mk']:>3}")

    print("\nAIM PER MATCH (l* = lobby average without you)")
    print(f"{'date':10} {'map':8} {'spot%':>6} {'lspot':>6} {'head%':>6} {'lhead':>6} {'spray':>6} {'preaim':>7} {'lpre':>6} {'RT ms':>6} {'lRT':>5} {'cstrf':>6}")
    for r in rows:
        print(f"{r['date']:10} {r['map']:8} {pc(r['acc_spot']):>6} {pc(r['l_spot']):>6} {pc(r['acc_head']):>6} {pc(r['l_head']):>6} {pc(r['spray']):>6} "
              f"{f(r['preaim']):>7} {f(r['l_preaim']):>6} {f(r['rt'], 0):>6} {f(r['l_rt'], 0):>5} {pc(r['cs']):>6}")

    print("\nUTILITY & TRADES PER MATCH (fFoe/fFr = enemies/teammates flashed, fK = flash led to kill, UoD = $ utility held on death)")
    print(f"{'date':10} {'map':8} {'rnd':>3} {'flash':>5} {'fFoe':>4} {'fFr':>4} {'fK':>3} {'HE':>3} {'smk':>3} {'mol':>3} {'u/rd':>5} {'l u/rd':>6} {'UoD$':>5} {'lUoD':>5} {'tradeK opp/att/ok':>18} {'tradedD opp/ok':>15} {'FF hits':>7}")
    for r in rows:
        tk = f"{r['tk_opp']:g}/{r['tk_att']:g}/{r['tk_ok']:g}"
        td = f"{r['td_opp']:g}/{r['td_ok']:g}"
        print(f"{r['date']:10} {r['map']:8} {r['rounds']:>3} {r['fl']:>5} {r['fl_foe']:>4} {r['fl_friend']:>4} {r['fl_kill']:>3} {r['he']:>3} {r['smoke']:>3} {r['molly']:>3} "
              f"{f(r['util_pr'], 2):>5} {f(r['l_util_pr'], 2):>6} {f(r['uod'], 0):>5} {f(r['l_uod'], 0):>5} {tk:>18} {td:>15} {r['ff']:>7}")


def print_summary(rows):
    fives = [r for r in rows if r["n_lobby"] >= 10]
    if not fives:
        print("No 5v5 matches.")
        return
    total_rounds = sum(r["rounds"] for r in fives)

    def wavg(key):
        return sum(r[key] * r["rounds"] for r in fives) / total_rounds

    print(f"\nSUMMARY over {len(fives)} 5v5 matches ({total_rounds} rounds), round-weighted: you vs lobby average")
    for key, lkey, label in [("adr", "l_adr", "ADR"), ("acc_spot", "l_spot", "accuracy (enemy spotted)"), ("acc_head", "l_head", "head accuracy"),
                             ("preaim", "l_preaim", "preaim (deg, lower is better)"), ("rt", "l_rt", "reaction time ms"),
                             ("util_pr", "l_util_pr", "utility thrown per round"), ("uod", "l_uod", "$ utility held on death")]:
        print(f"  {label:32} {wavg(key):8.3f}   lobby {wavg(lkey):8.3f}")
    for key, label in [("rating", "Leetify rating"), ("ct", "CT rating"), ("t", "T rating"), ("survived", "rounds survived"), ("cs", "counter-strafing")]:
        print(f"  {label:32} {wavg(key):8.3f}")
    kills = sum(r["k"] for r in fives)
    deaths = sum(r["d"] for r in fives)
    hs = sum(r["hs"] * r["k"] for r in fives) / max(kills, 1)
    print(f"  K/D {kills}/{deaths} = {kills / max(deaths, 1):.2f}, headshot kills {hs * 100:.0f}%")
    flashes = sum(r["fl"] for r in fives)
    print(f"  flashes {flashes} ({flashes / total_rounds:.2f}/round): enemies flashed {sum(r['fl_foe'] for r in fives)}, "
          f"teammates flashed {sum(r['fl_friend'] for r in fives)}, led to kill {sum(r['fl_kill'] for r in fives)}")
    print(f"  HE {sum(r['he'] for r in fives)}, smokes {sum(r['smoke'] for r in fives)}, molotovs {sum(r['molly'] for r in fives)}")
    tk_opp, tk_att, tk_ok = (sum(r[k] for r in fives) for k in ("tk_opp", "tk_att", "tk_ok"))
    td_opp, td_ok = (sum(r[k] for r in fives) for k in ("td_opp", "td_ok"))
    print(f"  trade kills: {tk_opp:g} chances, {tk_att:g} attempts ({tk_att / max(tk_opp, 1):.0%}), {tk_ok:g} traded ({tk_ok / max(tk_att, 1):.0%} of attempts)")
    print(f"  your deaths traded: {td_ok:g} of {td_opp:g} ({td_ok / max(td_opp, 1):.0%})")
    print(f"  lobby rank by rating: {[r['rk_lobby'] for r in fives]}")
    print(f"  team rank by rating:  {[r['rk_team'] for r in fives]}")

    def group(label, rs):
        w, l, t = (sum(r["res"] == x for r in rs) for x in "WLT")
        print(f"    {label:12} n={len(rs):<3} W-L-T {w}-{l}-{t}  rating {st.mean(r['rating'] for r in rs):+6.2f}  ADR {st.mean(r['adr'] for r in rs):5.1f}  team rank {st.mean(r['rk_team'] for r in rs):.1f}")

    print("  by mode (all matches):")
    for md in sorted({r["mode"] for r in rows}):
        group(md, [r for r in rows if r["mode"] == md])
    print("  by map (5v5):")
    for mp in sorted({r["map"] for r in fives}):
        group(mp, [r for r in fives if r["map"] == mp])
    print("  by result (5v5):")
    for res, label in (("W", "wins"), ("L", "losses"), ("T", "ties")):
        rs = [r for r in fives if r["res"] == res]
        if rs:
            group(label, rs)
    if len(fives) >= 4:
        mid = len(fives) // 2
        print("  trend (5v5, older half vs newer half):")
        for label, rs in (("older", fives[:mid]), ("newer", fives[mid:])):
            print(f"    {label:6} {rs[0]['date']}..{rs[-1]['date']}  rating {st.mean(r['rating'] for r in rs):+6.2f}  ADR {st.mean(r['adr'] for r in rs):5.1f}  "
                  f"preaim {st.mean(r['preaim'] for r in rs):4.1f}  head {st.mean(r['acc_head'] for r in rs) * 100:4.1f}%  util/round {st.mean(r['util_pr'] for r in rs):.2f}")


def build_debrief(steam64):
    """Bake the player's rows (own stats + lobby averages, no other players' names) into debrief/template.html."""
    rows = build_rows(steam64)
    profile = json.load(open(os.path.join(data_dir(steam64), "profile.json"), encoding="utf-8"))
    data = {
        "steam64": steam64,
        "matches": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()} for r in rows],
        "profile": {k: profile.get(k) for k in ("name", "winrate", "total_matches", "first_match_date", "ranks", "rating", "stats")},
    }
    template = os.path.join(ROOT, "debrief", "template.html")
    out = os.path.join(ROOT, "debrief", "index.html")
    html = open(template, encoding="utf-8").read()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html.replace("__DATA__", payload))
    print(f"Debrief with {len(rows)} matches written to {os.path.relpath(out, ROOT)}")


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("fetch", "report", "debrief"):
        sys.exit(__doc__)
    steam64 = next((a for a in args[1:] if a.isdigit() and len(a) == 17), DEFAULT_STEAM64)
    if args[0] == "fetch":
        fetch(steam64)
        return
    if args[0] == "debrief":
        build_debrief(steam64)
        return
    section = next((a for a in args[1:] if a in ("all", "matches", "summary")), "all")
    rows = build_rows(steam64)
    if section in ("all", "matches"):
        print_matches(rows)
    if section in ("all", "summary"):
        print_summary(rows)
    print(f"\nData Provided by Leetify - View on Leetify: https://leetify.com/app/profile/{steam64}")


if __name__ == "__main__":
    main()
