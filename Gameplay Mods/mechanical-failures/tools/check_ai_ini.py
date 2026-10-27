"""KI-Einstellungen (ai.ini) aller F1-Autos der AC-Installation vergleichen, gruppiert nach Saison und Mod-Familie.

  python check_ai_ini.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" [--md ../research/data/ai_ini_scan.md]

Liest ai.ini aus dem data-Ordner oder der data.acd. Felder: AERO_HINT, [TYRES] HINT, BRAKE_HINT, TRAIL_HINT,
ULTRA_GRIP, GASGAIN, LOOKAHEAD BASE, STEER_GAIN, Schaltpunkte. Autos mit identischen Werten werden zusammengefasst.
"""
import argparse
import collections
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_aero_damage import read_from_acd  # noqa: E402

FIELDS = [("PHYSICS_HINTS", "AERO_HINT", "Aero"), ("TYRES", "HINT", "Reifen"), ("PEDALS", "BRAKE_HINT", "Bremse"),
          ("PEDALS", "TRAIL_HINT", "Trail"), ("ULTRA_GRIP", "VALUE", "UltraGrip"), ("PEDALS", "GASGAIN", "GasGain"),
          ("LOOKAHEAD", "BASE", "Lookahead"), ("STEER", "STEER_GAIN", "Steer"), ("GEARS", "UP", "Hoch"), ("GEARS", "DOWN", "Runter"),
          ("HEADER", "VERSION", "Ver")]


def parse_ini(text):
    data, sec = {}, None
    for raw in text.splitlines():
        line = raw.split(";")[0].split("//")[0].strip()
        m = re.match(r"^\[(.+)\]", line)
        if m:
            sec = m.group(1).upper(); data.setdefault(sec, {}); continue
        m = re.match(r"^([\w]+)\s*=\s*(.*)$", line)
        if m and sec:
            data[sec][m.group(1).upper()] = m.group(2).strip()
    return data


def family(car):
    c = car.lower()
    for pre in ("cim_", "acfl_", "f1_", "gp_", "msf_", "vrc_", "rss_", "asr_", "ks_", "trp_", "acr_", "mhr_"):
        if c.startswith(pre):
            return pre.rstrip("_")
    return c.split("_")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    ap.add_argument("--md", help="Markdown-Tabelle schreiben")
    a = ap.parse_args()
    cars = Path(a.ac) / "content" / "cars"
    rows = []
    for c in sorted(os.listdir(cars), key=str.lower):
        cardir = cars / c
        ui = cardir / "ui" / "ui_car.json"
        if not ui.is_file():
            continue
        try:
            j = json.loads(re.sub(r"[\x00-\x1f]", " ", ui.read_text(encoding="utf-8", errors="ignore")), strict=False)
        except Exception:
            j = {}
        blob = f"{c} {j.get('brand', '')} {j.get('name', '')} {' '.join(j.get('tags') or [])}".lower()
        if not re.search(r"\bf1\b|formula|grand prix|\bgp\b", blob):
            continue
        year = 0
        for m in re.findall(r"(?<!\d)(\d{4})(?!\d)", f"{c} {j.get('name', '')}"):
            if 1988 <= int(m) <= 2026:
                year = int(m); break
        if not year:
            try:
                year = int(j.get("year") or 0)
            except Exception:
                year = 0
        f = cardir / "data" / "ai.ini"
        acd = cardir / "data.acd"
        # wie AC: data.acd hat Vorrang, der data-Ordner zählt nur ohne acd
        text = read_from_acd(str(acd), "ai.ini") if acd.is_file() else (
            f.read_text(encoding="utf-8", errors="ignore") if f.is_file() else None)
        if not text:
            continue
        ini = parse_ini(text)
        vals = tuple(ini.get(s, {}).get(k, "-") for s, k, _ in FIELDS)
        rows.append((year, family(c), c, vals))

    groups = collections.OrderedDict()
    for year, fam, c, vals in sorted(rows):
        groups.setdefault((year, fam, vals), []).append(c)
    head = ["Saison", "Mod", "Autos"] + [n for _, _, n in FIELDS]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for (year, fam, vals), lst in groups.items():
        names = lst[0] if len(lst) == 1 else f"{lst[0]} +{len(lst) - 1}"
        lines.append("| " + " | ".join([str(year), fam, names] + list(vals)) + " |")
    out = "\n".join(lines)
    print(out)
    if a.md:
        Path(a.md).write_text("# KI-Einstellungen der F1-Autos (ai.ini)\n\nErzeugt mit tools/check_ai_ini.py. "
                              "Trail 1 = Trail-Braking an, GasGain klein = sanfter Gaseinsatz, UltraGrip = Gripaufschlag der KI.\n\n" + out + "\n",
                              encoding="utf-8")


if __name__ == "__main__":
    main()
