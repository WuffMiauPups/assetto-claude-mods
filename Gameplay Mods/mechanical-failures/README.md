# Zuverlässigkeit, Degradation und Dirty Air

## Zwei Wege

| | App `app/reliability` (empfohlen) | Auto-Script `script/` |
|---|---|---|
| Gilt für | alle Autos im Feld, jede Ära, einmal installieren | nur Autos, in denen es installiert ist |
| Eingriff ins Auto | keiner, `data.acd` bleibt original | `data.acd` wird neu gepackt (Checksum ändert sich) |
| Dirty Air | Grip vorn/hinten reduzieren (Runde gültig) oder Luftdichte (Runde ungültig) | Gain pro Flügel, feiner |
| Ausfälle | Motor, Leistungsverlust, Turbo, Getriebe, Hydraulik, Elektrik, Kühlung, Reifen, Aufhängung | zusätzlich Bremsen |
| Online | nein, nur offline | ja, wenn Checksum erlaubt |
| Installation | `python tools/install_app.py --ac <AC>` | `python tools/install.py ... --pack` |

Grundlage für den App-Weg ist die `physics.*`-API in `lua-sdk/ac_apps`, die pro Auto-Index Grip, Luftdichte, Motorleben, Restriktor, Reifen und Aufhängung setzen kann (RARE nutzt dieselbe API). Die Saison kommt aus dem Baujahr des Autos (`ac.getCar(i).year`) oder wird im App-Fenster gesetzt, daraus folgen Dirty-Air-Kennlinie und Ausfallprofil.

Assetto Corsa kennt Unfallschäden, aber keine zufälligen Defekte, keinen Verschleiß über Wochenenden und keinen Abtriebsverlust im Verkehr. Diese Mod rüstet alle drei nach, mit Fokus auf F1. Vollständige Liste aller Defekte, Verluste und des Dirty-Air-Modells mit Machbarkeit: `research/f1-ausfaelle-degradation-dirty-air.md`.

## Technik

CSP Extended Physics, `script.lua` im Datenordner des Autos. Das Script läuft für jede Instanz des Autos, also Spieler und KI. Pro Physikschritt wird gegen eine Rate gewürfelt; tritt ein Defekt ein, wird er über die verifizierte CSP-API ausgelöst:

| Defekt | Auslösung | API |
|---|---|---|
| Motorschaden total | Motor stirbt, Rauch über Schadenswert | `engineLifeLeft = 0` |
| Leistungsverlust (Zylinder, Zündung) | Drehmoment auf 70 bis 85 Prozent | `ac.overrideEngineTorque` |
| Turbo | Gas begrenzt, Drehmoment reduziert | `ac.overrideGasInput`, `ac.overrideEngineTorque` |
| Getriebe | ein Gang fällt aus oder Schaltverzögerung | `requestedGearIndex`, Gearbox damage |
| Hydraulik, Servo | Lenkübersetzung verschlechtert | `ac.setPhysicsValue(SteerRatio)` (0.3.0-preview366 oder neuer) |
| Elektrik | Zündaussetzer, kurze Gasunterbrechungen, am Ende Stillstand | `gas = 0` in Intervallen |
| Bremsen | Bremsmoment sinkt, Balance wandert | `BrakeTorque`, `BrakeFrontBias` (0.3.0-preview398 oder neuer) |
| Reifenschaden | Druckverlust, Platzer | Tyre inflation (Feldname gegen das lokale `lua-sdk` prüfen) |

Defekte entwickeln sich: Erst ein Warnsignal (Temperatur, kurzer Aussetzer), dann Verschlechterung, dann Ausfall. Das gibt dir die Chance, das Auto zu schonen, wie 1983 oder 2017 real.

## Konfiguration

`failures.ini` im Datenordner des Autos, wird vom Karriere-System vor jedem Wochenende geschrieben, kann aber auch von Hand gepflegt werden:

```ini
[GLOBAL]
SEED=2017-13            ; pro Wochenende fest, damit Replays und Neustarts reproduzierbar sind
RACE_LENGTH_MIN=90      ; Bezugsgröße: Raten gelten pro Rennen dieser Länge
MULT_ALL=1.0

[ERA]                   ; Grundraten pro Rennen in Prozent, Ära 2017
ENGINE=4
POWER_LOSS=6
TURBO=2
GEARBOX=3
HYDRAULICS=2
ELECTRICS=3
BRAKES=1
PUNCTURE=5

[DRIVER_mclaren_honda_sabanov]   ; Skin-Name, überschreibt oder multipliziert
ENGINE_MULT=5.0
TURBO_MULT=3.0
ENGINE_MILEAGE_KM=1450           ; Laufleistung, erhöht die Rate progressiv
BALLAST_KG=0
RESTRICTOR=0
```

Fahrerzuordnung über den Skin-Namen, weil KI-Fahrer im selben Auto nur so unterscheidbar sind. Ballast und Restriktor werden hier nur protokolliert; die Werte selbst setzt Content Manager über die Entry-Liste.

## Profile pro Saison

`profiles/failures_<jahr>.ini` für 1988 bis 2025, berechnet aus allen Rennergebnissen der Saison (F1DB). Details, Tabelle und Fahrer-Multiplikatoren: `research/ausfallstatistik.md`. Die Gruppe-C-Profile für den 956 folgen aus der WEC-Statistik.

GP2 2005 und 2006 (`sr_gp2_05`, `sr_gp2_06`): Die App erkennt GP2 an Ordnername, Brand oder Tag und nimmt dann `profiles/failures_gp2_<jahr>.ini` statt des F1-Profils. Grundlage sind 319 Ausfälle aus 44 Rennen (`research/gp2-ausfallstatistik.md`, Rohdaten `research/data/gp2_retirements.json`), erzeugt mit `py -3.11 tools/gp2_profiles.py`. Mechanisch 12,2 % (2005) und 13,1 % (2006) pro Start, Bezug 50 Minuten (Mittel aus Hauptrennen etwa 61 und Sprint etwa 38 Minuten). Häufungen sind auf 3 Ausfälle gleicher Art pro Rennen gedeckelt (Imola 2005 Bremsen, Schätzung). Teamfaktor aus dem Skin-Namen über `gp2_rates.json`, zum Saisonmittel geschrumpft (20 virtuelle Starts, Schätzung): ART und iSport um 0,5, BCN, Campos, DPR, FMS und Trident um 1,4. Dirty Air nutzt die F1-Kennlinie 2005 bis 2008, für GP2 ungeprüft.

## Dirty Air

Abtriebsverlust im Nachlauf pro Ära, aus FIA-CFD-Werten für 2019 bis 2026 und Schätzungen für ältere Jahre: `research/dirty-air.md`, Modell `tools/dirty_air_model.py`, Modul `script/dirty_air.lua`.

Umsetzung (gegen das lokale lua-sdk geprüft): pro Physikschritt wird für jedes andere Auto Abstand entlang seiner Fahrtrichtung und seitlicher Versatz berechnet, der Verlust aus `dirty_air.lut` (Spalten Abstand, gesamt, vorn, hinten) mit einer Gauss-Breite über den Versatz gewichtet, tiefpassgefiltert und per `ac.setWingGain(index, 1, 1 - Verlust)` auf die Flügel gelegt. Die Zuordnung vorn/hinten kommt aus den `NAME`-Einträgen der `aero.ini` (FRONT, REAR, DIFF, MONKEY), kann in `failures.ini` unter `[DIRTY_AIR]` mit `FRONT_WINGS`/`REAR_WINGS` fest vorgegeben werden. `EXCLUDE_WINGS` nimmt Flügel aus, die das Auto in seinem eigenen Script steuert (BMW Sauber 2008: Diffusor 5 und 6, Porpoising-Effekt). Widerstand bleibt unverändert, Windschatten macht AC selbst.

## Kopplung an das Karriere-System

1. Karriere schreibt `failures.ini` für jedes Auto der Serie, mit Laufleistung pro Motor und Fahrer-Multiplikatoren.
2. Nach dem Rennen liest die Karriere die Ergebnisdatei. Ein Ausfall durch das Script wird im Log des Scripts protokolliert und als DNF-Grund übernommen.
3. Motorwechsel über das Kontingent lösen Gridstrafen aus, wie in deinen Vertragsklauseln beschrieben.

## Voraussetzungen und Grenzen

- Jedes betroffene Auto braucht einen entpackten Datenordner mit `VERSION=extended-2` in `car.ini`. Content Manager: Auto auswählen, „Unpack data“. `tools/install.py` erledigt das Einfügen von Script und INI für alle Autos einer Serie.
- Nur offline oder auf eigenen Servern; fremde Server mit Prüfsummen lehnen geänderte Autos ab.
- Die Felder für Reifendruck und das genaue Verhalten von Getriebeschaden sind gegen das lokale `extension/internal/lua-sdk` der installierten CSP-Version zu prüfen.

## Struktur

```
mechanical-failures/
  script/      script.lua (Entwurf) und failures.ini (Vorlage)
  profiles/    Grundraten pro Ära
  tools/       install.py, failure_stats.py (Quoten aus F1DB), dirty_air_model.py
  research/    Vollständige Liste der Defekte, Dirty-Air-Modell, Ausfallstatistiken der Saisons
```

## Status

13.10.2026: App `reliability` gebaut und installiert, noch nicht im Spiel getestet. Auto-Script-Weg im BMW Sauber 2008 getestet und bestätigt (Dirty Air bis 0,63 Verlust vorn, Flügel-Gain), danach wieder auf Original-`data.acd` zurückgesetzt, damit App und Script nicht doppelt wirken. Erkenntnis: AC lädt die `data.acd`, ein entpackter `data`-Ordner daneben wird ignoriert.

Offen: App im Spiel testen (Log `[reliability]`, App-Fenster), Dirty-Air-Stärke und Abtriebsanteil abstimmen, Ausfälle mit Rate x20 einzeln prüfen. Restriktor-Skala (Prozent) und Aufhängungsschaden (70 km/h) sind Schätzwerte.
