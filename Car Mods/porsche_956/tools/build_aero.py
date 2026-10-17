"""Baut den data-Ordner des Porsche 956 Venturi aus dem Basis-Mod und dem Venturi-Modell.

  python build_aero.py          schreibt ../physics/data (aero.ini, car.ini, LUTs, Kennfelder)
  python build_aero.py --check  nur rechnen und Kennzahlen ausgeben, nichts schreiben

Ablauf:
  1. Alle Dateien aus reference/vac_groupc_956/data nach physics/data kopieren.
  2. car.ini auf VERSION=extended-2 setzen (schaltet CSP Extended Physics frei).
  3. aero.ini neu erzeugen: Karosserie (nur Widerstand), Frontfluegel, Heckfluegel und der
     Unterboden als [MAP_0]. Der Diffusor-Fluegel des Basis-Mods und sein Controller entfallen,
     der Unterboden kommt vollstaendig aus den Kennfeldern von venturi_model.py.
  4. Fluegel-Gains so skalieren, dass bei statischer Bodenfreiheit die Zielwerte aus
     tools/out/summary.json erreicht werden (cla_wing_front, cla_wing_rear, cda_total_design).

Voraussetzung: venturi_model.py wurde vorher ausgefuehrt (physics/data/aero/*.2Dlut, out/summary.json).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
REF = MOD / "reference" / "vac_groupc_956" / "data"
OUT = MOD / "physics" / "data"
AERO_DIR = OUT / "aero"
SUMMARY = HERE / "out" / "summary.json"

RHO = 1.225
G = 9.81

# Im Spiel gemessen (Ride Height Monitor, Messung 6 und Stand-Messung 2026-10-17) mit den 1983er
# Reifenmassen (Radius 0,325 beide, BASEY 0,010/-0,030): statisch 0,042/0,074 m. Dabei galten laut
# Setup-Bildschirm die Stangenlaengen 0,000 vorn und 0,016 hinten, nicht die aus der Datei: Das
# gespeicherte Setup ueberschreibt ROD_LENGTH, Einheit im Setup ist 0,1 mm (160 = 0,016 m).
MEASURED_STATIC_RH = (0.042, 0.074)
MEASURED_ROD = (0.000, 0.016)
MEASURED_WITH_TYRE_RADIUS = (0.325, 0.325)
MEASURED_ROD_BASE = (0.011, 0.0375)     # Stangenlaengen der Messungen 2 bis 5 (Federweg-Referenz)

# Fahrwerksabstimmung (Zielwerte aus venturi_model.py Config): Design-Hoehe 55/85 mm,
# Radraten 140/190 N/mm. ROD_LENGTH wirkt etwa 1:1 auf die Bodenfreiheit (im Spiel pruefen).
# Motor Typ 935/76, Schaetzung (research/01-technische-daten.md): offiziell 620 PS bei 8200/min
# und 1,3 bar, 600 Nm bei 5000; Porsche gab konservativ an. Hier: 1,3 bar = Quali (Regler 100 %),
# 1,2 bar Rennen (92 %), 1,1 bar Le Mans (85 %). AC: Moment = power.lut * (1 + Summe Ladedruck).
ENGINE = {
    "boost_per_turbo": 0.65,                 # zwei Turbos, zusammen 1,3 bar bei 100 %
    "default_adjustment": 0.92,              # Rennstufe 1,2 bar
    "limiter": 8560,
    # Zielmoment in Nm bei 1,3 bar ueber Drehzahl (Schaetzung)
    "torque_full_boost": [(0, 60), (1000, 150), (2000, 230), (3000, 330), (3500, 420), (4000, 510),
                          (4500, 570), (5000, 600), (5500, 600), (6000, 600), (6500, 598),
                          (7000, 592), (7500, 585), (8000, 578), (8200, 575), (8560, 545), (9000, 500)],
    "mass_total": 895,                       # 820 kg plus 75 kg Fahrer
    # Getriebe Ring 1983 (Schaetzung): Fuenfter bei ~320 km/h und 8400/min, Radius hinten 0,33 m
    # Fahrer-Setup vom 2026-10-14: 14/37, 18/34, 22/29, 26/26, 28/23 (rto-Saetze des Basis-Mods)
    "gears": [37 / 14, 34 / 18, 29 / 22, 26 / 26, 23 / 28],
    "final": 3.875,                          # 8/31 aus final.rto; Fuenfter dann 335 km/h am Begrenzer (zu pruefen)
}

# Reifen 1983: Dunlop 280/650-13 vorn (956-007 am Ring mit 13-Zoll-Felgen), 350/650-16 hinten.
# Der Basis-Mod hat vorn Radius 0,28 m (560 mm), real 650 mm. Groesserer Radius hebt in AC
# Schwerpunkt und Karosserie an, deshalb BASEY und ROD_LENGTH um die Differenz korrigieren,
# damit Schwerpunkthoehe und statische Bodenfreiheit unveraendert bleiben.
TYRES = {
    "radius": (0.325, 0.325),
    "rim_radius": (0.165 + 0.0254, 0.2032 + 0.0254),   # 13 und 16 Zoll, plus 1 Zoll wie in AC ueblich
    "width": (0.280, 0.350),
}

SUSPENSION = {
    "rh_design": (0.055, 0.085),
    "wheel_rate": (140000, 190000),      # N/m je Rad
    "setup_spring_range": ((100, 180), (150, 240)),  # kN/m, Setup-Schieber
}


# ---------------------------------------------------------------- Hilfsfunktionen

def read_lut(path: Path) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or "|" not in line:
            continue
        a, b = line.split("|", 1)
        xs.append(float(a))
        ys.append(float(b))
    return np.array(xs), np.array(ys)


def lut(path: Path, x: float) -> float:
    xs, ys = read_lut(path)
    return float(np.interp(x, xs, ys))


def read_2dlut(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = [r.split() for r in path.read_text().splitlines() if r.strip()]
    xs = np.array([float(v) for v in rows[0]])
    ys = np.array([float(r[0]) for r in rows[1:]])
    table = np.array([[float(v) for v in r[1:]] for r in rows[1:]])
    return xs, ys, table


def lut2d(path: Path, x: float, y: float) -> float:
    """Bilineare Interpolation, x = vorn, y = hinten (wie im CSP-Format)."""
    xs, ys, t = read_2dlut(path)
    i = int(np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2))
    j = int(np.clip(np.searchsorted(ys, y) - 1, 0, len(ys) - 2))
    fx = np.clip((x - xs[i]) / (xs[i + 1] - xs[i]), 0, 1)
    fy = np.clip((y - ys[j]) / (ys[j + 1] - ys[j]), 0, 1)
    a = t[j, i] * (1 - fx) + t[j, i + 1] * fx
    b = t[j + 1, i] * (1 - fx) + t[j + 1, i + 1] * fx
    return float(a * (1 - fy) + b * fy)


def ini_value(text: str, section: str, key: str) -> str:
    sec = re.search(rf"\[{re.escape(section)}\](.*?)(?=\n\[|\Z)", text, re.S)
    if not sec:
        raise KeyError(f"[{section}] fehlt")
    m = re.search(rf"^\s*{re.escape(key)}\s*=\s*([^;\n]*)", sec.group(1), re.M)
    if not m:
        raise KeyError(f"{section}.{key} fehlt")
    return m.group(1).strip()


def q_dyn(v_kmh: float) -> float:
    v = v_kmh / 3.6
    return 0.5 * RHO * v * v


# ---------------------------------------------------------------- Geometrie des Basis-Mods

def static_geometry() -> dict:
    """Schwerpunkthoehe und statische Bodenfreiheit aus suspensions.ini, tyres.ini, car.ini.

    AC: Hoehe des Schwerpunkts ueber Boden je Achse = Reifenradius - BASEY. Die Bodenfreiheit,
    die Apps und (nach Wiki) die Aero-Map sehen, ist der Abstand des PICKUP-Punkts aus car.ini
    zum Boden. ROD_LENGTH verschiebt das zusaetzlich, der genaue Wert ist im Spiel zu pruefen.
    """
    sus = (REF / "suspensions.ini").read_text()
    tyr = (REF / "tyres.ini").read_text()
    car = (REF / "car.ini").read_text()
    rf = float(ini_value(tyr, "FRONT", "RADIUS"))
    rr = float(ini_value(tyr, "REAR", "RADIUS"))
    bf = float(ini_value(sus, "FRONT", "BASEY"))
    br = float(ini_value(sus, "REAR", "BASEY"))
    cg_loc = float(ini_value(sus, "BASIC", "CG_LOCATION"))
    rod_f = float(ini_value(sus, "FRONT", "ROD_LENGTH"))
    rod_r = float(ini_value(sus, "REAR", "ROD_LENGTH"))
    pick_f = float(ini_value(car, "RIDE", "PICKUP_FRONT_HEIGHT"))
    pick_r = float(ini_value(car, "RIDE", "PICKUP_REAR_HEIGHT"))
    cg_f = rf - bf
    cg_r = rr - br
    cg_h = cg_loc * cg_f + (1 - cg_loc) * cg_r
    geo_f = cg_f + pick_f + rod_f
    geo_r = cg_r + pick_r + rod_r
    tf, tr = SUSPENSION["rh_design"]
    d_rf = TYRES["radius"][0] - rf          # Radiusaenderung gegenueber Basis-Mod (fuer BASEY)
    d_rr = TYRES["radius"][1] - rr
    # Radiusaenderung gegenueber der Messung (fuer ROD_LENGTH); 0, solange TYRES unveraendert
    m_rf = TYRES["radius"][0] - MEASURED_WITH_TYRE_RADIUS[0]
    m_rr = TYRES["radius"][1] - MEASURED_WITH_TYRE_RADIUS[1]
    return {
        "cg_height": cg_h,
        "rh_front": tf,
        "rh_rear": tr,
        "rh_front_geometry_estimate": geo_f,
        "rh_rear_geometry_estimate": geo_r,
        # neue Stangenlaengen: gemessene Hoehe + Delta zur Zielhoehe, minus Reifenradius-Zuwachs
        "rod_front": MEASURED_ROD[0] + (tf - MEASURED_STATIC_RH[0]) - m_rf,
        "rod_rear": MEASURED_ROD[1] + (tr - MEASURED_STATIC_RH[1]) - m_rr,
        # BASEY so, dass Schwerpunkt je Achse auf gleicher Hoehe bleibt (CoG = Radius - BASEY)
        "basey_front": bf + d_rf,
        "basey_rear": br + d_rr,
        "tyre_dr_front": d_rf,
        "tyre_dr_rear": d_rr,
    }


# ---------------------------------------------------------------- Aero-Rechnung

def compute(summary: dict, geo: dict) -> dict:
    hf, hr = geo["rh_front"], geo["rh_rear"]
    cg_h = geo["cg_height"]

    # Fluegel des Basis-Mods bei ihren Standardwinkeln
    front_angle, rear_angle = 2.0, 8.0
    front_chord, front_span = 1.0, 1.69
    rear_chord, rear_span = 0.8, 1.69
    body_chord, body_span = 1.0, 1.74
    front_pos_y, body_pos_y = -0.244, 0.25

    # Hoehen-Multiplikatoren der Fluegel-LUTs: Eingang ist Hoehe des Fluegels ueber Boden
    front_h = cg_h + front_pos_y
    body_h = cg_h + body_pos_y
    front_gh_cl = lut(REF / "height_front_CL.lut", front_h)
    front_gh_cd = lut(REF / "height_front_CD.lut", front_h)
    body_gh_cd = lut(REF / "height_body_CD.lut", body_h)

    front_cla_base = lut(REF / "wing_front_AOA_CL.lut", front_angle) * front_chord * front_span * front_gh_cl
    rear_cla_base = lut(REF / "wing_rear_AOA_CL.lut", rear_angle) * rear_chord * rear_span
    front_cda = lut(REF / "wing_front_AOA_CD.lut", front_angle) * front_chord * front_span * front_gh_cd
    rear_cda = lut(REF / "wing_rear_AOA_CD.lut", rear_angle) * rear_chord * rear_span
    body_cda_base = lut(REF / "wing_body_AOA_CD.lut", 0.0) * body_chord * body_span * body_gh_cd

    # Unterboden aus den Kennfeldern bei statischer Bodenfreiheit
    ub_cla = lut2d(AERO_DIR / "underbody_cl_rh.2Dlut", hf, hr)
    ub_cda = lut2d(AERO_DIR / "underbody_cd_rh.2Dlut", hf, hr)
    ub_bal = lut2d(AERO_DIR / "underbody_balance_rh.2Dlut", hf, hr)

    # Gains: Fluegel auf Zielwerte des Modells, Karosserie-Widerstand fuellt den Rest auf
    front_gain = summary["cla_wing_front"] / front_cla_base
    rear_gain = summary["cla_wing_rear"] / rear_cla_base
    body_cd_gain = (summary["cda_total_design"] - ub_cda - front_cda - rear_cda) / body_cda_base
    if body_cd_gain < 0.3:
        raise SystemExit(f"Karosserie-CD-Gain {body_cd_gain:.2f} unplausibel, Zielwiderstand zu klein")

    total_cla = ub_cla + summary["cla_wing_front"] + summary["cla_wing_rear"]
    total_cda = ub_cda + front_cda + rear_cda + body_cda_base * body_cd_gain
    front_share = (ub_cla * ub_bal + summary["cla_wing_front"]) / total_cla

    return {
        "rh_front_static": hf,
        "rh_rear_static": hr,
        "rod_front": geo["rod_front"],
        "rod_rear": geo["rod_rear"],
        "basey_front": geo["basey_front"],
        "basey_rear": geo["basey_rear"],
        "tyre_dr_front": geo["tyre_dr_front"],
        "tyre_dr_rear": geo["tyre_dr_rear"],
        "wheel_rate_front": SUSPENSION["wheel_rate"][0],
        "wheel_rate_rear": SUSPENSION["wheel_rate"][1],
        "cg_height": cg_h,
        "front_cl_gain": front_gain,
        "rear_cl_gain": rear_gain,
        "body_cd_gain": body_cd_gain,
        "underbody_cla_static": ub_cla,
        "underbody_cda_static": ub_cda,
        "underbody_front_balance_static": ub_bal,
        "total_cla_static": total_cla,
        "total_cda_static": total_cda,
        "front_balance_static": front_share,
        "downforce_kg": {
            v: round(total_cla * q_dyn(v) / G) for v in (100, 150, 200, 250, 300, 322)
        },
    }


# ---------------------------------------------------------------- Dateien schreiben

AERO_TEMPLATE = """\
; Porsche 956 Venturi, erzeugt von tools/build_aero.py. Nicht von Hand aendern, sondern das
; Skript anpassen. Basis: VAC Porsche 956 (vac_groupc_956). Der Unterboden kommt als CSP
; Aero Map aus physics/data/aero (venturi_model.py), die Fluegel bleiben klassische [WING].
; Zielwerte bei statischer Bodenfreiheit vorn {rh_front:.3f} m, hinten {rh_rear:.3f} m:
;   Cl*A gesamt {total_cla:.3f} (Unterboden {ub_cla:.3f}), Cd*A gesamt {total_cda:.3f}, Balance vorn {bal:.2f}

[HEADER]
VERSION=3

[WING_0]
NAME=BODY
CHORD=1
SPAN=1.74
POSITION=0,0.25,-0.060
LUT_AOA_CL=wing_body_AOA_CL.lut
LUT_GH_CL=
CL_GAIN=0
LUT_AOA_CD=wing_body_AOA_CD.lut
LUT_GH_CD=height_body_CD.lut
CD_GAIN={body_cd_gain:.3f}
ANGLE=0
ZONE_FRONT_CL=0
ZONE_FRONT_CD=0.005
ZONE_REAR_CL=0
ZONE_REAR_CD=0.005
ZONE_LEFT_CL=0
ZONE_LEFT_CD=0.01
ZONE_RIGHT_CL=0
ZONE_RIGHT_CD=0.01
YAW_CL_GAIN=0.0

[WING_1]
NAME=FRONT
CHORD=1
SPAN=1.69
POSITION=0,-0.244,2.400
LUT_AOA_CL=wing_front_AOA_CL.lut
LUT_GH_CL=height_front_CL.lut
CL_GAIN={front_cl_gain:.3f}
LUT_AOA_CD=wing_front_AOA_CD.lut
LUT_GH_CD=height_front_CD.lut
CD_GAIN=1.0
ANGLE=2
ZONE_FRONT_CL=0.015
ZONE_FRONT_CD=0.015
ZONE_REAR_CL=0
ZONE_REAR_CD=0
ZONE_LEFT_CL=0
ZONE_LEFT_CD=0
ZONE_RIGHT_CL=0
ZONE_RIGHT_CD=0
YAW_CL_GAIN=-0.15

[WING_2]
NAME=REAR
CHORD=0.8
SPAN=1.69
POSITION=0,0.50,-2.100
LUT_AOA_CL=wing_rear_AOA_CL.lut
LUT_GH_CL=
CL_GAIN={rear_cl_gain:.3f}
LUT_AOA_CD=wing_rear_AOA_CD.lut
LUT_GH_CD=
CD_GAIN=1.0
ANGLE=8
ZONE_FRONT_CL=0
ZONE_FRONT_CD=0
ZONE_REAR_CL=0.01
ZONE_REAR_CD=0.015
ZONE_LEFT_CL=0
ZONE_LEFT_CD=0
ZONE_RIGHT_CL=0
ZONE_RIGHT_CD=0
YAW_CL_GAIN=-0.17

; Unterboden als Venturi-Kennfeld (CSP Extended Physics, car.ini VERSION=extended-2).
; Eingang: Bodenfreiheit vorn (x) und hinten (y) in Metern. FRONT/REAR_RH_OFFSET verschieben
; den Eingang, falls die im Spiel gemessene Bodenfreiheit nicht zur Modellannahme passt.
[MAP_0]
NAME=Unterboden Kurzheck
MAP_CL_RH=aero/underbody_cl_rh.2Dlut
MAP_CD_RH=aero/underbody_cd_rh.2Dlut
MAP_BALANCE_RH=aero/underbody_balance_rh.2Dlut
MAP_YAW_CL=aero/underbody_yaw_cl.lut
MAP_YAW_BALANCE=aero/underbody_yaw_balance.lut
FRONT_RH_OFFSET=0.000
REAR_RH_OFFSET=0.000
CL_MULT=1.00
CD_MULT=1.00
BALANCE_OFFSET=0.00
INTERPOLATION=CUBIC
DRAG_OFFSET=0.00, 0.35
; Kleine Werte = mehr Verzoegerung = mehr Aufschaukeln. Im Test anpassen.
FRONT_FORCE_DELAY=0.035
REAR_FORCE_DELAY=0.030
DRAG_FORCE_DELAY=0.045
"""


def set_key(text: str, section: str, key: str, value: str) -> str:
    """Ersetzt key=... innerhalb [section], Kommentar am Zeilenende bleibt erhalten."""
    m = re.search(rf"\[{re.escape(section)}\]", text)
    if not m:
        raise KeyError(f"[{section}] fehlt")
    start = m.end()
    nxt = re.search(r"\n\[", text[start:])
    end = start + nxt.start() if nxt else len(text)
    body, n = re.subn(rf"^(\s*{re.escape(key)}\s*=\s*)[^;\n]*", lambda mm: mm.group(1) + value, text[start:end], count=1, flags=re.M)
    if n == 0:
        raise KeyError(f"{section}.{key} fehlt")
    return text[:start] + body + text[end:]


def tune_suspension(res: dict) -> None:
    sus_p = OUT / "suspensions.ini"
    sus = sus_p.read_text()
    sus = set_key(sus, "FRONT", "ROD_LENGTH", f"{res['rod_front']:.4f}")
    sus = set_key(sus, "REAR", "ROD_LENGTH", f"{res['rod_rear']:.4f}")
    sus = set_key(sus, "FRONT", "SPRING_RATE", str(res["wheel_rate_front"]))
    sus = set_key(sus, "REAR", "SPRING_RATE", str(res["wheel_rate_rear"]))
    sus = set_key(sus, "FRONT", "BASEY", f"{res['basey_front']:.4f}")
    sus = set_key(sus, "REAR", "BASEY", f"{res['basey_rear']:.4f}")

    ref = (REF / "suspensions.ini").read_text()
    for sec, d_r, rod_ref in (("FRONT", res["tyre_dr_front"], MEASURED_ROD_BASE[0]),
                              ("REAR", res["tyre_dr_rear"], MEASURED_ROD_BASE[1])):
        # Querlenkerpunkte bleiben unveraendert: ob sie in AC relativ zum Schwerpunkt oder zur
        # Radmitte liegen, ist nicht belegt. Eine Verschiebung um d_r waere Spekulation.
        # Anschlaege: Einfederweg in AC = BUMPSTOP_UP + ROD_LENGTH. Den Federweg beibehalten, den die
        # gut funktionierenden Messungen 2 bis 5 hatten (Basis-Anschlag plus damalige Stangenlaenge).
        up_ref = float(ini_value(ref, sec, "BUMPSTOP_UP"))
        packer_ref = float(ini_value(ref, sec, "PACKER_RANGE"))
        rod_new = res["rod_front"] if sec == "FRONT" else res["rod_rear"]
        sus = set_key(sus, sec, "BUMPSTOP_UP", f"{up_ref + rod_ref - rod_new:.4f}")
        sus = set_key(sus, sec, "PACKER_RANGE", f"{packer_ref + rod_ref - rod_new:.4f}")
    sus_p.write_text(sus)

    tyr_p = OUT / "tyres.ini"
    tyr = tyr_p.read_text()
    for sec, i in (("FRONT", 0), ("REAR", 1)):
        tyr = set_key(tyr, sec, "RADIUS", f"{TYRES['radius'][i]:.4f}")
        tyr = set_key(tyr, sec, "RIM_RADIUS", f"{TYRES['rim_radius'][i]:.4f}")
        tyr = set_key(tyr, sec, "WIDTH", f"{TYRES['width'][i]:.3f}")
    tyr_p.write_text(tyr)

    set_p = OUT / "setup.ini"
    setup = set_p.read_text()
    (fmin, fmax), (rmin, rmax) = SUSPENSION["setup_spring_range"]
    for sec, lo, hi in (("SPRING_RATE_LF", fmin, fmax), ("SPRING_RATE_RF", fmin, fmax),
                        ("SPRING_RATE_LR", rmin, rmax), ("SPRING_RATE_RR", rmin, rmax)):
        setup = set_key(setup, sec, "MIN", str(lo))
        setup = set_key(setup, sec, "MAX", str(hi))
    # Setup-Einheit fuer die Stangenlaenge ist 0,1 mm (Bildschirm 2026-10-17: 160 = 0,016 m).
    # Bereich so, dass die Standardwerte aus der Datei und +/- 30 mm darin liegen.
    rf, rr = round(res["rod_front"] * 10000), round(res["rod_rear"] * 10000)
    for sec, mid in (("ROD_LENGTH_LF", rf), ("ROD_LENGTH_RF", rf), ("ROD_LENGTH_LR", rr), ("ROD_LENGTH_RR", rr)):
        setup = set_key(setup, sec, "MIN", str(mid - 300))
        setup = set_key(setup, sec, "MAX", str(mid + 300))
        setup = set_key(setup, sec, "STEP", "10")
    set_p.write_text(setup)


def tune_engine() -> dict:
    boost_total = 2 * ENGINE["boost_per_turbo"]
    lut = [(rpm, nm / (1 + boost_total)) for rpm, nm in ENGINE["torque_full_boost"]]
    (OUT / "power.lut").write_text("".join(f"{rpm}|{nm:.1f}\n" for rpm, nm in lut))

    eng_p = OUT / "engine.ini"
    eng = eng_p.read_text()
    eng = set_key(eng, "ENGINE_DATA", "LIMITER", str(ENGINE["limiter"]))
    eng = set_key(eng, "ENGINE_DATA", "DEFAULT_TURBO_ADJUSTMENT", f"{ENGINE['default_adjustment']:.2f}")
    for sec in ("TURBO_0", "TURBO_1"):
        eng = set_key(eng, sec, "MAX_BOOST", f"{ENGINE['boost_per_turbo']:.2f}")
        eng = set_key(eng, sec, "WASTEGATE", f"{ENGINE['boost_per_turbo']:.2f}")
        eng = set_key(eng, sec, "DISPLAY_MAX_BOOST", f"{ENGINE['boost_per_turbo']:.2f}")
    eng = set_key(eng, "DAMAGE", "TURBO_BOOST_THRESHOLD", f"{ENGINE['boost_per_turbo'] + 0.05:.2f}")
    eng_p.write_text(eng)

    car_p = OUT / "car.ini"
    car_p.write_text(set_key(car_p.read_text(), "BASIC", "TOTALMASS", str(ENGINE["mass_total"])))

    dt_p = OUT / "drivetrain.ini"
    dt = dt_p.read_text()
    for i, g in enumerate(ENGINE["gears"], 1):
        dt = set_key(dt, "GEARS", f"GEAR_{i}", f"{g:.2f}")
    dt = set_key(dt, "GEARS", "FINAL", f"{ENGINE['final']:.2f}")
    dt_p.write_text(dt)

    peak = {}
    for name, adj in (("quali 1,3 bar", 1.0), ("rennen 1,2 bar", ENGINE["default_adjustment"]), ("le mans 1,1 bar", 0.85)):
        b = boost_total * adj
        peak[name] = max(rpm * nm * (1 + b) / 9549 * 1.36 for rpm, nm in lut)
    v_top = ENGINE["limiter"] / 60 * 2 * 3.14159 * TYRES["radius"][1] / (ENGINE["gears"][-1] * ENGINE["final"]) * 3.6
    return {"peak_ps": peak, "v_top_kmh_limiter": v_top}


def write_data(res: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src in REF.iterdir():
        if src.is_file():
            shutil.copy2(src, OUT / src.name)

    car = (OUT / "car.ini").read_text()
    car = re.sub(r"^VERSION\s*=\s*2\b[^\n]*", "VERSION=extended-2 ; CSP Extended Physics (Aero Map)", car, count=1, flags=re.M)
    car = re.sub(r"^SCREEN_NAME\s*=.*$", "SCREEN_NAME=Porsche 956 Venturi (WIP)", car, flags=re.M)
    car = re.sub(r"^SHORT_NAME\s*=.*$", "SHORT_NAME=956 Venturi", car, flags=re.M)
    (OUT / "car.ini").write_text(car)
    tune_suspension(res)
    res["engine"] = tune_engine()

    (OUT / "aero.ini").write_text(AERO_TEMPLATE.format(
        rh_front=res["rh_front_static"], rh_rear=res["rh_rear_static"],
        total_cla=res["total_cla_static"], ub_cla=res["underbody_cla_static"],
        total_cda=res["total_cda_static"], bal=res["front_balance_static"],
        body_cd_gain=res["body_cd_gain"], front_cl_gain=res["front_cl_gain"],
        rear_cl_gain=res["rear_cl_gain"],
    ))
    (HERE / "out" / "build_aero.json").write_text(json.dumps(res, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="nur rechnen, nichts schreiben")
    args = ap.parse_args()

    if not SUMMARY.exists() or not (AERO_DIR / "underbody_cl_rh.2Dlut").exists():
        raise SystemExit("Erst venturi_model.py ausfuehren (summary.json und Kennfelder fehlen)")
    summary = json.loads(SUMMARY.read_text())
    res = compute(summary, static_geometry())

    print(f"Ziel-Bodenfreiheit statisch: vorn {res['rh_front_static']*1000:.0f} mm, hinten {res['rh_rear_static']*1000:.0f} mm "
          f"(ROD_LENGTH {res['rod_front']:.4f}/{res['rod_rear']:.4f}, BASEY {res['basey_front']:.4f}/{res['basey_rear']:.4f}, "
          f"Radraten {res['wheel_rate_front']/1000:.0f}/{res['wheel_rate_rear']/1000:.0f} N/mm)")
    print(f"Gains: Front CL {res['front_cl_gain']:.3f}, Heck CL {res['rear_cl_gain']:.3f}, Karosserie CD {res['body_cd_gain']:.3f}")
    print(f"Unterboden statisch: Cl*A {res['underbody_cla_static']:.3f}, Cd*A {res['underbody_cda_static']:.3f}, Balance vorn {res['underbody_front_balance_static']:.2f}")
    print(f"Gesamt statisch: Cl*A {res['total_cla_static']:.3f}, Cd*A {res['total_cda_static']:.3f}, Balance vorn {res['front_balance_static']:.2f}")
    print("Abtrieb ohne Einfedern (kg): " + ", ".join(f"{v} km/h {kg}" for v, kg in res["downforce_kg"].items()))
    if args.check:
        return
    write_data(res)
    e = res["engine"]
    print("Motor: " + ", ".join(f"{k} {v:.0f} PS" for k, v in e["peak_ps"].items()) + f"; Fuenfter am Begrenzer {e['v_top_kmh_limiter']:.0f} km/h")
    print(f"Geschrieben: {OUT}")


if __name__ == "__main__":
    main()
