# Physik

`data/` ist der komplette, entpackte `data`-Ordner des Autos. Er wird von `tools/build_aero.py` erzeugt (Basis: `reference/vac_groupc_956/data`, Unterboden-Kennfelder aus `tools/venturi_model.py`) und von `tools/install.py` ins Spiel nach `content/cars/porsche_956_venturi/data` gespiegelt. Nicht von Hand in `data/` editieren, sondern die Skripte anpassen.

| Datei | Herkunft | Status |
|---|---|---|
| `data/aero/*.2Dlut`, `*.lut` | erzeugt von `tools/venturi_model.py` | erzeugt, unkalibriert |
| `data/aero.ini` | erzeugt von `build_aero.py`: Karosserie (nur Widerstand), Front- und Heckflügel skaliert, `[MAP_0]` Unterboden; Diffusor-Flügel und Speed-Controller des Basis-Mods entfernt | erste Fassung, Spieltest offen |
| `data/car.ini` | Basis-Mod, `VERSION=extended-2`, Name geändert; Masse 915 kg noch vom Basis-Mod | Masse und Schwerpunkt offen |
| `data/suspensions.ini` | Basis-Mod, `ROD_LENGTH` und `SPRING_RATE` von `build_aero.py` gesetzt (55/85 mm, 140/190 N/mm) | Messung 2 abwarten |
| `data/tyres.ini` | Basis-Mod | Dunlop 1983 vorn 13 Zoll offen |
| `data/engine.ini`, `power.lut` | Basis-Mod (611 PS bei 8200) | Turbo-Quali-Trimm offen |
| `data/drivetrain.ini`, `*.rto` | Basis-Mod | Übersetzungen Ring offen |
| alle übrigen | Basis-Mod unverändert | |
| `aero_map_template.ini`, `setup_aeromap_template.ini` | Vorlagen, Map-Block ist inzwischen in `build_aero.py` | nur noch Referenz |

## Kennzahlen der ersten Fassung (`tools/out/build_aero.json`)

## Messung 1 (2026-10-13, Basis-Fahrwerk, `tools/out/messungen/01_basisfahrwerk_20261013.csv`)

Statisch 60 mm vorn, 62 mm hinten (die Geometrie-Schätzung 81/90 war 21/28 mm zu hoch, `build_aero.py` nutzt jetzt die Messwerte). Mit den weichen Basis-Federn (78/110 N/mm) sinkt das Heck ab 200 km/h auf 25 mm, also unter die Abrisshöhe von 30 mm: Abtrieb springt zwischen 700 und 1450 kg, Balance 10 bis 45 Prozent vorn. Das ist der Abriss mit Aufschaukeln, nur viel zu früh. Mehr als 260 km/h wurden nicht erreicht.

Konsequenz in `build_aero.py`: `ROD_LENGTH` auf 0,011/0,0375 (Ziel statisch 55/85 mm wie im Modell), Radraten 140/190 N/mm aus dem Modell, Setup-Bereiche der Federn angehoben. Erwartung laut Modell: bei 300 km/h etwa 35 mm vorn, 52 mm hinten, Heck bleibt über dem Abriss.


| Größe | statisch (Fassung 2, 55/85 mm) | Ziel Modell bei Design-Höhe 55/85 mm |
|---|---|---|
| Cl·A Unterboden | 2,27 | 2,28 |
| Cl·A gesamt | 3,79 | 3,80 |
| Cd·A gesamt | 1,04 | 1,04 |
| Balance vorn | 0,36 | 0,42 |

Beim Einfedern unter Abtrieb läuft das Heck in den steilen Bereich des Kennfelds (unter 60 mm), das ist gewollt.

## Messung 2 (2026-10-13, Modellfahrwerk, `tools/out/messungen/02_modellfahrwerk_20261013.csv`)

Statisch 62/87 mm. Heck bleibt bei 280 km/h mit 59 mm über dem Abriss, Abtrieb steigt sauber: 804 kg bei 200, 1150 bei 240, 1655 bei 280 km/h (Modell 819, 1282, 1840). Balance 35 Prozent vorn (Ziel 42). Topspeed nur 280 km/h, Widerstand zu hoch.

Konsequenz in `venturi_model.py`: `total_drag_kg` 640 auf 520 (Karosserie-`CD_GAIN` jetzt 1,78, rechnerisch rund 300 km/h), `ub_front_balance` 0,40 auf 0,45.

## Bekannte Baustellen

- **Widerstand**: nach Messung 2 auf Cd·A 1,04 gesenkt (520 kg bei 322 km/h). Ziel-Topspeed Döttinger Höhe mit Quali-Motor rund 310 bis 320 km/h, Messung 3 abwarten.
- **Masse**: Basis-Mod 915 kg mit Fahrer, Ziel laut Recherche rund 820 bis 850 kg plus Fahrer.

Abstimmungsziel: Bei Höchstgeschwindigkeit soll die Bodenfreiheit hinten knapp über der Abrisshöhe (30 mm) liegen, damit Bodenwellen und Kuppen das Auto kurz in den Abriss schicken. Das ist der historische Charakter, siehe Bellofs Überschlag an der Kuppe im Rennen 1983.

## Testablauf

1. `python tools/venturi_model.py`, dann `python tools/build_aero.py`, dann `python tools/install.py` (aus `tools/` heraus).
2. Content Manager: Auto "Porsche 956 Venturi (WIP)", Strecke Nordschleife, Practice.
3. Prüfen, ob das Auto lädt (Fehler in `Documents\Assetto Corsa\logs\log.txt`, Suche nach `aero` oder `MAP_0`).
4. App "Ride Height Monitor" (wird von `install.py` nach `apps/lua` kopiert) öffnen. Sie zeigt Bodenfreiheit, Abtrieb (aus Radlasten minus statischer Last, deshalb vor dem Losfahren kurz stehen bleiben), Balance und Radlasten live und mittelt je 10 km/h bei ruhiger Geradeausfahrt. Döttinger Höhe einmal voll durchfahren, dann "CSV speichern". Datei liegt in `apps/lua/rideheight_monitor/logs/`.
5. Vergleich mit `tools/out/summary.json` (Gleichgewicht über Geschwindigkeit), Kalibrierung in `venturi_model.py`.
