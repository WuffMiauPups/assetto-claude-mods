"""Eine fast_lane.ai analysieren: Kennzahlen und Diagramm.

  python scripts/analyse.py pfad/zur/fast_lane.ai [--out plot.png]
"""
import argparse
import _common  # noqa: F401
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fastlane import read_ai, curvature
from fastlane.speed import lap_time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    line = read_ai(a.file)
    print(line.summary())
    print(f"Geschätzte Rundenzeit aus Speed-Profil: {lap_time(line.col('speed'), line.length):.1f} s")
    k = curvature(line.position)
    print(f"Engster Radius: {1 / max(np.abs(k).max(), 1e-6):.0f} m")

    fig, ax = plt.subplots(2, 2, figsize=(14, 9))
    ax[0, 0].plot(line.position[:, 0], line.position[:, 2], lw=1)
    ax[0, 0].set_aspect("equal"); ax[0, 0].set_title("Linie (Draufsicht)")
    sc = ax[0, 1].scatter(line.position[:, 0], line.position[:, 2], c=line.speed_kmh, s=2, cmap="viridis")
    ax[0, 1].set_aspect("equal"); ax[0, 1].set_title("Geschwindigkeit km/h"); fig.colorbar(sc, ax=ax[0, 1])
    ax[1, 0].plot(line.length, line.speed_kmh); ax[1, 0].set_title("Speed über Streckenmeter"); ax[1, 0].grid()
    ax[1, 1].plot(line.length, k); ax[1, 1].set_title("Krümmung 1/m"); ax[1, 1].grid()
    fig.tight_layout()
    out = a.out or (a.file + ".png")
    fig.savefig(out, dpi=110)
    print(f"Diagramm: {out}")


if __name__ == "__main__":
    main()
