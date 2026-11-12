"""Macht aus einem Auto mit Team-Skins (Formula Hybrid von RSS) je Team ein eigenes Auto.

  python team_autos.py --ac <AC> --plan ../data/teams_2017.json            (zeigt nur, was entstehen würde)
  python team_autos.py --ac <AC> --plan ../data/teams_2017.json --apply

Je Team entsteht content/cars/<quelle>_<team> mit den Skins dieses Teams. Danach lassen sich Motor und
Abtrieb je Team einstellen wie bei den Cimmerian-Jahrgängen (acdini.py). Die Quelle wird nie verändert.

- Modell, Texturen, Skins, Animationen und Sound-Bank sind Hardlinks auf die Dateien der Quelle (kein
  zusätzlicher Platz). Hardlinks teilen den Inhalt: wer so eine Datei im Team-Ordner bearbeitet, ändert
  auch das Original. Klappt der Hardlink nicht (anderes Laufwerk), wird kopiert.
- data.acd wird neu geschrieben, weil AC sie mit dem Ordnernamen verschlüsselt; geändert ist nur
  SCREEN_NAME in car.ini. ui_car.json bekommt den Team-Namen, GUIDs.txt den neuen Ordnernamen.
- Die CSP-Konfiguration extension/config/cars/loaded/<quelle>.ini wird für jedes Team-Auto kopiert.
- Ein vorhandener Team-Ordner wird nie angefasst (dort können schon Physik-Änderungen liegen).
"""
import argparse
import json
import os
import shutil
from pathlib import Path

from acdini import CarData, acd_read, acd_write, generate_key, set_value

EIGENE = {"data.acd", "data.acd.bak"}      # nie verlinken
stat = {"link": 0, "kopie": 0}


def link(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst); stat["link"] += 1
    except OSError:
        shutil.copy2(src, dst); stat["kopie"] += 1


def link_tree(src, dst):
    for p in src.rglob("*"):
        if p.is_file(): link(p, dst / p.relative_to(src))


def build(ac, quelle, key, team, jahr):
    cars = ac / "content" / "cars"
    src, name = cars / quelle, f"{quelle}_{key}"
    dst = cars / name
    for p in src.iterdir():
        if p.is_file() and p.name.lower() not in EIGENE: link(p, dst / p.name)
        elif p.is_dir() and p.name.lower() not in ("skins", "sfx", "ui", "data"): link_tree(p, dst / p.name)
    for skin in team["skins"]:
        link_tree(src / "skins" / skin, dst / "skins" / skin)
    # Sound: Bank unter neuem Namen, Ereignispfade auf den neuen Ordner
    (dst / "sfx").mkdir(exist_ok=True)
    link(src / "sfx" / f"{quelle}.bank", dst / "sfx" / f"{name}.bank")
    guids = (src / "sfx" / "GUIDs.txt").read_bytes().decode("latin1")
    (dst / "sfx" / "GUIDs.txt").write_bytes(guids.replace(f"/cars/{quelle}/", f"/cars/{name}/").encode("latin1"))
    # Oberfläche
    (dst / "ui").mkdir(exist_ok=True)
    for p in (src / "ui").iterdir():
        if p.is_file() and p.name != "ui_car.json": shutil.copy2(p, dst / "ui" / p.name)
    ui = json.loads((src / "ui" / "ui_car.json").read_text(encoding="utf-8-sig"), strict=False)
    titel = f"F1 {jahr} {team['name']}"
    ui["name"] = titel
    ui["description"] = f"{team['name']}, Team-Auto aus {quelle} (eigene Physik je Team).<br><br>" + ui.get("description", "")
    ui["tags"] = ui.get("tags", []) + [f"f1 {jahr} teams"]
    (dst / "ui" / "ui_car.json").write_text(json.dumps(ui, indent=2, ensure_ascii=False), encoding="utf-8")
    # Physik: gleiche Dateien, neuer Schlüssel
    header, entries, _ = acd_read(src / "data.acd")
    for e in entries:
        if e[0].lower() == "car.ini":
            e[1] = set_value(e[1].decode("latin1"), "INFO", "SCREEN_NAME", titel)[0].encode("latin1")
    acd_write(dst / "data.acd", header, entries, generate_key(name.lower()).encode())
    # CSP
    cfg = ac / "extension" / "config" / "cars" / "loaded"
    if (cfg / f"{quelle}.ini").is_file() and not (cfg / f"{name}.ini").exists():
        shutil.copy2(cfg / f"{quelle}.ini", cfg / f"{name}.ini")
    # Prüfung: alles außer car.ini muss gleich der Quelle sein
    a, b = CarData(src), CarData(dst)
    anders = [n for n in a.files if a.files[n][1] != b.files[n][1]]
    assert set(a.files) == set(b.files) and anders == ["car.ini"], anders
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True); ap.add_argument("--plan", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    plan = json.load(open(a.plan, encoding="utf-8"))
    ac, quelle = Path(a.ac), plan["quelle"]
    src = ac / "content" / "cars" / quelle
    for key, team in plan["teams"].items():
        dst = src.parent / f"{quelle}_{key}"
        fehlt = [s for s in team["skins"] if not (src / "skins" / s / "ui_skin.json").is_file()]
        if fehlt:
            print(f"{dst.name}: Skins fehlen in der Quelle: {fehlt}"); continue
        if dst.exists():
            print(f"{dst.name}: vorhanden, nicht angefasst"); continue
        if not a.apply:
            print(f"{dst.name}: würde entstehen als 'F1 {plan['jahr']} {team['name']}' mit {team['skins']}  [Trockenlauf]"); continue
        build(ac, quelle, key, team, plan["jahr"])
        print(f"{dst.name}: gebaut, {len(team['skins'])} Skins")
    if a.apply: print(f"{stat['link']} Hardlinks, {stat['kopie']} Kopien")


if __name__ == "__main__":
    main()
