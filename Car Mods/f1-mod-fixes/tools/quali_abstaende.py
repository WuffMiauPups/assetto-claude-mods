"""Echte Quali-Abstände je Team einer Saison aus der Ergast-kompatiblen API (api.jolpi.ca).

  python quali_abstaende.py 2008

Je Rennen: beste Runde des Teams zur besten Runde aller Teams in Prozent, davon der Median über die Saison.
Gemittelt werden zwei Rechnungen: nur Q1 (die Spitze fährt dort nicht immer voll) und bestes aus Q1/Q2
(Teams, die in Q1 ausscheiden, fehlt die Streckenentwicklung). Q3 zählt nicht, 2008 und 2009 wurde dort
mit Rennsprit gefahren. Ausgabe in Sekunden, umgerechnet auf eine 85-Sekunden-Runde.
"""
import argparse
import json
import statistics as st
import time
import urllib.request

API = "https://api.jolpi.ca/ergast/f1/{}/qualifying.json?limit=100&offset={}"


def fetch(year):
    rounds, off = {}, 0
    while True:
        req = urllib.request.Request(API.format(year, off), headers={"User-Agent": "lap-analysis"})
        d = json.load(urllib.request.urlopen(req, timeout=30))["MRData"]
        for r in d["RaceTable"]["Races"]: rounds.setdefault(r["round"], []).extend(r["QualifyingResults"])
        off += int(d["limit"])
        if off >= int(d["total"]): return rounds
        time.sleep(0.5)


def seconds(t):
    if not t: return None
    m, s = t.split(":")
    return int(m) * 60 + float(s)


def medians(rounds, sessions):
    gaps = {}
    for res in rounds.values():
        best = {}
        for q in res:
            times = [seconds(q.get(s)) for s in sessions if q.get(s)]
            if times:
                c = q["Constructor"]["constructorId"]
                best[c] = min(best.get(c, 1e9), min(times))
        if best:
            top = min(best.values())
            for c, t in best.items(): gaps.setdefault(c, []).append((t / top - 1) * 100)
    return {c: (st.median(v), len(v)) for c, v in gaps.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jahr", type=int)
    a = ap.parse_args()
    rounds = fetch(a.jahr)
    both, q1 = medians(rounds, ["Q1", "Q2"]), medians(rounds, ["Q1"])
    mean = {c: (both[c][0] + q1[c][0]) / 2 for c in both}
    base = min(mean.values())
    print(f"{a.jahr}, {len(rounds)} Rennen, Abstand zum besten Team in s (85-s-Runde)")
    for c in sorted(mean, key=mean.get):
        print(f"  {c:14s} {(mean[c] - base) * 0.85:5.2f}   ({both[c][1]} Rennen)")


if __name__ == "__main__":
    main()
