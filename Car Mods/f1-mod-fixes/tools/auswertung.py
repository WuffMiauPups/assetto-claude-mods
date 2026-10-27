"""Quali-Auswertung aus Documents/Assetto Corsa/out/race_out.json, nur mit echten Runden.

  python auswertung.py                                  (Standardpfade unter Documents)
  python auswertung.py --real real_2010_barcelona.json  (echte Abstände je Fahrer zum Vergleich)

Was herausgefiltert wird:
- Hochgerechnete Runden: verlässt man die Session vorzeitig, schreibt AC Runden bis zum Ende weiter.
  Ab dort verbessern sich alle drei Sektoren je Runde um fast denselben Betrag (Differenzen <= 25 ms).
- Kopierte Runden: Fahrer ohne eigene volle Runde bekommen die Runde eines anderen, Sektoren nur um
  wenige ms versetzt. Verworfen wird die Kopie beim Auto mit weniger Einträgen.
- Runden über 150 s (Out-Laps, Unfälle) und Runden mehr als 3 % über der eigenen Bestzeit.
--real: JSON {"Webber": 0.0, "Hamilton": 0.31, ...}, Abstand in s zum Bezugsfahrer (--ref).
"""
import argparse
import json
import os
import re
import statistics as st
from pathlib import Path

DOCS = Path(os.environ.get("USERPROFILE", "~")).expanduser() / "Documents" / "Assetto Corsa"


def extrap_start(laps):
    for k in range(1, len(laps)):
        a, b = laps[k - 1], laps[k]
        if a["time"] > 0 and b["time"] > 0:
            dd = [y - x for x, y in zip(a["sectors"], b["sectors"])]
            if max(dd) - min(dd) <= 25 and max(abs(x) for x in dd) < 200:
                return k
    return len(laps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=str(DOCS / "out" / "race_out.json"))
    ap.add_argument("--ini", default=str(DOCS / "cfg" / "race.ini"))
    ap.add_argument("--session", type=int, default=0)
    ap.add_argument("--real"); ap.add_argument("--ref", help="Bezugsfahrer, Standard: schnellster")
    a = ap.parse_args()
    d = json.load(open(a.json, encoding="utf-8"))
    ini = open(a.ini, encoding="utf-8", errors="ignore").read()
    grid = {int(m.group(1)): dict(re.findall(r"^(\w+)=(.*)$", m.group(2), re.M)) for m in re.finditer(r"\[CAR_(\d+)\]([^\[]*)", ini)}
    s = d["sessions"][a.session]
    bycar = {}
    for lap in s["laps"]: bycar.setdefault(lap["car"], []).append(lap)
    real = {c: [l for l in L[:extrap_start(L)] if 0 < l["time"] < 150000] for c, L in bycar.items()}
    flat = [(c, l) for c, ls in real.items() for l in ls]
    drop = set()
    for c1, l1 in flat:
        for c2, l2 in flat:
            if c1 >= c2: continue
            dd = [x - y for x, y in zip(l1["sectors"], l2["sectors"])]
            if max(dd) - min(dd) <= 2 and abs(dd[0]) <= 30:
                drop.add((c1, id(l1)) if len(bycar[c1]) < len(bycar[c2]) else (c2, id(l2)))
    rows = []
    for i, p in enumerate(d["players"]):
        v = sorted(l["time"] for l in real.get(i, []) if (i, id(l)) not in drop)
        v = [t for t in v if t < v[0] * 1.03] if v else v
        g = grid.get(i, {})
        rows.append(dict(name=p["name"], car=p["car"], best=v[0] if v else None, top3=st.mean(v[:3]) if v else None,
                         n=len(v), ai=g.get("AI_LEVEL"), ballast=g.get("BALLAST"), restr=g.get("RESTRICTOR")))
    ok = [r for r in rows if r["best"]]
    ref = next((r["best"] for r in ok if a.ref and a.ref in r["name"]), min((r["best"] for r in ok if r["ai"]), default=0))
    realgap = json.load(open(a.real, encoding="utf-8")) if a.real else {}
    print(f"{s['name']}, {s.get('duration')} min, {d.get('track')}, {len(drop)} Kopien verworfen")
    for r in sorted(ok, key=lambda r: r["best"]) + [r for r in rows if not r["best"]]:
        if not r["best"]:
            print(f"  {r['name'][:20]:20s} {r['car']:26s} keine echte Runde"); continue
        gap = (r["best"] - ref) / 1000
        rg = next((v for k, v in realgap.items() if k in r["name"]), None)
        cmp_ = f" | real +{rg:.2f} Abw {gap - rg:+.2f}" if rg is not None else ""
        m, sx = divmod(r["best"] / 1000, 60)
        print(f"  {r['name'][:20]:20s} {r['car']:26s} {int(m)}:{sx:06.3f} {gap:+5.2f}  n={r['n']:2d} {r['ballast']}kg {r['restr']}% KI {r['ai']}{cmp_}")


if __name__ == "__main__":
    main()
