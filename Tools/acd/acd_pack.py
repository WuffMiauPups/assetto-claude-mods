"""data-Ordner eines Autos in eine data.acd packen (Gegenstück zu acd_unpack.py).

  python acd_pack.py <data-Ordner> <ziel.acd>

Der Schlüssel kommt aus dem Namen des Auto-Ordners (Elternordner des data-Ordners), also muss der
data-Ordner unter content/cars/<auto>/ liegen. Jedes Byte wird als (byte + key[i]) & 0xFF plus drei
Nullbytes abgelegt. Reihenfolge der Einträge wie NTFS (Großbuchstaben-Vergleich), ohne Unterordner.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acd_unpack import generate_key  # noqa: E402


def pack(folder, out):
    folder = os.path.abspath(folder)
    car = os.path.basename(os.path.dirname(folder))
    key = generate_key(car.lower()).encode()  # AC verschlüsselt mit dem Ordnernamen in Kleinbuchstaben
    buf = bytearray()
    n = 0
    for name in sorted(os.listdir(folder), key=str.upper):
        path = os.path.join(folder, name)
        if not os.path.isfile(path) or name.lower().endswith(('.bak', '.orig')):
            continue
        data = open(path, 'rb').read()
        nb = name.encode('utf8')
        buf += struct.pack('<I', len(nb)) + nb + struct.pack('<I', len(data))
        enc = bytearray(len(data) * 4)
        enc[0::4] = bytes(((b + key[i % len(key)]) & 0xff) for i, b in enumerate(data))
        buf += enc
        n += 1
    open(out, 'wb').write(buf)
    print('packed', n, 'files from', folder, '->', out, 'key', key.decode())


if __name__ == '__main__':
    pack(sys.argv[1], sys.argv[2])
