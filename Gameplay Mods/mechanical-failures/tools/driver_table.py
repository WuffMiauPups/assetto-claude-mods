"""Fahrer -> Konstrukteur pro Saison aus F1DB erzeugen (für Autos, deren Skins nach Fahrern heißen).

  python driver_table.py --f1db <ordner mit f1db-*.csv> [--years 1988 2026]

Quelle: https://github.com/f1db/f1db (Release-Asset f1db-csv.zip, Lizenz CC BY 4.0).
Ausgabe: research/data/drivers_by_season.json
  { "2013": { "vettel": "red-bull", "webber": "red-bull", ... }, ... }
Schlüssel sind Nachname, Nummer und Kürzel in Kleinbuchstaben ohne Sonderzeichen. Bei einem Fahrer mit
mehreren Teams in einer Saison zählt das Team mit den meisten Starts.
"""
import argparse
import collections
import csv
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^0-9a-z]", "", s.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--f1db", required=True)
    ap.add_argument("--years", nargs=2, type=int, default=[1988, 2026])
    a = ap.parse_args()
    src = Path(a.f1db)
    drivers = {r["id"]: r for r in csv.DictReader(open(src / "f1db-drivers.csv", encoding="utf-8"))}
    starts = collections.defaultdict(lambda: collections.Counter())   # (year, driverId) -> constructor -> starts
    numbers = {}
    for r in csv.DictReader(open(src / "f1db-races-race-results.csv", encoding="utf-8")):
        y = int(r["year"])
        if not (a.years[0] <= y <= a.years[1]):
            continue
        starts[(y, r["driverId"])][r["constructorId"]] += 1
        if r.get("driverNumber"):
            numbers[(y, r["driverId"])] = r["driverNumber"]
    out = {}
    for (y, did), cnt in starts.items():
        team = cnt.most_common(1)[0][0]
        d = drivers.get(did, {})
        keys = {norm(d.get("lastName")), norm(d.get("abbreviation")), norm(did)}
        full = norm(d.get("fullName"))
        if full:
            keys.add(full)
        keys.discard("")
        season = out.setdefault(str(y), {})
        for k in keys:
            if len(k) >= 3:
                # Nachnamen, die in einer Saison doppelt vorkommen (Schumacher 1997, Piquet 2008), nicht eindeutig zuordnen
                if k in season and season[k] != team:
                    season[k] = None
                else:
                    season.setdefault(k, team)
        num = numbers.get((y, did))
        if num:
            season.setdefault("nr" + num, team)
    for y in out:
        out[y] = {k: v for k, v in out[y].items() if v}
    dst = HERE.parent / "research" / "data" / "drivers_by_season.json"
    dst.write_text(json.dumps({"source": "f1db (CC BY 4.0)", "seasons": out}, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"{dst}: {len(out)} Saisons, {sum(len(v) for v in out.values())} Schlüssel")


if __name__ == "__main__":
    main()
