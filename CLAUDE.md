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
| `Gameplay Mods/mechanical-failures` | Ausfallquoten pro Saison aus F1DB, Profile 1988 bis 2025, Dirty-Air-Kennlinien, zwei Lua-Entwürfe | API-Namen gegen lokales lua-sdk prüfen, Script in `cim_2008_bmw_sauber` installieren und testen |
| `Career Mods/career-system` | Excel-Importer für die 2017er Datei | zurückgestellt, bis die restlichen Excels vorliegen |

## Konventionen

- Python 3.11 oder neuer, numpy und matplotlib. Skripte werden aus dem Mod-Ordner heraus aufgerufen
- Jede Änderung an Spieldateien: Original vorher als `.bak` sichern, nie `data.acd` überschreiben
- Werte, die geschätzt sind, als Schätzung kennzeichnen; Quellen in `research/` der jeweiligen Mod
- Commits auf `main`, deutsche Commit-Nachrichten
- Keine Lizenz-Dateien von Kunos oder fremden Mods einchecken (siehe `.gitignore`)

## Offene Prüfpunkte gegen das lokale lua-sdk

- Felder in `ac.accessCarPhysics()`: Reifendruck, Getriebeschaden, Temperaturen (Wasser, Öl, Bremsen, Reifen), Bodenfreiheit
- Funktionsname für Flügel-Gain (Feature seit CSP 0.1.78)
- Zugriff auf andere Autos aus dem Physik-Script (`ac.getCar(i)` im Physik-Thread) für Dirty Air
- `ac.INIConfig.carData` zum Lesen von `failures.ini`
