"""GP2-Profile aus research/data/gp2_retirements.json erzeugen.

  py -3.11 tools/gp2_profiles.py

Schreibt profiles/failures_gp2_<jahr>.ini (Prozent pro Auto und Rennen, Bezug: mittlere Renndauer der Saison)
und research/data/gp2_rates.json (Teamfaktor pro Saison, Zuordnung in der App über den Skin-Namen).
"""
import json
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
SRC = MOD / "research" / "data" / "gp2_retirements.json"
CATS = ("ENGINE", "POWER_LOSS", "TURBO", "GEARBOX", "HYDRAULICS", "ELECTRICS", "BRAKES", "PUNCTURE", "SUSPENSION", "COOLING")
# STALL (Abwürgen am Start), ACCIDENT und UNKNOWN zählen nicht; die App würfelt nur Defekte während der Fahrt
MAP = {}
# Häufungen dämpfen: höchstens so viele Ausfälle derselben Kategorie pro Rennen (Imola 2005: je 5 Bremsausfälle
# am ersten Wochenende, danach kaum noch). Schätzung, siehe research/gp2-ausfallstatistik.md
MAX_SAME_PER_RACE = 3
# Skin-Namen der sr_gp2-Mods, die nicht den Teamschlüssel enthalten
ALIASES = {"FMS": ["Pofms", "PetrolOfisi"], "Piquet": ["PiquetSports"], "RacingEngineering": ["RacingEng"],
           "SuperNova": ["Supernova"], "DPR": ["DavidPrice"], "BCN": ["BCNCompeticion"]}
# Schrumpfung kleiner Stichproben zum Saisonmittel: so viele "virtuelle" Starts mit Durchschnittsquote (Schätzung)
PRIOR_STARTS = 20


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    rates = {}
    for year, d in sorted(data.items()):
        races = d["races"]
        starts = sum(r["starters"] for r in races)
        durations = [r["duration_min"] for r in races if r.get("duration_min")]
        avg_min = round(sum(durations) / len(durations)) if durations else 45
        cats = {c: 0 for c in CATS}
        team_mech = {}
        per_race = {}
        for r in d["retirements"]:
            c = MAP.get(r["category"], r["category"])
            key = (r["race_index"], c)
            per_race[key] = per_race.get(key, 0) + 1
            if c in cats and per_race[key] <= MAX_SAME_PER_RACE:
                cats[c] += 1
                team_mech[r["team"]] = team_mech.get(r["team"], 0) + 1
        mech = sum(cats.values())
        season_rate = mech / starts
        lines = [f"; Erzeugt mit tools/gp2_profiles.py aus research/data/gp2_retirements.json, GP2 {year}",
                 f"; Starts {starts}, Rennen {len(races)}, mechanische Ausfälle {mech} ({100 * season_rate:.2f} Prozent)",
                 f"; RACE_LENGTH_MIN = mittlere Renndauer Haupt- und Sprintrennen",
                 "[GLOBAL]", f"SEED={year}-01", f"RACE_LENGTH_MIN={avg_min}", "MULT_ALL=1.0", "LOG=1", "", "[ERA]"]
        lines += [f"{c}={100 * cats[c] / starts:.2f}" for c in CATS]
        lines += ["", "[DRIVER_default]", "ENGINE_MULT=1.0", "TURBO_MULT=1.0", "GEARBOX_MULT=1.0", "ENGINE_MILEAGE_KM=0", ""]
        (MOD / "profiles" / f"failures_gp2_{year}.ini").write_text("\n".join(lines), encoding="utf-8")

        teams = {}
        for team, n in d["team_starts"].items():
            m = team_mech.get(team, 0)
            shrunk = (m + PRIOR_STARTS * season_rate) / (n + PRIOR_STARTS)
            teams[team] = {"starts": n, "mech": m, "factor": round(shrunk / season_rate, 2) if season_rate else 1.0,
                           "aliases": ALIASES.get(team, [])}
        rates[year] = teams
        print(f"GP2 {year}: {starts} Starts, {mech} mechanisch ({100 * season_rate:.1f} %), Renndauer {avg_min} min")
        for t, v in sorted(teams.items(), key=lambda kv: -kv[1]["factor"]):
            print(f"  {t:18s} {v['mech']:2d}/{v['starts']:3d}  Faktor {v['factor']:.2f}")
    out = MOD / "research" / "data" / "gp2_rates.json"
    out.write_text(json.dumps(rates, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
