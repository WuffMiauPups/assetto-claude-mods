"""Echte Quali-Abstände je Team für alle Saisons aus F1DB (https://github.com/f1db/f1db, f1db-csv.zip, CC BY 4.0).

  py -3.11 quali_f1db.py --f1db <Ordner mit f1db-*.csv> [--jahre 1988 1993] [--runden 1 8]

Ergänzt quali_abstaende.py: die API dort hat vor 2003 kaum Quali-Zeiten. Gleiche Rechnung: je Rennen beste Runde des
Teams zur besten Runde aller Teams in Prozent, Median über die Saison, mal 0,85 (85-Sekunden-Runde).
Mit Q1/Q2/Q3-Spalten (ab 2006): Mittel aus "nur Q1" und "bestes aus Q1/Q2", Q3 zählt nicht (Rennsprit 2006 bis 2009).
Sonst die eine Quali-Zeit der Tabelle. 2003 bis 2005 wurde die gewertete Runde mit Rennsprit gefahren, die Abstände
dieser Jahre enthalten deshalb die Spritstrategie und sind unsicherer.
Schreibt alle Jahre nach ../data/quali_abstaende.json.
"""
import argparse
import csv
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent


def lade(f1db):
    rennen = {}
    with open(Path(f1db) / "f1db-races-qualifying-results.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rennen.setdefault((int(r["year"]), int(r["round"])), []).append(r)
    return rennen


def median_abstand(rennen, jahr, spalten, runden=None):
    gaps = {}
    for (y, rd), res in rennen.items():
        if y != jahr or (runden and not runden[0] <= rd <= runden[1]):
            continue
        best = {}
        for q in res:
            t = [int(q[s]) for s in spalten if q.get(s)]
            if t: best[q["constructorId"]] = min(best.get(q["constructorId"], 10 ** 9), min(t))
        if best:
            top = min(best.values())
            for c, t in best.items(): gaps.setdefault(c, []).append((t / top - 1) * 100)
    return {c: (st.median(v), len(v)) for c, v in gaps.items()}


def abstaende(rennen, jahr, runden=None):
    q1 = median_abstand(rennen, jahr, ["q1Millis"], runden)
    if len(q1) >= 5:
        both = median_abstand(rennen, jahr, ["q1Millis", "q2Millis"], runden)
        mean = {c: ((both[c][0] + q1[c][0]) / 2, both[c][1]) for c in both if c in q1}
    else:
        mean = median_abstand(rennen, jahr, ["timeMillis"], runden)
    if not mean: return {}
    base = min(v[0] for v in mean.values())
    return {c: [round((v[0] - base) * 0.85, 2), v[1]] for c, v in sorted(mean.items(), key=lambda kv: kv[1][0])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f1db", required=True); ap.add_argument("--jahre", nargs="*", type=int)
    ap.add_argument("--runden", nargs=2, type=int, help="nur Rennen von bis (Saisonphase), schreibt keine Datei")
    a = ap.parse_args()
    rennen = lade(a.f1db)
    alle = {str(j): abstaende(rennen, j, a.runden) for j in sorted({y for y, _ in rennen}) if j >= 1980}
    if not a.runden:
        (HERE.parent / "data" / "quali_abstaende.json").write_text(json.dumps(
            {"_quelle": "F1DB, tools/quali_f1db.py. Je Team [Abstand zum besten Team in s auf einer 85-s-Runde, Zahl der Rennen].", **alle},
            indent=1), encoding="utf-8")
    for j in a.jahre or []:
        print(j, "  ".join(f"{c} {v[0]:.2f}" for c, v in alle[str(j)].items()))


if __name__ == "__main__":
    main()
