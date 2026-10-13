"""Installiert den Porsche 956 Venturi als eigenes Auto in Assetto Corsa.

  python install.py           Auto anlegen (falls noetig) und physics/data hineinkopieren
  python install.py --ac PFAD anderer AC-Ordner

Erster Lauf: kopiert content/cars/vac_groupc_956 nach content/cars/porsche_956_venturi.
  - data.acd wird nicht mitkopiert, damit AC den entpackten data-Ordner verwendet.
  - Sound-Bank und GUIDs.txt werden auf den neuen Ordnernamen umgeschrieben (wie CM "Replace sound").
  - ui/ui_car.json bekommt eigenen Namen und Tag.
Jeder Lauf: physics/data wird komplett in den data-Ordner des Autos gespiegelt. Vorher wird der
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
    print("Fertig. Im Content Manager: Auto 'Porsche 956 Venturi (WIP)', CSP Extended Physics aktiv lassen.")


if __name__ == "__main__":
    main()
