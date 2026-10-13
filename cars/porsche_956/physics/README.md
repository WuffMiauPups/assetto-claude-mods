# Physik

Hier entsteht der entpackte `data`-Ordner des Autos. Basis wird der `data`-Ordner des installierten 956-Mods, der schrittweise ersetzt wird.

| Datei | Herkunft | Status |
|---|---|---|
| `data/aero/*.2Dlut`, `*.lut` | erzeugt von `tools/venturi_model.py` | erzeugt, unkalibriert |
| `aero_map_template.ini` | Vorlage für den `[MAP_0]`-Block in `data/aero.ini` | fertig |
| `setup_aeromap_template.ini` | Vorlage für Map-Umschaltung im Setup | fertig |
| `data/car.ini` | Basis-Mod, `VERSION=extended-2`, Masse 820 kg, Schwerpunkt | offen |
| `data/aero.ini` | Basis-Mod, Flügel neu skaliert, Map-Block eingefügt | offen |
| `data/suspensions.ini` | Doppelquerlenker, Radstand 2650, Federraten aus Modell, progressive Kennung | offen |
| `data/tyres.ini` | Dunlop 280/650 und 350/650, 1983 vorn 13 Zoll Felge | offen |
| `data/engine.ini`, `power.lut`, Turbo | 935/76, 620 PS bei 8200, 1,3 bar Quali | offen |
| `data/drivetrain.ini` | 5-Gang Transaxle, Übersetzungen Ring (geschätzt) | offen |
| `data/brakes.ini`, `electronics.ini` | Basis-Mod | offen |

Abstimmungsziel: Bei Höchstgeschwindigkeit soll die Bodenfreiheit hinten knapp über der Abrisshöhe liegen (siehe `tools/out/venturi_model.png`), damit Bodenwellen und Kuppen das Auto kurz in den Abriss schicken. Das ist der historische Charakter, siehe Bellofs Überschlag an der Kuppe im Rennen 1983.
