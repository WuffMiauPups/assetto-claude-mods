"""Geometrie auf Polylinien im AC-Koordinatensystem (x, y=Höhe, z)."""
from __future__ import annotations

import numpy as np


def arc_length(pos: np.ndarray) -> np.ndarray:
    d = np.linalg.norm(np.diff(pos, axis=0), axis=1)
    return np.concatenate([[0.0], np.cumsum(d)])


def close_loop(pos: np.ndarray, tol: float = 5.0) -> np.ndarray:
    """Entfernt einen doppelten Schlusspunkt, falls Start und Ende fast identisch sind."""
    if np.linalg.norm(pos[0] - pos[-1]) < tol and len(pos) > 2:
        return pos[:-1]
    return pos


def resample(pos: np.ndarray, spacing: float = 2.0, closed: bool = True) -> np.ndarray:
    """Gleichmäßig in Bogenlänge abtasten. Bei closed wird der Rundschluss berücksichtigt."""
    p = pos
    if closed:
        p = np.vstack([pos, pos[:1]])
    s = arc_length(p)
    total = s[-1]
    n = max(int(round(total / spacing)), 4)
    s_new = np.linspace(0, total, n, endpoint=not closed)
    out = np.column_stack([np.interp(s_new, s, p[:, k]) for k in range(3)])
    return out.astype(np.float32)


def smooth(pos: np.ndarray, window: int = 9, passes: int = 2, closed: bool = True) -> np.ndarray:
    """Gleitender Mittelwert mit Rundschluss. Fenster ungerade."""
    if window < 3:
        return pos.copy()
    window |= 1
    half = window // 2
    kernel = np.ones(window) / window
    out = pos.astype(np.float64).copy()
    for _ in range(passes):
        if closed:
            padded = np.vstack([out[-half:], out, out[:half]])
        else:
            padded = np.vstack([np.repeat(out[:1], half, 0), out, np.repeat(out[-1:], half, 0)])
        out = np.column_stack([np.convolve(padded[:, k], kernel, mode="valid") for k in range(3)])
    return out.astype(np.float32)


def curvature(pos: np.ndarray, closed: bool = True) -> np.ndarray:
    """Signierte Krümmung 1/m in der Horizontalebene (x, z). Positiv = Linkskurve in AC."""
    xz = pos[:, [0, 2]].astype(np.float64)
    if closed:
        d1 = (np.roll(xz, -1, 0) - np.roll(xz, 1, 0)) / 2
        d2 = np.roll(xz, -1, 0) - 2 * xz + np.roll(xz, 1, 0)
    else:
        d1 = np.gradient(xz, axis=0)
        d2 = np.gradient(d1, axis=0)
    num = d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]
    den = (d1[:, 0] ** 2 + d1[:, 1] ** 2) ** 1.5
    with np.errstate(divide="ignore", invalid="ignore"):
        k = np.where(den > 1e-9, num / den, 0.0)
    return k


def forward_vectors(pos: np.ndarray, closed: bool = True) -> np.ndarray:
    if closed:
        d = np.roll(pos, -1, 0) - np.roll(pos, 1, 0)
    else:
        d = np.gradient(pos.astype(np.float64), axis=0)
    n = np.linalg.norm(d, axis=1, keepdims=True)
    return (d / np.where(n > 1e-9, n, 1)).astype(np.float32)


def lateral_offset(pos: np.ndarray, forward: np.ndarray, dist: np.ndarray, side: int) -> np.ndarray:
    """Punkt seitlich versetzen. side=+1 links (in AC: Kreuzprodukt up x forward), -1 rechts."""
    up = np.array([0.0, 1.0, 0.0])
    left = np.cross(np.broadcast_to(up, forward.shape), forward)
    return pos + side * left * dist[:, None]
