# 01 Fast Lane Recorder

Eigene Runden aufnehmen und daraus eine neue `fast_lane.ai` erzeugen, damit die KI deine Linie und dein Tempo fährt.

Startstrecke: **Monza GP** (Kunos, Ordner `content/tracks/monza`).

## Bestandteile

| Pfad | Zweck |
|---|---|
| `app/fastlane_recorder/` | Lua-App für CSP, loggt pro Frame Position, Speed, Pedale, Lenkung in eine CSV |
| `fastlane/` | Python-Paket: Parser und Writer für `fast_lane.ai`, Geometrie, Geschwindigkeitsprofil, Telemetrie |
| `scripts/analyse.py` | Kennzahlen und Diagramm einer AI-Linie |
| `scripts/build.py` | Aus Telemetrie-Logs eine neue AI-Linie bauen |
| `scripts/compare.py` | Zwei AI-Linien vergleichen |
| `tests/test_roundtrip.py` | Format-Roundtrip und komplette Pipeline mit synthetischer Strecke |
| `dist/<track>/` | Fertige Dateien zum Kopieren ins Spiel |

## Ablauf

1. `app/fastlane_recorder` nach `assettocorsa/apps/lua/` kopieren, Spiel starten, App aktivieren.
2. Aufnahme starten, drei bis fünf saubere Runden fahren, stoppen. CSV liegt in `apps/lua/fastlane_recorder/logs/`.
3. CSV nach `AI/data/monza/laps/` legen, Original `content/tracks/monza/ai/fast_lane.ai` nach `AI/data/monza/original/`.
4. Bauen:

```
pip install numpy matplotlib
python scripts/analyse.py ../data/monza/original/fast_lane.ai
python scripts/build.py --laps ../data/monza/laps/*.csv --reference ../data/monza/original/fast_lane.ai --out dist/monza/fast_lane.ai --margin 0.97
python scripts/compare.py ../data/monza/original/fast_lane.ai dist/monza/fast_lane.ai
```

5. `dist/monza/fast_lane.ai` nach `content/tracks/monza/ai/` kopieren. Original vorher sichern.
6. Rennen gegen die KI fahren. Zu langsam: `--margin` erhöhen oder `--lat-g` anheben. Zu schnell oder Abflüge: senken.

## Parameter von build.py

| Option | Standard | Bedeutung |
|---|---|---|
| `--margin` | 0.97 | Skaliert das Speed-Profil, 0.97 heißt drei Prozent langsamer |
| `--spacing` | 2.0 | Punktabstand in Metern |
| `--smooth` | 9 | Glättungsfenster in Punkten |
| `--lat-g` | 1.3 | Kurvengrenze in g, GT3 etwa 1.3 bis 1.6, Straßenauto 0.9 bis 1.1 |
| `--brake-g` | 1.2 | Bremsverzögerung in g |
| `--accel-g` | 0.5 | Beschleunigung in g |
| `--vmax` | 320 | Höchstgeschwindigkeit km/h |
| `--use-recorded-speed` | aus | Gefahrene Geschwindigkeit statt berechnetem Profil nehmen |

## Format

Dokumentiert in `fastlane/aifile.py`. Version 7, Header mit Punktzahl, dann pro Punkt Position und Länge, dann pro Punkt 18 Float-Werte (Speed, Gas, Bremse, Radius, Seitenabstände, Richtung, Vorwärtsvektor und mehr).

## Status

- Paket, Skripte und App geschrieben, Pipeline mit synthetischer Strecke getestet (`python tests/test_roundtrip.py`).
- Offen: Test mit echter Monza-Datei, Test der App im Spiel, Abgleich der CSP-API-Funktionen in `recorder.lua` mit der installierten CSP-Version.
