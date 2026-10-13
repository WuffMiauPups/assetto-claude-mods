"""Zwei fast_lane.ai vergleichen (z. B. Original gegen neu).

  python scripts/compare.py original.ai neu.ai [--out vergleich.png]
"""
import argparse
import _common  # noqa: F401
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fastlane import read_ai
from fastlane.speed import lap_time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--out", default="compare.png")
    args = ap.parse_args()
    A, B = read_ai(args.a), read_ai(args.b)
    for name, L in (("A", A), ("B", B)):
        print(f"{name}: {L.summary()}  Zeit(Profil) {lap_time(L.col('speed'), L.length):.1f} s")

    fig, ax = plt.subplots(1, 2, figsize=(16, 7))
    ax[0].plot(A.position[:, 0], A.position[:, 2], label="A", lw=1)
    ax[0].plot(B.position[:, 0], B.position[:, 2], label="B", lw=1)
    ax[0].set_aspect("equal"); ax[0].legend(); ax[0].set_title("Linien")
    ax[1].plot(A.length / A.total_length, A.speed_kmh, label="A")
    ax[1].plot(B.length / B.total_length, B.speed_kmh, label="B")
    ax[1].set_xlabel("Rundenanteil"); ax[1].set_ylabel("km/h"); ax[1].legend(); ax[1].grid()
    fig.tight_layout(); fig.savefig(args.out, dpi=110)
    print(f"Diagramm: {args.out}")


if __name__ == "__main__":
    main()
