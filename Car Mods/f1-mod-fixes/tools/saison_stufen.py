"""Abtrieb aller Autos eines Jahrgangs auf die Werte einer Saisonphase setzen.

  python saison_stufen.py --ac <AC> --plan ../data/stufen_2009.json                     (zeigt die aktive Stufe)
  python saison_stufen.py --ac <AC> --plan ../data/stufen_2009.json --stufe 2 --apply

Die Faktoren der Plan-Datei gelten gegenüber aero.ini.basis im Autoordner. Diese Kopie entsteht beim ersten
Schreiben aus der aktuellen aero.ini, das Hin- und Herschalten summiert deshalb keine Rundungsfehler auf.
Geändert wird nur CL_GAIN, ohne --apply wird nur angezeigt.
"""
import argparse
import json
import re
from pathlib import Path

from acdini import CarData, get_value, set_value


def wings(text):
    return re.findall(r"^\[(WING_\d+)\]", text, re.M)


def read_basis(path):
    return path.read_bytes().decode("latin1") if path.is_file() else None


def scale(text, basis, factor):
    for sec in wings(basis):
        v = float(get_value(basis, sec, "CL_GAIN") or 0)
        if v: text, _ = set_value(text, sec, "CL_GAIN", f"{v * factor:.4f}")
    return text


def active(text, basis):
    for sec in wings(basis):
        v = float(get_value(basis, sec, "CL_GAIN") or 0)
        if v: return float(get_value(text, sec, "CL_GAIN")) / v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True); ap.add_argument("--plan", required=True)
    ap.add_argument("--stufe"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    stufen = json.load(open(a.plan, encoding="utf-8"))["stufen"]
    root = Path(a.ac) / "content" / "cars"
    if a.stufe is None:
        passt = set(stufen)
        for car in next(iter(stufen.values())):
            basis = read_basis(root / car / "aero.ini.basis")
            if basis is None:
                print(f"{car}: noch keine Basis"); passt = set(); continue
            f = active(CarData(root / car).read("aero.ini"), basis)
            passt &= {s for s in stufen if abs(stufen[s][car] - f) < 0.0006}
            print(f"{car}: Faktor {f:.4f}")
        print("Aktive Stufe:", ", ".join(sorted(passt)) or "keine")
        return
    for car, factor in stufen[a.stufe].items():
        cd, path = CarData(root / car), root / car / "aero.ini.basis"
        text = cd.read("aero.ini")
        basis = read_basis(path)
        if basis is None:
            basis = text
            if a.apply: path.write_bytes(text.encode("latin1"))
        new = scale(text, basis, factor)
        if a.apply and new != text: cd.write("aero.ini", new)
        print(f"{car}: Stufe {a.stufe}, Faktor {factor:.4f}" + ("" if a.apply else "  [Trockenlauf]"))


if __name__ == "__main__":
    main()
