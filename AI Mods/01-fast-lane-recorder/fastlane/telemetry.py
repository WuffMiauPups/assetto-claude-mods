"""Telemetrie-CSV der Aufnahme-App lesen und in Runden zerlegen.

Spalten (siehe app/fastlane_recorder/fastlane_recorder.lua):
  t, lap, spline, x, y, z, speed, gas, brake, steer, yaw_rate, track_left, track_right
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

COLUMNS = ("t", "lap", "spline", "x", "y", "z", "speed", "gas", "brake",
           "steer", "yaw_rate", "track_left", "track_right")


def load_lap_csv(path: str | Path) -> dict[str, np.ndarray]:
    raw = np.genfromtxt(path, delimiter=",", names=True, dtype=np.float64)
    missing = [c for c in COLUMNS if c not in raw.dtype.names]
    if missing:
        raise ValueError(f"Spalten fehlen in {path}: {missing}")
    return {c: np.asarray(raw[c]) for c in raw.dtype.names}


def split_laps(data: dict[str, np.ndarray]) -> list[dict[str, np.ndarray]]:
    laps = []
    for lap_id in np.unique(data["lap"]):
        m = data["lap"] == lap_id
        if m.sum() < 50:
            continue
        laps.append({k: v[m] for k, v in data.items()})
    return laps


def lap_duration(lap: dict[str, np.ndarray]) -> float:
    return float(lap["t"][-1] - lap["t"][0])


def is_complete(lap: dict[str, np.ndarray]) -> bool:
    sp = lap["spline"]
    return sp.min() < 0.02 and sp.max() > 0.98


def best_lap(laps: list[dict[str, np.ndarray]]) -> dict[str, np.ndarray]:
    complete = [l for l in laps if is_complete(l)]
    if not complete:
        raise ValueError("Keine vollständige Runde im Log (Spline 0 bis 1 nicht abgedeckt)")
    return min(complete, key=lap_duration)


def positions(lap: dict[str, np.ndarray]) -> np.ndarray:
    return np.column_stack([lap["x"], lap["y"], lap["z"]]).astype(np.float32)
