"""Aus Telemetrie-Logs eine neue fast_lane.ai bauen.

  python scripts/build.py --laps AI/data/monza/laps/*.csv --out dist/monza/fast_lane.ai \
      [--reference content/tracks/monza/ai/fast_lane.ai] [--margin 0.97] [--spacing 2] \
      [--smooth 9] [--lat-g 1.3] [--brake-g 1.2] [--accel-g 0.5] [--vmax 320] [--use-recorded-speed]

Mit --reference werden Seitenabstände (side_left/right) und Höhe aus der Original-Linie übernommen,
sonst aus den Telemetriewerten track_left/track_right.
"""
import argparse
from pathlib import Path
import _common  # noqa: F401
import numpy as np

from fastlane import (AILine, read_ai, write_ai, resample, smooth, curvature, arc_length,
                      speed_profile, VehicleLimits, load_lap_csv, split_laps, best_lap)
from fastlane.aifile import EXTRA_COUNT
from fastlane.geometry import forward_vectors, close_loop
from fastlane.speed import lap_time, gas_brake_from_speed
from fastlane.telemetry import positions, lap_duration


def nearest_index(ref_pos: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """Für jeden Punkt den Index des nächsten Referenzpunkts (nur x,z)."""
    out = np.empty(len(pts), dtype=int)
    rxz = ref_pos[:, [0, 2]]
    for i, p in enumerate(pts[:, [0, 2]]):
        out[i] = np.argmin(((rxz - p) ** 2).sum(1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--laps", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reference", default=None)
    ap.add_argument("--margin", type=float, default=0.97)
    ap.add_argument("--spacing", type=float, default=2.0)
    ap.add_argument("--smooth", type=int, default=9)
    ap.add_argument("--lat-g", type=float, default=1.3)
    ap.add_argument("--brake-g", type=float, default=1.2)
    ap.add_argument("--accel-g", type=float, default=0.5)
    ap.add_argument("--vmax", type=float, default=320.0)
    ap.add_argument("--use-recorded-speed", action="store_true",
                    help="Gefahrene Geschwindigkeit statt berechnetem Profil verwenden")
    a = ap.parse_args()

    laps = []
    for f in a.laps:
        laps += split_laps(load_lap_csv(f))
    print(f"{len(laps)} Runden geladen")
    lap = best_lap(laps)
    print(f"Beste Runde: {lap_duration(lap):.2f} s, {len(lap['t'])} Samples")

    raw = close_loop(positions(lap))
    pos = resample(raw, a.spacing)
    pos = smooth(pos, a.smooth)
    s = arc_length(np.vstack([pos, pos[:1]]))[:-1]
    k = curvature(pos)
    fwd = forward_vectors(pos)
    n = len(pos)

    line = AILine.empty(n)
    line.position[:] = pos
    line.length[:] = s
    line.set_col("length", s)
    line.set_col("direction", 1.0)
    line.set_col("forward_x", fwd[:, 0]); line.set_col("forward_y", fwd[:, 1]); line.set_col("forward_z", fwd[:, 2])
    line.set_col("normal_y", 1.0)
    with np.errstate(divide="ignore"):
        line.set_col("radius", np.where(np.abs(k) > 1e-4, 1 / np.abs(k), 0.0))

    if a.use_recorded_speed:
        rec_s = arc_length(raw)
        rec_s = rec_s / rec_s[-1] * s[-1]
        v = np.interp(s, rec_s, lap["speed"][:len(rec_s)] / 3.6) * a.margin
        v = smooth(np.column_stack([v, v, v]), 15)[:, 0]
    else:
        lim = VehicleLimits(a.lat_g, a.brake_g, a.accel_g, a.vmax, a.margin)
        v = speed_profile(k, np.append(s, s[-1] + a.spacing), lim)
    line.set_col("speed", v)
    gas, brake = gas_brake_from_speed(v, s)
    line.set_col("gas", gas); line.set_col("brake", brake)

    if a.reference:
        ref = read_ai(a.reference)
        idx = nearest_index(ref.position, pos)
        line.position[:, 1] = ref.position[idx, 1]
        line.set_col("side_left", ref.col("side_left")[idx])
        line.set_col("side_right", ref.col("side_right")[idx])
        line.set_col("camber", ref.col("camber")[idx]); line.set_col("grade", ref.col("grade")[idx])
        print(f"Referenz: {ref.summary()}")
        print(f"Referenz-Rundenzeit (Profil): {lap_time(ref.col('speed'), ref.length):.1f} s")
    else:
        rec_s = arc_length(raw); rec_s = rec_s / rec_s[-1] * s[-1]
        line.set_col("side_left", np.interp(s, rec_s, lap["track_left"][:len(rec_s)]))
        line.set_col("side_right", np.interp(s, rec_s, lap["track_right"][:len(rec_s)]))

    print(f"Neu:      {line.summary()}")
    print(f"Neue Rundenzeit (Profil):     {lap_time(v, s):.1f} s")
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    write_ai(line, out)
    print(f"Geschrieben: {out}")


if __name__ == "__main__":
    main()
