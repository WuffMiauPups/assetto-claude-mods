# Projektkontext für Claude

Sammlung eigener Assetto-Corsa-Mods. Sprache mit dem Nutzer: Deutsch. Oberste Ordner sind Mod-Kategorien, darunter die einzelnen Mods, jede mit README (Ziel, Installation, Status).

## Umgebung des Nutzers

- Assetto Corsa: `E:\SteamLibrary\steamapps\common\assettocorsa`
- CSP: 0.3.0-preview649 (Alternative 0.2.11 installiert). Lua-SDK lokal unter `extension\internal\lua-sdk`
- Content Manager wird für alles genutzt, die CM-Saisons und die AC-Karriere nicht (gelten als unbrauchbar)
- Fahrzeuge: `content\cars\`, zum Beispiel `vac_groupc_956` (Porsche 956), `cim_2008_bmw_sauber` (Testauto für Ausfall-Script)
- F1-Jahre vorhanden: 88, 93, 94, 96 bis 04, 06 bis 14, 17 bis 21, 23 bis 25. Am liebsten 06 bis 14
- Bei Arbeit in einer lokalen Sitzung: Dateien aus dem Spielordner dürfen ins Repo kopiert werden, aber keine `.kn5`, `.acd`, Texturen (`.dds`, große `.png`). `preview.jpg` und `ui_skin.json` sind erwünscht

## Stand der Mods

| Mod | Stand | Nächster Schritt |
|---|---|---|
| `AI Mods/01-fast-lane-recorder` | Python-Paket, Lua-Aufnahme-App, Build-Skripte, Test mit synthetischer Strecke grün | Original `content\tracks\monza\ai\fast_lane.ai` parsen, App im Spiel testen, Runden aufnehmen, erste echte Linie bauen |
| `AI Mods/02` bis `06` | nur README | nach 01 |
| `Car Mods/porsche_956` | Recherche, Venturi-Modell (`tools/venturi_model.py`), CSP-Aero-Map-Kennfelder erzeugt | `data`-Ordner von `vac_groupc_956` als Basis übernehmen, `aero.ini` mit `[MAP_0]`, Fahrwerk und Motor abstimmen |
| `Gameplay Mods/mechanical-failures` | API gegen lua-sdk geprüft, `failures.lua` + `dirty_air.lua` als Module, im BMW Sauber 2008 installiert (Hook an dessen eigenes script.lua) | Test im Spiel: CSP-Debug `dirty air front/rear`, Log `[dirty_air]`/`[failures]` |
| `Career Mods/career-system` | Excel-Importer für die 2017er Datei | zurückgestellt, bis die restlichen Excels vorliegen |

## Konventionen

- Python 3.11 oder neuer, numpy und matplotlib. Skripte werden aus dem Mod-Ordner heraus aufgerufen
- Jede Änderung an Spieldateien: Original vorher als `.bak` sichern, nie `data.acd` überschreiben
- Werte, die geschätzt sind, als Schätzung kennzeichnen; Quellen in `research/` der jeweiligen Mod
- Commits auf `main`, deutsche Commit-Nachrichten
- Keine Lizenz-Dateien von Kunos oder fremden Mods einchecken (siehe `.gitignore`)

## Offene Prüfpunkte gegen das lokale lua-sdk

Geklärt (lua-sdk liegt unter `Tools/csp-reference/lua-sdk`, Physik-API in `ac_car_cphys/lib.lua`):
- Flügel-Gain: `ac.setWingGain(wingIndex, cdGain, clGain)`
- Andere Autos im Physik-Script: `ac.getCar(i)` liefert `ac.StateCar` (position, look, isActive, isInPitlane), `sim.carsCount`
- INI im Datenordner: `ac.INIConfig.carData(car.index, 'failures.ini')`; Dateien lesen: `io.load(ac.getFolder(ac.FolderID.ScriptOrigin) .. '/x')`
- Reifendruck: `ac.setTyreInflation(ac.Wheel.*, 0..1)`; Motor: `ac.setEngineLifeLeft(0)`; Skin: `ac.getCarSkinID(car.index)`
Noch offen:
- Getriebeschaden: `gearboxDamage` in `ac.StateCarPhysics` ist nur lesbar, kein Setter gefunden
- Ob `require('failures')` aus einem Physik-Script im `data`-Ordner funktioniert (erst im Spiel prüfbar)
- Ob AC bei vorhandenem `data`-Ordner und `data.acd` den Ordner nimmt (Annahme ja; BMW Sauber hat jetzt beides)
