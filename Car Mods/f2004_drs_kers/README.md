# Ferrari F2004 mit DRS und KERS (2013) und Pirelli-Mischungen 2018

Ziel: Der Kunos-F2004 mit der Technik, die er nie hatte: DRS und KERS nach dem Reglement 2013, dazu die fünf Trockenmischungen der RSS Formula Hybrid 2018 (Hyper-Soft bis Medium). Vorlagen: Cimmerian Iter 2013 Ferrari (DRS, KERS) und RSS Formula Hybrid 2018 (Reifen).

## Was drin ist

| Baustein | Umsetzung | Stand |
|---|---|---|
| DRS | Kunos-Heckflügel in Hauptblatt (55 %) und Klappe (45 %) geteilt, `drs.ini` setzt die Klappe bei offenem DRS auf 0 Grad. Offen: rund 14 % weniger Widerstand, 42 % weniger Heckflügel-Abtrieb, etwa plus 17 km/h. Herleitung in `research/01-drs-herleitung.md` | gebaut, Physik als data.acd gepackt (AC lud die drs.ini aus dem offenen data-Ordner nicht) |
| DRS-Animation | Die obere Klappe (128 Dreiecke) wird mit `tools/make_flap.py` aus der Karosserie-Mesh des Kunos-Modells in einen eigenen Knoten `WING_Rear_Flap` getrennt (Haupt-kn5 und LOD B) und mit `car_wing.ksanim` um 30 Grad geöffnet, Drehpunkt Hinterkante | gebaut, im Spiel noch nicht gesehen |
| KERS | 60 kW, 400 kJ pro Runde, 6,6 s, Knopfbetrieb. Lade-Werte vom CIM 2013, Drehmomentkurve auf 60 kW über das V10-Band | gebaut |
| Reifen | tyres.ini der Formula Hybrid 2018 unverändert mit allen LUTs (auch Breite 305/405 und Radius 0,335). Standard Hyper-Soft | gebaut |
| Setup | "Rear wing main" verstellt das Hauptblatt (55 % des Flügels), die Klappe steht fest auf 25 Grad, damit Animation und Physik zusammenpassen | gebaut |
| Modell, Sound, Skins | unverändert vom Kunos-F2004, Sound auf neuen Ordnernamen umgeschrieben | fertig |

LOD C und D (ab 45 m) behalten die geschlossene Klappe.

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
  tools/make_flap.py      trennt die Klappe im kn5 ab und schreibt die Animation
  tools/kn5.py            kn5 lesen und schreiben
  physics/                eigene Dateien: kers.ini, kers_torque.lut
  research/               Quellen (00), DRS-Herleitung (01), KERS und Reifen (02), Rechenskript
```

Kunos- und RSS-Dateien liegen nicht im Repo, sie entstehen beim Bauen aus den installierten Autos.

## Nächste Schritte

- Im Spiel fahren: Klappe öffnet sichtbar in der DRS-Zone, Topspeed mit und ohne DRS messen (Monza), KERS-Abgabe prüfen, Reifentemperaturen (Ideal 95 Grad) beobachten.
- Öffnet die Klappe in die falsche Richtung oder zu weit: `OPEN_DEG` und Vorzeichen in `tools/make_flap.py`.
- Falls der Hyper-Soft zu viel Grip hat: `DY_REF`/`DX_REF` in `tools/build.py` skalieren.
- Klappenanteil `FLAP_SHARE` nach Messung anpassen.
