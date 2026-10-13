"""Geschwindigkeitsprofil aus Krümmung und einfachen Fahrzeuggrenzen."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class VehicleLimits:
    lat_g: float = 1.3          # maximale Querbeschleunigung in g
    brake_g: float = 1.2        # maximale Bremsverzögerung in g
    accel_g: float = 0.5        # grobe Längsbeschleunigung in g
    v_max_kmh: float = 300.0    # Höchstgeschwindigkeit
    margin: float = 1.0         # Skalierung des Ergebnisses (0.97 = 3 Prozent langsamer)


G = 9.81


def speed_profile(curv: np.ndarray, s: np.ndarray, lim: VehicleLimits, closed: bool = True) -> np.ndarray:
    """Vorwärts-Rückwärts-Pass: Kurvengrenze, dann Beschleunigen, dann Bremsen. Ergibt m/s."""
    k = np.abs(curv) + 1e-6
    v_corner = np.sqrt(lim.lat_g * G / k)
    v = np.minimum(v_corner, lim.v_max_kmh / 3.6)
    ds = np.diff(s)
    n = len(v)
    reps = 2 if closed else 1
    for _ in range(reps):
        for i in range(1, n):                       # Beschleunigen
            v[i] = min(v[i], np.sqrt(v[i - 1] ** 2 + 2 * lim.accel_g * G * ds[i - 1]))
        if closed:
            v[0] = min(v[0], np.sqrt(v[-1] ** 2 + 2 * lim.accel_g * G * ds[-1]))
        for i in range(n - 2, -1, -1):              # Bremsen
            v[i] = min(v[i], np.sqrt(v[i + 1] ** 2 + 2 * lim.brake_g * G * ds[i]))
        if closed:
            v[-1] = min(v[-1], np.sqrt(v[0] ** 2 + 2 * lim.brake_g * G * ds[-1]))
    return (v * lim.margin).astype(np.float32)


def lap_time(v: np.ndarray, s: np.ndarray) -> float:
    ds = np.diff(s)
    v_mid = (v[1:] + v[:-1]) / 2
    return float(np.sum(ds / np.maximum(v_mid, 0.1)))


def gas_brake_from_speed(v: np.ndarray, s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Grobe Gas/Brems-Hinweise aus der Geschwindigkeitsänderung."""
    dv = np.gradient(v)
    gas = np.clip(dv / (np.abs(dv).max() + 1e-9), 0, 1)
    brake = np.clip(-dv / (np.abs(dv).max() + 1e-9), 0, 1)
    return gas.astype(np.float32), brake.astype(np.float32)
