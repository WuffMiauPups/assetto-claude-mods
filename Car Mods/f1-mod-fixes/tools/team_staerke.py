"""Teamstärke über Motor, Abtrieb und Luftwiderstand einstellen (Plan-Datei in data/).

  python team_staerke.py --ac <AC> --plan ../data/teams_2017.json            (zeigt nur die Rechnung)
  python team_staerke.py --ac <AC> --plan ../data/teams_2023.json --apply

Zwei Arten von Plänen:
  "quelle" im Plan   Team-Autos aus team_autos.py (<quelle>_<team>), gerechnet wird von den Dateien der Quelle aus.
  "ordner" je Team   Autos, die schon eigene Ordner haben (ACFL 2023). Basis ist data.acd.bak im Ordner, also der
                     Zustand vor der ersten Änderung; solange es keine gibt, die aktuelle data.acd.
Mehrfaches Anwenden summiert deshalb nichts auf.

Das beste Team ist der Bezug. Für die anderen gilt:
  Leistung:  Gesamtleistung im Verhältnis der geschätzten PS. Ohne "ers_mitskalieren" wird nur power.lut (Verbrenner)
             skaliert und der Elektroanteil "ers_ps" bleibt, der Faktor der Kurve fällt dann etwas größer aus.
             Mit "ers_mitskalieren" bekommen power.lut und kers_torque.lut denselben Faktor.
  Abtrieb:   (echter Abstand - Zeitverlust durch Motor und Luftwiderstand) / s_pro_prozent_abtrieb, als Faktor auf
             alle CL_GAIN. Die Balance bleibt. "cl" im Plan setzt den Faktor fest (Wunschauto, Nachstellen nach Test).
  Luftwiderstand: "cd" im Plan als Faktor auf alle CD_GAIN (Autokonzept).
Optional: "masse" setzt TOTALMASS bei allen, "angleichen" übernimmt einzelne Dateien vom Referenz-Team.
Alle Empfindlichkeiten und PS-Werte sind Schätzungen.
"""
import argparse
import json
import math
import re
from pathlib import Path

from acdini import CarData, acd_read, get_value, set_value

ZEILE = re.compile(r"(?m)^([ \t]*\d+(?:\.\d+)?[ \t]*\|[ \t]*)(-?\d+(?:\.\d+)?)")


class Bak:
    """Liest die Dateien aus data.acd.bak (gleicher Schlüssel wie data.acd, weil derselbe Ordner)."""

    def __init__(self, cardir):
        self.f = {n.lower(): c for n, c in acd_read(Path(cardir) / "data.acd.bak")[1]}

    def read(self, name):
        c = self.f.get(name.lower())
        return c.decode("latin1") if c is not None else None


def basis(cardir):
    return Bak(cardir) if (Path(cardir) / "data.acd.bak").is_file() else CarData(cardir)


def ice_ps(cd):
    """Spitzenleistung des Verbrenners: power.lut mal (1 + Ladedruck aus dem Turbo-Regler, höchstens MAX_BOOST)."""
    en = cd.read("engine.ini")
    cap = float(get_value(en, "TURBO_0", "MAX_BOOST") or 0)
    boost = [(float(a), float(b)) for a, b in re.findall(r"(\d+)=([\d.]+)", get_value(cd.read("ctrl_turbo0.ini") or "", "CONTROLLER_0", "LUT") or "")]
    def b(rpm):
        for (r0, v0), (r1, v1) in zip(boost, boost[1:]):
            if r0 <= rpm <= r1: return min(cap, v0 + (v1 - v0) * (rpm - r0) / (r1 - r0))
        return min(cap, boost[-1][1]) if boost else cap
    lim = float(get_value(en, "ENGINE_DATA", "LIMITER"))
    return max(float(r) * float(t) * (1 + b(float(r))) for r, t in re.findall(r"(?m)^\s*(\d+)\|([\d.]+)", cd.read("power.lut")) if float(r) <= lim) * 2 * math.pi / 60 / 735.5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True); ap.add_argument("--plan", required=True); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    plan = json.load(open(a.plan, encoding="utf-8"))
    e, teams, quelle = plan["empfindlichkeit"], plan["teams"], plan.get("quelle")
    cars = Path(a.ac) / "content" / "cars"
    ordner = lambda key: cars / teams[key].get("ordner", f"{quelle}_{key}")
    best = min((t for t in teams.values() if "abstand" in t), key=lambda t: t["abstand"])
    gleich = plan.get("angleichen")
    ref = basis(ordner(gleich["referenz"])) if gleich else None
    for key, t in sorted(teams.items(), key=lambda kv: kv[1].get("abstand", 99)):
        src = CarData(cars / quelle) if quelle else basis(ordner(key))
        neu = {}                                                    # Dateiname -> neuer Inhalt
        for f in (gleich["dateien"] if gleich else []): neu[f] = ref.read(f)
        minus_ps = (1 - t["ps"] / best["ps"]) * 100
        if plan.get("ers_mitskalieren"):
            f_lut = t["ps"] / best["ps"]
            neu["kers_torque.lut"] = ZEILE.sub(lambda m: m.group(1) + f"{float(m.group(2)) * f_lut:.4f}", src.read("kers_torque.lut"))
        else:
            ice = ice_ps(src)
            f_lut = 1 - minus_ps / 100 * (ice + e["ers_ps"]) / ice
        neu["power.lut"] = ZEILE.sub(lambda m: m.group(1) + f"{float(m.group(2)) * f_lut:.4f}", src.read("power.lut"))
        s_motor = minus_ps * e["s_pro_prozent_leistung"]
        f_cd = t.get("cd", 1.0)
        s_cd = (f_cd - 1) * 100 * e.get("s_pro_prozent_widerstand", 0.04)
        f_cl = t["cl"] if "cl" in t else 1 - (t["abstand"] - best["abstand"] - s_motor - s_cd) / e["s_pro_prozent_abtrieb"] / 100
        aero = src.read("aero.ini")
        neu["aero.ini"] = aero
        for sec in re.findall(r"(?m)^\[(WING_\d+)\]", aero):
            v = float(get_value(aero, sec, "CL_GAIN") or 0)
            if v: neu["aero.ini"], _ = set_value(neu["aero.ini"], sec, "CL_GAIN", f"{v * f_cl:.4f}")
            v = float(get_value(aero, sec, "CD_GAIN") or 0)
            if v and f_cd != 1: neu["aero.ini"], _ = set_value(neu["aero.ini"], sec, "CD_GAIN", f"{v * f_cd:.4f}")
        if "masse" in plan:
            neu["car.ini"] = set_value(CarData(ordner(key)).read("car.ini"), "BASIC", "TOTALMASS", str(plan["masse"]))[0]
        if a.apply:
            cd = CarData(ordner(key))
            for f, text in neu.items():
                if cd.read(f) != text: cd.write(f, text)
        print(f"{key:15s} {('+%.2f s' % t['abstand']) if 'abstand' in t else 'fest   '}  {t['ps']} PS (Motor {s_motor:.2f} s)  Leistung x{f_lut:.4f}  CL_GAIN x{f_cl:.4f}  CD_GAIN x{f_cd:.2f}" + ("" if a.apply else "  [Trockenlauf]"))


if __name__ == "__main__":
    main()
