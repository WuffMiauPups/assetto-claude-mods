# Ferrari F2004 mit DRS und KERS (2013) und Pirelli-Mischungen 2018

Ziel: Der Kunos-F2004 mit der Technik, die er nie hatte: DRS und KERS nach dem Reglement 2013, dazu die fünf Trockenmischungen der RSS Formula Hybrid 2018 (Hyper-Soft bis Medium). Vorlagen: Cimmerian Iter 2013 Ferrari (DRS, KERS) und RSS Formula Hybrid 2018 (Reifen).

## Was drin ist

| Baustein | Umsetzung | Stand |
|---|---|---|
| DRS | Kunos-Heckflügel in Hauptblatt (55 %) und Klappe (45 %) geteilt, `drs.ini` setzt die Klappe bei offenem DRS auf 0 Grad. Offen: rund 14 % weniger Widerstand, 42 % weniger Heckflügel-Abtrieb, etwa plus 17 km/h. Herleitung in `research/01-drs-herleitung.md` | gebaut, im Spiel noch nicht gefahren |
| KERS | 60 kW, 400 kJ pro Runde, 6,6 s, Knopfbetrieb. Lade-Werte vom CIM 2013, Drehmomentkurve auf 60 kW über das V10-Band | gebaut |
| Reifen | tyres.ini der Formula Hybrid 2018 mit allen LUTs, Geometrie des F2004 (245/325, 13 Zoll). Standard Hyper-Soft | gebaut |
| Setup | zwei Heckflügel-Einträge: "Rear wing main" und "Rear flap (DRS)" | gebaut |
| Modell, Sound, Skins | unverändert vom Kunos-F2004, Sound auf neuen Ordnernamen umgeschrieben | fertig |

Keine bewegliche Klappe am 3D-Modell, DRS ist nur physikalisch und in der Anzeige vorhanden.

## Installation

Aus diesem Ordner:

```bash
py -3.11 tools/build.py
```

Baut `content\cars\ferrari_f2004_drs_kers` neu aus `ks_ferrari_f2004` und `rss_formula_hybrid_2018` (beide müssen installiert sein, beide bleiben unverändert). Ein vorhandener Zielordner wird als `.bak` gesichert. Der neue Ordner hat einen entpackten `data`-Ordner und keine `data.acd`.

Im Spiel: DRS-Taste und KERS-Taste wie bei den 2013er Autos belegen (Content Manager, Steuerung). Im Content Manager heißt das Auto "Ferrari F2004 DRS KERS".

## Ordner

```
f2004_drs_kers/
  tools/build.py          baut das Auto, enthält die ganze Ableitung (Reifen, Flügelteilung, Namen)
  physics/                eigene Dateien: kers.ini, kers_torque.lut
  research/               Quellen (00), DRS-Herleitung (01), KERS und Reifen (02), Rechenskript
```

Kunos- und RSS-Dateien liegen nicht im Repo, sie entstehen beim Bauen aus den installierten Autos.

## Nächste Schritte

- Im Spiel fahren: Topspeed mit und ohne DRS messen (Monza), KERS-Abgabe prüfen, Reifentemperaturen (Ideal 95 Grad) beobachten.
- Falls der Hyper-Soft zu viel Grip hat: `DY_REF`/`DX_REF` in `tools/build.py` skalieren.
- Klappenanteil `FLAP_SHARE` nach Messung anpassen.
