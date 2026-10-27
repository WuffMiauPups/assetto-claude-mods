"""Sound-Bank eines anderen Autos einsetzen (wie "Sound ersetzen" in Content Manager), mit Sicherung.

  python sound_tausch.py --ac <AC> --target cim_2013_mercedes --donor cim_2012_mercedes [--int 4.9 --ext 1.0] [--apply]

Kopiert <donor>.bank als <target>.bank und schreibt in GUIDs.txt alle Pfade auf den Zielnamen um.
Originale: <target>.bank.bak und GUIDs.txt.bak. --int/--ext setzen [AUDIO_VOLUME] in extension/ext_config.ini
(die 2012er Banks von Cimmerian sind auf ENGINE_INT = 4.9 abgestimmt).
"""
import argparse
import shutil
from pathlib import Path

from acdini import set_value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True); ap.add_argument("--target", required=True); ap.add_argument("--donor", required=True)
    ap.add_argument("--int", dest="vol_int"); ap.add_argument("--ext", dest="vol_ext"); ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    cars = Path(a.ac) / "content" / "cars"
    T, D = cars / a.target / "sfx", cars / a.donor / "sfx"
    if not a.apply:
        print(f"Trockenlauf: {D / (a.donor + '.bank')} -> {T / (a.target + '.bank')}"); return
    for f in (f"{a.target}.bank", "GUIDs.txt"):
        if not (T / f"{f}.bak").exists(): shutil.copy2(T / f, T / f"{f}.bak")
    shutil.copyfile(D / f"{a.donor}.bank", T / f"{a.target}.bank")
    g = (D / "GUIDs.txt").read_bytes().decode("latin1")
    (T / "GUIDs.txt").write_bytes(g.replace(a.donor, a.target).encode("latin1"))
    print(f"{a.target}: Bank von {a.donor}, {g.count(a.donor)} Pfade umgeschrieben")
    if a.vol_int or a.vol_ext:
        p = cars / a.target / "extension" / "ext_config.ini"
        if not Path(str(p) + ".bak").exists(): shutil.copy2(p, str(p) + ".bak")
        t = p.read_bytes().decode("latin1")
        if a.vol_ext: t, _ = set_value(t, "AUDIO_VOLUME", "ENGINE_EXT", a.vol_ext)
        if a.vol_int: t, _ = set_value(t, "AUDIO_VOLUME", "ENGINE_INT", a.vol_int)
        p.write_bytes(t.encode("latin1"))
        print(f"{a.target}: [AUDIO_VOLUME] gesetzt")


if __name__ == "__main__":
    main()
