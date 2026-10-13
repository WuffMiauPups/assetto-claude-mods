# CSP Extended Physics: Werkzeuge für den Ground-Effect (Recherchestand 2026-10-13)

Quellen: CSP-Wiki (acc-extension-config), Lua-SDK (acc-lua-sdk), Beispiele (acc-lua-examples). Kopien der Wiki-Seiten liegen neben dieser Datei.

## Kernerkenntnis

CSP kann ride-height-abhängige Aerodynamik direkt über `aero.ini` abbilden, ohne Lua. Der Mechanismus heißt Aero Map (`[MAP_N]`). Damit lässt sich der Venturi-Effekt des 956 als Kennfeld modellieren: Abtrieb, Widerstand und Balance als Funktion der Bodenfreiheit vorn und hinten, zusätzlich Multiplikatoren über Geschwindigkeit, Gier-, Roll- und Lenkwinkel.

## Aktivierung

```ini
[HEADER]
VERSION=extended-2
```

Optional Versionssperre mit `[_EXTENSION] REQUIRED_VERSION=<CSP-Versionscode>`. Mindestens ein `[WING_N]` muss in `aero.ini` bleiben, sonst lädt AC das Auto nicht.

## Aero Map `[MAP_N]`

| Schlüssel | Bedeutung |
|---|---|
| `MAP_CL_RH` | 2D-LUT: Cl·A über Bodenfreiheit vorn (x) und hinten (y) in Metern |
| `MAP_CD_RH` | 2D-LUT: Cd·A über Bodenfreiheit |
| `MAP_BALANCE_RH` | 2D-LUT: Anteil vorn (0 bis 1) über Bodenfreiheit |
| `MAP_SPEED_CL`, `MAP_SPEED_CD`, `MAP_SPEED_BALANCE` | LUT über km/h, Multiplikator bzw. Addition |
| `MAP_YAW_*`, `MAP_ROLL_*`, `MAP_STEER_*` | LUT über Grad, Multiplikator bzw. Addition |
| `FRONT_RH_OFFSET`, `REAR_RH_OFFSET` | statischer Versatz auf den LUT-Eingang in m |
| `CL_MULT`, `CD_MULT`, `BALANCE_OFFSET` | globale Skalierung |
| `INTERPOLATION` | `LINEAR` oder `CUBIC` |
| `DRAG_OFFSET` | Angriffspunkt des Widerstands, seitlich und Höhe in m |
| `FRONT_FORCE_DELAY`, `REAR_FORCE_DELAY`, `DRAG_FORCE_DELAY` | Verzögerung der Kräfte, höher heißt weniger Lag |

2D-LUT-Format: erste Zeile x-Werte (vorn), erste Spalte y-Werte (hinten), Tab- oder Leerzeichen-getrennt, aufsteigend. Zusätzlich `[FAN_N]` für Lüfterautos und `[AEROMAP]` in `setup.ini`, um im Setup zwischen Maps umzuschalten (Kurzheck, Langheck, Ring-Qualitrimm).

Die Kraftverzögerung ist wichtig für den 956: Mit kleinen Werten lässt sich das Aufschaukeln (Porpoising) nachbilden, mit größeren Werten ein ruhigeres Auto.

## Was damit geht und was nicht

Geht über Aero Map:
- Steiler Abtriebsanstieg bei sinkendem Heck, Einbruch beim Anheben
- Strömungsabriss bei zu geringer Bodenfreiheit (Kennfeld fällt unterhalb der Abrisshöhe ab)
- Balancewanderung mit Nickwinkel (vorn tief, hinten hoch: Balance nach vorn)
- Abtriebsverlust bei Gierwinkel (Tunnel verlieren Anströmung im Drift)
- Verschiedene Trimms per Setup

Geht nur mit Lua `script.lua`:
- Hysterese beim Wiederanlegen der Strömung nach Abriss
- Zeitabhängige Effekte, Beschädigung des Unterbodens, Reaktion auf Kerbs
- Beliebige Zusatzkräfte über `ac.addForce(pos, posLocal, force, forceLocal)`
- Flügel-Gain zur Laufzeit (Feature seit 0.1.78, Funktionsname in den gelesenen Quellen nicht dokumentiert)

Plan: zuerst alles über Aero Map, Lua nur falls das Fahrgefühl den Abriss mit Hysterese braucht.

## Lua-Physik-Script, verifizierte API

- Datei `script.lua` im `data`-Ordner, Extended Physics muss aktiv sein, bei entpackten Daten Live-Reload.
- `script.update(dt)` jeden Physikschritt (dt etwa 0,003 s), `script.reset()` bei Teleport oder neuer Session.
- `ac.accessCarPhysics()` liefert beschreibbaren Zustand: `rpm`, `gas`, `brake`, `turboBoost` (ab 0.3.0-preview445), `gForces`, `requestedGearIndex`, `engineLifeLeft`, `controllerInputs[0..7]`, Rad-Felder (ab 0.3.0-preview440 unter anderem `pressureDynamic`, `surfaceGrip`).
- `ac.addForce(vec3 pos, bool posLocal, vec3 force, bool forceLocal)`, Reihenfolge aus Wiki-Beispiel abgeleitet.
- `ac.overrideEngineTorque(nm)`, `ac.overrideGasInput(v)`, `ac.DataLUT11.carData(car.index, 'datei.lut')`.
- `ac.getSetupValue(id)`, eigene Setup-Elemente über `[CUSTOM_SCRIPT_ITEM_N]` in `setup.ini`.
- `ac.setPhysicsValue(ac.CarPhysicsValueID.X, wert)` für Bremsmoment, Bremsbalance, TC, Lenkübersetzung und mehr (Enum im SDK, Datei `ac_car_cphys_enums.lua`).
- Dämpfer lesbar und schreibbar (`state_cphys_damper`), Oberfläche lesbar (`state_cphys_surface`).

Nicht gefunden: Feldname für Bodenfreiheit im Physik-Script. Instrument-Inputs kennen `RIDE_HEIGHT` (vier Werte in Metern), für das Script ist der Zugriff noch zu verifizieren. Die vollständige generierte API liegt lokal in `extension/internal/lua-sdk` der installierten CSP-Version, das ist auf dem Rechner des Nutzers zu prüfen.

## Dynamische Controller (auch ohne CSP)

`aero.ini` kennt `[DYNAMIC_CONTROLLER_N]` mit `WING`, `COMBINATOR=ADD|MULT`, `INPUT` (Geschwindigkeit, Bremse, Gas, Lenkung, Quer-G, bei CSP auch `HEADLIGHTS`), `LUT`, `FILTER`, `UP_LIMIT`, `DOWN_LIMIT`. Relevant für das spätere F2004-Projekt mit aktiver Aero.

## Weiteres Vorgehen für den 956

1. Python-Modell des Venturi-Unterbodens: Abtrieb und Balance über Bodenfreiheit vorn und hinten, kalibriert auf die Schätzwerte (Kurzheck grob 1500 bis 2000 kg bei 320 km/h, Langheck etwa 1050 kg, Widerstand etwa 380 kg bei 320 km/h Langheck).
2. Daraus die drei 2D-LUTs und die Speed- und Yaw-LUTs erzeugen.
3. `aero.ini` mit einer Map je Trimm, `setup.ini` mit `[AEROMAP]`.
4. Fahrwerk so abstimmen, dass die Bodenfreiheit bei Höchstgeschwindigkeit in den steilen Bereich des Kennfelds läuft, aber über der Abrisshöhe bleibt. Progressive Federn wie im Original.
5. Test im Spiel, Vergleich der Kurvengeschwindigkeiten mit historischen Angaben (Ring 6:11, Schnitt 202 km/h).
