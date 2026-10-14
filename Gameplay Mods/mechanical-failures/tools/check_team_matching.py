"""Prüft für alle F1-Autos der AC-Installation, welchem F1DB-Konstrukteur die App sie zuordnen würde.
Bildet die Logik aus app/reliability/reliability.lua (teamFactor) in Python nach.

  python check_team_matching.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" [--all]

Ohne --all werden nur Autos ohne Zuordnung gelistet.
"""
import argparse
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALIASES = {
    'larrousse': 'lola', 'amr': 'aston-martin', 'amr23': 'aston-martin', 'amr24': 'aston-martin', 'sf71h': 'ferrari', 'sf90': 'ferrari',
    'f310': 'ferrari', 'f310b': 'ferrari', 'f300': 'ferrari', 'f399': 'ferrari', 'f2000': 'ferrari', 'f2001': 'ferrari', 'f2002': 'ferrari',
    'f2003ga': 'ferrari', 'f2004': 'ferrari', 'w11': 'mercedes', 'w12': 'mercedes', 'w13': 'mercedes', 'w14': 'mercedes',
    'rb16': 'red-bull', 'rb18': 'red-bull', 'rb19': 'red-bull', 'rb20': 'red-bull', 'mp4': 'mclaren', 'mcl': 'mclaren',
    'scuderia': 'ferrari', 'stake': 'kick-sauber', 'bwt': 'racing-point', 'visa': 'rb', 'vcarb': 'rb',
    # Chassis-Codes 1997 bis 2000 (Grand-Prix-Mods)
    'a18': 'arrows', 'a19': 'arrows', 'a20': 'arrows', 'a21': 'arrows', 'a22': 'arrows', 'a23': 'arrows',
    'b197': 'benetton', 'b198': 'benetton', 'b199': 'benetton', 'b200': 'benetton', 'b201': 'benetton',
    'c16': 'sauber', 'c17': 'sauber', 'c18': 'sauber', 'c19': 'sauber', 'c20': 'sauber', 'c21': 'sauber', 'c22': 'sauber', 'c23': 'sauber',
    'fw19': 'williams', 'fw20': 'williams', 'fw21': 'williams', 'fw22': 'williams', 'fw23': 'williams', 'fw24': 'williams', 'fw25': 'williams', 'fw26': 'williams',
    'js45': 'ligier', 'm197': 'minardi', 'm198': 'minardi', 'm01': 'minardi', 'm02': 'minardi', 'ps01': 'minardi', 'ps03': 'minardi',
    'sf01': 'stewart', 'sf2': 'stewart', 'sf3': 'stewart', 't97': 'tyrrell', 'ap01': 'prost', 'ap02': 'prost', 'ap03': 'prost', 'ap04': 'prost',
    'ej10': 'jordan', 'ej11': 'jordan', 'ej12': 'jordan', 'r1': 'jaguar', 'r2': 'jaguar', 'r3': 'jaguar', 'r4': 'jaguar', 'r5': 'jaguar',
    'sf15t': 'ferrari', 'sf16h': 'ferrari', 'sf70h': 'ferrari', 'sf1000': 'ferrari', 'sf21': 'ferrari', 'sf23': 'ferrari', 'sf24': 'ferrari', 'sf25': 'ferrari',
}


def norm(s):
    return re.sub(r'[^0-9a-z]', '', str(s).lower())


def toks(s):
    return set(re.findall(r'[0-9a-z]+', str(s).lower()))


def match_in(cons, flat, tk):
    best = None
    for name, v in cons.items():
        cand = norm(name)
        hit = False
        if len(cand) >= 4:
            hit = cand in flat
            if not hit:
                short = re.sub(r'racing$', '', re.sub(r'f1$', '', cand))
                if len(short) >= 4 and short != cand and short in flat:
                    hit = True
                    cand = short
        else:
            hit = cand in tk
        if hit and (best is None or len(cand) > best[0]):
            best = (len(cand), name, v)
    if best:
        return best[1], best[2]
    for t in tk:
        a = ALIASES.get(t)
        if a and a in cons:
            return a, cons[a]
    for name, v in cons.items():
        for part in name.split('-'):
            if len(part) >= 5 and norm(part) in flat and (best is None or len(part) > best[0]):
                best = (len(part), name, v)
    return (best[1], best[2]) if best else (None, None)


def team_factor(rates, raw, skin, season):
    for s in (season, season - 1, season + 1, season - 2, season + 2):
        cons = {k.split(':')[1]: v for k, v in rates.items() if k.startswith(f'{s}:')}
        if not cons:
            continue
        for st in (raw, raw + ' ' + skin):
            name, v = match_in(cons, norm(st), toks(st))
            if v:
                return max(0.3, min(2.5, v['factor'])), (name if s == season else f'{name} ({s})')
    return 1.0, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ac', required=True)
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    rates = json.load(open(HERE.parent / 'research' / 'data' / 'failure_rates.json', encoding='utf-8'))['constructors']
    cars = Path(a.ac) / 'content' / 'cars'
    ok = bad = 0
    for c in sorted(os.listdir(cars), key=str.lower):
        ui = cars / c / 'ui' / 'ui_car.json'
        if not ui.is_file():
            continue
        try:
            j = json.loads(re.sub(r'[\x00-\x1f]', ' ', ui.read_text(encoding='utf-8', errors='ignore')), strict=False)
        except Exception:
            continue
        try:
            year = int(j.get('year') or 0)
        except Exception:
            year = 0
        tags = ' '.join(j.get('tags') or [])
        raw = f"{c} {j.get('brand', '')} {j.get('name', '')}"
        # wie in der App: Jahr zuerst aus Ordnername oder Anzeigename, sonst ui_car.json
        for m in re.findall(r'(?<!\d)(\d{4})(?!\d)', raw):
            if 1988 <= int(m) <= 2026:
                year = int(m)
                break
        isf1 = re.search(r'f1|formula|grand prix', (raw + ' ' + tags).lower()) and 1988 <= year <= 2026
        if not isf1 and not a.all:
            continue
        skins = sorted(os.listdir(cars / c / 'skins')) if (cars / c / 'skins').is_dir() else ['']
        f, name = team_factor(rates, raw, skins[0] if skins else '', year)
        if name:
            ok += 1
        else:
            bad += 1
        if not name or a.all:
            print(f'{year} {c:38s} -> {name or "KEIN TEAM (1.0)":22s} {f:.2f}   [{j.get("brand", "")} | {j.get("name", "")} | skin {skins[0] if skins else ""}]')
    print(f'\n{ok} zugeordnet, {bad} ohne Team')


if __name__ == '__main__':
    main()
