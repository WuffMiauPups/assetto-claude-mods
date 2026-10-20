"""Trennt die obere Heckfluegel-Klappe des F2004-Modells ab und erzeugt die DRS-Animation.

Die Klappe steckt in der Karosserie-Mesh g_Body_SUB0 (Material Carpaint) als eigenes, nicht mit dem
Hauptblatt verbundenes Teil: 128 Dreiecke, Sehne rund 110 mm, Anstellung rund 55 Grad.
Sie wird in einen neuen Knoten WING_Rear_Flap (Fahrzeugkoordinaten, Drehpunkt an der Hinterkante)
verschoben; car_wing.ksanim dreht ihn um OPEN_DEG nach oben (Vorderkante hebt sich, Spalt oeffnet).

Konventionen aus dem Cimmerian 2013 (kn5 und ksanim nachgerechnet): Quaternion (x,y,z,w) wirkt
rechtshaendig auf Spaltenvektoren, Drehpunkt an der Hinterkante, Oeffnen = negative Drehung um die
Querachse x des Autos (+z ist vorn).
"""
from __future__ import annotations

import math
import struct
from pathlib import Path

import numpy as np

import kn5

NODE = "WING_Rear_Flap"
OPEN_DEG = 30.0           # Klappe hebt die Vorderkante um 30 Grad: Spalt rund 55 mm
FRAMES = 20
# Klappenbox in Fahrzeugkoordinaten (aus der Komponentenanalyse des Originalmodells)
BOX = dict(x=0.484, y_min=0.731, z_min=-2.215, z_max=-2.13)
PIVOT = np.array([0.0, 0.82, -2.20])   # Hinterkante oben


def _extract(mesh: kn5.Node, M: np.ndarray, suffix: str) -> kn5.Node | None:
    """Dreiecke der Mesh, die ganz in der Klappenbox liegen, als neue Mesh in Klappenkoordinaten."""
    vs = kn5.VSIZE[mesh.type]
    raw = np.frombuffer(mesh.verts, dtype=np.float32).reshape(-1, vs // 4).copy()
    pos_car = (np.c_[raw[:, :3], np.ones(len(raw))] @ M)[:, :3]
    idx = np.frombuffer(mesh.indices, dtype=np.uint16).reshape(-1, 3)
    inside = (np.abs(pos_car[:, 0]) < BOX["x"]) & (pos_car[:, 1] > BOX["y_min"]) \
        & (pos_car[:, 2] > BOX["z_min"]) & (pos_car[:, 2] < BOX["z_max"])
    sel = inside[idx].all(1)
    if sel.sum() < 10:
        return None
    flap_tris = idx[sel]
    used = np.unique(flap_tris)
    remap = {int(v): i for i, v in enumerate(used)}
    M3 = M[:3, :3]
    new = raw[used].copy()
    new[:, 0:3] = pos_car[used] - PIVOT
    new[:, 3:6] = new[:, 3:6] @ M3                      # Normalen
    new[:, 8:11] = new[:, 8:11] @ M3                    # Tangenten
    new_idx = np.vectorize(remap.get)(flap_tris).astype(np.uint16)
    center = (new[:, :3].min(0) + new[:, :3].max(0)) / 2
    radius = float(np.linalg.norm(new[:, :3] - center, axis=1).max())
    mat, layer, lod_in, lod_out = struct.unpack_from("<iiff", mesh.tail, 0)

    flap = kn5.Node(2, f"{NODE}_{suffix}", 1)
    flap.flags = mesh.flags
    flap.verts = new.astype(np.float32).tobytes()
    flap.indices = new_idx.tobytes()
    flap.tail = struct.pack("<iiff3ffB", mat, layer, lod_in, lod_out, *center, radius, 1)
    mesh.indices = idx[~sel].astype(np.uint16).tobytes()   # Klappe aus der Quelle entfernen
    print(f"   {mesh.name}: {sel.sum()} Dreiecke, {len(used)} Punkte")
    return flap


def split_flap(src: Path, dst: Path) -> bool:
    """Sucht in allen Meshes unter Wurzel-Dummies (Karosserie) nach Klappen-Dreiecken."""
    k = kn5.read(src)
    parts = []
    for dummy in k.root.children:
        if dummy.type != 1 or not dummy.children:
            continue
        M = np.array(struct.unpack("<16f", dummy.matrix)).reshape(4, 4)
        for mesh in dummy.children:
            if mesh.type == 2 and ("body" in mesh.name.lower() or "carpaint" in mesh.name.lower()):
                part = _extract(mesh, M, mesh.name)
                if part is not None:
                    parts.append(part)
    if not parts:
        return False
    node = kn5.Node(1, NODE, 1)
    mtx = np.eye(4, dtype=np.float32)
    mtx[3, :3] = PIVOT
    node.matrix = mtx.tobytes()
    node.children = parts
    k.root.children.append(node)
    kn5.write(k, dst)
    print(f"Klappe abgetrennt -> {dst.name}")
    return True


def write_anim(path: Path) -> None:
    out = bytearray(struct.pack("<ii", 2, 1))
    out.extend(struct.pack("<i", len(NODE)) + NODE.encode())
    out.extend(struct.pack("<i", FRAMES))
    for f in range(FRAMES):
        a = math.radians(OPEN_DEG) * f / (FRAMES - 1)
        q = (-math.sin(a / 2), 0.0, 0.0, math.cos(a / 2))
        out.extend(struct.pack("<10f", *q, *PIVOT, 1.0, 1.0, 1.0))
    path.write_bytes(out)
    print(f"Animation geschrieben: {path.name}, {FRAMES} Bilder, {OPEN_DEG:.0f} Grad")
