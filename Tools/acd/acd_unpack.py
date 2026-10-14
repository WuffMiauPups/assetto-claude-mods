"""data.acd eines Autos entpacken.

  python acd_unpack.py <auto>/data.acd <ziel-ordner>

Schlüssel aus dem Namen des Auto-Ordners (Elternordner der data.acd). Algorithmus nach albertowd/live-telemetry.
"""
import sys, os, struct

def generate_key(n):
    k1 = sum(ord(c) for c in n) & 0xff
    i=0;k2=0
    while i < len(n)-1:
        k2 *= ord(n[i]); i+=1; k2 -= ord(n[i]); i+=1
    k2 &= 0xff
    i=1;k3=0
    while i < len(n)-3:
        k3 *= ord(n[i]); i+=1; k3 = int(k3/(ord(n[i])+0x1b)); i-=2; k3 += -0x1b-ord(n[i]); i+=4
    k3 &= 0xff
    k4 = (0x1683 - sum(ord(c) for c in n[1:])) & 0xff
    i=1;k5=0x42
    while i < len(n)-4:
        tmp=(ord(n[i])+0xf)*k5; i-=1; k5=(ord(n[i])+0xf)*tmp+0x16; i+=5
    k5 &= 0xff
    i=0;k6=0x65
    while i < len(n)-2:
        k6 -= ord(n[i]); i+=2
    k6 &= 0xff
    i=0;k7=0xab
    while i < len(n)-2:
        k7 %= ord(n[i]); i+=2
    k7 &= 0xff
    i=0;k8=0xab
    while i < len(n)-1:
        k8 = int(k8/ord(n[i])) + ord(n[i+1]); i+=1
    k8 &= 0xff
    return "{}-{}-{}-{}-{}-{}-{}-{}".format(k1,k2,k3,k4,k5,k6,k7,k8)

def unpack(acd, out):
    car = os.path.basename(os.path.dirname(os.path.abspath(acd)))
    key = generate_key(car).encode()
    data = open(acd,'rb').read()
    off = 0
    v = struct.unpack_from('<i', data, 0)[0]
    if v < 0: off = 8
    os.makedirs(out, exist_ok=True)
    n = 0
    while off < len(data):
        ln = struct.unpack_from('<I', data, off)[0]; off += 4
        name = data[off:off+ln].decode('utf8'); off += ln
        sz = struct.unpack_from('<I', data, off)[0]; off += 4
        packed = data[off:off+sz*4:4]; off += sz*4
        dec = bytes(((packed[i] - key[i % len(key)]) & 0xff) for i in range(sz))
        with open(os.path.join(out, name), 'wb') as f: f.write(dec)
        n += 1
    print("unpacked", n, "files from", acd, "key", key.decode())

if __name__ == "__main__":
    unpack(sys.argv[1], sys.argv[2])
