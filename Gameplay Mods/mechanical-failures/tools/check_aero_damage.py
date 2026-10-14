"""Prüft für alle F1-Autos der AC-Installation, ob Karosserieschaden in der aero.ini physikalisch wirkt.

  python check_aero_damage.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" [--all]

AC rechnet pro Flügel: CL = CL / (1 + ZONE_x_CL * DAMAGE), CD = CD * (1 + ZONE_x_CD * DAMAGE),
DAMAGE ist die Aufprallgeschwindigkeit der Zone (vorn, hinten, links, rechts) in km/h. Stehen alle ZONE_*_CL
auf 0, ist ein Schaden rein optisch. Liest aero.ini aus dem data-Ordner oder direkt aus der data.acd.
"""
import argparse
import json
import os
import re
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "Tools" / "acd"))
from acd_unpack import generate_key  # noqa: E402


def read_from_acd(acd_path, wanted):
    car = os.path.basename(os.path.dirname(acd_path))
    key = generate_key(car).encode()
    data = open(acd_path, "rb").read()
    off = 8 if struct.unpack_from("<i", data, 0)[0] < 0 else 0
    while off < len(data):
        ln = struct.unpack_from("<I", data, off)[0]; off += 4
        name = data[off:off + ln].decode("utf8", "ignore"); off += ln
        sz = struct.unpack_from("<I", data, off)[0]; off += 4
        if name.lower() == wanted:
            packed = data[off:off + sz * 4:4]
            return bytes(((packed[i] - key[i % len(key)]) & 0xFF) for i in range(sz)).decode("utf8", "ignore")
        off += sz * 4
    return None


def read_aero(cardir):
    f = cardir / "data" / "aero.ini"
    if f.is_file():
        return f.read_text(encoding="utf-8", errors="ignore")
    acd = cardir / "data.acd"
    return read_from_acd(str(acd), "aero.ini") if acd.is_file() else None


def analyse(text):
    wings, zone_cl, zone_cd = 0, 0.0, 0.0
    sec = None
    for raw in text.splitlines():
        line = raw.split(";")[0].split("//")[0].strip()
        m = re.match(r"^\[(.+)\]", line)
        if m:
            sec = m.group(1).upper(); wings += sec.startswith("WING_"); continue
        m = re.match(r"^(ZONE_(?:FRONT|REAR|LEFT|RIGHT)_(CL|CD))\s*=\s*([-\d.]+)", line, re.I)
        if m and sec and sec.startswith("WING_"):
            try:
                v = abs(float(m.group(3)))
            except ValueError:
                continue
            if m.group(2).upper() == "CL": zone_cl = max(zone_cl, v)
            else: zone_cd = max(zone_cd, v)
    return wings, zone_cl, zone_cd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    ap.add_argument("--all", action="store_true", help="alle Autos, nicht nur F1")
    ap.add_argument("--json", help="Ergebnis zusätzlich als JSON schreiben")
    a = ap.parse_args()
    cars = Path(a.ac) / "content" / "cars"
    out = {}
    for c in sorted(os.listdir(cars), key=str.lower):
        cardir = cars / c
        ui = cardir / "ui" / "ui_car.json"
        if not ui.is_file():
            continue
        try:
            j = json.loads(re.sub(r"[\x00-\x1f]", " ", ui.read_text(encoding="utf-8", errors="ignore")), strict=False)
        except Exception:
            j = {}
        tags = " ".join(j.get("tags") or [])
        blob = f"{c} {j.get('brand', '')} {j.get('name', '')} {tags}".lower()
        if not a.all and not re.search(r"\bf1\b|formula|grand prix|\bgp\b", blob):
            continue
        text = read_aero(cardir)
        if not text:
            out[c] = {"wings": 0, "zone_cl": None, "zone_cd": None, "verdict": "keine aero.ini"}
            continue
        wings, zcl, zcd = analyse(text)
        verdict = "physikalisch" if zcl > 0 else ("nur Widerstand" if zcd > 0 else "kosmetisch")
        out[c] = {"wings": wings, "zone_cl": zcl, "zone_cd": zcd, "verdict": verdict}
    counts = {}
    for c, r in out.items():
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
        print(f"{c:40s} {r['wings']:3d} Flügel  ZONE_CL max {r['zone_cl'] if r['zone_cl'] is not None else '-':>6}  ZONE_CD max {r['zone_cd'] if r['zone_cd'] is not None else '-':>6}  -> {r['verdict']}")
    print("\nZusammenfassung:", ", ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
