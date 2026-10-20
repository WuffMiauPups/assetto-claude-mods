"""Minimaler kn5-Leser und -Schreiber (Version 5/6), fuer das Abtrennen der DRS-Klappe."""
from __future__ import annotations
import struct
from dataclasses import dataclass, field


class R:
    def __init__(self, b: bytes): self.b, self.o = b, 0
    def i(self): v = struct.unpack_from("<i", self.b, self.o)[0]; self.o += 4; return v
    def f(self): v = struct.unpack_from("<f", self.b, self.o)[0]; self.o += 4; return v
    def raw(self, n): v = self.b[self.o:self.o + n]; self.o += n; return v
    def s(self): return self.raw(self.i()).decode("latin-1")


@dataclass
class Node:
    type: int
    name: str
    active: int
    children: list = field(default_factory=list)
    matrix: bytes = b""          # type 1
    flags: bytes = b""           # type 2/3: 3 bytes
    bones: list = field(default_factory=list)  # type 3: (name, matrix)
    verts: bytes = b""
    indices: bytes = b""
    tail: bytes = b""            # material/layer/lod/bounds


@dataclass
class KN5:
    magic: bytes
    version: int
    extra: bytes
    textures: list
    materials: bytes
    root: Node


VSIZE = {2: 44, 3: 76}


def read(path) -> KN5:
    r = R(open(path, "rb").read())
    magic = r.raw(6); version = r.i(); extra = r.raw(4) if version > 5 else b""
    textures = []
    for _ in range(r.i()):
        t = r.i(); name = r.s(); data = r.raw(r.i()); textures.append((t, name, data))
    m0 = r.o
    for _ in range(r.i()):
        r.s(); r.s(); r.raw(6)
        for _ in range(r.i()): r.s(); r.raw(40)
        for _ in range(r.i()): r.s(); r.i(); r.s()
    materials = r.b[m0:r.o]

    def node():
        t = r.i(); name = r.s(); nc = r.i(); active = r.raw(1)[0]
        n = Node(t, name, active)
        if t == 1:
            n.matrix = r.raw(64)
        else:
            n.flags = r.raw(3)
            if t == 3:
                n.bones = [(r.s(), r.raw(64)) for _ in range(r.i())]
            n.verts = r.raw(r.i() * VSIZE[t])
            n.indices = r.raw(r.i() * 2)
            n.tail = r.raw(33 if t == 2 else 16)
        n.children = [node() for _ in range(nc)]
        return n
    root = node()
    assert r.o == len(r.b), (r.o, len(r.b))
    return KN5(magic, version, extra, textures, materials, root)


def write(k: KN5, path) -> None:
    out = bytearray(k.magic + struct.pack("<i", k.version) + k.extra)
    def s(x): out.extend(struct.pack("<i", len(x)) + x.encode("latin-1"))
    out.extend(struct.pack("<i", len(k.textures)))
    for t, name, data in k.textures:
        out.extend(struct.pack("<i", t)); s(name); out.extend(struct.pack("<i", len(data)) + data)
    out.extend(k.materials)
    def node(n: Node):
        out.extend(struct.pack("<i", n.type)); s(n.name); out.extend(struct.pack("<i", len(n.children))); out.append(n.active)
        if n.type == 1:
            out.extend(n.matrix)
        else:
            out.extend(n.flags)
            if n.type == 3:
                out.extend(struct.pack("<i", len(n.bones)))
                for bn, bm in n.bones: s(bn); out.extend(bm)
            out.extend(struct.pack("<i", len(n.verts) // VSIZE[n.type]) + n.verts)
            out.extend(struct.pack("<i", len(n.indices) // 2) + n.indices)
            out.extend(n.tail)
        for c in n.children: node(c)
    node(k.root)
    open(path, "wb").write(out)


def walk(n: Node, depth=0):
    yield n, depth
    for c in n.children:
        yield from walk(c, depth + 1)


def positions(n: Node):
    vs = VSIZE[n.type]
    return [struct.unpack_from("<3f", n.verts, i * vs) for i in range(len(n.verts) // vs)]
