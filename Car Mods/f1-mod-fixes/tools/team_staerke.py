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
import shutil
from pathlib import Path

from acdini import CarData, acd_read, acd_write, get_value, set_value

ZEILE = re.compile(r"(?m)^([ \t]*\d+(?:\.\d+)?[ \t]*\|[ \t]*)(-?\d+(?:\.\d+)?)")


class Bak:
    """Liest die Dateien aus data.acd.bak (gleicher Schlüssel wie data.acd, weil derselbe Ordner)."""

    def __init__(self, cardir):
        self.f = {n.lower(): c for n, c in acd_read(Path(cardir) / "data.acd.bak")[1]}

    def read(self, name):
        c = self.f.get(name.lower())
        return c.decode("latin1") if c is not None else None


class OffenBak:
    """Offener data-Ordner: liest <datei>.bak (Zustand vor der ersten Änderung), sonst die Datei selbst."""

    def __init__(self, cardir):
        self.d = Path(cardir) / "data"

    def read(self, name):
        for p in (self.d / (name + ".bak"), self.d / name):
            if p.is_file(): return p.read_text(encoding="latin1")
        return None


def basis(cardir):
    if (Path(cardir) / "data.acd.bak").is_file(): return Bak(cardir)
    return CarData(cardir) if (Path(cardir) / "data.acd").is_file() else OffenBak(cardir)


def zahl(s):
    """Liest Zahlen wie AC (atof): '1..17' ist 1.0, leere Werte 0."""
    m = re.match(r"\s*(-?\d*\.?\d*)", s or "")
    return float(m.group(1)) if m and m.group(1) not in ("", "-", ".", "-.") else 0.0


def absolut(plan, cars, apply):
    """Plan mit "absolut": Autos mit eigenen Ordnern, deren Ausgangswerte sich unterscheiden dürfen.

    Leistung:  der stärkste echte Motor bekommt die höchste Leistung der Mod ("ps_anker" setzt sie fest), die anderen
               im Verhältnis ihrer geschätzten PS. Jedes Auto wird von seiner eigenen Ausgangsleistung dorthin skaliert.
    Abtrieb:   Bezug ist der Ausgangs-Abtrieb des schnellsten echten Teams. Zielwert = Bezug x (1 - Rückstand in Prozent),
               Rückstand = (Abstand - Motor - Luftwiderstand - Gewicht - "s_sonst") / s_pro_prozent_abtrieb.
               "cl_min" begrenzt den Rückstand (die KI bricht mit sehr wenig Abtrieb ein), der Rest wird nur gemeldet.
    Luftwiderstand: bleibt wie in der Mod, "cd" je Team ist ein Faktor darauf. Unterschiede gehen in die Rechnung ein.
    Gewicht:   "masse" im Plan für alle, je Team überschreibbar; Unterschiede zählen mit "s_pro_kg".
    """
    from bestand import aero, peak_ps
    e, teams = plan["empfindlichkeit"], plan["teams"]
    info = {}
    for k, t in teams.items():
        b = basis(cars / t["ordner"])
        kg, cda, _ = aero(b)
        info[k] = {"b": b, "ps": peak_ps(b)[1], "kg": kg, "cda": cda * t.get("cd", 1.0)}
    ref = min((k for k in teams if "abstand" in teams[k]), key=lambda k: teams[k]["abstand"])
    anker = plan.get("ps_anker") or max(i["ps"] for i in info.values())
    ps_max = max(t["ps"] for t in teams.values())
    masse = lambda k: teams[k].get("masse", plan.get("masse"))
    for k, t in sorted(teams.items(), key=lambda kv: kv[1].get("abstand", 99)):
        i, d = info[k], cars / t["ordner"]
        ers = e.get("ers_ps", 0)                                    # Elektroanteil, der nicht in power.lut steckt
        ziel_ps = (anker + ers) * t["ps"] / ps_max - ers
        f_lut = ziel_ps / i["ps"]
        s_motor = (1 - t["ps"] / teams[ref]["ps"]) * 100 * e["s_pro_prozent_leistung"]
        s_cd = (i["cda"] / info[ref]["cda"] - 1) * 100 * e.get("s_pro_prozent_widerstand", 0.04)
        s_m = (masse(k) - masse(ref)) * e.get("s_pro_kg", 0.024) if masse(k) else 0.0
        rest = 0.0
        sonst = lambda x: x.get("s_sonst", 0) + (e.get("s_ohne_kers", 0.3) if x.get("ohne_kers") else 0)
        s_sonst = sonst(t) - sonst(teams[ref])                      # Nachteile, die schon im Auto stecken (Reifen, kein KERS)
        if "cl" in t:
            rel = t["cl"]
        else:
            rel = 1 - (t["abstand"] - teams[ref]["abstand"] - s_motor - s_cd - s_m - s_sonst) / e["s_pro_prozent_abtrieb"] / 100
            if rel < plan.get("cl_min", 0):
                rest, rel = (plan["cl_min"] - rel) * 100 * e["s_pro_prozent_abtrieb"], plan["cl_min"]
        bezug = plan.get("abtrieb_bezug") or info[ref]["kg"]        # kg bei 200 km/h, die dem schnellsten Team zustehen
        info[ref]["kg_bezug"] = bezug
        f_cl, f_cd = bezug * rel / i["kg"], t.get("cd", 1.0)
        en = i["b"].read("engine.ini")
        pname = (re.search(r"(?im)^\s*POWER_CURVE\s*=\s*([^;\r\n]+)", en) or [0, "power.lut"])[1].strip()
        neu = {pname: ZEILE.sub(lambda m: m.group(1) + f"{float(m.group(2)) * f_lut:.4f}", i["b"].read(pname))}
        text = i["b"].read("aero.ini")
        neu["aero.ini"] = text
        for sec in re.findall(r"(?m)^\[(WING_\d+)\]", text):
            v = zahl(get_value(text, sec, "CL_GAIN"))
            if v: neu["aero.ini"], _ = set_value(neu["aero.ini"], sec, "CL_GAIN", f"{v * f_cl:.4f}")
            v = zahl(get_value(text, sec, "CD_GAIN"))
            if v and f_cd != 1: neu["aero.ini"], _ = set_value(neu["aero.ini"], sec, "CD_GAIN", f"{v * f_cd:.4f}")
        cd = CarData(d)
        if masse(k): neu["car.ini"] = set_value(cd.read("car.ini"), "BASIC", "TOTALMASS", str(masse(k)))[0]
        if apply:
            for f, inhalt in neu.items():
                if cd.read(f) != inhalt: cd.write(f, inhalt)
            if t.get("ohne_kers") and cd.files is not None and "kers.ini" in cd.files:      # Team fuhr ohne KERS
                if not (d / "data.acd.bak").exists(): shutil.copy2(cd.acd, d / "data.acd.bak")
                cd.entries[:] = [x for x in cd.entries if x[0].lower() not in ("kers.ini", "kers_torque.lut")]
                acd_write(cd.acd, cd.header, cd.entries, cd.key)
        print(f"{k:14s} {('+%.2f s' % t['abstand']) if 'abstand' in t else 'fest   '}  {t['ps']:4d} PS  Modell {i['ps']:4.0f} -> {ziel_ps:4.0f} PS (x{f_lut:.4f}, {s_motor:+.2f} s)"
              f"  Abtrieb {i['kg']:4.0f} -> {bezug * rel:4.0f} kg (x{f_cl:.4f}, {(rel - 1) * 100:+.1f} %)  CdA {i['cda']:.3f} ({s_cd:+.2f} s)" + ("  ohne KERS" if t.get("ohne_kers") else "")
              + (f"  {masse(k)} kg" if masse(k) else "") + (f"  Rest {rest:.2f} s" if rest > 0.005 else "") + ("" if apply else "  [Trockenlauf]"))


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
    if plan.get("absolut"): return absolut(plan, cars, a.apply)
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
