"""App "Reliability & Dirty Air" nach apps/lua/reliability kopieren, mit Profilen und Dirty-Air-Kennlinien.

  python install_app.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa"

Danach im Spiel die App in der Apps-Leiste aktivieren. Wirkt auf alle Autos im Feld, offline.
"""
import argparse
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    a = ap.parse_args()
    dst = Path(a.ac) / "apps" / "lua" / "reliability"
    (dst / "data").mkdir(parents=True, exist_ok=True)
    (dst / "profiles").mkdir(parents=True, exist_ok=True)
    for f in (MOD / "app" / "reliability").iterdir():
        if f.is_file():
            shutil.copy(f, dst / f.name)
    n_lut = n_prof = 0
    for f in (MOD / "research" / "data").glob("dirty_air_*.lut"):
        if not f.name.endswith("_lateral.lut"):
            shutil.copy(f, dst / "data" / f.name); n_lut += 1
    shutil.copy(MOD / "research" / "data" / "failure_rates.json", dst / "data" / "failure_rates.json")
    for f in (MOD / "profiles").glob("failures_*.ini"):
        shutil.copy(f, dst / "profiles" / f.name); n_prof += 1
    print(f"installiert nach {dst}: {n_lut} Kennlinien, {n_prof} Profile")


if __name__ == "__main__":
    main()
