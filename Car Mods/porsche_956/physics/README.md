# Physik

`data/` ist der komplette, entpackte `data`-Ordner des Autos. Er wird von `tools/build_aero.py` erzeugt (Basis: `reference/vac_groupc_956/data`, Unterboden-Kennfelder aus `tools/venturi_model.py`) und von `tools/install.py` ins Spiel nach `content/cars/porsche_956_venturi/data` gespiegelt. Nicht von Hand in `data/` editieren, sondern die Skripte anpassen.

| Datei | Herkunft | Status |
|---|---|---|
| `data/aero/*.2Dlut`, `*.lut` | erzeugt von `tools/venturi_model.py` | erzeugt, unkalibriert |
| `data/aero.ini` | erzeugt von `build_aero.py`: Karosserie (nur Widerstand), Front- und Heckflügel skaliert, `[MAP_0]` Unterboden; Diffusor-Flügel und Speed-Controller des Basis-Mods entfernt | erste Fassung, Spieltest offen |
| `data/car.ini` | Basis-Mod, `VERSION=extended-2`, Name geändert, Masse 895 kg (820 plus Fahrer) | Schwerpunkt, Trägheit offen |
| `data/suspensions.ini` | Basis-Mod, `ROD_LENGTH` und `SPRING_RATE` von `build_aero.py` gesetzt (55/85 mm, 140/190 N/mm) | Messung 2 abwarten |
| `data/tyres.ini` | Maße von `build_aero.py` (`TYRES`): 280/650-13 vorn, 350/650-16 hinten, Radius 0,325 m beide. BASEY und ROD_LENGTH kompensieren den um 45 mm größeren Vorderreifen, Schwerpunkt und Bodenfreiheit bleiben. Gummi, Thermik, Verschleiß noch Basis-Mod | Spieltest, dann Verschleiß |
| `data/engine.ini`, `power.lut` | von `build_aero.py` (`ENGINE`): 935/76, zwei Turbos je 0,65 bar, Regler 100 % = Quali 1,3 bar 672 PS, 92 % = Rennen 1,2 bar 641 PS, 85 % = Le Mans 615 PS. 600 Nm 5000 bis 6500. Schätzung | getestet, 300 km/h, Turbo ab 4000 spürbar |
| `data/drivetrain.ini` | Fahrer-Übersetzung 14/37, 18/34, 22/29, 26/26, 28/23, Achse 8/31 (3,875), Fünfter am Begrenzer 329 km/h | Achse bestätigen |
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

## Messung 3 (2026-10-13, Widerstand 520 kg, `tools/out/messungen/03_drag520_20261013.csv`)

Abtrieb trifft das Modell jetzt fast genau: 678 kg bei 200 (Modell bei den gemessenen Höhen 729), 1360 bei 260 (1404), 1578 bei 270 (1585). Bodenfreiheit bei 270 km/h 43/61 mm. Topspeed nur 270 km/h, obwohl der Widerstand gesenkt wurde; Getriebe lässt rechnerisch 293 km/h im Fünften zu (0,82 × 4,43, Radius 0,33 m, 8560/min). Ursache offen, Fahrerangabe zu Drehzahl und Gang bei Topspeed nötig.

Balance aus Radlasten 35 Prozent vorn, unverändert gegenüber Messung 2 trotz `ub_front_balance` 0,40 auf 0,45. Die Radlast-Messung enthält aber die Lastverlagerung durch das Widerstandsmoment (Widerstand greift laut `DRAG_OFFSET` 0,35 m über dem Schwerpunkt an, rund 0,69 m über Boden): bei 260 km/h etwa 90 kg nach hinten, also rund 6 Prozentpunkte. Die reine Aero-Balance liegt damit bei etwa 41 Prozent und damit am Ziel. Balance wird vorerst nicht weiter angefasst.

## Messung 4 (2026-10-13, langer Anlauf Döttinger Höhe, `tools/out/messungen/04_topspeed_20261013.csv`)

Topspeed 290 km/h im Fünften bei knapp 8000/min (Begrenzer 8560, Getriebe erlaubt 293), also leistungs- und widerstandsbegrenzt wie berechnet. Bei 290 km/h: 39 mm vorn, 58 mm hinten, 1842 kg Abtrieb (Modell rund 1900), Balance aus Radlasten 36 Prozent (plus rund 6 Punkte Widerstandsmoment). Fahrerurteil: sehr stabil bei hohem Tempo, ruhig beim Anbremsen, Heck wird nur bei frühem Herunterschalten leicht.

**Aero-Phase damit abgeschlossen.** Kennfeld, Fahrwerk und Widerstand bleiben so, bis Motor, Masse und Reifen auf 1983 stehen. Danach erneut messen.

## Messung 5 (2026-10-14, Motor 935/76 Quali 1,3 bar, 895 kg, `tools/out/messungen/05_motor1983_20261014.csv`)

Topspeed 300 km/h mit vollem Anlauf (Drehzahl passt, Begrenzer nicht erreicht). Bei 300 km/h: 38 mm vorn, 55 mm hinten, 1999 kg Abtrieb, Balance aus Radlasten 38 Prozent (plus Widerstandsmoment, also reine Aero-Balance über 40). Das Heck liegt bei Topspeed 25 mm über dem Abriss, das Auto bleibt laut Fahrer stabil. Turbo setzt ab etwa 4000/min spürbar ein. Fahrer-Übersetzung 14/37, 18/34, 22/29, 26/26, 28/23 ist jetzt Standard in `drivetrain.ini`, Achse 8/31 angenommen. Fahreindruck Reifen: untersteuernd bei niedrigem Tempo, leicht untersteuernd bei hohem, im Grenzbereich schiebt das Heck, Hinterräder blockieren bei zu frühem Herunterschalten, kaum Gripabbau. Entspricht dem historischen Urteil über den 956.

## Messung 6 (2026-10-14, Reifen 1983, `tools/out/messungen/06_reifen1983_zu_tief_20261014.csv`)

Statisch nur 42/74 mm statt 55/85: Die Stangenlängen-Kompensation für den größeren Vorderreifen war 12 mm zu schwach, die Stangenlänge wirkt nicht 1:1. Folge: Heck bei 240 km/h schon auf 44 mm, mehr Abtrieb und Widerstand als geplant, Topspeed 280. Aero bei gleichen Höhen unverändert konsistent mit Messung 5. Konsequenz: `MEASURED_STATIC_RH` in `build_aero.py` auf diese Messung gesetzt, Stangenlängen jetzt -0,021/0,0535.

## Fahrtest 7 (2026-10-17, Stangenlängen -0,021/0,0535): deutlich weniger Grip, fährt sich fremd

Ursache gefunden: In AC ist der Einfederweg `BUMPSTOP_UP + ROD_LENGTH`. Mit der negativen Stangenlänge vorn blieben nur 29 mm (Messung 6: 16 mm) bis zum harten Anschlag, das Auto lag vorn ständig auf dem Puffer. `build_aero.py` setzt `BUMPSTOP_UP` und `PACKER_RANGE` jetzt so, dass der Federweg dem der Messungen 2 bis 5 entspricht (vorn 61 mm, hinten 97 mm). Stand-Messung danach wieder 41,5/72,5: Der Setup-Bildschirm zeigte Height LF 0 und LR 160. Das gespeicherte Setup überschreibt `ROD_LENGTH`, Einheit ist 0,1 mm (160 = 0,016 m). Die Stangenlänge wirkt also vermutlich doch 1:1, nur kamen die Dateiwerte nie an. `build_aero.py` kalibriert jetzt auf 0,000/0,016 und setzt die Setup-Bereiche in 0,1 mm um die Standardwerte. **Im Spiel müssen die Höhen im Setup einmal auf die Dateiwerte gestellt werden** (Height LF/RF und LR/RR, Werte siehe Build-Ausgabe), oder Setup auf Default. Fahrer-Entscheidung 2026-10-17: Setup bleibt (Height 30/30), Stand damit 63/85 mm; die Aero-Map bekommt `FRONT_RH_OFFSET=-0.008`, damit sie 55/85 sieht.

## Fahrtest 8 (2026-10-17, Setup des Fahrers, Map-Versatz vorn -8 mm, keine CSV)

Grip wieder gut, Einlenken mit den 13-Zoll-Vorderrädern besser als vorher. Reifenmaße bleiben. Döttinger Höhe nur 290 km/h, Vortrieb subjektiv zu schwach, Begrenzer nicht erreicht. Konsequenz: Quali-Trimm von 672 auf rund 710 PS (Schätzung), Turbostufe 100 Prozent als Standard.

## Bekannte Baustellen

- **Widerstand**: Cd·A 1,04 (520 kg bei 322 km/h). Mit Quali-Motor 300 km/h gemessen bei nicht ganz vollem Anlauf, rechnerisch 310 bis 320 möglich. Bleibt so.

Abstimmungsziel: Bei Höchstgeschwindigkeit soll die Bodenfreiheit hinten knapp über der Abrisshöhe (30 mm) liegen, damit Bodenwellen und Kuppen das Auto kurz in den Abriss schicken. Das ist der historische Charakter, siehe Bellofs Überschlag an der Kuppe im Rennen 1983.

## Testablauf

1. `python tools/venturi_model.py`, dann `python tools/build_aero.py`, dann `python tools/install.py` (aus `tools/` heraus).
2. Content Manager: Auto "Porsche 956 Venturi (WIP)", Strecke Nordschleife, Practice.
3. Prüfen, ob das Auto lädt (Fehler in `Documents\Assetto Corsa\logs\log.txt`, Suche nach `aero` oder `MAP_0`).
4. App "Ride Height Monitor" (wird von `install.py` nach `apps/lua` kopiert) öffnen. Sie zeigt Bodenfreiheit, Abtrieb (aus Radlasten minus statischer Last, deshalb vor dem Losfahren kurz stehen bleiben), Balance und Radlasten live und mittelt je 10 km/h bei ruhiger Geradeausfahrt. Döttinger Höhe einmal voll durchfahren, dann "CSV speichern". Datei liegt in `apps/lua/rideheight_monitor/logs/`.
5. Vergleich mit `tools/out/summary.json` (Gleichgewicht über Geschwindigkeit), Kalibrierung in `venturi_model.py`.
