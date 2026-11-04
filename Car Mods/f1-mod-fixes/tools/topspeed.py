"""Topspeed je Auto aus Luftwiderstand (mit dynamischen Flügel-Controllern bei Vollgas geradeaus), power.lut und letztem Gang.

  python topspeed.py --ac <AC> --prefix cim_2010_

Ohne Rollwiderstand und Getriebeverluste, die absoluten Werte sind deshalb zu hoch. Für den Vergleich der Teams reicht es.
"""
import argparse
import math
import re
from pathlib import Path
from acdini import CarData, get_value

RHO = 1.22

def lut(text, x):
    pts = sorted((float(a), float(b)) for a, b in (l.split(';')[0].split('|')[:2] for l in (text or "").splitlines() if '|' in l.split(';')[0]))
    if not pts: return None
    if x <= pts[0][0]: return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]

def sections(text, prefix):
    return {m.group(1): m.group(2) for m in re.finditer(r"^\[(" + prefix + r"_\d+)\]([^\[]*)", text, re.M)}

def g(blk, k):
    m = re.search(r"^\s*" + k + r"\s*=\s*([^;\r\n]*)", blk, re.M | re.I)
    return m.group(1).strip() if m else ""

def drag_area(cd, kmh):
    aero = cd.read("aero.ini")
    wings = sections(aero, "WING")
    ang = {int(k.split("_")[1]): float(g(b, "ANGLE") or 0) for k, b in wings.items()}
    inputs = {"SPEED_KMH": kmh, "GAS": 1.0, "STEER": 0.0, "BRAKE": 0.0}
    for k, b in sorted(sections(aero, "DYNAMIC_CONTROLLER").items()):
        w = int(g(b, "WING")); inp = g(b, "INPUT").upper()
        if inp not in inputs: continue
        v = lut(cd.read(g(b, "LUT")), inputs[inp])
        if v is None: continue
        a = ang[w] + v if g(b, "COMBINATOR").upper() == "ADD" else ang[w] * v
        ang[w] = min(max(a, float(g(b, "DOWN_LIMIT") or -99)), float(g(b, "UP_LIMIT") or 99))
    total = 0; parts = {}
    for k, b in list(wings.items()) + list(sections(aero, "FIN").items()):
        if k.startswith("FIN"): continue  # Seitenflossen: bei 0 Grad Gierwinkel kein Widerstand gerechnet
        w = int(k.split("_")[1])
        c = lut(cd.read(g(b, "LUT_AOA_CD")), ang[w]) or 0
        A = float(g(b, "CHORD")) * float(g(b, "SPAN"))
        x = A * c * float(g(b, "CD_GAIN") or 0)
        total += x; parts[g(b, "NAME")] = round(x, 3)
    return total, parts

def topspeed(cardir):
    cd = CarData(cardir)
    dt = cd.read("drivetrain.ini"); en = cd.read("engine.ini"); ty = cd.read("tyres.ini")
    n = int(get_value(dt, "GEARS", "COUNT")); top = float(get_value(dt, "GEARS", f"GEAR_{n}")); fin = float(get_value(dt, "GEARS", "FINAL"))
    lim = float(get_value(en, "ENGINE_DATA", "LIMITER")); r = float(get_value(ty, "REAR", "RADIUS"))
    pl = cd.read(g(re.search(r"\[HEADER\][^\[]*", en).group(0), "POWER_CURVE") or "power.lut")
    pts = [(float(a), float(b)) for a, b in (l.split('|')[:2] for l in pl.split() if '|' in l)]
    ps = max(rpm * t * 2 * math.pi / 60 for rpm, t in pts) / 735.5
    v_lim = lim / 60 * 2 * math.pi * r / (top * fin) * 3.6
    best = 0
    for kmh in range(250, 380):
        v = kmh / 3.6; rpm = v / (2 * math.pi * r) * top * fin * 60
        if rpm > lim: break
        F = lut(pl, rpm) * top * fin / r
        D = 0.5 * RHO * v * v * drag_area(cd, kmh)[0]
        if F >= D: best = kmh
    return best, v_lim, ps, drag_area(cd, 300)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True); ap.add_argument("--prefix", default="cim_2010_")
    a = ap.parse_args()
    root = Path(a.ac) / "content" / "cars"
    rows = []
    for p in sorted(root.iterdir()):
        if p.name.startswith(a.prefix) and ((p / "data.acd").is_file() or (p / "data").is_dir()):
            vt, vl, ps, (cda, _) = topspeed(p)
            rows.append((vt, p.name, vl, ps, cda))
    for vt, name, vl, ps, cda in sorted(rows, reverse=True):
        print(f"{name:26s} Topspeed {vt:3d} km/h  Begrenzer letzter Gang {vl:5.1f}  {ps:4.0f} PS  CdA(300) {cda:.3f}")


if __name__ == "__main__":
    main()
