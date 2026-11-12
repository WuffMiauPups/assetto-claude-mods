"""Teamstärke der Team-Autos (team_autos.py) über Motor und Abtrieb einstellen.

  python team_staerke.py --ac <AC> --plan ../data/teams_2017.json            (zeigt nur die Rechnung)
  python team_staerke.py --ac <AC> --plan ../data/teams_2017.json --apply

Das beste Team behält die Werte der Quelle. Für die anderen gilt:
  Leistung:  Gesamtleistung im Verhältnis der geschätzten PS. Skaliert wird nur power.lut (Verbrenner),
             der Elektroanteil (ers_ps) bleibt, deshalb fällt der Faktor der Kurve etwas größer aus.
  Abtrieb:   (echter Abstand - Zeitverlust durch den Motor) / s_pro_prozent_abtrieb, als Faktor auf alle CL_GAIN.
             Die Balance bleibt, der Luftwiderstand auch.
Gerechnet wird immer von den Dateien der Quelle aus, mehrfaches Anwenden summiert nichts auf.
Die Empfindlichkeiten stammen von den V8-Jahrgängen und sind Schätzungen.
"""
import argparse
import json
import math
import re
from pathlib import Path

from acdini import CarData, get_value, set_value

ZEILE = re.compile(r"(?m)^([ \t]*\d+(?:\.\d+)?[ \t]*\|[ \t]*)(-?\d+(?:\.\d+)?)")


def ice_ps(cd):
    """Spitzenleistung des Verbrenners: power.lut mal (1 + Ladedruck aus dem Turbo-Regler)."""
    boost = [(float(a), float(b)) for a, b in re.findall(r"(\d+)=([\d.]+)", get_value(cd.read("ctrl_turbo0.ini"), "CONTROLLER_0", "LUT"))]
    def b(rpm):
        for (r0, v0), (r1, v1) in zip(boost, boost[1:]):
            if r0 <= rpm <= r1: return v0 + (v1 - v0) * (rpm - r0) / (r1 - r0)
        return boost[-1][1]
    lim = float(get_value(cd.read("engine.ini"), "ENGINE_DATA", "LIMITER"))
    return max(float(r) * float(t) * (1 + b(float(r))) for r, t in re.findall(r"(?m)^\s*(\d+)\|([\d.]+)", cd.read("power.lut")) if float(r) <= lim) * 2 * math.pi / 60 / 735.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True); ap.add_argument("--plan", required=True); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    plan = json.load(open(a.plan, encoding="utf-8"))
    e, teams, quelle = plan["empfindlichkeit"], plan["teams"], plan["quelle"]
    cars = Path(a.ac) / "content" / "cars"
    src = CarData(cars / quelle)
    aero, power, ice = src.read("aero.ini"), src.read("power.lut"), ice_ps(src)
    best = min(teams.values(), key=lambda t: t["abstand"])
    print(f"Quelle {quelle}: Verbrenner {ice:.0f} PS + {e['ers_ps']} PS elektrisch")
    for key, t in sorted(teams.items(), key=lambda kv: kv[1]["abstand"]):
        minus_ps = (1 - t["ps"] / best["ps"]) * 100
        f_lut = 1 - minus_ps / 100 * (ice + e["ers_ps"]) / ice
        s_motor = minus_ps * e["s_pro_prozent_leistung"]
        f_cl = 1 - (t["abstand"] - best["abstand"] - s_motor) / e["s_pro_prozent_abtrieb"] / 100
        cd = CarData(cars / f"{quelle}_{key}")
        new_aero = aero
        for sec in re.findall(r"(?m)^\[(WING_\d+)\]", aero):
            v = float(get_value(aero, sec, "CL_GAIN") or 0)
            if v: new_aero, _ = set_value(new_aero, sec, "CL_GAIN", f"{v * f_cl:.4f}")
        new_power = ZEILE.sub(lambda m: m.group(1) + f"{float(m.group(2)) * f_lut:.4f}", power)
        if a.apply:
            if cd.read("aero.ini") != new_aero: cd.write("aero.ini", new_aero)
            if cd.read("power.lut") != new_power: cd.write("power.lut", new_power)
        print(f"{key:11s} +{t['abstand']:.2f} s  {t['ps']} PS (Motor {s_motor:.2f} s)  power.lut x{f_lut:.4f}  CL_GAIN x{f_cl:.4f}" + ("" if a.apply else "  [Trockenlauf]"))


if __name__ == "__main__":
    main()
