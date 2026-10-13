# F1: Ausfälle, Degradation, Dirty Air. Vollständige Liste und Machbarkeit

Stand 2026-10-13. Machbarkeit bezieht sich auf CSP Extended Physics mit `script.lua`, verifizierte API siehe `Car Mods/porsche_956/research/02-csp-technik.md`.

## A. Totalausfälle

| Defekt | Ursache | Effekt im Spiel | Umsetzung | Status |
|---|---|---|---|---|
| Verbrennungsmotor | Kolben, Pleuel, Ventil, Öldruck | Leistungsverlust, Aussetzer, Stillstand, Rauch | `overrideEngineTorque`, `gas=0`, `engineLifeLeft=0` | API bekannt |
| Turbolader | Welle, Lager | Ladedruck weg, Leistung 50 Prozent, später Rauch | `overrideGasInput`, `overrideEngineTorque` | API bekannt |
| MGU-K | Elektrik, Hitze | minus 160 PS, keine Rekuperation | Drehmomentabzug, ERS-Werte über `CarPhysicsValueID.ERSRecovery` | API bekannt |
| MGU-H | Lager, Hitze | Turboloch, träger Ladedruck | Gasbegrenzung abhängig von Drehzahl | API bekannt |
| Energiespeicher, Steuerelektronik | Zellschaden, Software | Hybrid aus, später Totalausfall | Drehmomentabzug, dann `engineLifeLeft=0` | API bekannt |
| Getriebe | Schaltmechanik | Gang fällt aus, Schaltverzögerung, Blockade | `requestedGearIndex`, Gearbox damage | Feldname Schaden prüfen |
| Hydraulik | Druckverlust | Lenkung schwer, Schalten träge, DRS aus, Kupplung weg | `SteerRatio`, Schaltlogik, Flügel-Gain | API teils bekannt |
| Kühlung, Leck | Leck, Debris | Temperaturen steigen, Drosseln nötig, dann Motor | Temperaturfeld beschreibbar? | prüfen |
| Kraftstoffsystem | Druck, Pumpe | Stottern, Stillstand | `gas` intervallweise 0, dann `engineLifeLeft=0` | API bekannt |
| Elektrik, Sensoren | Kabel, Sensor | Zündaussetzer, Totalausfall | `gas=0` in Intervallen | API bekannt |
| Bremsen | Scheibe, Brake-by-Wire | Bremsleistung sinkt, Balance springt | `BrakeTorque`, `BrakeFrontBias` | API bekannt (0.3.0-preview398) |
| Aufhängung | Kerb, Kontakt | Auto zieht, Ausfall | Lenkoffset über Steuerung, Dämpfer-Struct | teils |
| Antriebswelle, Radlager | Verschleiß | Vibration, Ausfall | Vibration zu prüfen, Ausfall über Drehmoment 0 | teils |
| Reifenschaden | Debris, Schnitt | Druckverlust, Platzer | Tyre inflation | Feldname prüfen |
| Radmutter nach Stopp | Boxenfehler | sofortiger Ausfall nach Stopp | nach Boxenstopp würfeln, Reifen 0 | API bekannt |
| DRS klemmt | Aktuator | offen: Abtriebsverlust hinten, zu: Topspeed fehlt | Flügel-Gain | Funktionsname prüfen |

## B. Schleichende Verluste

| Verlust | Mechanismus | Umsetzung | Status |
|---|---|---|---|
| Motorverschleiß | Laufleistung über Wochenenden, 1 bis 3 Prozent pro Rennen | Drehmomentfaktor aus `failures.ini` | API bekannt |
| Turbo- und Hybridverschleiß | Ladedruck, Rekuperation lassen nach | Gas- und ERS-Faktoren | API bekannt |
| Hitze-Derating | Motor oder ERS zu heiß, abhängig von Verkehr und Lufttemperatur | Drehmomentfaktor aus Temperaturmodell | Temperaturquelle prüfen |
| Motormodi | Quali-Modus mit Extraleistung und mehr Verschleiß, Sparmodus | Extra-Schalter, Drehmomentfaktor, Verschleißzähler | API bekannt |
| Getriebeverschleiß | Schaltzeiten länger | Schaltlogik | API bekannt |
| Bremsverschleiß, Fading | Bremsmoment sinkt mit Hitze und Distanz | `BrakeTorque` | API bekannt |
| Unterboden-, Plankenschaden | Kerbs, Aufsetzer kosten Abtrieb dauerhaft | Flügel-Gain, Aufsetzer über Bodenfreiheit erkennen | Funktionsname prüfen |
| Frontflügelschaden | AC hat Kontaktmodell, zu grob | Verfeinerung über Flügel-Gain | später |
| Debris im Bremsschacht, Kühler | Temperaturen steigen bis Stopp | Temperaturmodell | prüfen |
| Flatspot-Vibration | vorhanden in AC | nichts nötig | vorhanden |

## C. Dirty Air und Windschatten

AC: Windschatten reduziert Widerstand. Fehlend: Abtriebsverlust im Nachlauf, Untersteuern, Reifen- und Kühltemperaturen im Verkehr.

Modell:
1. Für jedes Auto die Vordermänner innerhalb 60 m suchen (`ac.getCar(i)`, Position, Geschwindigkeit, Richtung).
2. Nachlauf als Kegel hinter dem Vordermann: Breite wächst mit Abstand, Stärke fällt mit Abstand und seitlichem Versatz.
3. Verlust: Abtrieb vorn bis 35 Prozent, hinten bis 15 Prozent, Widerstand minus 10 bis 20 Prozent (Windschatten).
4. Flügel-Gain setzen (vorn und hinten getrennt), alternativ `ac.addForce` nach oben an der Vorderachse.
5. Reifentemperatur vorn im Verkehr erhöhen (Feld prüfen), Kühlung verschlechtern (Temperaturmodell).
6. Ära-Parameter: 2017 bis 2021 stark, 2022 schwächer, 1983 moderat, 2004 stark.

## D. Nicht sinnvoll im Spiel

- Echte Strömungssimulation: Kegelmodell reicht.
- Funk- und Boxenfehler, falsche Reifenwahl: Ereignisse im Karriere-System, nicht in der Physik.
- Sichtbarer Rauch an KI-Autos: zweites Lua-Script, Kosmetik, später.

## Offene Prüfungen gegen das lokale lua-sdk

- Beschreibbare Temperaturen (Wasser, Öl, ERS, Bremsen, Reifen)
- Feldname Reifendruck und Getriebeschaden in `accessCarPhysics()`
- Funktionsname für Flügel-Gain (Feature seit 0.1.78)
- Zugriff auf andere Autos aus dem Physik-Script (`ac.getCar(i)` im Physik-Thread)
