# Projektkontext für Claude

Sammlung eigener Assetto-Corsa-Mods. Sprache mit dem Nutzer: Deutsch. Oberste Ordner sind Mod-Kategorien, darunter die einzelnen Mods, jede mit README (Ziel, Installation, Status).

## Umgebung des Nutzers

- Assetto Corsa: `E:\SteamLibrary\steamapps\common\assettocorsa`
- CSP: 0.3.0-preview140 laut Log (Alternative 0.2.11 installiert). Lua-SDK lokal unter `extension\internal\lua-sdk`
- Content Manager wird für alles genutzt, die CM-Saisons und die AC-Karriere nicht (gelten als unbrauchbar)
- Fahrzeuge: `content\cars\`, zum Beispiel `vac_groupc_956` (Porsche 956), `cim_2008_bmw_sauber` (Testauto für Ausfall-Script)
- F1-Jahre vorhanden: 88, 93, 94, 96 bis 04, 06 bis 14, 17 bis 21, 23 bis 25. Am liebsten 06 bis 14
- Bei Arbeit in einer lokalen Sitzung: Dateien aus dem Spielordner dürfen ins Repo kopiert werden, aber keine `.kn5`, `.acd`, Texturen (`.dds`, große `.png`). `preview.jpg` und `ui_skin.json` sind erwünscht

## Stand der Mods

| Mod | Stand | Nächster Schritt |
|---|---|---|
| `AI Mods/01-fast-lane-recorder` | Python-Paket, Lua-Aufnahme-App, Build-Skripte, Test mit synthetischer Strecke grün | Original `content\tracks\monza\ai\fast_lane.ai` parsen, App im Spiel testen, Runden aufnehmen, erste echte Linie bauen |
| `AI Mods/02` bis `06` | nur README | nach 01 |
| `Car Mods/porsche_956` | Fertig. Release-Auto `content\cars\porsche_956_groupc_bellof` ("Porsche 956 Group C Stefan Bellof", Rothmans Nr. 2), gebaut mit `py -3.11 install.py --release`. Aero-Map, Fahrwerk, Reifenmaße 1983, Motor 935/76 (Quali 710 PS), 895 kg; 10 Messungen in `tools/out/messungen/`, 310 km/h, 2450 kg Abtrieb | keiner; bei Bedarf Reifenverschleiß 1983 oder eigener Skin |
| `Car Mods/f2004_drs_kers` | Gebaut: `content\carserrari_f2004_drs_kers` ("Ferrari F2004 DRS KERS") mit `py -3.11 tools/build.py` aus ks_ferrari_f2004 und rss_formula_hybrid_2018. DRS als geteilter Heckflügel (Klappe 45 %, EFFECT 0) mit abgetrennter, animierter Klappe im kn5 (`tools/make_flap.py`), KERS 60 kW / 400 kJ, RSS-2018-Reifen mit Grip x1,20 (GRIP_SCALE, Slick gegen Rillen), Physik als data.acd (offener data-Ordner: AC lud drs.ini nicht). Nur eigene Dateien im Repo | im Spiel prüfen: Log `LOADING DRS`, Klappe öffnet, Drehrichtung; dann Topspeed mit/ohne DRS, KERS |
| `Gameplay Mods/mechanical-failures` | App `app/reliability` (physics-API, alle Autos, keine data.acd-Änderung) gebaut und installiert; Auto-Script-Weg im BMW bestätigt, BMW wieder original | App im Spiel testen, Stärke und Abtriebsanteil abstimmen, Ausfälle mit Rate x20 prüfen |
| `Career Mods/career-system` | Excel-Importer für die 2017er Datei | zurückgestellt, bis die restlichen Excels vorliegen |

## Konventionen

- Python 3.11 oder neuer, numpy und matplotlib. Skripte werden aus dem Mod-Ordner heraus aufgerufen
- Jede Änderung an Spieldateien: Original vorher als `.bak` sichern, nie `data.acd` überschreiben
- Werte, die geschätzt sind, als Schätzung kennzeichnen; Quellen in `research/` der jeweiligen Mod
- Commits auf `main`, deutsche Commit-Nachrichten
- Keine Lizenz-Dateien von Kunos oder fremden Mods einchecken (siehe `.gitignore`)

## Geklärt gegen das lokale lua-sdk (ac_car_cphys)

- Laufende CSP-Version laut Log: 0.3.0-preview140 (Build 3676), nicht preview649. Vor API-Fragen das Log prüfen
- AC lädt `data.acd`; ein entpackter `data`-Ordner daneben wird ignoriert. Auto-Scripts brauchen deshalb den ACD-Packer aus `Tools/acd`, die App `app/reliability` braucht gar keine Auto-Änderung
- `ac.accessCarPhysics()`: `wheels[i].inflation` (nur lesen, setzen mit `ac.setTyreInflation`), `waterTemperature`, `engineLifeLeft` (nur lesen, setzen mit `ac.setEngineLifeLeft`), kein Getriebeschaden-Feld, keine Bodenfreiheit (die liegt in `ac.getCar(i).rideHeight`)
- Flügel-Gain: `ac.setWingGain(wingIndex, cdGain, clGain)`
- Andere Autos aus dem Physik-Script: `ac.getCar(i)` erlaubt, Daten aus dem Grafik-Thread, mit Tiefpass nutzbar
- `ac.INIConfig.carData(car.index, 'failures.ini')` funktioniert, Abschnitte über `.sections[name]`, Skin über `car:skin()`
- Nicht vorhanden: `SteerRatio` als Physikwert, schreibbarer Getriebeschaden
