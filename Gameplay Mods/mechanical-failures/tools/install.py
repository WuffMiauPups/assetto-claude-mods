"""Ausfall-Script, Dirty Air und failures.ini in die Datenordner von Autos kopieren.

  python install.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" --cars cim_2008_bmw_sauber \
      --profile ../profiles/failures_2008.ini --era 2005_2008 [--exclude-wings 5,6] [--front-wings 1,2] [--rear-wings 3,4,7]

Voraussetzung: data-Ordner des Autos ist entpackt (Content Manager: Unpack data, oder Tools/acd_unpack.py).
Was passiert pro Auto:
  - car.ini: VERSION=extended-N setzen, falls nicht gesetzt (Original als car.ini.bak)
  - failures.lua, dirty_air.lua und die Kennlinie der Ära als dirty_air.lut kopieren
  - Profil als failures.ini kopieren, Abschnitt [DIRTY_AIR] anhängen
  - script.lua: fehlt es, wird unser Einstieg kopiert. Hat das Auto ein eigenes Script, wird es als
    script.lua.orig gesichert und am Ende ein Hook angehängt, der unser Modul zusätzlich aufruft.
"""
import argparse
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "script"
LUTS = HERE.parent / "research" / "data"
MARKER = "-- [mechanical-failures] Hook, von install.py angehängt"
HOOK = f"""

{MARKER}
do
  local __mf = require('failures')
  local __update, __reset = script.update, script.reset
  function script.update(dt)
    if __update then __update(dt) end
    __mf.update(dt)
  end
  function script.reset()
    if __reset then __reset() end
    __mf.reset()
  end
end
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    ap.add_argument("--cars", nargs="+", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--era", required=True, help="Kennlinie, z.B. 2005_2008 -> research/data/dirty_air_2005_2008.lut")
    ap.add_argument("--exclude-wings", default="", help="Flügel, die das Auto selbst steuert, z.B. 5,6")
    ap.add_argument("--front-wings", default="", help="leer = automatisch aus aero.ini")
    ap.add_argument("--rear-wings", default="")
    a = ap.parse_args()

    lut = LUTS / f"dirty_air_{a.era}.lut"
    if not lut.is_file():
        raise SystemExit(f"Kennlinie fehlt: {lut}")

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

        shutil.copy(SCRIPT / "failures.lua", data / "failures.lua")
        shutil.copy(SCRIPT / "dirty_air.lua", data / "dirty_air.lua")
        shutil.copy(lut, data / "dirty_air.lut")

        ini = Path(a.profile).read_text(encoding="utf-8")
        if "[DIRTY_AIR]" not in ini:
            ini += (f"\n[DIRTY_AIR]\nENABLED=1\nLUT=dirty_air.lut\nMAX_DIST=80\nSMOOTHING=6\n"
                    f"FRONT_WINGS={a.front_wings}\nREAR_WINGS={a.rear_wings}\nEXCLUDE_WINGS={a.exclude_wings}\nDEBUG=1\n")
        (data / "failures.ini").write_text(ini, encoding="utf-8")

        script = data / "script.lua"
        if not script.is_file():
            shutil.copy(SCRIPT / "script.lua", script)
            print(f"{car}: installiert (eigenes script.lua)")
        else:
            body = script.read_text(encoding="utf-8", errors="ignore")
            if MARKER in body:
                print(f"{car}: aktualisiert (Hook war schon da)")
            elif "require('failures')" in body:
                shutil.copy(SCRIPT / "script.lua", script)
                print(f"{car}: aktualisiert (unser Einstieg)")
            else:
                orig = data / "script.lua.orig"
                if not orig.exists():
                    shutil.copy(script, orig)
                script.write_text(body.rstrip("\n") + HOOK, encoding="utf-8")
                print(f"{car}: installiert (Hook an vorhandenes script.lua, Original: script.lua.orig)")


if __name__ == "__main__":
    main()
