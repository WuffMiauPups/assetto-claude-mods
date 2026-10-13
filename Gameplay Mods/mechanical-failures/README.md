# Mechanische Ausfälle

Assetto Corsa kennt Unfallschäden, aber keine zufälligen Defekte. Diese Mod rüstet sie nach: Motor, Getriebe, Turbo, Hydraulik, Elektrik, Bremsen, Reifen. Raten pro Ära, pro Bauteil und pro Fahrer, mit Laufleistung über Rennwochenenden.

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

## Profile pro Ära

`profiles/` enthält Grundraten je Epoche, abgeleitet aus realen Ausfallquoten der Saisons:

| Ära | Ausfallquote real (technisch, pro Auto und Rennen) | Schwerpunkte |
|---|---|---|
| 1983 Gruppe C, Turbo | hoch, 20 bis 30 Prozent über Langstrecke | Motor, Turbo, Getriebe |
| 2004 V10 | mittel, 10 bis 15 Prozent | Motor, Hydraulik |
| 2017 Hybrid | niedrig bis mittel, 8 bis 12 Prozent, Honda deutlich höher | ERS, Elektrik, Turbo |
| 2025 | niedrig, unter 8 Prozent | Elektrik, Hydraulik |

Die Werte werden noch gegen die Statistik der jeweiligen Saisons geprüft (Quellen folgen in `research/`).

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
  tools/       install.py: Script und INI in die Datenordner einer Serie kopieren
  research/    Ausfallstatistiken der Saisons
```

## Status

Konzept und Script-Entwurf. Erster Test braucht einen entpackten Auto-Datenordner und die CSP-Version.
