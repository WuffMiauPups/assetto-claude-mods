"""INI-Werte in Autos lesen und setzen, egal ob die Daten in data.acd oder im offenen data-Ordner liegen.

  python acdini.py --ac <AC> --cars cim_2010_redbull cim_2010_hrt --file car.ini --section BASIC --key TOTALMASS --value 620 [--apply]
  python acdini.py --ac <AC> --prefix cim_2013_ --file suspensions.ini --section REAR --key BASEY --value 0.02 --apply
  python acdini.py --ac <AC> --prefix f1_2009_ --file ai.ini --section PEDALS --key BRAKE_HINT          (nur lesen)

Ohne --value wird nur gelesen, ohne --apply nur angezeigt, was sich ändern würde.
Sicherung: data.acd.bak bzw. <datei>.bak, jeweils nur beim ersten Mal (das Original bleibt erhalten).
AC verschlüsselt data.acd mit dem Ordnernamen in Kleinbuchstaben (cim_2007_honda_V2 -> cim_2007_honda_v2).
"""
import argparse
import os
import re
import shutil
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "Tools" / "acd"))
from acd_unpack import generate_key  # noqa: E402


def acd_read(path):
    key = generate_key(Path(path).parent.name.lower()).encode()
    data = open(path, "rb").read()
    off = 8 if struct.unpack_from("<i", data, 0)[0] < 0 else 0
    header, entries = data[:off], []
    while off < len(data):
        ln = struct.unpack_from("<I", data, off)[0]; off += 4
        name = data[off:off + ln].decode("utf8", "ignore"); off += ln
        sz = struct.unpack_from("<I", data, off)[0]; off += 4
        packed = data[off:off + sz * 4:4]; off += sz * 4
        entries.append([name, bytes(((packed[i] - key[i % len(key)]) & 0xFF) for i in range(sz))])
    return header, entries, key


def acd_write(path, header, entries, key):
    buf = bytearray(header)
    for name, content in entries:
        nb = name.encode("utf8")
        buf += struct.pack("<I", len(nb)) + nb + struct.pack("<I", len(content))
        enc = bytearray(len(content) * 4)
        enc[0::4] = bytes(((b + key[i % len(key)]) & 0xFF) for i, b in enumerate(content))
        buf += enc
    open(path, "wb").write(buf)


def section(text, name):
    m = re.search(r"^\[" + re.escape(name) + r"\][^\n]*\n.*?(?=^\[|\Z)", text, re.M | re.S | re.I)
    return m.group(0) if m else None


def get_value(text, sec, key):
    m = re.search(r"^\s*" + re.escape(key) + r"\s*=\s*([^;\r\n]*)", section(text, sec) or "", re.M | re.I)
    return m.group(1).strip() if m else None


def set_value(text, sec, key, value):
    """Setzt key=value im Abschnitt, Kommentar und Zeilenende bleiben. Gibt (neuer Text, alter Wert|None) zurück."""
    block = section(text, sec)
    nl = "\r\n" if "\r\n" in text else "\n"
    if block is None:
        return text.rstrip("\r\n") + f"{nl}{nl}[{sec}]{nl}{key}={value}{nl}", None
    m = re.search(r"^(\s*)" + re.escape(key) + r"\s*=\s*([^;\r\n]*?)(\s*(?:;[^\r\n]*)?)$", block, re.M | re.I)
    if m:
        new_block = block[:m.start()] + f"{m.group(1)}{key}={value}{m.group(3)}" + block[m.end():]
        return text.replace(block, new_block, 1), m.group(2).strip()
    head_end = block.index("\n") + 1
    return text.replace(block, block[:head_end] + f"{key}={value}{nl}" + block[head_end:], 1), None


class CarData:
    """Zugriff auf die Physikdateien eines Autos, data.acd hat Vorrang (so lädt auch AC)."""

    def __init__(self, cardir):
        self.dir = Path(cardir)
        self.acd = self.dir / "data.acd"
        if self.acd.is_file():
            self.header, self.entries, self.key = acd_read(self.acd)
            self.files = {e[0].lower(): e for e in self.entries}
        else:
            self.files = None

    def read(self, name):
        if self.files is not None:
            e = self.files.get(name.lower())
            return e[1].decode("latin1") if e else None
        p = self.dir / "data" / name
        return p.read_text(encoding="latin1") if p.is_file() else None

    def write(self, name, text):
        if self.files is not None:
            if not (self.dir / "data.acd.bak").exists():
                shutil.copy2(self.acd, self.dir / "data.acd.bak")
            self.files[name.lower()][1] = text.encode("latin1")
            acd_write(self.acd, self.header, self.entries, self.key)
        else:
            p = self.dir / "data" / name
            if not Path(str(p) + ".bak").exists():
                shutil.copy2(p, str(p) + ".bak")
            p.write_bytes(text.encode("latin1"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    ap.add_argument("--cars", nargs="*", default=[])
    ap.add_argument("--prefix", help="alle Autos, deren Ordner so beginnt")
    ap.add_argument("--file", required=True); ap.add_argument("--section", required=True); ap.add_argument("--key", required=True)
    ap.add_argument("--value"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = Path(a.ac) / "content" / "cars"
    cars = list(a.cars) + (sorted(p.name for p in root.iterdir() if p.name.startswith(a.prefix)) if a.prefix else [])
    for car in cars:
        cd = CarData(root / car)
        text = cd.read(a.file)
        if text is None:
            print(f"{car}: {a.file} fehlt"); continue
        if a.value is None:
            print(f"{car}: [{a.section}] {a.key} = {get_value(text, a.section, a.key)}"); continue
        new, old = set_value(text, a.section, a.key, a.value)
        if a.apply and new != text: cd.write(a.file, new)
        print(f"{car}: [{a.section}] {a.key} {old} -> {a.value}" + ("" if a.apply else "  [Trockenlauf]"))


if __name__ == "__main__":
    main()
