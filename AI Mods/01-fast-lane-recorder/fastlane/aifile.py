"""Binärformat von fast_lane.ai / pit_lane.ai.

Aufbau (alles little-endian):
  Header
    int32  version        (immer 7)
    int32  point_count
    int32  lap_time_ms    (von AC meist 0)
    int32  sample_count   (bei Kunos-Dateien 0)
  point_count mal
    float32 x, y, z       Position (AC-Koordinaten: y ist Höhe)
    float32 length        kumulierte Strecke in Metern
    int32   id            laufende Nummer
  int32  extra_count     (identisch zu point_count)
  extra_count mal, 18 float32 "extra":
    0  speed              Zielgeschwindigkeit m/s
    1  gas
    2  brake
    3  obsolete_lat_g
    4  radius             Kurvenradius m (0 = gerade)
    5  side_left          Abstand zur linken Streckenkante m
    6  side_right         Abstand zur rechten Streckenkante m
    7  camber
    8  direction          +1 vorwärts
    9  normal_x
    10 normal_y
    11 normal_z
    12 length             wie oben
    13 forward_x
    14 forward_y
    15 forward_z
    16 tag
    17 grade
  int32  has_grid       (1 = Kunos-Nachschlagegitter folgt, 0 = keins)
  optional Gitter: float32 max_xyz[3], min_xyz[3] (Strecken-Bounding-Box plus 350 m),
    int32 cell_size, float32 cell_size, int32 cols, int32 rows,
    dann pro Zelle int32 count + count int32 Punktindizes (die nächstgelegenen Punkte).
    Das Gitter ist nur ein Lookup-Cache. Beim Lesen wird es roh in AILine.grid behalten,
    beim Schreiben einer neuen Linie wird has_grid=0 geschrieben.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

VERSION = 7
EXTRA_COUNT = 18
HEADER = struct.Struct("<iiii")
POINT = struct.Struct("<ffffi")

EXTRA_FIELDS = (
    "speed", "gas", "brake", "obsolete_lat_g", "radius",
    "side_left", "side_right", "camber", "direction",
    "normal_x", "normal_y", "normal_z", "length",
    "forward_x", "forward_y", "forward_z", "tag", "grade",
)
EXTRA_INDEX = {name: i for i, name in enumerate(EXTRA_FIELDS)}


@dataclass
class AILine:
    """Eine AI-Linie: Positionen (N,3), kumulierte Länge (N,), Extra-Daten (N,18)."""

    position: np.ndarray
    length: np.ndarray
    extra: np.ndarray
    lap_time_ms: int = 0
    sample_count: int = 0
    ids: np.ndarray = field(default=None)
    grid: bytes = b""  # roher Gitterblock (nach has_grid), leer wenn keins

    def __post_init__(self):
        n = len(self.position)
        assert self.position.shape == (n, 3), self.position.shape
        assert self.length.shape == (n,), self.length.shape
        assert self.extra.shape == (n, EXTRA_COUNT), self.extra.shape
        if self.ids is None:
            self.ids = np.arange(n, dtype=np.int32)

    def __len__(self):
        return len(self.position)

    def col(self, name: str) -> np.ndarray:
        return self.extra[:, EXTRA_INDEX[name]]

    def set_col(self, name: str, values) -> None:
        self.extra[:, EXTRA_INDEX[name]] = values

    @property
    def speed_kmh(self) -> np.ndarray:
        return self.col("speed") * 3.6

    @property
    def total_length(self) -> float:
        return float(self.length[-1])

    def summary(self) -> str:
        v = self.speed_kmh
        return (
            f"Punkte: {len(self)}  Länge: {self.total_length:.0f} m  "
            f"Abstand: {np.diff(self.length).mean():.2f} m  "
            f"Speed min/mean/max: {v.min():.0f}/{v.mean():.0f}/{v.max():.0f} km/h"
        )

    @classmethod
    def empty(cls, n: int) -> "AILine":
        return cls(np.zeros((n, 3), np.float32), np.zeros(n, np.float32),
                   np.zeros((n, EXTRA_COUNT), np.float32))


def read_ai(path: str | Path) -> AILine:
    data = Path(path).read_bytes()
    version, count, lap_time, sample_count = HEADER.unpack_from(data, 0)
    if version != VERSION:
        raise ValueError(f"Unbekannte Version {version} (erwartet {VERSION})")
    off = HEADER.size
    pts = np.frombuffer(data, dtype=np.dtype([("p", "<f4", 3), ("len", "<f4"), ("id", "<i4")]),
                        count=count, offset=off)
    off += count * POINT.size
    (extra_count,) = struct.unpack_from("<i", data, off)
    off += 4
    if extra_count != count:
        raise ValueError(f"extra_count {extra_count} != point_count {count}")
    extra = np.frombuffer(data, dtype="<f4", count=count * EXTRA_COUNT, offset=off)
    extra = extra.reshape(count, EXTRA_COUNT).copy()
    off += count * EXTRA_COUNT * 4
    grid = b""
    if off + 4 <= len(data):
        (has_grid,) = struct.unpack_from("<i", data, off)
        off += 4
        if has_grid == 1:
            grid = bytes(data[off:])
        elif len(data) != off:
            raise ValueError("Dateilänge passt nicht zum Header")
    return AILine(pts["p"].astype(np.float32).copy(), pts["len"].copy(), extra,
                  lap_time_ms=lap_time, sample_count=sample_count, ids=pts["id"].copy(), grid=grid)


def write_ai(line: AILine, path: str | Path) -> None:
    n = len(line)
    out = bytearray(HEADER.pack(VERSION, n, int(line.lap_time_ms), int(line.sample_count)))
    for i in range(n):
        x, y, z = line.position[i]
        out += POINT.pack(float(x), float(y), float(z), float(line.length[i]), int(line.ids[i]))
    out += struct.pack("<i", n)
    out += line.extra.astype("<f4").tobytes()
    if line.grid:
        out += struct.pack("<i", 1) + line.grid
    else:
        out += struct.pack("<i", 0)
    Path(path).write_bytes(out)
