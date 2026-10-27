"""Physik eines Spender-Autos auf ein Ziel-Auto übertragen, Modell, Skins, Sound und Geometrie bleiben.
Nur für Autos mit offenem data-Ordner (z. B. das F1-2009-Paket von The Race Project).

  python transplant.py --ac <AC> --target f1_2009_Renault_R29_S2 --donor f1_2009_RedBull_RB5_S2 [--apply]
  python transplant.py --ac <AC> --target f1_2009_Ferrari_F60_S2 --donor f1_2009_BmwSauber_S1 --parts fahrwerk --apply

Teile (--parts, Standard: alle):
  physik    aero, Motor, Getriebe, Elektronik, Setup, KI, Sprit, Reifen, Bremsen, alle .lut/.rto, Trägheit und Sprit aus car.ini
  fahrwerk  suspensions.ini und setup.ini
  kollider  colliders.ini (einzelner Körper ohne Bodenkontakt wie bei den TRP-Autos)
Eigen bleiben immer: Radstand, Spurbreiten, [GRAPHICS_OFFSETS], Bremsscheiben-Grafik, alles Grafische.
Reifen kommen mit Spender-Radius: ein kleinerer eigener Radius ließ Renault und Force India 2009 in der Box hängen.
KERS wird entfernt, außer --keep-kers. Vorher wird data/ einmalig nach data_vor_transplantation/ kopiert.
"""
import argparse
import os
import shutil
from pathlib import Path

from acdini import get_value, section, set_value

PHYS_INI = ["aero.ini", "drivetrain.ini", "engine.ini", "electronics.ini", "ai.ini", "fuel_cons.ini", "tyres.ini"]


def rd(p): return Path(p).read_bytes().decode("latin1")
def wr(p, t): Path(p).write_bytes(t.encode("latin1"))


def replace_section(text, name, block):
    old = section(text, name)
    return text.replace(old, block, 1) if old and block else text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True); ap.add_argument("--target", required=True); ap.add_argument("--donor", required=True)
    ap.add_argument("--parts", nargs="*", default=["physik", "fahrwerk", "kollider"])
    ap.add_argument("--keep-kers", action="store_true"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    cars = Path(a.ac) / "content" / "cars"
    T, D = cars / a.target / "data", cars / a.donor / "data"
    B = cars / a.target / "data_vor_transplantation"
    if not T.is_dir() or not D.is_dir():
        raise SystemExit("Ziel und Spender brauchen einen offenen data-Ordner")
    if not a.apply:
        print(f"Trockenlauf: {a.donor} -> {a.target}, Teile {a.parts}"); return
    if not B.exists(): shutil.copytree(T, B)
    own = lambda f: rd(B / f)

    if "physik" in a.parts:
        for f in PHYS_INI: shutil.copyfile(D / f, T / f)
        n = 0
        for f in os.listdir(D):
            if f.lower().endswith((".lut", ".rto")) and (a.keep_kers or f.lower() != "kers_torque.lut"):
                shutil.copyfile(D / f, T / f); n += 1
        if not a.keep_kers:
            for f in ("kers.ini", "kers_torque.lut"):
                if (T / f).exists(): os.remove(T / f)
        wr(T / "brakes.ini", replace_section(rd(D / "brakes.ini"), "DISCS_GRAPHICS", section(own("brakes.ini"), "DISCS_GRAPHICS")))
        c, dc = rd(T / "car.ini"), rd(D / "car.ini")
        for sec, key in (("BASIC", "INERTIA"), ("FUEL", "CONSUMPTION"), ("FUEL", "FUEL"), ("FUEL", "MAX_FUEL")):
            v = get_value(dc, sec, key)
            if v: c, _ = set_value(c, sec, key, v)
        wr(T / "car.ini", c)
        print(f"physik: {len(PHYS_INI)} ini, Bremsen, car.ini-Werte, {n} Kennlinien")

    if "fahrwerk" in a.parts or "physik" in a.parts:
        s, o = rd(D / "suspensions.ini"), own("suspensions.ini")
        for sec, key in (("BASIC", "WHEELBASE"), ("FRONT", "TRACK"), ("REAR", "TRACK")):
            s, _ = set_value(s, sec, key, get_value(o, sec, key))
        wr(T / "suspensions.ini", replace_section(s, "GRAPHICS_OFFSETS", section(o, "GRAPHICS_OFFSETS")))
        shutil.copyfile(D / "setup.ini", T / "setup.ini")
        print(f"fahrwerk: vom Spender, Radstand {get_value(o, 'BASIC', 'WHEELBASE')}, Spur {get_value(o, 'FRONT', 'TRACK')}/{get_value(o, 'REAR', 'TRACK')} eigen")

    if "kollider" in a.parts:
        shutil.copyfile(D / "colliders.ini", T / "colliders.ini")
        print("kollider: vom Spender")


if __name__ == "__main__":
    main()
