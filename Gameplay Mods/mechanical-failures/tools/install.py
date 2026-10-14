"""Ausfall-Script und Dirty Air in Autos installieren.

  python install.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" --cars cim_2008_bmw_sauber \
      --profile ../profiles/failures_2008.ini --era 2005_2008 [--exclude-wings 5,6] [--front-wings 1,2] \
      [--rear-wings 3,4,7] [--pack]

Erzeugt EIN script.lua ohne require: dirty_air.lua und failures.lua werden als lokale Module eingebettet,
die Kennlinie der Ära als Text gleich mit. Nur failures.ini wird zur Laufzeit gelesen (ac.INIConfig.carData,
funktioniert aus Ordner und data.acd).

Pro Auto:
  - data-Ordner muss existieren (Tools/acd/acd_unpack.py oder Content Manager "Unpack data")
  - car.ini: VERSION=extended-N, falls nicht gesetzt (Original als car.ini.bak)
  - failures.ini = Profil + Abschnitt [DIRTY_AIR]
  - script.lua: ohne eigenes Script wird unser Einstieg geschrieben. Hat das Auto ein eigenes Script, wird
    es als script.lua.orig gesichert und ein Hook-Block angehängt (Markierung, idempotent).
  - --pack: data-Ordner mit Tools/acd/acd_pack.py zu data.acd packen, Original einmalig als data.acd.bak
    sichern. Nötig, wenn AC die data.acd dem Ordner vorzieht.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "script"
LUTS = HERE.parent / "research" / "data"
sys.path.insert(0, str(HERE.parents[2] / "Tools" / "acd"))

MARKER = "-- [mechanical-failures] von install.py erzeugt"


def module_block(name, source):
    return f"local {name} = (function()\n{source.rstrip()}\nend)()\n"


def build_bundle(lut_text):
    dirty = (SCRIPT / "dirty_air.lua").read_text(encoding="utf-8")
    fail = (SCRIPT / "failures.lua").read_text(encoding="utf-8")
    fail = fail.replace("local DirtyAir = require('dirty_air')", "local DirtyAir = __dirty_air")
    assert "__dirty_air" in fail, "require-Zeile in failures.lua nicht gefunden"
    assert "]=]" not in lut_text
    return (
        f"{MARKER}\n"
        f"ac.log('[mechanical-failures] Script geladen, car ' .. tostring(car and car.index))\n"
        + module_block("__dirty_air", dirty)
        + f"__dirty_air.lutText = [=[\n{lut_text.rstrip()}\n]=]\n"
        + module_block("__failures", fail)
        + "ac.log('[mechanical-failures] Module bereit')\n"
    )


def standalone(bundle):
    return bundle + "function script.update(dt) __failures.update(dt) end\nfunction script.reset() __failures.reset() end\n"


def hook(bundle):
    return ("\n\ndo\n" + "".join("  " + l + "\n" for l in bundle.splitlines()) +
            "  local __update, __reset = script.update, script.reset\n"
            "  function script.update(dt)\n    if __update then __update(dt) end\n    __failures.update(dt)\n  end\n"
            "  function script.reset()\n    if __reset then __reset() end\n    __failures.reset()\n  end\n"
            "end\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    ap.add_argument("--cars", nargs="+", required=True)
    ap.add_argument("--profile", required=True)
    ap.add_argument("--era", required=True, help="Kennlinie, z.B. 2005_2008 -> research/data/dirty_air_2005_2008.lut")
    ap.add_argument("--exclude-wings", default="", help="Flügel, die das Auto selbst steuert, z.B. 5,6")
    ap.add_argument("--front-wings", default="", help="leer = automatisch aus aero.ini")
    ap.add_argument("--rear-wings", default="")
    ap.add_argument("--strength", default="0.5", help="Skalierung Dirty Air fuer den Spieler, 1.0 = volle Kennlinie")
    ap.add_argument("--ai-strength", default="0.35", help="Skalierung fuer KI-Autos")
    ap.add_argument("--pack", action="store_true", help="data-Ordner nach data.acd packen (Original als data.acd.bak)")
    a = ap.parse_args()

    lut = LUTS / f"dirty_air_{a.era}.lut"
    if not lut.is_file():
        raise SystemExit(f"Kennlinie fehlt: {lut}")
    bundle = build_bundle(lut.read_text(encoding="utf-8"))

    for car in a.cars:
        cardir = Path(a.ac) / "content" / "cars" / car
        data = cardir / "data"
        if not data.is_dir():
            print(f"{car}: data-Ordner fehlt (entpacken)"); continue

        car_ini = data / "car.ini"
        txt = car_ini.read_text(errors="ignore")
        if not re.search(r"VERSION\s*=\s*extended", txt):
            shutil.copy(car_ini, data / "car.ini.bak")
            txt = re.sub(r"(VERSION\s*=\s*)(\d+)", r"\1extended-\2", txt, count=1)
            car_ini.write_text(txt)

        ini = Path(a.profile).read_text(encoding="utf-8")
        if "[DIRTY_AIR]" not in ini:
            ini += (f"\n[DIRTY_AIR]\nENABLED=1\nSTRENGTH={a.strength}\nAI_STRENGTH={a.ai_strength}\nMAX_DIST=80\nSMOOTHING=6\n"
                    f"FRONT_WINGS={a.front_wings}\nREAR_WINGS={a.rear_wings}\nEXCLUDE_WINGS={a.exclude_wings}\nDEBUG=1\n")
        (data / "failures.ini").write_text(ini, encoding="utf-8")
        for old in ("failures.lua", "dirty_air.lua", "dirty_air.lut"):   # Reste der require-Variante
            (data / old).unlink(missing_ok=True)

        script = data / "script.lua"
        orig = data / "script.lua.orig"
        if orig.exists():
            base = orig.read_text(encoding="utf-8", errors="ignore")
        elif script.exists() and MARKER not in script.read_text(encoding="utf-8", errors="ignore"):
            shutil.copy(script, orig)
            base = orig.read_text(encoding="utf-8", errors="ignore")
        else:
            base = None
        if base is None:
            script.write_text(standalone(bundle), encoding="utf-8")
            mode = "eigenständiges script.lua"
        else:
            script.write_text(base.rstrip("\n") + hook(bundle), encoding="utf-8")
            mode = "Hook an vorhandenes script.lua (Original: script.lua.orig)"

        if a.pack:
            from acd_pack import pack
            acd = cardir / "data.acd"
            if acd.exists() and not (cardir / "data.acd.bak").exists():
                shutil.copy(acd, cardir / "data.acd.bak")
            pack(str(data), str(acd))
            mode += ", data.acd gepackt"
        print(f"{car}: installiert, {mode}")


if __name__ == "__main__":
    main()
