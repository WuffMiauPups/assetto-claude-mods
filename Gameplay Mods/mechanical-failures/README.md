# Zuverlässigkeit, Degradation und Dirty Air

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

## Dirty Air

Abtriebsverlust im Nachlauf pro Ära, aus FIA-CFD-Werten für 2019 bis 2026 und Schätzungen für ältere Jahre: `research/dirty-air.md`, Modell `tools/dirty_air_model.py`, Lua-Entwurf `script/dirty_air.lua`.

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

Ausfallquoten pro Saison berechnet, Dirty-Air-Kennlinien erzeugt, zwei Script-Entwürfe. Erster Test: BMW Sauber 2008 (`cim_2008_bmw_sauber`) mit CSP 0.3.0-preview649, sobald lua-sdk und Datenordner im Repo liegen.
