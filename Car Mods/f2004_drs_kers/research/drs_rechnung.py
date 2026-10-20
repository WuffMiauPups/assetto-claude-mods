"""Zahlen fuer 01-drs-herleitung.md: Anteil der DRS-Klappe am F2004-Heckfluegel.

  py -3.11 drs_rechnung.py <entpackter data-Ordner des ks_ferrari_f2004> [Klappenanteil]
"""
import sys
from pathlib import Path

import numpy as np

data = Path(sys.argv[1])
p = float(sys.argv[2]) if len(sys.argv) > 2 else 0.45


def lut(name):
    a = np.array([[float(x) for x in l.split("|")] for l in (data / name).read_text().splitlines() if "|" in l])
    return lambda x: np.interp(x, a[:, 0], a[:, 1])


A = 1.417  # Spannweite x Sehne aller Hauptfluegel des F2004
rcl, rcd = lut("wing_rear_AOA_CL.lut"), lut("wing_rear_AOA_CD.lut")
fcl, fcd = lut("wing_front_AOA_CL.lut"), lut("wing_front_AOA_CD.lut")
bcd = lut("wing_body_AOA_CD.lut")
dcl, dcd = lut("wing_diffuser_AOA_CL.lut"), lut("wing_diffuser_AOA_CD.lut")

rear_cl, rear_cd = rcl(25) * 0.904 * A, rcd(25) * 0.88 * A
tot_cd = rear_cd + fcd(14) * A + bcd(0.5) * A + dcd(1.5) * A
tot_cl = rear_cl + fcl(14) * 1.0697 * A + dcl(1.5) * (0.5852 + 0.5016) * A
d_cd = p * 0.88 * A * (rcd(25) - rcd(0))
d_cl = p * 0.904 * A * (rcl(25) - rcl(0))
q = 0.5 * 1.225 * (340 / 3.6) ** 2

print(f"Heckfluegel CL*A {rear_cl:.3f}  CD*A {rear_cd:.3f};  Auto CL*A {tot_cl:.2f}  CD*A {tot_cd:.3f}")
print(f"DRS offen: -CL*A {d_cl:.3f} ({d_cl / rear_cl:.1%} Heck, {d_cl / tot_cl:.1%} Auto), "
      f"-CD*A {d_cd:.3f} ({d_cd / tot_cd:.1%} Auto)")
print(f"340 km/h: -{q * d_cd:.0f} N Widerstand, -{q * d_cl / 9.81:.0f} kg Abtrieb, "
      f"vmax +{340 * ((tot_cd / (tot_cd - d_cd)) ** (1 / 3) - 1):.1f} km/h")
