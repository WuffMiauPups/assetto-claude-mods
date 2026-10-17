"""Installiert den Porsche 956 Venturi als eigenes Auto in Assetto Corsa.

  python install.py           Auto anlegen (falls noetig) und physics/data hineinkopieren
  python install.py --ac PFAD anderer AC-Ordner

Erster Lauf: kopiert content/cars/vac_groupc_956 nach content/cars/porsche_956_venturi.
  - data.acd wird nicht mitkopiert, damit AC den entpackten data-Ordner verwendet.
  - Sound-Bank und GUIDs.txt werden auf den neuen Ordnernamen umgeschrieben (wie CM "Replace sound").
  - ui/ui_car.json bekommt eigenen Namen und Tag.
Jeder Lauf: app/rideheight_monitor wird nach apps/lua kopiert, physics/data wird komplett in den data-Ordner des Autos gespiegelt. Vorher wird der
alte data-Ordner als data.bak gesichert (nur die letzte Version). Das Original vac_groupc_956
wird nie veraendert.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
SRC_DATA = MOD / "physics" / "data"
SRC_APP = MOD / "app" / "rideheight_monitor"

AC_DEFAULT = Path(r"E:\SteamLibrary\steamapps\common\assettocorsa")
BASE_CAR = "vac_groupc_956"
NEW_CAR = "porsche_956_venturi"


def create_car(cars: Path) -> Path:
    base = cars / BASE_CAR
    dst = cars / NEW_CAR
    if not base.is_dir():
        raise SystemExit(f"Basis-Mod fehlt: {base}")
    print(f"Lege {dst} als Kopie von {base} an ...")
    shutil.copytree(base, dst, ignore=shutil.ignore_patterns("data.acd", "data"))

    # Sound auf neuen Namen umschreiben
    sfx = dst / "sfx"
    bank = sfx / f"{BASE_CAR}.bank"
    if bank.exists():
        bank.rename(sfx / f"{NEW_CAR}.bank")
    guids = sfx / "GUIDs.txt"
    if guids.exists():
        guids.write_text(guids.read_text().replace(f"/{BASE_CAR}", f"/{NEW_CAR}"))

    # UI-Eintrag
    ui = dst / "ui" / "ui_car.json"
    if ui.exists():
        meta = json.loads(ui.read_text(encoding="utf-8"))
        meta["name"] = "Porsche 956 Venturi (WIP)"
        meta["parent"] = BASE_CAR
        meta["tags"] = sorted(set(meta.get("tags", [])) | {"venturi", "eigenbau"})
        meta["description"] = (
            "Eigenbau auf Basis des VAC 956: Unterboden als CSP-Aero-Map (Venturi-Kennfeld "
            "ueber Bodenfreiheit vorn/hinten). Physik in Arbeit, Stand im Repo assetto-claude-mods.<br><br>"
            + meta.get("description", "")
        )
        ui.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return dst


def update_ui(car: Path) -> None:
    """Name und Kenndaten im Content Manager auf den Stand der Physik bringen."""
    ui = car / "ui" / "ui_car.json"
    if not ui.exists():
        return
    meta = json.loads(ui.read_text(encoding="utf-8"))
    meta["name"] = "Porsche 956 Venturi (Bellof, Ring 1983)"
    meta["specs"] = {
        "bhp": "710 bhp (Quali 1,3 bar)",
        "torque": "635 Nm",
        "weight": "895 kg",
        "topspeed": "310 km/h (Ring)",
        "acceleration": "--s",
        "pwratio": "1.26 kg/hp",
    }
    meta["year"] = 1983
    ui.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ui_car.json aktualisiert")


def sync_data(car: Path) -> None:
    dst = car / "data"
    if dst.exists():
        bak = car / "data.bak"
        if bak.exists():
            shutil.rmtree(bak)
        dst.rename(bak)
    shutil.copytree(SRC_DATA, dst)
    print(f"data-Ordner gespiegelt: {SRC_DATA} -> {dst}")
    if (car / "data.acd").exists():
        print("Warnung: data.acd liegt noch im Auto-Ordner, AC koennte ihn bevorzugen. Bitte entfernen.")


def install_app(ac: Path) -> None:
    dst = ac / "apps" / "lua" / SRC_APP.name
    dst.mkdir(parents=True, exist_ok=True)
    # nur Script und Manifest ersetzen, logs/ mit den Messungen bleibt erhalten
    for src in SRC_APP.iterdir():
        if src.is_file():
            shutil.copy2(src, dst / src.name)
    print(f"App installiert: {dst}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", type=Path, default=AC_DEFAULT)
    args = ap.parse_args()
    if not SRC_DATA.is_dir():
        raise SystemExit("physics/data fehlt, erst build_aero.py ausfuehren")
    cars = args.ac / "content" / "cars"
    car = cars / NEW_CAR
    if not car.is_dir():
        car = create_car(cars)
    sync_data(car)
    update_ui(car)
    install_app(args.ac)
    print("Fertig. Im Content Manager: Auto 'Porsche 956 Venturi (Bellof, Ring 1983)', CSP Extended Physics aktiv lassen.")


if __name__ == "__main__":
    main()
