# Zuverlässigkeit, Degradation und Dirty Air

Assetto Corsa kennt Unfallschäden, aber keine zufälligen Defekte, keinen Verschleiß über Wochenenden und keinen Abtriebsverlust im Verkehr. Diese Mod rüstet alle drei nach, mit Fokus auf F1. Vollständige Liste aller Defekte, Verluste und des Dirty-Air-Modells mit Machbarkeit: `research/f1-ausfaelle-degradation-dirty-air.md`.

## Technik

CSP Extended Physics. `failures.lua` liegt als Modul im Datenordner des Autos und wird aus `script.lua` aufgerufen; hat das Auto bereits ein eigenes Script (der BMW Sauber 2008 hat eines für Bremsmigration und Differenzial), hängt der Installer nur einen Hook an. Das Script läuft für jede Instanz des Autos, also Spieler und KI. Pro Physikschritt wird gegen eine Rate gewürfelt; tritt ein Defekt ein, wird er über die gegen das lokale lua-sdk (0.3.0-preview649) geprüfte API ausgelöst:

| Defekt | Auslösung | API (geprüft) |
|---|---|---|
| Motorschaden total | Drehmoment sinkt, Aussetzer, dann Motor aus | `ac.overrideEngineTorque` mit `power.lut`, `ac.setEngineLifeLeft(0)` |
| Leistungsverlust (Zylinder, Zündung) | Drehmoment auf 70 bis 85 Prozent | `ac.overrideEngineTorque` |
| Turbo | Ladedruck auf 55 Prozent, Saugmotor: Gas begrenzt | `ac.overrideTurboBoost`, sonst `ac.overrideGasInput` |
| Getriebe | ein Gang fällt aus, nach zwei Minuten nur noch Neutral | `requestedGearIndex`, `ac.setGearsGrinding` |
| Hydraulik, Servo | Lenkeingabe gedämpft (kein Lenkübersetzungs-Zugriff im SDK) | `carPhysics.steer` |
| Elektrik | Zündaussetzer, am Ende Motor aus | `gas = 0` in Intervallen, `ac.setEngineLifeLeft(0)` |
| Bremsen | Bremsmoment sinkt, Balance wandert nach vorn | `ac.overrideBrakesTorque`, `ac.setBrakeBias` |
| Reifenschaden | schleichender Druckverlust, dann Platzer | `ac.setTyreInflation(rad, 0)` |
| Aufhängung | ein Dämpfer verliert seine Wirkung | `ac.accessCarDamper` |
| Kühlung | Wasser 18 Grad pro Minute wärmer, nach drei Minuten Motor aus | `ac.setWaterTemperature` |

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

- Jedes betroffene Auto braucht einen entpackten Datenordner mit `VERSION=extended-N` in `car.ini`. Content Manager: Auto auswählen, „Unpack data“. `tools/install.py` erledigt das Einfügen von Script und INI für alle Autos einer Serie, mit `--uninstall` auch den Rückbau.
- Nur offline oder auf eigenen Servern; fremde Server mit Prüfsummen lehnen geänderte Autos ab.
- Nicht im SDK vorhanden: Lenkübersetzung als Physikwert und ein schreibbarer Getriebeschaden. Ersatz: gedämpfte Lenkeingabe und erzwungener Leerlauf.
- `ac.overrideBrakesTorque` schaltet die Originalbremse für den Rest der Session ab; deshalb wird sie erst beim Bremsdefekt gerufen und danach jeden Schritt für alle vier Räder gesetzt.

## Struktur

```
mechanical-failures/
  script/      failures.lua (Modul), script.lua (Loader für Autos ohne Script), hook.lua (Anhang für Autos mit Script),
               dirty_air.lua (Modul, noch ohne Kennlinie), failures.ini (Vorlage)
  profiles/    Grundraten pro Ära
  tools/       install.py, failure_stats.py (Quoten aus F1DB), dirty_air_model.py
  research/    Vollständige Liste der Defekte, Dirty-Air-Modell, Ausfallstatistiken der Saisons
```

## Test im Spiel

```
cd tools
python install.py --ac "E:/SteamLibrary/steamapps/common/assettocorsa" --cars cim_2008_bmw_sauber --profile ../profiles/failures_2008.ini --test ENGINE:20
```

`--test ART:SEKUNDEN` schreibt einen Abschnitt `[TEST]` in die `failures.ini`, der den Defekt fest nach der angegebenen Zeit auslöst. Arten: ENGINE, POWER_LOSS, TURBO, GEARBOX, HYDRAULICS, ELECTRICS, BRAKES, PUNCTURE, SUSPENSION, COOLING. Ohne `--test` gelten nur die Raten des Profils. Prüfen im Spiel: Nachricht „Defekt: …“ oben, Zeile `[failures]` im CSP-Log (`Documents\Assetto Corsa\logs\custom_shaders_patch.log`), Wert `failures active` in der CSP-Debug-App.

## Status

Ausfallquoten pro Saison berechnet, Dirty-Air-Kennlinien erzeugt. API gegen lua-sdk 0.3.0-preview649 geprüft, `failures.lua` darauf umgebaut. Installiert im BMW Sauber 2008 (`cim_2008_bmw_sauber`, Datenordner aus `reference/` entpackt, Profil 2008, Testdefekt ENGINE nach 20 s). Erster Lauf im Spiel steht aus. Dirty Air wartet noch auf die Kennlinie als `dirty_air.ini`.
