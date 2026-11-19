"""Sortiert die F1-Mod-Autos im Content Manager nach Saison: Brand in ui_car.json wird "F1 <Jahr>".

  py -3.11 tools/brands_nach_jahr.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa"            (zeigt nur den Plan)
  py -3.11 tools/brands_nach_jahr.py --ac <AC> --apply
  py -3.11 tools/brands_nach_jahr.py --ac <AC> --restore                                            (alte Brands zurück)

Nur die Zeile "brand" wird ersetzt, der Rest der Datei bleibt Byte für Byte gleich. Die alte Brand steht
danach in ui/ui_car.json.brand.bak (Kopie der Originaldatei) und in data/brands_vorher.json.
Kunos-Originale und Nicht-F1-Formelautos (GP2, Formula Renault 3.5, IndyCar, Red Bull X1) bleiben unberührt.
"""
import argparse
import json
import os
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
VORHER = HERE.parent / "data" / "brands_vorher.json"
BRAND = re.compile(r'("brand"\s*:\s*")([^"]*)(")')

# Ordner-Präfix (Kleinbuchstaben) -> Jahr. Längster Treffer gewinnt.
PRAEFIX = {
    "f1_1990_": 1990, "f1_1995_": 1995, "acfl_2016_": 2016,
    "f1_1983_": 1983, "f1_1988_": 1988, "vrc_1988_": 1988, "f1_1993_": 1993, "acfl_1994_": 1994,
    "f1_1996_": 1996, "f1_1997_": 1997, "gp_1997_": 1997, "vrc_1997_": 1997, "gp_1998_": 1998,
    "f1_1999_": 1999, "gp_1999_": 1999, "gp_2000_": 2000, "f1_2001_": 2001, "f1_2002_": 2002,
    "f1_2003_": 2003, "f1_2004_": 2004, "msf_2004_": 2004, "asr_2004_": 2004, "vrc_2005_": 2005,
    "acfl_2006_": 2006, "cim_2006_": 2006, "f1_2006_": 2006, "cim_2007_": 2007, "cim_2008_": 2008,
    "f1_2009_": 2009, "trp_2009_": 2009, "vrc_2009_": 2009, "cim_2010_": 2010, "cim_2011_": 2011,
    "cim_2012_": 2012, "f1_2012_": 2012, "cim_2013_": 2013, "f1_2014_": 2014,
    "rss_formula_hybrid_2017": 2017, "rss_formula_hybrid_2018": 2018, "f1_2018_": 2018,
    "rss_formula_hybrid_2019": 2019, "rss_formula_hybrid_2020": 2020, "f1_2020_": 2020,
    "acfl_f1_2021": 2021, "acfl_f1_2023_": 2023, "f1_2023_": 2023, "aston_martin_amr23": 2023,
    "rss_formula_hybrid_2024": 2024, "vrc_formula_alpha_2024": 2024, "f1_2026": 2026,
}
# Einzelne Ordner (Kleinbuchstaben) -> Jahr
EINZELN = {
    "f1_williams_fw14b": 1992, "mhr_ps01": 2001, "msf_williams_fw26_vers_b": 2004,
    "ks_ferrari_f2004_s0": 2004, "ks_ferrari_f2004_s1": 2004, "ks_ferrari_f2004_s3": 2004, "ks_ferrari_f2004_slicks": 2004,
    "vrc_formula_alpha_2007_mc22": 2007, "red_bull_rb7": 2011, "ferrari_f2012": 2012, "redbull_rb9": 2013,
    "caterham_2014": 2014, "caterham_late_2014": 2014, "ferrari_2014": 2014, "forceindia_2014": 2014, "lotus_2014": 2014,
    "marussia_2014": 2014, "mclaren_2014": 2014, "mercedes_w05_hybrid": 2014, "redbull_2014": 2014, "sauber_2014": 2014,
    "tororosso_2014": 2014, "williams_2014": 2014,
    "acr_ferrari_sf71h": 2018, "ferrari_sf90": 2019, "alpine_a521": 2021, "red_bull_rb16b_ds": 2021,
    "f1_mclaren_2024": 2024, "f1_sauber_2024": 2024,
    "aston_martin_amr25": 2025, "f1_alpine_2025": 2025, "f1_haas_2025": 2025, "ferrari_sf25": 2025, "forbys_sauber_c45": 2025,
    "mclaren_mcl39": 2025, "mercedes_w16": 2025, "racingbulls_rb02": 2025, "red_bull_rb21": 2025, "williams_fw47": 2025,
    "formula_ultra_26": 2026,
}


# Auf Wunsch des Nutzers nicht in der Jahres-Brand: die Formula-Hybrid-Grundautos (die Team-Autos daraus bleiben
# in "F1 <Jahr>") und der SF71H von ACR.
WUNSCH = {"rss_formula_hybrid_2018": "Race Sim Studio", "rss_formula_hybrid_2018_s1": "Race Sim Studio",
          "rss_formula_hybrid_2019": "Race Sim Studio", "rss_formula_hybrid_2020": "Race Sim Studio",
          "rss_formula_hybrid_2017": "Race Sim Studio", "rss_formula_hybrid_2024": "Race Sim Studio",
          "acr_ferrari_sf71h": "Ferrari",
          # Brand "F1 2026" gibt es auf Wunsch nicht: diese drei behalten ihre ursprüngliche Brand
          "f1_2026": "FIA", "f1_2026_sf26": "Ferrari F1", "formula_ultra_26": "Formula Ultra"}


def jahr(ordner):
    n = ordner.lower()
    if n in EINZELN:
        return EINZELN[n]
    treffer = [p for p in PRAEFIX if n.startswith(p)]
    return PRAEFIX[max(treffer, key=len)] if treffer else None


def schreibe(ui, text):
    tmp = ui.with_suffix(".json.tmp")
    tmp.write_bytes(text.encode("latin-1"))   # latin-1 bildet jedes Byte 1:1 ab, die Kodierung bleibt erhalten
    os.replace(tmp, ui)                       # löst auch einen eventuellen Hardlink


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ac", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--restore", action="store_true")
    a = ap.parse_args()
    cars = Path(a.ac) / "content" / "cars"

    if a.restore:
        alt = json.loads(VORHER.read_text(encoding="utf-8"))
        for ordner, brand in alt.items():
            ui = cars / ordner / "ui" / "ui_car.json"
            if ui.is_file():
                schreibe(ui, BRAND.sub(lambda m: m.group(1) + brand + m.group(3), ui.read_bytes().decode("latin-1"), count=1))
        print(f"{len(alt)} Brands zurückgesetzt")
        return

    alt = json.loads(VORHER.read_text(encoding="utf-8")) if VORHER.is_file() else {}
    zahl, fehler = {}, []
    for d in sorted(cars.iterdir(), key=lambda p: p.name.lower()):
        j = jahr(d.name)
        ui = d / "ui" / "ui_car.json"
        if j is None or d.name.lower().endswith(".bak") or not ui.is_file():
            continue
        text = ui.read_bytes().decode("latin-1")
        m = BRAND.search(text)
        if not m:
            fehler.append(d.name)
            continue
        n = d.name.lower()                                       # The Race Project 2026 bleibt auf Wunsch eine eigene Brand
        neu = "F1 2026 TRP" if n.startswith("f1_2026_") and n != "f1_2026_sf26" else f"F1 {j}"
        if n.startswith("f1_2012_"): neu = "Ponz F1"            # Ponz 2012 getrennt von Cimmerian (Wunsch des Nutzers)
        neu = WUNSCH.get(n, neu)
        zahl[neu] = zahl.get(neu, 0) + 1
        if m.group(2) == neu:
            continue
        print(f"{d.name:42s} {m.group(2).encode('latin-1').decode('utf-8', 'replace'):28s} -> {neu}")
        if a.apply:
            alt.setdefault(d.name, m.group(2))
            bak = ui.with_suffix(".json.brand.bak")
            if not bak.exists():
                shutil.copy2(ui, bak)
            schreibe(ui, text[:m.start(2)] + neu + text[m.end(2):])
    if a.apply:
        VORHER.write_text(json.dumps(alt, indent=1, ensure_ascii=False), encoding="utf-8")
    print()
    for b in sorted(zahl):
        print(f"{b}: {zahl[b]} Autos")
    print(f"\n{sum(zahl.values())} Autos in {len(zahl)} Jahren" + ("" if a.apply else "  (nur Plan, --apply schreibt)"))
    if fehler:
        print("Keine brand-Zeile gefunden:", ", ".join(fehler))


if __name__ == "__main__":
    main()
