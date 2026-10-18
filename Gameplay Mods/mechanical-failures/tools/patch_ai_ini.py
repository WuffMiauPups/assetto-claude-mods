"""Einen Wert in der ai.ini vieler Autos setzen, direkt in der data.acd (oder im data-Ordner), mit Sicherung.

  python patch_ai_ini.py --ac <AC> --section PEDALS --key TRAIL_HINT --value 1 [--only-if 0] [--cars a b | --f1] [--apply]

Ohne --apply nur Trockenlauf. Sicherung: data.acd.bak (einmalig, wird nie überschrieben), ai.ini.bak im data-Ordner.
--only-if: nur Autos, bei denen der Wert aktuell gleich diesem ist (oder fehlt, wenn --only-if missing).
Achtung: geänderte data.acd hat einen anderen Checksum, online mit Checksum-Prüfung fliegt das Auto raus.
Rückbau: data.acd.bak zurück nach data.acd (python patch_ai_ini.py --restore --cars ... oder --f1).
"""
import argparse
import json
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
    car = os.path.basename(os.path.dirname(path))
    key = generate_key(car).encode()
    data = open(path, "rb").read()
    off = 8 if struct.unpack_from("<i", data, 0)[0] < 0 else 0
    header = data[:off]
    entries = []
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


def set_value(text, section, key, value):
    """Setzt key=value im Abschnitt, legt Abschnitt oder Schlüssel an. Gibt (neuer Text, alter Wert|None) zurück."""
    lines = text.splitlines(keepends=True)
    nl = "\r\n" if "\r\n" in text else "\n"
    sec_i, cur = None, None
    old = None
    for i, raw in enumerate(lines):
        line = raw.split(";")[0].split("//")[0].strip()
        m = re.match(r"^\[(.+)\]", line)
        if m:
            cur = m.group(1).upper()
            if cur == section.upper(): sec_i = i
            continue
        if cur == section.upper():
            m = re.match(r"^(\s*)" + re.escape(key) + r"\s*=\s*([^;/\r\n]*)(.*)$", raw, re.I)
            if m:
                old = m.group(2).strip()
                rest = m.group(3).rstrip("\r\n")
                lines[i] = f"{m.group(1)}{key}={value}{rest}{nl}"
                return "".join(lines), old
    if sec_i is None:
        if lines and not lines[-1].endswith("\n"): lines[-1] += nl
        lines += [f"{nl}[{section}]{nl}", f"{key}={value}{nl}"]
    else:
        lines.insert(sec_i + 1, f"{key}={value}{nl}")
    return "".join(lines), None


def is_f1(cardir):
    ui = cardir / "ui" / "ui_car.json"
    if not ui.is_file():
        return False
    try:
        j = json.loads(re.sub(r"[\x00-\x1f]", " ", ui.read_text(encoding="utf-8", errors="ignore")), strict=False)
    except Exception:
        j = {}
    blob = f"{cardir.name} {j.get('brand', '')} {j.get('name', '')} {' '.join(j.get('tags') or [])}".lower()
    return bool(re.search(r"\bf1\b|formula|grand prix|\bgp\b", blob))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    ap.add_argument("--section"); ap.add_argument("--key"); ap.add_argument("--value")
    ap.add_argument("--only-if", help="aktueller Wert, oder 'missing'")
    ap.add_argument("--cars", nargs="*"); ap.add_argument("--f1", action="store_true")
    ap.add_argument("--apply", action="store_true"); ap.add_argument("--restore", action="store_true")
    a = ap.parse_args()
    cars = Path(a.ac) / "content" / "cars"
    names = a.cars or [c for c in sorted(os.listdir(cars), key=str.lower) if a.f1 and is_f1(cars / c)]
    if not names:
        raise SystemExit("--cars oder --f1 angeben")
    changed = 0
    for c in names:
        cardir = cars / c
        acd, bak = cardir / "data.acd", cardir / "data.acd.bak"
        ini_file = cardir / "data" / "ai.ini"
        if a.restore:
            if bak.is_file():
                shutil.copy(bak, acd); print(f"{c}: data.acd aus .bak wiederhergestellt")
            if (cardir / "data" / "ai.ini.bak").is_file():
                shutil.copy(cardir / "data" / "ai.ini.bak", ini_file); print(f"{c}: ai.ini aus .bak wiederhergestellt")
            continue
        if not (a.section and a.key and a.value is not None):
            raise SystemExit("--section, --key, --value nötig")
        # AC lädt die data.acd, wenn sie existiert; der data-Ordner zählt nur ohne acd
        if ini_file.is_file() and not acd.is_file():
            text = ini_file.read_text(encoding="utf-8", errors="ignore"); where = "ordner"
        elif acd.is_file():
            header, entries, key = acd_read(str(acd))
            idx = next((i for i, e in enumerate(entries) if e[0].lower() == "ai.ini"), None)
            if idx is None:
                print(f"{c}: keine ai.ini"); continue
            text = entries[idx][1].decode("utf8", "ignore"); where = "acd"
        else:
            continue
        new, old = set_value(text, a.section, a.key, a.value)
        if a.only_if is not None:
            if a.only_if == "missing" and old is not None: continue
            if a.only_if != "missing" and (old is None or old != a.only_if): continue
        if old == a.value:
            continue
        print(f"{c}: [{a.section}] {a.key} {old if old is not None else '(fehlt)'} -> {a.value}  ({where}){'' if a.apply else '  [Trockenlauf]'}")
        changed += 1
        if not a.apply:
            continue
        if where == "ordner":
            if not (cardir / "data" / "ai.ini.bak").exists(): shutil.copy(ini_file, cardir / "data" / "ai.ini.bak")
            ini_file.write_text(new, encoding="utf-8")
        else:
            if not bak.exists(): shutil.copy(acd, bak)
            entries[idx][1] = new.encode("utf8")
            acd_write(str(acd), header, entries, key)
    print(f"\n{changed} Autos {'geändert' if a.apply else 'würden geändert'}")


if __name__ == "__main__":
    main()
