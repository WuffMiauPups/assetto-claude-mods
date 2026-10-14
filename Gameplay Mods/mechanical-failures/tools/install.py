"""Ausfall-Script in die Datenordner von Autos einbauen oder wieder entfernen.

  python install.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" --cars cim_2008_bmw_sauber --profile ../profiles/failures_2008.ini
  python install.py --ac ... --cars cim_2008_bmw_sauber --profile ... --test ENGINE:20     # Defekt nach 20 s erzwingen
  python install.py --ac ... --cars cim_2008_bmw_sauber --uninstall

Voraussetzung: der data-Ordner des Autos ist entpackt (Content Manager: Unpack data). Fehlt er, kann er mit
--unpack-from <ordner> aus einer entpackten Kopie (zum Beispiel reference/<auto>/data) angelegt werden. data.acd wird nie angefasst.

Was passiert pro Auto:
  - car.ini: VERSION=extended-N, falls nicht gesetzt (Sicherung car.ini.bak)
  - failures.lua und failures.ini werden kopiert
  - script.lua: existiert keins, kommt das Loader-Script aus script/script.lua. Existiert eins, wird es als script.lua.bak
    gesichert und der Hook-Block aus script/hook.lua angefügt, damit das vorhandene Script weiterläuft.
"""
import argparse
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT_DIR = HERE.parent / "script"
HOOK_MARK = ">>> mechanical-failures"


def ensure_extended(data: Path) -> None:
    car_ini = data / "car.ini"
    txt = car_ini.read_text(errors="ignore")
    if re.search(r"VERSION\s*=\s*extended", txt):
        return
    shutil.copy(car_ini, data / "car.ini.bak")
    txt = re.sub(r"(VERSION\s*=\s*)(\d+)", r"\1extended-\2", txt, count=1)
    car_ini.write_text(txt)
    print("  car.ini: VERSION auf extended gesetzt, Sicherung car.ini.bak")


def install_script(data: Path) -> None:
    script = data / "script.lua"
    if not script.exists():
        shutil.copy(SCRIPT_DIR / "script.lua", script)
        print("  script.lua: Loader angelegt")
        return
    txt = script.read_text(errors="ignore")
    if HOOK_MARK in txt:
        print("  script.lua: Hook bereits vorhanden")
        return
    shutil.copy(script, data / "script.lua.bak")
    script.write_text(txt.rstrip("\n") + "\n" + (SCRIPT_DIR / "hook.lua").read_text())
    print("  script.lua: vorhandenes Script gesichert (script.lua.bak), Hook angefügt")


def write_profile(data: Path, profile: Path, test: str | None) -> None:
    txt = profile.read_text(errors="ignore").rstrip("\n") + "\n"
    if test:
        kind, _, at = test.partition(":")
        txt += f"\n[TEST]\nFORCE={kind.upper()}\nFORCE_AT={at or 20}\n"
        print(f"  failures.ini: Testdefekt {kind.upper()} nach {at or 20} s")
    (data / "failures.ini").write_text(txt)


def install(data: Path, profile: Path, test: str | None) -> None:
    ensure_extended(data)
    shutil.copy(SCRIPT_DIR / "failures.lua", data / "failures.lua")
    write_profile(data, profile, test)
    install_script(data)


def uninstall(data: Path) -> None:
    for name in ("failures.lua", "failures.ini"):
        p = data / name
        if p.exists():
            p.unlink()
    script, bak = data / "script.lua", data / "script.lua.bak"
    if bak.exists():
        shutil.move(bak, script)
        print("  script.lua: Original aus script.lua.bak wiederhergestellt")
    elif script.exists() and HOOK_MARK not in script.read_text(errors="ignore"):
        pass
    elif script.exists():
        script.unlink()
        print("  script.lua: Loader entfernt")
    car_bak = data / "car.ini.bak"
    if car_bak.exists():
        shutil.move(car_bak, data / "car.ini")
        print("  car.ini: Original wiederhergestellt")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ac", required=True, help="Assetto-Corsa-Ordner")
    ap.add_argument("--cars", nargs="+", required=True, help="Auto-Ordnernamen unter content/cars")
    ap.add_argument("--profile", help="failures_<jahr>.ini aus profiles/")
    ap.add_argument("--test", help="Defekt erzwingen, zum Beispiel ENGINE:20")
    ap.add_argument("--unpack-from", help="entpackter data-Ordner als Vorlage, falls das Auto noch keinen hat")
    ap.add_argument("--uninstall", action="store_true")
    a = ap.parse_args()
    if not a.uninstall and not a.profile:
        ap.error("--profile fehlt")

    for car in a.cars:
        data = Path(a.ac) / "content" / "cars" / car / "data"
        print(f"{car}:")
        if not data.is_dir():
            if a.unpack_from and not a.uninstall:
                shutil.copytree(a.unpack_from, data)
                print(f"  data-Ordner aus {a.unpack_from} angelegt")
            else:
                print("  data-Ordner fehlt (Content Manager: Unpack data, oder --unpack-from)")
                continue
        if a.uninstall:
            uninstall(data)
        else:
            install(data, Path(a.profile), a.test)
        print("  fertig")


if __name__ == "__main__":
    main()
