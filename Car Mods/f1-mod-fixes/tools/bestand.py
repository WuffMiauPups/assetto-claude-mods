"""Bestandsaufnahme der Physikwerte eines Jahrgangs: Gewicht, Leistung, Abtrieb, Luftwiderstand, Reifen.

  py -3.11 bestand.py --ac <AC> --prefix cim_2011_
  py -3.11 bestand.py --ac <AC> --cars f1_2014_ferrari_f14_t ferrari_2014 [--bak]

--bak liest data.acd.bak (Originalzustand) statt der aktuellen data.acd.
Abtrieb und CdA: Summe über alle [WING_n] aus CHORD x SPAN x Beiwert(ANGLE) x GAIN bei 200 km/h, ohne Höhen-LUTs
und ohne dynamische Regler. Für den Vergleich innerhalb einer Mod reicht das, absolute Werte sind Näherungen.
Leistung: Spitze aus power.lut, bei Turbos mal (1 + Ladedruck), siehe team_staerke.ice_ps.
"""
import argparse
import math
import re
from pathlib import Path

from acdini import CarData, get_value
from team_staerke import Bak, zahl
from topspeed import g, lut, sections

RHO = 1.22


def peak_ps(cd):
    en = cd.read("engine.ini")
    hdr = re.search(r"\[HEADER\][^\[]*", en)
    pl = cd.read((g(hdr.group(0), "POWER_CURVE") if hdr else "") or "power.lut")
    lim = float(get_value(en, "ENGINE_DATA", "LIMITER") or 99999)
    pts = [(float(a), float(b)) for a, b in re.findall(r"(?m)^\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)", pl)]
    boost = 0.0
    for sec in re.findall(r"(?m)^\[(TURBO_\d+)\]", en):
        mb, wg = float(get_value(en, sec, "MAX_BOOST") or 0), float(get_value(en, sec, "WASTEGATE") or 0)
        boost += min(mb, wg) if wg else mb
    na = max(r * t for r, t in pts if r <= lim) * 2 * math.pi / 60 / 735.5
    return na, na * (1 + boost), lim


def aero(cd, kmh=200.0):
    text = cd.read("aero.ini")
    q = 0.5 * RHO * (kmh / 3.6) ** 2
    lift = drag = 0.0
    for k, b in sections(text, "WING").items():
        area = zahl(g(b, "CHORD")) * zahl(g(b, "SPAN"))
        ang = zahl(g(b, "ANGLE"))
        lift += area * (lut(cd.read(g(b, "LUT_AOA_CL")), ang) or 0) * zahl(g(b, "CL_GAIN"))
        drag += area * (lut(cd.read(g(b, "LUT_AOA_CD")), ang) or 0) * zahl(g(b, "CD_GAIN"))
    return lift * q / 9.81, drag, len(sections(text, "WING"))


def zeile(cardir, bak):
    cd = Bak(cardir) if bak and (cardir / "data.acd.bak").is_file() else CarData(cardir)
    art = ("acd" if (cardir / "data.acd").is_file() else "offen") + ("+bak" if (cardir / "data.acd.bak").is_file() else "")
    car, ty = cd.read("car.ini"), cd.read("tyres.ini") or ""
    na, ps, lim = peak_ps(cd)
    kg, cda, n = aero(cd)
    kers = "KERS" if cd.read("kers.ini") else "-"
    return (f"{cardir.name:36s} {art:8s} {float(get_value(car, 'BASIC', 'TOTALMASS')):5.0f} kg  {ps:5.0f} PS"
            f"{'' if abs(ps - na) < 1 else ' (Sauger %.0f)' % na:14s} Lim {lim:5.0f}  {kers:4s}  Abtrieb {kg:5.0f} kg  CdA {cda:.3f}  "
            f"L/D {kg * 9.81 / (0.5 * RHO * (200 / 3.6) ** 2) / cda if cda else 0:4.2f}  Flügel {n}  "
            f"DY {get_value(ty, 'FRONT', 'DY_REF') or get_value(ty, 'FRONT', 'DY0')}/{get_value(ty, 'REAR', 'DY_REF') or get_value(ty, 'REAR', 'DY0')} "
            f"{get_value(ty, 'FRONT', 'NAME') or ''}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True); ap.add_argument("--prefix"); ap.add_argument("--cars", nargs="*", default=[])
    ap.add_argument("--bak", action="store_true")
    a = ap.parse_args()
    root = Path(a.ac) / "content" / "cars"
    cars = list(a.cars) + (sorted((p.name for p in root.iterdir() if p.name.lower().startswith(a.prefix.lower())), key=str.lower) if a.prefix else [])
    for c in cars:
        try:
            print(zeile(root / c, a.bak))
        except Exception as e:                                   # defekte oder fremd verschlüsselte data.acd
            print(f"{c:36s} FEHLER {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
