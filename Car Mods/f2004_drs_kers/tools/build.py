"""Baut den Ferrari F2004 mit DRS und KERS (2013) und Pirelli-Mischungen 2018 als eigenes Auto.

  py -3.11 build.py            Auto content/cars/ferrari_f2004_drs_kers anlegen oder neu bauen
  py -3.11 build.py --ac PFAD  anderer AC-Ordner

Quellen im Spielordner (werden nie veraendert):
  ks_ferrari_f2004         Modell, Sound, Skins, Physik-Basis (data.acd wird entpackt)
  rss_formula_hybrid_2018  tyres.ini mit den fuenf Mischungen HS/US/SS/S/M samt LUTs
  cim_2013_ferrari         nur als Vorlage gelesen (KERS-Werte stehen in physics/)

Es werden keine Kunos- oder RSS-Dateien ins Repo kopiert; alles Abgeleitete entsteht beim Bauen.
Ein vorhandener Zielordner wird vorher als <name>.bak gesichert (nur die letzte Version).
Die Physik wird als data.acd gepackt (AC laedt drs.ini nur daraus), die entpackte Kopie liegt in tools/out.
Das Modell bekommt die DRS-Klappe als eigenen Knoten plus Animation (make_flap.py).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_flap  # noqa: E402

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
PHYSICS = MOD / "physics"
ACD_UNPACK = MOD.parent.parent / "Tools" / "acd" / "acd_unpack.py"

AC_DEFAULT = Path(r"E:\SteamLibrary\steamapps\common\assettocorsa")
BASE_CAR = "ks_ferrari_f2004"
TYRE_CAR = "rss_formula_hybrid_2018"
NEW_CAR = "ferrari_f2004_drs_kers"
SCREEN_NAME = "Ferrari F2004 DRS KERS"

# DRS: Anteil der Klappe am Heckfluegel (Herleitung in research/01-drs-herleitung.md)
FLAP_SHARE = 0.45
REAR_WING = 2          # Heckfluegel-Index in der aero.ini des F2004
FLAP_WING = 6          # neuer Index fuer die DRS-Klappe (0..5 sind belegt)

# Reifen: tyres.ini der Formula Hybrid 2018 wird 1:1 uebernommen (auch Breite 305/405 und Radius 0,335),
# nur die Standardmischung wird auf Hyper-Soft gesetzt. Hier koennten Werte je Achse ueberschrieben werden.
GEOMETRY: dict[str, dict[str, str]] = {"FRONT": {}, "REAR": {}}


def load_unpacker():
    spec = importlib.util.spec_from_file_location("acd_unpack", ACD_UNPACK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unpack(cars: Path, car: str, out: Path) -> None:
    acd = cars / car / "data.acd"
    if not acd.exists():
        raise SystemExit(f"fehlt: {acd}")
    out.mkdir(parents=True, exist_ok=True)
    load_unpacker().unpack(str(acd), str(out))


# ---------------------------------------------------------------- Auto-Ordner
def create_car(cars: Path) -> Path:
    base, dst = cars / BASE_CAR, cars / NEW_CAR
    if dst.exists():
        bak = cars / f"{NEW_CAR}.bak"
        if bak.exists():
            shutil.rmtree(bak)
        dst.rename(bak)
        print(f"alter Stand gesichert: {bak}")
    print(f"kopiere {base} -> {dst}")
    shutil.copytree(base, dst, ignore=shutil.ignore_patterns("data.acd", "data"))

    # Sound: Bank umbenennen, GUIDs aus der globalen Liste ableiten (Kunos-Autos haben keine eigene)
    sfx = dst / "sfx"
    bank = sfx / f"{BASE_CAR}.bank"
    if bank.exists():
        bank.rename(sfx / f"{NEW_CAR}.bank")
    guids_src = cars.parent / "sfx" / "GUIDs.txt"
    lines = [l for l in guids_src.read_text(errors="ignore").splitlines() if f"/{BASE_CAR}" in l]
    (sfx / "GUIDs.txt").write_text("\n".join(l.replace(f"/{BASE_CAR}", f"/{NEW_CAR}") for l in lines) + "\n")
    print(f"Sound: {len(lines)} GUID-Eintraege umgeschrieben")

    unpack(cars, BASE_CAR, dst / "data")
    return dst


# ---------------------------------------------------------------- Reifen
def parse_sections(text: str) -> list[tuple[str, list[str]]]:
    """INI als Liste (Abschnittsname, Zeilen) inkl. Vorspann unter ''."""
    sections, name, lines = [], "", []
    for line in text.splitlines():
        m = re.match(r"\s*\[([^\]]+)\]", line)
        if m:
            sections.append((name, lines))
            name, lines = m.group(1), [line]
        else:
            lines.append(line)
    sections.append((name, lines))
    return sections


def set_key(lines: list[str], key: str, value: str) -> None:
    for i, l in enumerate(lines):
        if re.match(rf"\s*{key}\s*=", l):
            lines[i] = f"{key}={value}"
            return
    lines.append(f"{key}={value}")


def build_tyres(src: Path, data: Path) -> list[str]:
    text = (src / "tyres.ini").read_text(errors="ignore")
    out, luts, names = [], set(), []
    for name, lines in parse_sections(text):
        axle = name.split("_")[0]
        if axle in GEOMETRY:
            for k, v in GEOMETRY[axle].items():
                set_key(lines, k, v)
            if axle == "FRONT":
                names.append(next(l.split("=", 1)[1] for l in lines if l.startswith("NAME=")))
        if name == "COMPOUND_DEFAULT":
            set_key(lines, "INDEX", "0")   # Hyper-Soft als Standard
        for l in lines:
            m = re.match(r"\s*(WEAR_CURVE|PERFORMANCE_CURVE|DCAMBER_LUT)\s*=\s*(\S+)", l)
            if m:
                luts.add(m.group(2))
        out.extend(lines)
    header = [
        "; Reifen: Mischungen und Karkasse der Formula Hybrid 2018 (RSS), Geometrie des F2004 (Kunos).",
        f"; Erzeugt von {HERE.name}/build.py, nicht von Hand aendern.",
    ]
    (data / "tyres.ini").write_text("\n".join(header + out) + "\n")
    for lut in luts:
        shutil.copy2(src / lut, data / lut)
    print(f"Reifen: {', '.join(names)}; {len(luts)} LUTs kopiert")
    return names


# ---------------------------------------------------------------- DRS
def build_drs(data: Path) -> None:
    aero = data / "aero.ini"
    sections = parse_sections(aero.read_text(errors="ignore"))
    rear = next(lines for name, lines in sections if name == f"WING_{REAR_WING}")

    def gain(key: str) -> float:
        return float(next(l for l in rear if l.startswith(key + "=")).split("=")[1].split(";")[0])

    cl, cd = gain("CL_GAIN"), gain("CD_GAIN")
    flap_angle = gain("ANGLE")
    flap = [l for l in rear]
    flap[0] = f"[WING_{FLAP_WING}]"
    set_key(flap, "NAME", "DRS")
    set_key(flap, "POSITION", "0,0.50,-1.85")
    set_key(flap, "CL_GAIN", f"{cl * FLAP_SHARE:.4f}")
    set_key(flap, "CD_GAIN", f"{cd * FLAP_SHARE:.4f}")
    set_key(rear, "CL_GAIN", f"{cl * (1 - FLAP_SHARE):.4f}")
    set_key(rear, "CD_GAIN", f"{cd * (1 - FLAP_SHARE):.4f}")

    # Klappe ohne Geschwindigkeitsregler und ohne Setup-Eintrag: fester Winkel, damit die
    # Animation (25 Grad zu, 0 Grad offen) immer zur Physik passt
    out = []
    for name, lines in sections:
        if name == f"WING_{FLAP_WING}" or (name.startswith("DYNAMIC_CONTROLLER_") and f"WING={FLAP_WING}" in lines):
            continue
        out.extend(lines)
        if name == f"WING_{REAR_WING}":
            out.append("")
            out.append(f"; DRS-Klappe: {FLAP_SHARE:.0%} des Heckfluegels, Winkel 0 bei offenem DRS (drs.ini)")
            out.extend(flap)
    aero.write_text("\n".join(out) + "\n")

    (data / "drs.ini").write_text(f"[WING_{FLAP_WING}]\nEFFECT=0\n")
    (data / "wing_animations.ini").write_text(
        "[HEADER]\nVERSION=2\n\n[ANIMATION_0]\n"
        f"WING={FLAP_WING}\nFILE=car_wing.ksanim\nMIN=0\nMAX={flap_angle:g}\nINVERTED=1\nSPEED=8\n")

    setup = data / "setup.ini"
    text = setup.read_text(errors="ignore")
    setup.write_text(text.replace("NAME=Rear wing\n", "NAME=Rear wing main\n"))
    print(f"DRS: Heckfluegel geteilt {1 - FLAP_SHARE:.0%} / {FLAP_SHARE:.0%}, drs.ini und wing_animations.ini angelegt")


def build_visuals(car: Path, cars: Path) -> None:
    """Klappe im Modell abtrennen (Haupt-kn5 und LOD B) und Animation schreiben."""
    for name in ("ferrari_f2004.kn5", "ferrari_f2004_lod_B.kn5"):
        src = cars / BASE_CAR / name
        if src.exists() and not make_flap.split_flap(src, car / name):
            print(f"Hinweis: keine Klappe in {name} gefunden, Datei bleibt original")
    make_flap.write_anim(car / "animations" / "car_wing.ksanim")


def pack_data(car: Path) -> None:
    """data-Ordner als data.acd packen; AC laedt DRS nur aus der acd. Entpackte Kopie nach tools/out."""
    spec = importlib.util.spec_from_file_location("acd_pack", ACD_UNPACK.with_name("acd_pack.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.pack(str(car / "data"), str(car / "data.acd"))
    keep = HERE / "out" / "data_unpacked"
    if keep.exists():
        shutil.rmtree(keep)
    shutil.move(str(car / "data"), str(keep))
    print(f"data.acd gepackt, entpackte Kopie unter {keep}")


# ---------------------------------------------------------------- KERS, Namen
def build_kers(data: Path) -> None:
    for f in ("kers.ini", "kers_torque.lut"):
        shutil.copy2(PHYSICS / f, data / f)
    print("KERS: kers.ini und kers_torque.lut uebernommen")


def update_names(car: Path, compounds: list[str]) -> None:
    car_ini = car / "data" / "car.ini"
    car_ini.write_text(re.sub(r"SCREEN_NAME=.*", f"SCREEN_NAME={SCREEN_NAME}", car_ini.read_text(errors="ignore")))

    ui = car / "ui" / "ui_car.json"
    meta = json.loads(ui.read_text(encoding="utf-8-sig"), strict=False)
    meta["name"] = SCREEN_NAME
    meta["parent"] = BASE_CAR
    meta["tags"] = sorted(set(meta.get("tags", [])) | {"drs", "kers", "eigenbau"})
    meta["description"] = (
        "Ferrari F2004 (Kunos) mit DRS und KERS nach dem Reglement 2013 und den Pirelli-Mischungen 2018 "
        f"({', '.join(compounds)}) der Formula Hybrid 2018. DRS: Klappe mit {FLAP_SHARE:.0%} Anteil am "
        "Heckfluegel, offen etwa 14 % weniger Widerstand und 42 % weniger Heckfluegel-Abtrieb. "
        "KERS: 60 kW, 400 kJ pro Runde, 6,6 s. Reifen in 2004-Groesse mit 2018-Gummi. "
        "Keine bewegliche Klappe am Modell. Stand im Repo assetto-claude-mods.<br><br>"
        + meta.get("description", "")
    )
    meta["specs"]["bhp"] = "865 bhp + 80 bhp KERS"
    meta["specs"]["weight"] = "605 kg"
    ui.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print("car.ini und ui_car.json benannt")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ac", type=Path, default=AC_DEFAULT)
    args = ap.parse_args()
    cars = args.ac / "content" / "cars"
    for c in (BASE_CAR, TYRE_CAR):
        if not (cars / c).is_dir():
            raise SystemExit(f"Quellauto fehlt: {cars / c}")

    car = create_car(cars)
    data = car / "data"
    tyre_src = HERE / "out" / "_tyre_src"
    if tyre_src.exists():
        shutil.rmtree(tyre_src)
    unpack(cars, TYRE_CAR, tyre_src)
    compounds = build_tyres(tyre_src, data)
    shutil.rmtree(tyre_src)
    build_drs(data)
    build_kers(data)
    update_names(car, compounds)
    build_visuals(car, cars)
    pack_data(car)
    print(f"fertig: {car}")


if __name__ == "__main__":
    sys.exit(main())
