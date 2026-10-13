"""Ausfallquoten pro F1-Saison aus F1DB berechnen und Ära-Profile erzeugen.

  python failure_stats.py --csv pfad/zu/f1db-races-race-results.csv [--years 1988 2025]

Quelle: https://github.com/f1db/f1db (Release-Asset f1db-csv.zip, Lizenz CC BY 4.0).
Ausgabe: research/data/failure_rates.json, research/data/failure_rates.md, profiles/failures_<year>.ini
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Zuordnung reasonRetired -> Kategorie des Scripts. Nicht-mechanische Gründe -> None.
CATEGORY = {
    "ENGINE": ["Engine", "Power unit", "Oil leak", "Oil pressure", "Oil pump", "Camshaft", "Fire", "Exhaust", "Valve",
               "Piston", "Con rod", "Crankshaft", "Ignition", "Spark plugs", "Engine fire", "Distributor", "Oil line", "Airbox"],
    "POWER_LOSS": ["Power loss", "Throttle", "Fuel pressure", "Fuel system", "Fuel pump", "Fuel leak", "Fuel", "Out of fuel",
                   "Fuel rig", "Injection", "Fuel injection", "Misfire"],
    "TURBO": ["Turbo", "Turbocharger", "Supercharger", "Pneumatics"],
    "GEARBOX": ["Gearbox", "Transmission", "Clutch", "Differential", "Drivetrain", "Driveshaft", "Halfshaft", "Launch control"],
    "HYDRAULICS": ["Hydraulics", "Steering", "Power steering", "Brake bias"],
    "ELECTRICS": ["Electrical", "Electronics", "Alternator", "Battery", "Wiring", "Sensor", "ECU", "Technical defect", "Mechanical",
                  "Mechenical", "Traction control", "KERS failure", "Energy storage system failure", "Hybrid system"],
    "BRAKES": ["Brakes", "Brake"],
    "PUNCTURE": ["Puncture", "Tyre", "Puncture damage", "Wheel", "Wheel nut", "Loose wheel", "Wheel rim", "Wheel bearing"],
    "SUSPENSION": ["Suspension", "Vibrations", "Handling", "Chassis", "Undertray", "Rear wing", "Front wing", "Broken wing", "Track rod", "Broken floor"],
    "COOLING": ["Overheating", "Water leak", "Water pressure", "Radiator", "Water pump", "Coolant leak", "Cooling system"],
}
LOOKUP = {r.lower(): cat for cat, rs in CATEGORY.items() for r in rs}
NON_MECH = {"collision", "accident", "spun off", "collision damage", "withdrew", "spin", "accident damage", "injury",
            "unwell", "safety concerns", "ignored red light", "car underweight", "illegal skid block wear",
            "illegal brake ducts", "illegal rear wing", "illegal car change", "illegal bodywork", "safety belt",
            "push start", "accident in qualifying", "accident in warm-up", "disqualified", "did not start",
            "excluded", "not classified", "retired", "retirement", "driver unwell", "black flag", "failed scrutineering",
            "missed weight check", "unfit", "physical", "ignored black flag", "reversed in pits", "received outside assistance",
            "injury in practice", "failed to serve stop-go penalty", "car damaged", "ignored yellow flags in practice",
            "ignored blue flags", "misled stewards", "illness", "car damaged in qualifying", "pit stop issue"}


def classify(reason: str) -> str | None:
    r = reason.strip().lower()
    if not r:
        return None
    if r in LOOKUP:
        return LOOKUP[r]
    if r in NON_MECH:
        return None
    for key, cat in LOOKUP.items():
        if key in r:
            return cat
    return "OTHER" if not any(w in r for w in ("collision", "accident", "spun", "crash", "illegal", "disqual")) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--years", nargs=2, type=int, default=[1988, 2025])
    a = ap.parse_args()
    rows = list(csv.DictReader(open(a.csv, encoding="utf-8")))
    y0, y1 = a.years
    rows = [r for r in rows if y0 <= int(r["year"]) <= y1 and r["sharedCar"] != "true"]

    per_year = collections.defaultdict(lambda: {"starts": 0, "races": set(), "cats": collections.Counter(), "unmapped": collections.Counter()})
    per_engine = collections.defaultdict(lambda: {"starts": 0, "mech": 0, "engine": 0})
    per_team = collections.defaultdict(lambda: {"starts": 0, "mech": 0})
    for r in rows:
        y = int(r["year"])
        if r["positionText"] in ("DNS", "DNQ", "DNPQ", "EX", "NC") and not r["reasonRetired"]:
            if r["positionText"] in ("DNS", "DNQ", "DNPQ"):
                continue
        d = per_year[y]
        d["starts"] += 1
        d["races"].add(r["round"])
        cat = classify(r["reasonRetired"])
        ek, tk = (y, r["engineManufacturerId"]), (y, r["constructorId"])
        per_engine[ek]["starts"] += 1
        per_team[tk]["starts"] += 1
        if cat:
            d["cats"][cat] += 1
            per_engine[ek]["mech"] += 1
            per_team[tk]["mech"] += 1
            if cat in ("ENGINE", "TURBO", "POWER_LOSS"):
                per_engine[ek]["engine"] += 1
            if cat == "OTHER":
                d["unmapped"][r["reasonRetired"]] += 1

    cats = list(CATEGORY) + ["OTHER"]
    out = {"source": "f1db (CC BY 4.0)", "years": {}, "engine_manufacturers": {}, "constructors": {}}
    md = ["# Ausfallquoten F1 pro Saison (Prozent der Starts, mechanisch)", "",
          "Quelle: F1DB. Ein Wert ist die Wahrscheinlichkeit pro Auto und Rennen in Prozent.", "",
          "| Jahr | Starts | mech. gesamt | " + " | ".join(c.title() for c in cats) + " |",
          "|---|---|---|" + "---|" * len(cats)]
    for y in sorted(per_year):
        d = per_year[y]
        n = d["starts"]
        rates = {c: round(100 * d["cats"][c] / n, 2) for c in cats}
        total = round(100 * sum(d["cats"].values()) / n, 2)
        out["years"][y] = {"starts": n, "races": len(d["races"]), "mechanical_total_pct": total, "rates_pct": rates,
                           "unmapped": dict(d["unmapped"])}
        md.append(f"| {y} | {n} | {total} | " + " | ".join(f"{rates[c]}" for c in cats) + " |")
    md += ["", "## Motorhersteller mit auffälliger Quote (Anteil Motor-, Turbo-, Kraftstoffausfälle an Starts)", "",
           "| Jahr | Hersteller | Starts | mech. gesamt % | Motor % | Faktor gegenüber Saisonschnitt |", "|---|---|---|---|---|---|"]
    for (y, e), v in sorted(per_engine.items()):
        if v["starts"] < 10:
            continue
        season_engine = sum(per_year[y]["cats"][c] for c in ("ENGINE", "TURBO", "POWER_LOSS")) / per_year[y]["starts"]
        rate = v["engine"] / v["starts"]
        factor = round(rate / season_engine, 2) if season_engine else None
        out["engine_manufacturers"][f"{y}:{e}"] = {"starts": v["starts"], "mech_pct": round(100 * v["mech"] / v["starts"], 2),
                                                   "engine_pct": round(100 * rate, 2), "factor": factor}
        if factor and (factor >= 1.6 or factor <= 0.5):
            md.append(f"| {y} | {e} | {v['starts']} | {100 * v['mech'] / v['starts']:.1f} | {100 * rate:.1f} | {factor} |")
    for (y, t), v in sorted(per_team.items()):
        if v["starts"] >= 10:
            season = sum(per_year[y]["cats"].values()) / per_year[y]["starts"]
            out["constructors"][f"{y}:{t}"] = {"starts": v["starts"], "mech_pct": round(100 * v["mech"] / v["starts"], 2),
                                               "factor": round((v["mech"] / v["starts"]) / season, 2) if season else None}

    data = ROOT / "research" / "data"; data.mkdir(parents=True, exist_ok=True)
    (data / "failure_rates.json").write_text(json.dumps(out, indent=1))
    (data / "failure_rates.md").write_text("\n".join(md) + "\n")

    prof = ROOT / "profiles"; prof.mkdir(exist_ok=True)
    for y, v in out["years"].items():
        r = v["rates_pct"]
        lines = ["; Automatisch aus F1DB erzeugt: Prozent pro Auto und Rennen, Saison " + str(y),
                 f"; Starts {v['starts']}, Rennen {v['races']}, mechanische Ausfälle gesamt {v['mechanical_total_pct']} Prozent",
                 "[GLOBAL]", f"SEED={y}-01", "RACE_LENGTH_MIN=90", "MULT_ALL=1.0", "LOG=1", "", "[ERA]"]
        for c in ("ENGINE", "POWER_LOSS", "TURBO", "GEARBOX", "HYDRAULICS", "ELECTRICS", "BRAKES", "PUNCTURE", "SUSPENSION", "COOLING"):
            lines.append(f"{c}={r.get(c, 0)}")
        lines += ["", "[DRIVER_default]", "ENGINE_MULT=1.0", "TURBO_MULT=1.0", "GEARBOX_MULT=1.0", "ENGINE_MILEAGE_KM=0", ""]
        (prof / f"failures_{y}.ini").write_text("\n".join(lines))
    print("\n".join(md[:6] + md[6 + (1996 - y0):6 + (1996 - y0) + 30]))
    print(f"\nProfile: {len(out['years'])} Dateien in {prof}")


if __name__ == "__main__":
    main()
