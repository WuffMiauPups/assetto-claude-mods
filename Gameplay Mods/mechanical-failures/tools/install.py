"""Script und failures.ini in die Datenordner aller Autos einer Serie kopieren.

  python install.py --ac "C:/.../assettocorsa" --cars f1_2017_mclaren f1_2017_mercedes --profile ../profiles/failures_2017_hybrid.ini

Voraussetzung: data-Ordner der Autos ist entpackt (Content Manager: Unpack data). Setzt VERSION=extended-2 in car.ini,
falls noch nicht gesetzt, und sichert die Originaldatei als car.ini.bak.
"""
import argparse
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    ap.add_argument("--cars", nargs="+", required=True)
    ap.add_argument("--profile", required=True)
    a = ap.parse_args()
    for car in a.cars:
        data = Path(a.ac) / "content" / "cars" / car / "data"
        if not data.is_dir():
            print(f"{car}: data-Ordner fehlt (entpacken)"); continue
        car_ini = data / "car.ini"
        txt = car_ini.read_text(errors="ignore")
        if not re.search(r"VERSION\s*=\s*extended", txt):
            shutil.copy(car_ini, data / "car.ini.bak")
            txt = re.sub(r"(VERSION\s*=\s*)(\d+)", r"\1extended-\2", txt, count=1)
            car_ini.write_text(txt)
        shutil.copy(HERE.parent / "script" / "script.lua", data / "script.lua")
        shutil.copy(a.profile, data / "failures.ini")
        print(f"{car}: installiert")


if __name__ == "__main__":
    main()
